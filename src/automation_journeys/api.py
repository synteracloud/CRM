"""API contracts for journey create/start/stop operations."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from src.event_bus import Event

from .entities import JourneyDefinition, JourneyNotFoundError, JourneyValidationError
from .services import JourneyService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "create_journey": {"method": "POST", "path": "/api/v1/journeys"},
    "start_journey": {"method": "POST", "path": "/api/v1/journeys/{journey_id}/activations"},
    "stop_journey": {"method": "POST", "path": "/api/v1/journeys/{journey_id}/deactivations"},
}


class JourneyApi:
    def __init__(self, service: JourneyService) -> None:
        self._service = service

    def create_journey(self, definition: JourneyDefinition, request_id: str) -> dict[str, Any]:
        try:
            created = self._service.create_journey(definition)
            return _success(asdict(created), request_id)
        except JourneyValidationError as exc:
            return _error("validation_error", str(exc), request_id)

    def start_journey(self, journey_id: str, event: Event, request_id: str) -> dict[str, Any]:
        try:
            started = self._service.start_journey(journey_id, event)
            return _success(asdict(started), request_id)
        except (JourneyValidationError, JourneyNotFoundError) as exc:
            return _error("conflict", str(exc), request_id)

    def stop_journey(self, journey_id: str, request_id: str) -> dict[str, Any]:
        try:
            stopped = self._service.stop_journey(journey_id)
            return _success(asdict(stopped), request_id)
        except JourneyNotFoundError as exc:
            return _error("not_found", str(exc), request_id)


def _success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def _error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}
