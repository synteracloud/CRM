"""Integration tests for /api/v1/campaigns, /segments, /templates endpoints.

Uses FastAPI TestClient + in-memory SQLite.

Spec: backend/docs/domain/marketing-campaigns.md §7
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


def _make_claims(role: str = "manager") -> TokenClaims:
    return TokenClaims(
        sub=TEST_USER,
        tenant_id=TEST_TENANT,
        role=role,
        scopes=["campaigns.read", "campaigns.manage"],
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


# ── GET /campaigns ────────────────────────────────────────────────────────────

class TestListCampaigns:
    def test_list_returns_seeded(self, client):
        resp = client.get("/api/v1/campaigns")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_filter_by_status(self, client):
        resp = client.get("/api/v1/campaigns?status=active")
        assert resp.status_code == 200
        for c in resp.json()["data"]:
            assert c["status"] == "active"

    def test_filter_by_type(self, client):
        resp = client.get("/api/v1/campaigns?type=email")
        assert resp.status_code == 200
        for c in resp.json()["data"]:
            assert c["type"] == "email"


# ── POST /campaigns ───────────────────────────────────────────────────────────

class TestCreateCampaign:
    def test_create_draft(self, client):
        resp = client.post("/api/v1/campaigns", json={"name": "Test Campaign", "type": "email"})
        assert resp.status_code == 201
        assert resp.json()["data"]["status"] == "draft"

    def test_invalid_type_422(self, client):
        resp = client.post("/api/v1/campaigns", json={"name": "X", "type": "telegram"})
        assert resp.status_code == 422

    def test_missing_name_422(self, client):
        resp = client.post("/api/v1/campaigns", json={"type": "email"})
        assert resp.status_code == 422


# ── POST /campaigns/:id/activate ─────────────────────────────────────────────

class TestActivateCampaign:
    def test_activate_draft_with_segment_and_template(self, client):
        resp = client.post(
            "/api/v1/campaigns/cmp-005/activate",
        )
        # cmp-005 has no segment_id — should fail activation
        assert resp.status_code == 422
        assert "segment_id" in resp.json()["message"].lower() or "ACTIVATION_BLOCKED" in resp.json().get("code", "")

    def test_activate_ready_campaign(self, client):
        # cmp-003 is already active — try activating cmp-006 (paused → active not via activate)
        # Create a new campaign with segment+template, then activate
        create_resp = client.post("/api/v1/campaigns", json={
            "name": "Ready Campaign",
            "type": "email",
            "segment_id":  "seg-001",
            "template_id": "tpl-002",
        })
        cid = create_resp.json()["data"]["campaign_id"]
        activate_resp = client.post(f"/api/v1/campaigns/{cid}/activate")
        assert activate_resp.status_code == 200
        assert activate_resp.json()["data"]["status"] == "active"


# ── POST /campaigns/:id/pause ─────────────────────────────────────────────────

class TestPauseCampaign:
    def test_pause_active(self, client):
        resp = client.post("/api/v1/campaigns/cmp-003/pause")
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "paused"

    def test_pause_draft_blocked(self, client):
        resp = client.post("/api/v1/campaigns/cmp-005/pause")
        assert resp.status_code == 422


# ── POST /campaigns/:id/resume ────────────────────────────────────────────────

class TestResumeCampaign:
    def test_resume_paused(self, client):
        resp = client.post("/api/v1/campaigns/cmp-006/resume")
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "active"

    def test_resume_active_blocked(self, client):
        resp = client.post("/api/v1/campaigns/cmp-003/resume")
        assert resp.status_code == 422


# ── POST /campaigns/:id/cancel ────────────────────────────────────────────────

class TestCancelCampaign:
    def test_cancel_draft(self, client):
        resp = client.post("/api/v1/campaigns/cmp-005/cancel")
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "cancelled"

    def test_cancel_completed_blocked(self, client):
        resp = client.post("/api/v1/campaigns/cmp-001/cancel")
        assert resp.status_code == 422


# ── GET /segments ─────────────────────────────────────────────────────────────

class TestListSegments:
    def test_list_returns_seeded(self, client):
        resp = client.get("/api/v1/segments")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_create_segment(self, client):
        resp = client.post("/api/v1/segments", json={
            "name": "Karachi Leads",
            "entity_type": "lead",
            "rules": [{"rule_id": "r1", "field": "lead.city", "operator": "eq", "value": "Karachi"}],
        })
        assert resp.status_code == 201
        assert resp.json()["data"]["entity_type"] == "lead"

    def test_invalid_entity_type_422(self, client):
        resp = client.post("/api/v1/segments", json={"name": "X", "entity_type": "opportunity"})
        assert resp.status_code == 422


# ── POST /segments/:id/validate ───────────────────────────────────────────────

class TestValidateSegment:
    def test_validate_returns_size_and_sample(self, client):
        resp = client.post("/api/v1/segments/seg-001/validate")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "estimated_size" in data
        assert "sample" in data
        assert data["estimated_size"] > 0

    def test_validate_nonexistent_404(self, client):
        resp = client.post("/api/v1/segments/no-such/validate")
        assert resp.status_code == 404


# ── GET /templates ────────────────────────────────────────────────────────────

class TestListTemplates:
    def test_list_returns_seeded(self, client):
        resp = client.get("/api/v1/templates")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_filter_by_channel(self, client):
        resp = client.get("/api/v1/templates?channel=email")
        assert resp.status_code == 200
        for t in resp.json()["data"]:
            assert t["channel"] == "email"

    def test_create_template(self, client):
        resp = client.post("/api/v1/templates", json={
            "name":    "Welcome SMS",
            "channel": "sms",
            "body":    "Welcome {{contact.name}}! Reply HELP for support.",
        })
        assert resp.status_code == 201
        t = resp.json()["data"]
        assert t["channel"] == "sms"
        assert t["is_urdu"] is False

    def test_create_urdu_template_sets_is_urdu(self, client):
        resp = client.post("/api/v1/templates", json={
            "name":     "Urdu Welcome",
            "channel":  "whatsapp_broadcast",
            "language": "ur",
            "body":     "خوش آمدید!",
        })
        assert resp.status_code == 201
        assert resp.json()["data"]["is_urdu"] is True
        assert resp.json()["data"]["meta_template_status"] == "pending"
