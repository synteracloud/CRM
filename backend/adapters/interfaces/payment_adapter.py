"""Canonical PaymentAdapter contracts consumed by country-agnostic services."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from .types import AdapterContext


class PaymentStatus(str, Enum):
    INITIATED = "initiated"
    REQUIRES_ACTION = "requires_action"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass(frozen=True)
class PaymentCreateInput:
    idempotency_key: str
    order_id: str
    customer_id: str
    amount_minor: int
    currency: str
    callback_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PaymentCaptureInput:
    payment_ref: str
    amount_minor: int | None = None
    reason: str | None = None


@dataclass(frozen=True)
class PaymentRefundInput:
    payment_ref: str
    refund_ref: str
    amount_minor: int
    reason: str


@dataclass(frozen=True)
class PaymentStatusInput:
    payment_ref: str


@dataclass(frozen=True)
class PaymentCreateResult:
    payment_ref: str
    status: PaymentStatus
    provider_txn_id: str | None = None
    next_action_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PaymentCaptureResult:
    payment_ref: str
    status: PaymentStatus
    provider_txn_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PaymentRefundResult:
    payment_ref: str
    status: PaymentStatus
    provider_txn_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PaymentStatusResult:
    payment_ref: str
    status: PaymentStatus
    last_updated_at: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RawWebhookInput:
    headers: dict[str, str]
    body: dict[str, Any]


@dataclass(frozen=True)
class PaymentWebhookEvent:
    event_id: str
    event_type: str
    payment_ref: str
    status: PaymentStatus
    occurred_at: str
    raw: dict[str, Any] = field(default_factory=dict)


class PaymentAdapter(Protocol):
    def create_payment(self, input: PaymentCreateInput, ctx: AdapterContext) -> PaymentCreateResult: ...

    def capture_payment(self, input: PaymentCaptureInput, ctx: AdapterContext) -> PaymentCaptureResult: ...

    def refund_payment(self, input: PaymentRefundInput, ctx: AdapterContext) -> PaymentRefundResult: ...

    def get_payment_status(self, input: PaymentStatusInput, ctx: AdapterContext) -> PaymentStatusResult: ...

    def parse_webhook(self, input: RawWebhookInput, ctx: AdapterContext) -> PaymentWebhookEvent: ...
