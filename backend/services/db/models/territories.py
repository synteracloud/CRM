"""SQLAlchemy ORM models for Territory Management domain.

Domain spec: backend/docs/domain/territory-management.md
Migration:   backend/alembic/versions/0006_territories_schema.py
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


class Territory(Base):
    __tablename__ = "territories"

    territory_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    parent_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    # TerritoryCriteriaType: geographic | postal | account_segment | rep_assigned | hybrid
    criteria_type: Mapped[str] = mapped_column(String(32), nullable=False, default="geographic")
    criteria_value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    assigned_reps: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    primary_manager: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    # Invariant: exactly one territory per tenant has is_default=true
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Lower value = higher priority; used for conflict resolution
    routing_priority: Mapped[int] = mapped_column(Integer, nullable=False, default=99)
    created_by: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class TerritoryRule(Base):
    __tablename__ = "territory_rules"

    rule_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    territory_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # TerritoryRuleType: city | postal_code | region | geo_polygon | account_industry |
    #                    account_size | account_tier | rep_explicit | custom_field
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False)
    field: Mapped[str | None] = mapped_column(String(128), nullable=True, default=None)
    # RuleOperator: eq | in | not_in | starts_with | contains | geo_within
    operator: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class TerritoryAssignment(Base):
    __tablename__ = "territory_assignments"

    assignment_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # SubjectType: lead | account | contact
    subject_type: Mapped[str] = mapped_column(String(16), nullable=False)
    subject_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    territory_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    assigned_rep_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    # AssignmentReason: auto_rule_match | manual_override | conflict_resolution | default_fallback
    assignment_reason: Mapped[str] = mapped_column(String(32), nullable=False, default="auto_rule_match")
    # Points to the new assignment that superseded this one (immutability chain)
    superseded_by: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    # Only one active assignment per (tenant_id, subject_type, subject_id)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    # null if system-assigned
    created_by: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
