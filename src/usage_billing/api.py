"""API contracts for usage metering and rating processing."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import (
    BillableEventRule,
    MeterRateCard,
    RatedUsageLine,
    TrackedEvent,
    UsageAggregate,
    UsageRecord,
)
from .services import UsageBillingError, UsageBillingService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "collect_usage": {"method": "POST", "path": "/api/v1/usage-collections"},
    "aggregate_usage": {"method": "POST", "path": "/api/v1/usage-aggregations"},
    "rate_usage": {"method": "POST", "path": "/api/v1/usage-ratings"},
    "generate_invoice_input": {"method": "POST", "path": "/api/v1/usage/invoice-inputs"},
    "usage_processing_rules": {"method": "GET", "path": "/api/v1/usage/processing-rules"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


class UsageBillingApi:
    """Thin API facade around usage billing service pipeline."""

    def __init__(self, service: UsageBillingService) -> None:
        self._service = service

    def collect_usage(
        self,
        tracked_events: list[TrackedEvent],
        rules: list[BillableEventRule],
        request_id: str,
    ) -> dict[str, Any]:
        try:
            records = self._service.collect_billable_events(tracked_events, rules)
            return success([asdict(record) for record in records], request_id)
        except UsageBillingError as exc:
            return error("validation_error", str(exc), request_id)

    def aggregate_usage(
        self,
        usage_records: list[UsageRecord],
        period_start: str,
        period_end: str,
        request_id: str,
    ) -> dict[str, Any]:
        aggregates = self._service.aggregate_usage(usage_records, period_start, period_end)
        return success([asdict(item) for item in aggregates], request_id)

    def rate_usage(
        self,
        usage_aggregates: list[UsageAggregate],
        rate_cards: list[MeterRateCard],
        request_id: str,
    ) -> dict[str, Any]:
        try:
            rated = self._service.rate_usage(usage_aggregates, rate_cards)
            return success([asdict(line) for line in rated], request_id)
        except UsageBillingError as exc:
            return error("validation_error", str(exc), request_id)

    def generate_invoice_input(self, rated_usage_lines: list[RatedUsageLine], request_id: str) -> dict[str, Any]:
        invoices = self._service.generate_invoice_inputs(rated_usage_lines)
        return success([asdict(invoice) for invoice in invoices], request_id)

    def usage_processing_rules(self, request_id: str) -> dict[str, Any]:
        return success(self._service.processing_rules(), request_id)
