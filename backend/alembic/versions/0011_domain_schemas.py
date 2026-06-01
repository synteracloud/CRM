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
    # Use raw psycopg2 cursor to execute multi-statement SQL (handles $$ blocks)
    conn = op.get_bind()
    raw_conn = conn.connection.dbapi_connection
    cursor = raw_conn.cursor()
    try:
        for schema in SCHEMAS:
            sql_path = DB_SCHEMA_ROOT / schema / "schema.sql"
            if not sql_path.exists():
                continue
            sql = sql_path.read_text(encoding="utf-8")
            # Keep SET search_path lines — they ensure FK references resolve to the
            # correct domain schema, not public. Also creates schema if missing.
            # Just ensure schema is created first.
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            cursor.execute(sql)
        raw_conn.commit()
    except Exception:
        raw_conn.rollback()
        raise
    finally:
        cursor.close()


def downgrade() -> None:
    conn = op.get_bind()
    for schema in reversed(SCHEMAS):
        conn.execute(sa.text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
