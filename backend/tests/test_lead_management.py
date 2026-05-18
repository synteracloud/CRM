from __future__ import annotations

import unittest

from src.lead_management import Lead, LeadService


class LeadServiceTests(unittest.TestCase):
    def test_lifecycle_create_qualify_convert_emits_events(self) -> None:
        emitted = []
        service = LeadService(event_sink=emitted.append)

        lead = Lead(
            lead_id="lead-1",
            tenant_id="tenant-1",
            owner_user_id="user-1",
            source="web_form",
            status="new",
            score=42,
            email="prospect@example.com",
            phone="+12065550100",
            company_name="Acme",
            created_at="2026-03-26T00:00:00Z",
        )

        service.create_lead(lead)
        service.qualify_lead("lead-1", qualified_at="2026-03-26T01:00:00Z")
        converted = service.convert_lead(
            "lead-1",
            converted_at="2026-03-26T02:00:00Z",
            account_id="acc-1",
            contact_id="con-1",
            opportunity_id="opp-1",
        )

        self.assertEqual(converted.status, "converted")
        self.assertEqual([evt.name for evt in emitted], ["lead_created", "lead_qualified", "lead_converted"])


if __name__ == "__main__":
    unittest.main()
