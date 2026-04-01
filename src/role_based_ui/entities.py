"""Role-based UI configuration entities.

Implements backend-driven UI visibility contracts aligned to docs/security-model.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

VisibilityMode = Literal["all", "any"]
AdaptationState = Literal["expanded", "condensed", "essential"]
NavigationMode = Literal["bottom_nav", "top_bar_with_rail", "left_sidebar"]
DensityMode = Literal["comfortable", "compact"]
ElementPriority = Literal["P0", "P1", "P2", "P3"]


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


@dataclass(frozen=True)
class ResponsiveElement:
    """Single layout element with a responsive priority classification."""

    element_id: str
    priority: ElementPriority


@dataclass(frozen=True)
class ResponsiveLayout:
    """Resolved responsive contract for a requested viewport."""

    viewport_width: int
    breakpoint_label: str
    adaptation_state: AdaptationState
    columns: int
    navigation_mode: NavigationMode
    density_mode: DensityMode
    visible_priorities: tuple[ElementPriority, ...]
    collapsible_priorities: tuple[ElementPriority, ...]
    sticky_top_bar: bool
    sticky_bottom_actions: bool
    layout_guards: tuple[str, ...]


@dataclass(frozen=True)
class ResponsiveQcScore:
    """Self-QC scoring for responsive/mobile guarantees."""

    workflow_usability: int
    layout_integrity: int
    priority_preservation: int
