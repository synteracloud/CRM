"""Add territory management schema.

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-29

Sprint: 5B-3 — Territories
Spec:   backend/docs/domain/territory-management.md

Tables created:
  territories          — Territory entity with criteria type and rep assignment
  territory_rules      — Per-territory matching rules (city, region, postal, etc.)
  territory_assignments — Immutable assignment audit; one active per subject

Partial unique indexes (PostgreSQL):
  uq_territory_default_per_tenant  — only one is_default=true per tenant
  uq_territory_active_assignment   — only one is_active=true per (tenant, type, subject)
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

VALID_CRITERIA_TYPE  = "('geographic','postal','account_segment','rep_assigned','hybrid')"
VALID_RULE_TYPE      = "('city','postal_code','region','geo_polygon','account_industry','account_size','account_tier','rep_explicit','custom_field')"
VALID_OPERATOR       = "('eq','in','not_in','starts_with','contains','geo_within')"
VALID_SUBJECT_TYPE   = "('lead','account','contact')"
VALID_ASSIGN_REASON  = "('auto_rule_match','manual_override','conflict_resolution','default_fallback')"


def upgrade() -> None:
    # ── 1. territories ────────────────────────────────────────────────────────
    op.create_table(
        "territories",
        sa.Column("territory_id",    sa.String(),    primary_key=True),
        sa.Column("tenant_id",       sa.String(),    nullable=False),
        sa.Column("name",            sa.String(100), nullable=False),
        sa.Column("description",     sa.String(500), nullable=True),
        sa.Column("parent_id",       sa.String(),    nullable=True),
        sa.Column("criteria_type",   sa.String(32),  nullable=False, server_default="geographic"),
        sa.Column("criteria_value",  sa.JSON(),      nullable=False, server_default="{}"),
        sa.Column("assigned_reps",   sa.JSON(),      nullable=False, server_default="[]"),
        sa.Column("primary_manager", sa.String(),    nullable=True),
        sa.Column("is_default",      sa.Boolean(),   nullable=False, server_default="false"),
        sa.Column("is_active",       sa.Boolean(),   nullable=False, server_default="true"),
        sa.Column("routing_priority",sa.Integer(),   nullable=False, server_default="99"),
        sa.Column("created_by",      sa.String(),    nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"criteria_type IN {VALID_CRITERIA_TYPE}", name="territories_criteria_type_chk"),
    )
    op.create_index("idx_territories_tenant",   "territories", ["tenant_id"])
    op.create_index("idx_territories_active",   "territories", ["tenant_id", "is_active"])
    op.create_index("idx_territories_priority", "territories", ["tenant_id", "routing_priority"])
    # Partial unique: exactly one default territory per tenant
    op.create_index(
        "uq_territory_default_per_tenant",
        "territories",
        ["tenant_id"],
        unique=True,
        postgresql_where=sa.text("is_default = true"),
    )

    # ── 2. territory_rules ────────────────────────────────────────────────────
    op.create_table(
        "territory_rules",
        sa.Column("rule_id",       sa.String(),   primary_key=True),
        sa.Column("territory_id",  sa.String(),   nullable=False),
        sa.Column("tenant_id",     sa.String(),   nullable=False),
        sa.Column("rule_type",     sa.String(32), nullable=False),
        sa.Column("field",         sa.String(128),nullable=True),
        sa.Column("operator",      sa.String(32), nullable=True),
        sa.Column("value",         sa.JSON(),     nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"rule_type IN {VALID_RULE_TYPE}", name="territory_rules_type_chk"),
        sa.ForeignKeyConstraint(
            ["territory_id"], ["territories.territory_id"],
            name="fk_territory_rules_territory",
        ),
    )
    op.create_index("idx_territory_rules_territory", "territory_rules", ["territory_id"])
    op.create_index("idx_territory_rules_tenant",    "territory_rules", ["tenant_id"])

    # ── 3. territory_assignments ──────────────────────────────────────────────
    op.create_table(
        "territory_assignments",
        sa.Column("assignment_id",    sa.String(),  primary_key=True),
        sa.Column("tenant_id",        sa.String(),  nullable=False),
        sa.Column("subject_type",     sa.String(16),nullable=False),
        sa.Column("subject_id",       sa.String(),  nullable=False),
        sa.Column("territory_id",     sa.String(),  nullable=False),
        sa.Column("assigned_rep_id",  sa.String(),  nullable=True),
        sa.Column("assignment_reason",sa.String(32),nullable=False, server_default="auto_rule_match"),
        sa.Column("superseded_by",    sa.String(),  nullable=True),
        sa.Column("is_active",        sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by",   sa.String(),  nullable=True),
        sa.Column("created_at",   sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(f"subject_type       IN {VALID_SUBJECT_TYPE}",  name="territory_assign_subject_chk"),
        sa.CheckConstraint(f"assignment_reason  IN {VALID_ASSIGN_REASON}", name="territory_assign_reason_chk"),
        sa.ForeignKeyConstraint(
            ["territory_id"], ["territories.territory_id"],
            name="fk_territory_assignments_territory",
        ),
    )
    op.create_index("idx_territory_assign_tenant",   "territory_assignments", ["tenant_id"])
    op.create_index("idx_territory_assign_subject",  "territory_assignments", ["tenant_id", "subject_type", "subject_id"])
    op.create_index("idx_territory_assign_territory","territory_assignments", ["territory_id"])
    # Partial unique: only one active assignment per subject
    op.create_index(
        "uq_territory_active_assignment",
        "territory_assignments",
        ["tenant_id", "subject_type", "subject_id"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )


def downgrade() -> None:
    op.drop_table("territory_assignments")
    op.drop_table("territory_rules")
    op.drop_table("territories")
