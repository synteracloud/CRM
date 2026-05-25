"""SQLAlchemy ORM model for idempotency_records.

Spec:      backend/docs/infrastructure/global-idempotency.md §2.1
Migration: backend/alembic/versions/0002_followup_states_leads_idempotency.py

Used by gateway idempotency middleware when it switches from in-memory Map
to DB-backed store (gap A-005).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from services.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    record_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    # 4-tuple key: tenant_id:METHOD:canonical_route:idempotency_key_header
    idempotency_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    http_method: Mapped[str] = mapped_column(String(10), nullable=False)
    canonical_route: Mapped[str] = mapped_column(String(512), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    # state: in_flight | complete | conflict
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="in_flight")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
