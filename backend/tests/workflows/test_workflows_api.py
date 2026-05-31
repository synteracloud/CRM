"""Integration tests for /api/v1/workflows endpoints.

Uses FastAPI TestClient + in-memory SQLite.

Spec: backend/docs/infrastructure/workflow-catalog.md §12
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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


TEST_TENANT = "tenant-test-001"
TEST_USER   = "user-test-001"


def _make_claims(role: str = "admin") -> TokenClaims:
    return TokenClaims(
        sub=TEST_USER,
        tenant_id=TEST_TENANT,
        role=role,
        scopes=["workflows.read", "workflows.manage"],
        jti=str(uuid.uuid4()),
        iss="test",
        aud="crm-gateway",
    )


@pytest.fixture
def client():
    app.dependency_overrides[get_db]           = _override_db
    app.dependency_overrides[get_current_user] = lambda: _make_claims()
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


# ── GET /workflows ────────────────────────────────────────────────────────────

class TestListWorkflows:
    def test_list_returns_seeded(self, client):
        resp = client.get("/api/v1/workflows")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_filter_by_status(self, client):
        resp = client.get("/api/v1/workflows?status=active")
        assert resp.status_code == 200
        for w in resp.json()["data"]:
            assert w["status"] == "active"


# ── POST /workflows ───────────────────────────────────────────────────────────

class TestCreateWorkflow:
    def test_create_draft(self, client):
        resp = client.post("/api/v1/workflows", json={
            "name":           "My Custom Workflow",
            "trigger_events": ["lead.created.v1"],
            "steps_dsl": [
                {"id": "s1", "type": "action", "name": "Do something", "action": "log_event"}
            ],
        })
        assert resp.status_code == 201
        w = resp.json()["data"]
        assert w["status"] == "draft"
        assert w["name"]   == "My Custom Workflow"

    def test_empty_trigger_events_422(self, client):
        resp = client.post("/api/v1/workflows", json={
            "name": "No Triggers",
            "trigger_events": [],
        })
        assert resp.status_code == 422

    def test_missing_name_422(self, client):
        resp = client.post("/api/v1/workflows", json={"trigger_events": ["lead.idle.v1"]})
        assert resp.status_code == 422


# ── GET /workflows/:id ────────────────────────────────────────────────────────

class TestGetWorkflow:
    def test_get_seeded(self, client):
        resp = client.get("/api/v1/workflows/wf-001")
        assert resp.status_code == 200
        assert resp.json()["data"]["workflow_key"] == "lead_followup_enforcement"

    def test_get_nonexistent_404(self, client):
        resp = client.get("/api/v1/workflows/no-such")
        assert resp.status_code == 404


# ── POST /workflows/:id/publish ───────────────────────────────────────────────

class TestPublishWorkflow:
    def test_publish_draft_with_steps(self, client):
        create_resp = client.post("/api/v1/workflows", json={
            "name":           "Publishable Workflow",
            "trigger_events": ["test.event.v1"],
            "steps_dsl": [{"id": "s1", "type": "action", "name": "Step 1", "action": "do_it"}],
        })
        wid = create_resp.json()["data"]["workflow_id"]
        pub_resp = client.post(f"/api/v1/workflows/{wid}/publish")
        assert pub_resp.status_code == 200
        assert pub_resp.json()["data"]["status"] == "active"

    def test_publish_draft_without_steps_422(self, client):
        create_resp = client.post("/api/v1/workflows", json={
            "name": "Empty Workflow",
            "trigger_events": ["test.event.v1"],
        })
        wid = create_resp.json()["data"]["workflow_id"]
        pub_resp = client.post(f"/api/v1/workflows/{wid}/publish")
        assert pub_resp.status_code == 422

    def test_cannot_publish_system_workflow_that_is_already_active(self, client):
        # wf-001 is already active
        resp = client.post("/api/v1/workflows/wf-001/publish")
        assert resp.status_code == 422  # already active → can't transition active→active


# ── POST /workflows/:id/simulate ──────────────────────────────────────────────

class TestSimulateWorkflow:
    def test_simulate_returns_steps(self, client):
        resp = client.post(
            "/api/v1/workflows/wf-001/simulate",
            json={"trigger_payload": {"lead_id": "l-001"}},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["simulated"] is True
        assert len(data["steps"]) == 3  # wf-001 has 3 steps

    def test_simulate_nonexistent_404(self, client):
        resp = client.post("/api/v1/workflows/no-such/simulate", json={})
        assert resp.status_code == 404


# ── GET /workflows/runs ───────────────────────────────────────────────────────

class TestListRuns:
    def test_list_returns_seeded(self, client):
        resp = client.get("/api/v1/workflows/runs")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_filter_by_status(self, client):
        resp = client.get("/api/v1/workflows/runs?status=failed")
        assert resp.status_code == 200
        for e in resp.json()["data"]:
            assert e["status"] == "failed"

    def test_filter_by_workflow_key(self, client):
        resp = client.get("/api/v1/workflows/runs?workflow_key=lead_followup_enforcement")
        assert resp.status_code == 200
        for e in resp.json()["data"]:
            assert e["workflow_key"] == "lead_followup_enforcement"


# ── GET /workflows/runs/:id ───────────────────────────────────────────────────

class TestGetRun:
    def test_get_execution_with_steps(self, client):
        resp = client.get("/api/v1/workflows/runs/exec-007")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["execution_id"] == "exec-007"
        assert "steps" in data
        assert len(data["steps"]) == 3

    def test_get_nonexistent_404(self, client):
        resp = client.get("/api/v1/workflows/runs/no-such")
        assert resp.status_code == 404


# ── POST /workflows/runs/:id/retry ────────────────────────────────────────────

class TestRetryExecution:
    def test_retry_failed_creates_new_run(self, client):
        resp = client.post("/api/v1/workflows/runs/exec-002/retry")
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["status"]              == "running"
        assert data["retry_count"]         == 1
        assert data["parent_execution_id"] == "exec-002"

    def test_retry_succeeded_422(self, client):
        resp = client.post("/api/v1/workflows/runs/exec-001/retry")
        assert resp.status_code == 422

    def test_retry_nonexistent_404(self, client):
        resp = client.post("/api/v1/workflows/runs/no-such/retry")
        assert resp.status_code == 404


# ── POST /workflows/runs/:id/cancel ──────────────────────────────────────────

class TestCancelExecution:
    def test_cancel_running(self, client):
        resp = client.post("/api/v1/workflows/runs/exec-008/cancel")
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "cancelled"

    def test_cancel_already_succeeded_409(self, client):
        resp = client.post("/api/v1/workflows/runs/exec-001/cancel")
        assert resp.status_code == 409
