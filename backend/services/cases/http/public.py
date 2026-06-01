"""Public REST endpoints for Case Management domain.

Spec: backend/docs/domain/cases-domain.md §8
API standards: backend/docs/api-standards.md

Routes:
    POST   /api/v1/cases
    GET    /api/v1/cases
    GET    /api/v1/cases/{case_id}
    POST   /api/v1/cases/{case_id}/assign
    POST   /api/v1/cases/{case_id}/comments
    POST   /api/v1/cases/{case_id}/resolve
    POST   /api/v1/cases/{case_id}/escalate
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.models.cases import Case, CaseComment, CaseEscalation
from services.cases.entities import (
    CasePriority,
    CaseTransitionError,
    SLATier,
    SLA_DEFAULTS,
    ALLOWED_TRANSITIONS,
    compute_sla_deadline,
    validate_transition,
)

router = APIRouter(tags=["cases"])

VALID_PRIORITIES = {p.value for p in CasePriority}
VALID_SOURCES = {"whatsapp", "web_form", "email", "phone", "internal"}
VALID_SLA_TIERS = {t.value for t in SLATier}
VALID_COMMENT_TYPES = {"internal_note", "customer_reply", "resolution", "status_change", "escalation_note"}
VALID_ESCALATION_REASONS = {
    "sla_first_response_breach", "sla_resolution_breach",
    "customer_request", "manager_override",
}

_CASE_COUNTER = 0  # fallback; each tenant sequence is approximate


def _next_case_number(db: Session, tenant_id: str) -> str:
    count = db.execute(
        select(func.count()).select_from(Case).where(Case.tenant_id == tenant_id)
    ).scalar_one()
    return f"CAS-{count + 1:05d}"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


def _case_dict(c: Case) -> dict[str, Any]:
    return {
        "case_id":                   c.case_id,
        "tenant_id":                 c.tenant_id,
        "case_number":               c.case_number,
        "subject":                   c.subject,
        "description":               c.description,
        "status":                    c.status,
        "priority":                  c.priority,
        "source":                    c.source,
        "category":                  c.category,
        "contact_id":                c.contact_id,
        "account_id":                c.account_id,
        "lead_id":                   c.lead_id,
        "assigned_to":               c.assigned_to,
        "assigned_team_id":          c.assigned_team_id,
        "queue_id":                  c.queue_id,
        "sla_tier":                  c.sla_tier,
        "sla_first_response_due_at": c.sla_first_response_due_at.isoformat() if c.sla_first_response_due_at else None,
        "sla_resolution_due_at":     c.sla_resolution_due_at.isoformat() if c.sla_resolution_due_at else None,
        "first_responded_at":        c.first_responded_at.isoformat() if c.first_responded_at else None,
        "resolved_at":               c.resolved_at.isoformat() if c.resolved_at else None,
        "resolution_confirmed_at":   c.resolution_confirmed_at.isoformat() if c.resolution_confirmed_at else None,
        "closed_at":                 c.closed_at.isoformat() if c.closed_at else None,
        "reopened_at":               c.reopened_at.isoformat() if c.reopened_at else None,
        "reopen_count":              c.reopen_count,
        "escalation_level":          c.escalation_level,
        "tags":                      c.tags,
        "custom_fields":             c.custom_fields,
        "version_no":                c.version_no,
        "created_at":                c.created_at.isoformat() if c.created_at else None,
        "updated_at":                c.updated_at.isoformat() if c.updated_at else None,
        "created_by":                c.created_by,
        "updated_by":                c.updated_by,
    }


def _comment_dict(c: CaseComment) -> dict[str, Any]:
    return {
        "comment_id":             c.comment_id,
        "case_id":                c.case_id,
        "tenant_id":              c.tenant_id,
        "comment_type":           c.comment_type,
        "body":                   c.body,
        "author_id":              c.author_id,
        "is_visible_to_customer": c.is_visible_to_customer,
        "attachment_urls":        c.attachment_urls,
        "created_at":             c.created_at.isoformat() if c.created_at else None,
        "updated_at":             c.updated_at.isoformat() if c.updated_at else None,
    }


def _get_case_or_404(case_id: str, tenant_id: str, db: Session) -> Case:
    row = db.execute(
        select(Case).where(
            Case.case_id == case_id,
            Case.tenant_id == tenant_id,
        )
    ).scalars().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return row


def _compute_sla_deadlines(sla_tier: str, now: datetime) -> tuple[Optional[datetime], Optional[datetime]]:
    try:
        tier_enum = SLATier(sla_tier)
    except ValueError:
        tier_enum = SLATier.TIER_3_STANDARD
    defaults = SLA_DEFAULTS[tier_enum]
    first_response_due = compute_sla_deadline(now, defaults["first_response_hours"])
    resolution_due = compute_sla_deadline(now, defaults["resolution_hours"])
    return first_response_due, resolution_due


# ── Request schemas ───────────────────────────────────────────────────────────

class CreateCaseRequest(BaseModel):
    subject: str
    priority: str = "medium"
    source: str = "web_form"
    description: Optional[str] = None
    category: Optional[str] = None
    contact_id: Optional[str] = None
    account_id: Optional[str] = None
    lead_id: Optional[str] = None
    sla_tier: str = "tier_3_standard"

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}")
        return v

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v not in VALID_SOURCES:
            raise ValueError(f"source must be one of {sorted(VALID_SOURCES)}")
        return v


class AssignCaseRequest(BaseModel):
    assigned_to: str


class AddCommentRequest(BaseModel):
    body: str
    comment_type: str
    attachment_urls: list = []

    @field_validator("comment_type")
    @classmethod
    def validate_comment_type(cls, v: str) -> str:
        if v not in VALID_COMMENT_TYPES:
            raise ValueError(f"comment_type must be one of {sorted(VALID_COMMENT_TYPES)}")
        return v


class ResolveCaseRequest(BaseModel):
    resolution_note: str


class EscalateCaseRequest(BaseModel):
    escalation_reason: str
    note: Optional[str] = None
    escalated_to: Optional[str] = None

    @field_validator("escalation_reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if v not in VALID_ESCALATION_REASONS:
            raise ValueError(f"escalation_reason must be one of {sorted(VALID_ESCALATION_REASONS)}")
        return v


# ── Case Endpoints ─────────────────────────────────────────────────────────────

@router.post("/api/v1/cases", status_code=status.HTTP_201_CREATED)
def create_case(
    body: CreateCaseRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    case_number = _next_case_number(db, claims.tenant_id)
    first_response_due, resolution_due = _compute_sla_deadlines(body.sla_tier, now)

    c = Case(
        case_id=str(uuid.uuid4()),
        tenant_id=claims.tenant_id,
        case_number=case_number,
        subject=body.subject,
        description=body.description,
        status="OPEN",
        priority=body.priority,
        source=body.source,
        category=body.category,
        contact_id=body.contact_id,
        account_id=body.account_id,
        lead_id=body.lead_id,
        sla_tier=body.sla_tier,
        sla_first_response_due_at=first_response_due,
        sla_resolution_due_at=resolution_due,
        escalation_level=0,
        reopen_count=0,
        tags=[],
        custom_fields={},
        version_no=1,
        created_by=claims.sub,
        updated_by=claims.sub,
        created_at=now,
        updated_at=now,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"data": _case_dict(c), "meta": _meta()}


@router.get("/api/v1/cases")
def list_cases(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(Case).where(Case.tenant_id == claims.tenant_id)
    if status is not None:
        q = q.where(Case.status == status)
    if priority is not None:
        q = q.where(Case.priority == priority)
    q = q.order_by(Case.created_at.desc())
    rows = db.execute(q).scalars().all()
    return {"data": [_case_dict(r) for r in rows], "meta": _meta()}


@router.get("/api/v1/cases/{case_id}")
def get_case(
    case_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_case_or_404(case_id, claims.tenant_id, db)
    return {"data": _case_dict(c), "meta": _meta()}


@router.post("/api/v1/cases/{case_id}/assign")
def assign_case(
    case_id: str,
    body: AssignCaseRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_case_or_404(case_id, claims.tenant_id, db)
    try:
        validate_transition(c.status, "ASSIGNED")
    except CaseTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    now = datetime.now(timezone.utc)
    c.assigned_to = body.assigned_to
    c.status = "ASSIGNED"
    c.updated_by = claims.sub
    c.updated_at = now
    c.version_no += 1
    db.commit()
    db.refresh(c)
    return {"data": _case_dict(c), "meta": _meta()}


@router.post("/api/v1/cases/{case_id}/comments", status_code=status.HTTP_201_CREATED)
def add_comment(
    case_id: str,
    body: AddCommentRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_case_or_404(case_id, claims.tenant_id, db)
    now = datetime.now(timezone.utc)

    # Transition to IN_PROGRESS if currently ASSIGNED and comment is customer_reply
    if c.status == "ASSIGNED" and body.comment_type == "customer_reply":
        c.status = "IN_PROGRESS"
        if c.first_responded_at is None:
            c.first_responded_at = now
        c.updated_by = claims.sub
        c.updated_at = now
        c.version_no += 1

    is_visible = body.comment_type in ("customer_reply", "resolution")
    comment = CaseComment(
        comment_id=str(uuid.uuid4()),
        case_id=case_id,
        tenant_id=claims.tenant_id,
        comment_type=body.comment_type,
        body=body.body,
        author_id=claims.sub,
        is_visible_to_customer=is_visible,
        attachment_urls=body.attachment_urls,
        created_at=now,
        updated_at=now,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"data": _comment_dict(comment), "meta": _meta()}


@router.post("/api/v1/cases/{case_id}/resolve")
def resolve_case(
    case_id: str,
    body: ResolveCaseRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_case_or_404(case_id, claims.tenant_id, db)
    try:
        validate_transition(c.status, "RESOLVED")
    except CaseTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    now = datetime.now(timezone.utc)
    c.status = "RESOLVED"
    c.resolved_at = now
    c.updated_by = claims.sub
    c.updated_at = now
    c.version_no += 1
    # Add resolution comment
    comment = CaseComment(
        comment_id=str(uuid.uuid4()),
        case_id=case_id,
        tenant_id=claims.tenant_id,
        comment_type="resolution",
        body=body.resolution_note,
        author_id=claims.sub,
        is_visible_to_customer=True,
        attachment_urls=[],
        created_at=now,
        updated_at=now,
    )
    db.add(comment)
    db.commit()
    db.refresh(c)
    return {"data": _case_dict(c), "meta": _meta()}


@router.post("/api/v1/cases/{case_id}/escalate", status_code=status.HTTP_201_CREATED)
def escalate_case(
    case_id: str,
    body: EscalateCaseRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_case_or_404(case_id, claims.tenant_id, db)

    # Cannot escalate resolved or closed cases
    if c.status in ("RESOLVED", "CLOSED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot escalate a case with status {c.status!r}",
        )

    now = datetime.now(timezone.utc)
    new_level = c.escalation_level + 1
    escalation = CaseEscalation(
        escalation_id=str(uuid.uuid4()),
        case_id=case_id,
        tenant_id=claims.tenant_id,
        escalation_level=new_level,
        escalation_reason=body.escalation_reason,
        escalated_by=claims.sub,
        escalated_to=body.escalated_to,
        note=body.note,
        triggered_at=now,
    )
    db.add(escalation)
    c.status = "ESCALATED"
    c.escalation_level = new_level
    c.updated_by = claims.sub
    c.updated_at = now
    c.version_no += 1
    db.commit()
    db.refresh(c)
    return {"case": _case_dict(c), "escalation_id": escalation.escalation_id, "meta": _meta()}
