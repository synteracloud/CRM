# CRM Workflow Catalog

This catalog defines the canonical business workflows and their explicit execution sequences.

## Alignment Rules

- Workflow sequencing is strictly ordered and references canonical events in `docs/event-catalog.md`.
- No workflow omits intermediate state transitions represented by required events.
- Service participation reflects ownership and consumers from `docs/service-map.md` and `docs/event-catalog.md`.

---

## 1) Tenant provisioning & entitlement

- **Name:** Tenant provisioning & entitlement
- **Trigger events:**
  - `tenant.provisioned.v1`
  - `tenant.entitlement.updated.v1`
- **Services involved:**
  - Organization & Tenant Service
  - Feature Flag Service
  - Identity & Access Service
  - Workflow Automation Service
  - Analytics & Reporting Service
  - Audit & Compliance Service
  - Search Index Service
- **Ordered steps:**
  1. Organization & Tenant Service creates and activates tenant, then emits `tenant.provisioned.v1`.
  2. Feature Flag Service initializes tenant-level flag context from provisioning payload.
  3. Identity & Access Service initializes tenant identity boundary for users/roles.
  4. Audit & Compliance Service records provisioning action.
  5. Search Index Service indexes tenant projection for lookup/discovery.
  6. Organization & Tenant Service applies or updates plan/feature entitlements and emits `tenant.entitlement.updated.v1`.
  7. Feature Flag Service updates effective feature exposure from entitlements.
  8. Workflow Automation Service evaluates entitlement-driven automations.
  9. Analytics & Reporting Service updates tenant/plan metrics.
- **Outcome:** Tenant is active, discoverable, policy-scoped, and running with correct entitlement-driven feature access.

## 2) Identity & access lifecycle

- **Name:** Identity & access lifecycle
- **Trigger events:**
  - `identity.user.provisioned.v1`
  - `identity.user.role.assigned.v1`
- **Services involved:**
  - Identity & Access Service
  - Notification Orchestrator
  - Feature Flag Service
  - Analytics & Reporting Service
  - Audit & Compliance Service
- **Ordered steps:**
  1. Identity & Access Service creates a tenant-scoped user and emits `identity.user.provisioned.v1`.
  2. Notification Orchestrator sends onboarding/access notifications.
  3. Audit & Compliance Service records user provisioning.
  4. Analytics & Reporting Service updates user lifecycle metrics.
  5. Identity & Access Service assigns role(s) and emits `identity.user.role.assigned.v1`.
  6. Feature Flag Service recalculates role-targeted feature exposure.
  7. Audit & Compliance Service records authorization change.
- **Outcome:** User is provisioned with explicit role-based access and onboarding/audit artifacts complete.

## 3) Lead intake, assignment, conversion

- **Name:** Lead intake, assignment, conversion
- **Trigger events:**
  - `lead.created.v1`
  - `lead.assignment.updated.v1`
  - `lead.converted.v1`
- **Services involved:**
  - Lead Management Service
  - Territory & Assignment Service
  - Data Quality Service
  - Activity Timeline Service
  - Notification Orchestrator
  - Contact Service
  - Account Service
  - Opportunity Service
  - Workflow Automation Service
  - Analytics & Reporting Service
  - Search Index Service
- **Ordered steps:**
  1. Lead Management Service captures new lead and emits `lead.created.v1`.
  2. Territory & Assignment Service computes ownership and persists assignment.
  3. Territory & Assignment Service emits `lead.assignment.updated.v1`.
  4. Lead Management Service updates lead owner state from assignment event.
  5. Notification Orchestrator notifies assigned owner.
  6. Data Quality Service evaluates/normalizes lead quality signals.
  7. Activity Timeline Service appends lead creation/assignment events.
  8. Search Index Service upserts lead search document.
  9. On conversion action, Lead Management Service creates linked account/contact/(optional) opportunity and emits `lead.converted.v1`.
  10. Contact Service, Account Service, and Opportunity Service materialize converted entities.
  11. Workflow Automation Service runs conversion automations.
  12. Analytics & Reporting Service updates funnel conversion metrics.
- **Outcome:** Captured lead is owned, traceable, and converted into downstream revenue/customer entities when qualified.

## 4) Contact & account management

- **Name:** Contact & account management
- **Trigger events:**
  - `contact.created.v1`
  - `contact.merged.v1`
  - `account.created.v1`
  - `account.hierarchy.updated.v1`
- **Services involved:**
  - Contact Service
  - Account Service
  - Activity Timeline Service
  - Search Index Service
  - Data Quality Service
  - Territory & Assignment Service
  - Analytics & Reporting Service
  - Audit & Compliance Service
- **Ordered steps:**
  1. Contact Service creates contact and emits `contact.created.v1`.
  2. Activity Timeline Service records contact creation.
  3. Search Index Service indexes contact projection.
  4. Data Quality Service evaluates duplicate/canonicalization signals.
  5. When duplicate resolution is executed, Contact Service merges records and emits `contact.merged.v1`.
  6. Search Index Service reindexes survivor/removes merged records.
  7. Analytics & Reporting Service updates contact quality and merge metrics.
  8. Audit & Compliance Service logs merge action.
  9. Account Service creates account and emits `account.created.v1`.
  10. Activity Timeline Service records account creation.
  11. Search Index Service indexes account projection.
  12. Territory & Assignment Service evaluates ownership/territory updates for account.
  13. Account Service updates parent-child linkage and emits `account.hierarchy.updated.v1`.
  14. Analytics & Reporting Service refreshes hierarchy rollups.
  15. Search Index Service updates hierarchy-aware search facets.
- **Outcome:** Contact/account master data is canonical, searchable, and hierarchy-aware for downstream sales/support workflows.

## 5) Opportunity pipeline & close outcomes

- **Name:** Opportunity pipeline & close outcomes
- **Trigger events:**
  - `opportunity.created.v1`
  - `opportunity.stage.changed.v1`
  - `opportunity.closed.v1`
- **Services involved:**
  - Opportunity Service
  - Activity Timeline Service
  - Territory & Assignment Service
  - Workflow Automation Service
  - Notification Orchestrator
  - Analytics & Reporting Service
- **Ordered steps:**
  1. Opportunity Service creates opportunity and emits `opportunity.created.v1`.
  2. Activity Timeline Service writes creation event.
  3. Territory & Assignment Service evaluates ownership/routing updates.
  4. Analytics & Reporting Service initializes pipeline/forecast metrics.
  5. Opportunity Service updates stage or forecast and emits `opportunity.stage.changed.v1`.
  6. Workflow Automation Service runs stage-based actions/tasks.
  7. Notification Orchestrator dispatches stage-change alerts where configured.
  8. Analytics & Reporting Service recalculates stage velocity and forecast.
  9. When opportunity reaches terminal state, Opportunity Service emits `opportunity.closed.v1`.
  10. Activity Timeline Service records close event.
  11. Workflow Automation Service executes won/lost close playbooks.
  12. Analytics & Reporting Service finalizes win-rate, cycle-time, and revenue outcomes.
- **Outcome:** Opportunity progresses through controlled stages to explicit won/lost closure with full forecast and performance tracking.

## 6) Quote, approval, acceptance

- **Name:** Quote, approval, acceptance
- **Trigger events:**
  - `quote.created.v1`
  - `quote.submitted_for_approval.v1`
  - `approval.requested.v1`
  - `approval.decided.v1`
  - `quote.accepted.v1`
- **Services involved:**
  - Quote Service
  - Approval Service
  - Notification Orchestrator
  - Activity Timeline Service
  - Workflow Automation Service
  - Analytics & Reporting Service
  - Audit & Compliance Service
  - Billing & Subscription Service
  - Opportunity Service
- **Ordered steps:**
  1. Quote Service creates quote and emits `quote.created.v1`.
  2. Activity Timeline Service records quote creation.
  3. Approval Service evaluates approval policy requirements.
  4. If approval is required, Quote Service transitions state and emits `quote.submitted_for_approval.v1`.
  5. Approval Service creates approval request and emits `approval.requested.v1`.
  6. Notification Orchestrator notifies assigned approver(s).
  7. Audit & Compliance Service logs approval request initiation.
  8. Approver decision is captured by Approval Service, which emits `approval.decided.v1`.
  9. Quote Service applies approval outcome (approved/rejected).
  10. Notification Orchestrator sends requester decision notification.
  11. Audit & Compliance Service records final decision.
  12. On customer acceptance, Quote Service emits `quote.accepted.v1`.
  13. Billing & Subscription Service and Opportunity Service consume acceptance for downstream fulfillment/closure.
  14. Analytics & Reporting Service updates quote-to-close metrics.
- **Outcome:** Commercial quote progresses through policy-controlled approvals and customer acceptance to downstream monetization.

## 7) Subscription, invoicing, payments

- **Name:** Subscription, invoicing, payments
- **Trigger events:**
  - `subscription.created.v1`
  - `subscription.status.changed.v1`
  - `invoice.summary.updated.v1`
  - `payment.event.recorded.v1`
- **Services involved:**
  - Billing & Subscription Service
  - Organization & Tenant Service
  - Notification Orchestrator
  - Workflow Automation Service
  - Analytics & Reporting Service
  - Search Index Service
  - Audit & Compliance Service
- **Ordered steps:**
  1. Billing & Subscription Service provisions subscription from accepted commercial action and emits `subscription.created.v1`.
  2. Organization & Tenant Service updates tenant subscription context.
  3. Search Index Service indexes subscription projection.
  4. Analytics & Reporting Service initializes recurring revenue metrics.
  5. On lifecycle transitions (active/past_due/canceled/etc.), Billing & Subscription Service emits `subscription.status.changed.v1`.
  6. Notification Orchestrator sends lifecycle/status notifications.
  7. Workflow Automation Service executes lifecycle automations.
  8. Analytics & Reporting Service updates retention/churn metrics.
  9. Billing & Subscription Service creates/updates invoice mirror and emits `invoice.summary.updated.v1`.
  10. Notification Orchestrator dispatches invoice communications.
  11. Billing & Subscription Service normalizes payment gateway updates and emits `payment.event.recorded.v1`.
  12. Workflow Automation Service triggers follow-up actions for payment states.
  13. Audit & Compliance Service records payment lifecycle artifacts.
  14. Analytics & Reporting Service refreshes cash collection and delinquency metrics.
- **Outcome:** Subscription lifecycle, invoice state, and payment events are synchronized and operationally actionable.

## 8) Case management & SLA

- **Name:** Case management & SLA
- **Trigger events:**
  - `case.created.v1`
  - `case.sla.breached.v1`
  - `case.resolved.v1`
- **Services involved:**
  - Case Management Service
  - Notification Orchestrator
  - Activity Timeline Service
  - Search Index Service
  - Workflow Automation Service
  - Analytics & Reporting Service
- **Ordered steps:**
  1. Case Management Service creates support case and emits `case.created.v1`.
  2. Notification Orchestrator sends intake/assignment acknowledgements.
  3. Activity Timeline Service appends case creation event.
  4. Search Index Service indexes case for support lookup.
  5. Case Management Service monitors SLA timers.
  6. If due time is exceeded while open, Case Management Service emits `case.sla.breached.v1`.
  7. Notification Orchestrator dispatches breach escalation notifications.
  8. Workflow Automation Service runs escalation/remediation playbooks.
  9. Analytics & Reporting Service updates SLA compliance metrics.
  10. Upon successful resolution, Case Management Service emits `case.resolved.v1`.
  11. Notification Orchestrator sends resolution communications.
  12. Activity Timeline Service records closure/resolution event.
  13. Analytics & Reporting Service updates resolution-time and backlog outcomes.
- **Outcome:** Support cases are tracked from intake to closure with deterministic SLA monitoring and escalation.

## 9) Communication engagement

- **Name:** Communication engagement
- **Trigger events:**
  - `communication.message.sent.v1`
  - `communication.message.engagement.updated.v1`
- **Services involved:**
  - Communication Service
  - Activity Timeline Service
  - Analytics & Reporting Service
  - Workflow Automation Service
- **Ordered steps:**
  1. Communication Service accepts outbound message from CRM flow and emits `communication.message.sent.v1`.
  2. Activity Timeline Service records send action in customer timeline.
  3. Analytics & Reporting Service updates outbound communication volume metrics.
  4. Communication provider webhooks are normalized by Communication Service.
  5. Communication Service emits `communication.message.engagement.updated.v1` for delivery/open/click/reply state changes.
  6. Activity Timeline Service appends engagement updates.
  7. Analytics & Reporting Service updates engagement conversion metrics.
  8. Workflow Automation Service evaluates engagement-triggered automations.
- **Outcome:** Outbound communication and recipient engagement state are fully observable and automation-ready.

## 10) Notification dispatch lifecycle

- **Name:** Notification dispatch lifecycle
- **Trigger events:**
  - `notification.dispatched.v1`
  - `notification.failed.v1`
- **Services involved:**
  - Notification Orchestrator
  - Analytics & Reporting Service
  - Workflow Automation Service
  - Audit & Compliance Service
- **Ordered steps:**
  1. Notification Orchestrator renders and dispatches notification via configured channel/provider.
  2. On successful provider send, Notification Orchestrator emits `notification.dispatched.v1`.
  3. Audit & Compliance Service records successful dispatch artifact.
  4. Analytics & Reporting Service updates delivery throughput metrics.
  5. On failed provider/API attempt, Notification Orchestrator emits `notification.failed.v1`.
  6. Workflow Automation Service triggers retry/escalation workflows.
  7. Analytics & Reporting Service updates failure/error-rate metrics.
  8. Audit & Compliance Service records failure artifact.
- **Outcome:** Notification delivery outcomes are explicit, audited, and support retry/escalation controls.

## 11) Knowledge publishing

- **Name:** Knowledge publishing
- **Trigger events:**
  - `knowledge.article.published.v1`
- **Services involved:**
  - Knowledge Base Service
  - Search Index Service
  - Case Management Service
  - Analytics & Reporting Service
- **Ordered steps:**
  1. Knowledge Base Service transitions article to published state and emits `knowledge.article.published.v1`.
  2. Search Index Service indexes published article content and metadata.
  3. Case Management Service refreshes article availability for agent assist/case suggestions.
  4. Analytics & Reporting Service updates content publication and usage metrics.
- **Outcome:** Published knowledge is discoverable in support flows with measurable content impact.

## 12) Workflow runtime orchestration

- **Name:** Workflow runtime orchestration
- **Trigger events:**
  - `workflow.execution.completed.v1`
  - `workflow.execution.failed.v1`
- **Services involved:**
  - Workflow Automation Service
  - Analytics & Reporting Service
  - Notification Orchestrator
  - Audit & Compliance Service
- **Ordered steps:**
  1. Workflow Automation Service executes workflow definition against trigger context.
  2. If execution succeeds, Workflow Automation Service emits `workflow.execution.completed.v1`.
  3. Analytics & Reporting Service records successful execution metrics.
  4. Audit & Compliance Service records successful automation trace.
  5. If execution errors, Workflow Automation Service emits `workflow.execution.failed.v1`.
  6. Notification Orchestrator alerts configured operators/owners.
  7. Audit & Compliance Service records failure trace.
- **Outcome:** Automation executions produce deterministic completion/failure signals for observability and governance.

## 13) Search indexing

- **Name:** Search indexing
- **Trigger events:**
  - `search.document.upserted.v1`
- **Services involved:**
  - Search Index Service
  - Analytics & Reporting Service
  - Audit & Compliance Service
- **Ordered steps:**
  1. Search Index Service processes source entity change and writes/refreshes search projection.
  2. Search Index Service emits `search.document.upserted.v1`.
  3. Analytics & Reporting Service updates indexing freshness/volume metrics.
  4. Audit & Compliance Service records indexing mutation for traceability.
- **Outcome:** Entity search projections remain current and measurable with governance trace.

## 14) Feature rollout

- **Name:** Feature rollout
- **Trigger events:**
  - `feature_flag.updated.v1`
- **Services involved:**
  - Feature Flag Service
  - API Gateway
  - Workflow Automation Service
  - Audit & Compliance Service
- **Ordered steps:**
  1. Feature Flag Service updates flag definition/default state and emits `feature_flag.updated.v1`.
  2. API Gateway and runtime consumers pick up updated flag evaluations.
  3. Workflow Automation Service reevaluates flag-dependent automations.
  4. Audit & Compliance Service records rollout mutation.
- **Outcome:** Feature exposure changes propagate safely and are auditable across runtime consumers.

## 15) Governance & audit

- **Name:** Governance & audit
- **Trigger events:**
  - `audit.log.recorded.v1`
- **Services involved:**
  - Audit & Compliance Service
  - Analytics & Reporting Service
  - Data Warehouse
- **Ordered steps:**
  1. Audit & Compliance Service persists immutable audit log for sensitive action.
  2. Audit & Compliance Service emits `audit.log.recorded.v1`.
  3. Analytics & Reporting Service updates compliance and anomaly metrics.
  4. Data Warehouse ingests audit event into historical marts.
- **Outcome:** Sensitive actions are immutably recorded and available for compliance analytics and investigations.

## 16) Platform reliability handling

- **Name:** Platform reliability handling
- **Trigger events:**
  - `eventbus.dead_lettered.v1`
- **Services involved:**
  - Event Bus
  - Workflow Automation Service
  - Audit & Compliance Service
  - Platform Operations
- **Ordered steps:**
  1. Event Bus exhausts retry policy for undeliverable event and dead-letters payload.
  2. Event Bus emits `eventbus.dead_lettered.v1`.
  3. Workflow Automation Service triggers compensating/recovery workflows.
  4. Audit & Compliance Service records reliability incident artifact.
  5. Platform Operations triages dead-letter queue item and performs remediation/replay decision.
- **Outcome:** Failed event deliveries are surfaced, governed, and remediated through explicit reliability operations.

## 17) Scheduler job lifecycle

- **Name:** Scheduler job lifecycle
- **Trigger events:**
  - `job.enqueued.v1`
  - `job.started.v1`
  - `job.succeeded.v1`
  - `job.retry.scheduled.v1`
  - `job.failed.v1`
  - `job.dead_lettered.v1`
- **Services involved:**
  - Job Scheduler
  - Workflow Automation Service
  - Analytics & Reporting Service
  - Audit & Compliance Service
  - Platform Operations
- **Ordered steps:**
  1. Scheduler API accepts job submission and enforces idempotency/deduplication.
  2. Job Scheduler writes durable queue record and emits `job.enqueued.v1`.
  3. Worker acquires lease atomically and emits `job.started.v1`.
  4. If handler succeeds, Job Scheduler acknowledges completion and emits `job.succeeded.v1`.
  5. If handler fails with attempts remaining, Job Scheduler computes backoff and emits `job.retry.scheduled.v1`.
  6. If final attempt fails, Job Scheduler emits `job.failed.v1` and moves payload to dead-letter storage.
  7. Job Scheduler emits `job.dead_lettered.v1` for operator remediation workflow.
  8. Workflow Automation Service may trigger compensating actions from failure/dead-letter events.
  9. Analytics & Reporting Service updates queue latency, retries, and failure SLO dashboards.
  10. Audit & Compliance Service and Platform Operations retain incident trail and replay decisions.
- **Outcome:** Background jobs execute with retry safety, lease-based single-run guarantees, and explicit dead-letter governance.

## 18) Scheduler schedule lifecycle

- **Name:** Scheduler schedule lifecycle
- **Trigger events:**
  - `schedule.created.v1`
  - `schedule.updated.v1`
  - `schedule.deleted.v1`
- **Services involved:**
  - Job Scheduler
  - Analytics & Reporting Service
  - Audit & Compliance Service
  - Platform Operations
- **Ordered steps:**
  1. Operator/service creates recurring schedule through Scheduler API and Job Scheduler emits `schedule.created.v1`.
  2. Scheduler computes next due run and stores recurrence cursor.
  3. For each due slot, scheduler materializes at most one job using `(schedule_id, scheduled_for)` idempotency seed.
  4. Schedule updates emit `schedule.updated.v1` and recompute next due run atomically.
  5. Disabled schedules stop materialization but preserve audit/history.
  6. Soft-delete emits `schedule.deleted.v1` and blocks new recurring runs.
  7. Platform Operations can trigger run-now/replay without corrupting recurring cursor state.
- **Outcome:** Recurring automation is deterministic, deduplicated per slot, and operationally controllable.
