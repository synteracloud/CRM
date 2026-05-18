"""SQLAlchemy ORM models for followup_tasks and followup_escalations.

Schema source: backend/db/activity_task_db/followup_enforcement_schema.sql
Domain spec:   backend/docs/followup-enforcement-model.md
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from services.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class FollowupTask(Base):
    __tablename__ = "followup_tasks"

    task_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    lead_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    owner_id: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="pending",
    )
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    completed_activity_id: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    rule_type: Mapped[str] = mapped_column(String, nullable=False)
    escalation_level: Mapped[str] = mapped_column(
        String, nullable=False, default="none"
    )
    generated_by: Mapped[str] = mapped_column(
        String, nullable=False, default="Scheduler"
    )
    is_canonical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    manager_cancel_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )
    canceled_by_manager_id: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )


class FollowupEscalation(Base):
    __tablename__ = "followup_escalations"

    escalation_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    lead_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String, nullable=False)
    escalation_level: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
