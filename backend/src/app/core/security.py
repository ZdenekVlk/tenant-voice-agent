from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings

settings = get_settings()


def create_widget_session_token(tenant_id: str, conversation_id: str) -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.widget_session_ttl_minutes)

    payload = {
        "tenant_id": tenant_id,
        "conversation_id": conversation_id,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    token = jwt.encode(payload, settings.widget_session_jwt_secret, algorithm=settings.widget_session_jwt_alg)
    return token, settings.widget_session_ttl_minutes * 60
