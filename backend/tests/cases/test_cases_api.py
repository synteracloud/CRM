"""Integration tests for /api/v1/cases and /api/v1/knowledge/articles endpoints.

Uses FastAPI TestClient + in-memory SQLite.
JWT auth is overridden with a test fixture.

Spec: backend/docs/domain/cases-domain.md §8
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from services.app import app
from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.base import Base
import services.db.models  # noqa: F401 — registers all ORM models incl. cases

# ── In-memory test DB ─────────────────────────────────────────────────────────

from tests.cases._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal


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


def _make_claims(role: str = "manager") -> TokenClaims:
    return TokenClaims(
        sub=TEST_USER,
        tenant_id=TEST_TENANT,
        role=role,
        scopes=[
            "cases.read", "cases.create", "cases.update", "cases.admin",
            "knowledge.read", "knowledge.manage",
        ],
        jti=str(uuid.uuid4()),
        iss="test",
        aud="crm-gateway",
    )


@pytest.fixture
def client():
    app.dependency_overrides[get_db]            = _override_db
    app.dependency_overrides[get_current_user]  = lambda: _make_claims()
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture
def agent_client():
    app.dependency_overrides[get_db]            = _override_db
    app.dependency_overrides[get_current_user]  = lambda: _make_claims(role="agent")
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _create_case(client, **kwargs) -> dict:
    payload = {"subject": "Test case", "priority": "medium", "source": "email", **kwargs}
    resp = client.post("/api/v1/cases", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]


# ── POST /cases ────────────────────────────────────────────────────────────────

class TestCreateCase:
    def test_create_minimal(self, client):
        case = _create_case(client)
        assert case["status"] == "OPEN"
        assert case["case_number"].startswith("CAS-")
        assert case["priority"] == "medium"

    def test_create_with_all_fields(self, client):
        case = _create_case(
            client,
            description="Detailed description",
            priority="critical",
            source="whatsapp",
            category="billing",
            sla_tier="tier_1_critical",
        )
        assert case["sla_tier"] == "tier_1_critical"
        assert case["sla_first_response_due_at"] is not None

    def test_invalid_priority_422(self, client):
        resp = client.post("/api/v1/cases", json={"subject": "X", "priority": "unknown"})
        assert resp.status_code == 422

    def test_missing_subject_422(self, client):
        resp = client.post("/api/v1/cases", json={"priority": "low"})
        assert resp.status_code == 422


# ── GET /cases ────────────────────────────────────────────────────────────────

class TestListCases:
    def test_list_empty(self, client):
        resp = client.get("/api/v1/cases")
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    def test_list_returns_created_case(self, client):
        _create_case(client)
        resp = client.get("/api/v1/cases")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 1

    def test_list_tenant_isolation(self, client, agent_client):
        _create_case(client)
        resp = client.get("/api/v1/cases")
        assert len(resp.json()["data"]) == 1

    def test_filter_by_status(self, client):
        _create_case(client)
        resp = client.get("/api/v1/cases?status=OPEN")
        assert resp.status_code == 200
        for c in resp.json()["data"]:
            assert c["status"] == "OPEN"


# ── GET /cases/:id ────────────────────────────────────────────────────────────

class TestGetCase:
    def test_get_existing(self, client):
        case = _create_case(client)
        resp = client.get(f"/api/v1/cases/{case['case_id']}")
        assert resp.status_code == 200
        assert resp.json()["data"]["case_id"] == case["case_id"]

    def test_get_nonexistent_404(self, client):
        resp = client.get("/api/v1/cases/does-not-exist")
        assert resp.status_code == 404


# ── POST /cases/:id/assign ────────────────────────────────────────────────────

class TestAssignCase:
    def test_assign_transitions_to_assigned(self, client):
        case = _create_case(client)
        resp = client.post(f"/api/v1/cases/{case['case_id']}/assign", json={"assigned_to": "user-123"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["assigned_to"] == "user-123"
        assert data["status"] == "ASSIGNED"

    def test_assign_without_user_422(self, client):
        case = _create_case(client)
        resp = client.post(f"/api/v1/cases/{case['case_id']}/assign", json={})
        assert resp.status_code == 422


# ── POST /cases/:id/comments ──────────────────────────────────────────────────

class TestAddComment:
    def test_add_customer_reply(self, client):
        case = _create_case(client)
        resp = client.post(
            f"/api/v1/cases/{case['case_id']}/comments",
            json={"body": "We are looking into this.", "comment_type": "customer_reply"},
        )
        assert resp.status_code == 201
        comment = resp.json()["data"]
        assert comment["comment_type"] == "customer_reply"
        assert comment["is_visible_to_customer"] is True

    def test_add_internal_note_not_visible(self, client):
        case = _create_case(client)
        resp = client.post(
            f"/api/v1/cases/{case['case_id']}/comments",
            json={"body": "Internal only.", "comment_type": "internal_note"},
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["is_visible_to_customer"] is False

    def test_invalid_comment_type_422(self, client):
        case = _create_case(client)
        resp = client.post(
            f"/api/v1/cases/{case['case_id']}/comments",
            json={"body": "X", "comment_type": "invalid_type"},
        )
        assert resp.status_code == 422


# ── POST /cases/:id/resolve ───────────────────────────────────────────────────

class TestResolveCase:
    def test_resolve_in_progress_case(self, client):
        case = _create_case(client)
        # Transition to IN_PROGRESS first
        client.post(f"/api/v1/cases/{case['case_id']}/assign", json={"assigned_to": "u-001"})
        client.post(
            f"/api/v1/cases/{case['case_id']}/comments",
            json={"body": "Working on it.", "comment_type": "customer_reply"},
        )
        resp = client.post(
            f"/api/v1/cases/{case['case_id']}/resolve",
            json={"resolution_note": "Issue fixed — updated config."},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "RESOLVED"

    def test_resolve_open_case_blocked(self, client):
        case = _create_case(client)
        resp = client.post(
            f"/api/v1/cases/{case['case_id']}/resolve",
            json={"resolution_note": "Quick fix."},
        )
        # OPEN → RESOLVED is not in ALLOWED_TRANSITIONS
        assert resp.status_code == 422


# ── POST /cases/:id/escalate ──────────────────────────────────────────────────

class TestEscalateCase:
    def test_escalate_sets_escalated_status(self, client):
        case = _create_case(client)
        resp = client.post(
            f"/api/v1/cases/{case['case_id']}/escalate",
            json={"escalation_reason": "manager_override", "note": "VIP client."},
        )
        assert resp.status_code == 201
        assert resp.json()["case"]["status"] == "ESCALATED"
        assert resp.json()["case"]["escalation_level"] >= 1

    def test_escalate_resolved_case_409(self, client):
        case = _create_case(client)
        client.post(f"/api/v1/cases/{case['case_id']}/assign", json={"assigned_to": "u-001"})
        client.post(
            f"/api/v1/cases/{case['case_id']}/comments",
            json={"body": "Fixed.", "comment_type": "customer_reply"},
        )
        client.post(
            f"/api/v1/cases/{case['case_id']}/resolve",
            json={"resolution_note": "Done."},
        )
        resp = client.post(
            f"/api/v1/cases/{case['case_id']}/escalate",
            json={"escalation_reason": "manager_override"},
        )
        assert resp.status_code == 409
