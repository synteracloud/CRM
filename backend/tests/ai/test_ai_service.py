"""Unit tests for AI service: scoring formulas, churn prediction, CLV, suggestions, intent.

Spec: backend/docs/domain/ai-predictive-models.md
"""
from __future__ import annotations

import pytest

from services.ai.entities import (
    AIDomainError,
    SCORING_MODELS,
    classify_churn_risk,
    classify_query_intent,
    classify_score_band,
    compute_churn_probability,
    compute_clv,
    compute_lead_score,
    compute_trend,
    is_stale,
    validate_suggestion_body,
)
from services.ai.service import AIService

from datetime import datetime, timedelta, timezone


# ── classify_score_band ────────────────────────────────────────────────────────

class TestScoreBand:
    def test_hot_at_75(self):
        assert classify_score_band(75) == "hot"

    def test_hot_at_100(self):
        assert classify_score_band(100) == "hot"

    def test_warm_at_74(self):
        assert classify_score_band(74) == "warm"

    def test_warm_at_50(self):
        assert classify_score_band(50) == "warm"

    def test_cold_at_49(self):
        assert classify_score_band(49) == "cold"

    def test_cold_at_25(self):
        assert classify_score_band(25) == "cold"

    def test_disqualified_at_24(self):
        assert classify_score_band(24) == "disqualified"

    def test_disqualified_at_0(self):
        assert classify_score_band(0) == "disqualified"


# ── compute_lead_score ────────────────────────────────────────────────────────

class TestLeadScore:
    def test_max_score_capped_at_100(self):
        features = {
            "deal_stage":             "negotiation",
            "follow_up_count":        10,
            "estimated_value":        1_000_000,
            "days_since_last_contact": 1,
            "email_open_rate":        1.0,
            "source_quality":         "referral",
            "account_tier":           "Enterprise",
            "call_attempts":          10,
            "whatsapp_replies":       10,
        }
        assert compute_lead_score(features) == 100

    def test_empty_features_returns_low_score(self):
        assert compute_lead_score({}) <= 10

    def test_negotiation_stage_adds_28(self):
        score_with = compute_lead_score({"deal_stage": "negotiation"})
        score_without = compute_lead_score({"deal_stage": "OPEN"})
        assert score_with - score_without == 28

    def test_follow_up_count_capped_at_18(self):
        score_6 = compute_lead_score({"follow_up_count": 6})
        score_100 = compute_lead_score({"follow_up_count": 100})
        assert score_6 == score_100

    def test_fresh_contact_adds_12(self):
        score = compute_lead_score({"days_since_last_contact": 2})
        score_stale = compute_lead_score({"days_since_last_contact": 60})
        assert score - score_stale == 12

    def test_stale_contact_adds_0(self):
        score = compute_lead_score({"days_since_last_contact": 40})
        # 30+ days → 0 points
        assert score == compute_lead_score({"days_since_last_contact": 999})

    def test_enterprise_tier_adds_6(self):
        score_ent = compute_lead_score({"account_tier": "Enterprise"})
        score_ind = compute_lead_score({"account_tier": "Individual"})
        assert score_ent - score_ind == 5

    def test_score_always_non_negative(self):
        assert compute_lead_score({"days_since_last_contact": 9999}) >= 0


# ── compute_trend ─────────────────────────────────────────────────────────────

class TestScoreTrend:
    def test_rising_when_delta_gt_3(self):
        trend, delta = compute_trend(80, 70)
        assert trend == "rising"
        assert delta == 10

    def test_falling_when_delta_lt_neg3(self):
        trend, delta = compute_trend(60, 70)
        assert trend == "falling"
        assert delta == -10

    def test_stable_when_no_previous(self):
        trend, delta = compute_trend(50, None)
        assert trend == "stable"
        assert delta is None

    def test_stable_when_small_change(self):
        trend, delta = compute_trend(50, 48)
        assert trend == "stable"


# ── compute_churn_probability ──────────────────────────────────────────────────

class TestChurnProbability:
    def test_no_risk_factors_is_zero(self):
        assert compute_churn_probability({}) == 0.0

    def test_past_due_invoice_high_risk(self):
        prob = compute_churn_probability({
            "days_since_last_invoice_paid": 70,
            "subscription_status": "past_due",
        })
        assert prob >= 0.65

    def test_healthy_account_low_risk(self):
        prob = compute_churn_probability({
            "days_since_last_invoice_paid": 5,
            "subscription_status": "active",
            "open_support_cases": 0,
        })
        assert prob < 0.35

    def test_probability_capped_at_1(self):
        prob = compute_churn_probability({
            "days_since_last_invoice_paid": 90,
            "subscription_status": "past_due",
            "open_support_cases": 10,
            "days_since_last_activity": 60,
            "follow_up_breach_count": 5,
            "nps_score_low": True,
        })
        assert prob <= 1.0

    def test_classify_high_band(self):
        assert classify_churn_risk(0.70) == "high"

    def test_classify_medium_band(self):
        assert classify_churn_risk(0.50) == "medium"

    def test_classify_low_band(self):
        assert classify_churn_risk(0.20) == "low"

    def test_boundary_high_at_0_65(self):
        assert classify_churn_risk(0.65) == "high"

    def test_boundary_medium_at_0_35(self):
        assert classify_churn_risk(0.35) == "medium"


# ── compute_clv ───────────────────────────────────────────────────────────────

class TestCLV:
    def test_basic_clv(self):
        clv, conf, anchor = compute_clv(100_000, 24, 0.20)
        assert clv == pytest.approx(100_000 * 24 * 0.80, abs=1)

    def test_zero_revenue_low_confidence(self):
        clv, conf, _ = compute_clv(0, 24, 0.50)
        assert clv == 0
        assert conf == 0.30

    def test_high_churn_reduces_clv(self):
        clv_low_churn, _, _ = compute_clv(100_000, 24, 0.10)
        clv_high_churn, _, _ = compute_clv(100_000, 24, 0.80)
        assert clv_low_churn > clv_high_churn

    def test_evidence_anchor_contains_values(self):
        _, _, anchor = compute_clv(50_000, 12, 0.30)
        assert "50,000" in anchor
        assert "12 months" in anchor
        assert "0.70" in anchor


# ── validate_suggestion_body ──────────────────────────────────────────────────

class TestValidateSuggestion:
    def _valid(self) -> dict:
        return {
            "suggestion_type": "follow_up_overdue",
            "priority":        "urgent",
            "title":           "Test Suggestion",
            "body":            "This is a test.",
            "evidence_anchor": "follow_up task #ft-001 overdue by 2 days",
        }

    def test_valid_body_no_errors(self):
        assert validate_suggestion_body(self._valid()) == []

    def test_missing_evidence_anchor_error(self):
        body = {**self._valid(), "evidence_anchor": ""}
        errors = validate_suggestion_body(body)
        assert any("evidence_anchor" in e for e in errors)

    def test_invalid_suggestion_type_error(self):
        body = {**self._valid(), "suggestion_type": "bad_type"}
        errors = validate_suggestion_body(body)
        assert any("suggestion_type" in e for e in errors)

    def test_invalid_priority_error(self):
        body = {**self._valid(), "priority": "critical"}
        errors = validate_suggestion_body(body)
        assert any("priority" in e for e in errors)

    def test_missing_title_error(self):
        body = {**self._valid(), "title": ""}
        errors = validate_suggestion_body(body)
        assert any("title" in e for e in errors)


# ── is_stale ──────────────────────────────────────────────────────────────────

class TestIsStale:
    def test_fresh_score_not_stale(self):
        now = datetime.now(timezone.utc)
        assert is_stale(now, 6) is False

    def test_old_score_is_stale(self):
        old = datetime.now(timezone.utc) - timedelta(hours=10)
        assert is_stale(old, 6) is True

    def test_naive_datetime_handled(self):
        old = datetime.now() - timedelta(hours=10)
        assert is_stale(old, 6) is True


# ── classify_query_intent ──────────────────────────────────────────────────────

class TestQueryIntent:
    def test_lead_intent(self):
        assert classify_query_intent("show me all leads") == "lead"

    def test_payment_intent(self):
        assert classify_query_intent("check invoice status") == "payment"

    def test_followup_intent(self):
        assert classify_query_intent("overdue follow-ups") == "followup"

    def test_case_intent(self):
        assert classify_query_intent("open support tickets") == "case"

    def test_oob_intent(self):
        assert classify_query_intent("what is the weather today") == "oob"

    def test_urdu_like_mixed_query(self):
        assert classify_query_intent("invoice paid nahi hua") == "payment"


# ── SCORING_MODELS catalog ────────────────────────────────────────────────────

class TestScoringModelsCatalog:
    def test_has_three_models(self):
        assert len(SCORING_MODELS) == 3

    def test_all_models_have_required_keys(self):
        for m in SCORING_MODELS:
            assert m.get("model_key")
            assert m.get("model_type")
            assert m.get("algorithm") == "rule_based"

    def test_lead_score_v1_has_9_features(self):
        model = next(m for m in SCORING_MODELS if m["model_key"] == "lead_score_v1")
        assert len(model["feature_weights"]) == 9

    def test_feature_weights_sum_to_100(self):
        model = next(m for m in SCORING_MODELS if m["model_key"] == "lead_score_v1")
        total = sum(f["weight"] for f in model["feature_weights"])
        assert total == 100


# ── AIService ─────────────────────────────────────────────────────────────────

class TestAIService:
    svc = AIService()

    def test_score_lead_returns_all_fields(self):
        result = self.svc.score_lead({"deal_stage": "negotiation", "follow_up_count": 5}, tenant_id="t-001")
        assert "score_id" in result
        assert result["model_id"] == "lead_score_v1"
        assert 0 <= result["score"] <= 100
        assert result["is_stale"] is False

    def test_predict_churn_returns_all_fields(self):
        result = self.svc.predict_churn({"account_id": "acc-001", "days_since_last_invoice_paid": 70, "subscription_status": "past_due"}, tenant_id="t-001")
        assert result["risk_band"] == "high"
        assert result["evidence_anchor"]
        assert result["recommended_action"]

    def test_estimate_clv_returns_all_fields(self):
        result = self.svc.estimate_clv("acc-001", 120_000, 0.20, 24, "t-001")
        assert result["estimated_clv"] > 0
        assert result["clv_horizon_months"] == 24
        assert result["evidence_anchor"]

    def test_build_suggestion_raises_on_missing_evidence(self):
        with pytest.raises(AIDomainError):
            self.svc.build_suggestion({
                "suggestion_type": "follow_up_overdue",
                "priority": "urgent",
                "title": "Test",
                "body": "Test body",
                "evidence_anchor": "",
            }, "t-001", "u-001")

    def test_apply_dismiss_sets_dismissed(self):
        sug = {"suggestion_id": "s-1", "is_dismissed": False, "dismissed_at": None, "updated_at": "x"}
        result = self.svc.apply_dismiss(sug)
        assert result["is_dismissed"] is True
        assert result["dismissed_at"] is not None

    def test_apply_action_sets_actioned(self):
        sug = {"suggestion_id": "s-1", "is_actioned": False, "actioned_at": None, "updated_at": "x"}
        result = self.svc.apply_action(sug)
        assert result["is_actioned"] is True
        assert result["actioned_at"] is not None

    def test_handle_query_classifies_intent(self):
        result = self.svc.handle_query("show overdue invoices", "t-001")
        assert result["intent"] == "payment"
        assert result["query"] == "show overdue invoices"

    def test_handle_query_oob(self):
        result = self.svc.handle_query("what is the weather", "t-001")
        assert result["intent"] == "oob"

    def test_flag_stale_uses_model_interval(self):
        old_record = {"computed_at": "2020-01-01T00:00:00+00:00", "is_stale": False}
        result = self.svc.flag_stale(old_record, "lead_score_v1")
        assert result["is_stale"] is True

    def test_compute_score_stats_empty(self):
        stats = self.svc.compute_score_stats([])
        assert stats["total"] == 0

    def test_compute_score_stats_counts_bands(self):
        scores = [
            {"score": 80, "score_band": "hot"},
            {"score": 60, "score_band": "warm"},
            {"score": 30, "score_band": "cold"},
        ]
        stats = self.svc.compute_score_stats(scores)
        assert stats["hot"] == 1
        assert stats["warm"] == 1
        assert stats["cold"] == 1
        assert stats["avg_score"] == pytest.approx(56.7, abs=0.2)

    def test_list_models_returns_all(self):
        assert len(self.svc.list_models()) == 3

    def test_get_model_by_key(self):
        model = self.svc.get_model("churn_predict_v1")
        assert model is not None
        assert model["model_type"] == "churn_predict"

    def test_get_model_unknown_key_returns_none(self):
        assert self.svc.get_model("does_not_exist") is None
