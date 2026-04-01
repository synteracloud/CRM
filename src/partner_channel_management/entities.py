"""Partner/channel entities and invariants for attribution sidecar workflows."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


PARTNER_FIELDS: tuple[str, ...] = (
    "partner_id",
    "tenant_id",
    "partner_code",
    "name",
    "partner_type",
    "status",
    "owner_user_id",
)


@dataclass(frozen=True)
class Partner:
    partner_id: str
    tenant_id: str
    partner_code: str
    name: str
    partner_type: str
    status: str
    owner_user_id: str


@dataclass(frozen=True)
class PartnerRelationship:
    partner_relationship_id: str
    tenant_id: str
    partner_id: str
    account_id: str | None
    opportunity_id: str | None
    relationship_type: str
    source_channel: str
    status: str


@dataclass(frozen=True)
class OpportunityRecord:
    """Minimal opportunity snapshot owned by direct sales owner."""

    opportunity_id: str
    tenant_id: str
    account_id: str
    owner_user_id: str
    stage: str

    def patch(self, **changes: Any) -> "OpportunityRecord":
        return replace(self, **changes)


@dataclass(frozen=True)
class PartnerAttribution:
    partner_attribution_id: str
    tenant_id: str
    partner_id: str
    opportunity_id: str
    account_id: str
    attribution_type: str
    attribution_model: str
    attribution_weight: float
    attribution_status: str
    locked_at: str | None = None

    def patch(self, **changes: Any) -> "PartnerAttribution":
        return replace(self, **changes)


@dataclass(frozen=True)
class DealRegistration:
    deal_registration_id: str
    tenant_id: str
    partner_id: str
    account_id: str
    opportunity_id: str
    registered_at: str
    window_end_at: str


class PartnerChannelError(ValueError):
    """Raised when partner/channel invariants are violated."""


class PartnerChannelNotFoundError(KeyError):
    """Raised when a required partner/channel record is missing."""
