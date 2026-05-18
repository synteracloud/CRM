"""API contracts for rules-based lead and opportunity scoring."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import LeadScoringInput, OpportunityScoringInput, ScoringValidationError
from .services import ScoringService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "score_lead": {"method": "POST", "path": "/api/v1/lead-scores"},
    "score_opportunity": {"method": "POST", "path": "/api/v1/opportunity-scores"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class ScoringApi:
    def __init__(self, service: ScoringService) -> None:
        self._service = service

    def score_lead(self, scoring_input: LeadScoringInput, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.score_lead(scoring_input)), request_id)
        except ScoringValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def score_opportunity(self, scoring_input: OpportunityScoringInput, request_id: str) -> dict[str, Any]:
        try:
            return success(asdict(self._service.score_opportunity(scoring_input)), request_id)
        except ScoringValidationError as exc:
            return error("validation_error", str(exc), request_id)
