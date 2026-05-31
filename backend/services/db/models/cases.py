"""SQLAlchemy ORM models for Case Management domain.

Domain spec: backend/docs/domain/cases-domain.md
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from services.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Case(Base):
    __tablename__ = "cases"

    case_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    case_number: Mapped[str] = mapped_column(String(32), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    # CaseStatus: OPEN | ASSIGNED | IN_PROGRESS | WAITING_ON_CUSTOMER | RESOLVED | ESCALATED | CLOSED
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    # CasePriority: critical | high | medium | low
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    # CaseSource: whatsapp | web_form | email | phone | internal
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="web_form")
    category: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)
    contact_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    account_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    lead_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    assigned_to: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    assigned_team_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    queue_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    # SLATier: tier_1_critical | tier_2_high | tier_3_standard | tier_4_low
    sla_tier: Mapped[str] = mapped_column(String(32), nullable=False, default="tier_3_standard")
    sla_first_response_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    sla_resolution_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    first_responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    resolution_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    reopened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    reopen_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    escalation_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    custom_fields: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    updated_by: Mapped[str] = mapped_column(String, nullable=False)


class CaseComment(Base):
    __tablename__ = "case_comments"

    comment_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # CommentType: internal_note | customer_reply | resolution | status_change | escalation_note
    comment_type: Mapped[str] = mapped_column(String(32), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[str] = mapped_column(String, nullable=False)
    is_visible_to_customer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    attachment_urls: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )


class CaseEscalation(Base):
    __tablename__ = "case_escalations"

    escalation_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    escalation_level: Mapped[int] = mapped_column(Integer, nullable=False)
    # EscalationReason: sla_first_response_breach | sla_resolution_breach | customer_request | manager_override
    escalation_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    escalated_by: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    escalated_to: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    escalated_to_team: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    note: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )


class SupportQueue(Base):
    __tablename__ = "support_queues"

    queue_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    # RoutingStrategy: round_robin | least_loaded | skill_based | manual
    routing_strategy: Mapped[str] = mapped_column(String(32), nullable=False, default="round_robin")
    skill_tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    sla_tier_default: Mapped[str] = mapped_column(String(32), nullable=False, default="tier_3_standard")
    team_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )


class SLAPolicy(Base):
    __tablename__ = "sla_policies"

    policy_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # SLATier: tier_1_critical | tier_2_high | tier_3_standard | tier_4_low
    sla_tier: Mapped[str] = mapped_column(String(32), nullable=False)
    first_response_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    business_hours_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    pause_on_waiting_customer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    article_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # ArticleStatus: draft | published | archived
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    author_id: Mapped[str] = mapped_column(String, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    not_helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
