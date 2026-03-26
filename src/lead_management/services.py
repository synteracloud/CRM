"""Services for lead handling and lifecycle transitions."""

from __future__ import annotations

from dataclasses import asdict
from typing import Callable

from .entities import Lead, LeadNotFoundError, LeadStateError
from .events import LeadEvent

EventSink = Callable[[LeadEvent], None]


class LeadService:
    """In-memory lead service implementing CRUD + status transitions."""

    def __init__(self, event_sink: EventSink | None = None) -> None:
        self._store: dict[str, Lead] = {}
        self._event_sink = event_sink or (lambda _: None)

    def list_leads(self) -> list[Lead]:
        return list(self._store.values())

    def create_lead(self, lead: Lead) -> Lead:
        if lead.lead_id in self._store:
            raise LeadStateError(f"Lead already exists: {lead.lead_id}")
        self._store[lead.lead_id] = lead
        self._emit("lead_created", lead, {"status": lead.status})
        return lead

    def get_lead(self, lead_id: str) -> Lead:
        lead = self._store.get(lead_id)
        if not lead:
            raise LeadNotFoundError(f"Lead not found: {lead_id}")
        return lead

    def update_lead(self, lead_id: str, **changes: object) -> Lead:
        lead = self.get_lead(lead_id)
        immutable_fields = {"lead_id", "tenant_id", "created_at"}
        if immutable_fields.intersection(changes.keys()):
            raise LeadStateError("Cannot update immutable lead fields.")
        updated = lead.patch(**changes)
        self._store[lead_id] = updated
        return updated

    def delete_lead(self, lead_id: str) -> None:
        self.get_lead(lead_id)
        del self._store[lead_id]

    def qualify_lead(self, lead_id: str, qualified_at: str) -> Lead:
        lead = self.get_lead(lead_id)
        if lead.status not in {"new", "open"}:
            raise LeadStateError(f"Only new/open leads can be qualified. current={lead.status}")
        qualified = lead.patch(status="qualified")
        self._store[lead_id] = qualified
        self._emit("lead_qualified", qualified, {"qualified_at": qualified_at, "status": "qualified"})
        return qualified

    def convert_lead(
        self,
        lead_id: str,
        converted_at: str,
        account_id: str,
        contact_id: str,
        opportunity_id: str | None = None,
    ) -> Lead:
        lead = self.get_lead(lead_id)
        if lead.status != "qualified":
            raise LeadStateError(f"Only qualified leads can be converted. current={lead.status}")

        converted = lead.patch(status="converted", converted_at=converted_at)
        self._store[lead_id] = converted
        self._emit(
            "lead_converted",
            converted,
            {
                "converted_at": converted_at,
                "account_id": account_id,
                "contact_id": contact_id,
                "opportunity_id": opportunity_id,
            },
        )
        return converted

    def _emit(self, name: str, lead: Lead, payload: dict[str, object]) -> None:
        event = LeadEvent(
            name=name,
            tenant_id=lead.tenant_id,
            lead_id=lead.lead_id,
            payload={**asdict(lead), **payload},
        )
        self._event_sink(event)
