"""Entities for the Admin Control Center domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

PanelCategory = Literal["workspace", "users_roles_permissions", "customization", "workflow", "config"]
VisibilityState = Literal["hidden", "read_only", "editable"]


class AdminControlValidationError(ValueError):
    """Raised when admin control center payloads are invalid."""


@dataclass(frozen=True)
class AdminPanel:
    panel_id: str
    name: str
    route: str
    category: PanelCategory
    required_permissions: tuple[str, ...] = field(default_factory=tuple)
    write_permissions: tuple[str, ...] = field(default_factory=tuple)
    critical: bool = False


@dataclass(frozen=True)
class ResolvedPanel:
    panel_id: str
    name: str
    route: str
    category: PanelCategory
    state: VisibilityState
    required_permissions: tuple[str, ...]
    write_permissions: tuple[str, ...]
    critical: bool


@dataclass(frozen=True)
class InteractionPattern:
    pattern_id: str
    title: str
    description: str
    controls: tuple[str, ...]


@dataclass(frozen=True)
class AdminControlCenter:
    tenant_id: str
    principal_id: str
    role_ids: tuple[str, ...]
    permissions: tuple[str, ...]
    structure: tuple[str, ...]
    views: tuple[ResolvedPanel, ...]
    interaction_patterns: tuple[InteractionPattern, ...]
    hidden_panel_ids: tuple[str, ...]
    policy_version: str
