from __future__ import annotations

from uuid import uuid4

from fastapi import Request


def get_or_create_request_id(request: Request) -> str:
    existing = request.headers.get("x-request-id")
    if existing:
        request.state.request_id = existing
        return existing

    current = getattr(request.state, "request_id", None)
    if current:
        return str(current)

    generated = str(uuid4())
    request.state.request_id = generated
    return generated
