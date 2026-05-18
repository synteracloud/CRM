"""API contract wrappers for predictive forecasting engine."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import ForecastValidationError
from .services import ForecastEngineService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "build_forecast": {"method": "POST", "path": "/api/v1/forecast-builds"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


class ForecastEngineApi:
    def __init__(self, service: ForecastEngineService) -> None:
        self._service = service

    def build_forecast(
        self,
        *,
        tenant_id: str,
        as_of: str,
        opportunities: list[Any],
        request_id: str,
    ) -> dict[str, Any]:
        try:
            result = self._service.build_forecast(tenant_id=tenant_id, as_of=as_of, opportunities=opportunities)
            return success(asdict(result), request_id)
        except ForecastValidationError as exc:
            return error("validation_error", str(exc), request_id)
