from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OwnerKpis:
    leads: int
    conversions: int
    conversion_rate: float
    revenue: float
    collections: float


@dataclass(frozen=True)
class EmployeePerformance:
    employee_id: str
    leads: int
    conversions: int
    conversion_rate: float
    revenue: float
    collections: float


@dataclass(frozen=True)
class PipelineStatus:
    status_counts: dict[str, int]


@dataclass(frozen=True)
class OwnerAlerts:
    overdue_leads: tuple[str, ...]
    missed_follow_ups: tuple[str, ...]


@dataclass(frozen=True)
class VisibilityQc:
    coverage_checks: dict[str, bool]
    blind_spots: tuple[str, ...]
    alignment_percent: float
    score: str
    fixed_to_ten_on_ten: bool = False


@dataclass(frozen=True)
class OwnerDashboard:
    tenant_id: str
    as_of: str
    kpis: OwnerKpis
    per_employee_performance: tuple[EmployeePerformance, ...]
    pipeline_status: PipelineStatus
    alerts: OwnerAlerts
    qc: VisibilityQc
    diagnostics: dict[str, object] = field(default_factory=dict)
