from __future__ import annotations

import unittest

from src.custom_object_framework import (
    ALLOWED_FIELD_TYPES,
    FieldBuilderApi,
    FieldBuilderService,
    FieldDefinition,
    FieldValidationError,
    ValidationRule,
)


class FieldBuilderServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FieldBuilderService()
        self.service.create_object("project_milestone")

    def test_dynamic_field_creation_and_validation(self) -> None:
        self.service.create_field(
            FieldDefinition(
                object_key="project_milestone",
                field_key="name",
                label="Name",
                type="text",
                required=True,
                max_length=32,
                is_searchable=True,
                is_filterable=True,
                is_sortable=True,
            )
        )
        self.service.create_field(
            FieldDefinition(
                object_key="project_milestone",
                field_key="status",
                label="Status",
                type="enum",
                enum_values=("planned", "in_progress", "done"),
                required=True,
                default_value="planned",
            )
        )
        self.service.create_rule(
            ValidationRule(
                rule_id="rule-name-format",
                object_key="project_milestone",
                target_field_keys=("name",),
                expression={"op": "regex", "field": "name", "pattern": r"^[a-zA-Z0-9 _-]+$"},
                error_code="invalid_name",
                error_message="Name contains unsupported characters",
            )
        )

        violations = self.service.validate_record(
            object_key="project_milestone",
            payload={"name": "Milestone 1", "status": "planned"},
        )
        self.assertEqual(violations, [])

        with self.assertRaises(FieldValidationError):
            self.service.validate_record(
                object_key="project_milestone",
                payload={"name": "Milestone which is way too long for max_length", "status": "planned"},
            )

    def test_rejects_invalid_field_type(self) -> None:
        self.assertNotIn("currency", ALLOWED_FIELD_TYPES)
        with self.assertRaises(FieldValidationError):
            self.service.create_field(
                FieldDefinition(
                    object_key="project_milestone",
                    field_key="budget",
                    label="Budget",
                    type="currency",  # type: ignore[arg-type]
                )
            )

    def test_range_and_required_if_rules(self) -> None:
        self.service.create_field(
            FieldDefinition(object_key="project_milestone", field_key="priority", label="Priority", type="number")
        )
        self.service.create_field(
            FieldDefinition(
                object_key="project_milestone",
                field_key="status",
                label="Status",
                type="enum",
                enum_values=("planned", "blocked"),
            )
        )
        self.service.create_field(
            FieldDefinition(object_key="project_milestone", field_key="block_reason", label="Block reason", type="long_text")
        )
        self.service.create_rule(
            ValidationRule(
                rule_id="priority-range",
                object_key="project_milestone",
                target_field_keys=("priority",),
                expression={"op": "range", "field": "priority", "min": 1, "max": 5},
                error_code="priority_out_of_range",
                error_message="Priority must be between 1 and 5",
            )
        )
        self.service.create_rule(
            ValidationRule(
                rule_id="block-reason-required",
                object_key="project_milestone",
                target_field_keys=("block_reason",),
                expression={
                    "op": "required_if",
                    "if": {"field": "status", "eq": "blocked"},
                    "then_required": "block_reason",
                },
                error_code="block_reason_required",
                error_message="block_reason is required when status is blocked",
            )
        )

        violations = self.service.validate_record(
            "project_milestone", {"priority": 8, "status": "blocked", "block_reason": ""}
        )
        self.assertEqual(len(violations), 2)
        self.assertEqual({v.error_code for v in violations}, {"priority_out_of_range", "block_reason_required"})


class FieldBuilderApiTests(unittest.TestCase):
    def test_api_contract_for_field_builder(self) -> None:
        service = FieldBuilderService()
        api = FieldBuilderApi(service)

        create_object = api.create_object("release_note", request_id="req-1")
        self.assertEqual(create_object["data"]["object_key"], "release_note")

        create_field = api.create_field(
            FieldDefinition(
                object_key="release_note",
                field_key="published_on",
                label="Published On",
                type="date",
                required=True,
            ),
            request_id="req-2",
        )
        self.assertEqual(create_field["meta"]["request_id"], "req-2")

        validate = api.validate_record(
            object_key="release_note",
            payload={"published_on": "2026-03-26"},
            request_id="req-3",
        )
        self.assertTrue(validate["data"]["valid"])


if __name__ == "__main__":
    unittest.main()
