"""Layout builder for secure, data-driven custom object UI schemas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DynamicFieldDefinition:
    field_key: str
    label: str
    type: str
    required: bool = False
    active: bool = True


@dataclass(frozen=True)
class LayoutSection:
    section_key: str
    label: str
    kind: str
    field_keys: tuple[str, ...]


@dataclass(frozen=True)
class LayoutConfig:
    object_key: str
    version: int
    sections: tuple[LayoutSection, ...]


class LayoutValidationError(ValueError):
    """Raised when a UI layout configuration is inconsistent or unsafe."""


class LayoutBuilderService:
    _COMPONENT_BY_TYPE: dict[str, str] = {
        "text": "TextInput",
        "long_text": "TextArea",
        "number": "NumberInput",
        "decimal": "DecimalInput",
        "boolean": "Toggle",
        "date": "DatePicker",
        "datetime": "DateTimePicker",
        "enum": "Select",
        "multi_enum": "MultiSelect",
        "lookup": "LookupSelect",
        "json": "JsonEditor",
    }

    _HEADER_ALLOWED_TYPES: frozenset[str] = frozenset(
        {"text", "number", "decimal", "boolean", "date", "datetime", "enum", "multi_enum"}
    )

    def build_ui_schema(self, fields: list[DynamicFieldDefinition], layout: LayoutConfig) -> dict[str, Any]:
        active_fields = {field.field_key: field for field in fields if field.active}
        referenced_field_keys = {field_key for section in layout.sections for field_key in section.field_keys}

        unknown_or_inactive = sorted(referenced_field_keys.difference(active_fields))
        if unknown_or_inactive:
            raise LayoutValidationError(f"Layout references unknown or inactive fields: {unknown_or_inactive}")

        orphan_active = sorted(set(active_fields).difference(referenced_field_keys))
        if orphan_active:
            raise LayoutValidationError(f"Orphan active fields are not placed in a section: {orphan_active}")

        sections: list[dict[str, Any]] = []
        for section in layout.sections:
            section_fields: list[dict[str, Any]] = []
            for field_key in section.field_keys:
                field = active_fields[field_key]
                self._validate_field_placement(section.kind, field)
                section_fields.append(
                    {
                        "field_key": field.field_key,
                        "label": field.label,
                        "type": field.type,
                        "required": field.required,
                        "component": self._component_for_type(field.type),
                    }
                )
            sections.append(
                {
                    "section_key": section.section_key,
                    "label": section.label,
                    "kind": section.kind,
                    "fields": section_fields,
                }
            )

        return {
            "object_key": layout.object_key,
            "version": layout.version,
            "field_count": len(active_fields),
            "sections": sections,
        }

    def _validate_field_placement(self, section_kind: str, field: DynamicFieldDefinition) -> None:
        if section_kind == "header" and field.type not in self._HEADER_ALLOWED_TYPES:
            raise LayoutValidationError(
                f"Invalid placement for field '{field.field_key}' of type '{field.type}' in section kind '{section_kind}'"
            )

    def _component_for_type(self, field_type: str) -> str:
        return self._COMPONENT_BY_TYPE.get(field_type, "TextInput")


class CustomObjectLayoutApi:
    def __init__(self, service: LayoutBuilderService) -> None:
        self._service = service

    def build_layout(
        self,
        fields: list[DynamicFieldDefinition],
        layout: LayoutConfig,
        request_id: str,
    ) -> dict[str, Any]:
        try:
            schema = self._service.build_ui_schema(fields=fields, layout=layout)
            return {"data": schema, "meta": {"request_id": request_id}}
        except LayoutValidationError as exc:
            return {
                "error": {"code": "layout_validation_error", "message": str(exc), "details": []},
                "meta": {"request_id": request_id},
            }
