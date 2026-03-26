"""API contracts for predictive models."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import PredictionValidationError
from .services import PredictiveModelService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "ingest_opportunity_history": {"method": "POST", "path": "/api/v1/predictive-models/history/opportunities"},
    "ingest_subscription_history": {"method": "POST", "path": "/api/v1/predictive-models/history/subscriptions"},
    "predict_win_probability": {"method": "POST", "path": "/api/v1/predictive-models/win-probability:predict"},
    "predict_churn": {"method": "POST", "path": "/api/v1/predictive-models/churn:predict"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": []},
        "meta": {"request_id": request_id},
    }


class PredictiveModelApi:
    def __init__(self, service: PredictiveModelService) -> None:
        self._service = service

    def ingest_opportunity_history(self, rows: list[Any], request_id: str) -> dict[str, Any]:
        try:
            count = self._service.ingest_opportunity_history(rows)
            return success({"ingested": count}, request_id)
        except PredictionValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def ingest_subscription_history(self, rows: list[Any], request_id: str) -> dict[str, Any]:
        try:
            count = self._service.ingest_subscription_history(rows)
            return success({"ingested": count}, request_id)
        except PredictionValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def predict_win_probability(
        self,
        tenant_id: str,
        opportunity_id: str,
        stage: str,
        amount: float,
        forecast_category: str,
        created_at: str,
        close_date: str,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            prediction = self._service.predict_win_probability(
                tenant_id=tenant_id,
                opportunity_id=opportunity_id,
                stage=stage,
                amount=amount,
                forecast_category=forecast_category,
                created_at=created_at,
                close_date=close_date,
            )
            return success(asdict(prediction), request_id)
        except PredictionValidationError as exc:
            return error("validation_error", str(exc), request_id)

    def predict_churn(
        self,
        tenant_id: str,
        subscription_id: str,
        status: str,
        mrr: float,
        started_at: str,
        current_period_end: str,
        last_payment_at: str,
        late_payment_count: int,
        support_case_count_90d: int,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            prediction = self._service.predict_churn(
                tenant_id=tenant_id,
                subscription_id=subscription_id,
                status=status,
                mrr=mrr,
                started_at=started_at,
                current_period_end=current_period_end,
                last_payment_at=last_payment_at,
                late_payment_count=late_payment_count,
                support_case_count_90d=support_case_count_90d,
            )
            return success(asdict(prediction), request_id)
        except PredictionValidationError as exc:
            return error("validation_error", str(exc), request_id)
