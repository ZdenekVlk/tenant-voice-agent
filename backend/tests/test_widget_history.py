from __future__ import annotations

import os
from datetime import datetime, timezone
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


class DummyRow:
    def __init__(
        self,
        *,
        message_id: UUID,
        role: str,
        content: str,
        meta: dict,
        created_at: datetime,
    ) -> None:
        self._mapping = {
            "id": message_id,
            "role": role,
            "content": content,
            "meta": meta,
            "created_at": created_at,
        }


class DummyResult:
    def __init__(self, rows: list[DummyRow]) -> None:
        self._rows = rows

    def fetchall(self) -> list[DummyRow]:
        return self._rows


class DummySession:
    def __init__(self, rows: list[DummyRow]) -> None:
        self.rows = rows
        self.executed: list[tuple[str, dict]] = []

    def execute(self, statement: object, params: dict) -> DummyResult:
        statement_text = str(statement)
        self.executed.append((statement_text, params))
        if "FROM messages" in statement_text:
            return DummyResult(self.rows)
        raise AssertionError("Unexpected SQL statement")

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


def test_list_widget_messages_happy_path() -> None:
    tenant_id = uuid4()
    conversation_id = uuid4()
    rows = [
        DummyRow(
            message_id=uuid4(),
            role="user",
            content="Ahoj",
            meta={"a": 1},
            created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        ),
        DummyRow(
            message_id=uuid4(),
            role="assistant",
            content="Zdravim",
            meta={},
            created_at=datetime(2025, 1, 1, 0, 1, tzinfo=timezone.utc),
        ),
        DummyRow(
            message_id=uuid4(),
            role="user",
            content="Diky",
            meta={},
            created_at=datetime(2025, 1, 1, 0, 2, tzinfo=timezone.utc),
        ),
    ]
    dummy_db = DummySession(rows)
    client = build_app_with_overrides(dummy_db, tenant_id, conversation_id)

    response = client.get(
        f"/widget/conversations/{conversation_id}/messages?limit=2&offset=0"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation_id"] == str(conversation_id)
    assert payload["paging"] == {"limit": 2, "offset": 0, "has_more": True}
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["id"] == str(rows[0]._mapping["id"])
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][0]["content"] == "Ahoj"
    assert payload["messages"][0]["metadata"] == {"a": 1}
    assert payload["messages"][0]["created_at"] == "2025-01-01T00:00:00+00:00"

    assert dummy_db.executed
    _, params = dummy_db.executed[0]
    assert params["tenant_id"] == str(tenant_id)
    assert params["conversation_id"] == str(conversation_id)
    assert params["limit"] == 3
    assert params["offset"] == 0


def test_list_widget_messages_conversation_mismatch_returns_403() -> None:
    tenant_id = uuid4()
    session_conversation_id = uuid4()
    other_conversation_id = uuid4()
    dummy_db = DummySession([])
    client = build_app_with_overrides(dummy_db, tenant_id, session_conversation_id)

    response = client.get(
        f"/widget/conversations/{other_conversation_id}/messages?limit=1&offset=0"
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "conversation_mismatch"}
    assert dummy_db.executed == []


def test_list_widget_messages_missing_token_returns_401() -> None:
    app = create_app()
    dummy_db = DummySession([])

    def override_get_db():
        yield dummy_db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get(f"/widget/conversations/{uuid4()}/messages")

    assert response.status_code == 401
    assert response.json() == {"detail": "missing_authorization"}
