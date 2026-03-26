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


def _success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}



def _error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}
