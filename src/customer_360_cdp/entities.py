"""Customer 360 CDP entities aligned to docs/domain-model.md."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LeadRecord:
    lead_id: str
    tenant_id: str
    email: str
    phone: str
    company_name: str
    created_at: str


@dataclass(frozen=True)
class ContactRecord:
    contact_id: str
    tenant_id: str
    account_id: str | None
    first_name: str
    last_name: str
    email: str
    phone: str
    created_at: str


@dataclass(frozen=True)
class AccountRecord:
    account_id: str
    tenant_id: str
    name: str
    status: str
    created_at: str


@dataclass(frozen=True)
class ActivityRecord:
    activity_id: str
    tenant_id: str
    entity_type: str
    entity_id: str
    activity_type: str
    occurred_at: str


@dataclass(frozen=True)
class UnifiedIdentity:
    primary_email: str | None
    primary_phone: str | None
    all_emails: tuple[str, ...] = ()
    all_phones: tuple[str, ...] = ()


@dataclass(frozen=True)
class UnifiedCustomerProfile:
    profile_id: str
    tenant_id: str
    lead_ids: tuple[str, ...] = ()
    contact_ids: tuple[str, ...] = ()
    account_ids: tuple[str, ...] = ()
    activity_ids: tuple[str, ...] = ()
    identity: UnifiedIdentity = field(default_factory=lambda: UnifiedIdentity(None, None))


class CustomerProfileError(ValueError):
    """Base customer profile validation failure."""


class MissingRelationError(CustomerProfileError):
    """Raised when an expected cross-entity relation cannot be resolved."""


class EntityNotFoundError(CustomerProfileError):
    """Raised when a requested entity does not exist."""
