from __future__ import annotations

import unittest

from services.activity import ActivityControlEngine, ActorContext, EntityRecord
from services.collections import CollectionsService, Invoice
from services.dashboard.owner import OwnerControlDashboardService
from src.lead_management import Lead, LeadService


class _StubAdapter:
    provider_name = "bank_transfer"

    def normalize_transaction(self, payload: dict[str, object]) -> dict[str, object]:
        return {
            "provider_txn_id": payload["txn_id"],
            "invoice_ref": payload.get("invoice_ref"),
            "customer_ref": payload["customer_id"],
            "amount": payload["amount"],
            "currency": payload.get("currency", "USD"),
            "status": payload.get("status", "succeeded"),
            "received_at": payload["received_at"],
        }

    def verify_callback(self, signature: str, payload: dict[str, object]) -> bool:
        return signature == "ok"


class OwnerControlDashboardTests(unittest.TestCase):
    def test_owner_dashboard_rolls_up_kpis_visibility_alerts_and_qc(self) -> None:
        leads = LeadService()
        collections = CollectionsService(adapters={"bank_transfer": _StubAdapter()})
        activity = ActivityControlEngine()

        leads.create_lead(
            Lead(
                lead_id="lead-1",
                tenant_id="tenant-1",
                owner_user_id="emp-1",
                source="web",
                status="new",
                score=70,
                email="a@example.com",
                phone="1",
                company_name="A",
                created_at="2026-03-20T00:00:00Z",
            )
        )
        leads.create_lead(
            Lead(
                lead_id="lead-2",
                tenant_id="tenant-1",
                owner_user_id="emp-2",
                source="event",
                status="qualified",
                score=82,
                email="b@example.com",
                phone="2",
                company_name="B",
                created_at="2026-03-21T00:00:00Z",
            )
        )
        leads.create_lead(
            Lead(
                lead_id="lead-3",
                tenant_id="tenant-1",
                owner_user_id="emp-1",
                source="referral",
                status="converted",
                score=90,
                email="c@example.com",
                phone="3",
                company_name="C",
                created_at="2026-03-22T00:00:00Z",
                converted_at="2026-03-25T00:00:00Z",
            )
        )

        actor = ActorContext(actor_id="emp-1", actor_name="E1", actor_role="sales_rep", team_id="t-a")
        activity.register_entity(
            EntityRecord(
                tenant_id="tenant-1",
                entity_type="lead",
                entity_id="lead-1",
                owner_id="emp-1",
                owner_team_id="t-a",
                last_activity_at="2026-03-20T00:00:00Z",
            ),
            actor,
            "req-1",
            "tr-1",
        )

        collections.create_invoice(
            Invoice(
                invoice_id="inv-1",
                invoice_number="INV-1",
                customer_id="cust-1",
                issue_date="2026-03-22",
                due_date="2026-03-28",
                currency="USD",
                total_amount=1000,
                metadata={"owner_user_id": "emp-1"},
            )
        )
        collections.ingest_payment(
            "bank_transfer",
            "ok",
            {
                "txn_id": "p-1",
                "invoice_ref": "INV-1",
                "customer_id": "cust-1",
                "amount": 1000,
                "currency": "USD",
                "status": "succeeded",
                "received_at": "2026-03-24T10:00:00Z",
                "owner_user_id": "emp-1",
            },
        )

        svc = OwnerControlDashboardService(
            lead_service=leads,
            activity_engine=activity,
            collections_service=collections,
            overdue_lead_hours=72,
            missed_followup_hours=48,
        )

        dashboard = svc.build_dashboard("tenant-1", "2026-03-30T00:00:00Z")

        self.assertEqual(dashboard.kpis.leads, 3)
        self.assertEqual(dashboard.kpis.conversions, 1)
        self.assertEqual(dashboard.kpis.revenue, 1000)
        self.assertEqual(dashboard.kpis.collections, 1000)

        self.assertEqual(dashboard.pipeline_status.status_counts["new"], 1)
        self.assertEqual(dashboard.pipeline_status.status_counts["qualified"], 1)
        self.assertEqual(dashboard.pipeline_status.status_counts["converted"], 1)

        self.assertIn("lead-2", dashboard.alerts.overdue_leads)
        self.assertIn("lead-2", dashboard.alerts.missed_follow_ups)

        self.assertEqual(dashboard.qc.alignment_percent, 100.0)
        self.assertEqual(dashboard.qc.score, "10/10")
        self.assertTrue(dashboard.qc.fixed_to_ten_on_ten)


if __name__ == "__main__":
    unittest.main()
