"""Tests for the overdue follow-up background scanner."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.db.base import Base
import services.db.models  # noqa: F401
from services.db.models.followup import FollowupTask
from services.followup.overdue import scan_overdue_tasks

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


def _make_task(state: str = "pending", due_offset_minutes: int = -5) -> FollowupTask:
    due = datetime.now(timezone.utc) + timedelta(minutes=due_offset_minutes)
    return FollowupTask(
        task_id=str(uuid.uuid4()),
        tenant_id="tenant-scanner-001",
        lead_id="lead-001",
        owner_id="user-001",
        state=state,
        due_at=due,
        rule_type="TimeBased",
        escalation_level="none",
        generated_by="Scheduler",
        is_canonical=True,
    )


class TestScanOverdueTasks:
    def test_marks_pending_overdue_task(self) -> None:
        db = _Session()
        task = _make_task(state="pending", due_offset_minutes=-5)
        db.add(task)
        db.commit()
        count = scan_overdue_tasks(db)
        db.refresh(task)
        assert count == 1
        assert task.state == "overdue"
        db.close()

    def test_ignores_future_pending_task(self) -> None:
        db = _Session()
        task = _make_task(state="pending", due_offset_minutes=60)
        db.add(task)
        db.commit()
        count = scan_overdue_tasks(db)
        db.refresh(task)
        assert count == 0
        assert task.state == "pending"
        db.close()

    def test_ignores_already_completed_task(self) -> None:
        db = _Session()
        task = _make_task(state="completed", due_offset_minutes=-5)
        db.add(task)
        db.commit()
        count = scan_overdue_tasks(db)
        db.refresh(task)
        assert count == 0
        assert task.state == "completed"
        db.close()

    def test_returns_count_of_updated_tasks(self) -> None:
        db = _Session()
        for _ in range(3):
            db.add(_make_task(state="pending", due_offset_minutes=-10))
        db.commit()
        count = scan_overdue_tasks(db)
        assert count == 3
        db.close()
