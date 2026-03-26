"""API interface for CRM AI Copilot suggestions."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import CopilotContext, CopilotValidationError
from .services import CopilotService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "get_suggestions": {"method": "POST", "path": "/api/v1/copilot/suggestions"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class CopilotApi:
    def __init__(self, service: CopilotService) -> None:
        self._service = service

    def get_suggestions(self, context: CopilotContext, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.suggest(context)), request_id)
        except CopilotValidationError as exc:
            return error("validation_error", str(exc), request_id)
