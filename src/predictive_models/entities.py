"""Predictive model entities based on historical CRM domain entities."""

from __future__ import annotations

from dataclasses import dataclass


OPPORTUNITY_HISTORY_FIELDS: tuple[str, ...] = (
    "opportunity_id",
    "tenant_id",
    "stage",
    "amount",
    "forecast_category",
    "is_closed",
    "is_won",
    "created_at",
    "close_date",
)

SUBSCRIPTION_HISTORY_FIELDS: tuple[str, ...] = (
    "subscription_id",
    "tenant_id",
    "status",
    "mrr",
    "started_at",
    "current_period_end",
    "last_payment_at",
    "late_payment_count",
    "support_case_count_90d",
)


@dataclass(frozen=True)
class OpportunityHistory:
    """Historical opportunity state used for win probability calibration."""

    opportunity_id: str
    tenant_id: str
    stage: str
    amount: float
    forecast_category: str
    is_closed: bool
    is_won: bool
    created_at: str
    close_date: str


@dataclass(frozen=True)
class SubscriptionHistory:
    """Historical subscription/account state used for churn risk scoring."""

    subscription_id: str
    tenant_id: str
    status: str
    mrr: float
    started_at: str
    current_period_end: str
    last_payment_at: str
    late_payment_count: int
    support_case_count_90d: int


@dataclass(frozen=True)
class WinProbabilityPrediction:
    """Prediction output for an active opportunity."""

    opportunity_id: str
    tenant_id: str
    probability: float
    confidence: str
    drivers: tuple[str, ...]


@dataclass(frozen=True)
class ChurnPrediction:
    """Prediction output for an active subscription/account."""

    subscription_id: str
    tenant_id: str
    churn_probability: float
    risk_level: str
    drivers: tuple[str, ...]


class PredictionValidationError(ValueError):
    """Raised when historical inputs or prediction payloads are invalid."""
