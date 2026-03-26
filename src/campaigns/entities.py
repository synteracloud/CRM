"""Campaign and segmentation entities aligned to docs/domain-model.md."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Literal


CAMPAIGN_FIELDS: tuple[str, ...] = (
    "campaign_id",
    "tenant_id",
    "owner_user_id",
    "name",
    "description",
    "status",
    "segment_id",
    "starts_at",
    "ends_at",
    "created_at",
    "updated_at",
    "activated_at",
    "completed_at",
)

SEGMENT_FIELDS: tuple[str, ...] = (
    "segment_id",
    "tenant_id",
    "name",
    "description",
    "entity_type",
    "rules",
    "created_at",
    "updated_at",
)

CAMPAIGN_LEAD_LINK_FIELDS: tuple[str, ...] = (
    "campaign_lead_link_id",
    "tenant_id",
    "campaign_id",
    "lead_id",
    "membership_status",
    "linked_at",
)

CAMPAIGN_CONTACT_LINK_FIELDS: tuple[str, ...] = (
    "campaign_contact_link_id",
    "tenant_id",
    "campaign_id",
    "contact_id",
    "membership_status",
    "linked_at",
)

CampaignStatus = Literal["draft", "active", "completed"]
SegmentEntityType = Literal["lead", "contact"]


@dataclass(frozen=True)
class SegmentRule:
    """A single rules-based clause for a segment."""

    field: str
    operator: str
    value: str | int | float | bool


@dataclass(frozen=True)
class SegmentDefinition:
    """Rules-based segment definition over leads or contacts."""

    segment_id: str
    tenant_id: str
    name: str
    description: str
    entity_type: SegmentEntityType
    rules: tuple[SegmentRule, ...]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class Campaign:
    """Campaign lifecycle entity: draft -> active -> completed."""

    campaign_id: str
    tenant_id: str
    owner_user_id: str
    name: str
    description: str
    status: CampaignStatus
    segment_id: str
    starts_at: str
    ends_at: str
    created_at: str
    updated_at: str
    activated_at: str | None = None
    completed_at: str | None = None

    def patch(self, **changes: Any) -> "Campaign":
        return replace(self, **changes)


@dataclass(frozen=True)
class CampaignLeadLink:
    """Membership link between campaign and lead."""

    campaign_lead_link_id: str
    tenant_id: str
    campaign_id: str
    lead_id: str
    membership_status: str
    linked_at: str


@dataclass(frozen=True)
class CampaignContactLink:
    """Membership link between campaign and contact."""

    campaign_contact_link_id: str
    tenant_id: str
    campaign_id: str
    contact_id: str
    membership_status: str
    linked_at: str


class CampaignNotFoundError(KeyError):
    """Raised when a campaign does not exist."""


class SegmentNotFoundError(KeyError):
    """Raised when a segment does not exist."""


class CampaignStateError(ValueError):
    """Raised when campaign lifecycle transition is invalid."""


class SegmentValidationError(ValueError):
    """Raised when a segment definition or rule is invalid."""
