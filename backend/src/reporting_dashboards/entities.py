"""Dashboard read models aligned to docs/read-models.md and docs/domain-model.md."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


DASHBOARD_TYPE = ("sales", "marketing", "support", "admin")
WIDGET_ZONE = ("posture", "primary_kpi", "execution_queue", "trend_diagnostic", "risk_anomaly")
WIDGET_STATE = ("default", "loading", "empty", "error", "restricted")


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


@dataclass(frozen=True)
class AdminDashboardReadModel:
    """Read model for tenant administration, identity posture, and audit risk."""

    tenant_id: str
    as_of: str
    active_user_count: int
    privileged_user_count: int
    dormant_user_count: int
    active_session_risk_count: int
    entitlement_feature_count: int
    audit_sensitive_action_count: int
    monthly_audit_trend: tuple[dict[str, float], ...]


class DashboardReadModelNotFoundError(KeyError):
    """Raised when read models have not yet been built for a dashboard."""


@dataclass(frozen=True)
class WidgetDefinition:
    """Config-driven widget mapped to a read-model metric path."""

    widget_id: str
    title: str
    widget_type: str
    metric_path: str
    zone: Literal["posture", "primary_kpi", "execution_queue", "trend_diagnostic", "risk_anomaly"] = "primary_kpi"
    format_as: str = "raw"
    required_permissions: tuple[str, ...] = field(default_factory=tuple)
    drilldown_route: str | None = None
    empty_value: object | None = None


@dataclass(frozen=True)
class DashboardLayoutConfig:
    """Config-driven dashboard layout based strictly on read-model metrics."""

    dashboard_type: str
    title: str
    columns: int
    widgets: tuple[WidgetDefinition, ...]


@dataclass(frozen=True)
class RoleDashboardMapping:
    """Role-level dashboard eligibility and default dashboard selection order."""

    role_id: str
    dashboard_types: tuple[str, ...]
    default_dashboard_type: str


@dataclass(frozen=True)
class DashboardQcVerdict:
    """Quality-control verdict for role dashboard and widget contracts."""

    role_accuracy: bool
    widget_zone_coverage: bool
    score_out_of_ten: int
