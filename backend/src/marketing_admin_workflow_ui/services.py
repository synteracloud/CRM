"""Service for composing end-to-end UI flows with no dead paths."""

from __future__ import annotations

from src.admin_control_center.services import ADMIN_PANELS
from src.campaigns.workspace import build_marketing_workspace

from .entities import IntegratedUiModel, UiFlowEdge, UiNode, WorkflowUiPane


def build_integrated_ui_model() -> IntegratedUiModel:
    marketing_workspace = build_marketing_workspace()
    nodes: list[UiNode] = [
        UiNode(node_id=view.view_id, route=view.route, title=view.title, node_type="workspace")
        for view in marketing_workspace.views
    ]
    nodes.extend(
        UiNode(node_id=panel.panel_id, route=panel.route, title=panel.name, node_type="admin_panel")
        for panel in ADMIN_PANELS
    )
    nodes.extend(
        (
            UiNode(
                node_id="workflow_builder_canvas",
                route="/app/admin/workflows/builder",
                title="Workflow Builder",
                node_type="workflow_ui",
            ),
            UiNode(
                node_id="workflow_validation_report",
                route="/app/admin/workflows/validate",
                title="Validation Report",
                node_type="workflow_ui",
            ),
            UiNode(
                node_id="workflow_execution_replay",
                route="/app/admin/workflows/replay",
                title="Execution Replay",
                node_type="workflow_ui",
            ),
        )
    )

    edges = (
        UiFlowEdge("campaign_workspace", "segment_builder", "Draft campaign routes to segment definition."),
        UiFlowEdge("segment_builder", "funnel_attribution", "Validated segment unlocks attribution monitoring."),
        UiFlowEdge("funnel_attribution", "journey_status", "Attribution filters drive journey runtime monitoring."),
        UiFlowEdge("journey_status", "performance_drilldown", "Journey outcomes feed performance drill-down."),
        UiFlowEdge("performance_drilldown", "workflow_management", "Anomalies escalate to workflow management."),
        UiFlowEdge("workflow_management", "workflow_builder_canvas", "Admin opens visual workflow builder."),
        UiFlowEdge("workflow_builder_canvas", "workflow_validation_report", "Builder validate action opens report."),
        UiFlowEdge(
            "workflow_validation_report",
            "workflow_execution_replay",
            "Approved definition advances to replay/monitoring.",
        ),
        UiFlowEdge("admin_workspace_home", "workflow_management", "Admin home routes to workflow controls."),
        UiFlowEdge("users_roles_permissions", "workflow_management", "Role updates flow into workflow permission checks."),
        UiFlowEdge("custom_object_control", "workflow_management", "Schema updates route to workflow step input validation."),
        UiFlowEdge(
            "config_flags_integrations",
            "campaign_workspace",
            "Config updates redirect to campaign workspace verification.",
        ),
    )

    panes = (
        WorkflowUiPane("palette", "Left Palette", ("trigger_block", "condition_block", "action_templates", "event_picker")),
        WorkflowUiPane("canvas", "Center Canvas", ("graph_authoring", "zoom_pan", "status_overlays")),
        WorkflowUiPane("inspector", "Right Inspector", ("schema_form", "dsl_preview", "validation_state")),
    )

    return IntegratedUiModel(
        model_id="marketing_admin_workflow_ui",
        start_node_id="campaign_workspace",
        nodes=tuple(nodes),
        edges=edges,
        workflow_ui_panes=panes,
    )


def run_self_qc() -> dict[str, object]:
    model = build_integrated_ui_model()
    nodes = {node.node_id for node in model.nodes}
    outgoing: dict[str, int] = {node_id: 0 for node_id in nodes}

    for edge in model.edges:
        outgoing[edge.source] = outgoing.get(edge.source, 0) + 1

    terminals = {"workflow_execution_replay"}
    dead_flow_nodes = sorted(node_id for node_id, count in outgoing.items() if count == 0 and node_id not in terminals)

    checks = {
        "all_edges_resolve": all(edge.source in nodes and edge.target in nodes for edge in model.edges),
        "no_dead_flows": len(dead_flow_nodes) == 0,
        "workflow_ui_three_pane_present": {pane.pane_id for pane in model.workflow_ui_panes} == {"palette", "canvas", "inspector"},
        "marketing_to_admin_handoff_present": any(
            edge.source == "performance_drilldown" and edge.target == "workflow_management" for edge in model.edges
        ),
        "admin_to_workflow_builder_present": any(
            edge.source == "workflow_management" and edge.target == "workflow_builder_canvas" for edge in model.edges
        ),
    }
    score = sum(1 for passed in checks.values() if passed)
    return {
        "checks": checks,
        "dead_flow_nodes": dead_flow_nodes,
        "score": f"{score}/{len(checks)}",
        "target": "10/10",
        "fix_loop": "Fix -> re-fix -> 10/10",
    }
