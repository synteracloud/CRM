from __future__ import annotations

import unittest

from src.custom_object_framework import (
    CustomObjectLayoutApi,
    DynamicFieldDefinition,
    LayoutBuilderService,
    LayoutConfig,
    LayoutSection,
    LayoutValidationError,
)


class CustomObjectLayoutBuilderTests(unittest.TestCase):
    def _fields(self) -> list[DynamicFieldDefinition]:
        return [
            DynamicFieldDefinition(field_key="name", label="Name", type="text", required=True),
            DynamicFieldDefinition(field_key="description", label="Description", type="long_text"),
            DynamicFieldDefinition(field_key="account_id", label="Account", type="lookup", required=True),
            DynamicFieldDefinition(field_key="stage", label="Stage", type="enum", required=True),
        ]

    def test_builds_data_driven_ui_schema_for_valid_layout(self) -> None:
        service = LayoutBuilderService()
        layout = LayoutConfig(
            object_key="project_milestone",
            version=1,
            sections=(
                LayoutSection(section_key="main", label="Main", kind="body", field_keys=("name", "description", "stage")),
                LayoutSection(section_key="context", label="Context", kind="sidebar", field_keys=("account_id",)),
            ),
        )

        schema = service.build_ui_schema(self._fields(), layout)
        self.assertEqual(schema["object_key"], "project_milestone")
        self.assertEqual(schema["field_count"], 4)
        self.assertEqual(schema["sections"][0]["fields"][1]["component"], "TextArea")

    def test_rejects_unknown_or_inactive_layout_fields(self) -> None:
        service = LayoutBuilderService()
        layout = LayoutConfig(
            object_key="project_milestone",
            version=1,
            sections=(
                LayoutSection(section_key="main", label="Main", kind="body", field_keys=("name", "missing_field")),
            ),
        )
        with self.assertRaisesRegex(LayoutValidationError, "unknown or inactive"):
            service.build_ui_schema(self._fields(), layout)

    def test_rejects_orphan_active_fields(self) -> None:
        service = LayoutBuilderService()
        layout = LayoutConfig(
            object_key="project_milestone",
            version=1,
            sections=(
                LayoutSection(section_key="main", label="Main", kind="body", field_keys=("name", "description")),
            ),
        )
        with self.assertRaisesRegex(LayoutValidationError, "Orphan active fields"):
            service.build_ui_schema(self._fields(), layout)

    def test_enforces_field_placement_rules(self) -> None:
        service = LayoutBuilderService()
        layout = LayoutConfig(
            object_key="project_milestone",
            version=1,
            sections=(
                LayoutSection(section_key="hero", label="Hero", kind="header", field_keys=("description",)),
                LayoutSection(section_key="main", label="Main", kind="body", field_keys=("name", "account_id", "stage")),
            ),
        )
        with self.assertRaisesRegex(LayoutValidationError, "Invalid placement"):
            service.build_ui_schema(self._fields(), layout)

    def test_api_returns_consistent_error_envelope(self) -> None:
        api = CustomObjectLayoutApi(LayoutBuilderService())
        layout = LayoutConfig(
            object_key="project_milestone",
            version=1,
            sections=(
                LayoutSection(section_key="main", label="Main", kind="body", field_keys=("name",)),
            ),
        )
        response = api.build_layout(self._fields(), layout, request_id="req-layout-1")
        self.assertEqual(response["error"]["code"], "layout_validation_error")
        self.assertEqual(response["meta"]["request_id"], "req-layout-1")


if __name__ == "__main__":
    unittest.main()
