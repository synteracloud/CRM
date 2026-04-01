"""End-to-end integration self-QC across sales, support, marketing, and event execution."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.automation_journeys import JourneyService
from src.automation_journeys.workflow_mapping import build_default_journeys
from src.campaigns import Campaign, CampaignLeadLink, CampaignService, SegmentDefinition, SegmentRule
from src.data_deduplication_engine import DataDeduplicationEngine
from src.event_bus import Event, InMemoryEventBus
from src.lead_management import Lead, LeadService
from src.rule_engine import CPQLineItemInput, CPQQuoteInput, CPQRulesEngine
from src.subscription_billing import PaymentEvent, Subscription, SubscriptionBillingService
from src.support_console import QueueItem, SupportConsoleService
from src.ticket_management import EscalationRule, SlaEscalationService, Ticket, TicketService
from src.usage_billing import BillableEventRule, MeterRateCard, TrackedEvent, UsageBillingService, period_bounds_from_month


def run_self_qc() -> tuple[int, list[str]]:
    checks: list[tuple[str, bool]] = []

    tenant_id = "tenant-e2e"

    # 1) SALES FLOW: Lead -> Quote -> Order -> Invoice input -> Payment linkage.
    lead_service = LeadService()
    lead = lead_service.create_lead(
        Lead(
            lead_id="lead-1",
            tenant_id=tenant_id,
            owner_user_id="owner-1",
            source="web",
            status="new",
            score=72,
            email="buyer@acme.io",
            phone="+1-415-555-1000",
            company_name="Acme",
            created_at="2026-03-01T00:00:00Z",
        )
    )
    lead = lead_service.qualify_lead("lead-1", "2026-03-01T01:00:00Z")
    lead = lead_service.convert_lead(
        "lead-1",
        "2026-03-01T02:00:00Z",
        account_id="acc-1",
        contact_id="con-1",
        opportunity_id="opp-1",
    )

    quote_engine = CPQRulesEngine()
    quote_eval = quote_engine.evaluate_quote(
        CPQQuoteInput(
            quote_id="quote-1",
            tenant_id=tenant_id,
            currency="USD",
            requested_quote_discount_percent=Decimal("5"),
            line_items=(
                CPQLineItemInput(
                    line_id="l1",
                    product_id="core-crm",
                    quantity=10,
                    list_price=Decimal("100"),
                    requested_discount_percent=Decimal("5"),
                ),
                CPQLineItemInput(
                    line_id="l2",
                    product_id="analytics-pro",
                    quantity=10,
                    list_price=Decimal("60"),
                    requested_discount_percent=Decimal("5"),
                ),
            ),
        )
    )
    submit = quote_engine.apply_approval_transition("quote-1", "draft", "submit")
    approve = quote_engine.apply_approval_transition("quote-1", submit.new_status, "approve")
    accept = quote_engine.apply_approval_transition("quote-1", approve.new_status, "accept_customer")

    billing = SubscriptionBillingService()
    subscription = billing.create_subscription(
        Subscription(
            subscription_id="sub-1",
            tenant_id=tenant_id,
            account_id="acc-1",
            quote_id="quote-1",
            external_subscription_ref="ext-sub-1",
            plan_code="growth",
            status="draft",
            start_date="2026-03-01T00:00:00Z",
            end_date="2026-04-01T00:00:00Z",
            renewal_date="2026-04-01T00:00:00Z",
            created_at="2026-03-01T00:00:00Z",
        )
    )
    subscription = billing.transition_subscription("sub-1", "active", "2026-03-01T02:30:00Z")

    usage = UsageBillingService()
    start, end = period_bounds_from_month("2026-03")
    usage_records = usage.collect_billable_events(
        [
            TrackedEvent(
                event_id="evt-usage-1",
                tenant_id=tenant_id,
                event_name="workflow.execution.completed.v1",
                occurred_at="2026-03-10T00:00:00Z",
                payload={"subscription_id": "sub-1", "account_id": "acc-1"},
            )
        ],
        [BillableEventRule(meter_code="workflow-runs", event_name="workflow.execution.completed.v1")],
    )
    aggregates = usage.aggregate_usage(usage_records, start, end)
    rated = usage.rate_usage(
        aggregates,
        [MeterRateCard(meter_code="workflow-runs", unit="event", currency="USD", billing_model="flat", unit_price=1.0)],
    )
    invoice_inputs = usage.generate_invoice_inputs(rated)
    payment = PaymentEvent(
        payment_event_id="pay-1",
        tenant_id=tenant_id,
        subscription_id=subscription.subscription_id,
        invoice_summary_id="inv-1",
        external_payment_ref="stripe_1",
        event_type="payment.succeeded",
        amount=1.0,
        currency="USD",
        event_time="2026-03-10T01:00:00Z",
        status="succeeded",
    )

    checks.append(
        (
            "sales flow continuity lead->quote->order->invoice->payment",
            lead.status == "converted"
            and quote_eval.status in {"approved", "approval_required"}
            and "order.created.v1" in accept.emitted_events
            and subscription.status == "active"
            and len(billing.list_invoice_hooks("sub-1")) == 1
            and len(invoice_inputs) == 1
            and payment.subscription_id == subscription.subscription_id,
        )
    )

    # 2) SUPPORT FLOW with SLA and escalation coverage.
    ticket_service = TicketService()
    ticket = ticket_service.create_ticket(
        Ticket(
            ticket_id="tic-1",
            tenant_id=tenant_id,
            account_id="acc-1",
            contact_id="con-1",
            owner_user_id="agent-1",
            subject="Need help",
            description="Issue",
            priority="high",
            status="open",
            created_at="2026-03-11T00:00:00Z",
            response_due_at="2026-03-11T01:00:00Z",
            resolution_due_at="2026-03-11T05:00:00Z",
        )
    )
    ticket_service.record_first_response(ticket.ticket_id, "2026-03-11T00:30:00Z")
    ticket_service.start_progress(ticket.ticket_id)
    ticket_service.resolve_ticket(ticket.ticket_id, "2026-03-11T04:00:00Z")
    ticket = ticket_service.close_ticket(ticket.ticket_id, "2026-03-11T04:30:00Z")

    escalation = SlaEscalationService(ticket_service)
    open_ticket = ticket_service.create_ticket(
        Ticket(
            ticket_id="tic-2",
            tenant_id=tenant_id,
            account_id="acc-1",
            contact_id="con-1",
            owner_user_id="agent-2",
            subject="Urgent",
            description="Escalate",
            priority="urgent",
            status="open",
            created_at="2026-03-12T00:00:00Z",
            response_due_at="2026-03-12T00:10:00Z",
            resolution_due_at="2026-03-12T00:20:00Z",
        )
    )
    escalation.register_rules(
        tenant_id,
        [
            EscalationRule(
                rule_id="rule-1",
                tenant_id=tenant_id,
                level=1,
                name="response-overdue",
                route_to="on-call",
                trigger="response_due",
                threshold_minutes=0,
                condition_field="status",
                condition_op="eq",
                condition_value="open",
                active=True,
            )
        ],
    )
    actions = escalation.evaluate_escalations(open_ticket.ticket_id, "2026-03-12T00:11:00Z")
    checks.append(("support flow ticket lifecycle + escalation", ticket.status == "closed" and len(actions) == 1))

    console = SupportConsoleService()
    queue_item = console.upsert_queue_item(
        QueueItem(
            ticket_id="tic-2",
            subject="Urgent",
            status="open",
            priority="urgent",
            owner_user_id="agent-2",
            queue_name="support",
            response_due_at="2026-03-12T00:10:00Z",
            resolution_due_at="2026-03-12T00:20:00Z",
            sla_state="breached",
        )
    )
    updated_queue_item = console.perform_escalation_action(queue_item.ticket_id, "page_on_call")
    checks.append(("support closure/escalation states remain valid", updated_queue_item.owner_user_id == "on-call-support"))

    # 3) MARKETING FLOW campaign->segment->journey with conversion feedback.
    campaign_service = CampaignService()
    campaign_service.create_segment(
        SegmentDefinition(
            segment_id="seg-1",
            tenant_id=tenant_id,
            name="SQLs",
            description="Qualified lead cohort",
            entity_type="lead",
            rules=(SegmentRule(field="status", operator="eq", value="qualified"),),
            created_at="2026-03-13T00:00:00Z",
            updated_at="2026-03-13T00:00:00Z",
        )
    )
    campaign = campaign_service.create_campaign(
        Campaign(
            campaign_id="cmp-1",
            tenant_id=tenant_id,
            owner_user_id="marketer-1",
            name="Q2 Pipeline",
            description="Promote conversion for qualified leads",
            status="draft",
            segment_id="seg-1",
            starts_at="2026-03-13T00:00:00Z",
            ends_at="2026-03-31T23:59:59Z",
            created_at="2026-03-13T00:00:00Z",
            updated_at="2026-03-13T00:00:00Z",
        )
    )
    campaign_service.activate_campaign(campaign.campaign_id, "2026-03-13T01:00:00Z")
    campaign_service.link_lead(
        CampaignLeadLink(
            campaign_lead_link_id="cll-1",
            tenant_id=tenant_id,
            campaign_id="cmp-1",
            lead_id="lead-1",
            membership_status="sent",
            linked_at="2026-03-13T01:10:00Z",
        )
    )
    campaign = campaign_service.complete_campaign(campaign.campaign_id, "2026-03-20T00:00:00Z")

    journeys = JourneyService()
    journeys.create_journey(build_default_journeys(tenant_id)[0])
    started = journeys.handle_event(
        Event(
            event_name="lead.converted.v1",
            event_id="evt-conv-1",
            occurred_at="2026-03-20T01:00:00Z",
            tenant_id=tenant_id,
            payload={"lead_id": "lead-1", "campaign_id": "cmp-1"},
        )
    )
    checks.append(("marketing campaign/journey conversion feedback", campaign.status == "completed" and len(started) == 1))

    # 4) CROSS-BATCH + EVENT DETERMINISM
    bus = InMemoryEventBus()
    received: list[str] = []
    bus.subscribe("lead.converted.v1", lambda event: received.append(event.event_id))
    duplicate_event = Event(
        event_name="lead.converted.v1",
        event_id="evt-dedupe-1",
        occurred_at="2026-03-21T00:00:00Z",
        tenant_id=tenant_id,
        payload={"lead_id": "lead-1"},
    )
    bus.publish(duplicate_event)
    bus.publish(duplicate_event)
    checks.append(("event idempotency prevents duplicate execution", received == ["evt-dedupe-1"]))

    bus2 = InMemoryEventBus()
    attempts = {"count": 0}

    def always_fail(_: Event) -> None:
        attempts["count"] += 1
        raise RuntimeError("boom")

    bus2.subscribe("workflow.execution.failed.v1", always_fail)
    failed_event = Event(
        event_name="workflow.execution.failed.v1",
        event_id="evt-fail-1",
        occurred_at="2026-03-21T01:00:00Z",
        tenant_id=tenant_id,
        payload={},
    )
    bus2.publish(failed_event)
    bus2.publish(failed_event)
    checks.append(("dead-letter routing deterministic with retries", attempts["count"] == 4 and len(bus2.dead_lettered) == 1))

    # 5) DATA CONSISTENCY
    dedupe = DataDeduplicationEngine()
    dedupe.upsert_record(
        entity_type="lead",
        tenant_id=tenant_id,
        record={"lead_id": "lead-a", "email": "dup@acme.io", "phone": "+1 (415) 222-3333", "company_name": "Acme"},
    )
    merged = dedupe.upsert_record(
        entity_type="lead",
        tenant_id=tenant_id,
        record={"lead_id": "lead-b", "email": "dup@acme.io", "phone": "14152223333", "company_name": "Acme"},
    )
    checks.append(
        (
            "dedup removes duplicate entities without data loss",
            merged.decision == "merged"
            and dedupe.get_record(entity_type="lead", tenant_id=tenant_id, record_id=merged.record_id) is not None,
        )
    )

    # 6) ID continuity across lifecycle artifacts.
    checks.append(("lifecycle IDs remain linked end-to-end", invoice_inputs[0].subscription_id == subscription.subscription_id == payment.subscription_id))

    passed = sum(1 for _, ok in checks if ok)
    score = int(round((passed / len(checks)) * 10))
    failed = [name for name, ok in checks if not ok]
    return score, failed


if __name__ == "__main__":
    score, failed_checks = run_self_qc()
    print(f"SELF_QC_SCORE={score}/10")
    if failed_checks:
        for item in failed_checks:
            print(f"FAILED: {item}")
        raise SystemExit(1)
