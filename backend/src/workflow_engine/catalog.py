"""Canonical workflow definitions aligned to docs/workflow-catalog.md."""

from __future__ import annotations

from .entities import (
    ActionDefinition,
    ConditionDefinition,
    ConditionRule,
    SequencingDefinition,
    TriggerDefinition,
    WorkflowDefinition,
    WorkflowStep,
)


def build_canonical_workflows() -> tuple[WorkflowDefinition, ...]:
    return (
        _tenant_provisioning(),
        _identity_access(),
        _lead_intake_conversion(),
        _contact_account_management(),
        _opportunity_pipeline(),
        _quote_approval_acceptance(),
        _subscription_lifecycle(),
        _case_management_sla(),
    )


def _tenant_provisioning() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_key="tenant_provisioning_entitlement",
        version="v1",
        metadata={"name": "Tenant provisioning & entitlement", "domain": "platform"},
        triggers=TriggerDefinition(mode="any", events=("tenant.provisioned.v1", "tenant.entitlement.updated.v1")),
        conditions=ConditionDefinition(match="all", rules=(ConditionRule("tenant_id", "exists", True),)),
        sequencing=SequencingDefinition(
            strategy="linear",
            on_error="fail_fast",
            steps=(
                WorkflowStep("init_flags", "init_flags"),
                WorkflowStep("init_identity", "init_identity"),
                WorkflowStep("audit", "audit"),
                WorkflowStep("index_tenant", "index_tenant"),
                WorkflowStep("evaluate_automations", "evaluate_automations"),
                WorkflowStep("update_metrics", "update_metrics"),
            ),
        ),
        actions={
            "init_flags": ActionDefinition("call_service", "Feature Flag Service", "initialize_tenant_context"),
            "init_identity": ActionDefinition("call_service", "Identity & Access Service", "initialize_boundary"),
            "audit": ActionDefinition("call_service", "Audit & Compliance Service", "record_provisioning"),
            "index_tenant": ActionDefinition("call_service", "Search Index Service", "upsert_tenant"),
            "evaluate_automations": ActionDefinition(
                "call_service", "Workflow Automation Service", "evaluate_entitlements"
            ),
            "update_metrics": ActionDefinition("call_service", "Analytics & Reporting Service", "update_tenant_plan_metrics"),
        },
    )


def _identity_access() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_key="identity_access_lifecycle",
        version="v1",
        metadata={"name": "Identity & access lifecycle", "domain": "identity"},
        triggers=TriggerDefinition(mode="any", events=("identity.user.provisioned.v1", "identity.user.role.assigned.v1")),
        conditions=ConditionDefinition(),
        sequencing=SequencingDefinition(
            strategy="linear",
            on_error="continue",
            steps=(
                WorkflowStep("notify_user", "notify_user"),
                WorkflowStep("audit_user", "audit_user"),
                WorkflowStep("metrics", "metrics"),
                WorkflowStep("recalc_features", "recalc_features", when="event == 'identity.user.role.assigned.v1'"),
            ),
        ),
        actions={
            "notify_user": ActionDefinition("notify", "Notification Orchestrator", "send_onboarding"),
            "audit_user": ActionDefinition("call_service", "Audit & Compliance Service", "record_identity_change"),
            "metrics": ActionDefinition("call_service", "Analytics & Reporting Service", "update_user_lifecycle_metrics"),
            "recalc_features": ActionDefinition("call_service", "Feature Flag Service", "recalculate_role_exposure"),
        },
    )


def _lead_intake_conversion() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_key="lead_intake_assignment_conversion",
        version="v1",
        metadata={"name": "Lead intake, assignment, conversion", "domain": "sales"},
        triggers=TriggerDefinition(mode="any", events=("lead.created.v1", "lead.assignment.updated.v1", "lead.converted.v1")),
        conditions=ConditionDefinition(match="all", rules=(ConditionRule("tenant_id", "exists", True),)),
        sequencing=SequencingDefinition(
            strategy="linear",
            on_error="fail_fast",
            steps=(
                WorkflowStep("compute_assignment", "compute_assignment", when="event == 'lead.created.v1'"),
                WorkflowStep("notify_owner", "notify_owner", when="event == 'lead.assignment.updated.v1'"),
                WorkflowStep("append_timeline", "append_timeline"),
                WorkflowStep("index_lead", "index_lead"),
                WorkflowStep("run_conversion", "run_conversion", when="event == 'lead.converted.v1'"),
                WorkflowStep("update_conversion_metrics", "update_conversion_metrics", when="event == 'lead.converted.v1'"),
            ),
        ),
        actions={
            "compute_assignment": ActionDefinition("call_service", "Territory & Assignment Service", "compute_and_assign"),
            "notify_owner": ActionDefinition("notify", "Notification Orchestrator", "notify_assigned_owner"),
            "append_timeline": ActionDefinition("call_service", "Activity Timeline Service", "append_event"),
            "index_lead": ActionDefinition("call_service", "Search Index Service", "upsert_lead"),
            "run_conversion": ActionDefinition("call_service", "Workflow Automation Service", "run_conversion_playbook"),
            "update_conversion_metrics": ActionDefinition(
                "call_service", "Analytics & Reporting Service", "update_funnel_metrics"
            ),
        },
    )


def _contact_account_management() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_key="contact_account_management",
        version="v1",
        metadata={"name": "Contact & account management", "domain": "crm"},
        triggers=TriggerDefinition(
            mode="any",
            events=("contact.created.v1", "contact.merged.v1", "account.created.v1", "account.hierarchy.updated.v1"),
        ),
        conditions=ConditionDefinition(),
        sequencing=SequencingDefinition(
            strategy="linear",
            on_error="continue",
            steps=(
                WorkflowStep("record_timeline", "record_timeline", when="event == 'contact.created.v1'"),
                WorkflowStep("index_projection", "index_projection"),
                WorkflowStep("quality_checks", "quality_checks", when="event == 'contact.created.v1'"),
                WorkflowStep("audit_merge", "audit_merge", when="event == 'contact.merged.v1'"),
                WorkflowStep("evaluate_territory", "evaluate_territory", when="event == 'account.created.v1'"),
                WorkflowStep("refresh_rollups", "refresh_rollups", when="event == 'account.hierarchy.updated.v1'"),
            ),
        ),
        actions={
            "record_timeline": ActionDefinition("call_service", "Activity Timeline Service", "append_event"),
            "index_projection": ActionDefinition("call_service", "Search Index Service", "upsert_projection"),
            "quality_checks": ActionDefinition("call_service", "Data Quality Service", "evaluate_duplicates"),
            "audit_merge": ActionDefinition("call_service", "Audit & Compliance Service", "record_merge"),
            "evaluate_territory": ActionDefinition("call_service", "Territory & Assignment Service", "evaluate_account_owner"),
            "refresh_rollups": ActionDefinition("call_service", "Analytics & Reporting Service", "refresh_hierarchy_rollups"),
        },
    )


def _opportunity_pipeline() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_key="opportunity_pipeline_close_outcomes",
        version="v1",
        metadata={"name": "Opportunity pipeline & close outcomes", "domain": "sales"},
        triggers=TriggerDefinition(mode="any", events=("opportunity.created.v1", "opportunity.stage.changed.v1", "opportunity.closed.v1")),
        conditions=ConditionDefinition(),
        sequencing=SequencingDefinition(
            strategy="linear",
            on_error="continue",
            steps=(
                WorkflowStep("timeline", "timeline"),
                WorkflowStep("assignment", "assignment", when="event != 'opportunity.closed.v1'"),
                WorkflowStep("run_stage_automation", "run_stage_automation", when="event == 'opportunity.stage.changed.v1'"),
                WorkflowStep("notify_stage_change", "notify_stage_change", when="event == 'opportunity.stage.changed.v1'"),
                WorkflowStep("close_playbook", "close_playbook", when="event == 'opportunity.closed.v1'"),
                WorkflowStep("metrics", "metrics"),
            ),
        ),
        actions={
            "timeline": ActionDefinition("call_service", "Activity Timeline Service", "append_opportunity_event"),
            "assignment": ActionDefinition("call_service", "Territory & Assignment Service", "evaluate_ownership"),
            "run_stage_automation": ActionDefinition("call_service", "Workflow Automation Service", "run_stage_actions"),
            "notify_stage_change": ActionDefinition("notify", "Notification Orchestrator", "send_stage_change_alert"),
            "close_playbook": ActionDefinition("call_service", "Workflow Automation Service", "run_close_playbook"),
            "metrics": ActionDefinition("call_service", "Analytics & Reporting Service", "update_opportunity_metrics"),
        },
    )


def _quote_approval_acceptance() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_key="quote_approval_acceptance",
        version="v1",
        metadata={"name": "Quote, approval, acceptance", "domain": "cpq"},
        triggers=TriggerDefinition(
            mode="any",
            events=(
                "quote.created.v1",
                "quote.submitted_for_approval.v1",
                "approval.requested.v1",
                "approval.decided.v1",
                "quote.accepted.v1",
                "order.created.v1",
            ),
        ),
        conditions=ConditionDefinition(),
        sequencing=SequencingDefinition(
            strategy="linear",
            on_error="fail_fast",
            steps=(
                WorkflowStep("timeline", "timeline", when="event == 'quote.created.v1'"),
                WorkflowStep("policy_eval", "policy_eval"),
                WorkflowStep("notify_approvers", "notify_approvers", when="event == 'approval.requested.v1'"),
                WorkflowStep("audit", "audit", when="event == 'approval.requested.v1'"),
                WorkflowStep("decision_notify", "decision_notify", when="event == 'approval.decided.v1'"),
                WorkflowStep("convert_order", "convert_order", when="event == 'quote.accepted.v1'"),
                WorkflowStep("update_metrics", "update_metrics"),
            ),
        ),
        actions={
            "timeline": ActionDefinition("call_service", "Activity Timeline Service", "append_quote_event"),
            "policy_eval": ActionDefinition("call_service", "Approval Service", "evaluate_policy"),
            "notify_approvers": ActionDefinition("notify", "Notification Orchestrator", "notify_approvers"),
            "audit": ActionDefinition("call_service", "Audit & Compliance Service", "record_approval_transition"),
            "decision_notify": ActionDefinition("notify", "Notification Orchestrator", "notify_requester_decision"),
            "convert_order": ActionDefinition("call_service", "Order Service", "convert_quote_to_order"),
            "update_metrics": ActionDefinition("call_service", "Analytics & Reporting Service", "update_quote_conversion"),
        },
    )


def _subscription_lifecycle() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_key="subscription_invoicing_payments",
        version="v1",
        metadata={"name": "Subscription, invoicing, payments", "domain": "billing"},
        triggers=TriggerDefinition(
            mode="any",
            events=(
                "subscription.created.v1",
                "subscription.status.changed.v1",
                "invoice.summary.updated.v1",
                "payment.event.recorded.v1",
            ),
        ),
        conditions=ConditionDefinition(),
        sequencing=SequencingDefinition(
            strategy="linear",
            on_error="continue",
            steps=(
                WorkflowStep("tenant_sync", "tenant_sync", when="event == 'subscription.created.v1'"),
                WorkflowStep("search_sync", "search_sync", when="event == 'subscription.created.v1'"),
                WorkflowStep("status_notify", "status_notify", when="event == 'subscription.status.changed.v1'"),
                WorkflowStep("lifecycle_automation", "lifecycle_automation", when="event == 'subscription.status.changed.v1'"),
                WorkflowStep("invoice_notify", "invoice_notify", when="event == 'invoice.summary.updated.v1'"),
                WorkflowStep("payment_followups", "payment_followups", when="event == 'payment.event.recorded.v1'"),
                WorkflowStep("audit", "audit", when="event == 'payment.event.recorded.v1'"),
                WorkflowStep("metrics", "metrics"),
            ),
        ),
        actions={
            "tenant_sync": ActionDefinition("call_service", "Organization & Tenant Service", "sync_subscription_context"),
            "search_sync": ActionDefinition("call_service", "Search Index Service", "upsert_subscription"),
            "status_notify": ActionDefinition("notify", "Notification Orchestrator", "send_subscription_status"),
            "lifecycle_automation": ActionDefinition("call_service", "Workflow Automation Service", "run_lifecycle_actions"),
            "invoice_notify": ActionDefinition("notify", "Notification Orchestrator", "send_invoice_summary"),
            "payment_followups": ActionDefinition("call_service", "Workflow Automation Service", "run_payment_followups"),
            "audit": ActionDefinition("call_service", "Audit & Compliance Service", "record_payment_lifecycle"),
            "metrics": ActionDefinition("call_service", "Analytics & Reporting Service", "refresh_revenue_metrics"),
        },
    )


def _case_management_sla() -> WorkflowDefinition:
    return WorkflowDefinition(
        workflow_key="case_management_sla",
        version="v1",
        metadata={"name": "Case management & SLA", "domain": "support"},
        triggers=TriggerDefinition(mode="any", events=("case.created.v1", "case.sla.breached.v1", "case.resolved.v1")),
        conditions=ConditionDefinition(),
        sequencing=SequencingDefinition(
            strategy="branching",
            on_error="continue",
            steps=(
                WorkflowStep("notify_case", "notify_case", next="timeline", when="event == 'case.created.v1'"),
                WorkflowStep("timeline", "timeline", next="index_case"),
                WorkflowStep("index_case", "index_case", next="sla_automation", when="event == 'case.sla.breached.v1'"),
                WorkflowStep("sla_automation", "sla_automation", next="metrics"),
                WorkflowStep("metrics", "metrics", next="end"),
            ),
        ),
        actions={
            "notify_case": ActionDefinition("notify", "Notification Orchestrator", "send_case_notifications"),
            "timeline": ActionDefinition("call_service", "Activity Timeline Service", "append_case_event"),
            "index_case": ActionDefinition("call_service", "Search Index Service", "upsert_case"),
            "sla_automation": ActionDefinition("call_service", "Workflow Automation Service", "run_sla_escalation"),
            "metrics": ActionDefinition("call_service", "Analytics & Reporting Service", "update_case_metrics"),
        },
    )
