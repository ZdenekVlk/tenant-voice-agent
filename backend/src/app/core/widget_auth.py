from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import jwt

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WidgetAuthError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class WidgetSessionContext:
    tenant_id: UUID
    conversation_id: UUID
    exp: int | None = None


def parse_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise WidgetAuthError("missing_header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise WidgetAuthError("invalid_format")

    return token.strip()


def decode_widget_session_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.widget_session_jwt_secret,
            algorithms=[settings.widget_session_jwt_alg],
        )
    except jwt.ExpiredSignatureError as exc:
        raise WidgetAuthError("expired") from exc
    except jwt.InvalidTokenError as exc:
        raise WidgetAuthError("invalid_signature") from exc


def build_widget_session_context(claims: dict[str, Any]) -> WidgetSessionContext:
    tenant_id = claims.get("tenant_id")
    conversation_id = claims.get("conversation_id")
    if not tenant_id or not conversation_id:
        raise WidgetAuthError("invalid_claims")

    try:
        tenant_uuid = UUID(str(tenant_id))
        conversation_uuid = UUID(str(conversation_id))
    except ValueError as exc:
        raise WidgetAuthError("invalid_claims") from exc

    exp = claims.get("exp")
    return WidgetSessionContext(
        tenant_id=tenant_uuid,
        conversation_id=conversation_uuid,
        exp=exp,
    )
