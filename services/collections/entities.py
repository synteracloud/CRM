"""Collections engine entities for invoice, payment, reminder, and reconciliation lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any, Literal

InvoiceState = Literal["unpaid", "partial", "paid", "overdue"]
PaymentProvider = Literal["jazzcash", "easypaisa", "bank_transfer"]
PaymentStatus = Literal["initiated", "succeeded", "failed", "reversed", "chargeback"]
MatchStatus = Literal["auto_matched", "needs_review", "resolved"]
MismatchReason = Literal["amount_diff", "missing_ref", "duplicate", "currency_diff", "late_settlement", "unknown"]
DeliveryStatus = Literal["queued", "sent", "delivered", "failed", "read"]


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    invoice_number: str
    customer_id: str
    issue_date: str
    due_date: str
    currency: str
    total_amount: float
    amount_paid: float = 0.0
    amount_outstanding: float = 0.0
    state: InvoiceState = "unpaid"
    overdue_days: int = 0
    reminder_policy_id: str = "default"
    escalation_level: int = 0
    metadata: dict[str, str] = field(default_factory=dict)

    def with_updates(self, **changes: Any) -> "Invoice":
        return replace(self, **changes)


@dataclass(frozen=True)
class Payment:
    payment_id: str
    provider: PaymentProvider
    provider_txn_id: str
    invoice_ref: str | None
    customer_ref: str
    amount: float
    currency: str
    status: PaymentStatus
    received_at: str
    settled_at: str | None
    raw_payload: dict[str, Any]


@dataclass(frozen=True)
class ReminderEvent:
    reminder_event_id: str
    invoice_id: str
    scheduled_at: str
    sent_at: str | None
    channel: Literal["whatsapp"]
    template_id: str
    attempt_no: int
    delivery_status: DeliveryStatus


@dataclass(frozen=True)
class ReconciliationCase:
    case_id: str
    payment_id: str
    invoice_id: str | None
    match_status: MatchStatus
    mismatch_reason: MismatchReason
    resolver_user_id: str | None
    resolution_action: str | None
    resolved_at: str | None


@dataclass(frozen=True)
class ReviewReport:
    lifecycle_steps: dict[str, bool]
    missing_flows: list[str]
    alignment_percent: int
    score: str


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
