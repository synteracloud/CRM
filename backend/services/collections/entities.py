"""Collections engine entities for invoice, payment, reminder, and reconciliation lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Literal

InvoiceState = Literal["unpaid", "partial", "paid", "overdue"]
# cash = physical cash; manual = bank transfer / cheque / informal entry recorded by agent
PaymentProvider = Literal["jazzcash", "easypaisa", "bank_transfer", "cash", "manual"]
PaymentStatus = Literal["initiated", "succeeded", "failed", "reversed", "chargeback"]
# pending_verification applies to cash/manual payments awaiting proof review
VerificationStatus = Literal["not_required", "pending_verification", "verified", "rejected"]
MatchStatus = Literal["auto_matched", "needs_review", "resolved"]
MismatchReason = Literal["amount_diff", "missing_ref", "duplicate", "currency_diff", "late_settlement", "unknown"]
DeliveryStatus = Literal["queued", "sent", "delivered", "failed", "read"]
# Tone tier controls culturally appropriate escalation in reminder messages
ToneTier = Literal["polite", "firm", "urgent"]


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
    tenant_id: str = ""
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
    # Manual/cash payment proof fields (None for digital adapter payments)
    entered_by: str | None = None          # user_id who manually entered the payment
    proof_url: str | None = None           # signed URL to uploaded screenshot/receipt
    proof_note: str | None = None          # free-text note from agent
    verification_status: VerificationStatus = "not_required"
    verified_by: str | None = None         # user_id who verified the proof
    verified_at: str | None = None


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
    tone_tier: ToneTier = "polite"    # polite (pre-due) / firm (1-7d overdue) / urgent (8d+)
    locale: str = "en"                # "en" or "ur" (Urdu)


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
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z"
