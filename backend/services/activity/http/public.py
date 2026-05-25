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
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.activity.engine import ActivityControlEngine
from services.activity.entities import ActorContext, EntityRecord
from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.models.activity import Activity

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
    db: Session = Depends(get_db),
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
    event_id = latest.event_id if latest else request_id
    event_type = latest.action if latest else body.action
    event_ts_str = latest.event_ts if latest else datetime.now(timezone.utc).isoformat()

    # Persist to activities table
    try:
        event_time = datetime.fromisoformat(event_ts_str.rstrip("Z"))
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
    except ValueError:
        event_time = datetime.now(timezone.utc)

    db_activity = Activity(
        activity_id=event_id,
        tenant_id=claims.tenant_id,
        actor_user_id=claims.sub,
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        event_type=event_type,
        event_time=event_time,
        payload_json={"action": event_type, "changes": body.changes, "owner_id": body.owner_id},
        source_service="activity-control-engine",
    )
    db.merge(db_activity)
    db.commit()

    return {
        "data": {
            "event_id": event_id,
            "entity_type": body.entity_type,
            "entity_id": body.entity_id,
            "action": event_type,
            "result": latest.result if latest else "success",
            "tenant_id": claims.tenant_id,
        },
        "meta": _meta(),
    }


@router.get("/api/v1/activities")
def list_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    entity_id: str | None = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return the activity feed for the authenticated tenant from DB (newest-first)."""
    q = (
        select(Activity)
        .where(Activity.tenant_id == claims.tenant_id)
        .order_by(Activity.event_time.desc())
    )
    if entity_id:
        q = q.where(Activity.entity_id == entity_id)

    offset = (page - 1) * page_size
    rows = db.execute(q.offset(offset).limit(page_size)).scalars().all()

    events = [
        {
            "event_id": r.activity_id,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "actor_id": r.actor_user_id,
            "action": r.event_type,
            "event_ts": r.event_time.isoformat() if r.event_time else None,
            "payload": r.payload_json,
        }
        for r in rows
    ]
    import math
    # total_count not tracked separately here — len(events) is the page count, not global total
    # Use count query for accurate total_items
    from sqlalchemy import func as _func
    count_q = select(_func.count()).select_from(Activity).where(Activity.tenant_id == claims.tenant_id)
    if entity_id:
        count_q = count_q.where(Activity.entity_id == entity_id)
    total_count = db.execute(count_q).scalar_one()
    total_pages = math.ceil(total_count / page_size) if page_size else 1
    return {"data": events, "meta": _meta(total_items=total_count, total_pages=total_pages, page=page, page_size=page_size)}


@router.get("/api/v1/activities/chain-integrity")
def chain_integrity(
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Verify the audit log hash chain is unbroken for the authenticated tenant."""
    result = _engine.verify_chain_integrity(claims.tenant_id)
    return {"data": result, "meta": _meta()}
