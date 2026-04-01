"""Lead capture entities for WhatsApp-driven lifecycle automation."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any


class LeadStage(str, Enum):
    NEW = "New"
    QUALIFIED = "Qualified"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"


ACTIVE_STAGES: set[LeadStage] = {LeadStage.NEW, LeadStage.QUALIFIED, LeadStage.NEGOTIATION}


@dataclass(frozen=True)
class PipelineConfig:
    pipeline_id: str
    tenant_id: str
    name: str
    stages: tuple[LeadStage, ...]


@dataclass(frozen=True)
class Lead:
    lead_id: str
    tenant_id: str
    contact_id: str
    normalized_phone: str
    pipeline_id: str
    stage: LeadStage
    owner_user_id: str
    source: str
    created_at: str
    updated_at: str
    merged_from_lead_ids: tuple[str, ...] = ()

    def patch(self, **changes: Any) -> "Lead":
        return replace(self, **changes)


@dataclass(frozen=True)
class LeadActivity:
    activity_id: str
    tenant_id: str
    lead_id: str
    contact_id: str
    conversation_id: str
    message_id: str
    event_type: str
    event_time: str
    direction: str
    details: dict[str, Any] = field(default_factory=dict)
