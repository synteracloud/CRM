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

SUBSCRIPTION_VALUE_FIELDS: tuple[str, ...] = (
    "subscription_id",
    "tenant_id",
    "status",
    "start_date",
    "end_date",
    "renewal_date",
    "invoice_amount_due_12m",
    "invoice_amount_paid_12m",
    "invoice_overdue_count_12m",
    "payment_failed_count_90d",
    "payment_success_count_90d",
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
class SubscriptionValueHistory:
    """Subscription + billing derived signals from Subscription/InvoiceSummary/PaymentEvent."""

    subscription_id: str
    tenant_id: str
    status: str
    start_date: str
    end_date: str | None
    renewal_date: str | None
    invoice_amount_due_12m: float
    invoice_amount_paid_12m: float
    invoice_overdue_count_12m: int
    payment_failed_count_90d: int
    payment_success_count_90d: int


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


@dataclass(frozen=True)
class CustomerLifetimeValuePrediction:
    """Prediction output for estimated remaining customer lifetime value."""

    subscription_id: str
    tenant_id: str
    estimated_clv: float
    confidence: str
    drivers: tuple[str, ...]


class PredictionValidationError(ValueError):
    """Raised when historical inputs or prediction payloads are invalid."""
