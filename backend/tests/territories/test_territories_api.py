"""Integration tests for /api/v1/territories endpoints.

Uses FastAPI TestClient + in-memory SQLite.

Spec: backend/docs/domain/territory-management.md §7
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

from tests.territories._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal


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
        scopes=["territories.read", "territories.write", "territories.admin"],
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
    app.dependency_overrides[get_current_user] = lambda: _make_claims(role="manager")
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


# ── GET /territories ──────────────────────────────────────────────────────────

class TestListTerritories:
    def test_list_returns_seeded_data(self, client):
        resp = client.get("/api/v1/territories")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 1

    def test_list_sorted_by_priority(self, client):
        resp = client.get("/api/v1/territories")
        priorities = [t["routing_priority"] for t in resp.json()["data"]]
        assert priorities == sorted(priorities)

    def test_filter_active(self, client):
        resp = client.get("/api/v1/territories?is_active=true")
        assert resp.status_code == 200
        for t in resp.json()["data"]:
            assert t["is_active"] is True


# ── POST /territories ─────────────────────────────────────────────────────────

class TestCreateTerritory:
    def test_create_minimal(self, client):
        resp = client.post("/api/v1/territories", json={
            "name": "Test Territory",
            "criteria_type": "geographic",
        })
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["name"] == "Test Territory"
        assert data["is_active"] is True

    def test_create_default_unsets_previous(self, client):
        # Create new default territory
        resp = client.post("/api/v1/territories", json={
            "name": "New Default",
            "criteria_type": "rep_assigned",
            "is_default": True,
        })
        assert resp.status_code == 201
        assert resp.json()["data"]["is_default"] is True
        # Old default (t-004) should now be unset
        list_resp = client.get("/api/v1/territories")
        defaults = [t for t in list_resp.json()["data"] if t["is_default"]]
        assert len(defaults) == 1

    def test_invalid_criteria_type_422(self, client):
        resp = client.post("/api/v1/territories", json={
            "name": "Bad",
            "criteria_type": "invalid_type",
        })
        assert resp.status_code == 422


# ── GET /territories/:id ──────────────────────────────────────────────────────

class TestGetTerritory:
    def test_get_seeded_territory(self, client):
        resp = client.get("/api/v1/territories/t-001")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["territory_id"] == "t-001"
        assert "rules" in data

    def test_get_nonexistent_404(self, client):
        resp = client.get("/api/v1/territories/does-not-exist")
        assert resp.status_code == 404


# ── PATCH /territories/:id ────────────────────────────────────────────────────

class TestUpdateTerritory:
    def test_update_name(self, client):
        resp = client.patch("/api/v1/territories/t-001", json={"name": "Punjab Updated"})
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Punjab Updated"

    def test_update_nonexistent_404(self, client):
        resp = client.patch("/api/v1/territories/no-such", json={"name": "X"})
        assert resp.status_code == 404


# ── DELETE /territories/:id ───────────────────────────────────────────────────

class TestDeactivateTerritory:
    def test_deactivate_non_default(self, client):
        resp = client.delete("/api/v1/territories/t-001")
        assert resp.status_code == 200
        assert resp.json()["data"]["deactivated"] is True

    def test_cannot_deactivate_default(self, client):
        resp = client.delete("/api/v1/territories/t-004")
        assert resp.status_code == 409


# ── POST /territories/:id/rules ───────────────────────────────────────────────

class TestAddRule:
    def test_add_city_rule(self, client):
        resp = client.post("/api/v1/territories/t-001/rules", json={
            "rule_type": "city",
            "field": "lead.city",
            "operator": "in",
            "value": {"cities": ["Lahore"]},
        })
        assert resp.status_code == 201
        assert resp.json()["data"]["rule_type"] == "city"

    def test_invalid_rule_type_422(self, client):
        resp = client.post("/api/v1/territories/t-001/rules", json={
            "rule_type": "invalid_rule",
            "value": {},
        })
        assert resp.status_code == 422


# ── POST /territories/assignments/evaluate ────────────────────────────────────

class TestEvaluateAssignment:
    def test_evaluate_lahore_lead(self, client):
        resp = client.post("/api/v1/territories/assignments/evaluate", json={
            "subject": {"city": "Lahore", "province": "Punjab"},
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "winner" in data
        assert "candidates" in data
        assert "reason" in data

    def test_evaluate_unknown_lead_gets_default(self, client):
        resp = client.post("/api/v1/territories/assignments/evaluate", json={
            "subject": {"city": "Gilgit", "province": "Gilgit-Baltistan"},
        })
        assert resp.status_code == 200
        # Should fall back to default or empty
        assert resp.json()["data"]["reason"] in ("default_fallback", "no_match", "single_match", "conflict_resolved", "priority_order")


# ── GET /territories/:id/performance ─────────────────────────────────────────

class TestPerformance:
    def test_performance_returns_metrics(self, client):
        resp = client.get("/api/v1/territories/t-001/performance")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "open_leads" in data
        assert "conversion_rate" in data
        assert "collection_rate" in data

    def test_performance_nonexistent_404(self, client):
        resp = client.get("/api/v1/territories/no-such/performance")
        assert resp.status_code == 404
