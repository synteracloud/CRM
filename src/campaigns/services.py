"""Campaign services including CRUD, activation, and audience linking."""

from __future__ import annotations

from dataclasses import asdict

from .entities import (
    Campaign,
    CampaignContactLink,
    CampaignLeadLink,
    CampaignNotFoundError,
    CampaignStateError,
    SegmentDefinition,
    SegmentNotFoundError,
    SegmentValidationError,
)
from .segmentation import SegmentEvaluator


class CampaignService:
    def __init__(self) -> None:
        self._campaigns: dict[str, Campaign] = {}
        self._segments: dict[str, SegmentDefinition] = {}
        self._campaign_leads: dict[str, CampaignLeadLink] = {}
        self._campaign_contacts: dict[str, CampaignContactLink] = {}
        self._segment_evaluator = SegmentEvaluator()

    def list_campaigns(self) -> list[Campaign]:
        return list(self._campaigns.values())

    def create_campaign(self, campaign: Campaign) -> Campaign:
        if campaign.status != "draft":
            raise CampaignStateError("Campaign must be created in draft status.")
        if campaign.campaign_id in self._campaigns:
            raise CampaignStateError(f"Campaign already exists: {campaign.campaign_id}")
        if campaign.segment_id not in self._segments:
            raise SegmentNotFoundError(f"Segment not found: {campaign.segment_id}")
        self._campaigns[campaign.campaign_id] = campaign
        return campaign

    def get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            raise CampaignNotFoundError(f"Campaign not found: {campaign_id}")
        return campaign

    def update_campaign(self, campaign_id: str, **changes: object) -> Campaign:
        campaign = self.get_campaign(campaign_id)
        immutable_fields = {"campaign_id", "tenant_id", "created_at", "activated_at", "completed_at"}
        if immutable_fields.intersection(changes.keys()):
            raise CampaignStateError("Cannot update immutable campaign fields.")
        if "status" in changes:
            raise CampaignStateError("Use activate_campaign/complete_campaign for lifecycle transitions.")
        updated = campaign.patch(**changes)
        self._campaigns[campaign_id] = updated
        return updated

    def delete_campaign(self, campaign_id: str) -> None:
        self.get_campaign(campaign_id)
        del self._campaigns[campaign_id]

    def activate_campaign(self, campaign_id: str, activated_at: str) -> Campaign:
        campaign = self.get_campaign(campaign_id)
        if campaign.status != "draft":
            raise CampaignStateError(f"Only draft campaigns can be activated. current={campaign.status}")
        updated = campaign.patch(status="active", activated_at=activated_at)
        self._campaigns[campaign_id] = updated
        return updated

    def complete_campaign(self, campaign_id: str, completed_at: str) -> Campaign:
        campaign = self.get_campaign(campaign_id)
        if campaign.status != "active":
            raise CampaignStateError(f"Only active campaigns can be completed. current={campaign.status}")
        updated = campaign.patch(status="completed", completed_at=completed_at)
        self._campaigns[campaign_id] = updated
        return updated

    def list_segments(self) -> list[SegmentDefinition]:
        return list(self._segments.values())

    def create_segment(self, segment: SegmentDefinition) -> SegmentDefinition:
        self._segment_evaluator.validate(segment)
        if segment.segment_id in self._segments:
            raise SegmentValidationError(f"Segment already exists: {segment.segment_id}")
        self._segments[segment.segment_id] = segment
        return segment

    def get_segment(self, segment_id: str) -> SegmentDefinition:
        segment = self._segments.get(segment_id)
        if not segment:
            raise SegmentNotFoundError(f"Segment not found: {segment_id}")
        return segment

    def update_segment(self, segment_id: str, **changes: object) -> SegmentDefinition:
        segment = self.get_segment(segment_id)
        immutable_fields = {"segment_id", "tenant_id", "created_at"}
        if immutable_fields.intersection(changes.keys()):
            raise SegmentValidationError("Cannot update immutable segment fields.")

        updated = SegmentDefinition(**{**asdict(segment), **changes})
        self._segment_evaluator.validate(updated)
        self._segments[segment_id] = updated
        return updated

    def delete_segment(self, segment_id: str) -> None:
        self.get_segment(segment_id)
        del self._segments[segment_id]

    def link_lead(self, link: CampaignLeadLink) -> CampaignLeadLink:
        self.get_campaign(link.campaign_id)
        key = f"{link.campaign_id}:{link.lead_id}"
        if key in self._campaign_leads:
            raise CampaignStateError(f"Lead already linked to campaign. key={key}")
        self._campaign_leads[key] = link
        return link

    def link_contact(self, link: CampaignContactLink) -> CampaignContactLink:
        self.get_campaign(link.campaign_id)
        key = f"{link.campaign_id}:{link.contact_id}"
        if key in self._campaign_contacts:
            raise CampaignStateError(f"Contact already linked to campaign. key={key}")
        self._campaign_contacts[key] = link
        return link
