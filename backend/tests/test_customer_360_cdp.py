from __future__ import annotations

import unittest

from src.customer_360_cdp import (
    AccountRecord,
    ActivityRecord,
    ContactRecord,
    Customer360Service,
    LeadRecord,
    MissingRelationError,
)


class Customer360ServiceTests(unittest.TestCase):
    def test_builds_unified_profile_and_deduplicates_identity(self) -> None:
        service = Customer360Service()

        service.upsert_account(
            AccountRecord(
                account_id="acc-1",
                tenant_id="tenant-1",
                name="Acme",
                status="active",
                created_at="2026-03-26T00:00:00Z",
            )
        )
        service.upsert_contact(
            ContactRecord(
                contact_id="con-1",
                tenant_id="tenant-1",
                account_id="acc-1",
                first_name="Ava",
                last_name="Jones",
                email="Ava@example.com",
                phone="+12065550100",
                created_at="2026-03-26T01:00:00Z",
            )
        )
        service.upsert_lead(
            LeadRecord(
                lead_id="lead-1",
                tenant_id="tenant-1",
                email="ava@example.com",
                phone="+12065550100",
                company_name="Acme",
                created_at="2026-03-26T02:00:00Z",
            )
        )
        service.link_lead("lead-1", contact_id="con-1", account_id="acc-1")
        service.add_activity(
            ActivityRecord(
                activity_id="act-1",
                tenant_id="tenant-1",
                entity_type="contact",
                entity_id="con-1",
                activity_type="email_open",
                occurred_at="2026-03-26T03:00:00Z",
            )
        )

        profile = service.build_profile(
            tenant_id="tenant-1",
            profile_id="profile-1",
            lead_id="lead-1",
        )

        self.assertEqual(profile.lead_ids, ("lead-1",))
        self.assertEqual(profile.contact_ids, ("con-1",))
        self.assertEqual(profile.account_ids, ("acc-1",))
        self.assertEqual(profile.activity_ids, ("act-1",))
        self.assertEqual(profile.identity.all_emails, ("ava@example.com",))
        self.assertEqual(profile.identity.all_phones, ("+12065550100",))

    def test_raises_for_unresolved_contact_account_relation(self) -> None:
        service = Customer360Service()
        service.upsert_contact(
            ContactRecord(
                contact_id="con-2",
                tenant_id="tenant-1",
                account_id="acc-missing",
                first_name="Lee",
                last_name="Tran",
                email="lee@example.com",
                phone="+12065550999",
                created_at="2026-03-26T01:00:00Z",
            )
        )

        with self.assertRaises(MissingRelationError):
            service.build_profile(
                tenant_id="tenant-1",
                profile_id="profile-2",
                contact_id="con-2",
            )


if __name__ == "__main__":
    unittest.main()
