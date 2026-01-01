from __future__ import annotations

from fastapi import Request


def get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        parts = [part.strip() for part in forwarded.split(",") if part.strip()]
        if parts:
            return parts[0]

    client = request.client
    if client:
        return client.host

    return None
