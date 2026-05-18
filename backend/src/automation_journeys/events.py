"""Journey trigger bindings and catalog alignment helpers."""

from __future__ import annotations

from src.event_bus import EVENT_NAMES


WORKFLOW_AUTOMATION_TRIGGER_EVENTS: tuple[str, ...] = (
    "tenant.entitlement.updated.v1",
    "lead.converted.v1",
    "opportunity.stage.changed.v1",
    "opportunity.closed.v1",
    "approval.requested.v1",
    "subscription.status.changed.v1",
    "payment.event.recorded.v1",
    "case.sla.breached.v1",
    "communication.message.engagement.updated.v1",
    "notification.failed.v1",
    "eventbus.dead_lettered.v1",
    "job.enqueued.v1",
    "job.succeeded.v1",
    "job.retry.scheduled.v1",
    "job.dead_lettered.v1",
    "feature_flag.updated.v1",
)


TRIGGER_EVENT_BINDINGS: dict[str, tuple[str, ...]] = {
    "tenant-entitlement-guardrails": ("tenant.entitlement.updated.v1",),
    "lead-conversion-playbook": ("lead.converted.v1",),
    "opportunity-stage-playbook": ("opportunity.stage.changed.v1", "opportunity.closed.v1"),
    "approval-followup": ("approval.requested.v1",),
    "subscription-retention": ("subscription.status.changed.v1", "payment.event.recorded.v1"),
    "case-escalation": ("case.sla.breached.v1",),
    "engagement-nurture": ("communication.message.engagement.updated.v1",),
    "notification-recovery": ("notification.failed.v1",),
    "platform-reliability": (
        "eventbus.dead_lettered.v1",
        "job.enqueued.v1",
        "job.succeeded.v1",
        "job.retry.scheduled.v1",
        "job.dead_lettered.v1",
    ),
    "feature-rollout-communications": ("feature_flag.updated.v1",),
}


def assert_triggers_in_catalog() -> None:
    catalog = set(EVENT_NAMES)
    missing = [event_name for event_name in WORKFLOW_AUTOMATION_TRIGGER_EVENTS if event_name not in catalog]
    if missing:
        raise AssertionError(f"Trigger events missing from event catalog: {missing}")

    binding_events = {event for events in TRIGGER_EVENT_BINDINGS.values() for event in events}
    not_covered = sorted(set(WORKFLOW_AUTOMATION_TRIGGER_EVENTS) - binding_events)
    if not_covered:
        raise AssertionError(f"Workflow trigger events without journey bindings: {not_covered}")
