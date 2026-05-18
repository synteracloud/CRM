"""Integration tests for public /api/v1/activation endpoints.

Spec: backend/docs/activation-model.md
API standards: backend/docs/api-standards.md
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

import services.activation.http.public as activation_module
from services.activation.service import ActivationOrchestrator
from services.app import app
from services.auth.jwt_deps import TokenClaims, get_current_user

# ── Fixtures ──────────────────────────────────────────────────────────────────

TEST_TENANT = "tenant-act2-001"


def _override_auth():
    return TokenClaims(
        sub="user-act2-001",
        tenant_id=TEST_TENANT,
        role="sales_rep",
        jti=str(uuid.uuid4()),
    )


@pytest.fixture(autouse=True)
def fresh_orchestrator():
    orch = ActivationOrchestrator()
    activation_module.set_orchestrator(orch)
    yield orch
    activation_module.set_orchestrator(ActivationOrchestrator())


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = _override_auth
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def started_client(client: TestClient) -> TestClient:
    client.post("/api/v1/activation/start")
    return client


# ── POST /api/v1/activation/start ────────────────────────────────────────────


class TestStartActivation:
    def test_start_returns_201_with_envelope(self, client: TestClient) -> None:
        r = client.post("/api/v1/activation/start")
        assert r.status_code == 201
        body = r.json()
        assert "data" in body
        assert "meta" in body

    def test_start_seeds_sample_data(self, client: TestClient) -> None:
        r = client.post("/api/v1/activation/start")
        data = r.json()["data"]
        assert data["sample_contacts"] == 5
        assert data["sample_deals"] == 4

    def test_start_creates_pipeline(self, client: TestClient) -> None:
        r = client.post("/api/v1/activation/start")
        pipeline = r.json()["data"]["pipeline"]
        assert pipeline["pipeline_id"] is not None
        assert "New" in pipeline["stages"]

    def test_start_duplicate_tenant_returns_409(self, client: TestClient) -> None:
        client.post("/api/v1/activation/start")
        r = client.post("/api/v1/activation/start")
        assert r.status_code == 409


# ── POST /api/v1/activation/whatsapp-sim ─────────────────────────────────────


class TestWhatsAppSim:
    def test_sim_updates_state(self, started_client: TestClient) -> None:
        r = started_client.post(
            "/api/v1/activation/whatsapp-sim",
            json={"contact_id": "c1"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["first_inbound_at"] is not None

    def test_sim_without_start_returns_404(self, client: TestClient) -> None:
        r = client.post("/api/v1/activation/whatsapp-sim", json={"contact_id": "c1"})
        assert r.status_code == 404


# ── POST /api/v1/activation/move-deal ────────────────────────────────────────


class TestMoveDeal:
    def test_move_deal_advances_stage(self, started_client: TestClient) -> None:
        r = started_client.post(
            "/api/v1/activation/move-deal",
            json={"deal_id": "d1", "to_stage": "Qualified"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["stage"] == "Qualified"

    def test_move_deal_invalid_stage_returns_422(self, started_client: TestClient) -> None:
        r = started_client.post(
            "/api/v1/activation/move-deal",
            json={"deal_id": "d1", "to_stage": "BadStage"},
        )
        assert r.status_code == 422

    def test_move_deal_aha_reached_after_both_steps(self, started_client: TestClient) -> None:
        started_client.post("/api/v1/activation/whatsapp-sim", json={"contact_id": "c1"})
        r = started_client.post(
            "/api/v1/activation/move-deal",
            json={"deal_id": "d1", "to_stage": "Qualified"},
        )
        assert r.json()["data"]["aha_reached"] is True


# ── GET /api/v1/activation/status ────────────────────────────────────────────


class TestActivationStatus:
    def test_status_not_started_returns_404(self, client: TestClient) -> None:
        r = client.get("/api/v1/activation/status")
        assert r.status_code == 404

    def test_status_returns_state_and_metrics(self, started_client: TestClient) -> None:
        r = started_client.get("/api/v1/activation/status")
        assert r.status_code == 200
        data = r.json()["data"]
        assert "state" in data
        assert "checklist" in data
        assert "metrics" in data
