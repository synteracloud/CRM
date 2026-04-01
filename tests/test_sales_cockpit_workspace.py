from __future__ import annotations

import unittest

from src.sales_cockpit import SalesCockpitApi, build_sales_cockpit


class SalesCockpitWorkspaceTests(unittest.TestCase):
    def test_workspace_contains_pipeline_first_contract(self) -> None:
        workspace = build_sales_cockpit()

        self.assertEqual(workspace.workspace_id, "sales_cockpit")
        self.assertEqual(workspace.workflow_name, "Opportunity pipeline & close outcomes")
        self.assertEqual(
            workspace.canonical_stages,
            ("qualification", "discovery", "proposal", "negotiation", "closed_won", "closed_lost"),
        )
        self.assertIn("advance_stage", workspace.p0_actions)
        self.assertIn("mark_closed_won", workspace.p0_actions)

        view_ids = {view.view_id for view in workspace.views}
        self.assertEqual(
            view_ids,
            {
                "pipeline_execution_rail",
                "deal_detail_workspace",
                "forecast_context_rail",
                "next_actions_panel",
            },
        )

    def test_metrics_map_to_required_read_models(self) -> None:
        workspace = build_sales_cockpit()

        bound_models = {
            binding.read_model
            for view in workspace.views
            for binding in view.metric_bindings
        }
        self.assertEqual(bound_models, {"OpportunityPipelineSnapshotRM", "ActivityTaskOperationalRM"})

    def test_api_returns_workspace_payload(self) -> None:
        api = SalesCockpitApi()

        response = api.get_workspace(request_id="req-sales")

        self.assertEqual(response["meta"]["request_id"], "req-sales")
        self.assertEqual(response["data"]["workspace_id"], "sales_cockpit")
        self.assertGreaterEqual(len(response["data"]["views"]), 4)


if __name__ == "__main__":
    unittest.main()
