from __future__ import annotations

import unittest

from src.campaigns import CampaignApi, CampaignService, build_marketing_workspace


class MarketingWorkspaceTests(unittest.TestCase):
    def test_workspace_has_clear_campaign_flow_and_required_views(self) -> None:
        workspace = build_marketing_workspace()
        self.assertEqual(workspace.workspace_id, "marketing_workspace")
        self.assertIn("Activate campaign", workspace.campaign_flow)
        self.assertIn("Complete campaign", workspace.campaign_flow)

        view_ids = {view.view_id for view in workspace.views}
        self.assertTrue(
            {
                "campaign_workspace",
                "segment_builder",
                "funnel_attribution",
                "journey_status",
                "performance_drilldown",
            }.issubset(view_ids)
        )

    def test_metrics_tie_to_existing_read_models(self) -> None:
        workspace = build_marketing_workspace()
        allowed_models = {
            "LeadFunnelPerformanceRM",
            "WorkflowAutomationOutcomeRM",
            "CommunicationEngagementRM",
            "OpportunityPipelineSnapshotRM",
        }
        bound_models = {
            binding.read_model
            for view in workspace.views
            for binding in view.metric_bindings
        }
        self.assertTrue(bound_models.issubset(allowed_models))

    def test_api_returns_workspace_payload_with_interaction_patterns(self) -> None:
        api = CampaignApi(CampaignService())
        response = api.get_marketing_workspace(request_id="req-marketing")

        self.assertEqual(response["meta"]["request_id"], "req-marketing")
        self.assertEqual(response["data"]["workspace_id"], "marketing_workspace")
        self.assertGreaterEqual(len(response["data"]["interaction_patterns"]), 4)


if __name__ == "__main__":
    unittest.main()
