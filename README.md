# Job Discovery System

A comprehensive job discovery, application tracking, and candidate management system with built-in job scraping capabilities.

## Overview

This system helps staffing agencies manage job applications for multiple candidates. Staff can:
- **Discover Jobs**: Scrape jobs from multiple job boards (Indeed, Jooble, Remotive, LinkedIn)
- **Manage Candidates**: Track candidate profiles, skills, and resumes
- **Track Applications**: Manage application workflow from draft to submission
- **Generate Applications**: Bulk generate job applications for candidates
- **Staff Collaboration**: Track staff progress and team performance

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Job Discovery System                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐ │
│   │   Frontend  │     │   Backend   │     │       Scraper          │ │
│   │  (React)    │◄───►│  (Node.js)  │     │      (Python)          │ │
│   │   (Next.js) │     │  Express +  │     │  Selenium + APIs       │ │
│   │             │     │   Prisma     │     │                        │ │
│   └─────────────┘     └──────┬──────┘     └───────────┬─────────────┘ │
│                              │                         │               │
│                              ▼                         ▼               │
│                       ┌─────────────┐          ┌─────────────┐          │
│                       │  PostgreSQL │◄────────│    Redis   │          │
│                       │  Database   │          │   Queue    │          │
│                       └─────────────┘          └─────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **Runtime**: Node.js 20 LTS
- **Framework**: Express.js
- **Database**: PostgreSQL 15
- **ORM**: Prisma
- **Queue**: Redis
- **Auth**: JWT + bcrypt
- **Validation**: Zod

### Scraper
- **Runtime**: Python 3.11+
- **APIs**: requests, aiohttp
- **Browser**: Selenium, Playwright
- **DB**: asyncpg

### Frontend (Coming Soon)
- React + Next.js
- TypeScript
- Tailwind CSS

## Features

### Job Discovery
- [x] Scrape from Jooble (free API)
- [x] Scrape from Remotive (free API)
- [ ] Scrape from Indeed (Selenium)
- [ ] Scrape from LinkedIn (Selenium)
- [x] Redis queue for background jobs
- [x] Job status tracking

### Candidate Management
- [x] CRUD operations
- [x] Resume upload & parsing
- [x] Skills tracking
- [x] Bulk import (CSV)
- [x] GDPR consent

### Application Workflow
- [x] Create applications
- [x] Bulk generate (60 per candidate)
- [x] Approval workflow (draft → review → approve/reject → submit)
- [x] Auto-fill data generation
- [x] Staff notes

### Dashboard & Reports
- [x] Staff statistics
- [x] Activity tracking
- [x] Team progress
- [x] Leaderboard

### Security
- [x] JWT authentication
- [x] Role-based access (Head, Senior Staff, Staff)
- [x] Rate limiting
- [x] Input validation

## Project Structure

```
project-apply/
├── backend/                    # Node.js API server
│   ├── src/
│   │   ├── domain/           # Business entities & rules
│   │   ├── infrastructure/   # Database & external services
│   │   ├── presentation/    # API routes & middleware
│   │   └── shared/          # Utilities
│   ├── prisma/              # Database schema
│   └── docker-compose.yml   # All services
│
├── tasks/                    # Task specifications
│   └── architecture.md      # System architecture
│
└── uploads/                  # File uploads
    └── resumes/             # Candidate resumes
```

## Getting Started

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose (recommended)

### Quick Start

```bash
# Clone and navigate to project
cd project-apply/backend

# Start all services
docker-compose up -d

# Or for local development
npm install
cp .env.example .env
npx prisma migrate dev
npm run dev
```

See [backend/README.md](backend/README.md) for detailed setup instructions.

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout

### Jobs
- `GET /api/jobs` - List jobs (with filters)
- `POST /api/jobs` - Create job manually
- `POST /api/jobs/sync` - Trigger scraper
- `GET /api/jobs/sync/status/:id` - Check scrape status

### Candidates
- `GET /api/candidates` - List candidates
- `POST /api/candidates` - Create candidate
- `PUT /api/candidates/:id` - Update candidate

### Applications
- `GET /api/applications` - List applications
- `POST /api/applications` - Create application
- `POST /api/applications/:id/approve` - Approve
- `POST /api/applications/:id/reject` - Reject

### Dashboard
- `GET /api/dashboard/stats` - Staff statistics
- `GET /api/dashboard/activity` - Recent activity

### Reports (Head only)
- `GET /api/reports/staff-progress` - Staff progress
- `GET /api/reports/team-stats` - Team stats

## Job Filters

Jobs can be filtered using query parameters:
```
GET /api/jobs?workType=remote&location=USA&source=jooble&datePosted=7&skills=python,javascript
```

| Parameter | Description |
|-----------|-------------|
| `workType` | remote, hybrid, onsite |
| `location` | Location name |
| `source` | jooble, remotive, indeed, linkedin |
| `datePosted` | Days since posted (1, 3, 7, 30) |
| `skills` | Comma-separated skills |
| `search` | Search in title/company |
| `page` | Page number |
| `limit` | Items per page |

## Roles & Permissions

| Role | Description |
|------|-------------|
| **Head** | Full access to all features |
| **Senior Staff** | Candidates, Jobs, Applications, approve/reject |
| **Staff** | View/create applications for assigned candidates |

## Scraping Jobs

```bash
# Trigger a scrape
curl -X POST http://localhost:3000/api/jobs/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "board": "jooble",
    "keywords": ["python", "javascript"],
    "location": "remote"
  }'

# Check status
curl http://localhost:3000/api/jobs/sync/status/<JOB_ID>
```

## Default Users (After Seeding)

| Email | Password | Role |
|-------|----------|------|
| head@company.com | password123 | Head |
| senior@company.com | password123 | Senior Staff |
| staff@company.com | password123 | Staff |

## Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/job_discovery
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key-min-32-chars
JWT_REFRESH_SECRET=your-refresh-secret-key
PORT=3000
NODE_ENV=development
```

## Development

### Running Tests
```bash
cd backend
npm run typecheck    # TypeScript checking
npm run db:studio   # Database GUI
```

### Adding New Features
1. Define entity in `src/domain/entities/`
2. Create repository interface in `src/domain/repositories/`
3. Implement in `src/infrastructure/database/repositories/`
4. Add route in `src/presentation/routes/`
5. Add validation in middleware

See [backend/README.md](backend/README.md) for detailed development guide.

## Roadmap

- [ ] Frontend (React + Next.js)
- [ ] Indeed scraper (Selenium)
- [ ] LinkedIn scraper (Selenium)
- [ ] Resume parsing service
- [ ] Skill matching algorithm
- [ ] Cover letter generation
- [ ] Email notifications
- [ ] Export to CSV/Excel

## License

MIT

"""
ICICI Breeze Historical 1-Min Option Data Fetcher
==================================================
Fetches expired option chain data for ACC & Reliance using Breeze API.

HOW TO USE:
-----------
1. Fill in your credentials in the CONFIG section below.
2. Set START_DATE and END_DATE.
3. Set EXPIRY_FILE_PATH to your Excel file containing monthly expiry dates.
4. Run:  python fetch_options.py
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG  ← UPDATE THESE VALUES
# ─────────────────────────────────────────────────────────────────────────────

API_KEY        = "YOUR_API_KEY_HERE"          # Breeze API key
API_SECRET     = "YOUR_API_SECRET_HERE"       # Breeze API secret
SESSION_TOKEN  = "YOUR_SESSION_TOKEN_HERE"    # Breeze session token

START_DATE     = "24-08-2024"                 # dd-mm-yyyy
END_DATE       = "29-08-2024"                 # dd-mm-yyyy

# Path to your Excel file with monthly expiry dates.
# The file must have a column named "ExpiryDate" in column A.
# Dates should be in a recognisable date format (e.g. 2024-08-29).
EXPIRY_FILE_PATH = r"C:\path\to\your\expiry_dates.xlsx"   # ← UPDATE THIS

# Folder where output CSVs will be saved (created automatically if missing)
OUTPUT_FOLDER  = "output"

# ─────────────────────────────────────────────────────────────────────────────
# STOCK DEFINITIONS  ← Add more stocks here in future
# ─────────────────────────────────────────────────────────────────────────────

STOCKS = {
    "ACC": {
        "stock_code": "ACC",          # Equity code used for underlying price
        "fno_code":   "ACC",          # Code used in options API
        "exchange":   "NSE",
    },
    "RELIANCE": {
        "stock_code": "RELIANCE",
        "fno_code":   "RELIANCE",
        "exchange":   "NSE",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

import os
import time
import logging
from datetime import datetime, timedelta, date

import pandas as pd
from breeze_connect import BreezeConnect

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_date(s: str) -> date:
    """Parse dd-mm-yyyy string to date."""
    return datetime.strptime(s, "%d-%m-%Y").date()


def date_range(start: date, end: date):
    """Yield each calendar date from start to end inclusive."""
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def load_expiry_dates(path: str) -> list[date]:
    """Load expiry dates from Excel file, column A header 'ExpiryDate'."""
    df = pd.read_excel(path, usecols=[0])
    df.columns = ["ExpiryDate"]
    df["ExpiryDate"] = pd.to_datetime(df["ExpiryDate"]).dt.date
    expiries = sorted(df["ExpiryDate"].dropna().tolist())
    log.info(f"Loaded {len(expiries)} expiry dates from Excel.")
    return expiries


def get_next_n_expiries(from_date: date, expiries: list[date], n: int = 2) -> list[date]:
    """Return next n expiry dates on or after from_date."""
    upcoming = [e for e in expiries if e >= from_date]
    return upcoming[:n]


def round_to_nearest_5(price: float) -> int:
    """Round price to nearest multiple of 5."""
    return int(round(price / 5) * 5)


def to_breeze_datetime(d: date, time_str: str = "09:15:00") -> str:
    """Return ISO datetime string expected by Breeze API: 'YYYY-MM-DDTHH:MM:SS.000Z'"""
    dt = datetime.combine(d, datetime.strptime(time_str, "%H:%M:%S").time())
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def to_breeze_expiry(d: date) -> str:
    """Breeze expects expiry as 'YYYY-MM-DDTHH:MM:SS.000Z' with time 07:00:00."""
    dt = datetime.combine(d, datetime.strptime("07:00:00", "%H:%M:%S").time())
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def fetch_equity_candles(breeze, stock_code: str, exchange: str, trade_date: date) -> pd.DataFrame:
    """Fetch 1-min equity candles for a given date (9:15 – 9:25 window)."""
    resp = breeze.get_historical_data_v2(
        interval="1minute",
        from_date=to_breeze_datetime(trade_date, "09:15:00"),
        to_date=to_breeze_datetime(trade_date, "09:25:00"),
        stock_code=stock_code,
        exchange_code=exchange,
        product_type="cash",
    )
    if resp.get("Status") != 200 or not resp.get("Success"):
        return pd.DataFrame()
    df = pd.DataFrame(resp["Success"])
    if df.empty:
        return df
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    return df


def get_920_close(equity_df: pd.DataFrame) -> float | None:
    """Return close price of the candle ending at (or nearest to) 9:20 AM."""
    if equity_df.empty:
        return None
    # The candle that closes AT 9:20 starts at 9:19; Breeze labels candles by
    # their open time, so we look for 09:19 first, then 09:20 as fallback.
    for t in ["09:19", "09:20"]:
        mask = equity_df["datetime"].dt.strftime("%H:%M") == t
        if mask.any():
            return float(equity_df.loc[mask, "close"].iloc[-1])
    # fallback: last candle before or at 9:20
    sub = equity_df[equity_df["datetime"].dt.time <= datetime.strptime("09:20", "%H:%M").time()]
    if sub.empty:
        return None
    return float(sub.iloc[-1]["close"])


def fetch_option_candles(
    breeze,
    fno_code: str,
    exchange: str,
    trade_date: date,
    expiry: date,
    strike: int,
    option_type: str,   # "call" or "put"
) -> pd.DataFrame:
    """Fetch 1-min option OHLC for the full trading day (9:15 – 15:30)."""
    right = "call" if option_type.lower() == "call" else "put"
    resp = breeze.get_historical_data_v2(
        interval="1minute",
        from_date=to_breeze_datetime(trade_date, "09:15:00"),
        to_date=to_breeze_datetime(trade_date, "15:30:00"),
        stock_code=fno_code,
        exchange_code=exchange,
        product_type="options",
        expiry_date=to_breeze_expiry(expiry),
        strike_price=str(strike),
        right=right,
    )
    if resp.get("Status") != 200 or not resp.get("Success"):
        return pd.DataFrame()
    df = pd.DataFrame(resp["Success"])
    if df.empty:
        return df
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def find_atm_strike(
    breeze,
    fno_code: str,
    exchange: str,
    trade_date: date,
    expiry: date,
    base_strike: int,
    option_type: str,
    max_steps: int = 30,
) -> int | None:
    """
    Starting from base_strike, search outward in steps of 5 for a strike
    that has actual option data. Returns the first such strike (ATM proxy).
    """
    offsets = [0]
    for i in range(1, max_steps + 1):
        offsets += [i * 5, -i * 5]

    for offset in offsets:
        strike = base_strike + offset
        if strike <= 0:
            continue
        df = fetch_option_candles(breeze, fno_code, exchange, trade_date, expiry, strike, option_type)
        time.sleep(0.3)   # polite rate-limit pause
        if not df.empty:
            log.info(f"    ATM found at strike {strike} (offset {offset:+d}) for {option_type.upper()}")
            return strike
    return None


def assign_moneyness(strike: int, atm_strike: int, option_type: str, step: int = 5) -> str:
    """
    Return moneyness label relative to ATM.
    For CALL: strikes > ATM are OTM; strikes < ATM are ITM.
    For PUT : strikes < ATM are OTM; strikes > ATM are ITM.
    """
    diff = (strike - atm_strike) // step   # signed number of steps from ATM

    if diff == 0:
        return "ATM"

    if option_type.lower() == "call":
        if diff > 0:
            return f"OTM{diff}"
        else:
            return f"ITM{abs(diff)}"
    else:  # put
        if diff < 0:
            return f"OTM{abs(diff)}"
        else:
            return f"ITM{diff}"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # ── Setup ────────────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    start_date = parse_date(START_DATE)
    end_date   = parse_date(END_DATE)
    expiries   = load_expiry_dates(EXPIRY_FILE_PATH)

    # Get 2 expiries from start date (used for the whole date range)
    target_expiries = get_next_n_expiries(start_date, expiries, n=2)
    if not target_expiries:
        log.error("No expiry dates found on or after the start date. Check your Excel file.")
        return
    log.info(f"Using expiries: {target_expiries}")

    # ── Connect to Breeze ────────────────────────────────────────────────────
    breeze = BreezeConnect(api_key=API_KEY)
    breeze.generate_session(api_secret=API_SECRET, session_token=SESSION_TOKEN)
    log.info("Breeze session established.")

    # ── Loop over dates ──────────────────────────────────────────────────────
    for trade_date in date_range(start_date, end_date):
        # Skip weekends
        if trade_date.weekday() >= 5:
            continue

        log.info(f"\n{'='*60}")
        log.info(f"Processing date: {trade_date}")

        all_rows = []

        for stock_name, cfg in STOCKS.items():
            log.info(f"  Stock: {stock_name}")

            # ── Step 1: Fetch equity candles and get 9:20 close ──────────────
            equity_df = fetch_equity_candles(breeze, cfg["stock_code"], cfg["exchange"], trade_date)
            time.sleep(0.3)

            close_920 = get_920_close(equity_df)
            if close_920 is None:
                log.warning(f"    Could not get 9:20 close for {stock_name} on {trade_date}. Skipping.")
                continue

            log.info(f"    9:20 close = {close_920}")
            base_strike = round_to_nearest_5(close_920)
            log.info(f"    Base strike (rounded to 5) = {base_strike}")

            # ── Step 2: For each expiry, fetch option data ────────────────────
            for expiry in target_expiries:
                log.info(f"    Expiry: {expiry}")

                for opt_type in ["call", "put"]:
                    log.info(f"      Option type: {opt_type.upper()}")

                    # Find ATM strike (first strike with actual data)
                    atm_strike = find_atm_strike(
                        breeze, cfg["fno_code"], cfg["exchange"],
                        trade_date, expiry, base_strike, opt_type,
                    )
                    if atm_strike is None:
                        log.warning(f"      No data found near {base_strike} for {opt_type.upper()}. Skipping.")
                        continue

                    # Build strike list: ATM ± 5 levels (11 strikes total)
                    strikes_to_fetch = [atm_strike + (i * 5) for i in range(-5, 6)]

                    for strike in strikes_to_fetch:
                        if strike <= 0:
                            continue

                        df = fetch_option_candles(
                            breeze, cfg["fno_code"], cfg["exchange"],
                            trade_date, expiry, strike, opt_type,
                        )
                        time.sleep(0.25)

                        if df.empty:
                            log.debug(f"        Strike {strike}: no data")
                            continue

                        moneyness = assign_moneyness(strike, atm_strike, opt_type)
                        log.info(f"        Strike {strike} ({moneyness}): {len(df)} rows")

                        for _, row in df.iterrows():
                            all_rows.append({
                                "Date":       str(trade_date),
                                "Stock":      stock_name,
                                "Expiry":     str(expiry),
                                "OptionType": opt_type.capitalize(),
                                "Moneyness":  moneyness,
                                "Strike":     strike,
                                "Open":       row.get("open"),
                                "High":       row.get("high"),
                                "Low":        row.get("low"),
                                "Close":      row.get("close"),
                                "Datetime":   row.get("datetime"),
                            })

        # ── Save CSV for this date ────────────────────────────────────────────
        if all_rows:
            out_df = pd.DataFrame(all_rows)
            csv_name = f"{trade_date.strftime('%d-%m-%Y')}.csv"
            csv_path = os.path.join(OUTPUT_FOLDER, csv_name)
            out_df.to_csv(csv_path, index=False)
            log.info(f"  ✓ Saved {len(all_rows)} rows → {csv_path}")
        else:
            log.warning(f"  No data collected for {trade_date}.")

    log.info("\nDone.")


if __name__ == "__main__":
    main()
