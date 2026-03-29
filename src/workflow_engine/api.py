"""API contracts for workflow lifecycle operations."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from src.event_bus import Event

from .entities import WorkflowNotFoundError, WorkflowValidationError
from .services import WorkflowEngine

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "start_workflow": {"method": "POST", "path": "/api/v1/workflows/{workflow_key}/start"},
    "stop_workflow": {"method": "POST", "path": "/api/v1/workflows/executions/{execution_id}/stop"},
    "create_workflow": {"method": "POST", "path": "/api/v1/workflows"},
    "edit_workflow": {"method": "PUT", "path": "/api/v1/workflows/{workflow_key}"},
    "get_workflow_graph": {"method": "GET", "path": "/api/v1/workflows/{workflow_key}/graph"},
    "recover_execution": {"method": "POST", "path": "/api/v1/workflows/executions/{execution_id}/recover"},
    "get_recovery_audit": {"method": "GET", "path": "/api/v1/workflows/executions/{execution_id}/recovery-audit"},
    "get_recovery_dashboard": {"method": "GET", "path": "/api/v1/workflows/recovery/dashboard"},
}


class WorkflowApi:
    def __init__(self, engine: WorkflowEngine) -> None:
        self._engine = engine

    def start_workflow(
        self, workflow_key: str, request_id: str, event: Event | None = None, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        try:
            execution = self._engine.start_workflow(workflow_key, event=event, context=context)
            return _success(asdict(execution), request_id)
        except (WorkflowValidationError, WorkflowNotFoundError) as exc:
            return _error("conflict", str(exc), request_id)

    def stop_workflow(self, execution_id: str, request_id: str) -> dict[str, Any]:
        try:
            execution = self._engine.stop_workflow(execution_id)
            return _success(asdict(execution), request_id)
        except WorkflowNotFoundError as exc:
            return _error("not_found", str(exc), request_id)

    def create_workflow(self, graph: dict[str, Any], request_id: str) -> dict[str, Any]:
        try:
            definition = self._engine.create_workflow_from_graph(_graph_from_dict(graph))
            return _success(asdict(definition), request_id)
        except (WorkflowValidationError, WorkflowNotFoundError) as exc:
            return _error("conflict", str(exc), request_id)

    def edit_workflow(self, workflow_key: str, graph: dict[str, Any], request_id: str) -> dict[str, Any]:
        try:
            definition = self._engine.update_workflow_from_graph(workflow_key, _graph_from_dict(graph))
            return _success(asdict(definition), request_id)
        except WorkflowNotFoundError as exc:
            return _error("not_found", str(exc), request_id)
        except WorkflowValidationError as exc:
            return _error("conflict", str(exc), request_id)

    def get_workflow_graph(self, workflow_key: str, request_id: str) -> dict[str, Any]:
        try:
            graph = self._engine.export_workflow_graph(workflow_key)
            return _success(asdict(graph), request_id)
        except WorkflowNotFoundError as exc:
            return _error("not_found", str(exc), request_id)

    def recover_execution(
        self, execution_id: str, strategy: str, reason: str, actor: str, request_id: str
    ) -> dict[str, Any]:
        try:
            execution = self._engine.recover_execution(
                execution_id=execution_id,
                strategy=strategy,
                reason=reason,
                actor=actor,
            )
            return _success(asdict(execution), request_id)
        except (WorkflowValidationError, WorkflowNotFoundError) as exc:
            return _error("conflict", str(exc), request_id)

    def get_recovery_audit(self, execution_id: str, request_id: str) -> dict[str, Any]:
        try:
            return _success(self._engine.recovery_audit_trail(execution_id), request_id)
        except WorkflowNotFoundError as exc:
            return _error("not_found", str(exc), request_id)

    def get_recovery_dashboard(self, request_id: str) -> dict[str, Any]:
        return _success(self._engine.recovery_dashboard(), request_id)


def _success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}



def _error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


def _graph_from_dict(payload: dict[str, Any]) -> Any:
    from .entities import ConditionDefinition, ConditionRule, TriggerDefinition, WorkflowBuilderGraph, WorkflowGraphEdge, WorkflowGraphNode

    return WorkflowBuilderGraph(
        workflow_key=payload["workflow_key"],
        version=payload.get("version", "v1"),
        metadata=payload.get("metadata", {}),
        triggers=TriggerDefinition(**payload["triggers"]),
        conditions=ConditionDefinition(
            match=payload.get("conditions", {}).get("match", "all"),
            rules=tuple(ConditionRule(**rule) for rule in payload.get("conditions", {}).get("rules", [])),
        ),
        nodes=tuple(WorkflowGraphNode(**node) for node in payload.get("nodes", [])),
        edges=tuple(WorkflowGraphEdge(**edge) for edge in payload.get("edges", [])),
        start_node_id=payload["start_node_id"],
    )
