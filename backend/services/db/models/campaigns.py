"""SQLAlchemy ORM models for Marketing Campaigns domain.

Domain spec: backend/docs/domain/marketing-campaigns.md
Migration:   backend/alembic/versions/0007_campaigns_schema.py

P-017 constraint: Urdu templates require urdu_approved_by before activation.
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


class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True, default=None)
    # CampaignStatus: draft | scheduled | active | paused | completed | cancelled
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    # CampaignType: whatsapp_broadcast | email | sms
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="whatsapp_broadcast")
    segment_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    template_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    attribution_window_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    # P-017: required when template is_urdu=true before activation
    urdu_approved_by: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    total_recipients: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delivered_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    opened_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    replied_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    opted_out_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    leads_generated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conversions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class CampaignSegment(Base):
    __tablename__ = "campaign_segments"

    segment_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    # SegmentEntityType: lead | contact
    entity_type: Mapped[str] = mapped_column(String(16), nullable=False, default="contact")
    rules: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    estimated_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    is_dynamic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class MessageTemplate(Base):
    __tablename__ = "message_templates"

    template_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # CampaignType: whatsapp_broadcast | email | sms
    channel: Mapped[str] = mapped_column(String(32), nullable=False, default="whatsapp_broadcast")
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="en")
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    footer: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    cta_label: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    cta_url: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)
    meta_template_name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    # MetaTemplateStatus: pending | approved | rejected | paused
    meta_template_status: Mapped[str | None] = mapped_column(String(16), nullable=True, default=None)
    # Derived: true when language = "ur"
    is_urdu: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class CampaignSend(Base):
    __tablename__ = "campaign_sends"

    send_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(String, nullable=False)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    # SendStatus: queued | sent | delivered | read | replied | failed | skipped
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="queued")
    # SkipReason: not_opted_in | no_channel | duplicate | opted_out
    skip_reason: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    # Idempotency key: campaign_{campaign_id}_contact_{contact_id}
    idempotency_key: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)


class CampaignConversion(Base):
    __tablename__ = "campaign_conversions"

    conversion_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    campaign_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(String, nullable=False)
    # ConversionType: lead_created | opportunity_created | opportunity_won
    conversion_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String, nullable=False)
    attributed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_now)
