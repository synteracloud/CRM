"""Lead domain entities aligned to docs/domain-model.md."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


LEAD_FIELDS: tuple[str, ...] = (
    "lead_id",
    "tenant_id",
    "owner_user_id",
    "source",
    "status",
    "score",
    "email",
    "phone",
    "company_name",
    "created_at",
    "converted_at",
)


@dataclass(frozen=True)
class Lead:
    """Canonical Lead entity definition from the domain model."""

    lead_id: str
    tenant_id: str
    owner_user_id: str
    source: str
    status: str
    score: int
    email: str
    phone: str
    company_name: str
    created_at: str
    converted_at: str | None = None

    def patch(self, **changes: Any) -> "Lead":
        """Return an updated immutable copy of the lead."""
        return replace(self, **changes)


class LeadNotFoundError(KeyError):
    """Raised when a lead cannot be found for a given lead_id."""


class LeadStateError(ValueError):
    """Raised when a lead lifecycle transition is invalid."""
