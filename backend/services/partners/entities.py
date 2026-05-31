"""Partner domain entities: tier rules, state machines, commission rates.

Domain spec: backend/docs/domain/partners.md §1, §2, §3, §4
"""
from __future__ import annotations

from enum import Enum
from typing import Optional


class PartnerTier(str, Enum):
    PLATINUM = "platinum"
    GOLD     = "gold"
    SILVER   = "silver"


class PartnerStatus(str, Enum):
    ACTIVE    = "active"
    INACTIVE  = "inactive"
    SUSPENDED = "suspended"


class DealRegStatus(str, Enum):
    SUBMITTED = "submitted"
    APPROVED  = "approved"
    REJECTED  = "rejected"
    LINKED    = "linked"
    EXPIRED   = "expired"


class CommissionStatus(str, Enum):
    PENDING   = "pending"
    APPROVED  = "approved"
    PAID      = "paid"
    DISPUTED  = "disputed"
    CANCELLED = "cancelled"


# Commission rates per tier — spec §1.2
COMMISSION_RATES: dict[str, float] = {
    PartnerTier.PLATINUM: 0.15,
    PartnerTier.GOLD:     0.10,
    PartnerTier.SILVER:   0.05,
}

# Deal registration expiry days per tier — spec §2.2
DEAL_REG_EXPIRY_DAYS: dict[str, Optional[int]] = {
    PartnerTier.PLATINUM: 30,
    PartnerTier.GOLD:     45,
    PartnerTier.SILVER:   None,   # No expiry for Silver
}

# PartnerStatus transitions — spec §3.1
PARTNER_STATUS_TRANSITIONS: dict[str, list[str]] = {
    "active":    ["inactive", "suspended"],
    "inactive":  ["active"],
    "suspended": ["active", "inactive"],
}

# DealRegStatus transitions — spec §3.2
DEAL_REG_TRANSITIONS: dict[str, list[str]] = {
    "submitted": ["approved", "rejected"],
    "approved":  ["linked", "expired"],
    "rejected":  [],   # terminal
    "linked":    [],   # terminal
    "expired":   [],   # terminal
}

# CommissionStatus transitions — spec §3.3
COMMISSION_TRANSITIONS: dict[str, list[str]] = {
    "pending":   ["approved", "disputed", "cancelled"],
    "approved":  ["paid"],
    "paid":      [],   # terminal + immutable
    "disputed":  ["approved", "cancelled"],
    "cancelled": [],   # terminal
}


class PartnerDomainError(ValueError):
    """Raised when a partner domain rule is violated."""


def validate_partner_status_transition(from_status: str, to_status: str) -> None:
    allowed = PARTNER_STATUS_TRANSITIONS.get(from_status, [])
    if to_status not in allowed:
        raise PartnerDomainError(
            f"Partner status transition {from_status!r} → {to_status!r} is not permitted."
        )


def validate_commission_transition(from_status: str, to_status: str) -> None:
    if from_status == CommissionStatus.PAID:
        raise PartnerDomainError(
            "Commission with status 'paid' is immutable — cannot be modified."
        )
    allowed = COMMISSION_TRANSITIONS.get(from_status, [])
    if to_status not in allowed:
        raise PartnerDomainError(
            f"Commission transition {from_status!r} → {to_status!r} is not permitted."
        )


def calculate_commission(opportunity_amount: float, partner_tier: str) -> tuple[float, float]:
    """
    Return (commission_amount, rate) for an opportunity amount and partner tier.
    Spec §4.1: commission = opportunity.amount * rate.
    """
    rate = COMMISSION_RATES.get(partner_tier, COMMISSION_RATES[PartnerTier.SILVER])
    return round(float(opportunity_amount) * rate, 2), rate


def compute_expiry_date(submitted_at_iso: str, partner_tier: str) -> Optional[str]:
    """
    Return expiry date ISO string for a deal registration, or None for Silver.
    Spec §2.2.
    """
    from datetime import datetime, timedelta, timezone
    days = DEAL_REG_EXPIRY_DAYS.get(partner_tier)
    if days is None:
        return None
    dt = datetime.fromisoformat(submitted_at_iso.replace("Z", "+00:00"))
    expiry = dt + timedelta(days=days)
    return expiry.date().isoformat()
