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

from dataclasses import asdict
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.followup.engine import FollowupEnforcementEngine, FollowupPolicyError
from services.followup.entities import LeadSnapshot

router = APIRouter(tags=["internal"])

# Module-level engine singleton — replaced at startup via set_engine().
_engine = FollowupEnforcementEngine()


def set_engine(engine: FollowupEnforcementEngine) -> None:
    """Override the default engine singleton.  Called once at service startup."""
    global _engine  # noqa: PLW0603
    _engine = engine


# ── GET /internal/leads/:lead_id/next-action ─────────────────────────────────
@router.get("/leads/{lead_id}/next-action")
def suggest_next_action(
    lead_id: str,
    now: str | None = Query(default=None, description="ISO-8601 override for 'now' (testing only)"),
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
def register_lead(lead_id: str, body: RegisterLeadRequest) -> dict:
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
        last_activity_at=now_dt or datetime.utcnow(),
    )

    try:
        task = _engine.register_lead(snapshot, now=now_dt)
    except FollowupPolicyError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

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

    events = _engine.process_due_transitions(now=now_dt)

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
def metrics() -> dict:
    """Return compliance metrics for the follow-up enforcement engine.

    Response::
        { "compliance_percent", "overdue_percent", "required_followups" }
    """
    m = _engine.metrics()
    return {
        "compliance_percent": m.compliance_percent,
        "overdue_percent":    m.overdue_percent,
        "required_followups": m.required_followups,
    }
