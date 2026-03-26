from __future__ import annotations

import unittest

from src.custom_objects import CustomFieldDefinition, CustomObjectDefinition, CustomObjectService


class CustomObjectServiceTests(unittest.TestCase):
    def test_create_update_delete_and_register_schema(self) -> None:
        service = CustomObjectService()
        definition = CustomObjectDefinition(
            tenant_id="tenant-1",
            object_key="project_milestone",
            display_name="Project Milestone",
            description="Tracks implementation milestones",
            module_scope="sales",
            ownership_model="team_owned",
            lifecycle_state="draft",
            dynamic_fields=(
                CustomFieldDefinition(
                    field_key="target_date",
                    label="Target Date",
                    field_type="date",
                    required=True,
                    is_filterable=True,
                    is_sortable=True,
                ),
            ),
        )

        created = service.create_object(definition)
        self.assertEqual(created.object_key, "project_milestone")

        updated = service.update_object(
            "tenant-1",
            "project_milestone",
            display_name="Milestone",
            lifecycle_state="active",
        )
        self.assertEqual(updated.display_name, "Milestone")
        self.assertEqual(updated.lifecycle_state, "active")

        registration = service.register_field(
            "tenant-1",
            "project_milestone",
            CustomFieldDefinition(field_key="budget", label="Budget", field_type="decimal"),
        )
        self.assertIn("budget", registration.schema)
        self.assertIn("tenant_id", registration.schema)

        service.delete_object("tenant-1", "project_milestone")
        self.assertEqual(service.list_registered_objects("tenant-1"), [])

    def test_rejects_core_entity_conflict(self) -> None:
        service = CustomObjectService()
        definition = CustomObjectDefinition(
            tenant_id="tenant-1",
            object_key="account",
            display_name="Account Shadow",
            module_scope="sales",
            ownership_model="org_owned",
            lifecycle_state="draft",
        )

        with self.assertRaisesRegex(ValueError, "core entity"):
            service.create_object(definition)

    def test_schema_isolation_by_tenant(self) -> None:
        service = CustomObjectService()
        tenant1_obj = CustomObjectDefinition(
            tenant_id="tenant-1",
            object_key="incident_postmortem",
            display_name="Incident Postmortem",
            module_scope="support",
            ownership_model="user_owned",
            lifecycle_state="active",
        )
        tenant2_obj = CustomObjectDefinition(
            tenant_id="tenant-2",
            object_key="incident_postmortem",
            display_name="Incident Postmortem",
            module_scope="support",
            ownership_model="user_owned",
            lifecycle_state="active",
        )

        service.create_object(tenant1_obj)
        service.create_object(tenant2_obj)
        service.register_field(
            "tenant-1",
            "incident_postmortem",
            CustomFieldDefinition(field_key="severity", label="Severity", field_type="enum"),
        )

        tenant1_schema = service.get_registration("tenant-1", "incident_postmortem").schema
        tenant2_schema = service.get_registration("tenant-2", "incident_postmortem").schema
        self.assertIn("severity", tenant1_schema)
        self.assertNotIn("severity", tenant2_schema)


if __name__ == "__main__":
    unittest.main()
