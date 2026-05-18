"""Territory management entities aligned with domain and security model constraints."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Literal

SubjectType = Literal["user", "team", "account", "lead"]
OwnerType = Literal["user", "team"]


@dataclass(frozen=True)
class Territory:
    territory_id: str
    tenant_id: str
    name: str
    code: str
    parent_territory_id: str | None
    level: int
    status: Literal["active", "inactive"] = "active"

    def patch(self, **changes: Any) -> "Territory":
        return replace(self, **changes)


@dataclass(frozen=True)
class TerritoryRule:
    rule_id: str
    tenant_id: str
    territory_id: str
    subject_type: SubjectType
    priority: int
    criteria: dict[str, str]
    owner_type: OwnerType
    owner_id: str


@dataclass(frozen=True)
class TerritoryAssignment:
    assignment_id: str
    tenant_id: str
    subject_type: SubjectType
    subject_id: str
    territory_id: str
    owner_type: OwnerType
    owner_id: str
    assignment_rule: str
    assigned_at: str


@dataclass(frozen=True)
class PrincipalContext:
    user_id: str
    tenant_id: str
    role: str
    permissions: frozenset[str]
    team_ids: frozenset[str] = frozenset()


class TerritoryError(ValueError):
    """Base domain error for territory management."""


class TerritoryNotFoundError(KeyError):
    """Raised when a territory cannot be found."""


class SecurityBoundaryError(PermissionError):
    """Raised when tenant/scope restrictions are violated."""


class AmbiguousOwnershipError(TerritoryError):
    """Raised when assignment rules create non-deterministic ownership."""
