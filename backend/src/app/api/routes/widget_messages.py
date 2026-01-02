from __future__ import annotations

import hashlib
import json
import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
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
    payload: WidgetMessageCreateRequest,
    request: Request,
    session: WidgetSessionContext = Depends(require_widget_session),
    db: Session = Depends(get_db),
) -> dict:
    trimmed_text = payload.text.strip()
    if not trimmed_text:
        raise HTTPException(status_code=400, detail="invalid_text")

    metadata = payload.metadata or {}
    idempotency_key = request.headers.get("idempotency-key")
    if idempotency_key:
        idempotency_key = idempotency_key.strip()

    request_id = request.headers.get("x-request-id")

    if idempotency_key:
        payload_hash = json.dumps(
            {"text": trimmed_text, "metadata": metadata},
            sort_keys=True,
            separators=(",", ":"),
        )
        request_hash = hashlib.sha256(payload_hash.encode("utf-8")).hexdigest()

        try:
            insert_result = db.execute(
                text(
                    "INSERT INTO idempotency_keys "
                    "(tenant_id, conversation_id, key, request_hash, response_json) "
                    "VALUES (:tenant_id, :conversation_id, :key, :request_hash, NULL) "
                    "ON CONFLICT (tenant_id, conversation_id, key) DO NOTHING "
                    "RETURNING id"
                ),
                {
                    "tenant_id": str(session.tenant_id),
                    "conversation_id": str(session.conversation_id),
                    "key": idempotency_key,
                    "request_hash": request_hash,
                },
            )
            idempotency_id = insert_result.scalar_one_or_none()
            if idempotency_id is not None:
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
                response_payload = {
                    "conversation_id": str(session.conversation_id),
                    "message_id": str(message_id),
                }
                db.execute(
                    text(
                        "UPDATE idempotency_keys "
                        "SET response_json = CAST(:response_json AS JSONB) "
                        "WHERE tenant_id = :tenant_id "
                        "AND conversation_id = :conversation_id "
                        "AND key = :key"
                    ),
                    {
                        "tenant_id": str(session.tenant_id),
                        "conversation_id": str(session.conversation_id),
                        "key": idempotency_key,
                        "response_json": json.dumps(response_payload),
                    },
                )
                db.commit()
                logger.info(
                    "idempotency_miss request_id=%s tenant_id=%s conversation_id=%s",
                    request_id,
                    session.tenant_id,
                    session.conversation_id,
                )
                return response_payload

            row = db.execute(
                text(
                    "SELECT request_hash, response_json "
                    "FROM idempotency_keys "
                    "WHERE tenant_id = :tenant_id "
                    "AND conversation_id = :conversation_id "
                    "AND key = :key"
                ),
                {
                    "tenant_id": str(session.tenant_id),
                    "conversation_id": str(session.conversation_id),
                    "key": idempotency_key,
                },
            ).fetchone()

            if row is None:
                logger.warning(
                    "idempotency_conflict request_id=%s tenant_id=%s conversation_id=%s reason=missing_record",
                    request_id,
                    session.tenant_id,
                    session.conversation_id,
                )
                raise HTTPException(status_code=409, detail="idempotency_key_conflict")

            existing_hash = row[0]
            response_json = row[1]

            if existing_hash != request_hash:
                logger.info(
                    "idempotency_conflict request_id=%s tenant_id=%s conversation_id=%s reason=hash_mismatch",
                    request_id,
                    session.tenant_id,
                    session.conversation_id,
                )
                raise HTTPException(status_code=409, detail="idempotency_key_conflict")

            if response_json is None:
                logger.warning(
                    "idempotency_conflict request_id=%s tenant_id=%s conversation_id=%s reason=missing_response",
                    request_id,
                    session.tenant_id,
                    session.conversation_id,
                )
                raise HTTPException(status_code=409, detail="idempotency_key_conflict")

            response_payload = (
                json.loads(response_json) if isinstance(response_json, str) else response_json
            )
            logger.info(
                "idempotency_hit request_id=%s tenant_id=%s conversation_id=%s",
                request_id,
                session.tenant_id,
                session.conversation_id,
            )
            return response_payload
        except HTTPException:
            raise
        except Exception:
            db.rollback()
            logger.exception(
                "widget_message_error tenant_id=%s conversation_id=%s",
                session.tenant_id,
                session.conversation_id,
            )
            raise

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
