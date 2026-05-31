"""Integration tests for /api/v1/ai endpoints.

Uses FastAPI TestClient + in-memory SQLite.

Spec: backend/docs/domain/ai-predictive-models.md
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
        scopes=[
            "ai.scores.read", "ai.scores.recompute",
            "ai.predictions.read", "ai.clv.read",
            "ai.copilot", "ai.models.read",
        ],
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


# ── GET /ai/scores/leads ──────────────────────────────────────────────────────

class TestListLeadScores:
    def test_returns_seeded_scores(self, client):
        resp = client.get("/api/v1/ai/scores/leads")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_scores_sorted_desc(self, client):
        resp = client.get("/api/v1/ai/scores/leads")
        scores = [s["score"] for s in resp.json()["data"]]
        assert scores == sorted(scores, reverse=True)

    def test_filter_by_score_band(self, client):
        resp = client.get("/api/v1/ai/scores/leads?score_band=hot")
        assert resp.status_code == 200
        for s in resp.json()["data"]:
            assert s["score_band"] == "hot"

    def test_filter_by_lead_id(self, client):
        resp = client.get("/api/v1/ai/scores/leads?lead_id=l-005")
        assert resp.status_code == 200
        for s in resp.json()["data"]:
            assert s["lead_id"] == "l-005"


# ── GET /ai/scores/leads/:lead_id ─────────────────────────────────────────────

class TestGetLeadScore:
    def test_get_seeded_lead_score(self, client):
        resp = client.get("/api/v1/ai/scores/leads/l-005")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["lead_id"] == "l-005"
        assert data["score_band"] == "hot"

    def test_get_nonexistent_404(self, client):
        resp = client.get("/api/v1/ai/scores/leads/no-such-lead")
        assert resp.status_code == 404


# ── POST /ai/scores/leads/:lead_id/recompute ──────────────────────────────────

class TestRecomputeLeadScore:
    def test_recompute_clears_stale(self, client):
        resp = client.post("/api/v1/ai/scores/leads/l-005/recompute")
        assert resp.status_code == 200
        assert resp.json()["data"]["is_stale"] is False

    def test_recompute_nonexistent_404(self, client):
        resp = client.post("/api/v1/ai/scores/leads/no-such/recompute")
        assert resp.status_code == 404


# ── GET /ai/predictions/churn ─────────────────────────────────────────────────

class TestListChurnPredictions:
    def test_returns_seeded_predictions(self, client):
        resp = client.get("/api/v1/ai/predictions/churn")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_sorted_by_probability_desc(self, client):
        resp = client.get("/api/v1/ai/predictions/churn")
        probs = [p["churn_probability"] for p in resp.json()["data"]]
        assert probs == sorted(probs, reverse=True)

    def test_filter_by_risk_band(self, client):
        resp = client.get("/api/v1/ai/predictions/churn?risk_band=high")
        assert resp.status_code == 200
        for p in resp.json()["data"]:
            assert p["risk_band"] == "high"


# ── GET /ai/predictions/churn/:account_id ────────────────────────────────────

class TestGetChurnPrediction:
    def test_get_seeded_prediction(self, client):
        resp = client.get("/api/v1/ai/predictions/churn/acc-001")
        assert resp.status_code == 200
        assert resp.json()["data"]["risk_band"] == "high"

    def test_get_nonexistent_404(self, client):
        resp = client.get("/api/v1/ai/predictions/churn/no-such")
        assert resp.status_code == 404


# ── GET /ai/estimates/clv ─────────────────────────────────────────────────────

class TestListCLVEstimates:
    def test_returns_seeded_estimates(self, client):
        resp = client.get("/api/v1/ai/estimates/clv")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_sorted_by_clv_desc(self, client):
        resp = client.get("/api/v1/ai/estimates/clv")
        clvs = [float(e["estimated_clv"]) for e in resp.json()["data"]]
        assert clvs == sorted(clvs, reverse=True)

    def test_get_clv_by_account(self, client):
        resp = client.get("/api/v1/ai/estimates/clv/acc-005")
        assert resp.status_code == 200
        assert resp.json()["data"]["account_id"] == "acc-005"

    def test_clv_nonexistent_404(self, client):
        resp = client.get("/api/v1/ai/estimates/clv/no-such")
        assert resp.status_code == 404


# ── GET /ai/copilot/suggestions ───────────────────────────────────────────────

class TestListSuggestions:
    def test_returns_active_suggestions(self, client):
        resp = client.get("/api/v1/ai/copilot/suggestions")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 1

    def test_dismissed_excluded_by_default(self, client):
        # Dismiss one
        client.post("/api/v1/ai/copilot/suggestions/sug-001/dismiss")
        resp = client.get("/api/v1/ai/copilot/suggestions")
        ids = [s["suggestion_id"] for s in resp.json()["data"]]
        assert "sug-001" not in ids

    def test_filter_by_priority(self, client):
        resp = client.get("/api/v1/ai/copilot/suggestions?priority=urgent")
        assert resp.status_code == 200
        for s in resp.json()["data"]:
            assert s["priority"] == "urgent"

    def test_sorted_by_priority_weight(self, client):
        resp = client.get("/api/v1/ai/copilot/suggestions")
        priorities = [s["priority"] for s in resp.json()["data"]]
        weight = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
        weights = [weight.get(p, 0) for p in priorities]
        assert weights == sorted(weights, reverse=True)


# ── POST /ai/copilot/suggestions/:id/dismiss ─────────────────────────────────

class TestDismissSuggestion:
    def test_dismiss_sets_flag(self, client):
        resp = client.post("/api/v1/ai/copilot/suggestions/sug-002/dismiss")
        assert resp.status_code == 200
        assert resp.json()["data"]["is_dismissed"] is True
        assert resp.json()["data"]["dismissed_at"] is not None

    def test_dismiss_nonexistent_404(self, client):
        resp = client.post("/api/v1/ai/copilot/suggestions/no-such/dismiss")
        assert resp.status_code == 404


# ── POST /ai/copilot/suggestions/:id/action ──────────────────────────────────

class TestActionSuggestion:
    def test_action_sets_flag(self, client):
        resp = client.post("/api/v1/ai/copilot/suggestions/sug-003/action")
        assert resp.status_code == 200
        assert resp.json()["data"]["is_actioned"] is True
        assert resp.json()["data"]["actioned_at"] is not None

    def test_action_nonexistent_404(self, client):
        resp = client.post("/api/v1/ai/copilot/suggestions/no-such/action")
        assert resp.status_code == 404


# ── POST /ai/copilot/query ────────────────────────────────────────────────────

class TestCopilotQuery:
    def test_lead_intent_classified(self, client):
        resp = client.post("/api/v1/ai/copilot/query", json={"query": "show me leads"})
        assert resp.status_code == 200
        assert resp.json()["data"]["intent"] == "lead"

    def test_payment_intent_classified(self, client):
        resp = client.post("/api/v1/ai/copilot/query", json={"query": "check overdue invoices"})
        assert resp.status_code == 200
        assert resp.json()["data"]["intent"] == "payment"

    def test_followup_intent_classified(self, client):
        resp = client.post("/api/v1/ai/copilot/query", json={"query": "pending follow-ups"})
        assert resp.status_code == 200
        assert resp.json()["data"]["intent"] == "followup"

    def test_oob_intent_returns_graceful(self, client):
        resp = client.post("/api/v1/ai/copilot/query", json={"query": "what is the weather"})
        assert resp.status_code == 200
        assert resp.json()["data"]["intent"] == "oob"

    def test_missing_query_422(self, client):
        resp = client.post("/api/v1/ai/copilot/query", json={})
        assert resp.status_code == 422

    def test_response_has_answered_at(self, client):
        resp = client.post("/api/v1/ai/copilot/query", json={"query": "show leads"})
        assert resp.status_code == 200
        assert resp.json()["data"]["answered_at"] is not None


# ── GET /ai/models ────────────────────────────────────────────────────────────

class TestModelRegistry:
    def test_list_models_returns_three(self, client):
        resp = client.get("/api/v1/ai/models")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 3

    def test_get_model_by_key(self, client):
        resp = client.get("/api/v1/ai/models/lead_score_v1")
        assert resp.status_code == 200
        assert resp.json()["data"]["model_key"] == "lead_score_v1"

    def test_get_unknown_model_404(self, client):
        resp = client.get("/api/v1/ai/models/does_not_exist")
        assert resp.status_code == 404

    def test_all_models_rule_based(self, client):
        resp = client.get("/api/v1/ai/models")
        for m in resp.json()["data"]:
            assert m["algorithm"] == "rule_based"
