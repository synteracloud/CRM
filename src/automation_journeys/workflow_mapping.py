"""Journey definitions aligned to docs/workflow-catalog.md."""

from __future__ import annotations

from .entities import JourneyDefinition, JourneyStep


def build_default_journeys(tenant_id: str) -> tuple[JourneyDefinition, ...]:
    return (
        JourneyDefinition(
            journey_id="lead-conversion-playbook",
            tenant_id=tenant_id,
            name="Lead conversion follow-up",
            trigger_event="lead.converted.v1",
            steps=(
                JourneyStep("assign-ae", "assign", {"assignee": "queue:account-executive"}),
                JourneyStep("update-lifecycle", "update", {"entity": "lead", "fields": {"status": "converted"}}),
                JourneyStep("send-intro-email", "email", {"template": "lead-conversion-welcome"}),
            ),
        ),
        JourneyDefinition(
            journey_id="opportunity-stage-playbook",
            tenant_id=tenant_id,
            name="Opportunity stage progression",
            trigger_event="opportunity.stage.changed.v1",
            steps=(
                JourneyStep("update-stage-flag", "update", {"entity": "opportunity", "fields": {"at_risk": False}}),
                JourneyStep("wait-for-follow-up", "delay", delay_seconds=3600),
                JourneyStep("email-owner", "email", {"template": "opportunity-stage-followup"}),
            ),
        ),
        JourneyDefinition(
            journey_id="subscription-retention",
            tenant_id=tenant_id,
            name="Subscription retention",
            trigger_event="subscription.status.changed.v1",
            steps=(
                JourneyStep("wait-grace-period", "delay", delay_seconds=86400),
                JourneyStep("send-retention-email", "email", {"template": "subscription-recovery"}),
                JourneyStep("assign-csm", "assign", {"assignee": "queue:customer-success"}),
                JourneyStep("mark-retention", "update", {"entity": "subscription", "fields": {"retention_playbook": True}}),
            ),
        ),
    )
