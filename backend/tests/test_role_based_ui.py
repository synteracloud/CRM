from __future__ import annotations

import unittest

from src.role_based_ui import RoleBasedUiApi, RoleBasedUiConfigService


class RoleBasedUiTests(unittest.TestCase):
    def test_tenant_admin_gets_admin_and_reporting_sections(self) -> None:
        service = RoleBasedUiConfigService()
        config = service.resolve(tenant_id="t1", principal_id="u-admin", role_ids=("tenant_admin",))
        visible = {section.section_id for section in config.visible_sections}
        self.assertIn("user_admin", visible)
        self.assertIn("tenant_settings", visible)
        self.assertIn("reports", visible)
        self.assertIn("audit_logs", visible)

    def test_agent_denied_admin_and_audit_sections(self) -> None:
        service = RoleBasedUiConfigService()
        config = service.resolve(tenant_id="t1", principal_id="u-agent", role_ids=("agent",))
        visible = {section.section_id for section in config.visible_sections}
        hidden = set(config.hidden_section_ids)

        self.assertIn("records_workspace", visible)
        self.assertIn("record_editor", visible)
        self.assertIn("user_admin", hidden)
        self.assertIn("tenant_settings", hidden)
        self.assertIn("audit_logs", hidden)

    def test_unknown_role_default_deny(self) -> None:
        service = RoleBasedUiConfigService()
        config = service.resolve(tenant_id="t1", principal_id="u-unknown", role_ids=("unknown_role",))
        self.assertEqual(config.visible_sections, tuple())

    def test_api_envelope(self) -> None:
        api = RoleBasedUiApi(RoleBasedUiConfigService())
        response = api.get_ui_config(
            request_id="req-ui",
            tenant_id="t1",
            principal_id="u-analyst",
            role_ids=("analyst",),
        )
        self.assertEqual(response["meta"]["request_id"], "req-ui")
        self.assertIn("data", response)
        self.assertEqual(response["data"]["principal_id"], "u-analyst")

    def test_role_permission_mapping_matches_security_matrix(self) -> None:
        service = RoleBasedUiConfigService()

        owner = set(service.resolve(tenant_id="t1", principal_id="u-owner", role_ids=("tenant_owner",)).permissions)
        self.assertIn("users.manage_roles", owner)
        self.assertIn("records.delete", owner)

        manager = set(service.resolve(tenant_id="t1", principal_id="u-manager", role_ids=("manager",)).permissions)
        self.assertIn("users.read", manager)
        self.assertIn("reports.read", manager)
        self.assertNotIn("users.manage_roles", manager)
        self.assertNotIn("records.delete", manager)

        analyst = set(service.resolve(tenant_id="t1", principal_id="u-analyst", role_ids=("analyst",)).permissions)
        self.assertIn("reports.read", analyst)
        self.assertNotIn("records.update", analyst)

        auditor = set(service.resolve(tenant_id="t1", principal_id="u-auditor", role_ids=("auditor",)).permissions)
        self.assertIn("audit.logs.read", auditor)
        self.assertNotIn("records.update", auditor)

        platform_sec = set(
            service.resolve(tenant_id="t1", principal_id="u-psoc", role_ids=("platform_security_ops",)).permissions
        )
        self.assertEqual(platform_sec, set())


if __name__ == "__main__":
    unittest.main()
