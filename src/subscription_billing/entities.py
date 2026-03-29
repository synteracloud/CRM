"""Subscription billing entities and lifecycle contracts."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Literal


SUBSCRIPTION_FIELDS: tuple[str, ...] = (
    "subscription_id",
    "tenant_id",
    "account_id",
    "quote_id",
    "external_subscription_ref",
    "plan_code",
    "status",
    "start_date",
    "end_date",
    "renewal_date",
    "created_at",
)

INVOICE_SUMMARY_FIELDS: tuple[str, ...] = (
    "invoice_summary_id",
    "tenant_id",
    "subscription_id",
    "external_invoice_ref",
    "invoice_number",
    "amount_due",
    "amount_paid",
    "currency",
    "status",
    "due_date",
    "issued_at",
)

PAYMENT_EVENT_FIELDS: tuple[str, ...] = (
    "payment_event_id",
    "tenant_id",
    "subscription_id",
    "invoice_summary_id",
    "external_payment_ref",
    "event_type",
    "amount",
    "currency",
    "event_time",
    "status",
)

SubscriptionStatus = Literal["draft", "trialing", "active", "past_due", "paused", "canceled", "expired"]
PlanChangeKind = Literal["upgrade", "downgrade"]


@dataclass(frozen=True)
class Subscription:
    subscription_id: str
    tenant_id: str
    account_id: str
    quote_id: str | None
    external_subscription_ref: str
    plan_code: str
    status: SubscriptionStatus
    start_date: str
    end_date: str
    renewal_date: str
    created_at: str

    def patch(self, **changes: Any) -> "Subscription":
        return replace(self, **changes)


@dataclass(frozen=True)
class PlanChange:
    plan_change_id: str
    tenant_id: str
    subscription_id: str
    from_plan_code: str
    to_plan_code: str
    change_kind: PlanChangeKind
    requested_at: str
    effective_at: str
    apply_on_renewal: bool


@dataclass(frozen=True)
class InvoiceSummary:
    invoice_summary_id: str
    tenant_id: str
    subscription_id: str
    external_invoice_ref: str
    invoice_number: str
    amount_due: float
    amount_paid: float
    currency: str
    status: str
    due_date: str
    issued_at: str


@dataclass(frozen=True)
class PaymentEvent:
    payment_event_id: str
    tenant_id: str
    subscription_id: str | None
    invoice_summary_id: str | None
    external_payment_ref: str
    event_type: str
    amount: float
    currency: str
    event_time: str
    status: str


@dataclass(frozen=True)
class RecurringInvoiceHook:
    hook_id: str
    tenant_id: str
    subscription_id: str
    trigger_type: Literal["activation", "renewal", "plan_change"]
    invoice_reason: Literal["initial", "recurring", "proration"]
    run_at: str
    metadata: dict[str, str]


class SubscriptionNotFoundError(KeyError):
    """Raised when a subscription does not exist."""


class SubscriptionStateError(ValueError):
    """Raised when a subscription lifecycle transition is invalid."""


class PlanChangeError(ValueError):
    """Raised when a plan change request is invalid."""
