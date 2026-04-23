"""
ICICI Breeze Historical 1-Min Option Data Fetcher
==================================================
- Reads expiry dates from NIFTY.csv (columns: Symbol, Previous Expiry, Current Expiry, Next Expiry)
- For each trading date in the range, looks up the correct Current Expiry from CSV
- Fetches 9:20 close of underlying → snaps to ATM → builds OTM2/OTM1/ATM/ITM1/ITM2 ladder
- Fetches full day 1-min OHLC (9:15–15:30) for each strike × CE/PE
- Saves one CSV per trading date in OUTPUT_FOLDER

Usage:
    pip install breeze-connect pandas openpyxl
    python fetch_options.py
"""

import os
import time
import logging
from datetime import datetime, timedelta, date

import pandas as pd
from breeze_connect import BreezeConnect

# ─────────────────────────────────────────────────────────────
#  CONFIG ← UPDATE THESE
# ─────────────────────────────────────────────────────────────

API_KEY       = "YOUR_API_KEY"
API_SECRET    = "YOUR_API_SECRET"
SESSION_TOKEN = "YOUR_SESSION_TOKEN"   # regenerate each day

START_DATE = "26-08-2024"   # dd-mm-yyyy
END_DATE   = "29-08-2024"   # dd-mm-yyyy

# Path to your NIFTY.csv expiry file
# Columns: Symbol, Previous Expiry, Current Expiry, Next Expiry
EXPIRY_CSV_PATH = "NIFTY.csv"

# Output folder (created automatically)
OUTPUT_FOLDER = "output"

# Steps on each side of ATM  (2 = OTM2, OTM1, ATM, ITM1, ITM2)
STEPS = 2

# Retry / rate-limit settings
MAX_RETRIES = 3
RETRY_DELAY = 2     # base seconds (doubles each retry: 2s → 4s → 8s)
CALL_DELAY  = 0.5   # pause between every API call

# Max strikes to search in each direction when ATM has no data
MAX_ATM_SEARCH_STEPS = 10

# ─────────────────────────────────────────────────────────────
#  STOCK DEFINITIONS
#  strike_interval = actual exchange-listed step between strikes
# ─────────────────────────────────────────────────────────────

STOCKS = {
    "ACC": {
        "stock_code":       "ACC",   # used for underlying equity fetch
        "fno_code":         "ACC",   # used for options fetch
        "exchange":         "NSE",
        "strike_interval":  10,      # ACC strikes go 2320, 2330, 2340 ...
    },
    "RELIANCE": {
        "stock_code":       "RELIANCE",
        "fno_code":         "RELIANCE",
        "exchange":         "NSE",
        "strike_interval":  20,      # Reliance strikes go 2900, 2920, 2940 ...
    },
}

# ─────────────────────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
#  DATE / EXPIRY HELPERS
# ─────────────────────────────────────────────────────────────

def parse_date(s: str) -> date:
    """Parse dd-mm-yyyy string → date."""
    return datetime.strptime(s, "%d-%m-%Y").date()


def date_range(start: date, end: date):
    """Yield each calendar date from start to end inclusive."""
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def load_expiry_map(csv_path: str) -> dict:
    """
    Read NIFTY.csv and build a dict:
        { trade_date: current_expiry_date }

    The CSV has columns: Symbol, Previous Expiry, Current Expiry, Next Expiry
    We map every date in [Previous Expiry + 1 day ... Current Expiry]
    to Current Expiry as the active contract expiry.
    """
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]

    df["Previous Expiry"] = pd.to_datetime(df["Previous Expiry"]).dt.date
    df["Current Expiry"]  = pd.to_datetime(df["Current Expiry"]).dt.date

    expiry_map = {}
    for _, row in df.iterrows():
        prev_exp    = row["Previous Expiry"]
        curr_exp    = row["Current Expiry"]
        # Every trading day AFTER prev expiry up to and including curr expiry
        # belongs to the curr expiry contract
        d = prev_exp + timedelta(days=1)
        while d <= curr_exp:
            expiry_map[d] = curr_exp
            d += timedelta(days=1)

    log.info(f"Loaded expiry map: {len(expiry_map)} dates mapped.")
    return expiry_map


def to_breeze_dt(d: date, time_str: str = "09:15:00") -> str:
    """Format date+time as Breeze API datetime string."""
    return f"{d.strftime('%Y-%m-%d')}T{time_str}.000Z"


def to_breeze_expiry(d: date) -> str:
    """Breeze options expiry format (time 06:00:00)."""
    return f"{d.strftime('%Y-%m-%d')}T06:00:00.000Z"

# ─────────────────────────────────────────────────────────────
#  SAFE API CALL — auto-retry on connection errors
# ─────────────────────────────────────────────────────────────

def safe_get_historical(breeze, **kwargs):
    """
    Call breeze.get_historical_data_v2() with retry on connection errors.
    Always waits CALL_DELAY seconds first to avoid rate limiting.
    Returns response dict or None on failure.
    """
    time.sleep(CALL_DELAY)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return breeze.get_historical_data_v2(**kwargs)
        except Exception as e:
            err = str(e)
            is_conn = any(x in err for x in [
                "Connection aborted", "ConnectionResetError",
                "Connection reset by peer", "RemoteDisconnected", "timeout",
            ])
            if is_conn and attempt < MAX_RETRIES:
                wait = RETRY_DELAY * (2 ** (attempt - 1))
                log.warning(f"[RETRY {attempt}/{MAX_RETRIES}] Connection error — waiting {wait}s...")
                time.sleep(wait)
            else:
                log.error(f"[FAILED] {err[:120]}")
                return None
    return None

# ─────────────────────────────────────────────────────────────
#  STEP 1 — GET 9:20 CLOSE OF UNDERLYING
# ─────────────────────────────────────────────────────────────

def get_920_close(breeze, stock_code: str, exchange: str, trade_date: date) -> float | None:
    """
    Fetch 1-min equity candle at exactly 9:20 AM.
    Returns close price or None if unavailable.
    """
    resp = safe_get_historical(
        breeze,
        interval      = "1minute",
        from_date     = to_breeze_dt(trade_date, "09:20:00"),
        to_date       = to_breeze_dt(trade_date, "09:21:00"),
        stock_code    = stock_code,
        exchange_code = exchange,
        product_type  = "cash",
    )

    if not resp or resp.get("Status") != 200 or not resp.get("Success"):
        log.warning(f"  No 9:20 candle for {stock_code} on {trade_date}")
        return None

    close = float(resp["Success"][0]["close"])
    log.info(f"  9:20 raw close = {close}")
    return close

# ─────────────────────────────────────────────────────────────
#  STEP 2 — FIND ATM STRIKE WITH FALLBACK
# ─────────────────────────────────────────────────────────────

def has_option_data(breeze, fno_code, exchange, trade_date, expiry, strike, option_type) -> bool:
    """Quick probe: does this strike have any data at 9:15 AM?"""
    resp = safe_get_historical(
        breeze,
        interval      = "1minute",
        from_date     = to_breeze_dt(trade_date, "09:15:00"),
        to_date       = to_breeze_dt(trade_date, "09:16:00"),
        stock_code    = fno_code,
        exchange_code = exchange,
        product_type  = "options",
        expiry_date   = to_breeze_expiry(expiry),
        right         = option_type,
        strike_price  = str(int(strike)),
    )
    return bool(resp and resp.get("Status") == 200 and resp.get("Success"))


def find_atm_strike(breeze, fno_code, exchange, trade_date, expiry, close_price, interval) -> int | None:
    """
    1. Snap close to nearest strike using interval.
    2. Check if that strike has data.
    3. If not → search both directions simultaneously up to MAX_ATM_SEARCH_STEPS.
    4. Pick closest strike with data (upper preferred on tie).
    """
    candidate = round(close_price / interval) * interval
    log.info(f"  Nearest strike = {candidate}  (interval={interval})")

    # Check candidate
    if has_option_data(breeze, fno_code, exchange, trade_date, expiry, candidate, "call") or \
       has_option_data(breeze, fno_code, exchange, trade_date, expiry, candidate, "put"):
        log.info(f"  ATM confirmed  = {candidate}")
        return candidate

    # Fallback: search both directions
    log.info(f"  No data at {candidate} — searching both directions (max {MAX_ATM_SEARCH_STEPS} steps)...")
    for step in range(1, MAX_ATM_SEARCH_STEPS + 1):
        upper = candidate + step * interval
        lower = candidate - step * interval

        upper_ok = has_option_data(breeze, fno_code, exchange, trade_date, expiry, upper, "call") or \
                   has_option_data(breeze, fno_code, exchange, trade_date, expiry, upper, "put")
        lower_ok = has_option_data(breeze, fno_code, exchange, trade_date, expiry, lower, "call") or \
                   has_option_data(breeze, fno_code, exchange, trade_date, expiry, lower, "put")

        if upper_ok and lower_ok:
            log.info(f"  Step {step}: both {upper} & {lower} have data → picking upper {upper}")
            return upper
        elif upper_ok:
            log.info(f"  Step {step}: data found at {upper} → ATM = {upper}")
            return upper
        elif lower_ok:
            log.info(f"  Step {step}: data found at {lower} → ATM = {lower}")
            return lower
        else:
            log.info(f"  Step {step}: no data at {upper} or {lower}")

    log.error(f"  No ATM found within {MAX_ATM_SEARCH_STEPS} steps of {candidate}")
    return None

# ─────────────────────────────────────────────────────────────
#  STEP 3 — MONEYNESS LABEL
# ─────────────────────────────────────────────────────────────

def moneyness_label(offset: int, option_type: str) -> str:
    """
    offset = number of strike steps from ATM (positive = above ATM)
    CALL: above ATM = OTM,  below ATM = ITM
    PUT:  above ATM = ITM,  below ATM = OTM
    """
    if offset == 0:
        return "ATM"
    if option_type == "call":
        return f"OTM{offset}" if offset > 0 else f"ITM{abs(offset)}"
    else:
        return f"ITM{offset}" if offset > 0 else f"OTM{abs(offset)}"

# ─────────────────────────────────────────────────────────────
#  STEP 4 — FETCH FULL DAY 1-MIN DATA FOR ONE STRIKE
# ─────────────────────────────────────────────────────────────

def fetch_fullday_option(breeze, fno_code, exchange, trade_date, expiry, strike, option_type) -> list:
    """Fetch all 1-min candles 9:15–15:30 for one strike. Returns list of row dicts."""
    resp = safe_get_historical(
        breeze,
        interval      = "1minute",
        from_date     = to_breeze_dt(trade_date, "09:15:00"),
        to_date       = to_breeze_dt(trade_date, "15:30:00"),
        stock_code    = fno_code,
        exchange_code = exchange,
        product_type  = "options",
        expiry_date   = to_breeze_expiry(expiry),
        right         = option_type,
        strike_price  = str(int(strike)),
    )

    if not resp or resp.get("Status") != 200 or not resp.get("Success"):
        log.warning(f"    No data — {fno_code} {option_type.upper()} {int(strike)}")
        return []

    return [{
        "timestamp": c.get("datetime", ""),
        "open":      float(c.get("open",   0)),
        "high":      float(c.get("high",   0)),
        "low":       float(c.get("low",    0)),
        "close":     float(c.get("close",  0)),
        "volume":    int(c.get("volume",   0)),
    } for c in resp["Success"]]

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Load expiry map from CSV
    expiry_map = load_expiry_map(EXPIRY_CSV_PATH)

    # Connect to Breeze
    breeze = BreezeConnect(api_key=API_KEY)
    breeze.generate_session(api_secret=API_SECRET, session_token=SESSION_TOKEN)
    log.info("Breeze session established.\n")

    start_date = parse_date(START_DATE)
    end_date   = parse_date(END_DATE)

    moneyness_order = (
        [f"OTM{i}" for i in range(STEPS, 0, -1)] +
        ["ATM"] +
        [f"ITM{i}" for i in range(1, STEPS + 1)]
    )

    for trade_date in date_range(start_date, end_date):
        # Skip weekends
        if trade_date.weekday() >= 5:
            log.info(f"Skipping weekend: {trade_date}")
            continue

        # Look up expiry from CSV
        expiry = expiry_map.get(trade_date)
        if expiry is None:
            log.warning(f"No expiry found for {trade_date} in CSV — skipping.")
            continue

        log.info(f"\n{'='*60}")
        log.info(f"Date: {trade_date}  |  Expiry: {expiry}")

        all_rows = []

        for stock_name, cfg in STOCKS.items():
            log.info(f"\n  Stock: {stock_name}")

            interval   = cfg["strike_interval"]
            fno_code   = cfg["fno_code"]
            exchange   = cfg["exchange"]

            # Step 1: 9:20 close
            close_price = get_920_close(breeze, cfg["stock_code"], exchange, trade_date)
            if close_price is None:
                continue

            # Step 2: Find ATM
            atm = find_atm_strike(
                breeze, fno_code, exchange, trade_date, expiry, close_price, interval
            )
            if atm is None:
                log.warning(f"  Skipping {stock_name} — no ATM found.")
                continue

            # Strike ladder centred on confirmed ATM
            offsets = list(range(-STEPS, STEPS + 1))  # [-2, -1, 0, 1, 2]
            strikes = [(offset, atm + offset * interval) for offset in offsets]
            log.info(f"  Strike ladder: {[int(s) for _, s in strikes]}")

            # Step 3: Fetch full day for each strike × CE/PE
            for option_type in ["call", "put"]:
                log.info(f"  -- {option_type.upper()} --")

                for offset, strike in strikes:
                    money = moneyness_label(offset, option_type)
                    log.info(f"    {money:5s} | strike={int(strike)}", )

                    candles = fetch_fullday_option(
                        breeze, fno_code, exchange, trade_date, expiry, strike, option_type
                    )

                    if candles:
                        log.info(f"      → {len(candles)} candles")
                        for c in candles:
                            all_rows.append({
                                "ticker":      stock_name,
                                "date":        str(trade_date),
                                "expiry":      str(expiry),
                                "option_type": option_type.upper(),
                                "moneyness":   money,
                                "strike":      int(strike),
                                "timestamp":   c["timestamp"],
                                "open":        c["open"],
                                "high":        c["high"],
                                "low":         c["low"],
                                "close":       c["close"],
                                "volume":      c["volume"],
                            })
                    else:
                        log.info(f"      → no data")

        # Save one CSV per trading date
        if all_rows:
            df = pd.DataFrame(all_rows, columns=[
                "ticker", "date", "expiry", "option_type", "moneyness",
                "strike", "timestamp", "open", "high", "low", "close", "volume"
            ])
            df["moneyness"] = pd.Categorical(df["moneyness"], categories=moneyness_order, ordered=True)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values(["ticker", "option_type", "moneyness", "timestamp"]).reset_index(drop=True)

            csv_name = f"{trade_date.strftime('%Y-%m-%d')}.csv"
            csv_path = os.path.join(OUTPUT_FOLDER, csv_name)
            df.to_csv(csv_path, index=False)
            log.info(f"\n  ✓ Saved {len(df)} rows → {csv_path}")
        else:
            log.warning(f"  No data collected for {trade_date}.")

    log.info("\nAll done.")


if __name__ == "__main__":
    main()
