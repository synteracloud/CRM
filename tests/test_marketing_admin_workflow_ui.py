from __future__ import annotations

import unittest

from src.marketing_admin_workflow_ui import API_ENDPOINTS, MarketingAdminWorkflowUiApi, build_integrated_ui_model, run_self_qc


class MarketingAdminWorkflowUiTests(unittest.TestCase):
    def test_model_contains_marketing_admin_and_workflow_ui_surfaces(self) -> None:
        model = build_integrated_ui_model()
        node_ids = {node.node_id for node in model.nodes}

        self.assertTrue(
            {
                "campaign_workspace",
                "segment_builder",
                "workflow_management",
                "workflow_builder_canvas",
                "workflow_validation_report",
                "workflow_execution_replay",
            }.issubset(node_ids)
        )

    def test_qc_reports_no_dead_flows_and_target_ten_on_ten(self) -> None:
        qc = run_self_qc()
        self.assertEqual(qc["target"], "10/10")
        self.assertEqual(qc["score"], "5/5")
        self.assertEqual(qc["dead_flow_nodes"], [])
        self.assertTrue(all(qc["checks"].values()))

    def test_api_contracts(self) -> None:
        api = MarketingAdminWorkflowUiApi()

        response = api.get_integrated_ui(request_id="req-ui")
        self.assertEqual(response["meta"]["request_id"], "req-ui")
        self.assertEqual(response["data"]["model_id"], "marketing_admin_workflow_ui")
        self.assertEqual(API_ENDPOINTS["get_integrated_ui"]["path"], "/api/v1/ui/marketing-admin-workflow")

        qc_response = api.get_integrated_ui_qc(request_id="req-ui-qc")
        self.assertEqual(qc_response["meta"]["request_id"], "req-ui-qc")
        self.assertEqual(qc_response["data"]["target"], "10/10")


if __name__ == "__main__":
    unittest.main()
