"""Rule engine API contracts and adapters."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import RuleDefinition, RuleNotFoundError, RuleValidationError
from .services import RuleEngineService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_rules": {"method": "GET", "path": "/api/v1/rules"},
    "create_rule": {"method": "POST", "path": "/api/v1/rules"},
    "get_rule": {"method": "GET", "path": "/api/v1/rules/{rule_id}"},
    "deactivate_rule": {"method": "POST", "path": "/api/v1/rules/{rule_id}/deactivations"},
    "evaluate_rules": {"method": "POST", "path": "/api/v1/rules/evaluations"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


class RuleEngineApi:
    def __init__(self, service: RuleEngineService) -> None:
        self._service = service

    def list_rules(self, request_id: str, trigger_event: str | None = None) -> dict[str, Any]:
        rules = [asdict(item) for item in self._service.list_rules(trigger_event=trigger_event)]
        return success(rules, request_id)

    def create_rule(self, definition: RuleDefinition, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.register_rule(definition)), request_id)
        except RuleValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def get_rule(self, rule_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.get_rule(rule_id)), request_id)
        except RuleNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def deactivate_rule(self, rule_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.deactivate_rule(rule_id)), request_id)
        except RuleNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def evaluate_rules(self, trigger_event: str, tenant_id: str, context: dict[str, Any], request_id: str) -> dict[str, Any]:
        result = self._service.evaluate(trigger_event=trigger_event, tenant_id=tenant_id, context=context)
        return success(asdict(result), request_id)
