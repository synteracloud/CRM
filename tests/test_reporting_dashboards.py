from __future__ import annotations

import unittest

from src.reporting_dashboards import DashboardApi, DashboardReadModelService


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

        self.assertEqual(service.get_sales("tenant-1").total_pipeline_amount, 1000)
        self.assertEqual(service.get_marketing("tenant-1").converted_lead_count, 1)
        self.assertEqual(service.get_support("tenant-1").sla_breach_count, 1)

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


if __name__ == "__main__":
    unittest.main()
