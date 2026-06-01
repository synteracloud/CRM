"""Integration tests for /api/v1/inbox endpoints.

Uses FastAPI TestClient + in-memory SQLite.
JWT auth overridden with test fixture.

Spec: backend/docs/domain/shared-inbox.md §7
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from services.app import app
from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.base import Base
import services.db.models  # noqa: F401

from tests.inbox._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal


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
        scopes=["inbox.read", "inbox.write", "inbox.admin"],
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


@pytest.fixture
def agent_client():
    app.dependency_overrides[get_db]           = _override_db
    app.dependency_overrides[get_current_user] = lambda: _make_claims(role="agent")
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


# ── GET /inbox/conversations ──────────────────────────────────────────────────

class TestListConversations:
    def test_list_returns_200(self, client):
        resp = client.get("/api/v1/inbox/conversations")
        assert resp.status_code == 200
        assert isinstance(resp.json()["data"], list)

    def test_filter_by_channel(self, client):
        resp = client.get("/api/v1/inbox/conversations?channel=whatsapp")
        assert resp.status_code == 200
        for c in resp.json()["data"]:
            assert c["channel"] == "whatsapp"

    def test_filter_by_state(self, client):
        resp = client.get("/api/v1/inbox/conversations?state=open")
        assert resp.status_code == 200
        for c in resp.json()["data"]:
            assert c["state"] == "open"


# ── GET /inbox/conversations/:id ──────────────────────────────────────────────

class TestGetConversation:
    def test_get_seeded_conv(self, client):
        resp = client.get("/api/v1/inbox/conversations/th-001")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["conversation_id"] == "th-001"
        assert "messages" in data

    def test_get_nonexistent_404(self, client):
        resp = client.get("/api/v1/inbox/conversations/does-not-exist")
        assert resp.status_code == 404


# ── POST /inbox/conversations/:id/claim ───────────────────────────────────────

class TestClaimConversation:
    def test_claim_unassigned_succeeds(self, client):
        resp = client.post("/api/v1/inbox/conversations/th-003/claim")
        assert resp.status_code == 200
        assert resp.json()["data"]["assigned_agent_id"] == TEST_USER

    def test_claim_already_assigned_409(self, client):
        # th-001 is already assigned to u-001
        resp = client.post("/api/v1/inbox/conversations/th-001/claim")
        assert resp.status_code == 409

    def test_claim_nonexistent_404(self, client):
        resp = client.post("/api/v1/inbox/conversations/no-such/claim")
        assert resp.status_code == 404


# ── POST /inbox/conversations/:id/handoff ─────────────────────────────────────

class TestHandoffConversation:
    def test_handoff_to_pool(self, client):
        resp = client.post(
            "/api/v1/inbox/conversations/th-001/handoff",
            json={"to_agent_id": None, "reason": "manual"},
        )
        assert resp.status_code == 201
        assert resp.json()["conversation"]["assigned_agent_id"] is None

    def test_handoff_to_agent(self, client):
        resp = client.post(
            "/api/v1/inbox/conversations/th-001/handoff",
            json={"to_agent_id": "u-002", "reason": "skill_match"},
        )
        assert resp.status_code == 201
        assert resp.json()["conversation"]["assigned_agent_id"] == "u-002"
        assert resp.json()["conversation"]["handoff_count"] == 1

    def test_invalid_reason_422(self, client):
        resp = client.post(
            "/api/v1/inbox/conversations/th-001/handoff",
            json={"to_agent_id": "u-002", "reason": "invalid_reason"},
        )
        assert resp.status_code == 422


# ── POST /inbox/conversations/:id/messages ────────────────────────────────────

class TestSendMessage:
    def test_send_on_assigned_conv(self, client):
        # th-001 assigned to u-001; TEST_USER is manager (supervisor can send)
        resp = client.post(
            "/api/v1/inbox/conversations/th-001/messages",
            json={"text": "Hello, I am looking into this for you."},
        )
        assert resp.status_code == 201
        msg = resp.json()["data"]
        assert msg["direction"] == "outbound"
        assert msg["text"] == "Hello, I am looking into this for you."

    def test_send_empty_text_422(self, client):
        resp = client.post(
            "/api/v1/inbox/conversations/th-001/messages",
            json={},
        )
        assert resp.status_code == 422


# ── PATCH /inbox/presence ─────────────────────────────────────────────────────

class TestUpdatePresence:
    def test_set_online(self, client):
        resp = client.patch("/api/v1/inbox/presence", json={"status": "online"})
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "online"

    def test_set_away(self, client):
        resp = client.patch("/api/v1/inbox/presence", json={"status": "away"})
        assert resp.status_code == 200

    def test_invalid_status_422(self, client):
        resp = client.patch("/api/v1/inbox/presence", json={"status": "invisible"})
        assert resp.status_code == 422


# ── GET /inbox/queues ─────────────────────────────────────────────────────────

class TestListQueues:
    def test_list_returns_seeded_queues(self, client):
        resp = client.get("/api/v1/inbox/queues")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_queue_has_expected_fields(self, client):
        resp = client.get("/api/v1/inbox/queues")
        q = resp.json()["data"][0]
        assert "queue_id" in q
        assert "routing_strategy" in q
        assert "auto_assign" in q


# ── GET /inbox/queues/:id/stats ───────────────────────────────────────────────

class TestQueueStats:
    def test_stats_returns_counts(self, client):
        resp = client.get("/api/v1/inbox/queues/q-001/stats")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "open_count" in data
        assert "unassigned_count" in data
        assert "assigned_count" in data

    def test_nonexistent_queue_404(self, client):
        resp = client.get("/api/v1/inbox/queues/no-such/stats")
        assert resp.status_code == 404
