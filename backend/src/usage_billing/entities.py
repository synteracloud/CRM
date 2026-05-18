"""Usage billing entities for metering, rating, and invoice input generation."""

from __future__ import annotations

from dataclasses import dataclass, field


TRACKED_BILLABLE_EVENT_NAMES: tuple[str, ...] = (
    "communication.message.sent.v1",
    "communication.message.engagement.updated.v1",
    "workflow.execution.completed.v1",
    "notification.dispatched.v1",
    "search.document.upserted.v1",
    "job.succeeded.v1",
)


@dataclass(frozen=True)
class TrackedEvent:
    """Canonical tracked event entering usage metering."""

    event_id: str
    tenant_id: str
    event_name: str
    occurred_at: str
    payload: dict[str, object]


@dataclass(frozen=True)
class BillableEventRule:
    """Rule mapping tracked events into a billable usage meter."""

    meter_code: str
    event_name: str
    quantity_field: str | None = None
    default_quantity: int = 1


@dataclass(frozen=True)
class UsageRecord:
    """Normalized billable usage row that can be aggregated and rated."""

    usage_record_id: str
    tenant_id: str
    subscription_id: str
    account_id: str
    meter_code: str
    quantity: int
    unit: str
    occurred_at: str
    source_event_id: str
    source_event_name: str
    dedupe_key: str


@dataclass(frozen=True)
class TierPrice:
    """Price tier for volume rating logic."""

    up_to: int | None
    unit_price: float


@dataclass(frozen=True)
class MeterRateCard:
    """Rate card for a specific meter code."""

    meter_code: str
    unit: str
    currency: str
    billing_model: str
    unit_price: float | None = None
    tiers: tuple[TierPrice, ...] = ()


@dataclass(frozen=True)
class UsageAggregate:
    """Aggregated usage within one invoice period and meter."""

    tenant_id: str
    subscription_id: str
    account_id: str
    meter_code: str
    unit: str
    period_start: str
    period_end: str
    total_quantity: int
    source_usage_record_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RatedUsageLine:
    """Rated usage line used to build invoice input."""

    tenant_id: str
    subscription_id: str
    account_id: str
    meter_code: str
    quantity: int
    unit: str
    currency: str
    subtotal: float
    period_start: str
    period_end: str
    rate_breakdown: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class InvoiceInput:
    """Invoice payload produced from usage rating output."""

    tenant_id: str
    subscription_id: str
    account_id: str
    currency: str
    billing_period_start: str
    billing_period_end: str
    usage_subtotal: float
    line_items: tuple[RatedUsageLine, ...]
