from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class RateLimit:
    max_requests: int
    window_seconds: int


class FixedWindowRateLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._entries: dict[str, tuple[float, int]] = {}

    def check(self, key: str, limit: RateLimit) -> tuple[bool, int]:
        now = time.time()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None or now - entry[0] >= limit.window_seconds:
                self._entries[key] = (now, 1)
                return True, 0

            window_start, count = entry
            if count >= limit.max_requests:
                retry_after = int(limit.window_seconds - (now - window_start))
                return False, max(1, retry_after)

            self._entries[key] = (window_start, count + 1)
            return True, 0


_UNIT_SECONDS = {
    "s": 1,
    "sec": 1,
    "second": 1,
    "seconds": 1,
    "m": 60,
    "min": 60,
    "minute": 60,
    "minutes": 60,
    "h": 3600,
    "hour": 3600,
    "hours": 3600,
}


def parse_rate_limit(value: str) -> RateLimit:
    if not value or "/" not in value:
        raise ValueError(f"Invalid rate limit format: {value}")

    count_str, unit = value.split("/", 1)
    count = int(count_str.strip())
    unit_key = unit.strip().lower()
    if count <= 0 or unit_key not in _UNIT_SECONDS:
        raise ValueError(f"Invalid rate limit format: {value}")

    return RateLimit(max_requests=count, window_seconds=_UNIT_SECONDS[unit_key])


rate_limiter = FixedWindowRateLimiter()


def check_rate_limit(key: str, limit_value: str) -> tuple[bool, int]:
    limit = parse_rate_limit(limit_value)
    return rate_limiter.check(key, limit)
