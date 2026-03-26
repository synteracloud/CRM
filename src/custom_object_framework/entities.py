"""Entities for dynamic custom-object fields and validation rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

FieldType = Literal[
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
]

IndexHint = Literal["none", "standard", "unique"]
RuleSeverity = Literal["error", "warning"]
RuleStatus = Literal["active", "inactive"]

ALLOWED_FIELD_TYPES: tuple[str, ...] = (
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

ALLOWED_INDEX_HINTS: tuple[str, ...] = ("none", "standard", "unique")
SYSTEM_FIELD_KEYS: frozenset[str] = frozenset(
    {"id", "created_at", "updated_at", "created_by", "updated_by", "tenant_id"}
)


@dataclass(frozen=True)
class FieldDefinition:
    object_key: str
    field_key: str
    label: str
    type: FieldType
    required: bool = False
    default_value: Any | None = None
    index_hint: IndexHint = "none"
    is_searchable: bool = False
    is_filterable: bool = False
    is_sortable: bool = False
    max_length: int | None = None
    precision: int | None = None
    scale: int | None = None
    enum_values: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ValidationRule:
    rule_id: str
    object_key: str
    target_field_keys: tuple[str, ...]
    expression: dict[str, Any]
    error_code: str
    error_message: str
    severity: RuleSeverity = "error"
    status: RuleStatus = "active"


@dataclass(frozen=True)
class ValidationViolation:
    error_code: str
    error_message: str
    severity: RuleSeverity
    target_field_keys: tuple[str, ...]


class FieldValidationError(ValueError):
    """Raised when field configuration or data fails validation."""


class FieldConflictError(ValueError):
    """Raised when a field conflicts with existing schema artifacts."""


class RuleConflictError(ValueError):
    """Raised when a validation rule conflicts with metadata constraints."""


class ObjectNotFoundError(KeyError):
    """Raised when a custom object key is not registered."""
