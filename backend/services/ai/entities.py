"""AI domain entities: scoring formulas, enums, validators, intent classifier.

Spec: backend/docs/domain/ai-predictive-models.md
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ── Enums ─────────────────────────────────────────────────────────────────────

class ScoreBand(str, Enum):
    hot          = "hot"           # 75–100
    warm         = "warm"          # 50–74
    cold         = "cold"          # 25–49
    disqualified = "disqualified"  # 0–24


class ScoreTrend(str, Enum):
    rising  = "rising"
    stable  = "stable"
    falling = "falling"


class ChurnRiskBand(str, Enum):
    high   = "high"    # >= 0.65
    medium = "medium"  # 0.35–0.64
    low    = "low"     # < 0.35


class SuggestionType(str, Enum):
    next_action       = "next_action"
    risk_flag         = "risk_flag"
    deal_nudge        = "deal_nudge"
    follow_up_overdue = "follow_up_overdue"
    sla_breach_alert  = "sla_breach_alert"
    stale_deal        = "stale_deal"


class SuggestionPriority(str, Enum):
    urgent = "urgent"
    high   = "high"
    medium = "medium"
    low    = "low"


class QueryIntent(str, Enum):
    lead     = "lead"
    payment  = "payment"
    followup = "followup"
    case     = "case"
    oob      = "oob"


# ── Exceptions ────────────────────────────────────────────────────────────────

class AIDomainError(Exception):
    """Raised for domain-level AI validation failures."""


# ── Model catalog (read-only registry) ────────────────────────────────────────

SCORING_MODELS: list[dict] = [
    {
        "model_key":  "lead_score_v1",
        "model_type": "lead_score",
        "version":    "1.0.0",
        "description": "Rule-based weighted-sum lead scoring for Pakistani SMB deals.",
        "algorithm":  "rule_based",
        "recompute_interval_hours": 6,
        "is_active": True,
        "feature_weights": [
            {"feature_key": "deal_stage",             "weight": 28, "description": "Current pipeline stage"},
            {"feature_key": "follow_up_count",        "weight": 18, "description": "Number of logged follow-up contacts"},
            {"feature_key": "estimated_value",        "weight": 14, "description": "PKR opportunity value"},
            {"feature_key": "days_since_last_contact","weight": 12, "description": "Recency signal"},
            {"feature_key": "email_open_rate",        "weight": 8,  "description": "Email engagement signal"},
            {"feature_key": "source_quality",         "weight": 7,  "description": "Inbound vs cold-outreach weighting"},
            {"feature_key": "account_tier",           "weight": 6,  "description": "Enterprise/SMB/Individual coefficient"},
            {"feature_key": "call_attempts",          "weight": 4,  "description": "Call engagement count"},
            {"feature_key": "whatsapp_replies",       "weight": 3,  "description": "WhatsApp reply engagement"},
        ],
    },
    {
        "model_key":  "churn_predict_v1",
        "model_type": "churn_predict",
        "version":    "1.0.0",
        "description": "Rule-based churn risk scoring for active accounts.",
        "algorithm":  "rule_based",
        "recompute_interval_hours": 24,
        "is_active": True,
        "feature_weights": [
            {"feature_key": "days_since_last_invoice_paid", "weight": 35, "description": "Invoice payment recency"},
            {"feature_key": "subscription_status",          "weight": 30, "description": "Subscription health signal"},
            {"feature_key": "open_support_cases",           "weight": 25, "description": "Open case count"},
            {"feature_key": "days_since_last_activity",     "weight": 15, "description": "Engagement recency"},
            {"feature_key": "follow_up_breach_count",       "weight": 10, "description": "Enforcement breach count"},
            {"feature_key": "nps_score_low",                "weight": 15, "description": "Low NPS signal"},
        ],
    },
    {
        "model_key":  "clv_estimate_v1",
        "model_type": "clv_estimate",
        "version":    "1.0.0",
        "description": "Historical revenue projection: avg_monthly × horizon × retention_rate.",
        "algorithm":  "rule_based",
        "recompute_interval_hours": 168,  # weekly
        "is_active": True,
        "feature_weights": [
            {"feature_key": "avg_monthly_revenue", "weight": 60, "description": "Average paid invoice amount per month"},
            {"feature_key": "retention_rate",      "weight": 40, "description": "1.0 - churn_probability"},
        ],
    },
]


# ── Lead Score computation ─────────────────────────────────────────────────────

_STAGE_SCORE: dict[str, int] = {
    "OPEN":        0,
    "qualifying":  10,
    "nurturing":   15,
    "proposal":    22,
    "negotiation": 28,
    "won":         0,
    "lost":        0,
}

_VALUE_SCORE: list[tuple[int, int]] = [
    (500_000, 14),
    (200_000, 12),
    (50_000,  10),
    (0,        5),
]

_RECENCY_SCORE: list[tuple[int, int]] = [
    (3,  12),
    (7,   9),
    (14,  6),
    (30,  3),
    (999, 0),
]

_SOURCE_SCORE: dict[str, int] = {
    "inbound":          7,
    "referral":         7,
    "whatsapp_inbound": 6,
    "whatsapp":         6,
    "social":           4,
    "web":              4,
    "campaign":         3,
    "cold_outreach":    2,
    "manual":           2,
    "import":           1,
}

_TIER_SCORE: dict[str, int] = {
    "Enterprise":  6,
    "Mid-Market":  4,
    "SMB":         2,
    "Individual":  1,
}


def compute_lead_score(features: dict[str, Any]) -> int:
    """Weighted-sum lead score clamped to 0–100.

    features keys (all optional, default to 0):
      deal_stage, follow_up_count, estimated_value, days_since_last_contact,
      email_open_rate, source_quality, account_tier, call_attempts, whatsapp_replies
    """
    score = 0

    # deal_stage (0–28)
    score += _STAGE_SCORE.get(features.get("deal_stage", "OPEN"), 0)

    # follow_up_count (0–18)
    fu = features.get("follow_up_count", 0)
    score += min(18, fu * 3)

    # estimated_value (0–14)
    val = features.get("estimated_value", 0)
    for threshold, pts in _VALUE_SCORE:
        if val >= threshold:
            score += pts
            break

    # days_since_last_contact (0–12)
    days = features.get("days_since_last_contact", 999)
    for threshold, pts in _RECENCY_SCORE:
        if days <= threshold:
            score += pts
            break

    # email_open_rate (0–8): rate is 0.0–1.0
    rate = min(1.0, max(0.0, features.get("email_open_rate", 0.0)))
    score += round(rate * 8)

    # source_quality (0–7)
    score += _SOURCE_SCORE.get(features.get("source_quality", ""), 2)

    # account_tier (0–6)
    score += _TIER_SCORE.get(features.get("account_tier", "Individual"), 1)

    # call_attempts (0–4)
    score += min(4, features.get("call_attempts", 0))

    # whatsapp_replies (0–3)
    score += min(3, features.get("whatsapp_replies", 0))

    return max(0, min(100, score))


def classify_score_band(score: int) -> str:
    if score >= 75:
        return ScoreBand.hot.value
    if score >= 50:
        return ScoreBand.warm.value
    if score >= 25:
        return ScoreBand.cold.value
    return ScoreBand.disqualified.value


def compute_trend(current: int, previous: int | None) -> tuple[str, int | None]:
    if previous is None:
        return ScoreTrend.stable.value, None
    delta = current - previous
    if delta > 3:
        return ScoreTrend.rising.value, delta
    if delta < -3:
        return ScoreTrend.falling.value, delta
    return ScoreTrend.stable.value, delta


def build_lead_score_drivers(features: dict[str, Any]) -> list[dict]:
    drivers = []
    stage = features.get("deal_stage", "OPEN")
    stage_pts = _STAGE_SCORE.get(stage, 0)
    drivers.append({
        "feature_key":   "deal_stage",
        "feature_label": f"Deal Stage: {stage}",
        "contribution":  stage_pts,
        "direction":     "positive" if stage_pts > 0 else "negative",
        "value":         stage,
    })
    days = features.get("days_since_last_contact", 999)
    recency_pts = next((pts for t, pts in _RECENCY_SCORE if days <= t), 0)
    drivers.append({
        "feature_key":   "days_since_last_contact",
        "feature_label": f"Days Since Contact: {days}",
        "contribution":  recency_pts,
        "direction":     "positive" if recency_pts >= 6 else "negative",
        "value":         str(days),
    })
    fu = features.get("follow_up_count", 0)
    fu_pts = min(18, fu * 3)
    drivers.append({
        "feature_key":   "follow_up_count",
        "feature_label": f"Follow-up Count: {fu}",
        "contribution":  fu_pts,
        "direction":     "positive" if fu_pts > 0 else "negative",
        "value":         str(fu),
    })
    return sorted(drivers, key=lambda d: d["contribution"], reverse=True)[:5]


# ── Churn prediction computation ──────────────────────────────────────────────

def compute_churn_probability(risk_features: dict[str, Any]) -> float:
    """Accumulate risk factor contributions. Returns probability 0.000–1.000."""
    prob = 0.0

    days_paid = risk_features.get("days_since_last_invoice_paid", 0)
    if days_paid > 60:
        prob += 0.35
    elif days_paid > 30:
        prob += 0.20
    elif days_paid > 15:
        prob += 0.10

    open_cases = risk_features.get("open_support_cases", 0)
    if open_cases > 3:
        prob += 0.25
    elif open_cases >= 1:
        prob += 0.10

    sub_status = risk_features.get("subscription_status", "")
    if sub_status == "past_due":
        prob += 0.30
    elif sub_status == "paused":
        prob += 0.20

    days_inactive = risk_features.get("days_since_last_activity", 0)
    if days_inactive > 45:
        prob += 0.15
    elif days_inactive > 30:
        prob += 0.08

    if risk_features.get("follow_up_breach_count", 0) > 2:
        prob += 0.10

    if risk_features.get("nps_score_low", False):
        prob += 0.15

    return round(min(1.0, prob), 3)


def classify_churn_risk(probability: float) -> str:
    if probability >= 0.65:
        return ChurnRiskBand.high.value
    if probability >= 0.35:
        return ChurnRiskBand.medium.value
    return ChurnRiskBand.low.value


# ── CLV estimation ────────────────────────────────────────────────────────────

def compute_clv(
    avg_monthly_revenue: float,
    clv_horizon_months: int,
    churn_probability: float,
) -> tuple[float, float, str]:
    """Returns (estimated_clv, confidence_score, evidence_anchor)."""
    retention_rate = 1.0 - churn_probability
    clv = round(avg_monthly_revenue * clv_horizon_months * retention_rate, 2)
    confidence = 0.75 if avg_monthly_revenue > 0 else 0.30
    anchor = (
        f"avg monthly revenue: PKR {avg_monthly_revenue:,.0f} "
        f"× {clv_horizon_months} months × retention_rate {retention_rate:.2f}"
    )
    return clv, confidence, anchor


# ── Suggestion validation ─────────────────────────────────────────────────────

def validate_suggestion_body(body: dict) -> list[str]:
    """Returns a list of validation error strings. Empty list = valid."""
    errors: list[str] = []
    if not body.get("evidence_anchor"):
        errors.append("evidence_anchor is required — suggestions must be grounded in CRM data")
    if not body.get("title"):
        errors.append("title is required")
    if not body.get("body"):
        errors.append("body is required")
    stype = body.get("suggestion_type", "")
    valid_types = {t.value for t in SuggestionType}
    if stype not in valid_types:
        errors.append(f"suggestion_type '{stype}' is not valid — must be one of {sorted(valid_types)}")
    priority = body.get("priority", "")
    valid_priorities = {p.value for p in SuggestionPriority}
    if priority not in valid_priorities:
        errors.append(f"priority '{priority}' is not valid — must be one of {sorted(valid_priorities)}")
    return errors


# ── Staleness check ───────────────────────────────────────────────────────────

def is_stale(computed_at: datetime, recompute_interval_hours: int) -> bool:
    now = datetime.now(timezone.utc)
    if computed_at.tzinfo is None:
        computed_at = computed_at.replace(tzinfo=timezone.utc)
    age_hours = (now - computed_at).total_seconds() / 3600
    return age_hours > recompute_interval_hours


# ── Intent classification ─────────────────────────────────────────────────────

_INTENT_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"lead|prospect|contact|customer", re.I),      QueryIntent.lead.value),
    (re.compile(r"payment|invoice|collection|paid|bill|overdue", re.I), QueryIntent.payment.value),
    (re.compile(r"follow[\- ]?up|overdue|pending task|task", re.I), QueryIntent.followup.value),
    (re.compile(r"case|ticket|support|issue|complaint", re.I), QueryIntent.case.value),
]


def classify_query_intent(text: str) -> str:
    for pattern, intent in _INTENT_PATTERNS:
        if pattern.search(text):
            return intent
    return QueryIntent.oob.value
