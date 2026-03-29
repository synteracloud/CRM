"""Billing workflows for subscription lifecycle and recurring invoicing."""

from __future__ import annotations

from dataclasses import dataclass


WORKFLOW_NAME = "subscription_billing"


@dataclass(frozen=True)
class BillingWorkflowStep:
    step_id: str
    trigger: str
    action: str
    outcome: str


BILLING_WORKFLOWS: tuple[BillingWorkflowStep, ...] = (
    BillingWorkflowStep(
        step_id="subscription-create",
        trigger="quote.accepted.v1",
        action="create subscription in draft and activate after provisioning checks",
        outcome="subscription.created.v1 emitted",
    ),
    BillingWorkflowStep(
        step_id="subscription-renewal",
        trigger="renewal scheduler tick",
        action="execute deterministic renewal_date match and enqueue recurring invoice hook",
        outcome="invoice.summary.updated.v1 emitted after invoice service completion",
    ),
    BillingWorkflowStep(
        step_id="subscription-upgrade",
        trigger="plan change request: upgrade",
        action="apply plan immediately and enqueue proration invoice hook",
        outcome="subscription.status.changed.v1 and invoice.summary.updated.v1",
    ),
    BillingWorkflowStep(
        step_id="subscription-downgrade",
        trigger="plan change request: downgrade",
        action="schedule plan for next renewal boundary",
        outcome="subscription.status.changed.v1 emitted at renewal boundary",
    ),
)
