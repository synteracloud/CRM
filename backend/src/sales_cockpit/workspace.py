"""Sales cockpit workspace model for pipeline-first opportunity execution."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CockpitMetricBinding:
    metric_id: str
    label: str
    read_model: str
    field: str


@dataclass(frozen=True)
class CockpitView:
    view_id: str
    title: str
    route: str
    purpose: str
    metric_bindings: tuple[CockpitMetricBinding, ...]


@dataclass(frozen=True)
class SalesCockpitModel:
    workspace_id: str
    title: str
    workflow_name: str
    primary_jobs: tuple[str, ...]
    p0_actions: tuple[str, ...]
    canonical_stages: tuple[str, ...]
    views: tuple[CockpitView, ...]


SALES_COCKPIT_ID = "sales_cockpit"


SALES_COCKPIT = SalesCockpitModel(
    workspace_id=SALES_COCKPIT_ID,
    title="Sales Cockpit",
    workflow_name="Opportunity pipeline & close outcomes",
    primary_jobs=(
        "Progress opportunities through valid stage transitions",
        "Execute close actions with forecast impact visibility",
        "Maintain next-action hygiene across active deals",
    ),
    p0_actions=("advance_stage", "mark_closed_won", "mark_closed_lost", "add_next_action"),
    canonical_stages=("qualification", "discovery", "proposal", "negotiation", "closed_won", "closed_lost"),
    views=(
        CockpitView(
            view_id="pipeline_execution_rail",
            title="Pipeline Execution Rail",
            route="/app/sales/pipeline",
            purpose="Own list and kanban stage progression actions without leaving the cockpit.",
            metric_bindings=(
                CockpitMetricBinding(
                    metric_id="weighted_pipeline",
                    label="Weighted pipeline",
                    read_model="OpportunityPipelineSnapshotRM",
                    field="weighted_pipeline",
                ),
                CockpitMetricBinding(
                    metric_id="stage_mix",
                    label="Pipeline by stage",
                    read_model="OpportunityPipelineSnapshotRM",
                    field="stage_distribution",
                ),
            ),
        ),
        CockpitView(
            view_id="deal_detail_workspace",
            title="Deal Detail Workspace",
            route="/app/sales/pipeline/deals/:deal_id",
            purpose="Keep detail execution in a split pane with stage, close, and timeline context.",
            metric_bindings=(
                CockpitMetricBinding(
                    metric_id="activity_freshness",
                    label="Latest activity timestamp",
                    read_model="OpportunityPipelineSnapshotRM",
                    field="last_activity_at",
                ),
            ),
        ),
        CockpitView(
            view_id="forecast_context_rail",
            title="Forecast Context Rail",
            route="/app/sales/forecast",
            purpose="Expose weighted, commit, best-case, and closed rollups with anomaly deep-links.",
            metric_bindings=(
                CockpitMetricBinding(
                    metric_id="commit_total",
                    label="Commit total",
                    read_model="OpportunityPipelineSnapshotRM",
                    field="forecast_commit_total",
                ),
                CockpitMetricBinding(
                    metric_id="gap_to_target",
                    label="Gap to target",
                    read_model="OpportunityPipelineSnapshotRM",
                    field="gap_to_target",
                ),
            ),
        ),
        CockpitView(
            view_id="next_actions_panel",
            title="Next Actions Panel",
            route="/app/sales/tasks",
            purpose="Surface due-today, overdue, and no-next-action queues tied to selected deal scope.",
            metric_bindings=(
                CockpitMetricBinding(
                    metric_id="overdue_actions",
                    label="Overdue actions",
                    read_model="ActivityTaskOperationalRM",
                    field="overdue_task_count",
                ),
            ),
        ),
    ),
)


def build_sales_cockpit() -> SalesCockpitModel:
    """Return the canonical sales cockpit model."""

    return SALES_COCKPIT
