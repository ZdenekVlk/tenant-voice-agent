from __future__ import annotations

import logging
import time
from typing import Callable
from uuid import uuid4

from app.core.metrics import metrics

logger = logging.getLogger(__name__)


class ObservabilityMiddleware:
    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request_id = _get_or_create_request_id(scope)
        state = scope.setdefault("state", {})
        state["request_id"] = request_id

        method = scope.get("method", "GET")
        path = scope.get("path", "")

        logger.info(
            "request_started",
            extra={
                "method": method,
                "path": path,
                "request_id": request_id,
            },
        )

        start = time.perf_counter()
        status_code_holder: dict[str, int] = {}

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                status_code_holder["status_code"] = int(message.get("status", 0))
                headers = list(message.get("headers", []))
                headers = [
                    (key, value)
                    for key, value in headers
                    if key.lower() != b"x-request-id"
                ]
                headers.append((b"x-request-id", request_id.encode("utf-8")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            status_code = status_code_holder.get("status_code", 500)
            path_label = _resolve_route_path(scope)
            metrics.record_request(method, path_label, status_code, duration_ms)

            context = _extract_context(state)
            logger.info(
                "request_finished",
                extra={
                    "method": method,
                    "path": path_label,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                    "request_id": request_id,
                    **context,
                },
            )


def _get_or_create_request_id(scope: dict) -> str:
    headers = {key.lower(): value for key, value in scope.get("headers", [])}
    request_id = headers.get(b"x-request-id")
    if request_id:
        return request_id.decode("utf-8")
    return str(uuid4())


def _resolve_route_path(scope: dict) -> str:
    route = scope.get("route")
    route_path = getattr(route, "path", None)
    return route_path or scope.get("path", "")


def _extract_context(state: dict) -> dict[str, str]:
    context: dict[str, str] = {}
    tenant_id = state.get("tenant_id")
    conversation_id = state.get("conversation_id")
    if tenant_id:
        context["tenant_id"] = str(tenant_id)
    if conversation_id:
        context["conversation_id"] = str(conversation_id)
    return context
