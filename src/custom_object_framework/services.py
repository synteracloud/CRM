"""Services for runtime custom object field definitions and validation."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from .entities import (
    ALLOWED_FIELD_TYPES,
    ALLOWED_INDEX_HINTS,
    SYSTEM_FIELD_KEYS,
    FieldConflictError,
    FieldDefinition,
    FieldValidationError,
    ObjectNotFoundError,
    RuleConflictError,
    ValidationRule,
    ValidationViolation,
)


class FieldBuilderService:
    """In-memory field system matching docs/custom-object-framework.md section 2/3/8."""

    def __init__(self) -> None:
        self._objects: set[str] = set()
        self._fields_by_object: dict[str, dict[str, FieldDefinition]] = {}
        self._rules_by_object: dict[str, dict[str, ValidationRule]] = {}

    def create_object(self, object_key: str) -> None:
        if not object_key.strip():
            raise FieldValidationError("object_key is required")
        self._objects.add(object_key)
        self._fields_by_object.setdefault(object_key, {})
        self._rules_by_object.setdefault(object_key, {})

    def create_field(self, definition: FieldDefinition) -> FieldDefinition:
        self._assert_object_exists(definition.object_key)
        self._validate_field_definition(definition)

        object_fields = self._fields_by_object[definition.object_key]
        if definition.field_key in object_fields:
            raise FieldConflictError(f"Field already exists: {definition.object_key}.{definition.field_key}")

        object_fields[definition.field_key] = definition
        return definition

    def create_rule(self, rule: ValidationRule) -> ValidationRule:
        self._assert_object_exists(rule.object_key)
        if rule.rule_id in self._rules_by_object[rule.object_key]:
            raise RuleConflictError(f"Rule already exists: {rule.rule_id}")
        if rule.severity not in {"error", "warning"}:
            raise FieldValidationError("severity must be one of: error, warning")
        if rule.status not in {"active", "inactive"}:
            raise FieldValidationError("status must be one of: active, inactive")

        known_fields = set(self._fields_by_object[rule.object_key])
        unknown_targets = set(rule.target_field_keys).difference(known_fields)
        if unknown_targets:
            raise FieldValidationError(f"rule targets unknown fields: {sorted(unknown_targets)}")

        op = rule.expression.get("op")
        if op not in {"regex", "range", "required_if"}:
            raise FieldValidationError("expression.op must be one of: regex, range, required_if")

        self._rules_by_object[rule.object_key][rule.rule_id] = rule
        return rule

    def validate_record(self, object_key: str, payload: dict[str, Any]) -> list[ValidationViolation]:
        self._assert_object_exists(object_key)
        fields = self._fields_by_object[object_key]
        violations: list[ValidationViolation] = []

        unknown_fields = set(payload).difference(fields)
        if unknown_fields:
            raise FieldValidationError(f"unknown fields in payload: {sorted(unknown_fields)}")

        for key, definition in fields.items():
            value = payload.get(key, definition.default_value)
            if definition.required and value is None:
                violations.append(
                    ValidationViolation(
                        error_code="required_field_missing",
                        error_message=f"{key} is required",
                        severity="error",
                        target_field_keys=(key,),
                    )
                )
                continue
            if value is None:
                continue
            typed = self._coerce_type(definition, value)
            self._validate_field_constraints(definition, typed)

        for rule in self._rules_by_object[object_key].values():
            if rule.status != "active":
                continue
            violation = self._evaluate_rule(rule, payload)
            if violation is not None:
                violations.append(violation)

        return violations

    def _assert_object_exists(self, object_key: str) -> None:
        if object_key not in self._objects:
            raise ObjectNotFoundError(f"Object is not registered: {object_key}")

    def _validate_field_definition(self, definition: FieldDefinition) -> None:
        if definition.type not in ALLOWED_FIELD_TYPES:
            raise FieldValidationError(
                f"Invalid field type '{definition.type}'. allowed={ALLOWED_FIELD_TYPES}"
            )
        if definition.index_hint not in ALLOWED_INDEX_HINTS:
            raise FieldValidationError(
                f"Invalid index_hint '{definition.index_hint}'. allowed={ALLOWED_INDEX_HINTS}"
            )
        if definition.field_key in SYSTEM_FIELD_KEYS:
            raise FieldConflictError(f"Field key collides with system field: {definition.field_key}")

        if definition.type in {"enum", "multi_enum"} and not definition.enum_values:
            raise FieldValidationError("enum and multi_enum fields require enum_values")
        if definition.type not in {"enum", "multi_enum"} and definition.enum_values:
            raise FieldValidationError("enum_values is only allowed for enum and multi_enum fields")

        if definition.type == "decimal":
            if definition.precision is None or definition.scale is None:
                raise FieldValidationError("decimal fields require precision and scale")
            if definition.scale < 0 or definition.precision < 1 or definition.scale > definition.precision:
                raise FieldValidationError("decimal precision/scale is invalid")

    def _coerce_type(self, definition: FieldDefinition, value: Any) -> Any:
        field_type = definition.type
        if field_type in {"text", "long_text", "enum", "lookup"}:
            if not isinstance(value, str):
                raise FieldValidationError(f"{definition.field_key} must be a string")
            return value
        if field_type == "number":
            if not isinstance(value, int) or isinstance(value, bool):
                raise FieldValidationError(f"{definition.field_key} must be an integer")
            return value
        if field_type == "decimal":
            try:
                return Decimal(str(value))
            except (InvalidOperation, ValueError) as exc:
                raise FieldValidationError(f"{definition.field_key} must be a decimal") from exc
        if field_type == "boolean":
            if not isinstance(value, bool):
                raise FieldValidationError(f"{definition.field_key} must be a boolean")
            return value
        if field_type == "date":
            if isinstance(value, date) and not isinstance(value, datetime):
                return value
            try:
                return date.fromisoformat(str(value))
            except ValueError as exc:
                raise FieldValidationError(f"{definition.field_key} must be an ISO date") from exc
        if field_type == "datetime":
            if isinstance(value, datetime):
                return value
            try:
                return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            except ValueError as exc:
                raise FieldValidationError(f"{definition.field_key} must be an ISO datetime") from exc
        if field_type == "json":
            if not isinstance(value, (dict, list)):
                raise FieldValidationError(f"{definition.field_key} must be JSON-like")
            return value
        if field_type == "multi_enum":
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise FieldValidationError(f"{definition.field_key} must be a list[str]")
            return value
        raise FieldValidationError(f"Unsupported type: {field_type}")

    def _validate_field_constraints(self, definition: FieldDefinition, value: Any) -> None:
        if definition.max_length is not None and isinstance(value, str) and len(value) > definition.max_length:
            raise FieldValidationError(f"{definition.field_key} exceeds max_length={definition.max_length}")

        if definition.type == "decimal" and definition.precision is not None and definition.scale is not None:
            numeric = Decimal(value)
            sign, digits, exponent = numeric.as_tuple()
            total_digits = len(digits)
            scale = max(0, -exponent)
            if total_digits > definition.precision or scale > definition.scale:
                raise FieldValidationError(
                    f"{definition.field_key} exceeds decimal precision={definition.precision}, scale={definition.scale}"
                )

        if definition.type == "enum" and value not in definition.enum_values:
            raise FieldValidationError(f"{definition.field_key} must be one of {definition.enum_values}")

        if definition.type == "multi_enum":
            invalid = [item for item in value if item not in definition.enum_values]
            if invalid:
                raise FieldValidationError(
                    f"{definition.field_key} includes invalid options {invalid}; allowed={definition.enum_values}"
                )

    def _evaluate_rule(self, rule: ValidationRule, payload: dict[str, Any]) -> ValidationViolation | None:
        op = rule.expression["op"]
        if op == "regex":
            import re

            field_key = rule.expression["field"]
            pattern = rule.expression["pattern"]
            value = payload.get(field_key)
            if value is not None and re.match(pattern, str(value)) is None:
                return ValidationViolation(
                    error_code=rule.error_code,
                    error_message=rule.error_message,
                    severity=rule.severity,
                    target_field_keys=rule.target_field_keys,
                )
            return None

        if op == "range":
            field_key = rule.expression["field"]
            value = payload.get(field_key)
            if value is None:
                return None
            minimum = rule.expression.get("min")
            maximum = rule.expression.get("max")
            if minimum is not None and value < minimum:
                return ValidationViolation(rule.error_code, rule.error_message, rule.severity, rule.target_field_keys)
            if maximum is not None and value > maximum:
                return ValidationViolation(rule.error_code, rule.error_message, rule.severity, rule.target_field_keys)
            return None

        if op == "required_if":
            condition = rule.expression["if"]
            if payload.get(condition["field"]) == condition["eq"]:
                required_field = rule.expression["then_required"]
                if payload.get(required_field) in {None, ""}:
                    return ValidationViolation(
                        error_code=rule.error_code,
                        error_message=rule.error_message,
                        severity=rule.severity,
                        target_field_keys=rule.target_field_keys,
                    )
            return None

        return None
