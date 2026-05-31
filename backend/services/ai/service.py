"""AI service: scoring, prediction, CLV estimation, suggestions, query handling.

Spec: backend/docs/domain/ai-predictive-models.md
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from services.ai.entities import (
    AIDomainError,
    SCORING_MODELS,
    build_lead_score_drivers,
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


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class AIService:
    """Stateless AI domain service — all methods are pure functions over dicts."""

    # ── Lead scoring ──────────────────────────────────────────────────────────

    def score_lead(
        self,
        lead_data: dict[str, Any],
        previous_score: int | None = None,
        tenant_id: str = "",
    ) -> dict:
        """Compute a new LeadScore record dict from lead feature data."""
        score = compute_lead_score(lead_data)
        trend, delta = compute_trend(score, previous_score)
        drivers = build_lead_score_drivers(lead_data)
        now = _utcnow()
        return {
            "score_id":         _uuid(),
            "tenant_id":        tenant_id,
            "lead_id":          lead_data.get("lead_id", ""),
            "model_id":         "lead_score_v1",
            "score":            score,
            "score_band":       classify_score_band(score),
            "trend":            trend,
            "trend_delta":      delta,
            "top_drivers":      drivers,
            "confidence_score": 0.85,
            "is_stale":         False,
            "computed_at":      now.isoformat(),
            "created_at":       now.isoformat(),
        }

    # ── Churn prediction ──────────────────────────────────────────────────────

    def predict_churn(
        self,
        account_data: dict[str, Any],
        tenant_id: str = "",
    ) -> dict:
        """Compute a new ChurnPrediction record dict."""
        prob = compute_churn_probability(account_data)
        risk = classify_churn_risk(prob)
        now  = _utcnow()

        recommended = {
            "high":   "Schedule renewal call within 14 days and review open invoices.",
            "medium": "Send relationship check-in WhatsApp within 7 days.",
            "low":    "Account is healthy — maintain standard follow-up cadence.",
        }[risk]

        days_paid = account_data.get("days_since_last_invoice_paid", 0)
        sub_status = account_data.get("subscription_status", "active")
        anchor = (
            f"last invoice paid {days_paid} days ago; "
            f"subscription status: {sub_status}; "
            f"open support cases: {account_data.get('open_support_cases', 0)}"
        )

        return {
            "prediction_id":     _uuid(),
            "tenant_id":         tenant_id,
            "account_id":        account_data.get("account_id", ""),
            "model_id":          "churn_predict_v1",
            "churn_probability": prob,
            "risk_band":         risk,
            "top_drivers":       [],
            "recommended_action": recommended,
            "confidence_score":  0.80,
            "evidence_anchor":   anchor,
            "is_stale":          False,
            "computed_at":       now.isoformat(),
            "created_at":        now.isoformat(),
        }

    # ── CLV estimation ────────────────────────────────────────────────────────

    def estimate_clv(
        self,
        account_id: str,
        avg_monthly_revenue: float,
        churn_probability: float,
        clv_horizon_months: int = 24,
        tenant_id: str = "",
    ) -> dict:
        """Compute a new CLVEstimate record dict."""
        clv, confidence, anchor = compute_clv(avg_monthly_revenue, clv_horizon_months, churn_probability)
        now = _utcnow()
        return {
            "estimate_id":        _uuid(),
            "tenant_id":          tenant_id,
            "account_id":         account_id,
            "model_id":           "clv_estimate_v1",
            "estimated_clv":      clv,
            "clv_horizon_months": clv_horizon_months,
            "confidence_score":   confidence,
            "evidence_anchor":    anchor,
            "is_stale":           False,
            "computed_at":        now.isoformat(),
            "created_at":         now.isoformat(),
        }

    # ── Staleness flagging ────────────────────────────────────────────────────

    def flag_stale(
        self,
        record: dict,
        model_key: str = "lead_score_v1",
    ) -> dict:
        """Return record with is_stale updated based on model recompute_interval."""
        model = next((m for m in SCORING_MODELS if m["model_key"] == model_key), None)
        interval = model["recompute_interval_hours"] if model else 24
        try:
            computed_at = datetime.fromisoformat(record["computed_at"])
        except (KeyError, ValueError):
            return {**record, "is_stale": True}
        return {**record, "is_stale": is_stale(computed_at, interval)}

    # ── Suggestion management ─────────────────────────────────────────────────

    def build_suggestion(self, body: dict, tenant_id: str, user_id: str) -> dict:
        """Validate and build a CopilotSuggestion dict. Raises AIDomainError on invalid input."""
        errors = validate_suggestion_body(body)
        if errors:
            raise AIDomainError("; ".join(errors))
        now = _utcnow()
        return {
            "suggestion_id":    _uuid(),
            "tenant_id":        tenant_id,
            "target_user_id":   user_id,
            "suggestion_type":  body["suggestion_type"],
            "priority":         body["priority"],
            "title":            body["title"],
            "body":             body["body"],
            "action_label":     body.get("action_label", "Open Record"),
            "action_href":      body.get("action_href", "app/dashboard.html"),
            "evidence_anchor":  body["evidence_anchor"],
            "entity_type":      body.get("entity_type"),
            "entity_id":        body.get("entity_id"),
            "confidence_score": body.get("confidence_score", 0.80),
            "is_dismissed":     False,
            "dismissed_at":     None,
            "is_actioned":      False,
            "actioned_at":      None,
            "expires_at":       body.get("expires_at"),
            "created_at":       now.isoformat(),
            "updated_at":       now.isoformat(),
        }

    def apply_dismiss(self, suggestion: dict) -> dict:
        now = _utcnow()
        return {**suggestion, "is_dismissed": True, "dismissed_at": now.isoformat(), "updated_at": now.isoformat()}

    def apply_action(self, suggestion: dict) -> dict:
        now = _utcnow()
        return {**suggestion, "is_actioned": True, "actioned_at": now.isoformat(), "updated_at": now.isoformat()}

    # ── Conversational query ──────────────────────────────────────────────────

    def handle_query(
        self,
        text: str,
        tenant_id: str,
        context: dict | None = None,
    ) -> dict:
        """Classify intent and return a structured response. No LLM — rule-based v1."""
        intent = classify_query_intent(text)
        ctx = context or {}
        now = _utcnow()

        response_map = {
            "lead": {
                "intent":  "lead",
                "summary": "Showing matching lead records and scores.",
                "records": ctx.get("leads", [])[:5],
                "actions": [{"label": "Open Lead", "href": "app/leads.html"}],
            },
            "payment": {
                "intent":  "payment",
                "summary": "Showing overdue invoices requiring attention.",
                "records": [i for i in ctx.get("invoices", []) if i.get("status") in ("overdue", "partial")][:5],
                "actions": [{"label": "Record Payment", "href": "app/collections.html"}],
            },
            "followup": {
                "intent":  "followup",
                "summary": "Showing overdue follow-up tasks.",
                "records": [f for f in ctx.get("followups", []) if f.get("status") == "overdue"][:5],
                "actions": [{"label": "View Follow-ups", "href": "app/followups.html"}],
            },
            "case": {
                "intent":  "case",
                "summary": "Showing open support cases.",
                "records": [c for c in ctx.get("cases", []) if c.get("status") == "OPEN"][:5],
                "actions": [{"label": "Open New Case", "href": "app/case-new.html"}],
            },
            "oob": {
                "intent":  "oob",
                "summary": "I can help with leads, payments, follow-ups, and support cases.",
                "records": [],
                "actions": [],
            },
        }

        return {
            "query":       text,
            "intent":      intent,
            "response":    response_map.get(intent, response_map["oob"]),
            "model_id":    "copilot_query_v1",
            "answered_at": now.isoformat(),
            "tenant_id":   tenant_id,
        }

    # ── Model registry ────────────────────────────────────────────────────────

    def get_model(self, model_key: str) -> dict | None:
        return next((m for m in SCORING_MODELS if m["model_key"] == model_key), None)

    def list_models(self) -> list[dict]:
        return SCORING_MODELS

    # ── Stats helper ──────────────────────────────────────────────────────────

    def compute_score_stats(self, scores: list[dict]) -> dict:
        if not scores:
            return {"total": 0, "hot": 0, "warm": 0, "cold": 0, "disqualified": 0, "avg_score": 0}
        bands = {"hot": 0, "warm": 0, "cold": 0, "disqualified": 0}
        total_score = 0
        for s in scores:
            band = s.get("score_band", "cold")
            if band in bands:
                bands[band] += 1
            total_score += s.get("score", 0)
        return {
            "total":        len(scores),
            **bands,
            "avg_score":    round(total_score / len(scores), 1),
        }
