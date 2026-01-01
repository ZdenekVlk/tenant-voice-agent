from __future__ import annotations

import os
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test")
os.environ.setdefault("WIDGET_SESSION_JWT_SECRET", "test-secret")
os.environ.setdefault("WIDGET_SESSION_JWT_ALG", "HS256")
os.environ.setdefault("WIDGET_SESSION_TTL_MINUTES", "10")

from app.api.dependencies.widget_auth import require_widget_session  # noqa: E402
from app.core.db import get_db  # noqa: E402
from app.core.widget_auth import WidgetSessionContext  # noqa: E402
from app.main import create_app  # noqa: E402


class DummyResult:
    def __init__(self, value: UUID) -> None:
        self._value = value

    def scalar_one(self) -> UUID:
        return self._value


class DummySession:
    def __init__(self, *, allow_execute: bool) -> None:
        self.allow_execute = allow_execute
        self.executed: list[tuple[str, dict]] = []
        self.message_id = uuid4()

    def execute(self, statement: object, params: dict) -> DummyResult:
        self.executed.append((str(statement), params))
        if not self.allow_execute:
            raise AssertionError("DB should not be used in this test")
        return DummyResult(self.message_id)

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def close(self) -> None:
        return None


def build_client_with_overrides(
    tenant_id: UUID,
    conversation_id: UUID,
    *,
    allow_db_execute: bool,
) -> TestClient:
    app = create_app()
    dummy_db = DummySession(allow_execute=allow_db_execute)

    def override_get_db():
        yield dummy_db

    def override_require_widget_session() -> WidgetSessionContext:
        return WidgetSessionContext(tenant_id=tenant_id, conversation_id=conversation_id)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_widget_session] = override_require_widget_session
    return TestClient(app)


def test_rate_limit_messages_tenant(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_MESSAGES_TENANT", "1/min")
    monkeypatch.setenv("RATE_LIMIT_MESSAGES_IP", "100/min")

    tenant_id = uuid4()
    conversation_id = uuid4()
    client = build_client_with_overrides(tenant_id, conversation_id, allow_db_execute=True)

    first = client.post("/widget/messages", json={"text": "hello"})
    second = client.post("/widget/messages", json={"text": "hello again"})

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json() == {"detail": "rate_limited"}
    assert "Retry-After" in second.headers
    assert second.headers.get("X-Request-Id")


def test_payload_size_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_JSON_BODY_BYTES", "20")

    client = TestClient(create_app())
    response = client.post("/widget/messages", json={"text": "x" * 50})

    assert response.status_code == 413
    assert response.json() == {"detail": "payload_too_large"}
    assert response.headers.get("X-Request-Id")


def test_text_length_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_MESSAGE_TEXT_LEN", "5")
    monkeypatch.setenv("RATE_LIMIT_MESSAGES_TENANT", "100/min")
    monkeypatch.setenv("RATE_LIMIT_MESSAGES_IP", "100/min")

    tenant_id = uuid4()
    conversation_id = uuid4()
    client = build_client_with_overrides(tenant_id, conversation_id, allow_db_execute=False)
    response = client.post("/widget/messages", json={"text": "too-long"})

    assert response.status_code == 400
    assert response.json() == {"detail": "text_too_long"}
    assert response.headers.get("X-Request-Id")
