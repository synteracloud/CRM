"""SQLAlchemy ORM models for collections (invoices, payments, reconciliation_cases).

Domain spec: backend/docs/domain/collections-engine-model.md §2
Migration:   backend/alembic/versions/0003_collections_conversations.py
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from services.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String, nullable=False)
    issue_date: Mapped[str] = mapped_column(String(10), nullable=False)
    due_date: Mapped[str] = mapped_column(String(10), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="PKR")
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    amount_paid: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    amount_outstanding: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="unpaid")
    overdue_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reminder_policy_id: Mapped[str] = mapped_column(String, nullable=False, default="default")
    escalation_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class Payment(Base):
    __tablename__ = "payments"

    payment_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_txn_id: Mapped[str] = mapped_column(String(256), nullable=False)
    invoice_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_ref: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="PKR")
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    received_at: Mapped[str] = mapped_column(String(32), nullable=False)
    settled_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    entered_by: Mapped[str | None] = mapped_column(String, nullable=True)
    proof_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    proof_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(24), nullable=False, default="not_required")
    verified_by: Mapped[str | None] = mapped_column(String, nullable=True)
    verified_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class ReconciliationCase(Base):
    __tablename__ = "reconciliation_cases"

    case_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    payment_id: Mapped[str] = mapped_column(String, nullable=False)
    invoice_id: Mapped[str | None] = mapped_column(String, nullable=True)
    match_status: Mapped[str] = mapped_column(String(20), nullable=False)
    mismatch_reason: Mapped[str | None] = mapped_column(String(32), nullable=True)
    resolver_user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    resolution_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
