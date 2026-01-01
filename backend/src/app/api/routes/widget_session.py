from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.rate_limiter import check_rate_limit
from app.core.security import create_widget_session_token
from app.utils.client_ip import get_client_ip
from app.utils.origin import normalize_origin
from app.utils.request_id import get_or_create_request_id

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
    settings = get_settings()
    request_id = get_or_create_request_id(request)
    route = request.url.path

    tenant_key = f"tenant:{tenant_id}:{route}"
    allowed, retry_after = check_rate_limit(tenant_key, settings.rate_limit_session_tenant)
    if not allowed:
        logger.warning(
            "blocked",
            extra={
                "reason": "rate_limit",
                "scope": "tenant",
                "route": route,
                "tenant_id": str(tenant_id),
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
        allowed, retry_after = check_rate_limit(ip_key, settings.rate_limit_session_ip)
        if not allowed:
            logger.warning(
                "blocked",
                extra={
                    "reason": "rate_limit",
                    "scope": "ip",
                    "route": route,
                    "tenant_id": str(tenant_id),
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
            extra={"route": route, "tenant_id": str(tenant_id), "request_id": request_id},
        )

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
