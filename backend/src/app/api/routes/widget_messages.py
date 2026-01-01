from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies.widget_auth import WidgetSessionContext, require_widget_session
from app.core.config import get_settings
from app.core.db import get_db
from app.core.rate_limiter import check_rate_limit
from app.utils.client_ip import get_client_ip
from app.utils.request_id import get_or_create_request_id

router = APIRouter()
logger = logging.getLogger(__name__)


class WidgetMessageCreateRequest(BaseModel):
    text: str = Field(...)
    metadata: dict[str, Any] | None = None


@router.get("/widget/conversations/{conversation_id}/messages")
def list_widget_messages(
    conversation_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: WidgetSessionContext = Depends(require_widget_session),
    db: Session = Depends(get_db),
) -> dict:
    if conversation_id != session.conversation_id:
        raise HTTPException(status_code=403, detail="conversation_mismatch")

    rows = db.execute(
        text(
            "SELECT id, role, content, meta, created_at "
            "FROM messages "
            "WHERE tenant_id = :tenant_id AND conversation_id = :conversation_id "
            "ORDER BY created_at ASC, id ASC "
            "LIMIT :limit OFFSET :offset"
        ),
        {
            "tenant_id": str(session.tenant_id),
            "conversation_id": str(conversation_id),
            "limit": limit + 1,
            "offset": offset,
        },
    ).fetchall()

    has_more = len(rows) > limit
    rows = rows[:limit]

    messages = []
    for row in rows:
        mapping = row._mapping
        created_at = mapping["created_at"]
        created_at_value = (
            created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at)
        )
        messages.append(
            {
                "id": str(mapping["id"]),
                "role": mapping["role"],
                "content": mapping["content"],
                "metadata": mapping["meta"] or {},
                "created_at": created_at_value,
            }
        )

    return {
        "conversation_id": str(conversation_id),
        "messages": messages,
        "paging": {
            "limit": limit,
            "offset": offset,
            "has_more": has_more,
        },
    }


@router.post("/widget/messages")
def create_widget_message(
    request: Request,
    payload: WidgetMessageCreateRequest,
    session: WidgetSessionContext = Depends(require_widget_session),
    db: Session = Depends(get_db),
) -> dict:
    trimmed_text = payload.text.strip()
    if not trimmed_text:
        raise HTTPException(status_code=400, detail="invalid_text")

    settings = get_settings()
    request_id = get_or_create_request_id(request)
    route = request.url.path

    if len(trimmed_text) > settings.max_message_text_len:
        logger.warning(
            "blocked",
            extra={
                "reason": "payload_text_length",
                "route": route,
                "tenant_id": str(session.tenant_id),
                "conversation_id": str(session.conversation_id),
                "request_id": request_id,
                "max_length": settings.max_message_text_len,
                "length": len(trimmed_text),
            },
        )
        raise HTTPException(
            status_code=400,
            detail="text_too_long",
            headers={"X-Request-Id": request_id},
        )

    tenant_key = f"tenant:{session.tenant_id}:{route}"
    allowed, retry_after = check_rate_limit(
        tenant_key, settings.rate_limit_messages_tenant
    )
    if not allowed:
        logger.warning(
            "blocked",
            extra={
                "reason": "rate_limit",
                "scope": "tenant",
                "route": route,
                "tenant_id": str(session.tenant_id),
                "conversation_id": str(session.conversation_id),
                "request_id": request_id,
            },
        )
        raise HTTPException(
            status_code=429,
            detail="rate_limited",
            headers={"Retry-After": str(retry_after), "X-Request-Id": request_id},
        )

    client_ip = get_client_ip(request)
    if client_ip:
        ip_key = f"ip:{client_ip}:{route}"
        allowed, retry_after = check_rate_limit(ip_key, settings.rate_limit_messages_ip)
        if not allowed:
            logger.warning(
                "blocked",
                extra={
                    "reason": "rate_limit",
                    "scope": "ip",
                    "route": route,
                    "tenant_id": str(session.tenant_id),
                    "conversation_id": str(session.conversation_id),
                    "request_id": request_id,
                },
            )
            raise HTTPException(
                status_code=429,
                detail="rate_limited",
                headers={"Retry-After": str(retry_after), "X-Request-Id": request_id},
            )
    else:
        logger.info(
            "rate_limit_ip_missing",
            extra={
                "route": route,
                "tenant_id": str(session.tenant_id),
                "conversation_id": str(session.conversation_id),
                "request_id": request_id,
            },
        )

    metadata = payload.metadata or {}

    try:
        result = db.execute(
            text(
                "INSERT INTO messages (tenant_id, conversation_id, role, content, meta) "
                "VALUES (:tenant_id, :conversation_id, :role, :content, CAST(:meta AS JSONB)) "
                "RETURNING id"
            ),
            {
                "tenant_id": str(session.tenant_id),
                "conversation_id": str(session.conversation_id),
                "role": "user",
                "content": trimmed_text,
                "meta": json.dumps(metadata),
            },
        )
        message_id = result.scalar_one()
        db.commit()
    except Exception:
        db.rollback()
        logger.exception(
            "widget_message_error tenant_id=%s conversation_id=%s",
            session.tenant_id,
            session.conversation_id,
        )
        raise

    return {
        "conversation_id": str(session.conversation_id),
        "message_id": str(message_id),
    }
