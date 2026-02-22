import asyncio
import logging
import time
from collections import defaultdict
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, requests_per_second: float = 1.0):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self._last_request_time: dict[str, float] = defaultdict(float)
        self._lock = asyncio.Lock()

    async def acquire(self, key: str = "default") -> None:
        async with self._lock:
            now = time.time()
            time_since_last = now - self._last_request_time[key]
            
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {key}")
                await asyncio.sleep(wait_time)
            
            self._last_request_time[key] = time.time()

    def set_rate(self, requests_per_second: float) -> None:
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second


class PortalRateLimiter:
    def __init__(self):
        self._limiters: dict[str, RateLimiter] = {}

    def get_limiter(self, portal: str, requests_per_second: float = 1.0) -> RateLimiter:
        if portal not in self._limiters:
            self._limiters[portal] = RateLimiter(requests_per_second)
        return self._limiters[portal]

    async def acquire(self, portal: str, requests_per_second: float = 1.0) -> None:
        limiter = self.get_limiter(portal, requests_per_second)
        await limiter.acquire(portal)
