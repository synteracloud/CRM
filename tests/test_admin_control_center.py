from __future__ import annotations

import unittest

from src.admin_control_center import API_ENDPOINTS, AdminControlCenterApi, AdminControlCenterService, run_self_qc


class AdminControlCenterTests(unittest.TestCase):
    def test_owner_gets_complete_admin_control_center(self) -> None:
        service = AdminControlCenterService()
        center = service.build(tenant_id="t1", principal_id="owner-1", role_ids=("tenant_owner",))

        visible_ids = {panel.panel_id for panel in center.views}
        self.assertIn("users_roles_permissions", visible_ids)
        self.assertIn("custom_object_control", visible_ids)
        self.assertIn("workflow_management", visible_ids)
        self.assertIn("config_flags_integrations", visible_ids)

        panel_state = {panel.panel_id: panel.state for panel in center.views}
        self.assertEqual(panel_state["users_roles_permissions"], "editable")
        self.assertEqual(panel_state["workflow_management"], "editable")

    def test_manager_is_default_deny_for_critical_admin_controls(self) -> None:
        service = AdminControlCenterService()
        center = service.build(tenant_id="t1", principal_id="mgr-1", role_ids=("manager",))

        hidden = set(center.hidden_panel_ids)
        self.assertNotIn("users_roles_permissions", hidden)
        self.assertIn("custom_object_control", hidden)
        self.assertIn("workflow_management", hidden)
        self.assertIn("config_flags_integrations", hidden)

    def test_api_envelope_and_endpoint(self) -> None:
        api = AdminControlCenterApi(AdminControlCenterService())
        response = api.get_admin_control_center(
            request_id="req-admin",
            tenant_id="t1",
            principal_id="admin-1",
            role_ids=("tenant_admin",),
        )

        self.assertEqual(API_ENDPOINTS["get_admin_control_center"]["path"], "/api/v1/admin/control-center")
        self.assertEqual(response["meta"]["request_id"], "req-admin")
        self.assertIn("data", response)
        self.assertEqual(response["data"]["principal_id"], "admin-1")

    def test_self_qc_is_10_on_10(self) -> None:
        qc = run_self_qc()
        self.assertTrue(all(qc.values()), qc)


if __name__ == "__main__":
    unittest.main()
