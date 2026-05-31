"""ORM models for AI / Predictive Models domain.

Spec: backend/docs/domain/ai-predictive-models.md
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
)

from services.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class LeadScore(Base):
    """Latest AI score for a lead. New row created on each recompute."""

    __tablename__ = "lead_scores"

    score_id         = Column(String(36), primary_key=True, default=_uuid)
    tenant_id        = Column(String(50), nullable=False, index=True)
    lead_id          = Column(String(36), nullable=False, index=True)
    model_id         = Column(String(50), nullable=False, default="lead_score_v1")
    score            = Column(Integer, nullable=False)
    score_band       = Column(String(20), nullable=False)   # hot|warm|cold|disqualified
    trend            = Column(String(10), nullable=False)   # rising|stable|falling
    trend_delta      = Column(Integer, nullable=True)
    top_drivers      = Column(JSON, nullable=True)          # FeatureContribution[]
    confidence_score = Column(Numeric(3, 2), nullable=False, default=0.85)
    is_stale         = Column(Boolean, nullable=False, default=False)
    computed_at      = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    created_at       = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_lead_score_range"),
        CheckConstraint(
            "score_band IN ('hot','warm','cold','disqualified')",
            name="ck_lead_score_band",
        ),
        CheckConstraint(
            "trend IN ('rising','stable','falling')",
            name="ck_lead_score_trend",
        ),
        Index("ix_lead_scores_tenant_lead", "tenant_id", "lead_id"),
    )


class ChurnPrediction(Base):
    """Churn probability prediction for an account."""

    __tablename__ = "churn_predictions"

    prediction_id      = Column(String(36), primary_key=True, default=_uuid)
    tenant_id          = Column(String(50), nullable=False, index=True)
    account_id         = Column(String(36), nullable=False, index=True)
    model_id           = Column(String(50), nullable=False, default="churn_predict_v1")
    churn_probability  = Column(Numeric(4, 3), nullable=False)
    risk_band          = Column(String(10), nullable=False)   # high|medium|low
    top_drivers        = Column(JSON, nullable=True)
    recommended_action = Column(String(255), nullable=True)
    confidence_score   = Column(Numeric(3, 2), nullable=False, default=0.80)
    evidence_anchor    = Column(String(500), nullable=False)
    is_stale           = Column(Boolean, nullable=False, default=False)
    computed_at        = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    created_at         = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    __table_args__ = (
        CheckConstraint(
            "risk_band IN ('high','medium','low')",
            name="ck_churn_risk_band",
        ),
        Index("ix_churn_predictions_tenant_account", "tenant_id", "account_id"),
    )


class CLVEstimate(Base):
    """Customer Lifetime Value estimate for an account."""

    __tablename__ = "clv_estimates"

    estimate_id        = Column(String(36), primary_key=True, default=_uuid)
    tenant_id          = Column(String(50), nullable=False, index=True)
    account_id         = Column(String(36), nullable=False, index=True)
    model_id           = Column(String(50), nullable=False, default="clv_estimate_v1")
    estimated_clv      = Column(Numeric(18, 2), nullable=False)
    clv_horizon_months = Column(Integer, nullable=False, default=24)
    confidence_score   = Column(Numeric(3, 2), nullable=False, default=0.75)
    evidence_anchor    = Column(String(500), nullable=False)
    is_stale           = Column(Boolean, nullable=False, default=False)
    computed_at        = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    created_at         = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    __table_args__ = (
        Index("ix_clv_estimates_tenant_account", "tenant_id", "account_id"),
    )


class CopilotSuggestion(Base):
    """AI-generated advisory suggestion for a CRM user. Advisory-only — no auto-action."""

    __tablename__ = "copilot_suggestions"

    suggestion_id    = Column(String(36), primary_key=True, default=_uuid)
    tenant_id        = Column(String(50), nullable=False, index=True)
    target_user_id   = Column(String(36), nullable=False, index=True)
    suggestion_type  = Column(String(30), nullable=False)
    priority         = Column(String(10), nullable=False)
    title            = Column(String(100), nullable=False)
    body             = Column(String(500), nullable=False)
    action_label     = Column(String(50), nullable=False)
    action_href      = Column(String(255), nullable=False)
    evidence_anchor  = Column(String(500), nullable=False)
    entity_type      = Column(String(30), nullable=True)
    entity_id        = Column(String(36), nullable=True)
    confidence_score = Column(Numeric(3, 2), nullable=False, default=0.80)
    is_dismissed     = Column(Boolean, nullable=False, default=False)
    dismissed_at     = Column(DateTime(timezone=True), nullable=True)
    is_actioned      = Column(Boolean, nullable=False, default=False)
    actioned_at      = Column(DateTime(timezone=True), nullable=True)
    expires_at       = Column(DateTime(timezone=True), nullable=True)
    created_at       = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at       = Column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )

    __table_args__ = (
        CheckConstraint(
            "suggestion_type IN ('next_action','risk_flag','deal_nudge',"
            "'follow_up_overdue','sla_breach_alert','stale_deal')",
            name="ck_suggestion_type",
        ),
        CheckConstraint(
            "priority IN ('urgent','high','medium','low')",
            name="ck_suggestion_priority",
        ),
        Index("ix_copilot_suggestions_tenant_user", "tenant_id", "target_user_id"),
    )
