"""Contract lifecycle entities aligned to docs/domain-model.md conventions."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


CONTRACT_STATUS_SEQUENCE: tuple[str, ...] = (
    "draft",
    "review",
    "approved",
    "active",
    "renewal_pending",
    "terminated",
)


@dataclass(frozen=True)
class ContractTerm:
    """Versioned snapshot of commercial and legal terms for a contract."""

    term_id: str
    version: int
    effective_from: str
    effective_to: str
    billing_frequency: str
    auto_renew: bool
    notice_period_days: int
    renewal_term_months: int
    payment_terms: str
    termination_for_convenience: bool


@dataclass(frozen=True)
class Contract:
    """Canonical Contract entity with lifecycle, terms, and downstream linkages."""

    contract_id: str
    tenant_id: str
    account_id: str
    order_id: str | None
    subscription_id: str | None
    invoice_summary_id: str | None
    owner_user_id: str
    contract_number: str
    title: str
    status: str
    currency: str
    total_contract_value: float
    term_start_at: str
    term_end_at: str
    renewal_alert_days: int
    next_renewal_at: str
    approved_at: str | None = None
    activated_at: str | None = None
    terminated_at: str | None = None
    termination_reason: str | None = None
    terms: tuple[ContractTerm, ...] = ()

    def patch(self, **changes: Any) -> "Contract":
        return replace(self, **changes)


class ContractNotFoundError(KeyError):
    """Raised when a contract cannot be found for a contract_id."""


class ContractStateError(ValueError):
    """Raised when a lifecycle transition or linkage/term update is invalid."""
