"""Aggregation logic for sales, marketing, and support reporting dashboards."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Iterable

from .entities import (
    DashboardLayoutConfig,
    DashboardReadModelNotFoundError,
    MarketingDashboardReadModel,
    SalesDashboardReadModel,
    SupportDashboardReadModel,
)


class DashboardReadModelService:
    """Builds and serves dashboard read models without direct raw query access."""

    def __init__(self) -> None:
        self._sales: dict[str, SalesDashboardReadModel] = {}
        self._marketing: dict[str, MarketingDashboardReadModel] = {}
        self._support: dict[str, SupportDashboardReadModel] = {}

    def refresh_sales(
        self,
        *,
        tenant_id: str,
        as_of: str,
        opportunities: Iterable[dict[str, object]],
    ) -> SalesDashboardReadModel:
        rows = [row for row in opportunities if row.get("tenant_id") == tenant_id]
        open_rows = [row for row in rows if not bool(row.get("is_closed"))]
        won_rows = [row for row in rows if bool(row.get("is_won"))]

        total_pipeline = sum(float(row.get("amount", 0) or 0) for row in open_rows)
        weighted_pipeline = sum(
            float(row.get("amount", 0) or 0) * _stage_weight(str(row.get("stage", "")))
            for row in open_rows
        )

        stage_counts: dict[str, int] = defaultdict(int)
        cycle_durations: list[float] = []
        trend: dict[str, dict[str, float]] = defaultdict(lambda: {"count": 0.0, "total_amount": 0.0})

        for row in rows:
            stage = str(row.get("stage", "unknown"))
            stage_counts[stage] += 1
            month = _year_month(str(row.get("created_at", as_of)))
            trend[month]["count"] += 1
            trend[month]["total_amount"] += float(row.get("amount", 0) or 0)

            if row.get("created_at") and row.get("is_closed") and row.get("updated_at"):
                cycle_durations.append(
                    _duration_hours(str(row["created_at"]), str(row["updated_at"])) / 24
                )

        read_model = SalesDashboardReadModel(
            tenant_id=tenant_id,
            as_of=as_of,
            total_pipeline_amount=round(total_pipeline, 2),
            weighted_pipeline_amount=round(weighted_pipeline, 2),
            open_opportunity_count=len(open_rows),
            won_opportunity_count=len(won_rows),
            avg_sales_cycle_days=round(_average(cycle_durations), 2),
            stage_counts=dict(stage_counts),
            monthly_trend=tuple(_sorted_trend(trend)),
        )
        self._sales[tenant_id] = read_model
        return read_model

    def refresh_marketing(
        self,
        *,
        tenant_id: str,
        as_of: str,
        leads: Iterable[dict[str, object]],
        assignments: Iterable[dict[str, object]],
    ) -> MarketingDashboardReadModel:
        leads_rows = [row for row in leads if row.get("tenant_id") == tenant_id]
        assignments_map = {
            str(item["lead_id"]): item for item in assignments if item.get("tenant_id") == tenant_id and item.get("lead_id")
        }

        qualified = [row for row in leads_rows if str(row.get("status")) == "qualified"]
        converted = [row for row in leads_rows if str(row.get("status")) == "converted"]

        source_counts: dict[str, int] = defaultdict(int)
        assignment_latencies: list[float] = []
        trend: dict[str, dict[str, float]] = defaultdict(lambda: {"lead_count": 0.0, "converted_count": 0.0})

        for row in leads_rows:
            source = str(row.get("source", "unknown"))
            source_counts[source] += 1
            month = _year_month(str(row.get("created_at", as_of)))
            trend[month]["lead_count"] += 1
            if str(row.get("status")) == "converted":
                trend[month]["converted_count"] += 1

            assignment = assignments_map.get(str(row.get("lead_id")))
            if assignment and row.get("created_at") and assignment.get("assigned_at"):
                assignment_latencies.append(
                    _duration_hours(str(row["created_at"]), str(assignment["assigned_at"]))
                )

        lead_count = len(leads_rows)
        conversion_rate = (len(converted) / lead_count) if lead_count else 0
        read_model = MarketingDashboardReadModel(
            tenant_id=tenant_id,
            as_of=as_of,
            lead_count=lead_count,
            qualified_lead_count=len(qualified),
            converted_lead_count=len(converted),
            conversion_rate=round(conversion_rate, 4),
            avg_assignment_latency_hours=round(_average(assignment_latencies), 2),
            source_counts=dict(source_counts),
            monthly_trend=tuple(_sorted_trend(trend)),
        )
        self._marketing[tenant_id] = read_model
        return read_model

    def refresh_support(
        self,
        *,
        tenant_id: str,
        as_of: str,
        cases: Iterable[dict[str, object]],
    ) -> SupportDashboardReadModel:
        rows = [row for row in cases if row.get("tenant_id") == tenant_id]
        open_rows = [row for row in rows if str(row.get("status")) in {"new", "open", "in_progress"}]
        resolved_rows = [row for row in rows if str(row.get("status")) in {"resolved", "closed"}]

        breached_rows: list[dict[str, object]] = []
        response_times: list[float] = []
        resolution_times: list[float] = []
        priority_counts: dict[str, int] = defaultdict(int)
        trend: dict[str, dict[str, float]] = defaultdict(lambda: {"opened": 0.0, "resolved": 0.0})

        for row in rows:
            priority_counts[str(row.get("priority", "unknown"))] += 1
            opened_month = _year_month(str(row.get("created_at", as_of)))
            trend[opened_month]["opened"] += 1

            if row.get("first_response_at") and row.get("created_at"):
                response_times.append(_duration_minutes(str(row["created_at"]), str(row["first_response_at"])))

            if row.get("resolved_at") and row.get("created_at"):
                resolution_times.append(_duration_hours(str(row["created_at"]), str(row["resolved_at"])))
                resolved_month = _year_month(str(row["resolved_at"]))
                trend[resolved_month]["resolved"] += 1

            due_at = row.get("sla_due_at")
            resolved_at = row.get("resolved_at")
            if due_at and resolved_at and _parse_rfc3339(str(resolved_at)) > _parse_rfc3339(str(due_at)):
                breached_rows.append(row)

        resolved_count = len(resolved_rows)
        breach_rate = (len(breached_rows) / resolved_count) if resolved_count else 0
        read_model = SupportDashboardReadModel(
            tenant_id=tenant_id,
            as_of=as_of,
            open_case_count=len(open_rows),
            resolved_case_count=resolved_count,
            sla_breach_count=len(breached_rows),
            breach_rate=round(breach_rate, 4),
            avg_first_response_minutes=round(_average(response_times), 2),
            avg_resolution_hours=round(_average(resolution_times), 2),
            priority_counts=dict(priority_counts),
            monthly_trend=tuple(_sorted_trend(trend)),
        )
        self._support[tenant_id] = read_model
        return read_model

    def get_sales(self, tenant_id: str) -> SalesDashboardReadModel:
        return self._get_or_raise(self._sales, tenant_id, "sales")

    def get_marketing(self, tenant_id: str) -> MarketingDashboardReadModel:
        return self._get_or_raise(self._marketing, tenant_id, "marketing")

    def get_support(self, tenant_id: str) -> SupportDashboardReadModel:
        return self._get_or_raise(self._support, tenant_id, "support")

    def build_dashboard(
        self,
        *,
        tenant_id: str,
        dashboard_type: str,
        layout: DashboardLayoutConfig,
    ) -> dict[str, object]:
        """Build a dashboard from read models using config-driven widget layout."""

        read_model = self.serialize(self._get_dashboard_model(tenant_id, dashboard_type))
        widgets: list[dict[str, object]] = []
        for widget in layout.widgets:
            raw_value = _metric_from_path(read_model, widget.metric_path)
            widgets.append(
                {
                    "widget_id": widget.widget_id,
                    "title": widget.title,
                    "widget_type": widget.widget_type,
                    "metric_path": widget.metric_path,
                    "raw_value": raw_value,
                    "display_value": _format_widget_value(raw_value, widget.format_as),
                    "format_as": widget.format_as,
                }
            )

        return {
            "dashboard_type": layout.dashboard_type,
            "title": layout.title,
            "columns": layout.columns,
            "widgets": widgets,
            "read_model": read_model,
        }

    @staticmethod
    def _get_or_raise(store: dict[str, object], tenant_id: str, dashboard: str) -> object:
        model = store.get(tenant_id)
        if not model:
            raise DashboardReadModelNotFoundError(
                f"Read model not found for tenant={tenant_id}, dashboard={dashboard}. Refresh the model first."
            )
        return model

    @staticmethod
    def serialize(read_model: object) -> dict[str, object]:
        return asdict(read_model)

    def _get_dashboard_model(self, tenant_id: str, dashboard_type: str) -> object:
        if dashboard_type == "sales":
            return self.get_sales(tenant_id)
        if dashboard_type == "marketing":
            return self.get_marketing(tenant_id)
        if dashboard_type == "support":
            return self.get_support(tenant_id)
        raise ValueError(f"Unsupported dashboard_type={dashboard_type}")


def _stage_weight(stage: str) -> float:
    weights = {
        "prospecting": 0.1,
        "qualification": 0.25,
        "proposal": 0.6,
        "negotiation": 0.8,
        "closed_won": 1.0,
        "closed_lost": 0.0,
    }
    return weights.get(stage, 0.2)


def _parse_rfc3339(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _duration_hours(start: str, end: str) -> float:
    return (_parse_rfc3339(end) - _parse_rfc3339(start)).total_seconds() / 3600


def _duration_minutes(start: str, end: str) -> float:
    return (_parse_rfc3339(end) - _parse_rfc3339(start)).total_seconds() / 60


def _year_month(value: str) -> str:
    parsed = _parse_rfc3339(value)
    return f"{parsed.year:04d}-{parsed.month:02d}"


def _average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0


def _sorted_trend(trend: dict[str, dict[str, float]]) -> list[dict[str, float]]:
    return [{"period": month, **metrics} for month, metrics in sorted(trend.items())]


def _metric_from_path(model: dict[str, object], path: str) -> object:
    current: object = model
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Metric path not found: {path}")
        current = current[part]
    return current


def _format_widget_value(value: object, format_as: str) -> str:
    if format_as == "currency":
        return f"${float(value):,.2f}"
    if format_as == "percent":
        return f"{float(value) * 100:.2f}%"
    if format_as == "integer":
        return f"{int(value):,}"
    return str(value)
