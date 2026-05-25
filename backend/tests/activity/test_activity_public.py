"""Integration tests for public /api/v1/activities endpoints.

Spec: backend/docs/activity-control-model.md
      backend/docs/observability-audit.md
API standards: backend/docs/api-standards.md
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import services.activity.http.public as activity_module
from services.activity.engine import ActivityControlEngine
from services.app import app
from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.base import Base
import services.db.models  # noqa: F401

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


def _override_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()

# ── Fixtures ──────────────────────────────────────────────────────────────────

TEST_TENANT = "tenant-act-001"


def _override_auth():
    return TokenClaims(
        sub="user-act-001",
        tenant_id=TEST_TENANT,
        role="sales_rep",
        jti=str(uuid.uuid4()),
    )


@pytest.fixture(autouse=True)
def fresh_engine():
    eng = ActivityControlEngine()
    activity_module.set_engine(eng)
    yield eng
    activity_module.set_engine(ActivityControlEngine())


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _activity_payload(
    entity_id: str = "lead-001",
    entity_type: str = "lead",
) -> dict:
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "owner_id": "user-act-001",
        "action": "lead.create",
    }


# ── POST /api/v1/activities ───────────────────────────────────────────────────


class TestLogActivity:
    def test_log_returns_201_with_envelope(self, client: TestClient) -> None:
        r = client.post("/api/v1/activities", json=_activity_payload())
        assert r.status_code == 201
        body = r.json()
        assert "data" in body
        assert "meta" in body

    def test_log_registers_new_entity(self, client: TestClient) -> None:
        r = client.post("/api/v1/activities", json=_activity_payload("lead-new"))
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["entity_id"] == "lead-new"

    def test_log_rejects_unsupported_entity_type(self, client: TestClient) -> None:
        payload = _activity_payload()
        payload["entity_type"] = "ticket"
        r = client.post("/api/v1/activities", json=payload)
        assert r.status_code == 422

    def test_log_with_changes_records_mutation(self, client: TestClient) -> None:
        client.post("/api/v1/activities", json=_activity_payload("lead-mut"))
        payload = _activity_payload("lead-mut")
        payload["changes"] = {"state": "qualified"}
        r = client.post("/api/v1/activities", json=payload)
        assert r.status_code == 201


# ── GET /api/v1/activities ────────────────────────────────────────────────────


class TestListActivities:
    def test_empty_feed_returns_200(self, client: TestClient) -> None:
        r = client.get("/api/v1/activities")
        assert r.status_code == 200
        assert r.json()["data"] == []

    def test_feed_contains_logged_events(self, client: TestClient) -> None:
        client.post("/api/v1/activities", json=_activity_payload("lead-f1"))
        client.post("/api/v1/activities", json=_activity_payload("lead-f2"))
        r = client.get("/api/v1/activities")
        assert r.status_code == 200
        assert len(r.json()["data"]) >= 2

    def test_meta_contains_total(self, client: TestClient) -> None:
        client.post("/api/v1/activities", json=_activity_payload())
        r = client.get("/api/v1/activities")
        assert "total_items" in r.json()["meta"]


# ── GET /api/v1/activities/chain-integrity ────────────────────────────────────


class TestChainIntegrity:
    def test_empty_chain_is_valid(self, client: TestClient) -> None:
        r = client.get("/api/v1/activities/chain-integrity")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["valid"] is True
        assert data["entries_checked"] == 0

    def test_chain_valid_after_activity_log(self, client: TestClient) -> None:
        client.post("/api/v1/activities", json=_activity_payload("lead-chain"))
        r = client.get("/api/v1/activities/chain-integrity")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["valid"] is True
        assert data["entries_checked"] >= 1
        assert data["first_broken_seq"] is None
