from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse


def normalize_origin(origin: Optional[str], referer: Optional[str]) -> Optional[str]:
    raw = origin or referer
    if raw is None:
        return None

    raw = raw.strip()
    if not raw or raw.lower() == "null":
        return None

    try:
        parsed = urlparse(raw)
    except ValueError:
        return None

    if not parsed.scheme or not parsed.netloc:
        return None

    hostname = parsed.hostname
    if not hostname:
        return None

    return hostname.lower()
