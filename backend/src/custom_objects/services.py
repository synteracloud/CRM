"""In-memory custom object engine with isolated tenant schemas."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import (
    ALLOWED_LIFECYCLE_STATES,
    ALLOWED_MODULE_SCOPES,
    ALLOWED_OWNERSHIP_MODELS,
    SUPPORTED_FIELD_TYPES,
    SYSTEM_FIELD_KEYS,
    CustomFieldDefinition,
    CustomObjectConflictError,
    CustomObjectDefinition,
    CustomObjectNotFoundError,
    CustomObjectValidationError,
    ObjectRegistration,
)

CORE_ENTITY_KEYS: frozenset[str] = frozenset(
    {
        "tenant",
        "tenant_entitlement",
        "user",
        "role",
        "permission",
        "user_role",
        "role_permission",
        "session_token",
        "lead",
        "lead_assignment",
        "contact",
        "account",
        "account_hierarchy",
        "opportunity",
        "opportunity_line_item",
        "quote",
        "quote_line_item",
        "order",
        "product",
        "price_book",
        "price_book_entry",
        "approval_request",
        "activity_event",
        "message_thread",
        "message",
        "case",
        "case_comment",
        "knowledge_article",
        "subscription",
        "invoice_summary",
        "payment_event",
        "workflow_definition",
        "workflow_execution",
        "notification_template",
        "notification",
        "feature_flag",
        "feature_flag_rule",
        "audit_log",
        "search_document",
    }
)

RESERVED_OBJECT_KEYS: frozenset[str] = frozenset({"api", "health", "metrics", "internal"})


class CustomObjectService:
    """Creates, updates, deletes, and registers custom objects per tenant."""

    def __init__(self) -> None:
        self._objects: dict[tuple[str, str], CustomObjectDefinition] = {}
        self._registry: dict[tuple[str, str], ObjectRegistration] = {}

    def create_object(self, definition: CustomObjectDefinition) -> CustomObjectDefinition:
        key = (definition.tenant_id, definition.object_key)
        self._validate_definition(definition)
        self._ensure_object_conflict_free(definition.tenant_id, definition.object_key)

        if key in self._objects:
            raise CustomObjectConflictError(f"custom object already exists: {definition.object_key}")

        schema = self._build_schema(definition.dynamic_fields)
        self._objects[key] = definition
        self._registry[key] = self._build_registration(definition, schema)
        return definition

    def update_object(self, tenant_id: str, object_key: str, **changes: Any) -> CustomObjectDefinition:
        current = self.get_object(tenant_id, object_key)
        immutable_fields = {"object_key", "tenant_id"}
        if immutable_fields.intersection(changes.keys()):
            raise CustomObjectValidationError("object_key and tenant_id are immutable")

        updated = current.patch(**changes)
        self._validate_definition(updated)
        self._objects[(tenant_id, object_key)] = updated
        self._registry[(tenant_id, object_key)] = self._build_registration(
            updated,
            schema=self._registry[(tenant_id, object_key)].schema,
        )
        return updated

    def delete_object(self, tenant_id: str, object_key: str) -> None:
        key = (tenant_id, object_key)
        self.get_object(tenant_id, object_key)
        del self._objects[key]
        del self._registry[key]

    def get_object(self, tenant_id: str, object_key: str) -> CustomObjectDefinition:
        key = (tenant_id, object_key)
        obj = self._objects.get(key)
        if not obj:
            raise CustomObjectNotFoundError(f"custom object not found: {object_key}")
        return obj

    def register_field(self, tenant_id: str, object_key: str, field: CustomFieldDefinition) -> ObjectRegistration:
        self._validate_field(field)
        obj = self.get_object(tenant_id, object_key)
        key = (tenant_id, object_key)
        registration = self._registry[key]

        if field.field_key in SYSTEM_FIELD_KEYS:
            raise CustomObjectConflictError(f"field conflicts with system field: {field.field_key}")
        if field.field_key in registration.schema:
            raise CustomObjectConflictError(f"field already exists: {field.field_key}")

        updated_fields = tuple([*obj.dynamic_fields, field])
        updated_obj = obj.patch(dynamic_fields=updated_fields)
        self._objects[key] = updated_obj

        updated_schema = {**registration.schema, field.field_key: asdict(field)}
        self._registry[key] = self._build_registration(updated_obj, schema=updated_schema)
        return self._registry[key]

    def get_registration(self, tenant_id: str, object_key: str) -> ObjectRegistration:
        key = (tenant_id, object_key)
        reg = self._registry.get(key)
        if not reg:
            raise CustomObjectNotFoundError(f"custom object registration not found: {object_key}")
        return reg

    def list_registered_objects(self, tenant_id: str) -> list[ObjectRegistration]:
        return [registration for (current_tenant, _), registration in self._registry.items() if current_tenant == tenant_id]

    def _validate_definition(self, definition: CustomObjectDefinition) -> None:
        if definition.module_scope not in ALLOWED_MODULE_SCOPES:
            raise CustomObjectValidationError(f"unsupported module_scope: {definition.module_scope}")
        if definition.ownership_model not in ALLOWED_OWNERSHIP_MODELS:
            raise CustomObjectValidationError(f"unsupported ownership_model: {definition.ownership_model}")
        if definition.lifecycle_state not in ALLOWED_LIFECYCLE_STATES:
            raise CustomObjectValidationError(f"unsupported lifecycle_state: {definition.lifecycle_state}")
        for field in definition.dynamic_fields:
            self._validate_field(field)

    def _validate_field(self, field: CustomFieldDefinition) -> None:
        if field.field_type not in SUPPORTED_FIELD_TYPES:
            raise CustomObjectValidationError(f"unsupported field_type: {field.field_type}")
        if field.field_key in SYSTEM_FIELD_KEYS:
            raise CustomObjectConflictError(f"field conflicts with system field: {field.field_key}")

    def _ensure_object_conflict_free(self, tenant_id: str, object_key: str) -> None:
        if object_key in RESERVED_OBJECT_KEYS:
            raise CustomObjectConflictError(f"object_key reserved: {object_key}")
        if object_key in CORE_ENTITY_KEYS:
            raise CustomObjectConflictError(f"object_key conflicts with core entity: {object_key}")

        # Deterministic route and event namespace collision checks.
        route_path = f"/api/v1/custom-objects/{object_key}"
        event_namespace = f"custom_object.{object_key}"
        for (other_tenant, _), reg in self._registry.items():
            if other_tenant != tenant_id:
                continue
            if reg.route_path == route_path:
                raise CustomObjectConflictError(f"api route collision: {route_path}")
            if reg.event_namespace == event_namespace:
                raise CustomObjectConflictError(f"event namespace collision: {event_namespace}")

    def _build_schema(self, fields: tuple[CustomFieldDefinition, ...]) -> dict[str, dict[str, Any]]:
        schema: dict[str, dict[str, Any]] = {
            field_key: {"field_key": field_key, "field_type": "system", "required": True}
            for field_key in SYSTEM_FIELD_KEYS
        }
        for field in fields:
            if field.field_key in schema:
                raise CustomObjectConflictError(f"field already exists: {field.field_key}")
            schema[field.field_key] = asdict(field)
        return schema

    def _build_registration(self, definition: CustomObjectDefinition, schema: dict[str, dict[str, Any]]) -> ObjectRegistration:
        return ObjectRegistration(
            tenant_id=definition.tenant_id,
            object_key=definition.object_key,
            route_path=f"/api/v1/custom-objects/{definition.object_key}",
            event_namespace=f"custom_object.{definition.object_key}",
            module_scope=definition.module_scope,
            lifecycle_state=definition.lifecycle_state,
            schema=schema,
        )
