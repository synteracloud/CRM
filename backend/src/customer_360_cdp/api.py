"""API contracts for Customer 360 CDP aggregation."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import (
    AccountRecord,
    ActivityRecord,
    ContactRecord,
    CustomerProfileError,
    LeadRecord,
)
from .services import Customer360Service


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "upsert_lead": {"method": "PUT", "path": "/api/v1/cdp/leads/{lead_id}"},
    "upsert_contact": {"method": "PUT", "path": "/api/v1/cdp/contacts/{contact_id}"},
    "upsert_account": {"method": "PUT", "path": "/api/v1/cdp/accounts/{account_id}"},
    "add_activity": {"method": "POST", "path": "/api/v1/cdp/activities"},
    "link_lead": {"method": "POST", "path": "/api/v1/cdp/leads/{lead_id}/links"},
    "get_profile": {"method": "GET", "path": "/api/v1/cdp/profiles/{profile_id}"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


class Customer360Api:
    def __init__(self, service: Customer360Service) -> None:
        self._service = service

    def upsert_lead(self, lead: LeadRecord, request_id: str) -> dict[str, Any]:
        return success(asdict(self._service.upsert_lead(lead)), request_id)

    def upsert_contact(self, contact: ContactRecord, request_id: str) -> dict[str, Any]:
        return success(asdict(self._service.upsert_contact(contact)), request_id)

    def upsert_account(self, account: AccountRecord, request_id: str) -> dict[str, Any]:
        return success(asdict(self._service.upsert_account(account)), request_id)

    def add_activity(self, activity: ActivityRecord, request_id: str) -> dict[str, Any]:
        return success(asdict(self._service.add_activity(activity)), request_id)

    def link_lead(
        self,
        lead_id: str,
        request_id: str,
        contact_id: str | None = None,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            self._service.link_lead(lead_id=lead_id, contact_id=contact_id, account_id=account_id)
            return success({"linked": True}, request_id)
        except CustomerProfileError as exc:
            return error("validation_error", str(exc), request_id)

    def get_profile(
        self,
        *,
        tenant_id: str,
        profile_id: str,
        request_id: str,
        lead_id: str | None = None,
        contact_id: str | None = None,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        try:
            profile = self._service.build_profile(
                tenant_id=tenant_id,
                profile_id=profile_id,
                lead_id=lead_id,
                contact_id=contact_id,
                account_id=account_id,
            )
            return success(asdict(profile), request_id)
        except CustomerProfileError as exc:
            return error("validation_error", str(exc), request_id)
