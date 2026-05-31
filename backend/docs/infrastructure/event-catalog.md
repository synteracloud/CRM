<!-- OWNERSHIP
PRIMARY FOR: Canonical event names with .v1 versioning suffix, event payload schemas, dedup rule (tenant_id, event_name, event_id). Authoritative list of all system events.
DEFERS TO: domain-model.md (entity field shapes in event payloads).
DO NOT RE-DEFINE: Nothing — all other files must point here for event names and payloads.
-->

# CRM Event Catalog

This catalog defines the canonical system events exchanged across services.

## Invariants

- Every workflow in the CRM service map is represented by one or more events.
- Every event has at least one producer and at least one consumer (no orphan events).
- Event payload fields align with the domain model entities in `docs/architecture/domain-model.md`.
- Every event MUST carry a producer-stable `event_id` that is preserved across retries and replay.
- Consumers MUST dedupe processing by `(tenant_id, event_name, event_id)` before side effects.

## System Events

| Workflow | Event Name | Trigger | Payload Schema (JSON-like) | Producer | Consumers |
|---|---|---|---|---|---|
| Tenant provisioning & entitlement | `tenant.provisioned.v1` | New tenant is created and activated. | `{ event_id, occurred_at, tenant_id, name, status, region, timezone, default_locale }` | Organization & Tenant Service | Feature Flag Service; Identity & Access Service; Audit & Compliance Service; Search Index Service |
| Tenant provisioning & entitlement | `tenant.entitlement.updated.v1` | Plan or feature entitlements change for a tenant. | `{ event_id, occurred_at, entitlement_id, tenant_id, plan_code, feature_code, limit_value, effective_from, effective_to }` | Organization & Tenant Service | Feature Flag Service; Workflow Automation Service; Analytics & Reporting Service |
| Identity & access lifecycle | `identity.user.provisioned.v1` | User record is created for a tenant. | `{ event_id, occurred_at, user_id, tenant_id, email, display_name, status, created_at }` | Identity & Access Service | Notification Orchestrator; Audit & Compliance Service; Analytics & Reporting Service |
| Identity & access lifecycle | `identity.user.role.assigned.v1` | Role assignment is added for a user. | `{ event_id, occurred_at, user_role_id, tenant_id, user_id, role_id, assigned_by_user_id, assigned_at }` | Identity & Access Service | Audit & Compliance Service; Feature Flag Service |
| Lead intake, assignment, conversion | `lead.created.v1` | Lead is captured from form/import/manual entry. | `{ event_id, occurred_at, lead_id, tenant_id, owner_user_id, source, status, score, email, phone, company_name, created_at }` | Lead Management Service | Territory & Assignment Service; Data Quality Service; Activity Timeline Service; Search Index Service |
| Lead intake, assignment, conversion | `lead.assignment.updated.v1` | Lead owner assignment is created or changed. | `{ event_id, occurred_at, lead_assignment_id, tenant_id, lead_id, assigned_user_id, assignment_rule, assigned_at }` | Territory & Assignment Service | Lead Management Service; Notification Orchestrator; Activity Timeline Service |
| Lead intake, assignment, conversion | `lead.converted.v1` | Lead is converted into account/contact and optional opportunity. | `{ event_id, occurred_at, lead_id, tenant_id, converted_at, account_id, contact_id, opportunity_id }` | Lead Management Service | Contact Service; Account Service; Opportunity Service; Workflow Automation Service; Analytics & Reporting Service |
| Lead intake, assignment, conversion | `lead.conversion.failed.v1` | Lead conversion saga failed and was compensated — opportunity soft-deleted if partially created. | `{ event_id, occurred_at, lead_id, tenant_id, failure_reason, compensation_action, failed_at }` | Lead Management Service | Workflow Automation Service; Notification Orchestrator; Audit & Compliance Service |
| Contact & account management | `contact.created.v1` | New contact is created. | `{ event_id, occurred_at, contact_id, tenant_id, account_id, owner_user_id, first_name, last_name, email, phone, lifecycle_status, created_at }` | Contact Service | Activity Timeline Service; Search Index Service; Data Quality Service |
| Contact & account management | `contact.merged.v1` | Duplicate contacts are merged into a survivor record. | `{ event_id, occurred_at, tenant_id, survivor_contact_id, merged_contact_ids[], merged_by_user_id }` | Contact Service | Search Index Service; Analytics & Reporting Service; Audit & Compliance Service |
| Contact & account management | `account.created.v1` | New account is created. | `{ event_id, occurred_at, account_id, tenant_id, owner_user_id, name, industry, segment, status, billing_address, created_at }` | Account Service | Activity Timeline Service; Search Index Service; Territory & Assignment Service |
| Contact & account management | `account.hierarchy.updated.v1` | Parent-child account relationship is added/changed. | `{ event_id, occurred_at, account_hierarchy_id, tenant_id, parent_account_id, child_account_id, relationship_type, created_at }` | Account Service | Analytics & Reporting Service; Search Index Service |
| Opportunity pipeline & close outcomes | `opportunity.created.v1` | Opportunity is created from account/contact or lead conversion. | `{ event_id, occurred_at, opportunity_id, tenant_id, account_id, primary_contact_id, owner_user_id, name, stage, amount, close_date, forecast_category, is_closed, is_won, created_at }` | Opportunity Service | Activity Timeline Service; Analytics & Reporting Service; Territory & Assignment Service |
| Opportunity pipeline & close outcomes | `opportunity.stage.changed.v1` | Opportunity stage or forecast category changes. | `{ event_id, occurred_at, opportunity_id, tenant_id, previous_stage, stage, forecast_category, amount, close_date, is_closed, is_won, updated_at }` | Opportunity Service | Workflow Automation Service; Analytics & Reporting Service; Notification Orchestrator |
| Opportunity pipeline & close outcomes | `opportunity.closed.v1` | Opportunity is moved to closed won/lost state. | `{ event_id, occurred_at, opportunity_id, tenant_id, stage, is_won, is_closed, amount, close_date, updated_at }` | Opportunity Service | Analytics & Reporting Service; Activity Timeline Service; Workflow Automation Service |
| Quote, approval, acceptance | `quote.created.v1` | Quote is created for an opportunity. | `{ event_id, occurred_at, quote_id, tenant_id, opportunity_id, status, currency, subtotal, discount_total, tax_total, grand_total, valid_until, created_at }` | Quote Service | Approval Service; Activity Timeline Service; Analytics & Reporting Service |
| Quote, approval, acceptance | `quote.submitted_for_approval.v1` | Quote state transitions to approval-required. | `{ event_id, occurred_at, quote_id, tenant_id, opportunity_id, status, grand_total, requested_by_user_id }` | Quote Service | Approval Service; Notification Orchestrator |
| Quote, approval, acceptance | `approval.requested.v1` | Approval request is created for a protected resource. | `{ event_id, occurred_at, approval_request_id, tenant_id, resource_type, resource_id, requested_by_user_id, assigned_approver_user_id, status, policy_code, requested_at }` | Approval Service | Notification Orchestrator; Audit & Compliance Service; Workflow Automation Service |
| Quote, approval, acceptance | `approval.decided.v1` | Approver approves or rejects request. | `{ event_id, occurred_at, approval_request_id, tenant_id, resource_type, resource_id, status, assigned_approver_user_id, decided_at }` | Approval Service | Quote Service; Notification Orchestrator; Audit & Compliance Service |
| Quote, approval, acceptance | `quote.accepted.v1` | Customer accepts quote. | `{ event_id, occurred_at, quote_id, tenant_id, opportunity_id, status, accepted_at, grand_total, currency }` | Quote Service | Billing & Subscription Service; Opportunity Service; Analytics & Reporting Service |
| Quote, approval, acceptance | `order.created.v1` | Accepted quote is converted into an order. | `{ event_id, occurred_at, order_id, tenant_id, quote_id, opportunity_id, status, currency, subtotal, discount_total, tax_total, grand_total, ordered_at, created_at }` | Order Service | Billing & Subscription Service; Opportunity Service; Analytics & Reporting Service |
| Subscription, invoicing, payments | `subscription.created.v1` | Subscription is created from accepted quote or plan action. | `{ event_id, occurred_at, subscription_id, tenant_id, account_id, quote_id, external_subscription_ref, plan_code, status, start_date, end_date, renewal_date, created_at }` | Billing & Subscription Service | Organization & Tenant Service; Analytics & Reporting Service; Search Index Service |
| Subscription, invoicing, payments | `subscription.status.changed.v1` | Subscription status changes (active, past_due, canceled, etc.). | `{ event_id, occurred_at, subscription_id, tenant_id, account_id, previous_status, status, renewal_date, updated_at }` | Billing & Subscription Service | Notification Orchestrator; Workflow Automation Service; Analytics & Reporting Service |
| Subscription, invoicing, payments | `invoice.summary.updated.v1` | Invoice mirror is created or status is updated. | `{ event_id, occurred_at, invoice_summary_id, tenant_id, subscription_id, external_invoice_ref, invoice_number, amount_due, amount_paid, currency, status, due_date, issued_at }` | Billing & Subscription Service | Notification Orchestrator; Analytics & Reporting Service |
| Subscription, invoicing, payments | `payment.event.recorded.v1` | Payment gateway lifecycle event is normalized and stored. | `{ event_id, occurred_at, payment_event_id, tenant_id, subscription_id, invoice_summary_id, external_payment_ref, event_type, amount, currency, event_time, status }` | Billing & Subscription Service | Analytics & Reporting Service; Workflow Automation Service; Audit & Compliance Service |
| Campaign segmentation lifecycle | `campaign.created.v1` | Campaign is drafted against a segment audience. | `{ event_id, occurred_at, campaign_id, tenant_id, segment_id, owner_user_id, status, starts_at, ends_at, created_at }` | Campaign Service | Workflow Automation Service; Analytics & Reporting Service |
| Campaign segmentation lifecycle | `campaign.activated.v1` | Campaign transitions from draft to active outreach. | `{ event_id, occurred_at, campaign_id, tenant_id, segment_id, status, activated_at }` | Campaign Service | Workflow Automation Service; Communication Service; Analytics & Reporting Service |
| Campaign segmentation lifecycle | `campaign.paused.v1` | Active campaign is paused by a manager. | `{ event_id, occurred_at, campaign_id, tenant_id, paused_by_user_id, paused_at }` | Campaign Service | Workflow Automation Service; Analytics & Reporting Service |
| Campaign segmentation lifecycle | `campaign.cancelled.v1` | Campaign is cancelled before or during outreach. | `{ event_id, occurred_at, campaign_id, tenant_id, cancelled_by_user_id, cancelled_at }` | Campaign Service | Workflow Automation Service; Analytics & Reporting Service |
| Campaign segmentation lifecycle | `campaign.completed.v1` | Campaign reaches completed terminal state. | `{ event_id, occurred_at, campaign_id, tenant_id, segment_id, status, completed_at }` | Campaign Service | Workflow Automation Service; Analytics & Reporting Service |
| Campaign send tracking | `campaign.send.queued.v1` | Individual contact send is enqueued for dispatch. | `{ event_id, occurred_at, send_id, campaign_id, tenant_id, contact_id, channel, idempotency_key }` | Campaign Service | Communication Service |
| Campaign send tracking | `campaign.send.delivered.v1` | Delivery receipt received from provider. | `{ event_id, occurred_at, send_id, campaign_id, tenant_id, contact_id, channel, delivered_at }` | Campaign Service | Analytics & Reporting Service |
| Campaign send tracking | `campaign.send.read.v1` | Read receipt received (WhatsApp blue ticks). | `{ event_id, occurred_at, send_id, campaign_id, tenant_id, contact_id, read_at }` | Campaign Service | Analytics & Reporting Service |
| Campaign send tracking | `campaign.send.replied.v1` | Contact replied to a campaign message — follow-up task spawned. | `{ event_id, occurred_at, send_id, campaign_id, tenant_id, contact_id, replied_at }` | Campaign Service | Follow-up Service; Analytics & Reporting Service |
| Campaign send tracking | `campaign.send.failed.v1` | Send failed after retries. | `{ event_id, occurred_at, send_id, campaign_id, tenant_id, contact_id, channel, failure_reason, failed_at }` | Campaign Service | Notification Orchestrator; Analytics & Reporting Service |
| Campaign conversion attribution | `campaign.conversion.attributed.v1` | A lead or opportunity is attributed to a campaign within the attribution window. | `{ event_id, occurred_at, conversion_id, campaign_id, tenant_id, contact_id, conversion_type, entity_id, attributed_at }` | Campaign Service | Analytics & Reporting Service |
| Contact opt-out | `contact.opted_out.v1` | Contact opts out of WhatsApp marketing via STOP / بند کریں keyword during a campaign. | `{ event_id, occurred_at, contact_id, tenant_id, campaign_id, channel, opted_out_at }` | Campaign Service | Communication Service; Analytics & Reporting Service |
| Case management & SLA | `case.created.v1` | Support case is created from portal, email, or API. | `{ event_id, occurred_at, case_id, tenant_id, account_id, contact_id, owner_user_id, subject, priority, status, sla_due_at, created_at }` | Case Management Service | Notification Orchestrator; Activity Timeline Service; Search Index Service |
| Case management & SLA | `case.sla.first_response_breached.v1` | First-response SLA deadline missed for open case. | `{ event_id, occurred_at, case_id, tenant_id, owner_user_id, priority, status, sla_first_response_due_at, breach_type: "first_response" }` | Case Management Service | Notification Orchestrator; Workflow Automation Service; Analytics & Reporting Service |
| Case management & SLA | `case.sla.resolution_breached.v1` | Resolution SLA deadline missed (emitted at 25%, 50%, 100% breach thresholds). | `{ event_id, occurred_at, case_id, tenant_id, owner_user_id, priority, status, sla_resolution_due_at, breach_pct, breach_type: "resolution" }` | Case Management Service | Notification Orchestrator; Workflow Automation Service; Analytics & Reporting Service |
| Case management & SLA | `case.sla.breached.v1` | Generic SLA breach event (alias for downstream consumers that do not distinguish breach type). Emitted alongside the type-specific event. | `{ event_id, occurred_at, case_id, tenant_id, owner_user_id, priority, status, sla_due_at }` | Case Management Service | Notification Orchestrator; Workflow Automation Service; Analytics & Reporting Service |
| Case management & SLA | `case.resolved.v1` | Case transitions into resolved/closed state. | `{ event_id, occurred_at, case_id, tenant_id, owner_user_id, status, resolved_at }` | Case Management Service | Notification Orchestrator; Analytics & Reporting Service; Activity Timeline Service |
| Communication engagement | `communication.message.sent.v1` | Outbound message is accepted by provider. | `{ event_id, occurred_at, message_id, tenant_id, message_thread_id, direction, provider_message_id, sender, recipient, status, sent_at }` | Communication Service | Activity Timeline Service; Analytics & Reporting Service |
| Communication engagement | `communication.message.engagement.updated.v1` | Delivery/open/click/reply webhook updates message state. | `{ event_id, occurred_at, message_id, tenant_id, message_thread_id, status, delivered_at, opened_at, clicked_at }` | Communication Service | Activity Timeline Service; Analytics & Reporting Service; Workflow Automation Service |
| Notification dispatch lifecycle | `notification.dispatched.v1` | Notification is successfully sent on selected channel. | `{ event_id, occurred_at, notification_id, tenant_id, template_id, recipient_user_id, channel_type, target_address, status, provider_ref, requested_at, sent_at }` | Notification Orchestrator | Audit & Compliance Service; Analytics & Reporting Service |
| Notification dispatch lifecycle | `notification.failed.v1` | Notification dispatch fails after provider/API attempt. | `{ event_id, occurred_at, notification_id, tenant_id, template_id, recipient_user_id, channel_type, target_address, status, provider_ref, requested_at, failed_at, error_code }` | Notification Orchestrator | Workflow Automation Service; Analytics & Reporting Service; Audit & Compliance Service |
| Knowledge publishing | `knowledge.article.published.v1` | Knowledge article status becomes published. | `{ event_id, occurred_at, knowledge_article_id, tenant_id, title, slug, status, version, published_at, updated_at }` | Knowledge Base Service | Search Index Service; Case Management Service; Analytics & Reporting Service |
| Workflow runtime orchestration | `workflow.execution.completed.v1` | Workflow execution finishes successfully. | `{ event_id, occurred_at, workflow_execution_id, tenant_id, workflow_definition_id, trigger_entity_type, trigger_entity_id, status, started_at, completed_at }` | Workflow Automation Service | Analytics & Reporting Service; Audit & Compliance Service |
| Workflow runtime orchestration | `workflow.execution.failed.v1` | Workflow execution ends in error. | `{ event_id, occurred_at, workflow_execution_id, tenant_id, workflow_definition_id, trigger_entity_type, trigger_entity_id, status, started_at, completed_at, error_message }` | Workflow Automation Service | Notification Orchestrator; Audit & Compliance Service |
| Search indexing | `search.document.upserted.v1` | Search projection is written/refreshed for entity. | `{ event_id, occurred_at, search_document_id, tenant_id, entity_type, entity_id, title, tags_json, indexed_at, last_source_update_at }` | Search Index Service | Analytics & Reporting Service; Audit & Compliance Service |
| Feature rollout | `feature_flag.updated.v1` | Feature flag definition or default state changes. | `{ event_id, occurred_at, feature_flag_id, tenant_id, flag_key, description, default_state, updated_at }` | Feature Flag Service | API Gateway; Workflow Automation Service; Audit & Compliance Service |
| Governance & audit | `audit.log.recorded.v1` | Audit entry is persisted for sensitive action. | `{ event_id, occurred_at, audit_log_id, tenant_id, actor_user_id, action, resource_type, resource_id, result, ip_address, user_agent, metadata_json }` | Audit & Compliance Service | Analytics & Reporting Service; Data Warehouse |
| Platform reliability handling | `eventbus.dead_lettered.v1` | Event exceeds retry policy and is moved to dead-letter queue. | `{ event_id, occurred_at, tenant_id, source_event_name, source_event_id, source_service, failure_reason, retry_count, dead_letter_topic }` | Event Bus | Workflow Automation Service; Audit & Compliance Service; Platform Operations |
| Scheduler job lifecycle | `job.enqueued.v1` | New background job is accepted into durable queue. | `{ event_id, occurred_at, job_id, tenant_id, job_type, idempotency_key, available_at, attempt, max_attempts, priority }` | Job Scheduler | Workflow Automation Service; Analytics & Reporting Service; Audit & Compliance Service |
| Scheduler job lifecycle | `job.started.v1` | Worker starts executing leased job. | `{ event_id, occurred_at, job_id, tenant_id, job_type, lease_owner, lease_expires_at, attempt, started_at }` | Job Scheduler | Analytics & Reporting Service; Audit & Compliance Service |
| Scheduler job lifecycle | `job.succeeded.v1` | Job finishes successfully and is acknowledged. | `{ event_id, occurred_at, job_id, tenant_id, job_type, attempt, started_at, completed_at, duration_ms }` | Job Scheduler | Workflow Automation Service; Analytics & Reporting Service; Audit & Compliance Service |
| Scheduler job lifecycle | `job.retry.scheduled.v1` | Failed attempt is rescheduled according to retry policy. | `{ event_id, occurred_at, job_id, tenant_id, job_type, attempt, next_run_at, backoff_seconds, failure_reason }` | Job Scheduler | Workflow Automation Service; Analytics & Reporting Service; Audit & Compliance Service |
| Scheduler job lifecycle | `job.failed.v1` | Job reaches terminal failed state prior to dead-letter handling. | `{ event_id, occurred_at, job_id, tenant_id, job_type, attempt, max_attempts, failure_reason, failed_at }` | Job Scheduler | Platform Operations; Analytics & Reporting Service; Audit & Compliance Service |
| Scheduler job lifecycle | `job.dead_lettered.v1` | Job exhausts retries and is moved to dead-letter storage. | `{ event_id, occurred_at, job_id, tenant_id, job_type, attempt, max_attempts, failure_reason, dead_letter_queue }` | Job Scheduler | Platform Operations; Workflow Automation Service; Audit & Compliance Service |
| Scheduler schedule lifecycle | `schedule.created.v1` | New recurring schedule is created. | `{ event_id, occurred_at, schedule_id, tenant_id, name, job_type, cron, timezone, concurrency_policy, misfire_policy, enabled }` | Job Scheduler | Analytics & Reporting Service; Audit & Compliance Service |
| Scheduler schedule lifecycle | `schedule.updated.v1` | Existing schedule is modified or enabled/disabled. | `{ event_id, occurred_at, schedule_id, tenant_id, name, cron, timezone, concurrency_policy, misfire_policy, enabled, updated_fields[] }` | Job Scheduler | Analytics & Reporting Service; Audit & Compliance Service |
| Scheduler schedule lifecycle | `schedule.deleted.v1` | Schedule is soft-deleted and no further automatic runs are materialized. | `{ event_id, occurred_at, schedule_id, tenant_id, name, deleted_at, deleted_by_user_id }` | Job Scheduler | Analytics & Reporting Service; Audit & Compliance Service |

| Partner channel management | `partner.created.v1` | Partner profile is created for a tenant. | `{ event_id, occurred_at, partner_id, tenant_id, partner_code, name, partner_type, status, tier, owner_user_id, created_at }` | Partner Management Service | Activity Timeline Service; Analytics & Reporting Service; Audit & Compliance Service |
| Partner channel management | `partner.tier_changed.v1` | Partner tier upgraded or downgraded (admin action). | `{ event_id, occurred_at, partner_id, tenant_id, previous_tier, new_tier, changed_by_user_id, changed_at }` | Partner Management Service | Analytics & Reporting Service; Audit & Compliance Service |
| Partner channel management | `partner.status_changed.v1` | Partner status transitions (active / inactive / suspended). | `{ event_id, occurred_at, partner_id, tenant_id, previous_status, new_status, changed_by_user_id, changed_at }` | Partner Management Service | Analytics & Reporting Service; Audit & Compliance Service |
| Partner channel management | `partner.relationship.activated.v1` | Partner relationship is linked to an account or opportunity with attribution scope. | `{ event_id, occurred_at, partner_relationship_id, tenant_id, partner_id, account_id, opportunity_id, relationship_type, source_channel, effective_from, status }` | Partner Management Service | Activity Timeline Service; Analytics & Reporting Service |
| Partner channel management | `partner.deal.registered.v1` | Partner registers a deal for attribution consideration. | `{ event_id, occurred_at, partner_relationship_id, tenant_id, partner_id, opportunity_id, registration_type, registered_at }` | Partner Management Service | Approval Service; Analytics & Reporting Service; Audit & Compliance Service |
| Partner channel management | `partner.deal.approved.v1` | Deal registration approved — protection window active. | `{ event_id, occurred_at, registration_id, tenant_id, partner_id, reviewed_by_user_id, approved_at }` | Partner Management Service | Analytics & Reporting Service; Audit & Compliance Service |
| Partner channel management | `partner.deal.rejected.v1` | Deal registration rejected with reason. | `{ event_id, occurred_at, registration_id, tenant_id, partner_id, rejection_reason, reviewed_by_user_id, rejected_at }` | Partner Management Service | Notification Orchestrator; Analytics & Reporting Service |
| Partner channel management | `partner.attribution.locked.v1` | Attribution weight is finalized and locked for a closed-won opportunity. | `{ event_id, occurred_at, partner_attribution_id, tenant_id, partner_id, opportunity_id, attribution_model, attribution_weight, attributed_amount, currency, locked_at }` | Partner Management Service | Billing & Subscription Service; Analytics & Reporting Service; Audit & Compliance Service |
| Partner channel management | `partner.commission.calculated.v1` | Commission amount is calculated from locked attribution and commission plan. | `{ event_id, occurred_at, partner_commission_id, tenant_id, partner_id, partner_attribution_id, opportunity_id, commission_plan_code, commission_rate, commission_amount, currency, eligible_at }` | Partner Management Service | Notification Orchestrator; Analytics & Reporting Service |
| Partner channel management | `partner.commission.approved.v1` | Commission payout is approved for disbursement. | `{ event_id, occurred_at, partner_commission_id, tenant_id, partner_id, commission_amount, currency, approved_at, approved_by_user_id }` | Partner Management Service | Billing & Subscription Service; Audit & Compliance Service; Analytics & Reporting Service |
| Partner channel management | `partner.commission.paid.v1` | Commission payment recorded and marked as paid (immutable after this event). | `{ event_id, occurred_at, partner_commission_id, tenant_id, partner_id, commission_amount, currency, payment_reference, paid_at }` | Partner Management Service | Audit & Compliance Service; Analytics & Reporting Service |
| AI scoring & copilot | `ai.lead_scored.v1` | Lead score computed or recomputed by scoring model. | `{ event_id, occurred_at, score_id, tenant_id, lead_id, model_id, score, score_band, confidence_score, computed_at }` | AI & Predictive Models Service | Analytics & Reporting Service |
| AI scoring & copilot | `ai.churn_predicted.v1` | Churn probability computed for an account. | `{ event_id, occurred_at, prediction_id, tenant_id, account_id, model_id, churn_probability, risk_band, confidence_score, computed_at }` | AI & Predictive Models Service | Analytics & Reporting Service; Notification Orchestrator |
| AI scoring & copilot | `ai.clv_estimated.v1` | CLV estimate computed for an account. | `{ event_id, occurred_at, estimate_id, tenant_id, account_id, model_id, estimated_clv, confidence_score, computed_at }` | AI & Predictive Models Service | Analytics & Reporting Service |
| AI scoring & copilot | `ai.suggestion_generated.v1` | Copilot suggestion created for a user. | `{ event_id, occurred_at, suggestion_id, tenant_id, target_user_id, suggestion_type, priority, entity_type, entity_id, evidence_anchor, expires_at }` | AI & Predictive Models Service | Notification Orchestrator |
| AI scoring & copilot | `ai.suggestion_dismissed.v1` | User dismissed a copilot suggestion. | `{ event_id, occurred_at, suggestion_id, tenant_id, target_user_id, dismissed_at }` | AI & Predictive Models Service | Analytics & Reporting Service |
| AI scoring & copilot | `ai.suggestion_actioned.v1` | User clicked Take Action on a copilot suggestion. | `{ event_id, occurred_at, suggestion_id, tenant_id, target_user_id, actioned_at }` | AI & Predictive Models Service | Analytics & Reporting Service |
| AI scoring & copilot | `ai.query_answered.v1` | Conversational copilot query processed and response returned. | `{ event_id, occurred_at, tenant_id, user_id, intent_class, query_length, response_card_count, answered_at }` | AI & Predictive Models Service | Analytics & Reporting Service |

## Global Idempotency Processing Rules

- Producer retries MUST reuse the same `event_id` for the same logical event.
- Consumer handlers MUST persist inbox dedupe records before acking delivery.
- Duplicate delivery of the same `(tenant_id, event_name, event_id)` MUST be treated as no-op.
- Side effects (notifications, workflow execution triggers, provider calls) MUST use deterministic idempotency keys derived from source `event_id`.
- Replay jobs and dead-letter reprocessing MUST retain original `event_id` and remain side-effect safe.

## Workflow-to-Event Coverage Check

| Workflow | Required Event Coverage |
|---|---|
| Tenant provisioning & entitlement | `tenant.provisioned.v1`, `tenant.entitlement.updated.v1` |
| Identity & access lifecycle | `identity.user.provisioned.v1`, `identity.user.role.assigned.v1` |
| Lead intake, assignment, conversion | `lead.created.v1`, `lead.assignment.updated.v1`, `lead.converted.v1` |
| Contact & account management | `contact.created.v1`, `contact.merged.v1`, `account.created.v1`, `account.hierarchy.updated.v1` |
| Opportunity pipeline & close outcomes | `opportunity.created.v1`, `opportunity.stage.changed.v1`, `opportunity.closed.v1` |
| Quote, approval, acceptance | `quote.created.v1`, `quote.submitted_for_approval.v1`, `approval.requested.v1`, `approval.decided.v1`, `quote.accepted.v1`, `order.created.v1` |
| Subscription, invoicing, payments | `subscription.created.v1`, `subscription.status.changed.v1`, `invoice.summary.updated.v1`, `payment.event.recorded.v1` |
| Campaign segmentation lifecycle | `campaign.created.v1`, `campaign.activated.v1`, `campaign.paused.v1`, `campaign.cancelled.v1`, `campaign.completed.v1` |
| Campaign send tracking | `campaign.send.queued.v1`, `campaign.send.delivered.v1`, `campaign.send.read.v1`, `campaign.send.replied.v1`, `campaign.send.failed.v1` |
| Campaign conversion attribution | `campaign.conversion.attributed.v1` |
| Contact opt-out | `contact.opted_out.v1` |
| Case management & SLA | `case.created.v1`, `case.sla.first_response_breached.v1`, `case.sla.resolution_breached.v1`, `case.sla.breached.v1`, `case.resolved.v1` |
| Communication engagement | `communication.message.sent.v1`, `communication.message.engagement.updated.v1` |
| Notification dispatch lifecycle | `notification.dispatched.v1`, `notification.failed.v1` |
| Knowledge publishing | `knowledge.article.published.v1` |
| Workflow runtime orchestration | `workflow.execution.completed.v1`, `workflow.execution.failed.v1` |
| Search indexing | `search.document.upserted.v1` |
| Feature rollout | `feature_flag.updated.v1` |
| Governance & audit | `audit.log.recorded.v1` |
| Platform reliability handling | `eventbus.dead_lettered.v1` |
| Scheduler job lifecycle | `job.enqueued.v1`, `job.started.v1`, `job.succeeded.v1`, `job.retry.scheduled.v1`, `job.failed.v1`, `job.dead_lettered.v1` |
| Scheduler schedule lifecycle | `schedule.created.v1`, `schedule.updated.v1`, `schedule.deleted.v1` |
| Partner channel management | `partner.created.v1`, `partner.tier_changed.v1`, `partner.status_changed.v1`, `partner.relationship.activated.v1`, `partner.deal.registered.v1`, `partner.deal.approved.v1`, `partner.deal.rejected.v1`, `partner.attribution.locked.v1`, `partner.commission.calculated.v1`, `partner.commission.approved.v1`, `partner.commission.paid.v1` |
| AI scoring & copilot | `ai.lead_scored.v1`, `ai.churn_predicted.v1`, `ai.clv_estimated.v1`, `ai.suggestion_generated.v1`, `ai.suggestion_dismissed.v1`, `ai.suggestion_actioned.v1`, `ai.query_answered.v1` |

---

## Event Bus Infrastructure

*Added from src/event_bus overlay — 2026-04-02*

The event bus provides typed publish/subscribe infrastructure. The contracts below define the canonical interface all event producers and consumers must implement.

### Event (envelope)

| Field | Notes |
|---|---|
| `event_name` | Canonical event name from this catalog (e.g., `opportunity.created.v1`) |
| `event_id` | Producer-stable UUID preserved across retries and replay |
| `occurred_at` | ISO-8601 UTC timestamp |
| `tenant_id` | Tenant scope |
| `payload` | Event-specific payload dict matching the catalog schema |

### EventHandler Protocol

```
EventHandler: (event: Event) -> None
```

All consumers implement this callable protocol. Called once per delivered event.

### EventPublisher Protocol

```
EventPublisher.publish(event: Event) -> None
```

Services produce events via this interface. Direct event dispatch is forbidden outside this interface.

### EventSubscriber Protocol

```
EventSubscriber.subscribe(event_name: str, handler: EventHandler) -> None
```

Registers a handler for a named event. A handler may be registered for multiple event names.

**Deduplication rule:** Every consumer MUST deduplicate by `(tenant_id, event_name, event_id)` before applying side effects. The event bus guarantees at-least-once delivery — idempotency is the consumer's responsibility.
