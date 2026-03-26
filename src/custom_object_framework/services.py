"""Services for dynamic layout config validation + UI schema projection."""

from __future__ import annotations

from dataclasses import asdict

from .entities import (
    DynamicFieldDefinition,
    FieldPlacementRule,
    LayoutConfig,
    LayoutValidationError,
    SUPPORTED_DYNAMIC_FIELD_TYPES,
)


DEFAULT_FIELD_PLACEMENT_RULES: tuple[FieldPlacementRule, ...] = (
    FieldPlacementRule(field_type="long_text", allowed_section_kinds=("body",)),
    FieldPlacementRule(field_type="json", allowed_section_kinds=("body",)),
    FieldPlacementRule(field_type="lookup", allowed_section_kinds=("body", "sidebar")),
    FieldPlacementRule(field_type="multi_enum", allowed_section_kinds=("body", "sidebar")),
)


class LayoutBuilderService:
    """Builds data-driven UI schema from dynamic fields + layout metadata."""

    def __init__(self, placement_rules: tuple[FieldPlacementRule, ...] = DEFAULT_FIELD_PLACEMENT_RULES) -> None:
        self._rules_by_type = {rule.field_type: rule for rule in placement_rules}

    def build_ui_schema(self, fields: list[DynamicFieldDefinition], layout: LayoutConfig) -> dict[str, object]:
        self._validate_field_types(fields)

        active_fields = {field.field_key: field for field in fields if field.lifecycle_state == "active"}
        if not active_fields:
            raise LayoutValidationError("Layout cannot be created without active fields.")

        placed_field_keys: list[str] = []
        sections_schema: list[dict[str, object]] = []
        for section in layout.sections:
            section_fields: list[dict[str, object]] = []
            for field_key in section.field_keys:
                field = active_fields.get(field_key)
                if field is None:
                    raise LayoutValidationError(
                        f"Layout references unknown or inactive field_key={field_key} in section={section.section_key}."
                    )
                self._validate_placement(section.kind, field)
                placed_field_keys.append(field_key)
                section_fields.append(
                    {
                        "field_key": field.field_key,
                        "label": field.label,
                        "type": field.type,
                        "required": field.required,
                        "component": self._component_for(field.type),
                    }
                )
            sections_schema.append(
                {
                    "section_key": section.section_key,
                    "label": section.label,
                    "kind": section.kind,
                    "fields": section_fields,
                }
            )

        self._validate_no_duplicate_placements(placed_field_keys)
        self._validate_no_orphan_fields(active_fields, placed_field_keys)

        return {
            "object_key": layout.object_key,
            "layout_version": layout.version,
            "sections": sections_schema,
            "field_count": len(active_fields),
        }

    @staticmethod
    def _validate_field_types(fields: list[DynamicFieldDefinition]) -> None:
        unsupported = sorted({field.type for field in fields if field.type not in SUPPORTED_DYNAMIC_FIELD_TYPES})
        if unsupported:
            raise LayoutValidationError(f"Unsupported dynamic field types: {unsupported}")

    def _validate_placement(self, section_kind: str, field: DynamicFieldDefinition) -> None:
        rule = self._rules_by_type.get(field.type)
        if rule and section_kind not in rule.allowed_section_kinds:
            raise LayoutValidationError(
                "Invalid placement for field "
                f"{field.field_key} (type={field.type}) in section kind={section_kind}; "
                f"allowed={rule.allowed_section_kinds}"
            )

    @staticmethod
    def _validate_no_duplicate_placements(placed_field_keys: list[str]) -> None:
        duplicates = sorted({key for key in placed_field_keys if placed_field_keys.count(key) > 1})
        if duplicates:
            raise LayoutValidationError(f"Duplicate field placement is not allowed: {duplicates}")

    @staticmethod
    def _validate_no_orphan_fields(
        active_fields: dict[str, DynamicFieldDefinition], placed_field_keys: list[str]
    ) -> None:
        placed = set(placed_field_keys)
        missing = sorted(set(active_fields) - placed)
        if missing:
            raise LayoutValidationError(f"Orphan active fields must be placed in the layout: {missing}")

    @staticmethod
    def _component_for(field_type: str) -> str:
        components = {
            "text": "TextInput",
            "long_text": "TextArea",
            "number": "NumberInput",
            "decimal": "DecimalInput",
            "boolean": "Checkbox",
            "date": "DatePicker",
            "datetime": "DateTimePicker",
            "json": "JsonEditor",
            "enum": "Select",
            "multi_enum": "MultiSelect",
            "lookup": "LookupPicker",
        }
        return components[field_type]


def serialize_layout_input(fields: list[DynamicFieldDefinition], layout: LayoutConfig) -> dict[str, object]:
    """Helper for logs/audits to emit deterministic metadata snapshot."""

    return {
        "fields": [asdict(field) for field in fields],
        "layout": {
            "object_key": layout.object_key,
            "version": layout.version,
            "sections": [asdict(section) for section in layout.sections],
        },
    }
