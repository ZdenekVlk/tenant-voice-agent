from __future__ import annotations

import os
from uuid import UUID, uuid4

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
    def __init__(self, message_id: UUID) -> None:
        self.message_id = message_id
        self.executed: list[tuple[str, dict]] = []
        self.committed = False
        self.rolled_back = False

    def execute(self, statement: object, params: dict) -> DummyResult:
        self.executed.append((str(statement), params))
        return DummyResult(self.message_id)

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        return None


def build_app_with_overrides(
    dummy_db: DummySession,
    tenant_id: UUID,
    conversation_id: UUID,
) -> TestClient:
    app = create_app()

    def override_get_db():
        yield dummy_db

    def override_require_widget_session() -> WidgetSessionContext:
        return WidgetSessionContext(tenant_id=tenant_id, conversation_id=conversation_id)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_widget_session] = override_require_widget_session
    return TestClient(app)


def test_create_widget_message_happy_path() -> None:
    tenant_id = uuid4()
    conversation_id = uuid4()
    message_id = uuid4()
    dummy_db = DummySession(message_id)
    client = build_app_with_overrides(dummy_db, tenant_id, conversation_id)

    response = client.post("/widget/messages", json={"text": "hello", "metadata": {"a": 1}})

    assert response.status_code == 200
    assert response.json() == {
        "conversation_id": str(conversation_id),
        "message_id": str(message_id),
    }
    assert dummy_db.committed is True
    assert dummy_db.executed
    _, params = dummy_db.executed[0]
    assert params["tenant_id"] == str(tenant_id)
    assert params["conversation_id"] == str(conversation_id)
    assert params["role"] == "user"
    assert params["content"] == "hello"
    assert params["meta"] == {"a": 1}


def test_create_widget_message_invalid_text_returns_400() -> None:
    tenant_id = uuid4()
    conversation_id = uuid4()
    message_id = uuid4()
    dummy_db = DummySession(message_id)
    client = build_app_with_overrides(dummy_db, tenant_id, conversation_id)

    response = client.post("/widget/messages", json={"text": "   "})

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid_text"}
    assert dummy_db.executed == []


def test_create_widget_message_missing_token_returns_401() -> None:
    app = create_app()
    dummy_db = DummySession(uuid4())

    def override_get_db():
        yield dummy_db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post("/widget/messages", json={"text": "hello"})

    assert response.status_code == 401
    assert response.json() == {"detail": "missing_authorization"}
