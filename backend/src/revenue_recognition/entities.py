"""Revenue recognition entities for deterministic schedule and deferred/earned reporting."""

from __future__ import annotations

from dataclasses import dataclass

ALLOWED_REVENUE_TYPES: tuple[str, ...] = ("one_time", "recurring")
ALLOWED_BILLING_EVENT_TYPES: tuple[str, ...] = (
    "invoice_posted",
    "payment_settled",
    "payment_refunded",
    "chargeback",
)


@dataclass(frozen=True)
class RecognitionRule:
    rule_id: str
    tenant_id: str
    contract_id: str
    revenue_type: str
    amount: float
    currency: str
    service_period_start: str
    service_period_end: str
    recognized_at: str | None = None


@dataclass(frozen=True)
class BillingEvent:
    event_id: str
    tenant_id: str
    contract_id: str
    event_type: str
    amount: float
    currency: str
    occurred_at: str


@dataclass(frozen=True)
class RevenueScheduleLine:
    line_id: str
    tenant_id: str
    contract_id: str
    rule_id: str
    recognition_date: str
    amount: float
    currency: str
    revenue_type: str
    trace_event_ids: tuple[str, ...]


@dataclass(frozen=True)
class RevenueSchedule:
    tenant_id: str
    contract_id: str
    currency: str
    lines: tuple[RevenueScheduleLine, ...]
    total_scheduled_amount: float


@dataclass(frozen=True)
class RevenuePosition:
    tenant_id: str
    contract_id: str
    currency: str
    as_of: str
    billed_amount: float
    collected_amount: float
    earned_amount: float
    deferred_amount: float
    scheduled_through_as_of: float


@dataclass(frozen=True)
class RecognitionReportInput:
    tenant_id: str
    contract_id: str
    currency: str
    as_of: str
    daily_earned: tuple[tuple[str, float], ...]
    daily_billed: tuple[tuple[str, float], ...]
    daily_collected: tuple[tuple[str, float], ...]
    cumulative_earned: float
    deferred_ending_balance: float


class RevenueRecognitionValidationError(ValueError):
    """Raised when revenue recognition input violates deterministic policy checks."""
