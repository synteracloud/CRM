"""Create all domain PostgreSQL schemas (org_tenant_db, identity_auth_db, etc.)

These schemas were pre-built locally via direct SQL; this migration
applies them to the Render production PostgreSQL database.

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-01
"""

from __future__ import annotations
from pathlib import Path
from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

DB_SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "db"

SCHEMAS = [
    "org_tenant_db",
    "identity_auth_db",
    "lead_management_db",
    "contact_account_db",
    "opportunity_db",
    "transaction_db",
    "activity_task_db",
    "feature_flag_db",
]


def upgrade() -> None:
    conn = op.get_bind()
    for schema in SCHEMAS:
        sql_path = DB_SCHEMA_ROOT / schema / "schema.sql"
        if not sql_path.exists():
            continue
        sql = sql_path.read_text(encoding="utf-8")
        # Remove SET search_path lines — breaks when schema doesn't exist yet
        cleaned_lines = [
            line for line in sql.splitlines()
            if not line.strip().upper().startswith("SET SEARCH_PATH")
        ]
        cleaned = "\n".join(cleaned_lines)
        # Execute as a single block — psycopg2 handles multi-statement SQL
        conn.execute(sa.text(cleaned))


def downgrade() -> None:
    conn = op.get_bind()
    for schema in reversed(SCHEMAS):
        conn.execute(sa.text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
