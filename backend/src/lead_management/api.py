"""API contracts for Lead Management Service, aligned to docs/api-standards.md."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import Lead, LeadNotFoundError, LeadStateError
from .services import LeadService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_leads": {"method": "GET", "path": "/api/v1/leads"},
    "create_lead": {"method": "POST", "path": "/api/v1/leads"},
    "get_lead": {"method": "GET", "path": "/api/v1/leads/{lead_id}"},
    "update_lead": {"method": "PATCH", "path": "/api/v1/leads/{lead_id}"},
    "delete_lead": {"method": "DELETE", "path": "/api/v1/leads/{lead_id}"},
    "qualify_lead": {"method": "POST", "path": "/api/v1/leads/{lead_id}/qualifications"},
    "convert_lead": {"method": "POST", "path": "/api/v1/leads/{lead_id}/conversions"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class LeadApi:
    def __init__(self, service: LeadService) -> None:
        self._service = service

    def list_leads(self, request_id: str) -> dict[str, Any]:
        return success([asdict(lead) for lead in self._service.list_leads()], request_id)

    def create_lead(self, lead: Lead, request_id: str) -> dict[str, Any]:
        try:
            created = self._service.create_lead(lead)
            return success(asdict(created), request_id)
        except LeadStateError as exc:
            return error("conflict", str(exc), request_id)

    def get_lead(self, lead_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.get_lead(lead_id)), request_id)
        except LeadNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def update_lead(self, lead_id: str, changes: dict[str, object], request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.update_lead(lead_id, **changes)), request_id)
        except LeadNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except LeadStateError as exc:
            return error("validation_error", str(exc), request_id)

    def delete_lead(self, lead_id: str, request_id: str) -> dict[str, Any]:
        try:
            self._service.delete_lead(lead_id)
            return success({"deleted": True}, request_id)
        except LeadNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def qualify_lead(self, lead_id: str, qualified_at: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.qualify_lead(lead_id, qualified_at)), request_id)
        except LeadNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except LeadStateError as exc:
            return error("conflict", str(exc), request_id)

    def convert_lead(
        self,
        lead_id: str,
        converted_at: str,
        account_id: str,
        contact_id: str,
        opportunity_id: str | None,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            converted = self._service.convert_lead(
                lead_id=lead_id,
                converted_at=converted_at,
                account_id=account_id,
                contact_id=contact_id,
                opportunity_id=opportunity_id,
            )
            return success(asdict(converted), request_id)
        except LeadNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except LeadStateError as exc:
            return error("conflict", str(exc), request_id)
