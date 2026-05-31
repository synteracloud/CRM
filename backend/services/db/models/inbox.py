"""SQLAlchemy ORM models for Shared Inbox domain.

Domain spec: backend/docs/domain/shared-inbox.md
Migration:   backend/alembic/versions/0005_inbox_schema.py

Extends the existing Conversation entity (conversations.py) with inbox-specific
fields via migration 0005. New tables: inbox_queues, agent_presence,
conversation_handoffs.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from services.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class InboxQueue(Base):
    __tablename__ = "inbox_queues"

    queue_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    # InboxRoutingStrategy: round_robin | least_loaded | claim_first | skill_based
    routing_strategy: Mapped[str] = mapped_column(String(32), nullable=False, default="round_robin")
    skill_tags: Mapped[str | None] = mapped_column(String, nullable=True, default=None)  # JSON-encoded list
    team_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    auto_assign: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class AgentPresence(Base):
    __tablename__ = "agent_presence"

    agent_id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # PresenceStatus: online | away | busy | offline
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="offline")
    open_conversation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_concurrent: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class ConversationHandoff(Base):
    __tablename__ = "conversation_handoffs"

    handoff_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    from_agent_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    to_agent_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    # HandoffReason: agent_unavailable | capacity_exceeded | skill_match | manual | escalation
    handoff_reason: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    note: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    initiated_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
