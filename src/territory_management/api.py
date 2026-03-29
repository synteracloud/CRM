"""API contracts for territory model and assignment endpoints."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import (
    AmbiguousOwnershipError,
    PrincipalContext,
    SecurityBoundaryError,
    Territory,
    TerritoryError,
    TerritoryNotFoundError,
    TerritoryRule,
)
from .services import TerritoryManagementService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "create_territory": {"method": "POST", "path": "/api/v1/territories"},
    "list_territories": {"method": "GET", "path": "/api/v1/territories"},
    "create_rule": {"method": "POST", "path": "/api/v1/territories/rules"},
    "assign_subject": {"method": "POST", "path": "/api/v1/territories/assignments"},
    "get_assignment": {"method": "GET", "path": "/api/v1/territories/assignments/{subject_type}/{subject_id}"},
    "get_coverage": {"method": "GET", "path": "/api/v1/territories/{territory_id}/coverage"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": []},
        "meta": {"request_id": request_id},
    }


class TerritoryManagementApi:
    def __init__(self, service: TerritoryManagementService) -> None:
        self._service = service

    def create_territory(self, territory: Territory, request_id: str) -> dict[str, Any]:
        try:
            created = self._service.create_territory(territory)
            return success(asdict(created), request_id)
        except (TerritoryError, TerritoryNotFoundError, SecurityBoundaryError) as exc:
            return error("validation_error", str(exc), request_id)

    def list_territories(self, tenant_id: str, request_id: str) -> dict[str, Any]:
        return success([asdict(t) for t in self._service.list_territories(tenant_id)], request_id)

    def create_rule(self, rule: TerritoryRule, request_id: str) -> dict[str, Any]:
        try:
            created = self._service.register_rule(rule)
            return success(asdict(created), request_id)
        except AmbiguousOwnershipError as exc:
            return error("conflict", str(exc), request_id)
        except (TerritoryError, TerritoryNotFoundError, SecurityBoundaryError) as exc:
            return error("validation_error", str(exc), request_id)

    def assign_subject(
        self,
        *,
        principal: PrincipalContext,
        subject_type: str,
        subject_id: str,
        subject_facts: dict[str, str],
        assigned_at: str,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            assignment = self._service.assign_subject(
                principal=principal,
                subject_type=subject_type,
                subject_id=subject_id,
                subject_facts=subject_facts,
                assigned_at=assigned_at,
            )
            return success(asdict(assignment), request_id)
        except TerritoryNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except SecurityBoundaryError as exc:
            return error("forbidden", str(exc), request_id)
        except TerritoryError as exc:
            return error("validation_error", str(exc), request_id)

    def get_assignment(
        self,
        *,
        principal: PrincipalContext,
        subject_type: str,
        subject_id: str,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            assignment = self._service.get_assignment(
                principal=principal,
                subject_type=subject_type,
                subject_id=subject_id,
            )
            return success(asdict(assignment), request_id)
        except TerritoryNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except SecurityBoundaryError as exc:
            return error("forbidden", str(exc), request_id)

    def get_coverage(self, *, principal: PrincipalContext, territory_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(self._service.get_coverage(principal=principal, territory_id=territory_id), request_id)
        except TerritoryNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except SecurityBoundaryError as exc:
            return error("forbidden", str(exc), request_id)
