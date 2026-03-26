"""Custom object entities aligned to docs/custom-object-framework.md."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

SYSTEM_FIELD_KEYS: tuple[str, ...] = (
    "id",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
    "tenant_id",
)

SUPPORTED_FIELD_TYPES: tuple[str, ...] = (
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

ALLOWED_MODULE_SCOPES: tuple[str, ...] = (
    "sales",
    "support",
    "marketing",
    "service",
    "platform",
    "operations",
)

ALLOWED_OWNERSHIP_MODELS: tuple[str, ...] = (
    "user_owned",
    "team_owned",
    "org_owned",
)

ALLOWED_LIFECYCLE_STATES: tuple[str, ...] = (
    "draft",
    "active",
    "deprecated",
    "archived",
)


@dataclass(frozen=True)
class CustomFieldDefinition:
    """Metadata for a dynamic field on a custom object."""

    field_key: str
    label: str
    field_type: str
    required: bool = False
    default_value: Any = None
    index_hint: str = "none"
    is_searchable: bool = False
    is_filterable: bool = True
    is_sortable: bool = False


@dataclass(frozen=True)
class CustomObjectDefinition:
    """Top-level metadata for a tenant-scoped custom object."""

    tenant_id: str
    object_key: str
    display_name: str
    module_scope: str
    ownership_model: str
    lifecycle_state: str
    description: str = ""
    dynamic_fields: tuple[CustomFieldDefinition, ...] = field(default_factory=tuple)

    def patch(self, **changes: Any) -> "CustomObjectDefinition":
        return replace(self, **changes)


@dataclass(frozen=True)
class ObjectRegistration:
    """Published descriptor used by runtime metadata registry/cache."""

    tenant_id: str
    object_key: str
    route_path: str
    event_namespace: str
    module_scope: str
    lifecycle_state: str
    schema: dict[str, dict[str, Any]]


class CustomObjectConflictError(ValueError):
    """Raised when object metadata collides with a reserved/core artifact."""


class CustomObjectNotFoundError(KeyError):
    """Raised when a custom object cannot be found for a tenant."""


class CustomObjectValidationError(ValueError):
    """Raised when object or field metadata fails deterministic validation."""
