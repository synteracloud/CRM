"""Public REST endpoints for follow-up management.

Spec: backend/docs/followup-enforcement-model.md
API standards: backend/docs/api-standards.md
Security: backend/docs/identity-auth-rbac.md

Routes:
    GET  /api/v1/followups
    POST /api/v1/followups
    GET  /api/v1/followups/{task_id}
    PATCH /api/v1/followups/{task_id}/complete
    POST /api/v1/followups/{task_id}/escalate
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.models.followup import FollowupEscalation, FollowupTask

router = APIRouter(tags=["followups"])

_VALID_RULE_TYPES = {"TimeBased", "ActivityBased", "InactivityBased"}
_VALID_ESCALATION_LEVELS = {"reminder", "warning", "escalated", "reassigned"}
_MANAGER_ROLES: frozenset[str] = frozenset({"manager", "admin"})


# ── Helpers ───────────────────────────────────────────────────────────────────


def _meta(request_id: str | None = None, **extra: Any) -> dict[str, Any]:
    return {"request_id": request_id or str(uuid.uuid4()), **extra}


def _task_dict(t: FollowupTask) -> dict[str, Any]:
    return {
        "task_id": t.task_id,
        "tenant_id": t.tenant_id,
        "lead_id": t.lead_id,
        "owner_id": t.owner_id,
        "state": t.state,
        "due_at": t.due_at.isoformat() if t.due_at else None,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        "completed_activity_id": t.completed_activity_id,
        "rule_type": t.rule_type,
        "escalation_level": t.escalation_level,
        "generated_by": t.generated_by,
        "is_canonical": t.is_canonical,
    }


def _require_manager(claims: TokenClaims) -> None:
    if claims.role not in _MANAGER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin role required",
        )


def _get_task_or_404(task_id: str, tenant_id: str, db: Session) -> FollowupTask:
    task = db.get(FollowupTask, task_id)
    if task is None or task.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Follow-up not found")
    return task


# ── Request schemas ───────────────────────────────────────────────────────────


class CreateFollowupRequest(BaseModel):
    lead_id: str
    owner_user_id: str
    rule_type: str = "TimeBased"
    due_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="RFC3339 UTC. Defaults to now (T+0 enforcement trigger).",
    )


class CompleteFollowupRequest(BaseModel):
    completed_activity_id: str | None = None


class EscalateFollowupRequest(BaseModel):
    reason: str
    escalation_level: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/api/v1/followups")
def list_followups(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    lead_id: str | None = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List follow-ups for the authenticated tenant. Overdue tasks pinned first."""
    q = select(FollowupTask).where(FollowupTask.tenant_id == claims.tenant_id)
    if lead_id:
        q = q.where(FollowupTask.lead_id == lead_id)

    # Overdue first, then pending by due_at, then completed last
    sort_key = case(
        (FollowupTask.state == "overdue", 0),
        (FollowupTask.state == "pending", 1),
        else_=2,
    )
    q = q.order_by(sort_key, FollowupTask.due_at)

    count_q = (
        select(func.count())
        .select_from(FollowupTask)
        .where(FollowupTask.tenant_id == claims.tenant_id)
    )
    if lead_id:
        count_q = count_q.where(FollowupTask.lead_id == lead_id)
    total_count = db.execute(count_q).scalar_one()

    offset = (page - 1) * page_size
    rows = db.execute(q.offset(offset).limit(page_size)).scalars().all()

    import math
    total_pages = math.ceil(total_count / page_size) if page_size else 1
    return {
        "data": [_task_dict(t) for t in rows],
        "meta": _meta(
            total_items=total_count,
            total_pages=total_pages,
            page=page,
            page_size=page_size,
        ),
    }


@router.post("/api/v1/followups", status_code=status.HTTP_201_CREATED)
def create_followup(
    body: CreateFollowupRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Create a follow-up task. Sets T+0 enforcement trigger."""
    if body.rule_type not in _VALID_RULE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"rule_type must be one of {sorted(_VALID_RULE_TYPES)}",
        )

    task = FollowupTask(
        task_id=str(uuid.uuid4()),
        tenant_id=claims.tenant_id,
        lead_id=body.lead_id,
        owner_id=body.owner_user_id,
        state="pending",
        due_at=body.due_at,
        rule_type=body.rule_type,
        escalation_level="none",
        generated_by="Scheduler",
        is_canonical=True,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {"data": _task_dict(task), "meta": _meta()}


@router.get("/api/v1/followups/{task_id}")
def get_followup(
    task_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve a single follow-up task by ID."""
    task = _get_task_or_404(task_id, claims.tenant_id, db)
    return {"data": _task_dict(task), "meta": _meta()}


@router.patch("/api/v1/followups/{task_id}/complete")
def complete_followup(
    task_id: str,
    body: CompleteFollowupRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Mark a follow-up as completed."""
    task = _get_task_or_404(task_id, claims.tenant_id, db)
    if task.state == "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Follow-up is already completed",
        )

    task.state = "completed"
    task.completed_at = datetime.now(timezone.utc)
    task.completed_activity_id = body.completed_activity_id
    db.commit()
    db.refresh(task)

    return {"data": _task_dict(task), "meta": _meta()}


@router.post("/api/v1/followups/{task_id}/escalate", status_code=status.HTTP_201_CREATED)
def escalate_followup(
    task_id: str,
    body: EscalateFollowupRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Manually escalate a follow-up task. Requires manager or admin role."""
    _require_manager(claims)
    if body.escalation_level not in _VALID_ESCALATION_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"escalation_level must be one of {sorted(_VALID_ESCALATION_LEVELS)}",
        )

    task = _get_task_or_404(task_id, claims.tenant_id, db)
    if task.state == "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot escalate a completed follow-up",
        )

    escalation = FollowupEscalation(
        escalation_id=str(uuid.uuid4()),
        tenant_id=claims.tenant_id,
        lead_id=task.lead_id,
        task_id=task_id,
        escalation_level=body.escalation_level,
        owner_id=task.owner_id,
        reason=body.reason,
        generated_at=datetime.now(timezone.utc),
    )
    task.escalation_level = body.escalation_level
    db.add(escalation)
    db.commit()
    db.refresh(task)
    db.refresh(escalation)

    return {
        "data": {
            "task": _task_dict(task),
            "escalation": {
                "escalation_id": escalation.escalation_id,
                "escalation_level": escalation.escalation_level,
                "reason": escalation.reason,
                "generated_at": escalation.generated_at.isoformat(),
            },
        },
        "meta": _meta(),
    }
