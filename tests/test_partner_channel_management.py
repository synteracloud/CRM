import unittest

from src.partner_channel_management import (
    DealRegistration,
    OpportunityRecord,
    Partner,
    PartnerAttribution,
    PartnerChannelService,
    PartnerRelationship,
)


class PartnerChannelManagementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PartnerChannelService()
        self.partner = self.service.create_partner(
            Partner(
                partner_id="partner-1",
                tenant_id="tenant-1",
                partner_code="P-001",
                name="Northwind Channel",
                partner_type="reseller",
                status="active",
                owner_user_id="user-channel-1",
            )
        )
        self.opportunity = self.service.register_opportunity(
            OpportunityRecord(
                opportunity_id="opp-1",
                tenant_id="tenant-1",
                account_id="account-1",
                owner_user_id="user-direct-1",
                stage="qualified",
            )
        )

    def test_channel_flow_deal_registration_attribution_lock_preserves_owner(self) -> None:
        relationship = self.service.activate_relationship(
            PartnerRelationship(
                partner_relationship_id="rel-1",
                tenant_id="tenant-1",
                partner_id="partner-1",
                account_id="account-1",
                opportunity_id="opp-1",
                relationship_type="deal_registration",
                source_channel="partner_portal",
                status="active",
            )
        )
        self.assertEqual(relationship.status, "active")

        registration = self.service.register_deal(
            DealRegistration(
                deal_registration_id="reg-1",
                tenant_id="tenant-1",
                partner_id="partner-1",
                account_id="account-1",
                opportunity_id="opp-1",
                registered_at="2026-04-01T10:00:00Z",
                window_end_at="2026-05-01T10:00:00Z",
            )
        )
        self.assertEqual(registration.partner_id, "partner-1")

        self.service.add_candidate_attribution(
            PartnerAttribution(
                partner_attribution_id="attr-1",
                tenant_id="tenant-1",
                partner_id="partner-1",
                opportunity_id="opp-1",
                account_id="account-1",
                attribution_type="sourced",
                attribution_model="first_touch",
                attribution_weight=1.0,
                attribution_status="candidate",
            )
        )

        locked = self.service.lock_attribution(
            tenant_id="tenant-1",
            opportunity_id="opp-1",
            locked_at="2026-04-02T12:00:00Z",
        )
        self.assertEqual(len(locked), 1)
        self.assertEqual(locked[0].attribution_status, "locked")
        self.assertEqual(self.service.get_opportunity("opp-1").owner_user_id, "user-direct-1")

    def test_split_attribution_requires_total_weight_1(self) -> None:
        self.service.add_candidate_attribution(
            PartnerAttribution(
                partner_attribution_id="attr-s1",
                tenant_id="tenant-1",
                partner_id="partner-1",
                opportunity_id="opp-1",
                account_id="account-1",
                attribution_type="influenced",
                attribution_model="split",
                attribution_weight=0.7,
                attribution_status="candidate",
            )
        )
        self.service.add_candidate_attribution(
            PartnerAttribution(
                partner_attribution_id="attr-s2",
                tenant_id="tenant-1",
                partner_id="partner-1",
                opportunity_id="opp-1",
                account_id="account-1",
                attribution_type="influenced",
                attribution_model="split",
                attribution_weight=0.2,
                attribution_status="candidate",
            )
        )

        with self.assertRaisesRegex(Exception, "total active weight of 1.0"):
            self.service.lock_attribution(
                tenant_id="tenant-1",
                opportunity_id="opp-1",
                locked_at="2026-04-02T12:00:00Z",
            )

    def test_deal_registration_conflict_detected(self) -> None:
        self.service.register_deal(
            DealRegistration(
                deal_registration_id="reg-1",
                tenant_id="tenant-1",
                partner_id="partner-1",
                account_id="account-1",
                opportunity_id="opp-1",
                registered_at="2026-04-01T10:00:00Z",
                window_end_at="2026-04-20T10:00:00Z",
            )
        )
        with self.assertRaisesRegex(Exception, "Registration conflict"):
            self.service.register_deal(
                DealRegistration(
                    deal_registration_id="reg-2",
                    tenant_id="tenant-1",
                    partner_id="partner-1",
                    account_id="account-1",
                    opportunity_id="opp-1",
                    registered_at="2026-04-10T10:00:00Z",
                    window_end_at="2026-04-30T10:00:00Z",
                )
            )


if __name__ == "__main__":
    unittest.main()
