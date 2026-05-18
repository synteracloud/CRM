from __future__ import annotations

import unittest

from src.campaigns import (
    Campaign,
    CampaignContactLink,
    CampaignLeadLink,
    CampaignService,
    SegmentDefinition,
    SegmentRule,
    SegmentValidationError,
    assert_campaign_workflow_events_are_catalog_backed,
)


class CampaignServiceTests(unittest.TestCase):
    def test_campaign_lifecycle_and_linking(self) -> None:
        service = CampaignService()

        segment = SegmentDefinition(
            segment_id="seg-1",
            tenant_id="tenant-1",
            name="Qualified leads",
            description="Leads with score >= 60",
            entity_type="lead",
            rules=(
                SegmentRule(field="score", operator="gte", value=60),
                SegmentRule(field="status", operator="eq", value="qualified"),
            ),
            created_at="2026-03-26T00:00:00Z",
            updated_at="2026-03-26T00:00:00Z",
        )
        service.create_segment(segment)

        campaign = Campaign(
            campaign_id="cmp-1",
            tenant_id="tenant-1",
            owner_user_id="usr-1",
            name="Q2 Upsell",
            description="Qualified-lead outreach",
            status="draft",
            segment_id="seg-1",
            starts_at="2026-04-01T00:00:00Z",
            ends_at="2026-06-30T23:59:59Z",
            created_at="2026-03-26T00:00:00Z",
            updated_at="2026-03-26T00:00:00Z",
        )
        created = service.create_campaign(campaign)
        self.assertEqual(created.status, "draft")

        activated = service.activate_campaign("cmp-1", activated_at="2026-04-01T00:00:00Z")
        self.assertEqual(activated.status, "active")

        service.link_lead(
            CampaignLeadLink(
                campaign_lead_link_id="cll-1",
                tenant_id="tenant-1",
                campaign_id="cmp-1",
                lead_id="lead-1",
                membership_status="included",
                linked_at="2026-04-01T00:05:00Z",
            )
        )

        service.link_contact(
            CampaignContactLink(
                campaign_contact_link_id="ccl-1",
                tenant_id="tenant-1",
                campaign_id="cmp-1",
                contact_id="contact-1",
                membership_status="included",
                linked_at="2026-04-01T00:06:00Z",
            )
        )

        completed = service.complete_campaign("cmp-1", completed_at="2026-06-30T23:59:59Z")
        self.assertEqual(completed.status, "completed")

    def test_segment_rejects_invalid_entity_field(self) -> None:
        service = CampaignService()
        with self.assertRaises(SegmentValidationError):
            service.create_segment(
                SegmentDefinition(
                    segment_id="seg-2",
                    tenant_id="tenant-1",
                    name="Bad segment",
                    description="Wrong field for contact",
                    entity_type="contact",
                    rules=(SegmentRule(field="company_name", operator="eq", value="Acme"),),
                    created_at="2026-03-26T00:00:00Z",
                    updated_at="2026-03-26T00:00:00Z",
                )
            )

    def test_campaign_workflow_catalog_events_exist(self) -> None:
        assert_campaign_workflow_events_are_catalog_backed()


if __name__ == "__main__":
    unittest.main()
