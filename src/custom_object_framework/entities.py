"""Entities for metadata-driven custom object layout configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


SUPPORTED_DYNAMIC_FIELD_TYPES: tuple[str, ...] = (
    "text",
    "long_text",
    "number",
    "decimal",
    "boolean",
    "date",
    "datetime",
    "json",
    "enum",
    "multi_enum",
    "lookup",
)


@dataclass(frozen=True)
class DynamicFieldDefinition:
    """Dynamic field metadata subset required by the layout builder."""

    field_key: str
    label: str
    type: str
    required: bool = False
    lifecycle_state: str = "active"


@dataclass(frozen=True)
class LayoutSection:
    """A UI section containing ordered field placements."""

    section_key: str
    label: str
    kind: str
    field_keys: tuple[str, ...]


@dataclass(frozen=True)
class LayoutConfig:
    """Tenant/object-specific layout metadata."""

    object_key: str
    version: int
    sections: tuple[LayoutSection, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FieldPlacementRule:
    """Restricts where a field type may appear inside a layout."""

    field_type: str
    allowed_section_kinds: tuple[str, ...]


class LayoutValidationError(ValueError):
    """Raised when a layout configuration violates field validation guarantees."""
