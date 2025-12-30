from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies.widget_auth import WidgetSessionContext, require_widget_session
from app.core.db import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/widget/messages/assistant")
def create_assistant_message(
    session: WidgetSessionContext = Depends(require_widget_session),
    db: Session = Depends(get_db),
) -> dict:
    row = db.execute(
        text(
            "SELECT content FROM messages "
            "WHERE tenant_id = :tenant_id AND conversation_id = :conversation_id "
            "AND role = 'user' "
            "ORDER BY created_at DESC "
            "LIMIT 1"
        ),
        {
            "tenant_id": str(session.tenant_id),
            "conversation_id": str(session.conversation_id),
        },
    ).fetchone()

    if row is None:
        raise HTTPException(status_code=400, detail="user_message_not_found")

    user_text = row[0]
    assistant_text = f"Echo: {user_text}"

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
                "role": "assistant",
                "content": assistant_text,
                "meta": {},
            },
        )
        message_id = result.scalar_one()
        db.commit()
    except Exception:
        db.rollback()
        logger.exception(
            "assistant_message_error tenant_id=%s conversation_id=%s",
            session.tenant_id,
            session.conversation_id,
        )
        raise

    return {
        "conversation_id": str(session.conversation_id),
        "message_id": str(message_id),
        "text": assistant_text,
    }
