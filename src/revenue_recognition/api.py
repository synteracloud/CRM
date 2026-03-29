"""API contract wrapper for revenue recognition engine."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import RevenueRecognitionValidationError
from .services import RevenueRecognitionService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "build_schedules": {"method": "POST", "path": "/api/v1/revenue-recognition-schedule-builds"},
    "build_positions": {"method": "POST", "path": "/api/v1/revenue-recognition-position-builds"},
    "build_reporting_inputs": {"method": "POST", "path": "/api/v1/revenue-recognition-reporting-input-builds"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


class RevenueRecognitionApi:
    def __init__(self, service: RevenueRecognitionService) -> None:
        self._service = service

    def build_schedules(
        self,
        *,
        tenant_id: str,
        rules: list[Any],
        billing_events: list[Any],
        request_id: str,
    ) -> dict[str, Any]:
        try:
            schedules = self._service.build_schedules(tenant_id=tenant_id, rules=rules, billing_events=billing_events)
            return success([asdict(item) for item in schedules], request_id)
        except RevenueRecognitionValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def build_positions(
        self,
        *,
        tenant_id: str,
        as_of: str,
        schedules: list[Any],
        billing_events: list[Any],
        request_id: str,
    ) -> dict[str, Any]:
        try:
            positions = self._service.build_positions(
                tenant_id=tenant_id,
                as_of=as_of,
                schedules=schedules,
                billing_events=billing_events,
            )
            return success([asdict(item) for item in positions], request_id)
        except RevenueRecognitionValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def build_reporting_inputs(
        self,
        *,
        tenant_id: str,
        as_of: str,
        schedules: list[Any],
        billing_events: list[Any],
        request_id: str,
    ) -> dict[str, Any]:
        try:
            inputs = self._service.build_reporting_inputs(
                tenant_id=tenant_id,
                as_of=as_of,
                schedules=schedules,
                billing_events=billing_events,
            )
            return success([asdict(item) for item in inputs], request_id)
        except RevenueRecognitionValidationError as exc:
            return error("validation_error", str(exc), request_id)
