"""API contracts for custom object metadata CRUD operations."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import (
    CustomFieldDefinition,
    CustomObjectConflictError,
    CustomObjectDefinition,
    CustomObjectNotFoundError,
    CustomObjectValidationError,
)
from .services import CustomObjectService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "create_custom_object": {"method": "POST", "path": "/api/v1/custom-objects"},
    "update_custom_object": {"method": "PATCH", "path": "/api/v1/custom-objects/{object_key}"},
    "delete_custom_object": {"method": "DELETE", "path": "/api/v1/custom-objects/{object_key}"},
    "create_custom_field": {"method": "POST", "path": "/api/v1/custom-objects/{object_key}/fields"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class CustomObjectApi:
    def __init__(self, service: CustomObjectService) -> None:
        self._service = service

    def create_custom_object(self, definition: CustomObjectDefinition, request_id: str) -> dict[str, Any]:
        try:
            created = self._service.create_object(definition)
            registration = self._service.get_registration(definition.tenant_id, definition.object_key)
            return success({"object": asdict(created), "registration": asdict(registration)}, request_id)
        except CustomObjectConflictError as exc:
            return error("conflict", str(exc), request_id)
        except CustomObjectValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def update_custom_object(
        self,
        tenant_id: str,
        object_key: str,
        changes: dict[str, object],
        request_id: str,
    ) -> dict[str, Any]:
        try:
            updated = self._service.update_object(tenant_id, object_key, **changes)
            registration = self._service.get_registration(tenant_id, object_key)
            return success({"object": asdict(updated), "registration": asdict(registration)}, request_id)
        except CustomObjectNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except CustomObjectValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def delete_custom_object(self, tenant_id: str, object_key: str, request_id: str) -> dict[str, Any]:
        try:
            self._service.delete_object(tenant_id, object_key)
            return success({"deleted": True}, request_id)
        except CustomObjectNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def create_custom_field(
        self,
        tenant_id: str,
        object_key: str,
        field_definition: CustomFieldDefinition,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            registration = self._service.register_field(tenant_id, object_key, field_definition)
            return success(asdict(registration), request_id)
        except CustomObjectNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except CustomObjectConflictError as exc:
            return error("conflict", str(exc), request_id)
        except CustomObjectValidationError as exc:
            return error("validation_error", str(exc), request_id)
