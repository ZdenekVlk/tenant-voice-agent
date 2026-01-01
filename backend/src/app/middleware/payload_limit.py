from __future__ import annotations

import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.utils.request_id import get_or_create_request_id

logger = logging.getLogger(__name__)

_LIMITED_ROUTES = {"/widget/session", "/widget/messages"}


class PayloadLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method != "POST" or request.url.path not in _LIMITED_ROUTES:
            return await call_next(request)

        max_bytes = get_settings().max_json_body_bytes
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError:
                length = None
            if length is not None and length > max_bytes:
                return _payload_too_large_response(request, length, max_bytes)
            if length is not None:
                return await call_next(request)

        body = await request.body()
        if len(body) > max_bytes:
            return _payload_too_large_response(request, len(body), max_bytes)

        request._body = body
        return await call_next(request)


def _payload_too_large_response(request: Request, length: int, max_bytes: int) -> Response:
    request_id = get_or_create_request_id(request)
    logger.warning(
        "blocked",
        extra={
            "reason": "payload_size",
            "route": request.url.path,
            "request_id": request_id,
            "content_length": length,
            "max_bytes": max_bytes,
        },
    )
    response = JSONResponse(status_code=413, content={"detail": "payload_too_large"})
    response.headers["X-Request-Id"] = request_id
    return response
