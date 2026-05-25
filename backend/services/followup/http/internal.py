"""Follow-up service internal HTTP endpoints.

Docs: docs/followup-enforcement-model.md §2.D — Next Action Suggestion
      gateway/routes/v1-leads.routes.js — GET /:id/next-action (gateway consumer)

These routes are NOT exposed to end-users.  The gateway calls them over a
trusted internal network.

Mount point (wired in services/app.py — P-019)::
    app.include_router(internal_router, prefix="/internal")

Engine lifecycle:
    The _engine singleton is the authoritative in-memory instance.
    P-019 will wire the shared instance via set_engine() at app startup
    (same pattern as services/activity/http/internal.py).
"""

from __future__ import annotations

import uuid as _uuid_mod
from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from services.db import get_db
from services.db.models.followup import FollowupTask as FollowupTaskORM, FollowupEscalation as FollowupEscalationORM
from services.db.models.lead import Lead
from services.followup.engine import FollowupEnforcementEngine, FollowupPolicyError
from services.followup.entities import EscalationLevel, FollowupState, FollowupTask as FollowupTaskEntity, LeadSnapshot

router = APIRouter(tags=["internal"])

# Module-level engine singleton — replaced at startup via set_engine().
_engine = FollowupEnforcementEngine()


def set_engine(engine: FollowupEnforcementEngine) -> None:
    """Override the default engine singleton.  Called once at service startup."""
    global _engine  # noqa: PLW0603
    _engine = engine


# ── DB ↔ entity converters ────────────────────────────────────────────────────

def _orm_to_entity(row: FollowupTaskORM) -> FollowupTaskEntity:
    return FollowupTaskEntity(
        task_id=row.task_id,
        lead_id=row.lead_id,
        tenant_id=row.tenant_id,
        owner_id=row.owner_id,
        state=FollowupState(row.state),
        due_at=row.due_at,
        created_at=row.created_at,
        rule_type=row.rule_type,
        escalation_level=EscalationLevel(row.escalation_level),
        generated_by=row.generated_by,
        completed_at=row.completed_at,
        completed_activity_id=row.completed_activity_id,
        is_canonical=row.is_canonical,
    )


def _lead_orm_to_snapshot(lead: Lead) -> LeadSnapshot:
    return LeadSnapshot(
        lead_id=lead.lead_id,
        tenant_id=lead.tenant_id,
        owner_id=lead.owner_id,
        status=lead.status,
        priority=lead.priority,
        stage=lead.stage,
        last_activity_at=lead.last_activity_at or lead.created_at or datetime.now(timezone.utc),
    )


def _hydrate_lead_from_db(lead_id: str, db: Session) -> None:
    """Load lead snapshot + tasks from DB into engine if not already present."""
    if _engine.has_lead(lead_id):
        return
    lead_row = db.get(Lead, lead_id)
    if lead_row is None:
        return
    task_rows = db.execute(
        select(FollowupTaskORM).where(FollowupTaskORM.lead_id == lead_id)
    ).scalars().all()
    _engine.hydrate_lead(
        _lead_orm_to_snapshot(lead_row),
        [_orm_to_entity(r) for r in task_rows],
    )


# ── GET /internal/leads/:lead_id/next-action ─────────────────────────────────
@router.get("/leads/{lead_id}/next-action")
def suggest_next_action(
    lead_id: str,
    now: str | None = Query(default=None, description="ISO-8601 override for 'now' (testing only)"),
    db: Session = Depends(get_db),
) -> dict:
    """Return the highest-priority next action for a lead.

    Called by gateway/routes/v1-leads.routes.js GET /leads/:id/next-action.

    Response contract (NextActionSuggestion)::
        {
          "lead_id": str,
          "suggested_action": "call" | "send_whatsapp" | "send_reminder" | "escalate" | "close",
          "reason": str,
          "priority": "urgent" | "high" | "normal",
          "due_by": ISO-8601 datetime
        }

    Docs: docs/followup-enforcement-model.md §2.D
    """
    if not lead_id.strip():
        raise HTTPException(status_code=400, detail="lead_id is required")

    now_dt: datetime | None = None
    if now:
        try:
            now_dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="now must be a valid ISO-8601 datetime")

    _hydrate_lead_from_db(lead_id, db)

    try:
        suggestion = _engine.suggest_next_action(lead_id, now=now_dt)
    except FollowupPolicyError as exc:
        if "LEAD_NOT_FOUND" in str(exc):
            raise HTTPException(status_code=404, detail=f"Lead not found: {lead_id}")
        raise HTTPException(status_code=422, detail=str(exc))

    result = asdict(suggestion)
    # due_by is a datetime — serialise to ISO-8601 for the JSON response
    if isinstance(result.get("due_by"), datetime):
        result["due_by"] = result["due_by"].isoformat()

    return result


# ── POST /internal/leads/{lead_id}/register ───────────────────────────────────
class RegisterLeadRequest(BaseModel):
    """Minimal lead snapshot to seed the enforcement engine."""
    tenant_id:        str
    owner_id:         str
    status:           str = "open"
    priority:         str = "warm"
    stage:            str = "new"
    last_activity_at: str | None = None   # ISO-8601; defaults to now


@router.post("/leads/{lead_id}/register")
def register_lead(lead_id: str, body: RegisterLeadRequest, db: Session = Depends(get_db)) -> dict:
    """Register a lead in the enforcement engine so it is tracked for follow-up.

    Called by gateway/routes/v1-leads.routes.js after a lead is created (P-020).

    Response::
        { "task_id": str, "due_at": str }

    Docs: docs/followup-enforcement-model.md §1 — every active lead must have
    a pending task within the SLA window.
    """
    if not lead_id.strip():
        raise HTTPException(status_code=400, detail="lead_id is required")

    now_dt: datetime | None = None
    if body.last_activity_at:
        try:
            now_dt = datetime.fromisoformat(body.last_activity_at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="last_activity_at must be ISO-8601")

    snapshot = LeadSnapshot(
        lead_id=lead_id,
        tenant_id=body.tenant_id,
        owner_id=body.owner_id,
        status=body.status,
        priority=body.priority,
        stage=body.stage,
        last_activity_at=now_dt or datetime.now(timezone.utc),
    )

    try:
        task = _engine.register_lead(snapshot, now=now_dt)
    except FollowupPolicyError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Persist task to DB (upsert — safe if called more than once for same task_id)
    db_task = FollowupTaskORM(
        task_id=task.task_id,
        tenant_id=task.tenant_id,
        lead_id=task.lead_id,
        owner_id=task.owner_id,
        state=task.state.value,
        due_at=task.due_at,
        created_at=task.created_at,
        rule_type=task.rule_type,
        escalation_level=task.escalation_level.value,
        generated_by=task.generated_by,
        is_canonical=task.is_canonical,
    )
    db.merge(db_task)
    db.commit()

    return {
        "lead_id": lead_id,
        "task_id": task.task_id,
        "due_at":  task.due_at.isoformat(),
        "state":   task.state.value,
    }


# ── POST /internal/process-due ────────────────────────────────────────────────
@router.post("/process-due")
def process_due(
    now: str | None = Query(default=None, description="ISO-8601 override for 'now' (testing only)"),
    db: Session = Depends(get_db),
) -> dict:
    """Process overdue task transitions and fire escalation events.

    Intended to be called by a cron job (e.g. every 15 minutes) or the
    gateway scheduler.  Returns all escalation events generated in this run.

    Docs: docs/followup-enforcement-model.md §2.C — Escalation Pipeline
    """
    now_dt: datetime | None = None
    if now:
        try:
            now_dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="now must be a valid ISO-8601 datetime")

    # Hydrate engine from DB — load all active leads whose tasks are in the engine's scope
    active_lead_ids = db.execute(
        select(FollowupTaskORM.lead_id).where(
            FollowupTaskORM.state.in_(["pending", "overdue"])
        ).distinct()
    ).scalars().all()
    for lid in active_lead_ids:
        _hydrate_lead_from_db(lid, db)

    events = _engine.process_due_transitions(now=now_dt)

    # Persist escalation records and task state changes
    if events:
        task_tenant: dict[str, str] = {}
        for event in events:
            if event.task_id not in task_tenant:
                db_task = db.get(FollowupTaskORM, event.task_id)
                if db_task:
                    task_tenant[event.task_id] = db_task.tenant_id
                    db_task.escalation_level = event.level.value
                    if db_task.state == "pending":
                        db_task.state = "overdue"

            esc = FollowupEscalationORM(
                escalation_id=str(_uuid_mod.uuid4()),
                tenant_id=task_tenant.get(event.task_id, ""),
                lead_id=event.lead_id,
                task_id=event.task_id,
                escalation_level=event.level.value,
                owner_id=event.owner_id,
                reason=event.reason,
                generated_at=event.generated_at,
            )
            db.add(esc)
        db.commit()

    return {
        "escalation_events": [
            {
                "lead_id":      e.lead_id,
                "task_id":      e.task_id,
                "level":        e.level.value,
                "owner_id":     e.owner_id,
                "reason":       e.reason,
                "generated_at": e.generated_at.isoformat(),
            }
            for e in events
        ],
        "count": len(events),
    }


# ── GET /internal/metrics ─────────────────────────────────────────────────────
@router.get("/metrics")
def metrics(db: Session = Depends(get_db)) -> dict:
    """Return compliance metrics computed from the DB (authoritative across restarts).

    Response::
        { "compliance_percent", "overdue_percent", "required_followups" }
    """
    _required_sources = ("Scheduler", "EscalationEngine", "SystemRepair")

    total_q = select(func.count()).select_from(FollowupTaskORM).where(
        FollowupTaskORM.generated_by.in_(_required_sources)
    )
    total = db.execute(total_q).scalar_one() or 0

    if total == 0:
        return {"compliance_percent": 100.0, "overdue_percent": 0.0, "required_followups": 0}

    completed_on_time = db.execute(
        select(func.count()).select_from(FollowupTaskORM).where(
            FollowupTaskORM.generated_by.in_(_required_sources),
            FollowupTaskORM.state == "completed",
            FollowupTaskORM.completed_at <= FollowupTaskORM.due_at,
        )
    ).scalar_one() or 0

    overdue_count = db.execute(
        select(func.count()).select_from(FollowupTaskORM).where(
            FollowupTaskORM.generated_by.in_(_required_sources),
            FollowupTaskORM.state == "overdue",
        )
    ).scalar_one() or 0

    return {
        "compliance_percent": round((completed_on_time / total) * 100, 2),
        "overdue_percent":    round((overdue_count / total) * 100, 2),
        "required_followups": total,
    }
