"""Seed fixtures for territory API and service tests."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

TEST_TENANT = "tenant-test-001"

from tests.territories._shared_db import shared_engine as _conftest_engine, SharedSession as _ConftestSession


@pytest.fixture(autouse=True)
def seed_territories():
    """Create schema and seed territory test data for every test in this directory."""
    from services.db.base import Base
    import services.db.models  # noqa: F401
    from services.db.models.territories import Territory, TerritoryRule

    Base.metadata.create_all(bind=_conftest_engine)
    now = datetime.now(timezone.utc)
    db = _ConftestSession()
    try:
        for t_data in [
            dict(territory_id="t-001", name="Punjab Territory", description="Covers Punjab province",
                 criteria_type="geographic", criteria_value={"provinces": ["Punjab"]},
                 assigned_reps=["rep-001", "rep-002"], primary_manager="mgr-001",
                 is_default=False, is_active=True, routing_priority=1),
            dict(territory_id="t-002", name="Sindh Territory", description="Covers Sindh province",
                 criteria_type="geographic", criteria_value={"provinces": ["Sindh"]},
                 assigned_reps=["rep-003"], primary_manager="mgr-002",
                 is_default=False, is_active=True, routing_priority=2),
            dict(territory_id="t-003", name="KPK Territory", description="Covers KPK province",
                 criteria_type="geographic", criteria_value={"provinces": ["KPK"]},
                 assigned_reps=[], primary_manager=None,
                 is_default=False, is_active=False, routing_priority=3),
            dict(territory_id="t-004", name="Default Territory", description="Catch-all",
                 criteria_type="rep_assigned", criteria_value={},
                 assigned_reps=["rep-001"], primary_manager="mgr-001",
                 is_default=True, is_active=True, routing_priority=99),
        ]:
            db.merge(Territory(
                tenant_id=TEST_TENANT, created_by="system",
                created_at=now, updated_at=now, **t_data,
            ))

        db.merge(TerritoryRule(
            rule_id="rule-001", territory_id="t-001", tenant_id=TEST_TENANT,
            rule_type="city", field="lead.city", operator="in",
            value={"cities": ["Lahore", "Faisalabad"]},
            created_at=now, updated_at=now,
        ))
        db.commit()
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=_conftest_engine)


@pytest.fixture
def db_session():
    """Yield a DB session pointing to the conftest engine (for service tests)."""
    sess = _ConftestSession()
    try:
        yield sess
    finally:
        sess.close()
