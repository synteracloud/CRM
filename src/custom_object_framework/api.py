"""API wrappers for custom-object field and validation services."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import FieldConflictError, FieldDefinition, FieldValidationError, ObjectNotFoundError, RuleConflictError, ValidationRule
from .services import FieldBuilderService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "create_object": {"method": "POST", "path": "/api/v1/custom-objects"},
    "create_field": {"method": "POST", "path": "/api/v1/custom-objects/{objectKey}/fields"},
    "create_rule": {"method": "POST", "path": "/api/v1/custom-objects/{objectKey}/rules"},
    "validate_record": {"method": "POST", "path": "/api/v1/custom-objects/{objectKey}/records/validate"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


class FieldBuilderApi:
    def __init__(self, service: FieldBuilderService) -> None:
        self._service = service

    def create_object(self, object_key: str, request_id: str) -> dict[str, Any]:
        try:
            self._service.create_object(object_key)
            return success({"object_key": object_key}, request_id)
        except FieldValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def create_field(self, definition: FieldDefinition, request_id: str) -> dict[str, Any]:
        try:
            created = self._service.create_field(definition)
            return success(asdict(created), request_id)
        except ObjectNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except FieldConflictError as exc:
            return error("conflict", str(exc), request_id)
        except FieldValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def create_rule(self, rule: ValidationRule, request_id: str) -> dict[str, Any]:
        try:
            created = self._service.create_rule(rule)
            return success(asdict(created), request_id)
        except ObjectNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except RuleConflictError as exc:
            return error("conflict", str(exc), request_id)
        except FieldValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def validate_record(self, object_key: str, payload: dict[str, Any], request_id: str) -> dict[str, Any]:
        try:
            violations = self._service.validate_record(object_key=object_key, payload=payload)
            response = {
                "valid": not any(v.severity == "error" for v in violations),
                "violations": [asdict(v) for v in violations],
            }
            return success(response, request_id)
        except ObjectNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except FieldValidationError as exc:
            return error("validation_error", str(exc), request_id)
