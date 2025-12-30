from __future__ import annotations

import os
import time
from uuid import uuid4

import jwt
import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test")
os.environ.setdefault("WIDGET_SESSION_JWT_SECRET", "test-secret")
os.environ.setdefault("WIDGET_SESSION_JWT_ALG", "HS256")
os.environ.setdefault("WIDGET_SESSION_TTL_MINUTES", "10")

from app.core.widget_auth import (  # noqa: E402
    WidgetAuthError,
    build_widget_session_context,
    decode_widget_session_token,
    parse_bearer_token,
)


def test_parse_bearer_token_missing_header() -> None:
    with pytest.raises(WidgetAuthError) as exc:
        parse_bearer_token(None)
    assert exc.value.reason == "missing_header"


@pytest.mark.parametrize("header", ["Token abc", "Bearer ", "bearer"])
def test_parse_bearer_token_invalid_format(header: str) -> None:
    with pytest.raises(WidgetAuthError) as exc:
        parse_bearer_token(header)
    assert exc.value.reason == "invalid_format"


def test_decode_widget_session_token_invalid_signature() -> None:
    token = jwt.encode(
        {
            "tenant_id": str(uuid4()),
            "conversation_id": str(uuid4()),
            "exp": int(time.time()) + 60,
        },
        "other-secret",
        algorithm="HS256",
    )

    with pytest.raises(WidgetAuthError) as exc:
        decode_widget_session_token(token)
    assert exc.value.reason == "invalid_signature"


def test_decode_widget_session_token_expired() -> None:
    token = jwt.encode(
        {
            "tenant_id": str(uuid4()),
            "conversation_id": str(uuid4()),
            "exp": int(time.time()) - 1,
        },
        os.environ["WIDGET_SESSION_JWT_SECRET"],
        algorithm="HS256",
    )

    with pytest.raises(WidgetAuthError) as exc:
        decode_widget_session_token(token)
    assert exc.value.reason == "expired"


def test_build_widget_session_context_invalid_claims() -> None:
    with pytest.raises(WidgetAuthError) as exc:
        build_widget_session_context({"tenant_id": "nope", "conversation_id": "still-nope"})
    assert exc.value.reason == "invalid_claims"
