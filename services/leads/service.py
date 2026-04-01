"""WhatsApp lead capture service with auto pipeline + owner assignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from .entities import ACTIVE_STAGES, Lead, LeadActivity, LeadStage

if TYPE_CHECKING:
    from services.messaging.entities import MessageRecord
from .pipelines import default_pipeline_for_tenant
from .repository import LeadsRepository


@dataclass(frozen=True)
class LeadCaptureResult:
    lead: Lead
    created: bool
    merged: bool


class OwnerAssigner:
    """Tenant-scoped deterministic owner assignment with round-robin fallback."""

    def __init__(self, default_owner_id: str = "system-owner") -> None:
        self._default_owner_id = default_owner_id
        self._owners_by_tenant: dict[str, tuple[str, ...]] = {}
        self._cursor_by_tenant: dict[str, int] = {}

    def configure(self, tenant_id: str, owners: tuple[str, ...]) -> None:
        self._owners_by_tenant[tenant_id] = owners
        self._cursor_by_tenant.setdefault(tenant_id, 0)

    def assign(self, tenant_id: str) -> str:
        owners = self._owners_by_tenant.get(tenant_id, ())
        if not owners:
            return self._default_owner_id
        idx = self._cursor_by_tenant.get(tenant_id, 0)
        owner = owners[idx % len(owners)]
        self._cursor_by_tenant[tenant_id] = (idx + 1) % len(owners)
        return owner


class WhatsAppLeadCaptureService:
    def __init__(self, repository: LeadsRepository, assigner: OwnerAssigner | None = None) -> None:
        self._repository = repository
        self._assigner = assigner or OwnerAssigner()

    def configure_owner_pool(self, tenant_id: str, owners: tuple[str, ...]) -> None:
        self._assigner.configure(tenant_id, owners)

    def capture_inbound_message(
        self,
        *,
        tenant_id: str,
        contact_id: str,
        normalized_phone: str,
        conversation_id: str,
        message: "MessageRecord",
        classified_intent: str,
    ) -> LeadCaptureResult:
        lead = self._repository.get_active_by_phone(tenant_id, normalized_phone)
        created = False
        merged = False

        if lead is None:
            lead = self._create_lead(
                tenant_id=tenant_id,
                contact_id=contact_id,
                normalized_phone=normalized_phone,
                created_at=message.timestamp,
            )
            created = True
        elif lead.contact_id != contact_id:
            lead = lead.patch(
                updated_at=message.timestamp,
                merged_from_lead_ids=tuple(sorted(set(lead.merged_from_lead_ids + (lead.lead_id,)))),
                contact_id=contact_id,
            )
            self._repository.save_lead(lead)
            merged = True

        staged = self._progress_stage(lead, classified_intent, message.timestamp)
        self._repository.save_lead(staged)

        self._repository.add_activity(
            LeadActivity(
                activity_id=str(uuid4()),
                tenant_id=tenant_id,
                lead_id=staged.lead_id,
                contact_id=contact_id,
                conversation_id=conversation_id,
                message_id=message.message_id,
                event_type="conversation_message_attached",
                event_time=message.timestamp,
                direction=getattr(message.direction, "value", str(message.direction)),
                details={"intent": classified_intent, "text": message.text},
            )
        )

        return LeadCaptureResult(lead=staged, created=created, merged=merged)

    def _create_lead(
        self,
        *,
        tenant_id: str,
        contact_id: str,
        normalized_phone: str,
        created_at: str,
    ) -> Lead:
        pipeline = self._repository.get_pipeline(tenant_id) or self._repository.save_pipeline(default_pipeline_for_tenant(tenant_id))
        return self._repository.save_lead(
            Lead(
                lead_id=str(uuid4()),
                tenant_id=tenant_id,
                contact_id=contact_id,
                normalized_phone=normalized_phone,
                pipeline_id=pipeline.pipeline_id,
                stage=LeadStage.NEW,
                owner_user_id=self._assigner.assign(tenant_id),
                source="whatsapp_inbound",
                created_at=created_at,
                updated_at=created_at,
            )
        )

    @staticmethod
    def _progress_stage(lead: Lead, intent: str, at: str) -> Lead:
        if lead.stage not in ACTIVE_STAGES:
            return lead.patch(updated_at=at)

        next_stage = lead.stage
        if intent in {"QUALIFICATION", "INBOUND_USER_MESSAGE"} and lead.stage == LeadStage.NEW:
            next_stage = LeadStage.QUALIFIED
        elif intent == "NEGOTIATION":
            next_stage = LeadStage.NEGOTIATION
        elif intent == "PURCHASE_CONFIRMED":
            next_stage = LeadStage.WON
        elif intent == "LOST_SIGNAL":
            next_stage = LeadStage.LOST

        return lead.patch(stage=next_stage, updated_at=at)
