from __future__ import annotations

import logging
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.widget_auth import (
    WidgetAuthError,
    WidgetSessionContext,
    build_widget_session_context,
    decode_widget_session_token,
    parse_bearer_token,
)

logger = logging.getLogger(__name__)


def require_widget_session(
    request: Request,
    db: Session = Depends(get_db),
) -> WidgetSessionContext:
    authorization = request.headers.get("authorization")

    try:
        token = parse_bearer_token(authorization)
        claims = decode_widget_session_token(token)
        context = build_widget_session_context(claims)
    except WidgetAuthError as exc:
        logger.warning("widget_auth_denied reason=%s", exc.reason)
        detail_map = {
            "missing_header": "missing_authorization",
            "invalid_format": "invalid_authorization",
            "expired": "token_expired",
            "invalid_signature": "invalid_token",
            "invalid_claims": "invalid_claims",
        }
        detail = detail_map.get(exc.reason, "invalid_token")
        raise HTTPException(status_code=401, detail=detail) from exc

    row = db.execute(
        text("SELECT tenant_id FROM conversations WHERE id = :conversation_id"),
        {"conversation_id": str(context.conversation_id)},
    ).fetchone()

    if row is None:
        logger.warning(
            "widget_auth_denied reason=conversation_not_found conversation_id=%s",
            context.conversation_id,
        )
        raise HTTPException(status_code=403, detail="conversation_not_found")

    db_tenant_id = row[0]
    if isinstance(db_tenant_id, str):
        db_tenant_id = UUID(db_tenant_id)

    if db_tenant_id != context.tenant_id:
        logger.warning(
            "widget_auth_denied reason=tenant_mismatch conversation_id=%s tenant_id=%s",
            context.conversation_id,
            context.tenant_id,
        )
        raise HTTPException(status_code=403, detail="tenant_mismatch")

    logger.info(
        "widget_auth_ok tenant_id=%s conversation_id=%s",
        context.tenant_id,
        context.conversation_id,
    )

    return context


def get_tenant_id(session: WidgetSessionContext = Depends(require_widget_session)) -> UUID:
    return session.tenant_id


def get_conversation_id(session: WidgetSessionContext = Depends(require_widget_session)) -> UUID:
    return session.conversation_id
