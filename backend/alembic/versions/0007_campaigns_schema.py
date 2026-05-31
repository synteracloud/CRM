"""Add marketing campaigns schema.

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-29

Sprint: 5B-4 — Marketing / Campaigns
Spec:   backend/docs/domain/marketing-campaigns.md

Tables created:
  campaigns             — Campaign entity with state machine status + counters
  campaign_segments     — Audience segment with rule definitions
  message_templates     — WhatsApp/Email/SMS message templates
  campaign_sends        — Per-contact send records with delivery tracking
  campaign_conversions  — Attribution records (last-touch, 30-day window)

P-017: campaigns.urdu_approved_by enforced at service layer, not DB level.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

VALID_CAMPAIGN_STATUS  = "('draft','scheduled','active','paused','completed','cancelled')"
VALID_CAMPAIGN_TYPE    = "('whatsapp_broadcast','email','sms')"
VALID_SEND_STATUS      = "('queued','sent','delivered','read','replied','failed','skipped')"
VALID_SKIP_REASON      = "('not_opted_in','no_channel','duplicate','opted_out')"
VALID_CONVERSION_TYPE  = "('lead_created','opportunity_created','opportunity_won')"
VALID_META_STATUS      = "('pending','approved','rejected','paused')"
VALID_ENTITY_TYPE      = "('lead','contact')"


def upgrade() -> None:
    # ── 1. campaign_segments ──────────────────────────────────────────────────
    op.create_table(
        "campaign_segments",
        sa.Column("segment_id",         sa.String(),    primary_key=True),
        sa.Column("tenant_id",          sa.String(),    nullable=False),
        sa.Column("name",               sa.String(255), nullable=False),
        sa.Column("description",        sa.Text(),      nullable=True),
        sa.Column("entity_type",        sa.String(16),  nullable=False, server_default="contact"),
        sa.Column("rules",              sa.JSON(),      nullable=False, server_default="[]"),
        sa.Column("estimated_size",     sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("last_validated_at",  sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_dynamic",         sa.Boolean(),   nullable=False, server_default="true"),
        sa.Column("created_by",         sa.String(),    nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"entity_type IN {VALID_ENTITY_TYPE}", name="campaign_segments_entity_chk"),
    )
    op.create_index("idx_campaign_segments_tenant", "campaign_segments", ["tenant_id"])

    # ── 2. message_templates ──────────────────────────────────────────────────
    op.create_table(
        "message_templates",
        sa.Column("template_id",          sa.String(),    primary_key=True),
        sa.Column("tenant_id",            sa.String(),    nullable=False),
        sa.Column("name",                 sa.String(255), nullable=False),
        sa.Column("channel",              sa.String(32),  nullable=False, server_default="whatsapp_broadcast"),
        sa.Column("language",             sa.String(8),   nullable=False, server_default="en"),
        sa.Column("subject",              sa.String(255), nullable=True),
        sa.Column("body",                 sa.Text(),      nullable=False),
        sa.Column("footer",               sa.String(255), nullable=True),
        sa.Column("cta_label",            sa.String(20),  nullable=True),
        sa.Column("cta_url",              sa.String(512), nullable=True),
        sa.Column("meta_template_name",   sa.String(255), nullable=True),
        sa.Column("meta_template_status", sa.String(16),  nullable=True),
        sa.Column("is_urdu",              sa.Boolean(),   nullable=False, server_default="false"),
        sa.Column("created_by",           sa.String(),    nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"channel               IN {VALID_CAMPAIGN_TYPE}", name="message_templates_channel_chk"),
        sa.CheckConstraint(f"meta_template_status  IN {VALID_META_STATUS}",   name="message_templates_meta_chk"),
    )
    op.create_index("idx_message_templates_tenant",  "message_templates", ["tenant_id"])
    op.create_index("idx_message_templates_channel", "message_templates", ["tenant_id", "channel"])

    # ── 3. campaigns ──────────────────────────────────────────────────────────
    op.create_table(
        "campaigns",
        sa.Column("campaign_id",             sa.String(),    primary_key=True),
        sa.Column("tenant_id",               sa.String(),    nullable=False),
        sa.Column("name",                    sa.String(255), nullable=False),
        sa.Column("description",             sa.String(2000),nullable=True),
        sa.Column("status",                  sa.String(16),  nullable=False, server_default="draft"),
        sa.Column("type",                    sa.String(32),  nullable=False, server_default="whatsapp_broadcast"),
        sa.Column("segment_id",              sa.String(),    nullable=True),
        sa.Column("template_id",             sa.String(),    nullable=True),
        sa.Column("scheduled_at",            sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at",            sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at",            sa.DateTime(timezone=True), nullable=True),
        sa.Column("paused_at",               sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at",            sa.DateTime(timezone=True), nullable=True),
        sa.Column("attribution_window_days", sa.Integer(),   nullable=False, server_default="30"),
        sa.Column("urdu_approved_by",        sa.String(),    nullable=True),
        sa.Column("total_recipients",        sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("sent_count",              sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("delivered_count",         sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("opened_count",            sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("replied_count",           sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("opted_out_count",         sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("leads_generated",         sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("conversions",             sa.Integer(),   nullable=False, server_default="0"),
        sa.Column("created_by",              sa.String(),    nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"status IN {VALID_CAMPAIGN_STATUS}", name="campaigns_status_chk"),
        sa.CheckConstraint(f"type   IN {VALID_CAMPAIGN_TYPE}",   name="campaigns_type_chk"),
        sa.ForeignKeyConstraint(["segment_id"],  ["campaign_segments.segment_id"],  name="fk_campaigns_segment",  ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["template_id"], ["message_templates.template_id"], name="fk_campaigns_template", ondelete="SET NULL"),
    )
    op.create_index("idx_campaigns_tenant",  "campaigns", ["tenant_id"])
    op.create_index("idx_campaigns_status",  "campaigns", ["tenant_id", "status"])

    # ── 4. campaign_sends ─────────────────────────────────────────────────────
    op.create_table(
        "campaign_sends",
        sa.Column("send_id",          sa.String(),    primary_key=True),
        sa.Column("campaign_id",      sa.String(),    nullable=False),
        sa.Column("tenant_id",        sa.String(),    nullable=False),
        sa.Column("contact_id",       sa.String(),    nullable=False),
        sa.Column("contact_phone",    sa.String(32),  nullable=True),
        sa.Column("contact_email",    sa.String(255), nullable=True),
        sa.Column("channel",          sa.String(32),  nullable=False),
        sa.Column("status",           sa.String(16),  nullable=False, server_default="queued"),
        sa.Column("skip_reason",      sa.String(32),  nullable=True),
        sa.Column("sent_at",          sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at",     sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at",          sa.DateTime(timezone=True), nullable=True),
        sa.Column("replied_at",       sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at",        sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason",   sa.Text(),      nullable=True),
        sa.Column("idempotency_key",  sa.String(512), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"status      IN {VALID_SEND_STATUS}", name="campaign_sends_status_chk"),
        sa.CheckConstraint(f"skip_reason IN {VALID_SKIP_REASON}", name="campaign_sends_skip_chk"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.campaign_id"], name="fk_campaign_sends_campaign"),
    )
    op.create_index("idx_campaign_sends_campaign", "campaign_sends", ["campaign_id"])
    op.create_index("idx_campaign_sends_tenant",   "campaign_sends", ["tenant_id"])
    op.create_index("idx_campaign_sends_contact",  "campaign_sends", ["tenant_id", "contact_id"])

    # ── 5. campaign_conversions ───────────────────────────────────────────────
    op.create_table(
        "campaign_conversions",
        sa.Column("conversion_id",   sa.String(),    primary_key=True),
        sa.Column("campaign_id",     sa.String(),    nullable=False),
        sa.Column("tenant_id",       sa.String(),    nullable=False),
        sa.Column("contact_id",      sa.String(),    nullable=False),
        sa.Column("conversion_type", sa.String(32),  nullable=False),
        sa.Column("entity_id",       sa.String(),    nullable=False),
        sa.Column("attributed_at",   sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at",      sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"conversion_type IN {VALID_CONVERSION_TYPE}", name="campaign_conversions_type_chk"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.campaign_id"], name="fk_campaign_conversions_campaign"),
    )
    op.create_index("idx_campaign_conversions_campaign", "campaign_conversions", ["campaign_id"])
    op.create_index("idx_campaign_conversions_tenant",   "campaign_conversions", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("campaign_conversions")
    op.drop_table("campaign_sends")
    op.drop_table("campaigns")
    op.drop_table("message_templates")
    op.drop_table("campaign_segments")
