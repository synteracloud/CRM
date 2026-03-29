"""Marketing workspace view model for campaign execution and analytics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkspaceMetricBinding:
    metric_id: str
    label: str
    read_model: str
    field: str


@dataclass(frozen=True)
class WorkspaceView:
    view_id: str
    title: str
    route: str
    purpose: str
    metric_bindings: tuple[WorkspaceMetricBinding, ...]


@dataclass(frozen=True)
class InteractionPattern:
    pattern_id: str
    name: str
    trigger: str
    response: str


@dataclass(frozen=True)
class CampaignWorkspaceModel:
    workspace_id: str
    title: str
    workflow_name: str
    campaign_flow: tuple[str, ...]
    views: tuple[WorkspaceView, ...]
    interaction_patterns: tuple[InteractionPattern, ...]


MARKETING_WORKSPACE_ID = "marketing_workspace"


MARKETING_WORKSPACE = CampaignWorkspaceModel(
    workspace_id=MARKETING_WORKSPACE_ID,
    title="Marketing Workspace",
    workflow_name="Lead intake, assignment, conversion",
    campaign_flow=(
        "Create draft campaign",
        "Build and validate segment",
        "Activate campaign",
        "Track funnel and attribution",
        "Monitor journey execution",
        "Drill down performance",
        "Complete campaign",
    ),
    views=(
        WorkspaceView(
            view_id="campaign_workspace",
            title="Campaign Workspace",
            route="/app/marketing/campaigns",
            purpose="Manage campaign lifecycle from draft to completion.",
            metric_bindings=(
                WorkspaceMetricBinding(
                    metric_id="campaign_stage_mix",
                    label="Campaigns by status",
                    read_model="WorkflowAutomationOutcomeRM",
                    field="execution_volume_by_status",
                ),
            ),
        ),
        WorkspaceView(
            view_id="segment_builder",
            title="Segment Builder",
            route="/app/marketing/segments",
            purpose="Compose and validate rules for lead/contact audiences.",
            metric_bindings=(
                WorkspaceMetricBinding(
                    metric_id="segment_to_lead_quality",
                    label="Qualified lead match rate",
                    read_model="LeadFunnelPerformanceRM",
                    field="lead_quality_match_rate",
                ),
            ),
        ),
        WorkspaceView(
            view_id="funnel_attribution",
            title="Funnel & Attribution",
            route="/app/marketing/funnel-attribution",
            purpose="Inspect source-to-conversion movement and attribution outcomes.",
            metric_bindings=(
                WorkspaceMetricBinding(
                    metric_id="source_conversion_rate",
                    label="Source conversion",
                    read_model="LeadFunnelPerformanceRM",
                    field="source_channel_conversion_rate",
                ),
            ),
        ),
        WorkspaceView(
            view_id="journey_status",
            title="Journey Status",
            route="/app/marketing/journeys",
            purpose="Observe automation run health for campaign-triggered journeys.",
            metric_bindings=(
                WorkspaceMetricBinding(
                    metric_id="journey_success_rate",
                    label="Journey success rate",
                    read_model="WorkflowAutomationOutcomeRM",
                    field="success_rate",
                ),
            ),
        ),
        WorkspaceView(
            view_id="performance_drilldown",
            title="Performance Drill-down",
            route="/app/marketing/performance",
            purpose="Pivot from campaign summary into segment/source/entity details.",
            metric_bindings=(
                WorkspaceMetricBinding(
                    metric_id="campaign_engagement_rate",
                    label="Engagement rate",
                    read_model="CommunicationEngagementRM",
                    field="delivery_open_click_reply_rate",
                ),
                WorkspaceMetricBinding(
                    metric_id="campaign_to_pipeline",
                    label="Campaign-influenced pipeline",
                    read_model="OpportunityPipelineSnapshotRM",
                    field="weighted_pipeline",
                ),
            ),
        ),
    ),
    interaction_patterns=(
        InteractionPattern(
            pattern_id="flow_guardrails",
            name="Guided campaign flow",
            trigger="User opens draft campaign",
            response="UI highlights next required action (segment validation, activation gate, completion criteria).",
        ),
        InteractionPattern(
            pattern_id="funnel_cross_filter",
            name="Cross-filter funnel",
            trigger="User selects source/channel in funnel view",
            response="Segment builder, journey status, and drill-down views inherit source filter context.",
        ),
        InteractionPattern(
            pattern_id="journey_exception_handoff",
            name="Journey exception handoff",
            trigger="Journey failure rate breaches threshold",
            response="Show failing steps, linked executions, and escalation actions from workflow outcomes.",
        ),
        InteractionPattern(
            pattern_id="metric_traceability",
            name="Metric traceability",
            trigger="User hovers metric badge",
            response="Tooltip displays backing read model + field to avoid opaque/passive data dumps.",
        ),
    ),
)


def build_marketing_workspace() -> CampaignWorkspaceModel:
    """Return the canonical marketing workspace model."""

    return MARKETING_WORKSPACE
