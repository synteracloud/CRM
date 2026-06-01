"""Public REST endpoints for Territory Management.

Spec: backend/docs/domain/territory-management.md §7
API standards: backend/docs/api-standards.md

Routes:
    GET    /api/v1/territories
    POST   /api/v1/territories
    GET    /api/v1/territories/{territory_id}
    PATCH  /api/v1/territories/{territory_id}
    DELETE /api/v1/territories/{territory_id}
    POST   /api/v1/territories/{territory_id}/rules
    POST   /api/v1/territories/assignments/evaluate
    GET    /api/v1/territories/{territory_id}/performance
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.models.territories import Territory, TerritoryRule
from services.territories.entities import TerritoryCriteriaType, TerritoryRuleType
from services.territories.service import TerritoriesService

router = APIRouter(tags=["territories"])

_svc = TerritoriesService()

VALID_CRITERIA_TYPES = {t.value for t in TerritoryCriteriaType}
VALID_RULE_TYPES = {t.value for t in TerritoryRuleType}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


def _territory_dict(t: Territory, rules: list[TerritoryRule] | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {
        "territory_id":    t.territory_id,
        "tenant_id":       t.tenant_id,
        "name":            t.name,
        "description":     t.description,
        "parent_id":       t.parent_id,
        "criteria_type":   t.criteria_type,
        "criteria_value":  t.criteria_value,
        "assigned_reps":   t.assigned_reps,
        "primary_manager": t.primary_manager,
        "is_default":      t.is_default,
        "is_active":       t.is_active,
        "routing_priority": t.routing_priority,
        "created_by":      t.created_by,
        "created_at":      t.created_at.isoformat() if t.created_at else None,
        "updated_at":      t.updated_at.isoformat() if t.updated_at else None,
    }
    if rules is not None:
        d["rules"] = [_rule_dict(r) for r in rules]
    return d


def _rule_dict(r: TerritoryRule) -> dict[str, Any]:
    return {
        "rule_id":      r.rule_id,
        "territory_id": r.territory_id,
        "rule_type":    r.rule_type,
        "field":        r.field,
        "operator":     r.operator,
        "value":        r.value,
        "created_at":   r.created_at.isoformat() if r.created_at else None,
    }


def _get_territory_or_404(territory_id: str, tenant_id: str, db: Session) -> Territory:
    t = db.get(Territory, territory_id)
    if t is None or t.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territory not found")
    return t


# ── Request schemas ───────────────────────────────────────────────────────────

class CreateTerritoryRequest(BaseModel):
    name: str
    criteria_type: str
    description: Optional[str] = None
    criteria_value: dict = {}
    assigned_reps: list = []
    primary_manager: Optional[str] = None
    is_default: bool = False
    routing_priority: int = 99


class UpdateTerritoryRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    criteria_type: Optional[str] = None
    criteria_value: Optional[dict] = None
    assigned_reps: Optional[list] = None
    primary_manager: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    routing_priority: Optional[int] = None


class AddRuleRequest(BaseModel):
    rule_type: str
    field: Optional[str] = None
    operator: Optional[str] = None
    value: dict = {}


class EvaluateAssignmentRequest(BaseModel):
    subject: dict


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/api/v1/territories")
def list_territories(
    is_active: Optional[bool] = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(Territory).where(Territory.tenant_id == claims.tenant_id)
    if is_active is not None:
        q = q.where(Territory.is_active == is_active)
    q = q.order_by(Territory.routing_priority)
    rows = db.execute(q).scalars().all()
    return {"data": [_territory_dict(t) for t in rows], "meta": _meta()}


@router.post("/api/v1/territories", status_code=status.HTTP_201_CREATED)
def create_territory(
    body: CreateTerritoryRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if body.criteria_type not in VALID_CRITERIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"criteria_type must be one of {sorted(VALID_CRITERIA_TYPES)}",
        )

    now = datetime.now(timezone.utc)

    # If new territory is default, unset the existing default
    if body.is_default:
        existing_default = db.execute(
            select(Territory).where(
                Territory.tenant_id == claims.tenant_id,
                Territory.is_default.is_(True),
            )
        ).scalar_one_or_none()
        if existing_default:
            existing_default.is_default = False
            existing_default.updated_at = now
            db.flush()

    t = Territory(
        territory_id=str(uuid.uuid4()),
        tenant_id=claims.tenant_id,
        name=body.name,
        description=body.description,
        criteria_type=body.criteria_type,
        criteria_value=body.criteria_value,
        assigned_reps=body.assigned_reps,
        primary_manager=body.primary_manager,
        is_default=body.is_default,
        is_active=True,
        routing_priority=body.routing_priority,
        created_by=claims.sub,
        created_at=now,
        updated_at=now,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"data": _territory_dict(t), "meta": _meta()}


@router.get("/api/v1/territories/assignments/evaluate")
def evaluate_assignment_get(
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    # Placeholder to avoid 404 on GET — actual evaluation is POST
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Use POST")


@router.post("/api/v1/territories/assignments/evaluate")
def evaluate_assignment(
    body: EvaluateAssignmentRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    # Load all active territories for this tenant
    territories = db.execute(
        select(Territory).where(
            Territory.tenant_id == claims.tenant_id,
            Territory.is_active.is_(True),
        ).order_by(Territory.routing_priority)
    ).scalars().all()

    # Load all rules grouped by territory_id
    rules_rows = db.execute(
        select(TerritoryRule).where(TerritoryRule.tenant_id == claims.tenant_id)
    ).scalars().all()
    rules_by_territory: dict[str, list[dict]] = {}
    for r in rules_rows:
        rules_by_territory.setdefault(r.territory_id, []).append(_rule_dict(r))

    territory_dicts = [_territory_dict(t) for t in territories]
    candidates = _svc.evaluate_subject(body.subject, territory_dicts, rules_by_territory)
    winner, reason = _svc.select_winner(candidates, rules_by_territory)

    # If no match, fall back to default territory
    if winner is None:
        default_t = db.execute(
            select(Territory).where(
                Territory.tenant_id == claims.tenant_id,
                Territory.is_default.is_(True),
            )
        ).scalar_one_or_none()
        if default_t:
            winner = _territory_dict(default_t)
            reason = "default_fallback"

    return {
        "data": {
            "winner":     winner,
            "candidates": candidates,
            "reason":     reason,
        },
        "meta": _meta(),
    }


@router.get("/api/v1/territories/{territory_id}/performance")
def get_performance(
    territory_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _get_territory_or_404(territory_id, claims.tenant_id, db)
    # Return stub metrics (no live performance data tables yet)
    return {
        "data": {
            "territory_id":    territory_id,
            "open_leads":      0,
            "closed_leads":    0,
            "conversion_rate": 0.0,
            "collection_rate": 0.0,
            "total_revenue":   0.0,
            "avg_deal_size":   0.0,
        },
        "meta": _meta(),
    }


@router.get("/api/v1/territories/{territory_id}")
def get_territory(
    territory_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    t = _get_territory_or_404(territory_id, claims.tenant_id, db)
    rules = db.execute(
        select(TerritoryRule).where(TerritoryRule.territory_id == territory_id)
    ).scalars().all()
    return {"data": _territory_dict(t, list(rules)), "meta": _meta()}


@router.patch("/api/v1/territories/{territory_id}")
def update_territory(
    territory_id: str,
    body: UpdateTerritoryRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    t = _get_territory_or_404(territory_id, claims.tenant_id, db)

    if body.criteria_type is not None and body.criteria_type not in VALID_CRITERIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"criteria_type must be one of {sorted(VALID_CRITERIA_TYPES)}",
        )

    now = datetime.now(timezone.utc)

    # If setting as default, unset existing default
    if body.is_default is True:
        existing_default = db.execute(
            select(Territory).where(
                Territory.tenant_id == claims.tenant_id,
                Territory.is_default.is_(True),
                Territory.territory_id != territory_id,
            )
        ).scalar_one_or_none()
        if existing_default:
            existing_default.is_default = False
            existing_default.updated_at = now
            db.flush()

    if body.name is not None:
        t.name = body.name
    if body.description is not None:
        t.description = body.description
    if body.criteria_type is not None:
        t.criteria_type = body.criteria_type
    if body.criteria_value is not None:
        t.criteria_value = body.criteria_value
    if body.assigned_reps is not None:
        t.assigned_reps = body.assigned_reps
    if body.primary_manager is not None:
        t.primary_manager = body.primary_manager
    if body.is_default is not None:
        t.is_default = body.is_default
    if body.is_active is not None:
        t.is_active = body.is_active
    if body.routing_priority is not None:
        t.routing_priority = body.routing_priority
    t.updated_at = now

    db.commit()
    db.refresh(t)
    return {"data": _territory_dict(t), "meta": _meta()}


@router.delete("/api/v1/territories/{territory_id}")
def deactivate_territory(
    territory_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    t = _get_territory_or_404(territory_id, claims.tenant_id, db)
    if t.is_default:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate the default territory",
        )
    t.is_active = False
    t.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"data": {"deactivated": True, "territory_id": territory_id}, "meta": _meta()}


@router.post("/api/v1/territories/{territory_id}/rules", status_code=status.HTTP_201_CREATED)
def add_rule(
    territory_id: str,
    body: AddRuleRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _get_territory_or_404(territory_id, claims.tenant_id, db)

    if body.rule_type not in VALID_RULE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"rule_type must be one of {sorted(VALID_RULE_TYPES)}",
        )

    now = datetime.now(timezone.utc)
    rule = TerritoryRule(
        rule_id=str(uuid.uuid4()),
        territory_id=territory_id,
        tenant_id=claims.tenant_id,
        rule_type=body.rule_type,
        field=body.field,
        operator=body.operator,
        value=body.value,
        created_at=now,
        updated_at=now,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"data": _rule_dict(rule), "meta": _meta()}
