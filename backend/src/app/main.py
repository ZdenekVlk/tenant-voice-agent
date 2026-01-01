import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import routers
from app.core.logging import configure_logging
from app.middleware.observability import ObservabilityMiddleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ObservabilityMiddleware)

    @app.exception_handler(HTTPException)
    async def http_exception_logging_handler(request: Request, exc: HTTPException):
        error_code = exc.detail if isinstance(exc.detail, str) else "http_exception"
        logger.warning(
            "request_error",
            extra=_build_error_log_extra(request, error_code, exc.status_code),
        )
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_logging_handler(
        request: Request, exc: RequestValidationError
    ):
        logger.warning(
            "request_error",
            extra=_build_error_log_extra(request, "validation_error", 422),
        )
        return await request_validation_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def unhandled_exception_logging_handler(request: Request, exc: Exception):
        logger.error(
            "request_error",
            extra=_build_error_log_extra(request, "internal_error", 500),
        )
        return await http_exception_handler(
            request, HTTPException(status_code=500, detail="internal_error")
        )

    for router in routers:
        app.include_router(router)

    return app


def _build_error_log_extra(request: Request, error_code: str, status_code: int) -> dict:
    state = request.state
    payload = {
        "request_id": getattr(state, "request_id", None),
        "tenant_id": getattr(state, "tenant_id", None),
        "conversation_id": getattr(state, "conversation_id", None),
        "method": request.method,
        "path": request.url.path,
        "status_code": status_code,
        "error_code": error_code,
    }
    return {key: value for key, value in payload.items() if value is not None}


app = create_app()
