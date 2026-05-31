"""SQLAlchemy ORM models for Partner Management domain.

Domain spec: backend/docs/domain/partners.md
Migration:   backend/alembic/versions/0008_partners_schema.py

Invariant: PartnerCommission.status = 'paid' records are immutable.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from services.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Partner(Base):
    __tablename__ = "partners"

    partner_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # PartnerTier: platinum | gold | silver
    partner_tier: Mapped[str] = mapped_column(String(16), nullable=False, default="silver")
    # PartnerStatus: active | inactive | suspended
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    region: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)
    city: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)
    primary_contact_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    account_manager_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    attributed_opp_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_commission_earned: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    commission_due: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    deal_registration_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True, default=None)
    tier_review_due_at: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)  # date ISO string
    created_by: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class DealRegistration(Base):
    __tablename__ = "deal_registrations"

    registration_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    partner_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    opportunity_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    prospect_name: Mapped[str] = mapped_column(String(255), nullable=False)
    prospect_phone: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    prospect_email: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    estimated_value: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    expected_close_date: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)
    # DealRegStatus: submitted | approved | rejected | linked | expired
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="submitted")
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    reviewed_by: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    expiry_date: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class PartnerCommission(Base):
    __tablename__ = "partner_commissions"

    commission_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    partner_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    opportunity_id: Mapped[str] = mapped_column(String, nullable=False)
    opportunity_name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    # CommissionStatus: pending | approved | paid | disputed | cancelled
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    payment_reference: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    dispute_reason: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class PartnerActivityLog(Base):
    __tablename__ = "partner_activity_logs"

    log_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    partner_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # PartnerEvent enum values
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    entity_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
