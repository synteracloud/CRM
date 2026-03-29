from __future__ import annotations

import unittest

from src.reporting_dashboards import (
    DashboardApi,
    DashboardLayoutConfig,
    DashboardReadModelService,
    WidgetDefinition,
)


class ReportingDashboardTests(unittest.TestCase):
    def test_all_dashboards_backed_by_read_models(self) -> None:
        service = DashboardReadModelService()

        service.refresh_sales(
            tenant_id="tenant-1",
            as_of="2026-03-26T00:00:00Z",
            opportunities=[
                {
                    "opportunity_id": "opp-1",
                    "tenant_id": "tenant-1",
                    "stage": "qualification",
                    "amount": 1000,
                    "is_closed": False,
                    "is_won": False,
                    "created_at": "2026-03-01T00:00:00Z",
                    "updated_at": "2026-03-05T00:00:00Z",
                },
                {
                    "opportunity_id": "opp-2",
                    "tenant_id": "tenant-1",
                    "stage": "closed_won",
                    "amount": 2000,
                    "is_closed": True,
                    "is_won": True,
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-20T00:00:00Z",
                },
            ],
        )

        service.refresh_marketing(
            tenant_id="tenant-1",
            as_of="2026-03-26T00:00:00Z",
            leads=[
                {
                    "lead_id": "lead-1",
                    "tenant_id": "tenant-1",
                    "status": "qualified",
                    "source": "web",
                    "created_at": "2026-03-01T00:00:00Z",
                },
                {
                    "lead_id": "lead-2",
                    "tenant_id": "tenant-1",
                    "status": "converted",
                    "source": "event",
                    "created_at": "2026-03-02T00:00:00Z",
                },
            ],
            assignments=[
                {
                    "lead_id": "lead-1",
                    "tenant_id": "tenant-1",
                    "assigned_at": "2026-03-01T02:00:00Z",
                },
                {
                    "lead_id": "lead-2",
                    "tenant_id": "tenant-1",
                    "assigned_at": "2026-03-02T01:00:00Z",
                },
            ],
        )

        service.refresh_support(
            tenant_id="tenant-1",
            as_of="2026-03-26T00:00:00Z",
            cases=[
                {
                    "case_id": "case-1",
                    "tenant_id": "tenant-1",
                    "status": "open",
                    "priority": "high",
                    "created_at": "2026-03-01T00:00:00Z",
                    "first_response_at": "2026-03-01T00:20:00Z",
                    "sla_due_at": "2026-03-03T00:00:00Z",
                },
                {
                    "case_id": "case-2",
                    "tenant_id": "tenant-1",
                    "status": "resolved",
                    "priority": "medium",
                    "created_at": "2026-03-02T00:00:00Z",
                    "first_response_at": "2026-03-02T00:10:00Z",
                    "resolved_at": "2026-03-03T00:00:00Z",
                    "sla_due_at": "2026-03-02T23:00:00Z",
                },
            ],
        )

        service.refresh_admin(
            tenant_id="tenant-1",
            as_of="2026-03-26T00:00:00Z",
            users=[
                {"tenant_id": "tenant-1", "user_id": "u-1", "role": "tenant_admin", "is_active": True},
                {"tenant_id": "tenant-1", "user_id": "u-2", "role": "manager", "is_active": True, "is_dormant": True},
            ],
            sessions=[
                {"tenant_id": "tenant-1", "session_id": "s1", "is_active": True, "risk_flag": True},
                {"tenant_id": "tenant-2", "session_id": "s2", "is_active": True, "risk_flag": True},
            ],
            entitlements=[
                {"tenant_id": "tenant-1", "feature": "forecasting", "enabled": True},
                {"tenant_id": "tenant-1", "feature": "audit", "enabled": True},
            ],
            audit_logs=[
                {"tenant_id": "tenant-1", "occurred_at": "2026-03-04T00:00:00Z", "sensitivity": "high"},
                {"tenant_id": "tenant-2", "occurred_at": "2026-03-05T00:00:00Z", "sensitivity": "high"},
            ],
        )

        self.assertEqual(service.get_sales("tenant-1").total_pipeline_amount, 1000)
        self.assertEqual(service.get_marketing("tenant-1").converted_lead_count, 1)
        self.assertEqual(service.get_support("tenant-1").sla_breach_count, 1)
        self.assertEqual(service.get_admin("tenant-1").active_session_risk_count, 1)

    def test_api_fetches_only_from_read_models(self) -> None:
        service = DashboardReadModelService()
        api = DashboardApi(service)

        not_ready = api.get_sales_dashboard("tenant-404", request_id="req-1")
        self.assertEqual(not_ready["error"]["code"], "not_found")

        service.refresh_sales(
            tenant_id="tenant-1",
            as_of="2026-03-26T00:00:00Z",
            opportunities=[
                {
                    "opportunity_id": "opp-1",
                    "tenant_id": "tenant-1",
                    "stage": "proposal",
                    "amount": 5000,
                    "is_closed": False,
                    "is_won": False,
                    "created_at": "2026-03-15T00:00:00Z",
                    "updated_at": "2026-03-18T00:00:00Z",
                }
            ],
        )
        ready = api.get_sales_dashboard("tenant-1", request_id="req-2")

        self.assertEqual(ready["meta"]["request_id"], "req-2")
        self.assertEqual(ready["data"]["open_opportunity_count"], 1)
        self.assertEqual(ready["data"]["weighted_pipeline_amount"], 3000.0)

    def test_dynamic_dashboard_engine_uses_configured_widgets(self) -> None:
        service = DashboardReadModelService()
        api = DashboardApi(service)

        service.refresh_sales(
            tenant_id="tenant-1",
            as_of="2026-03-26T00:00:00Z",
            opportunities=[
                {
                    "opportunity_id": "opp-1",
                    "tenant_id": "tenant-1",
                    "stage": "proposal",
                    "amount": 10000,
                    "is_closed": False,
                    "is_won": False,
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-13T00:00:00Z",
                },
                {
                    "opportunity_id": "opp-2",
                    "tenant_id": "tenant-1",
                    "stage": "closed_won",
                    "amount": 6000,
                    "is_closed": True,
                    "is_won": True,
                    "created_at": "2026-03-11T00:00:00Z",
                    "updated_at": "2026-03-20T00:00:00Z",
                },
            ],
        )

        layout = DashboardLayoutConfig(
            dashboard_type="sales",
            title="Sales pulse",
            columns=2,
            widgets=(
                WidgetDefinition(
                    widget_id="w-1",
                    title="Open opportunities",
                    widget_type="kpi",
                    metric_path="open_opportunity_count",
                    format_as="integer",
                    required_permissions=("reports.read",),
                    drilldown_route="/app/sales/{tenant_id}/pipeline/open",
                ),
                WidgetDefinition(
                    widget_id="w-2",
                    title="Weighted pipeline",
                    widget_type="kpi",
                    metric_path="weighted_pipeline_amount",
                    format_as="currency",
                    required_permissions=("reports.read",),
                ),
            ),
        )

        response = api.get_dynamic_dashboard(
            "tenant-1",
            "req-dynamic-1",
            layout=layout,
            role_ids=("manager",),
            permissions=("reports.read",),
            route_context={"tenant_id": "tenant-1"},
        )

        self.assertEqual(response["meta"]["request_id"], "req-dynamic-1")
        self.assertEqual(response["data"]["dashboard_type"], "sales")
        self.assertEqual(response["data"]["widgets"][0]["raw_value"], 1)
        self.assertEqual(response["data"]["widgets"][0]["display_value"], "1")
        self.assertEqual(response["data"]["widgets"][0]["drilldown_route"], "/app/sales/tenant-1/pipeline/open")
        self.assertEqual(response["data"]["widgets"][1]["display_value"], "$6,000.00")

    def test_dynamic_dashboard_rejects_invalid_metric_path(self) -> None:
        service = DashboardReadModelService()
        api = DashboardApi(service)

        service.refresh_support(
            tenant_id="tenant-2",
            as_of="2026-03-26T00:00:00Z",
            cases=[],
        )
        layout = DashboardLayoutConfig(
            dashboard_type="support",
            title="Support pulse",
            columns=1,
            widgets=(
                WidgetDefinition(
                    widget_id="w-404",
                    title="Bad metric",
                    widget_type="kpi",
                    metric_path="does_not_exist",
                ),
            ),
        )

        response = api.get_dynamic_dashboard("tenant-2", "req-dynamic-2", layout=layout)
        self.assertEqual(response["error"]["code"], "invalid_dashboard_config")

    def test_role_gate_and_widget_permissions(self) -> None:
        service = DashboardReadModelService()
        api = DashboardApi(service)

        service.refresh_admin(
            tenant_id="tenant-5",
            as_of="2026-03-26T00:00:00Z",
            users=[{"tenant_id": "tenant-5", "role": "tenant_owner", "is_active": True}],
            sessions=[],
            entitlements=[{"tenant_id": "tenant-5", "feature": "x", "enabled": True}],
            audit_logs=[{"tenant_id": "tenant-5", "occurred_at": "2026-03-26T00:00:00Z", "sensitivity": "high"}],
        )

        layout = DashboardLayoutConfig(
            dashboard_type="admin",
            title="Admin",
            columns=2,
            widgets=(
                WidgetDefinition(
                    widget_id="admin-kpi",
                    title="Sensitive actions",
                    widget_type="kpi",
                    metric_path="audit_sensitive_action_count",
                    format_as="integer",
                    required_permissions=("audit.logs.read",),
                ),
            ),
        )

        forbidden = api.get_dynamic_dashboard(
            "tenant-5",
            "req-admin-1",
            layout=layout,
            role_ids=("manager",),
            permissions=("audit.logs.read",),
        )
        self.assertEqual(forbidden["error"]["code"], "forbidden")

        filtered = api.get_dynamic_dashboard(
            "tenant-5",
            "req-admin-2",
            layout=layout,
            role_ids=("tenant_admin",),
            permissions=("reports.read",),
        )
        self.assertEqual(filtered["data"]["widgets"], [])

        allowed = api.get_dynamic_dashboard(
            "tenant-5",
            "req-admin-3",
            layout=layout,
            role_ids=("tenant_admin",),
            permissions=("audit.logs.read",),
        )
        self.assertEqual(allowed["data"]["widgets"][0]["raw_value"], 1)


if __name__ == "__main__":
    unittest.main()
