"""Public REST endpoints for activity logging and audit chain integrity.

Spec: backend/docs/activity-control-model.md
      backend/docs/observability-audit.md
API standards: backend/docs/api-standards.md

Routes:
    POST /api/v1/activities                  — log an activity event (JWT)
    GET  /api/v1/activities                  — list activity feed for tenant (JWT)
    GET  /api/v1/activities/chain-integrity  — verify audit chain integrity (JWT)
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from services.activity.engine import ActivityControlEngine
from services.activity.entities import ActorContext, EntityRecord
from services.auth.jwt_deps import TokenClaims, get_current_user

router = APIRouter(tags=["activities"])

_engine = ActivityControlEngine()


def set_engine(eng: ActivityControlEngine) -> None:
    global _engine  # noqa: PLW0603
    _engine = eng


def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


# ── Request schemas ───────────────────────────────────────────────────────────


class LogActivityRequest(BaseModel):
    entity_type: str              # "lead" or "deal"
    entity_id: str
    owner_id: str
    action: str
    changes: dict[str, Any] = {}  # optional field mutations


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/api/v1/activities", status_code=status.HTTP_201_CREATED)
def log_activity(
    body: LogActivityRequest,
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Register or mutate an entity, producing an immutable activity event.

    If the entity does not exist it is registered (first-ever activity).
    If it already exists and changes are provided, a mutation event is recorded.
    """
    request_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())
    actor = ActorContext(
        actor_id=claims.sub,
        actor_name=claims.sub,
        actor_role=claims.role,
    )
    entity_key = (body.entity_type, body.entity_id)

    if entity_key not in _engine._entities:
        entity = EntityRecord(
            tenant_id=claims.tenant_id,
            entity_type=body.entity_type,
            entity_id=body.entity_id,
            owner_id=body.owner_id,
        )
        try:
            _engine.register_entity(entity, actor, request_id=request_id, trace_id=trace_id)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    elif body.changes:
        try:
            _engine.mutate_entity(
                entity_type=body.entity_type,
                entity_id=body.entity_id,
                actor=actor,
                changes=body.changes,
                request_id=request_id,
                trace_id=trace_id,
            )
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    # Return the most recently recorded activity event for this entity
    feed = _engine.activity_feed(claims.tenant_id, limit=1)
    latest = feed[0] if feed else None
    return {
        "data": {
            "event_id": latest.event_id if latest else request_id,
            "entity_type": body.entity_type,
            "entity_id": body.entity_id,
            "action": latest.action if latest else body.action,
            "result": latest.result if latest else "success",
            "tenant_id": claims.tenant_id,
        },
        "meta": _meta(),
    }


@router.get("/api/v1/activities")
def list_activities(
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Return the activity feed for the authenticated tenant (newest-first, up to 500)."""
    feed = _engine.activity_feed(claims.tenant_id)
    events = [
        {
            "event_id": e.event_id,
            "entity_type": e.entity_type,
            "entity_id": e.entity_id,
            "actor_id": e.actor_id,
            "action": e.action,
            "result": e.result,
            "event_ts": e.event_ts,
        }
        for e in feed
    ]
    return {"data": events, "meta": _meta(total=len(events))}


@router.get("/api/v1/activities/chain-integrity")
def chain_integrity(
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Verify the audit log hash chain is unbroken for the authenticated tenant."""
    result = _engine.verify_chain_integrity(claims.tenant_id)
    return {"data": result, "meta": _meta()}
