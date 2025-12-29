from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import create_widget_session_token
from app.utils.origin import normalize_origin

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/widget/session")
def create_widget_session(request: Request, db: Session = Depends(get_db)) -> dict:
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    domain = normalize_origin(origin, referer)

    if not domain:
        logger.warning(
            "widget_session_denied reason=invalid_origin origin=%s referer=%s",
            origin,
            referer,
        )
        raise HTTPException(status_code=400, detail="invalid_origin")

    tenant_row = db.execute(
        text("SELECT tenant_id FROM tenant_domains WHERE domain = :domain"),
        {"domain": domain},
    ).fetchone()

    if tenant_row is None:
        logger.warning("widget_session_denied reason=domain_not_allowed domain=%s", domain)
        raise HTTPException(status_code=403, detail="domain_not_allowed")

    tenant_id = tenant_row[0]

    try:
        result = db.execute(
            text("INSERT INTO conversations (tenant_id) VALUES (:tenant_id) RETURNING id"),
            {"tenant_id": tenant_id},
        )
        conversation_id = result.scalar_one()
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("widget_session_error domain=%s tenant_id=%s", domain, tenant_id)
        raise

    token, expires_in = create_widget_session_token(str(tenant_id), str(conversation_id))

    logger.info(
        "widget_session_created domain=%s tenant_id=%s conversation_id=%s",
        domain,
        tenant_id,
        conversation_id,
    )

    return {
        "conversation_id": str(conversation_id),
        "token": token,
        "expires_in": expires_in,
        "ui_config": {},
    }
