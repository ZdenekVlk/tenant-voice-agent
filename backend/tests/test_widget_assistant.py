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
    def __init__(self, row: tuple | None = None, scalar: UUID | None = None) -> None:
        self._row = row
        self._scalar = scalar

    def fetchone(self) -> tuple | None:
        return self._row

    def scalar_one(self) -> UUID:
        if self._scalar is None:
            raise AssertionError("Missing scalar value")
        return self._scalar


class DummySession:
    def __init__(self, user_text: str | None, message_id: UUID) -> None:
        self.user_text = user_text
        self.message_id = message_id
        self.executed: list[tuple[str, dict]] = []
        self.committed = False
        self.rolled_back = False

    def execute(self, statement: object, params: dict) -> DummyResult:
        statement_text = str(statement)
        self.executed.append((statement_text, params))
        if "SELECT content FROM messages" in statement_text:
            row = None if self.user_text is None else (self.user_text,)
            return DummyResult(row=row)
        if "INSERT INTO messages" in statement_text:
            return DummyResult(scalar=self.message_id)
        raise AssertionError("Unexpected SQL statement")

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


def test_create_assistant_message_happy_path() -> None:
    tenant_id = uuid4()
    conversation_id = uuid4()
    message_id = uuid4()
    dummy_db = DummySession(user_text="Ahoj", message_id=message_id)
    client = build_app_with_overrides(dummy_db, tenant_id, conversation_id)

    response = client.post("/widget/messages/assistant")

    assert response.status_code == 200
    assert response.json() == {
        "conversation_id": str(conversation_id),
        "message_id": str(message_id),
        "text": "Echo: Ahoj",
    }
    assert dummy_db.committed is True
    assert len(dummy_db.executed) == 2
    select_params = dummy_db.executed[0][1]
    insert_params = dummy_db.executed[1][1]
    assert select_params["tenant_id"] == str(tenant_id)
    assert select_params["conversation_id"] == str(conversation_id)
    assert insert_params["tenant_id"] == str(tenant_id)
    assert insert_params["conversation_id"] == str(conversation_id)
    assert insert_params["role"] == "assistant"
    assert insert_params["content"] == "Echo: Ahoj"


def test_create_assistant_message_without_user_message_returns_400() -> None:
    tenant_id = uuid4()
    conversation_id = uuid4()
    message_id = uuid4()
    dummy_db = DummySession(user_text=None, message_id=message_id)
    client = build_app_with_overrides(dummy_db, tenant_id, conversation_id)

    response = client.post("/widget/messages/assistant")

    assert response.status_code == 400
    assert response.json() == {"detail": "user_message_not_found"}
    assert dummy_db.executed
    assert dummy_db.committed is False


def test_create_assistant_message_missing_token_returns_401() -> None:
    app = create_app()
    dummy_db = DummySession(user_text="Ahoj", message_id=uuid4())

    def override_get_db():
        yield dummy_db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post("/widget/messages/assistant")

    assert response.status_code == 401
    assert response.json() == {"detail": "missing_authorization"}
