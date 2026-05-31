"""Add cases management schema.

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-29

Sprint: 5B-1 — Cases / Support Tickets
Spec:   backend/docs/domain/cases-domain.md

Tables created:
  cases             — Case entity with SLA fields and state machine status
  case_comments     — Immutable comment thread per case
  case_escalations  — Escalation audit records (immutable once created)
  support_queues    — Queue configuration with routing strategy
  sla_policies      — SLA tier definitions (first-response + resolution windows)
  knowledge_articles — Knowledge base articles linked to cases
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

VALID_CASE_STATUS    = "('OPEN','ASSIGNED','IN_PROGRESS','WAITING_ON_CUSTOMER','RESOLVED','ESCALATED','CLOSED')"
VALID_PRIORITY       = "('critical','high','medium','low')"
VALID_CASE_SOURCE    = "('whatsapp','web_form','email','phone','internal')"
VALID_SLA_TIER       = "('tier_1_critical','tier_2_high','tier_3_standard','tier_4_low')"
VALID_COMMENT_TYPE   = "('internal_note','customer_reply','resolution','status_change','escalation_note')"
VALID_ESC_REASON     = "('sla_first_response_breach','sla_resolution_breach','customer_request','manager_override')"
VALID_ROUTING_STRAT  = "('round_robin','least_loaded','skill_based','manual')"
VALID_ARTICLE_STATUS = "('draft','published','archived')"


def upgrade() -> None:
    # ── 1. cases ──────────────────────────────────────────────────────────────────
    op.create_table(
        "cases",
        sa.Column("case_id",      sa.String(),     primary_key=True),
        sa.Column("tenant_id",    sa.String(),     nullable=False),
        sa.Column("case_number",  sa.String(32),   nullable=False),
        sa.Column("subject",      sa.String(255),  nullable=False),
        sa.Column("description",  sa.Text(),       nullable=True),
        sa.Column("status",       sa.String(32),   nullable=False, server_default="OPEN"),
        sa.Column("priority",     sa.String(16),   nullable=False, server_default="medium"),
        sa.Column("source",       sa.String(32),   nullable=False, server_default="web_form"),
        sa.Column("category",     sa.String(64),   nullable=True),
        sa.Column("contact_id",   sa.String(),     nullable=True),
        sa.Column("account_id",   sa.String(),     nullable=True),
        sa.Column("lead_id",      sa.String(),     nullable=True),
        sa.Column("assigned_to",  sa.String(),     nullable=True),
        sa.Column("assigned_team_id", sa.String(), nullable=True),
        sa.Column("queue_id",     sa.String(),     nullable=True),
        sa.Column("sla_tier",     sa.String(32),   nullable=False, server_default="tier_3_standard"),
        sa.Column("sla_first_response_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sla_resolution_due_at",     sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_responded_at",        sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at",               sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_confirmed_at",   sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at",                 sa.DateTime(timezone=True), nullable=True),
        sa.Column("reopened_at",               sa.DateTime(timezone=True), nullable=True),
        sa.Column("reopen_count",      sa.Integer(), nullable=False, server_default="0"),
        sa.Column("escalation_level",  sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tags",          sa.JSON(),    nullable=False, server_default="[]"),
        sa.Column("custom_fields", sa.JSON(),    nullable=False, server_default="{}"),
        sa.Column("version_no",    sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at",    sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at",    sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by",    sa.String(), nullable=False),
        sa.Column("updated_by",    sa.String(), nullable=False),
        sa.CheckConstraint(f"status   IN {VALID_CASE_STATUS}", name="cases_status_chk"),
        sa.CheckConstraint(f"priority IN {VALID_PRIORITY}",    name="cases_priority_chk"),
        sa.CheckConstraint(f"source   IN {VALID_CASE_SOURCE}", name="cases_source_chk"),
        sa.CheckConstraint(f"sla_tier IN {VALID_SLA_TIER}",    name="cases_sla_tier_chk"),
    )
    op.create_index("idx_cases_tenant",        "cases", ["tenant_id"])
    op.create_index("idx_cases_status",        "cases", ["tenant_id", "status"])
    op.create_index("idx_cases_assigned_to",   "cases", ["tenant_id", "assigned_to"])
    op.create_index("idx_cases_contact",       "cases", ["tenant_id", "contact_id"])
    op.create_index("idx_cases_number",        "cases", ["tenant_id", "case_number"], unique=True)

    # ── 2. case_comments ──────────────────────────────────────────────────────────
    op.create_table(
        "case_comments",
        sa.Column("comment_id",              sa.String(),  primary_key=True),
        sa.Column("case_id",                 sa.String(),  nullable=False),
        sa.Column("tenant_id",               sa.String(),  nullable=False),
        sa.Column("comment_type",            sa.String(32), nullable=False),
        sa.Column("body",                    sa.Text(),    nullable=False),
        sa.Column("author_id",               sa.String(),  nullable=False),
        sa.Column("is_visible_to_customer",  sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("attachment_urls",         sa.JSON(),    nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"comment_type IN {VALID_COMMENT_TYPE}", name="case_comments_type_chk"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.case_id"], name="fk_case_comments_case"),
    )
    op.create_index("idx_case_comments_case",   "case_comments", ["case_id"])
    op.create_index("idx_case_comments_tenant", "case_comments", ["tenant_id"])

    # ── 3. case_escalations ───────────────────────────────────────────────────────
    op.create_table(
        "case_escalations",
        sa.Column("escalation_id",     sa.String(),  primary_key=True),
        sa.Column("case_id",           sa.String(),  nullable=False),
        sa.Column("tenant_id",         sa.String(),  nullable=False),
        sa.Column("escalation_level",  sa.Integer(), nullable=False),
        sa.Column("escalation_reason", sa.String(64), nullable=False),
        sa.Column("escalated_by",      sa.String(),  nullable=True),
        sa.Column("escalated_to",      sa.String(),  nullable=True),
        sa.Column("escalated_to_team", sa.String(),  nullable=True),
        sa.Column("note",              sa.Text(),    nullable=True),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("resolved_at",  sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(f"escalation_reason IN {VALID_ESC_REASON}", name="case_esc_reason_chk"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.case_id"], name="fk_case_escalations_case"),
    )
    op.create_index("idx_case_escalations_case",   "case_escalations", ["case_id"])
    op.create_index("idx_case_escalations_tenant", "case_escalations", ["tenant_id"])

    # ── 4. support_queues ─────────────────────────────────────────────────────────
    op.create_table(
        "support_queues",
        sa.Column("queue_id",          sa.String(),  primary_key=True),
        sa.Column("tenant_id",         sa.String(),  nullable=False),
        sa.Column("name",              sa.String(128), nullable=False),
        sa.Column("description",       sa.Text(),    nullable=True),
        sa.Column("routing_strategy",  sa.String(32), nullable=False, server_default="round_robin"),
        sa.Column("skill_tags",        sa.JSON(),    nullable=False, server_default="[]"),
        sa.Column("sla_tier_default",  sa.String(32), nullable=False, server_default="tier_3_standard"),
        sa.Column("team_id",           sa.String(),  nullable=True),
        sa.Column("is_active",         sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"routing_strategy IN {VALID_ROUTING_STRAT}", name="support_queues_strategy_chk"),
    )
    op.create_index("idx_support_queues_tenant", "support_queues", ["tenant_id"])

    # ── 5. sla_policies ───────────────────────────────────────────────────────────
    op.create_table(
        "sla_policies",
        sa.Column("policy_id",                  sa.String(),  primary_key=True),
        sa.Column("tenant_id",                  sa.String(),  nullable=False),
        sa.Column("sla_tier",                   sa.String(32), nullable=False),
        sa.Column("first_response_hours",       sa.Integer(), nullable=False),
        sa.Column("resolution_hours",           sa.Integer(), nullable=False),
        sa.Column("business_hours_only",        sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("pause_on_waiting_customer",  sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"sla_tier IN {VALID_SLA_TIER}", name="sla_policies_tier_chk"),
        sa.UniqueConstraint("tenant_id", "sla_tier", name="uq_sla_policies_tenant_tier"),
    )
    op.create_index("idx_sla_policies_tenant", "sla_policies", ["tenant_id"])

    # ── 6. knowledge_articles ─────────────────────────────────────────────────────
    op.create_table(
        "knowledge_articles",
        sa.Column("article_id",        sa.String(),   primary_key=True),
        sa.Column("tenant_id",         sa.String(),   nullable=False),
        sa.Column("title",             sa.String(255), nullable=False),
        sa.Column("body",              sa.Text(),     nullable=False, server_default=""),
        sa.Column("category",          sa.String(64), nullable=True),
        sa.Column("tags",              sa.JSON(),     nullable=False, server_default="[]"),
        sa.Column("status",            sa.String(16), nullable=False, server_default="draft"),
        sa.Column("language",          sa.String(8),  nullable=False, server_default="en"),
        sa.Column("author_id",         sa.String(),   nullable=False),
        sa.Column("published_at",      sa.DateTime(timezone=True), nullable=True),
        sa.Column("view_count",        sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("helpful_count",     sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("not_helpful_count", sa.Integer(),  nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"status IN {VALID_ARTICLE_STATUS}", name="knowledge_articles_status_chk"),
    )
    op.create_index("idx_knowledge_articles_tenant",   "knowledge_articles", ["tenant_id"])
    op.create_index("idx_knowledge_articles_status",   "knowledge_articles", ["tenant_id", "status"])
    op.create_index("idx_knowledge_articles_category", "knowledge_articles", ["tenant_id", "category"])


def downgrade() -> None:
    op.drop_table("knowledge_articles")
    op.drop_table("sla_policies")
    op.drop_table("support_queues")
    op.drop_table("case_escalations")
    op.drop_table("case_comments")
    op.drop_table("cases")
