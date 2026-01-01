from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test")
os.environ.setdefault("WIDGET_SESSION_JWT_SECRET", "test-secret")
os.environ.setdefault("WIDGET_SESSION_JWT_ALG", "HS256")
os.environ.setdefault("WIDGET_SESSION_TTL_MINUTES", "10")

from app.main import create_app  # noqa: E402


def test_request_id_generated_and_returned() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("x-request-id")


def test_request_id_respects_incoming_header() -> None:
    client = TestClient(create_app())
    request_id = "test-request-id-123"

    response = client.get("/health", headers={"X-Request-Id": request_id})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == request_id


def test_metrics_endpoint_exposes_counters() -> None:
    client = TestClient(create_app())

    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    body = response.text
    assert "http_requests_total" in body
    assert "http_request_duration_ms_sum" in body
    assert "http_request_duration_ms_count" in body
