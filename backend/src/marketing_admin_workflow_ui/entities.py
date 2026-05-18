"""Entities for integrated marketing/admin/workflow UI maps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

NodeType = Literal["workspace", "admin_panel", "workflow_ui"]


@dataclass(frozen=True)
class UiNode:
    node_id: str
    route: str
    title: str
    node_type: NodeType


@dataclass(frozen=True)
class UiFlowEdge:
    source: str
    target: str
    reason: str


@dataclass(frozen=True)
class WorkflowUiPane:
    pane_id: str
    title: str
    controls: tuple[str, ...]


@dataclass(frozen=True)
class IntegratedUiModel:
    model_id: str
    start_node_id: str
    nodes: tuple[UiNode, ...]
    edges: tuple[UiFlowEdge, ...]
    workflow_ui_panes: tuple[WorkflowUiPane, ...]
