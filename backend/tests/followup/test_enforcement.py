"""Unit tests for FollowupEnforcementEngine.

Covers: timer rules, escalation ladder, inactivity rule, closure gate,
enforcement ramp-up (soft/medium/strict).

Spec: backend/docs/followup-enforcement-model.md
"""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta, timezone

import pytest

from services.followup.engine import (
    FollowupEnforcementEngine,
    FollowupPolicyError,
    FollowupPolicyWarning,
)
from services.followup.entities import (
    EscalationLevel,
    FollowupPolicy,
    FollowupState,
    LeadSnapshot,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _lead(
    lead_id: str = "lead-001",
    priority: str = "warm",
    status: str = "open",
    stage: str = "new",
    last_activity_at: datetime | None = None,
) -> LeadSnapshot:
    return LeadSnapshot(
        lead_id=lead_id,
        tenant_id="tenant-001",
        owner_id="owner-001",
        status=status,
        priority=priority,
        stage=stage,
        last_activity_at=last_activity_at or _now(),
    )


# ── Timer rules ───────────────────────────────────────────────────────────────


class TestTimerRules:
    def test_register_lead_creates_pending_task(self) -> None:
        engine = FollowupEnforcementEngine()
        now = _now()
        task = engine.register_lead(_lead(), now=now)

        assert task.state == FollowupState.PENDING
        assert task.rule_type == "TimeBased"
        assert task.generated_by == "Scheduler"

    def test_hot_lead_sla_4_hours(self) -> None:
        policy = FollowupPolicy(hot_sla_hours=4)
        engine = FollowupEnforcementEngine(policy=policy)
        now = _now()
        task = engine.register_lead(_lead(priority="hot"), now=now)

        expected_due = now + timedelta(hours=4)
        delta = abs((task.due_at - expected_due).total_seconds())
        assert delta < 1  # within 1 second

    def test_warm_lead_sla_24_hours(self) -> None:
        policy = FollowupPolicy(warm_sla_hours=24)
        engine = FollowupEnforcementEngine(policy=policy)
        now = _now()
        task = engine.register_lead(_lead(priority="warm"), now=now)

        expected_due = now + timedelta(hours=24)
        delta = abs((task.due_at - expected_due).total_seconds())
        assert delta < 1

    def test_cold_lead_sla_72_hours(self) -> None:
        policy = FollowupPolicy(cold_sla_hours=72)
        engine = FollowupEnforcementEngine(policy=policy)
        now = _now()
        task = engine.register_lead(_lead(priority="cold"), now=now)

        expected_due = now + timedelta(hours=72)
        delta = abs((task.due_at - expected_due).total_seconds())
        assert delta < 1

    def test_log_activity_closes_pending_and_creates_new(self) -> None:
        engine = FollowupEnforcementEngine()
        now = _now()
        engine.register_lead(_lead(), now=now)
        new_task = engine.log_activity("lead-001", "activity-abc", now=now)

        tasks = engine.tasks_for_lead("lead-001")
        completed = [t for t in tasks if t.state == FollowupState.COMPLETED]
        assert len(completed) == 1
        assert completed[0].completed_activity_id == "activity-abc"
        assert new_task.state == FollowupState.PENDING
        assert new_task.rule_type == "ActivityBased"

    def test_pending_task_transitions_to_overdue_when_past_due(self) -> None:
        engine = FollowupEnforcementEngine()
        past = _now() - timedelta(hours=25)
        lead = _lead(last_activity_at=past - timedelta(hours=1))
        engine.register_lead(lead, now=past)
        engine.process_due_transitions(now=_now())

        tasks = engine.tasks_for_lead("lead-001")
        overdue = [t for t in tasks if t.state == FollowupState.OVERDUE]
        assert len(overdue) >= 1


# ── Escalation ladder ─────────────────────────────────────────────────────────


class TestEscalationLadder:
    def test_reminder_fires_at_overdue(self) -> None:
        policy = FollowupPolicy(warm_sla_hours=1)
        engine = FollowupEnforcementEngine(policy=policy)
        # Register 2 hours ago with 1h SLA → task is 1h overdue now
        past = _now() - timedelta(hours=2)
        lead = _lead(last_activity_at=past - timedelta(hours=1))
        engine.register_lead(lead, now=past)
        events = engine.process_due_transitions(now=_now())

        levels = [e.level for e in events]
        assert EscalationLevel.REMINDER in levels

    def test_warning_fires_after_warning_threshold(self) -> None:
        policy = FollowupPolicy(warm_sla_hours=1, warning_after_hours=2)
        engine = FollowupEnforcementEngine(policy=policy)
        past = _now() - timedelta(hours=4)  # 3h overdue
        lead = _lead(last_activity_at=past - timedelta(hours=1))
        engine.register_lead(lead, now=past)
        events = engine.process_due_transitions(now=_now())

        levels = [e.level for e in events]
        assert EscalationLevel.WARNING in levels

    def test_escalated_fires_after_escalation_threshold(self) -> None:
        policy = FollowupPolicy(warm_sla_hours=1, escalation_after_hours=2)
        engine = FollowupEnforcementEngine(policy=policy)
        past = _now() - timedelta(hours=4)  # 3h overdue, past escalation
        lead = _lead(last_activity_at=past - timedelta(hours=1))
        engine.register_lead(lead, now=past)
        events = engine.process_due_transitions(now=_now())

        levels = [e.level for e in events]
        assert EscalationLevel.ESCALATED in levels

    def test_reassigned_fires_after_reassignment_threshold(self) -> None:
        policy = FollowupPolicy(warm_sla_hours=1, reassignment_after_hours=2)
        engine = FollowupEnforcementEngine(policy=policy)
        past = _now() - timedelta(hours=4)  # 3h overdue, past reassignment
        lead = _lead(last_activity_at=past - timedelta(hours=1))
        engine.register_lead(lead, now=past)
        events = engine.process_due_transitions(now=_now())

        levels = [e.level for e in events]
        assert EscalationLevel.REASSIGNED in levels


# ── Inactivity rule ───────────────────────────────────────────────────────────


class TestInactivityRule:
    def test_inactivity_breach_creates_overdue_task(self) -> None:
        policy = FollowupPolicy(inactivity_hours=2, warm_sla_hours=1)
        engine = FollowupEnforcementEngine(policy=policy)
        now = _now()
        stale = now - timedelta(hours=3)  # inactive for 3h, threshold is 2h
        lead = _lead(last_activity_at=stale)
        engine.register_lead(lead, now=stale)

        # Clear existing tasks so inactivity creates a fresh one
        engine._tasks_by_lead["lead-001"] = []

        events = engine.process_due_transitions(now=now)
        tasks = engine.tasks_for_lead("lead-001")
        inactivity_tasks = [t for t in tasks if t.rule_type == "InactivityBased"]
        assert inactivity_tasks, "Expected InactivityBased task to be created"


# ── Closure gate ──────────────────────────────────────────────────────────────


class TestClosureGate:
    def test_strict_blocks_close_with_no_followup_history(self) -> None:
        engine = FollowupEnforcementEngine(enforcement_level="strict")
        lead = _lead()
        engine._leads["lead-001"] = lead

        with pytest.raises(FollowupPolicyError, match="CLOSE_BLOCKED_MISSING_FOLLOWUP_HISTORY"):
            engine.request_close_lead("lead-001", "Won the deal")

    def test_strict_blocks_close_with_unresolved_tasks(self) -> None:
        engine = FollowupEnforcementEngine(enforcement_level="strict")
        now = _now()
        engine.register_lead(_lead(), now=now)

        with pytest.raises(FollowupPolicyError, match="CLOSE_BLOCKED_UNRESOLVED_MANDATORY_TASKS"):
            engine.request_close_lead("lead-001", "Won the deal")

    def test_soft_allows_close_despite_violations(self) -> None:
        engine = FollowupEnforcementEngine(enforcement_level="soft")
        lead = _lead()
        engine._leads["lead-001"] = lead

        closed = engine.request_close_lead("lead-001", "Won the deal")
        assert closed.status == "closed"
        assert len(engine.violations()) >= 1

    def test_medium_warns_but_allows_close(self) -> None:
        engine = FollowupEnforcementEngine(enforcement_level="medium")
        lead = _lead()
        engine._leads["lead-001"] = lead

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            closed = engine.request_close_lead("lead-001", "Won the deal")

        assert closed.status == "closed"
        assert any(issubclass(warning.category, FollowupPolicyWarning) for warning in w)

    def test_successful_close_after_all_tasks_completed(self) -> None:
        engine = FollowupEnforcementEngine(enforcement_level="strict")
        now = _now()
        engine.register_lead(_lead(), now=now)
        engine.log_activity("lead-001", "call-001", now=now)

        tasks = engine.tasks_for_lead("lead-001")
        # Mark all tasks completed
        for task in tasks:
            engine._replace_task(task.patch(state=FollowupState.COMPLETED, completed_at=now))

        closed = engine.request_close_lead("lead-001", "Won the deal")
        assert closed.status == "closed"


# ── Metrics ───────────────────────────────────────────────────────────────────


class TestMetrics:
    def test_100_percent_compliance_when_all_on_time(self) -> None:
        engine = FollowupEnforcementEngine()
        now = _now()
        engine.register_lead(_lead(), now=now)
        task = engine.tasks_for_lead("lead-001")[0]
        completed = task.patch(
            state=FollowupState.COMPLETED,
            completed_at=task.due_at - timedelta(minutes=30),
        )
        engine._replace_task(completed)

        m = engine.metrics()
        assert m.compliance_percent == 100.0

    def test_overdue_reflects_in_metrics(self) -> None:
        engine = FollowupEnforcementEngine()
        now = _now()
        past = now - timedelta(hours=25)
        lead = _lead(last_activity_at=past - timedelta(hours=1))
        engine.register_lead(lead, now=past)
        engine.process_due_transitions(now=now)

        m = engine.metrics()
        assert m.overdue_percent > 0
