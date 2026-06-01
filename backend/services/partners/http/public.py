"""Public REST endpoints for Partner Management.

Spec: backend/docs/domain/partners.md §5
API standards: backend/docs/api-standards.md

Routes:
    GET    /api/v1/partners
    POST   /api/v1/partners
    GET    /api/v1/partners/{partner_id}
    PATCH  /api/v1/partners/{partner_id}
    GET    /api/v1/partners/{partner_id}/commissions
    POST   /api/v1/partners/{partner_id}/commissions/{commission_id}/approve
    POST   /api/v1/partners/{partner_id}/commissions/{commission_id}/pay
    POST   /api/v1/partners/{partner_id}/deal-registrations
    POST   /api/v1/deal-registrations/{registration_id}/approve
    POST   /api/v1/deal-registrations/{registration_id}/reject
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
from services.db.models.partners import DealRegistration, Partner, PartnerCommission
from services.partners.entities import (
    CommissionStatus,
    PartnerDomainError,
    PartnerTier,
    validate_commission_transition,
)
from services.partners.service import PartnersService

router = APIRouter(tags=["partners"])

_svc = PartnersService()

VALID_TIERS = {t.value for t in PartnerTier}
_ADMIN_ROLES = frozenset({"admin", "tenant_admin", "tenant_owner"})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


def _partner_dict(p: Partner) -> dict[str, Any]:
    return {
        "partner_id":              p.partner_id,
        "tenant_id":               p.tenant_id,
        "name":                    p.name,
        "partner_tier":            p.partner_tier,
        "status":                  p.status,
        "region":                  p.region,
        "city":                    p.city,
        "contact_name":            p.contact_name,
        "contact_phone":           p.contact_phone,
        "contact_email":           p.contact_email,
        "account_manager_id":      p.account_manager_id,
        "attributed_opp_count":    p.attributed_opp_count,
        "total_commission_earned": float(p.total_commission_earned) if p.total_commission_earned is not None else 0,
        "commission_due":          float(p.commission_due) if p.commission_due is not None else 0,
        "deal_registration_count": p.deal_registration_count,
        "notes":                   p.notes,
        "tier_review_due_at":      p.tier_review_due_at,
        "created_by":              p.created_by,
        "created_at":              p.created_at.isoformat() if p.created_at else None,
        "updated_at":              p.updated_at.isoformat() if p.updated_at else None,
    }


def _commission_dict(c: PartnerCommission) -> dict[str, Any]:
    return {
        "commission_id":    c.commission_id,
        "partner_id":       c.partner_id,
        "tenant_id":        c.tenant_id,
        "opportunity_id":   c.opportunity_id,
        "opportunity_name": c.opportunity_name,
        "amount":           float(c.amount) if c.amount is not None else 0,
        "rate":             float(c.rate) if c.rate is not None else 0,
        "status":           c.status,
        "calculated_at":    c.calculated_at.isoformat() if c.calculated_at else None,
        "approved_at":      c.approved_at.isoformat() if c.approved_at else None,
        "approved_by":      c.approved_by,
        "paid_at":          c.paid_at.isoformat() if c.paid_at else None,
        "payment_reference": c.payment_reference,
        "dispute_reason":   c.dispute_reason,
        "created_at":       c.created_at.isoformat() if c.created_at else None,
        "updated_at":       c.updated_at.isoformat() if c.updated_at else None,
    }


def _deal_reg_dict(r: DealRegistration) -> dict[str, Any]:
    return {
        "registration_id":    r.registration_id,
        "partner_id":         r.partner_id,
        "tenant_id":          r.tenant_id,
        "opportunity_id":     r.opportunity_id,
        "prospect_name":      r.prospect_name,
        "prospect_phone":     r.prospect_phone,
        "prospect_email":     r.prospect_email,
        "estimated_value":    float(r.estimated_value) if r.estimated_value is not None else 0,
        "expected_close_date": r.expected_close_date,
        "status":             r.status,
        "submitted_at":       r.submitted_at.isoformat() if r.submitted_at else None,
        "reviewed_at":        r.reviewed_at.isoformat() if r.reviewed_at else None,
        "reviewed_by":        r.reviewed_by,
        "rejection_reason":   r.rejection_reason,
        "expiry_date":        r.expiry_date,
        "notes":              r.notes,
        "created_at":         r.created_at.isoformat() if r.created_at else None,
        "updated_at":         r.updated_at.isoformat() if r.updated_at else None,
    }


def _get_partner_or_404(partner_id: str, tenant_id: str, db: Session) -> Partner:
    p = db.get(Partner, partner_id)
    if p is None or p.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return p


def _get_commission_or_404(commission_id: str, partner_id: str, tenant_id: str, db: Session) -> PartnerCommission:
    c = db.get(PartnerCommission, commission_id)
    if c is None or c.tenant_id != tenant_id or c.partner_id != partner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commission not found")
    return c


def _get_deal_reg_or_404(registration_id: str, tenant_id: str, db: Session) -> DealRegistration:
    r = db.get(DealRegistration, registration_id)
    if r is None or r.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal registration not found")
    return r


# ── Request schemas ───────────────────────────────────────────────────────────

class CreatePartnerRequest(BaseModel):
    name: str
    partner_tier: str = "silver"
    region: Optional[str] = None
    city: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None


class UpdatePartnerRequest(BaseModel):
    name: Optional[str] = None
    partner_tier: Optional[str] = None
    status: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None


class PayCommissionRequest(BaseModel):
    payment_reference: str


class SubmitDealRegistrationRequest(BaseModel):
    prospect_name: str
    estimated_value: float
    prospect_phone: Optional[str] = None
    prospect_email: Optional[str] = None
    expected_close_date: Optional[str] = None
    notes: Optional[str] = None


class RejectDealRegistrationRequest(BaseModel):
    rejection_reason: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/api/v1/partners")
def list_partners(
    partner_tier: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(Partner).where(Partner.tenant_id == claims.tenant_id)
    if partner_tier:
        q = q.where(Partner.partner_tier == partner_tier)
    if status:
        q = q.where(Partner.status == status)
    q = q.order_by(Partner.name)
    rows = db.execute(q).scalars().all()
    return {"data": [_partner_dict(p) for p in rows], "meta": _meta()}


@router.post("/api/v1/partners", status_code=status.HTTP_201_CREATED)
def create_partner(
    body: CreatePartnerRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if body.partner_tier not in VALID_TIERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"partner_tier must be one of {sorted(VALID_TIERS)}",
        )

    now = datetime.now(timezone.utc)
    p = Partner(
        partner_id=str(uuid.uuid4()),
        tenant_id=claims.tenant_id,
        name=body.name,
        partner_tier=body.partner_tier,
        status="active",
        region=body.region,
        city=body.city,
        contact_name=body.contact_name,
        contact_phone=body.contact_phone,
        contact_email=body.contact_email,
        attributed_opp_count=0,
        total_commission_earned=0.0,
        commission_due=0,
        deal_registration_count=0,
        notes=body.notes,
        created_by=claims.sub,
        created_at=now,
        updated_at=now,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"data": _partner_dict(p), "meta": _meta()}


@router.get("/api/v1/partners/{partner_id}")
def get_partner(
    partner_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    p = _get_partner_or_404(partner_id, claims.tenant_id, db)
    return {"data": _partner_dict(p), "meta": _meta()}


@router.patch("/api/v1/partners/{partner_id}")
def update_partner(
    partner_id: str,
    body: UpdatePartnerRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    p = _get_partner_or_404(partner_id, claims.tenant_id, db)

    # Only admins can change partner tier
    if body.partner_tier is not None and claims.role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change partner tier",
        )

    if body.partner_tier is not None and body.partner_tier not in VALID_TIERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"partner_tier must be one of {sorted(VALID_TIERS)}",
        )

    now = datetime.now(timezone.utc)
    if body.name is not None:
        p.name = body.name
    if body.partner_tier is not None:
        p.partner_tier = body.partner_tier
    if body.status is not None:
        p.status = body.status
    if body.region is not None:
        p.region = body.region
    if body.city is not None:
        p.city = body.city
    if body.contact_name is not None:
        p.contact_name = body.contact_name
    if body.contact_phone is not None:
        p.contact_phone = body.contact_phone
    if body.contact_email is not None:
        p.contact_email = body.contact_email
    if body.notes is not None:
        p.notes = body.notes
    p.updated_at = now

    db.commit()
    db.refresh(p)
    return {"data": _partner_dict(p), "meta": _meta()}


@router.get("/api/v1/partners/{partner_id}/commissions")
def list_commissions(
    partner_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _get_partner_or_404(partner_id, claims.tenant_id, db)
    rows = db.execute(
        select(PartnerCommission).where(
            PartnerCommission.partner_id == partner_id,
            PartnerCommission.tenant_id == claims.tenant_id,
        ).order_by(PartnerCommission.calculated_at.desc())
    ).scalars().all()
    return {"data": [_commission_dict(c) for c in rows], "meta": _meta()}


@router.post("/api/v1/partners/{partner_id}/commissions/{commission_id}/approve")
def approve_commission(
    partner_id: str,
    commission_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_commission_or_404(commission_id, partner_id, claims.tenant_id, db)
    try:
        validate_commission_transition(c.status, CommissionStatus.APPROVED)
    except PartnerDomainError as exc:
        if "immutable" in str(exc) or c.status == CommissionStatus.PAID:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    now = datetime.now(timezone.utc)
    c.status = CommissionStatus.APPROVED
    c.approved_at = now
    c.approved_by = claims.sub
    c.updated_at = now
    db.commit()
    db.refresh(c)
    return {"data": _commission_dict(c), "meta": _meta()}


@router.post("/api/v1/partners/{partner_id}/commissions/{commission_id}/pay")
def pay_commission(
    partner_id: str,
    commission_id: str,
    body: PayCommissionRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_commission_or_404(commission_id, partner_id, claims.tenant_id, db)

    # Must be approved before paying
    if c.status == CommissionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Commission must be approved before payment",
        )

    try:
        validate_commission_transition(c.status, CommissionStatus.PAID)
    except PartnerDomainError as exc:
        if "immutable" in str(exc) or c.status == CommissionStatus.PAID:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    now = datetime.now(timezone.utc)
    c.status = CommissionStatus.PAID
    c.paid_at = now
    c.payment_reference = body.payment_reference
    c.updated_at = now
    db.commit()
    db.refresh(c)
    return {"data": _commission_dict(c), "meta": _meta()}


@router.post("/api/v1/partners/{partner_id}/deal-registrations", status_code=status.HTTP_201_CREATED)
def submit_deal_registration(
    partner_id: str,
    body: SubmitDealRegistrationRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    p = _get_partner_or_404(partner_id, claims.tenant_id, db)

    # Partner must be active
    if p.status != "active":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only active partners can submit deal registrations",
        )

    now = datetime.now(timezone.utc)
    reg_dict = _svc.build_deal_registration(
        partner=_partner_dict(p),
        prospect_name=body.prospect_name,
        estimated_value=body.estimated_value,
        tenant_id=claims.tenant_id,
        submitted_at_iso=now.isoformat(),
        prospect_phone=body.prospect_phone,
        prospect_email=body.prospect_email,
        expected_close_date=body.expected_close_date,
        notes=body.notes,
    )

    reg = DealRegistration(
        registration_id=str(uuid.uuid4()),
        partner_id=partner_id,
        tenant_id=claims.tenant_id,
        prospect_name=reg_dict["prospect_name"],
        prospect_phone=reg_dict.get("prospect_phone"),
        prospect_email=reg_dict.get("prospect_email"),
        estimated_value=reg_dict["estimated_value"],
        expected_close_date=reg_dict.get("expected_close_date"),
        status="submitted",
        submitted_at=now,
        expiry_date=reg_dict.get("expiry_date"),
        notes=reg_dict.get("notes"),
        created_at=now,
        updated_at=now,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return {"data": _deal_reg_dict(reg), "meta": _meta()}


@router.post("/api/v1/deal-registrations/{registration_id}/approve")
def approve_deal_registration(
    registration_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    r = _get_deal_reg_or_404(registration_id, claims.tenant_id, db)
    if r.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot approve a deal registration with status '{r.status}'",
        )

    now = datetime.now(timezone.utc)
    r.status = "approved"
    r.reviewed_at = now
    r.reviewed_by = claims.sub
    r.updated_at = now
    db.commit()
    db.refresh(r)
    return {"data": _deal_reg_dict(r), "meta": _meta()}


@router.post("/api/v1/deal-registrations/{registration_id}/reject")
def reject_deal_registration(
    registration_id: str,
    body: RejectDealRegistrationRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    r = _get_deal_reg_or_404(registration_id, claims.tenant_id, db)
    if r.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot reject a deal registration with status '{r.status}'",
        )

    now = datetime.now(timezone.utc)
    r.status = "rejected"
    r.reviewed_at = now
    r.reviewed_by = claims.sub
    r.rejection_reason = body.rejection_reason
    r.updated_at = now
    db.commit()
    db.refresh(r)
    return {"data": _deal_reg_dict(r), "meta": _meta()}
