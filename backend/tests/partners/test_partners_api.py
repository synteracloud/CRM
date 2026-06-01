"""Integration tests for /api/v1/partners and /deal-registrations endpoints.

Uses FastAPI TestClient + in-memory SQLite.

Spec: backend/docs/domain/partners.md §5
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

from tests.partners._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal


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
        scopes=["partners.read", "partners.manage", "partners.admin"],
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
def manager_client():
    app.dependency_overrides[get_db]           = _override_db
    app.dependency_overrides[get_current_user] = lambda: _make_claims("manager")
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


# ── GET /partners ─────────────────────────────────────────────────────────────

class TestListPartners:
    def test_list_returns_seeded(self, client):
        resp = client.get("/api/v1/partners")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_filter_by_tier(self, client):
        resp = client.get("/api/v1/partners?partner_tier=platinum")
        assert resp.status_code == 200
        for p in resp.json()["data"]:
            assert p["partner_tier"] == "platinum"

    def test_filter_by_status(self, client):
        resp = client.get("/api/v1/partners?status=active")
        assert resp.status_code == 200
        for p in resp.json()["data"]:
            assert p["status"] == "active"


# ── POST /partners ────────────────────────────────────────────────────────────

class TestCreatePartner:
    def test_create_silver_partner(self, client):
        resp = client.post("/api/v1/partners", json={
            "name":         "New Partner Corp",
            "partner_tier": "silver",
            "region":       "Punjab",
            "city":         "Lahore",
        })
        assert resp.status_code == 201
        p = resp.json()["data"]
        assert p["partner_tier"] == "silver"
        assert p["status"]       == "active"
        assert p["commission_due"] == 0

    def test_invalid_tier_422(self, client):
        resp = client.post("/api/v1/partners", json={"name": "X", "partner_tier": "diamond"})
        assert resp.status_code == 422


# ── GET /partners/:id ─────────────────────────────────────────────────────────

class TestGetPartner:
    def test_get_seeded(self, client):
        resp = client.get("/api/v1/partners/p-001")
        assert resp.status_code == 200
        assert resp.json()["data"]["partner_id"] == "p-001"

    def test_get_nonexistent_404(self, client):
        resp = client.get("/api/v1/partners/no-such")
        assert resp.status_code == 404


# ── PATCH /partners/:id ───────────────────────────────────────────────────────

class TestUpdatePartner:
    def test_update_name(self, client):
        resp = client.patch("/api/v1/partners/p-001", json={"name": "NovaTech Updated"})
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "NovaTech Updated"

    def test_manager_cannot_change_tier(self, manager_client):
        resp = manager_client.patch("/api/v1/partners/p-001", json={"partner_tier": "silver"})
        assert resp.status_code == 403

    def test_admin_can_change_tier(self, client):
        resp = client.patch("/api/v1/partners/p-001", json={"partner_tier": "gold"})
        assert resp.status_code == 200
        assert resp.json()["data"]["partner_tier"] == "gold"


# ── GET /partners/:id/commissions ─────────────────────────────────────────────

class TestListCommissions:
    def test_list_seeded_commissions(self, client):
        resp = client.get("/api/v1/partners/p-001/commissions")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) == 3
        statuses = {c["status"] for c in data}
        assert "pending" in statuses
        assert "paid"    in statuses


# ── POST /partners/:id/commissions/:id/approve ────────────────────────────────

class TestApproveCommission:
    def test_approve_pending(self, client):
        resp = client.post("/api/v1/partners/p-001/commissions/com-001/approve")
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "approved"

    def test_approve_paid_returns_409(self, client):
        resp = client.post("/api/v1/partners/p-001/commissions/com-003/approve")
        assert resp.status_code == 409

    def test_approve_nonexistent_404(self, client):
        resp = client.post("/api/v1/partners/p-001/commissions/no-such/approve")
        assert resp.status_code == 404


# ── POST /partners/:id/commissions/:id/pay ────────────────────────────────────

class TestPayCommission:
    def test_pay_approved_commission(self, client):
        resp = client.post(
            "/api/v1/partners/p-001/commissions/com-002/pay",
            json={"payment_reference": "TRF-2026-TEST"},
        )
        assert resp.status_code == 200
        c = resp.json()["data"]
        assert c["status"]            == "paid"
        assert c["payment_reference"] == "TRF-2026-TEST"

    def test_pay_already_paid_409(self, client):
        resp = client.post(
            "/api/v1/partners/p-001/commissions/com-003/pay",
            json={"payment_reference": "TRF-DUPLICATE"},
        )
        assert resp.status_code == 409

    def test_pay_pending_without_approve_422(self, client):
        resp = client.post(
            "/api/v1/partners/p-001/commissions/com-001/pay",
            json={"payment_reference": "TRF-PENDING"},
        )
        assert resp.status_code == 422

    def test_pay_without_reference_422(self, client):
        resp = client.post(
            "/api/v1/partners/p-001/commissions/com-002/pay",
            json={},
        )
        assert resp.status_code == 422


# ── Deal Registrations ────────────────────────────────────────────────────────

class TestDealRegistrations:
    def test_submit_deal_registration(self, client):
        resp = client.post(
            "/api/v1/partners/p-001/deal-registrations",
            json={"prospect_name": "New Client Corp", "estimated_value": 500000},
        )
        assert resp.status_code == 201
        reg = resp.json()["data"]
        assert reg["status"] == "submitted"
        assert reg["expiry_date"] is not None  # platinum → 30 days

    def test_inactive_partner_cannot_register(self, client):
        resp = client.post(
            "/api/v1/partners/p-007/deal-registrations",
            json={"prospect_name": "Test", "estimated_value": 100000},
        )
        assert resp.status_code == 422

    def test_approve_registration(self, client):
        # Submit first
        sub = client.post(
            "/api/v1/partners/p-001/deal-registrations",
            json={"prospect_name": "Approve Test", "estimated_value": 200000},
        )
        reg_id = sub.json()["data"]["registration_id"]
        approve_resp = client.post(f"/api/v1/deal-registrations/{reg_id}/approve")
        assert approve_resp.status_code == 200
        assert approve_resp.json()["data"]["status"] == "approved"

    def test_reject_registration(self, client):
        sub = client.post(
            "/api/v1/partners/p-002/deal-registrations",
            json={"prospect_name": "Reject Test", "estimated_value": 100000},
        )
        reg_id = sub.json()["data"]["registration_id"]
        reject_resp = client.post(
            f"/api/v1/deal-registrations/{reg_id}/reject",
            json={"rejection_reason": "Already in pipeline"},
        )
        assert reject_resp.status_code == 200
        assert reject_resp.json()["data"]["status"] == "rejected"
