"""Public REST endpoints for Workflow Execution Engine.

Spec: backend/docs/infrastructure/workflow-catalog.md §12
API standards: backend/docs/api-standards.md

Routes:
    GET  /api/v1/workflows
    POST /api/v1/workflows
    GET  /api/v1/workflows/{workflow_id}
    POST /api/v1/workflows/{workflow_id}/publish
    POST /api/v1/workflows/{workflow_id}/simulate
    GET  /api/v1/workflows/runs
    GET  /api/v1/workflows/runs/{execution_id}
    POST /api/v1/workflows/runs/{execution_id}/retry
    POST /api/v1/workflows/runs/{execution_id}/cancel
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.models.workflows import WorkflowDefinition, WorkflowExecution, WorkflowStep
from services.workflows.entities import (
    RETRYABLE_EXECUTION_STATUSES,
    TERMINAL_EXECUTION_STATUSES,
    WorkflowDomainError,
    validate_workflow_transition,
    validate_steps_dsl,
)
from services.workflows.service import WorkflowService

router = APIRouter(tags=["workflows"])

_svc = WorkflowService()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


def _wf_dict(w: WorkflowDefinition) -> dict[str, Any]:
    return {
        "workflow_id":    w.workflow_id,
        "tenant_id":      w.tenant_id,
        "workflow_key":   w.workflow_key,
        "name":           w.name,
        "description":    w.description,
        "status":         w.status,
        "trigger_events": w.trigger_events,
        "steps_dsl":      w.steps_dsl,
        "max_retries":    w.max_retries,
        "is_system":      w.is_system,
        "version":        w.version,
        "created_by":     w.created_by,
        "created_at":     w.created_at.isoformat() if w.created_at else None,
        "updated_at":     w.updated_at.isoformat() if w.updated_at else None,
    }


def _exec_dict(e: WorkflowExecution, steps: list[WorkflowStep] | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {
        "execution_id":        e.execution_id,
        "workflow_id":         e.workflow_id,
        "tenant_id":           e.tenant_id,
        "workflow_key":        e.workflow_key,
        "workflow_name":       e.workflow_name,
        "trigger_event":       e.trigger_event,
        "trigger_payload":     e.trigger_payload,
        "status":              e.status,
        "step_count":          e.step_count,
        "current_step":        e.current_step,
        "failed_step":         e.failed_step,
        "error_message":       e.error_message,
        "retry_count":         e.retry_count,
        "parent_execution_id": e.parent_execution_id,
        "started_at":          e.started_at.isoformat() if e.started_at else None,
        "ended_at":            e.ended_at.isoformat() if e.ended_at else None,
        "duration_ms":         e.duration_ms,
        "created_at":          e.created_at.isoformat() if e.created_at else None,
    }
    if steps is not None:
        d["steps"] = [_step_dict(s) for s in steps]
    return d


def _step_dict(s: WorkflowStep) -> dict[str, Any]:
    return {
        "step_record_id": s.step_record_id,
        "execution_id":   s.execution_id,
        "step_index":     s.step_index,
        "step_name":      s.step_name,
        "step_type":      s.step_type,
        "status":         s.status,
        "input_data":     s.input_data,
        "output_data":    s.output_data,
        "error_message":  s.error_message,
        "duration_ms":    s.duration_ms,
    }


def _get_workflow_or_404(workflow_id: str, tenant_id: str, db: Session) -> WorkflowDefinition:
    w = db.get(WorkflowDefinition, workflow_id)
    if w is None or w.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return w


def _get_execution_or_404(execution_id: str, tenant_id: str, db: Session) -> WorkflowExecution:
    e = db.get(WorkflowExecution, execution_id)
    if e is None or e.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")
    return e


# ── Request schemas ───────────────────────────────────────────────────────────

class CreateWorkflowRequest(BaseModel):
    name: str
    trigger_events: list
    description: Optional[str] = None
    steps_dsl: Optional[list] = None
    max_retries: int = 3
    is_system: bool = False

    @validator("trigger_events")
    def trigger_events_nonempty(cls, v):
        if not v:
            raise ValueError("trigger_events must not be empty")
        return v


class SimulateRequest(BaseModel):
    trigger_payload: dict = {}


class RetryRequest(BaseModel):
    pass


class CancelRequest(BaseModel):
    pass


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/api/v1/workflows/runs")
def list_runs(
    status: Optional[str] = Query(None),
    workflow_key: Optional[str] = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(WorkflowExecution).where(WorkflowExecution.tenant_id == claims.tenant_id)
    if status:
        q = q.where(WorkflowExecution.status == status)
    if workflow_key:
        q = q.where(WorkflowExecution.workflow_key == workflow_key)
    q = q.order_by(WorkflowExecution.started_at.desc())
    rows = db.execute(q).scalars().all()
    return {"data": [_exec_dict(e) for e in rows], "meta": _meta()}


@router.get("/api/v1/workflows/runs/{execution_id}")
def get_run(
    execution_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    e = _get_execution_or_404(execution_id, claims.tenant_id, db)
    steps = db.execute(
        select(WorkflowStep)
        .where(WorkflowStep.execution_id == execution_id)
        .order_by(WorkflowStep.step_index)
    ).scalars().all()
    return {"data": _exec_dict(e, list(steps)), "meta": _meta()}


@router.post("/api/v1/workflows/runs/{execution_id}/retry", status_code=status.HTTP_201_CREATED)
def retry_execution(
    execution_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    e = _get_execution_or_404(execution_id, claims.tenant_id, db)
    retryable = {s.value for s in RETRYABLE_EXECUTION_STATUSES}
    if e.status not in retryable:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot retry execution with status '{e.status}'. Only failed/retrying executions can be retried.",
        )

    now = datetime.now(timezone.utc)
    new_exec = WorkflowExecution(
        execution_id=str(uuid.uuid4()),
        workflow_id=e.workflow_id,
        tenant_id=claims.tenant_id,
        workflow_key=e.workflow_key,
        workflow_name=e.workflow_name,
        trigger_event=e.trigger_event,
        trigger_payload=e.trigger_payload or {},
        status="running",
        step_count=e.step_count,
        current_step=0,
        retry_count=(e.retry_count or 0) + 1,
        parent_execution_id=execution_id,
        started_at=now,
        created_at=now,
    )
    db.add(new_exec)
    db.commit()
    db.refresh(new_exec)
    return {"data": _exec_dict(new_exec), "meta": _meta()}


@router.post("/api/v1/workflows/runs/{execution_id}/cancel")
def cancel_execution(
    execution_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    e = _get_execution_or_404(execution_id, claims.tenant_id, db)
    terminal = {s.value for s in TERMINAL_EXECUTION_STATUSES}
    if e.status == "succeeded":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot cancel a succeeded execution",
        )
    if e.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Execution is already cancelled",
        )

    now = datetime.now(timezone.utc)
    e.status = "cancelled"
    e.ended_at = now
    db.commit()
    db.refresh(e)
    return {"data": _exec_dict(e), "meta": _meta()}


@router.get("/api/v1/workflows")
def list_workflows(
    status: Optional[str] = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(WorkflowDefinition).where(WorkflowDefinition.tenant_id == claims.tenant_id)
    if status:
        q = q.where(WorkflowDefinition.status == status)
    q = q.order_by(WorkflowDefinition.created_at.desc())
    rows = db.execute(q).scalars().all()
    return {"data": [_wf_dict(w) for w in rows], "meta": _meta()}


@router.post("/api/v1/workflows", status_code=status.HTTP_201_CREATED)
def create_workflow(
    body: CreateWorkflowRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    # Generate a workflow_key from the name
    workflow_key = body.name.lower().replace(" ", "_").replace("-", "_")

    w = WorkflowDefinition(
        workflow_id=str(uuid.uuid4()),
        tenant_id=claims.tenant_id,
        workflow_key=workflow_key,
        name=body.name,
        description=body.description,
        status="draft",
        trigger_events=body.trigger_events,
        steps_dsl=body.steps_dsl or [],
        max_retries=body.max_retries,
        is_system=body.is_system,
        version=1,
        created_by=claims.sub,
        created_at=now,
        updated_at=now,
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return {"data": _wf_dict(w), "meta": _meta()}


@router.get("/api/v1/workflows/{workflow_id}")
def get_workflow(
    workflow_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    w = _get_workflow_or_404(workflow_id, claims.tenant_id, db)
    return {"data": _wf_dict(w), "meta": _meta()}


@router.post("/api/v1/workflows/{workflow_id}/publish")
def publish_workflow(
    workflow_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    w = _get_workflow_or_404(workflow_id, claims.tenant_id, db)

    # Cannot transition to active if already active
    try:
        validate_workflow_transition(w.status, "active")
    except WorkflowDomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # Must have steps
    if not w.steps_dsl:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot publish a workflow with no steps",
        )

    w.status = "active"
    w.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(w)
    return {"data": _wf_dict(w), "meta": _meta()}


@router.post("/api/v1/workflows/{workflow_id}/simulate")
def simulate_workflow(
    workflow_id: str,
    body: SimulateRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    w = _get_workflow_or_404(workflow_id, claims.tenant_id, db)
    wf_dict = _wf_dict(w)
    steps = _svc.simulate_execution(wf_dict, body.trigger_payload)
    return {
        "data": {
            "simulated":   True,
            "workflow_id": workflow_id,
            "steps":       steps,
        },
        "meta": _meta(),
    }
