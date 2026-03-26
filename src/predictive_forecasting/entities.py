"""Predictive forecasting entities aligned with Opportunity fields from docs/domain-model.md."""

from __future__ import annotations

from dataclasses import dataclass


OPPORTUNITY_FORECAST_FIELDS: tuple[str, ...] = (
    "opportunity_id",
    "tenant_id",
    "stage",
    "amount",
    "close_date",
    "forecast_category",
    "is_closed",
    "is_won",
)

ALLOWED_FORECAST_CATEGORIES: tuple[str, ...] = ("pipeline", "best_case", "commit", "closed", "omitted")


@dataclass(frozen=True)
class OpportunityForecastRow:
    """Tenant-scoped opportunity row used by the forecast engine."""

    opportunity_id: str
    tenant_id: str
    stage: str
    amount: float
    close_date: str
    forecast_category: str
    is_closed: bool
    is_won: bool


@dataclass(frozen=True)
class ForecastBucket:
    key: str
    opportunity_count: int
    total_amount: float
    weighted_amount: float
    won_amount: float


@dataclass(frozen=True)
class OpportunityPrediction:
    opportunity_id: str
    tenant_id: str
    probability: float | None
    predicted_revenue: float
    confidence: str
    basis: tuple[str, ...]


@dataclass(frozen=True)
class ForecastTotals:
    opportunity_count: int
    open_count: int
    closed_count: int
    won_count: int
    lost_count: int
    total_pipeline_amount: float
    weighted_pipeline_amount: float
    won_revenue_amount: float
    predicted_revenue_amount: float


@dataclass(frozen=True)
class ForecastResult:
    tenant_id: str
    as_of: str
    totals: ForecastTotals
    by_stage: tuple[ForecastBucket, ...]
    by_forecast_category: tuple[ForecastBucket, ...]
    by_close_month: tuple[ForecastBucket, ...]
    predictions: tuple[OpportunityPrediction, ...]


class ForecastValidationError(ValueError):
    """Raised when forecast rows fail domain-model validation rules."""
