"""Seed fixtures for AI API and service tests."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from tests.ai._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal

TEST_TENANT = "tenant-test-001"


@pytest.fixture(autouse=True)
def seed_ai_data():
    """Create schema and seed AI test data for every test in this directory."""
    from services.db.base import Base
    import services.db.models  # noqa: F401
    from services.db.models.ai_scores import (
        LeadScore,
        ChurnPrediction,
        CLVEstimate,
        CopilotSuggestion,
    )

    Base.metadata.create_all(bind=_test_engine)
    now = datetime.now(timezone.utc)
    db = TestSessionLocal()
    try:
        # ── Lead Scores ───────────────────────────────────────────────────────
        lead_scores = [
            LeadScore(
                score_id="ls-001", tenant_id=TEST_TENANT, lead_id="l-001",
                model_id="lead_score_v1", score=90, score_band="hot",
                trend="rising", trend_delta=5, top_drivers=[],
                confidence_score=Decimal("0.85"), is_stale=False,
                computed_at=now, created_at=now,
            ),
            LeadScore(
                score_id="ls-002", tenant_id=TEST_TENANT, lead_id="l-002",
                model_id="lead_score_v1", score=70, score_band="warm",
                trend="stable", trend_delta=0, top_drivers=[],
                confidence_score=Decimal("0.85"), is_stale=False,
                computed_at=now, created_at=now,
            ),
            LeadScore(
                score_id="ls-003", tenant_id=TEST_TENANT, lead_id="l-003",
                model_id="lead_score_v1", score=40, score_band="cold",
                trend="falling", trend_delta=-5, top_drivers=[],
                confidence_score=Decimal("0.85"), is_stale=False,
                computed_at=now, created_at=now,
            ),
            LeadScore(
                score_id="ls-004", tenant_id=TEST_TENANT, lead_id="l-004",
                model_id="lead_score_v1", score=80, score_band="hot",
                trend="stable", trend_delta=1, top_drivers=[],
                confidence_score=Decimal("0.85"), is_stale=True,
                computed_at=now, created_at=now,
            ),
            LeadScore(
                score_id="ls-005", tenant_id=TEST_TENANT, lead_id="l-005",
                model_id="lead_score_v1", score=85, score_band="hot",
                trend="rising", trend_delta=8, top_drivers=[],
                confidence_score=Decimal("0.85"), is_stale=False,
                computed_at=now, created_at=now,
            ),
        ]
        for s in lead_scores:
            db.merge(s)

        # ── Churn Predictions ─────────────────────────────────────────────────
        churn_predictions = [
            ChurnPrediction(
                prediction_id="cp-001", tenant_id=TEST_TENANT, account_id="acc-001",
                model_id="churn_predict_v1", churn_probability=Decimal("0.750"),
                risk_band="high", top_drivers=[], recommended_action="Schedule renewal call.",
                confidence_score=Decimal("0.80"), evidence_anchor="last invoice 70 days ago",
                is_stale=False, computed_at=now, created_at=now,
            ),
            ChurnPrediction(
                prediction_id="cp-002", tenant_id=TEST_TENANT, account_id="acc-002",
                model_id="churn_predict_v1", churn_probability=Decimal("0.500"),
                risk_band="medium", top_drivers=[], recommended_action="Send check-in message.",
                confidence_score=Decimal("0.80"), evidence_anchor="last invoice 40 days ago",
                is_stale=False, computed_at=now, created_at=now,
            ),
            ChurnPrediction(
                prediction_id="cp-003", tenant_id=TEST_TENANT, account_id="acc-003",
                model_id="churn_predict_v1", churn_probability=Decimal("0.200"),
                risk_band="low", top_drivers=[], recommended_action="Maintain standard cadence.",
                confidence_score=Decimal("0.80"), evidence_anchor="account healthy",
                is_stale=False, computed_at=now, created_at=now,
            ),
        ]
        for p in churn_predictions:
            db.merge(p)

        # ── CLV Estimates ─────────────────────────────────────────────────────
        clv_estimates = [
            CLVEstimate(
                estimate_id="ce-001", tenant_id=TEST_TENANT, account_id="acc-001",
                model_id="clv_estimate_v1", estimated_clv=Decimal("2400000.00"),
                clv_horizon_months=24, confidence_score=Decimal("0.75"),
                evidence_anchor="avg monthly: PKR 100,000 × 24 months × 1.00",
                is_stale=False, computed_at=now, created_at=now,
            ),
            CLVEstimate(
                estimate_id="ce-005", tenant_id=TEST_TENANT, account_id="acc-005",
                model_id="clv_estimate_v1", estimated_clv=Decimal("1200000.00"),
                clv_horizon_months=24, confidence_score=Decimal("0.75"),
                evidence_anchor="avg monthly: PKR 50,000 × 24 months × 1.00",
                is_stale=False, computed_at=now, created_at=now,
            ),
        ]
        for e in clv_estimates:
            db.merge(e)

        # ── Copilot Suggestions ───────────────────────────────────────────────
        suggestions = [
            CopilotSuggestion(
                suggestion_id="sug-001", tenant_id=TEST_TENANT, target_user_id="user-test-001",
                suggestion_type="follow_up_overdue", priority="urgent",
                title="Overdue Follow-up: Lead l-001",
                body="Lead l-001 has an overdue follow-up task.",
                action_label="Open Lead", action_href="app/leads.html",
                evidence_anchor="follow_up task #ft-001 overdue by 2 days",
                confidence_score=Decimal("0.80"),
                is_dismissed=False, dismissed_at=None,
                is_actioned=False, actioned_at=None,
                expires_at=None, created_at=now, updated_at=now,
            ),
            CopilotSuggestion(
                suggestion_id="sug-002", tenant_id=TEST_TENANT, target_user_id="user-test-001",
                suggestion_type="risk_flag", priority="high",
                title="High Churn Risk: Account acc-001",
                body="Account acc-001 has high churn risk.",
                action_label="Review Account", action_href="app/accounts.html",
                evidence_anchor="churn probability 0.75",
                confidence_score=Decimal("0.80"),
                is_dismissed=False, dismissed_at=None,
                is_actioned=False, actioned_at=None,
                expires_at=None, created_at=now, updated_at=now,
            ),
            CopilotSuggestion(
                suggestion_id="sug-003", tenant_id=TEST_TENANT, target_user_id="user-test-001",
                suggestion_type="deal_nudge", priority="medium",
                title="Stale Deal: Lead l-003",
                body="Lead l-003 has not been contacted in 30 days.",
                action_label="Open Lead", action_href="app/leads.html",
                evidence_anchor="days_since_last_contact: 30",
                confidence_score=Decimal("0.80"),
                is_dismissed=False, dismissed_at=None,
                is_actioned=False, actioned_at=None,
                expires_at=None, created_at=now, updated_at=now,
            ),
            CopilotSuggestion(
                suggestion_id="sug-004", tenant_id=TEST_TENANT, target_user_id="user-test-001",
                suggestion_type="next_action", priority="low",
                title="Low Priority Action",
                body="Consider sending a welcome message.",
                action_label="View", action_href="app/dashboard.html",
                evidence_anchor="no recent activity for 10 days",
                confidence_score=Decimal("0.80"),
                is_dismissed=False, dismissed_at=None,
                is_actioned=False, actioned_at=None,
                expires_at=None, created_at=now, updated_at=now,
            ),
        ]
        for s in suggestions:
            db.merge(s)

        db.commit()
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def db_session():
    """Yield a DB session pointing to the test engine."""
    sess = TestSessionLocal()
    try:
        yield sess
    finally:
        sess.close()
