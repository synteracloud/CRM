"""Dashboard read models aligned to docs/read-models.md and docs/domain-model.md."""

from __future__ import annotations

from dataclasses import dataclass


DASHBOARD_TYPE = ("sales", "marketing", "support")


@dataclass(frozen=True)
class SalesDashboardReadModel:
    """Read model for sales dashboard metrics from opportunities and quotes."""

    tenant_id: str
    as_of: str
    total_pipeline_amount: float
    weighted_pipeline_amount: float
    open_opportunity_count: int
    won_opportunity_count: int
    avg_sales_cycle_days: float
    stage_counts: dict[str, int]
    monthly_trend: tuple[dict[str, float], ...]


@dataclass(frozen=True)
class MarketingDashboardReadModel:
    """Read model for marketing dashboard metrics from leads and campaigns."""

    tenant_id: str
    as_of: str
    lead_count: int
    qualified_lead_count: int
    converted_lead_count: int
    conversion_rate: float
    avg_assignment_latency_hours: float
    source_counts: dict[str, int]
    monthly_trend: tuple[dict[str, float], ...]


@dataclass(frozen=True)
class SupportDashboardReadModel:
    """Read model for support dashboard metrics from cases and case comments."""

    tenant_id: str
    as_of: str
    open_case_count: int
    resolved_case_count: int
    sla_breach_count: int
    breach_rate: float
    avg_first_response_minutes: float
    avg_resolution_hours: float
    priority_counts: dict[str, int]
    monthly_trend: tuple[dict[str, float], ...]


class DashboardReadModelNotFoundError(KeyError):
    """Raised when read models have not yet been built for a dashboard."""
