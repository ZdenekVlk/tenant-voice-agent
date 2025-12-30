from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies.widget_auth import WidgetSessionContext, require_widget_session
from app.core.db import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


class WidgetMessageCreateRequest(BaseModel):
    text: str = Field(..., max_length=2000)
    metadata: dict[str, Any] | None = None


@router.post("/widget/messages")
def create_widget_message(
    payload: WidgetMessageCreateRequest,
    session: WidgetSessionContext = Depends(require_widget_session),
    db: Session = Depends(get_db),
) -> dict:
    trimmed_text = payload.text.strip()
    if not trimmed_text:
        raise HTTPException(status_code=400, detail="invalid_text")

    metadata = payload.metadata or {}

    try:
        result = db.execute(
            text(
                "INSERT INTO messages (tenant_id, conversation_id, role, content, meta) "
                "VALUES (:tenant_id, :conversation_id, :role, :content, :meta) "
                "RETURNING id"
            ),
            {
                "tenant_id": str(session.tenant_id),
                "conversation_id": str(session.conversation_id),
                "role": "user",
                "content": trimmed_text,
                "meta": metadata,
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
