from __future__ import annotations

import json
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
    def __init__(self, value: UUID | None) -> None:
        self._value = value

    def scalar_one(self) -> UUID:
        return self._value

    def scalar_one_or_none(self) -> UUID | None:
        return self._value


class DummyRowResult:
    def __init__(self, row: tuple | None) -> None:
        self._row = row

    def fetchone(self) -> tuple | None:
        return self._row


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


class DummyIdempotencySession:
    def __init__(self, message_id: UUID) -> None:
        self.message_id = message_id
        self.executed: list[tuple[str, dict]] = []
        self.commits = 0
        self.rollbacks = 0
        self.message_inserts = 0
        self.idempotency_store: dict[tuple[str, str, str], dict[str, object]] = {}

    def execute(self, statement: object, params: dict) -> DummyResult | DummyRowResult:
        sql = str(statement)
        self.executed.append((sql, params))
        if "INSERT INTO idempotency_keys" in sql:
            key = (params["tenant_id"], params["conversation_id"], params["key"])
            if key in self.idempotency_store:
                return DummyResult(None)
            self.idempotency_store[key] = {
                "request_hash": params["request_hash"],
                "response_json": None,
            }
            return DummyResult(uuid4())
        if "SELECT request_hash, response_json FROM idempotency_keys" in sql:
            key = (params["tenant_id"], params["conversation_id"], params["key"])
            record = self.idempotency_store.get(key)
            if record is None:
                return DummyRowResult(None)
            return DummyRowResult((record["request_hash"], record["response_json"]))
        if "UPDATE idempotency_keys SET response_json" in sql:
            key = (params["tenant_id"], params["conversation_id"], params["key"])
            record = self.idempotency_store[key]
            response_json = params["response_json"]
            if isinstance(response_json, str):
                response_json = json.loads(response_json)
            record["response_json"] = response_json
            return DummyResult(None)
        if "INSERT INTO messages" in sql:
            self.message_inserts += 1
            return DummyResult(self.message_id)
        raise AssertionError(f"Unexpected SQL: {sql}")

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

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
    if isinstance(params["meta"], str):
        assert json.loads(params["meta"]) == {"a": 1}
    else:
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


def test_create_widget_message_idempotency_replay_returns_same_message_id() -> None:
    tenant_id = uuid4()
    conversation_id = uuid4()
    message_id = uuid4()
    dummy_db = DummyIdempotencySession(message_id)
    client = build_app_with_overrides(dummy_db, tenant_id, conversation_id)

    headers = {"Idempotency-Key": "demo-key"}
    response_one = client.post(
        "/widget/messages",
        headers=headers,
        json={"text": "hello", "metadata": {"a": 1}},
    )
    response_two = client.post(
        "/widget/messages",
        headers=headers,
        json={"text": "hello", "metadata": {"a": 1}},
    )

    assert response_one.status_code == 200
    assert response_two.status_code == 200
    assert response_one.json() == response_two.json()
    assert dummy_db.message_inserts == 1
    assert dummy_db.commits == 1


def test_create_widget_message_idempotency_conflict_returns_409() -> None:
    tenant_id = uuid4()
    conversation_id = uuid4()
    message_id = uuid4()
    dummy_db = DummyIdempotencySession(message_id)
    client = build_app_with_overrides(dummy_db, tenant_id, conversation_id)

    headers = {"Idempotency-Key": "demo-key"}
    response_one = client.post("/widget/messages", headers=headers, json={"text": "hello"})
    response_two = client.post("/widget/messages", headers=headers, json={"text": "different"})

    assert response_one.status_code == 200
    assert response_two.status_code == 409
    assert response_two.json() == {"detail": "idempotency_key_conflict"}
    assert dummy_db.message_inserts == 1
