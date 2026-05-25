"""Integration tests for public /api/v1/followups endpoints.

Uses FastAPI TestClient + in-memory SQLite database.
JWT auth is overridden with a test fixture.

Spec: backend/docs/followup-enforcement-model.md
API standards: backend/docs/api-standards.md
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.app import app
from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.base import Base
# Import all models so they are registered with Base.metadata
import services.db.models  # noqa: F401

# ── In-memory test DB ─────────────────────────────────────────────────────────
# StaticPool forces all sessions to share one connection, keeping in-memory
# SQLite tables visible across the test lifecycle.

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


def _override_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── JWT override ──────────────────────────────────────────────────────────────

TEST_TENANT = "tenant-test-001"
TEST_USER   = "user-test-001"


def _override_auth():
    return TokenClaims(sub=TEST_USER, tenant_id=TEST_TENANT, role="sales_rep", jti=str(uuid.uuid4()))


def _override_auth_manager():
    return TokenClaims(sub=TEST_USER, tenant_id=TEST_TENANT, role="manager", jti=str(uuid.uuid4()))


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_auth
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_manager():
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_auth_manager
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helpers ───────────────────────────────────────────────────────────────────


def _create_payload(
    lead_id: str = "lead-001",
    rule_type: str = "TimeBased",
) -> dict:
    return {
        "lead_id": lead_id,
        "owner_user_id": TEST_USER,
        "rule_type": rule_type,
        "due_at": datetime.now(timezone.utc).isoformat(),
    }


# ── POST /api/v1/followups ────────────────────────────────────────────────────


class TestCreateFollowup:
    def test_create_returns_201_with_data_envelope(self, client: TestClient) -> None:
        r = client.post("/api/v1/followups", json=_create_payload())
        assert r.status_code == 201
        body = r.json()
        assert "data" in body
        assert "meta" in body
        assert body["data"]["state"] == "pending"

    def test_create_assigns_correct_tenant(self, client: TestClient) -> None:
        r = client.post("/api/v1/followups", json=_create_payload())
        assert r.json()["data"]["tenant_id"] == TEST_TENANT

    def test_create_stores_lead_id_and_owner(self, client: TestClient) -> None:
        r = client.post("/api/v1/followups", json=_create_payload(lead_id="lead-xyz"))
        data = r.json()["data"]
        assert data["lead_id"] == "lead-xyz"
        assert data["owner_id"] == TEST_USER

    def test_create_rejects_invalid_rule_type(self, client: TestClient) -> None:
        r = client.post("/api/v1/followups", json=_create_payload(rule_type="BadType"))
        assert r.status_code == 422


# ── GET /api/v1/followups ─────────────────────────────────────────────────────


class TestListFollowups:
    def test_empty_list_returns_200(self, client: TestClient) -> None:
        r = client.get("/api/v1/followups")
        assert r.status_code == 200
        assert r.json()["data"] == []

    def test_list_returns_created_tasks(self, client: TestClient) -> None:
        client.post("/api/v1/followups", json=_create_payload("lead-a"))
        client.post("/api/v1/followups", json=_create_payload("lead-b"))
        r = client.get("/api/v1/followups")
        assert r.status_code == 200
        assert len(r.json()["data"]) == 2

    def test_list_pagination(self, client: TestClient) -> None:
        for i in range(5):
            client.post("/api/v1/followups", json=_create_payload(f"lead-{i}"))
        r = client.get("/api/v1/followups?page=1&page_size=3")
        assert r.status_code == 200
        assert len(r.json()["data"]) == 3

    def test_list_filter_by_lead_id(self, client: TestClient) -> None:
        client.post("/api/v1/followups", json=_create_payload("lead-alpha"))
        client.post("/api/v1/followups", json=_create_payload("lead-beta"))
        r = client.get("/api/v1/followups?lead_id=lead-alpha")
        assert r.status_code == 200
        data = r.json()["data"]
        assert all(t["lead_id"] == "lead-alpha" for t in data)

    def test_meta_contains_total_page_info(self, client: TestClient) -> None:
        client.post("/api/v1/followups", json=_create_payload())
        r = client.get("/api/v1/followups")
        meta = r.json()["meta"]
        assert "total_items" in meta
        assert "total_pages" in meta
        assert "page" in meta
        assert "page_size" in meta


# ── GET /api/v1/followups/{id} ────────────────────────────────────────────────


class TestGetFollowup:
    def test_get_returns_200_with_envelope(self, client: TestClient) -> None:
        created = client.post("/api/v1/followups", json=_create_payload()).json()
        task_id = created["data"]["task_id"]
        r = client.get(f"/api/v1/followups/{task_id}")
        assert r.status_code == 200
        assert r.json()["data"]["task_id"] == task_id

    def test_get_unknown_id_returns_404(self, client: TestClient) -> None:
        r = client.get(f"/api/v1/followups/{uuid.uuid4()}")
        assert r.status_code == 404


# ── PATCH /api/v1/followups/{id}/complete ────────────────────────────────────


class TestCompleteFollowup:
    def test_complete_sets_state_and_timestamp(self, client: TestClient) -> None:
        task_id = client.post("/api/v1/followups", json=_create_payload()).json()["data"]["task_id"]
        r = client.patch(f"/api/v1/followups/{task_id}/complete", json={})
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["state"] == "completed"
        assert data["completed_at"] is not None

    def test_complete_with_activity_id(self, client: TestClient) -> None:
        task_id = client.post("/api/v1/followups", json=_create_payload()).json()["data"]["task_id"]
        r = client.patch(
            f"/api/v1/followups/{task_id}/complete",
            json={"completed_activity_id": "activity-789"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["completed_activity_id"] == "activity-789"

    def test_complete_already_completed_returns_409(self, client: TestClient) -> None:
        task_id = client.post("/api/v1/followups", json=_create_payload()).json()["data"]["task_id"]
        client.patch(f"/api/v1/followups/{task_id}/complete", json={})
        r = client.patch(f"/api/v1/followups/{task_id}/complete", json={})
        assert r.status_code == 409

    def test_complete_unknown_id_returns_404(self, client: TestClient) -> None:
        r = client.patch(f"/api/v1/followups/{uuid.uuid4()}/complete", json={})
        assert r.status_code == 404


# ── POST /api/v1/followups/{id}/escalate ─────────────────────────────────────


class TestEscalateFollowup:
    def test_escalate_creates_escalation_record(self, client_manager: TestClient) -> None:
        task_id = client_manager.post("/api/v1/followups", json=_create_payload()).json()["data"]["task_id"]
        r = client_manager.post(
            f"/api/v1/followups/{task_id}/escalate",
            json={"reason": "No response for 24h", "escalation_level": "warning"},
        )
        assert r.status_code == 201
        body = r.json()
        assert body["data"]["escalation"]["escalation_level"] == "warning"
        assert body["data"]["task"]["escalation_level"] == "warning"

    def test_escalate_updates_task_level(self, client_manager: TestClient) -> None:
        task_id = client_manager.post("/api/v1/followups", json=_create_payload()).json()["data"]["task_id"]
        client_manager.post(
            f"/api/v1/followups/{task_id}/escalate",
            json={"reason": "Manager escalation", "escalation_level": "escalated"},
        )
        r = client_manager.get(f"/api/v1/followups/{task_id}")
        assert r.json()["data"]["escalation_level"] == "escalated"

    def test_escalate_invalid_level_returns_422(self, client_manager: TestClient) -> None:
        task_id = client_manager.post("/api/v1/followups", json=_create_payload()).json()["data"]["task_id"]
        r = client_manager.post(
            f"/api/v1/followups/{task_id}/escalate",
            json={"reason": "test", "escalation_level": "invalid_level"},
        )
        assert r.status_code == 422

    def test_escalate_completed_task_returns_409(self, client_manager: TestClient) -> None:
        task_id = client_manager.post("/api/v1/followups", json=_create_payload()).json()["data"]["task_id"]
        client_manager.patch(f"/api/v1/followups/{task_id}/complete", json={})
        r = client_manager.post(
            f"/api/v1/followups/{task_id}/escalate",
            json={"reason": "test", "escalation_level": "reminder"},
        )
        assert r.status_code == 409

    def test_escalate_unknown_id_returns_404(self, client_manager: TestClient) -> None:
        r = client_manager.post(
            f"/api/v1/followups/{uuid.uuid4()}/escalate",
            json={"reason": "test", "escalation_level": "reminder"},
        )
        assert r.status_code == 404

    def test_sales_rep_cannot_escalate(self, client: TestClient) -> None:
        task_id = client.post("/api/v1/followups", json=_create_payload()).json()["data"]["task_id"]
        r = client.post(
            f"/api/v1/followups/{task_id}/escalate",
            json={"reason": "test", "escalation_level": "reminder"},
        )
        assert r.status_code == 403
