"""Role-based UI configuration entities.

Implements backend-driven UI visibility contracts aligned to docs/security-model.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

VisibilityMode = Literal["all", "any"]


class UiConfigValidationError(ValueError):
    """Raised when a UI configuration contract is invalid."""


@dataclass(frozen=True)
class UiSectionRule:
    """Visibility rule for a single UI section."""

    section_id: str
    title: str
    route: str
    required_permissions: tuple[str, ...] = field(default_factory=tuple)
    allowed_roles: tuple[str, ...] = field(default_factory=tuple)
    visibility_mode: VisibilityMode = "all"


@dataclass(frozen=True)
class UiConfig:
    """Resolved UI payload returned to clients."""

    tenant_id: str
    principal_id: str
    role_ids: tuple[str, ...]
    permissions: tuple[str, ...]
    visible_sections: tuple[UiSectionRule, ...]
    hidden_section_ids: tuple[str, ...]
    policy_version: str
