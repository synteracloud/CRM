"""Design system entities for token + component contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

TokenCategory = Literal["foundation", "semantic", "domain_alias"]


class DesignSystemValidationError(ValueError):
    """Raised when a design-system definition violates contract rules."""


@dataclass(frozen=True)
class DesignToken:
    token_id: str
    category: TokenCategory
    value: str
    description: str


@dataclass(frozen=True)
class ComponentContract:
    component_id: str
    primitive_family: str
    required_states: tuple[str, ...]
    optional_states: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DesignSystemSnapshot:
    version: str
    token_count: int
    component_count: int
    tokens: tuple[DesignToken, ...]
    components: tuple[ComponentContract, ...]
    alias_map: dict[str, str]
