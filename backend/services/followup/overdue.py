"""Overdue follow-up scanner — marks pending tasks past due_at as overdue."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from services.db.models.followup import FollowupTask


def scan_overdue_tasks(db: Session) -> int:
    """Mark FollowupTask records with state='pending' and due_at in the past as 'overdue'.

    Returns the number of tasks updated.
    """
    now = datetime.now(timezone.utc)
    overdue_tasks = (
        db.query(FollowupTask)
        .filter(FollowupTask.state == "pending", FollowupTask.due_at < now)
        .all()
    )
    for task in overdue_tasks:
        task.state = "overdue"
    if overdue_tasks:
        db.commit()
    return len(overdue_tasks)
