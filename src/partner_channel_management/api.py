"""API contracts for partner/channel management lifecycle."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import (
    DealRegistration,
    OpportunityRecord,
    Partner,
    PartnerAttribution,
    PartnerChannelError,
    PartnerChannelNotFoundError,
    PartnerRelationship,
)
from .services import PartnerChannelService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "create_partner": {"method": "POST", "path": "/api/v1/partners"},
    "activate_relationship": {"method": "POST", "path": "/api/v1/partners/{partner_id}/relationships"},
    "register_deal": {"method": "POST", "path": "/api/v1/partners/{partner_id}/deal-registrations"},
    "add_candidate_attribution": {
        "method": "POST",
        "path": "/api/v1/opportunities/{opportunity_id}/partner-attributions",
    },
    "lock_attribution": {
        "method": "POST",
        "path": "/api/v1/opportunities/{opportunity_id}/partner-attributions/lock",
    },
    "list_opportunity_attributions": {
        "method": "GET",
        "path": "/api/v1/opportunities/{opportunity_id}/partner-attributions",
    },
}


class PartnerChannelApi:
    def __init__(self, service: PartnerChannelService) -> None:
        self._service = service

    def create_partner(self, partner: Partner, request_id: str) -> dict[str, Any]:
        return self._wrap(lambda: asdict(self._service.create_partner(partner)), request_id)

    def register_opportunity(self, opportunity: OpportunityRecord, request_id: str) -> dict[str, Any]:
        return self._wrap(lambda: asdict(self._service.register_opportunity(opportunity)), request_id)

    def activate_relationship(self, relationship: PartnerRelationship, request_id: str) -> dict[str, Any]:
        return self._wrap(lambda: asdict(self._service.activate_relationship(relationship)), request_id)

    def register_deal(self, registration: DealRegistration, request_id: str) -> dict[str, Any]:
        return self._wrap(lambda: asdict(self._service.register_deal(registration)), request_id)

    def add_candidate_attribution(self, attribution: PartnerAttribution, request_id: str) -> dict[str, Any]:
        return self._wrap(lambda: asdict(self._service.add_candidate_attribution(attribution)), request_id)

    def lock_attribution(self, tenant_id: str, opportunity_id: str, locked_at: str, request_id: str) -> dict[str, Any]:
        return self._wrap(
            lambda: [
                asdict(row)
                for row in self._service.lock_attribution(
                    tenant_id=tenant_id,
                    opportunity_id=opportunity_id,
                    locked_at=locked_at,
                )
            ],
            request_id,
        )

    def list_opportunity_attributions(self, opportunity_id: str, request_id: str) -> dict[str, Any]:
        return self._wrap(
            lambda: [asdict(row) for row in self._service.list_opportunity_attributions(opportunity_id)], request_id
        )

    @staticmethod
    def _wrap(func: Any, request_id: str) -> dict[str, Any]:
        try:
            return {"data": func(), "meta": {"request_id": request_id}}
        except PartnerChannelNotFoundError as exc:
            return {"error": {"code": "not_found", "message": str(exc), "details": []}, "meta": {"request_id": request_id}}
        except PartnerChannelError as exc:
            return {"error": {"code": "conflict", "message": str(exc), "details": []}, "meta": {"request_id": request_id}}
