"""Add partner management schema.

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-29

Sprint: 5B-5 — Partners
Spec:   backend/docs/domain/partners.md

Tables created:
  partners               — Partner entity with tier, status, commission counters
  deal_registrations     — Deal registration with protection window + expiry
  partner_commissions    — Commission ledger; status=paid records are immutable
  partner_activity_logs  — Immutable activity audit per partner

Invariant: partner_commissions.status = 'paid' enforced at service layer.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None

VALID_PARTNER_TIER    = "('platinum','gold','silver')"
VALID_PARTNER_STATUS  = "('active','inactive','suspended')"
VALID_DEAL_REG_STATUS = "('submitted','approved','rejected','linked','expired')"
VALID_COMMISSION_STATUS = "('pending','approved','paid','disputed','cancelled')"


def upgrade() -> None:
    # ── 1. partners ───────────────────────────────────────────────────────────
    op.create_table(
        "partners",
        sa.Column("partner_id",              sa.String(),     primary_key=True),
        sa.Column("tenant_id",               sa.String(),     nullable=False),
        sa.Column("name",                    sa.String(255),  nullable=False),
        sa.Column("partner_tier",            sa.String(16),   nullable=False, server_default="silver"),
        sa.Column("status",                  sa.String(16),   nullable=False, server_default="active"),
        sa.Column("region",                  sa.String(64),   nullable=True),
        sa.Column("city",                    sa.String(64),   nullable=True),
        sa.Column("primary_contact_id",      sa.String(),     nullable=True),
        sa.Column("contact_name",            sa.String(255),  nullable=True),
        sa.Column("contact_phone",           sa.String(32),   nullable=True),
        sa.Column("contact_email",           sa.String(255),  nullable=True),
        sa.Column("account_manager_id",      sa.String(),     nullable=True),
        sa.Column("attributed_opp_count",    sa.Integer(),    nullable=False, server_default="0"),
        sa.Column("total_commission_earned", sa.Numeric(18,2), nullable=False, server_default="0"),
        sa.Column("commission_due",          sa.Numeric(18,2), nullable=False, server_default="0"),
        sa.Column("deal_registration_count", sa.Integer(),    nullable=False, server_default="0"),
        sa.Column("notes",                   sa.String(2000), nullable=True),
        sa.Column("tier_review_due_at",      sa.String(10),   nullable=True),
        sa.Column("created_by",              sa.String(),     nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"partner_tier IN {VALID_PARTNER_TIER}",   name="partners_tier_chk"),
        sa.CheckConstraint(f"status       IN {VALID_PARTNER_STATUS}", name="partners_status_chk"),
    )
    op.create_index("idx_partners_tenant", "partners", ["tenant_id"])
    op.create_index("idx_partners_tier",   "partners", ["tenant_id", "partner_tier"])
    op.create_index("idx_partners_status", "partners", ["tenant_id", "status"])

    # ── 2. deal_registrations ─────────────────────────────────────────────────
    op.create_table(
        "deal_registrations",
        sa.Column("registration_id",    sa.String(),     primary_key=True),
        sa.Column("partner_id",         sa.String(),     nullable=False),
        sa.Column("tenant_id",          sa.String(),     nullable=False),
        sa.Column("opportunity_id",     sa.String(),     nullable=True),
        sa.Column("prospect_name",      sa.String(255),  nullable=False),
        sa.Column("prospect_phone",     sa.String(32),   nullable=True),
        sa.Column("prospect_email",     sa.String(255),  nullable=True),
        sa.Column("estimated_value",    sa.Numeric(18,2), nullable=False, server_default="0"),
        sa.Column("expected_close_date",sa.String(10),   nullable=True),
        sa.Column("status",             sa.String(16),   nullable=False, server_default="submitted"),
        sa.Column("submitted_at",       sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("reviewed_at",        sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by",        sa.String(),     nullable=True),
        sa.Column("rejection_reason",   sa.Text(),       nullable=True),
        sa.Column("expiry_date",        sa.String(10),   nullable=True),
        sa.Column("notes",              sa.Text(),       nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"status IN {VALID_DEAL_REG_STATUS}", name="deal_reg_status_chk"),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.partner_id"], name="fk_deal_reg_partner"),
    )
    op.create_index("idx_deal_reg_partner", "deal_registrations", ["partner_id"])
    op.create_index("idx_deal_reg_tenant",  "deal_registrations", ["tenant_id"])
    op.create_index("idx_deal_reg_status",  "deal_registrations", ["tenant_id", "status"])

    # ── 3. partner_commissions ────────────────────────────────────────────────
    op.create_table(
        "partner_commissions",
        sa.Column("commission_id",    sa.String(),      primary_key=True),
        sa.Column("partner_id",       sa.String(),      nullable=False),
        sa.Column("tenant_id",        sa.String(),      nullable=False),
        sa.Column("opportunity_id",   sa.String(),      nullable=False),
        sa.Column("opportunity_name", sa.String(255),   nullable=True),
        sa.Column("amount",           sa.Numeric(18,2), nullable=False),
        sa.Column("rate",             sa.Numeric(5,4),  nullable=False),
        sa.Column("status",           sa.String(16),    nullable=False, server_default="pending"),
        sa.Column("calculated_at",    sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("approved_at",      sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by",      sa.String(),      nullable=True),
        sa.Column("paid_at",          sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_reference",sa.String(255),   nullable=True),
        sa.Column("dispute_reason",   sa.Text(),        nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"status IN {VALID_COMMISSION_STATUS}", name="partner_commission_status_chk"),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.partner_id"], name="fk_commission_partner"),
    )
    op.create_index("idx_partner_comm_partner", "partner_commissions", ["partner_id"])
    op.create_index("idx_partner_comm_tenant",  "partner_commissions", ["tenant_id"])
    op.create_index("idx_partner_comm_status",  "partner_commissions", ["tenant_id", "status"])
    op.create_index("idx_partner_comm_opp",     "partner_commissions", ["opportunity_id"])

    # ── 4. partner_activity_logs ──────────────────────────────────────────────
    op.create_table(
        "partner_activity_logs",
        sa.Column("log_id",       sa.String(),      primary_key=True),
        sa.Column("partner_id",   sa.String(),      nullable=False),
        sa.Column("tenant_id",    sa.String(),      nullable=False),
        sa.Column("event_type",   sa.String(64),    nullable=False),
        sa.Column("description",  sa.String(1000),  nullable=False),
        sa.Column("actor_id",     sa.String(),      nullable=True),
        sa.Column("entity_id",    sa.String(),      nullable=True),
        sa.Column("created_at",   sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.partner_id"], name="fk_activity_partner"),
    )
    op.create_index("idx_partner_activity_partner", "partner_activity_logs", ["partner_id"])
    op.create_index("idx_partner_activity_tenant",  "partner_activity_logs", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("partner_activity_logs")
    op.drop_table("partner_commissions")
    op.drop_table("deal_registrations")
    op.drop_table("partners")
