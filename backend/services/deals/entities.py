"""Deal and revenue tracking entities for execution-tied pipeline control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DealState = Literal["open", "won", "lost"]
RevenueLinkStatus = Literal["linked", "broken", "missing_payment", "missing_invoice"]


@dataclass(frozen=True)
class LeadContext:
    lead_id: str
    account_id: str
    owner_id: str


@dataclass(frozen=True)
class Deal:
    deal_id: str
    lead_id: str
    title: str
    stage: str
    state: DealState
    expected_value: float
    weighted_value: float
    currency: str = "USD"


@dataclass(frozen=True)
class InvoiceLink:
    invoice_id: str
    deal_id: str
    amount: float
    currency: str


@dataclass(frozen=True)
class PaymentLink:
    payment_id: str
    invoice_id: str
    amount: float
    currency: str
    status: Literal["initiated", "succeeded", "failed"]


@dataclass(frozen=True)
class RevenueIssue:
    code: str
    deal_id: str
    detail: str


@dataclass(frozen=True)
class RevenueAlignmentReport:
    checks: dict[str, bool]
    inconsistencies: list[RevenueIssue]
    alignment_percent: int
    score: str
