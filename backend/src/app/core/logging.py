from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any


_STANDARD_LOG_RECORD_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key in _STANDARD_LOG_RECORD_ATTRS:
                continue
            if value is None:
                continue
            log_record[key] = _normalize_value(value)

        if record.exc_info:
            exc_type = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            log_record["error_type"] = exc_type

        return json.dumps(log_record, ensure_ascii=True)


def _normalize_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _normalize_value(val) for key, val in value.items()}
    return str(value)


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if getattr(configure_logging, "_configured", False):
        return

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = logging._nameToLevel.get(level_name, logging.INFO)

    if root_logger.handlers:
        for handler in root_logger.handlers:
            handler.setFormatter(JsonFormatter())
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root_logger.addHandler(handler)

    root_logger.setLevel(level)
    configure_logging._configured = True
