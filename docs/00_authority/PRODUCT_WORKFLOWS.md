Status: Draft
Authority Level: Critical
Last Reviewed: 2026-06-21
Owner: Shared

---

# PRODUCT WORKFLOWS — Pakistan CRM OS

## Workflow Engine Architecture

**Type:** Event-driven workflow engine
**Trigger mechanism:** Events emitted to internal event bus (src/event_bus/) on entity state changes
**Execution chain:** WorkflowDefinition → WorkflowExecution → WorkflowStepRecords
**Step types:** condition (boolean branch), action (data operation), notification (WhatsApp/email/system)
**Retry policy:** configurable max_retries (default 3), retry_backoff_seconds (default 60)
**System workflows:** 5 seeded, is_system=true, not editable by tenants
**Custom workflows:** Tenants can create additional workflows via POST /workflows (WORKFLOWS_MANAGE scope)

---

## Primary Business Workflows

### WF-A — Lead-to-Deal Workflow

**Description:** End-to-end journey from lead capture to closed opportunity.

**Trigger:** Inbound WhatsApp message or manual lead entry

**Steps:**
1. **Lead capture** — POST /leads creates Lead (source: whatsapp/web/import/manual); contact_id linked
2. **Automatic territory assignment** — WF-004 fires on lead.created.v1; evaluates TerritoryRules; sets owner_id; creates LeadAssignment record
3. **Follow-up scheduling** — POST /followups creates canonical FollowupTask (is_canonical=true); exactly one pending per lead
4. **Lead qualification** — Agent updates lead.stage (new→qualifying→nurturing→proposal); PATCH /leads/:id
5. **Follow-up enforcement** — If lead goes idle, WF-001 fires on lead.idle.v1; creates new follow-up task; sends WhatsApp alert to owner
6. **Opportunity creation** — POST /opportunities creates Opportunity linked to Account + Contact
7. **CPQ quote** — POST /quotes creates Quote with line items; discount > 10% triggers approval routing
8. **Quote approval** — PATCH /quotes/:id (approved/rejected); if approved: POST /quotes/:id/accept creates Order
9. **Opportunity close** — PATCH /opportunities/:id (stage→closed_won/closed_lost); emits opportunity.stage.changed.v1; WF-005 fires; forecast refreshed
10. **Invoice generation** — POST /invoices creates Invoice linked to Order/Account

**Entities involved:** Lead, LeadAssignment, LeadHistory, FollowupTask, Contact, Opportunity, OpportunityLineItem, Quote, Order, Invoice, Territory, TerritoryRule, AuditLog

**Roles involved:** agent (lead capture, follow-up), manager (assignment, quote approval), tenant_owner (all)

**API endpoints involved:**
- POST /leads, PATCH /leads/:id, GET /leads/:id
- POST /followups, POST /followups/:id/complete, POST /followups/:id/snooze
- POST /opportunities, PATCH /opportunities/:id, POST /opportunities/:id/line-items
- POST /quotes, PATCH /quotes/:id, POST /quotes/:id/accept
- POST /orders, POST /invoices

**Frontend pages involved:**
- leads.html (B-02), leads-detail.html (C-01), lead-new.html (I-01), followups.html (B-01)
- opportunities-detail.html (C-04), opportunity-new.html (I-03), sales-cockpit.html (D-01)
- quote-builder.html (I-05), quotes-detail.html (C-06)
- invoices.html (B-09), invoices-detail.html (C-08)

**Permissions required:** leads.read, leads.create, leads.update, leads.assign, followups.*, opportunities.*, quotes.create, quotes.accept, invoices.create

---

### WF-B — Deal-to-Invoice Workflow

**Description:** Converting a closed deal to a paid invoice via Pakistan payment rails.

**Trigger:** Opportunity closed_won OR manual invoice creation

**Steps:**
1. **Order creation** — POST /orders (from accepted Quote) or direct invoice creation
2. **Invoice issuance** — POST /invoice-summaries (scope: invoices.create) OR POST /collections/invoices (scope: collections.invoice, requires subscription_id FK); status=draft→sent; invoice_id linked to Account. Note: PRODUCT_WORKFLOWS.md previously referenced POST /invoices which does not exist as a standalone route — use POST /invoice-summaries for standalone invoice creation or POST /collections/invoices when creating via the collections workflow.
3. **Payment initiation** — POST /payments (method: jazzcash/easypaisa) — currently stub_mode=True
4. **Payment webhook** — POST /payment-webhooks/jazzcash or /easypaisa; updates Invoice.paid_amount
5. **Auto-reminder** — If Invoice.is_overdue=true, WF-002 fires on invoice.overdue.v1; sends WhatsApp reminder to Contact
6. **Collections escalation** — If unpaid, Collection record created; collections agent manages via collections.html
7. **Reconciliation** — POST /collections/:id/reconcile marks collection as resolved; updates Invoice status=paid

**Entities involved:** Opportunity, Quote, Order, Invoice, Payment, Collection, Contact, AuditLog

**Roles involved:** agent (invoice view), manager (invoice create), tenant_owner (payment config), auditor (read-only)

**API endpoints involved:**
- POST /orders, GET /orders/:id
- POST /invoice-summaries (invoices.create scope) or POST /collections/invoices (collections.invoice scope), GET /invoice-summaries, GET /invoice-summaries/:id
- POST /payments, POST /payment-webhooks/jazzcash, POST /payment-webhooks/easypaisa
- GET /collections/invoices, POST /collections/reconcile

**Frontend pages involved:**
- orders-detail.html (C-07), invoices.html (B-09), invoices-detail.html (C-08)
- collections.html (B-08), billing-settings.html (G-04 — blocked P-016)
- finance-analytics.html (H-04)

**Permissions required:** invoices.create, payments.create, collections.*, revenue.read

**Known constraint:** JazzCash and Easypaisa are in stub_mode=True (P-016); payments are simulated until credentials received

---

### WF-C — Case Lifecycle Workflow

**Description:** Support request from creation through SLA-tracked resolution.

**Trigger:** Customer WhatsApp message, web form submission, or agent creates case manually

**Steps:**
1. **Case creation** — POST /cases; SLA timers set based on sla_tier (tier_1: 1h response/8h resolution, etc.)
2. **Queue routing** — Case assigned to SupportQueue by routing_strategy (round_robin/least_loaded/manual)
3. **Agent assignment** — POST /cases/:id/assign (CASES_ADMIN); status: OPEN→ASSIGNED
4. **First response** — POST /cases/:id/comments (comment_type: customer_reply); auto-transitions ASSIGNED→IN_PROGRESS
5. **SLA monitoring** — SLA monitor checks sla_first_response_due_at and sla_resolution_due_at
6. **SLA breach handling** — If breached, WF-003 fires on case.sla.breached.v1: escalate case → notify supervisor → log to AuditLog
7. **Customer communication** — POST /cases/:id/comments (comment_type: customer_reply or internal_note)
8. **Knowledge linking** — POST /cases/:id/link-article (links KnowledgeArticle to Case for future deflection)
9. **Resolution** — POST /cases/:id/resolve; status→RESOLVED
10. **Closure** — POST /cases/:id/close (admin); status→CLOSED
11. **Reopen (if needed)** — POST /cases/:id/reopen (within 14 days only); 422 REOPEN_WINDOW_EXPIRED after 14 days

**Entities involved:** Case, CaseComment, CaseEscalation, SupportQueue, KnowledgeArticle, User, AuditLog

**Roles involved:** agent (create, comment, resolve), manager (assign, escalate, force-close), auditor (read-only)

**API endpoints involved:**
- POST /cases, GET /cases, GET /cases/:id, PATCH /cases/:id
- POST /cases/:id/assign, POST /cases/:id/comments, POST /cases/:id/resolve
- POST /cases/:id/close, POST /cases/:id/reopen, POST /cases/:id/escalate
- POST /cases/:id/link-article
- GET /support/queues, POST /support/queues

**Frontend pages involved:**
- cases.html (B-05), cases-detail.html (C-05), case-new.html (I-04)
- support-console.html (E-01), support-dashboard.html (A-07)
- knowledge-article.html (C-12), knowledge-dashboard.html (A-09)

**Permissions required:** cases.read, cases.create, cases.update, cases.admin, knowledge.read

---

### WF-D — WhatsApp Conversation Workflow

**Description:** Inbound WhatsApp message handling through intent classification to CRM action.

**Trigger:** Inbound WhatsApp message received via webhook (POST /whatsapp-webhooks/{provider})

**Steps:**
1. **Webhook ingestion** — POST /whatsapp-webhooks/meta or /gupshup or /360dialog or /twilio; idempotent processing
2. **Contact lookup** — Phone number matched against existing Contacts via E.164 lookup
3. **Conversation creation/continuation** — Conversation created or existing thread updated in messaging_db
4. **Intent detection** — NL query classified via regex into: payment_query/follow_up_response/lead_inquiry/support_request
5. **Auto-routing** — Conversation assigned to InboxQueue by routing_strategy; agent claimed via POST /inbox/conversations/:id/claim
6. **Agent capacity check** — Claim fails if agent open_conversation_count >= max_concurrent (10); route to another agent
7. **Agent response** — POST /inbox/conversations/:id/messages; WhatsApp outbound via MessagingAdapter
8. **Handoff (if needed)** — POST /inbox/conversations/:id/handoff; Handoff record created with from/to/reason
9. **Resolution** — Conversation resolved; state→resolved/closed

**Entities involved:** Conversation, Message, Handoff, AgentPresence, InboxQueue, Contact, AuditLog

**Roles involved:** agent (claim, respond), manager/supervisor (handoff any, view presence board), integration_service (webhook)

**API endpoints involved:**
- POST /whatsapp-webhooks/meta, POST /whatsapp-webhooks/gupshup, POST /whatsapp-webhooks/360dialog, POST /whatsapp-webhooks/twilio
- GET /inbox/conversations, GET /inbox/conversations/:id
- POST /inbox/conversations/:id/claim, POST /inbox/conversations/:id/messages
- POST /inbox/conversations/:id/handoff
- PATCH /inbox/presence, GET /inbox/presence
- GET /inbox/queues, POST /inbox/queues

**Frontend pages involved:**
- inbox.html (L-01), inbox-thread.html (L-02), engagement-dashboard.html (A-08 — Wired)
- routing-config.html (L-03)

**Permissions required:** inbox.read, inbox.write, inbox.admin (for queue management and presence board)

**Integration points:** MessagingAdapter (Meta/Gupshup/Dialog360/Twilio); provider selection at startup via adapter registry

---

### WF-E — Payment Collection Workflow

**Description:** Automated payment reminder and collection management for overdue invoices.

**Trigger:** invoice.overdue.v1 event emitted by billing service scheduler

**Steps:**
1. **Overdue detection** — Billing scheduler checks Invoice.due_date; emits invoice.overdue.v1 if is_overdue=true
2. **WF-002 execution** — collections_reminder workflow fires:
   - action: Load invoice details (amount, contact, due date)
   - notification: Send WhatsApp reminder to Contact via MessagingAdapter
   - Retry on WhatsApp rate-limit (max_retries=3, backoff=60s)
3. **Collection record** — Collection entity created or updated; days_overdue incremented
4. **Agent follow-up** — Agent views collections.html queue; updates Collection.status (pending→contacted→promised)
5. **Payment receipt** — Customer pays via JazzCash/Easypaisa (stub) or bank transfer
6. **Reconciliation** — POST /collections/:id/reconcile; Invoice.status→paid; Collection.status→paid

**System Workflow:** WF-002 (collections_reminder)
**trigger_events:** `["invoice.overdue.v1"]`
**max_retries:** 3, **timeout_seconds:** 120

**Entities involved:** Invoice, Collection, Contact, Payment, WorkflowExecution, AuditLog

**Roles involved:** manager (configure), agent (collections queue), auditor (read-only)

**API endpoints involved:**
- GET /invoice-summaries, GET /collections, POST /collections/:id/reconcile
- POST /payments (stub), POST /payment-webhooks (stub)
- GET /workflows/runs (execution monitoring)

**Frontend pages involved:**
- collections.html (B-08), invoices.html (B-09), invoices-detail.html (C-08)
- finance-analytics.html (H-04)

**Known constraint:** WhatsApp reminders may fail on rate-limit; WF-002 retries automatically (exec-002, exec-005 show this pattern)

---

## System Workflows (5 Seeded, Non-Editable)

### WF-001 — Lead Follow-up Enforcement
**workflow_key:** lead_followup_enforcement
**Trigger:** lead.idle.v1
**Steps:** (1) condition: idle_days > threshold; (2) action: create FollowupTask; (3) notification: WhatsApp alert to owner
**Entities:** Lead, FollowupTask, User (owner)
**max_retries:** 3, **timeout_seconds:** 300
**Status:** Active (seeded)

### WF-002 — Collections Auto-Reminder
**workflow_key:** collections_reminder
**Trigger:** invoice.overdue.v1
**Steps:** (1) action: load invoice; (2) notification: WhatsApp reminder to Contact
**Entities:** Invoice, Contact, Payment, WorkflowExecution
**max_retries:** 3, **timeout_seconds:** 120
**Status:** Active (seeded); retries on WhatsApp rate-limit

### WF-003 — SLA Breach Notification
**workflow_key:** sla_breach_notify
**Trigger:** case.sla.breached.v1, case.sla.first_response_breached.v1
**Steps:** (1) action: load case; (2) action: escalate case → ESCALATED, increment escalation_level; (3) notification: notify supervisor; (4) action: log to AuditLog
**Entities:** Case, CaseEscalation, User (supervisor), AuditLog
**max_retries:** 3, **timeout_seconds:** 300
**Status:** Active (seeded)

### WF-004 — Lead Territory Assignment
**workflow_key:** lead_assignment
**Trigger:** lead.created.v1
**Steps:** (1) action: evaluate TerritoryRules for lead attributes; (2) action: set owner_id, create LeadAssignment
**Entities:** Lead, Territory, TerritoryRule, LeadAssignment, User
**max_retries:** 3, **retry_backoff_seconds:** 30, **timeout_seconds:** 60
**Status:** Active (seeded)

### WF-005 — Opportunity Stage Change Notification
**workflow_key:** opportunity_stage_notify
**Trigger:** opportunity.stage.changed.v1
**Steps:** (1) condition: stage in notification-enabled stages; (2) notification: send stage alert to team; (3) action: refresh forecast via predictive_forecasting
**Entities:** Opportunity, User (team), Forecast
**max_retries:** 3, **timeout_seconds:** 120
**Status:** Active (seeded)

---

## System Events Catalog

| Event | Emitter | Consumers |
|---|---|---|
| lead.created.v1 | POST /leads | WF-004 (territory assignment) |
| lead.idle.v1 | followup service scheduler | WF-001 (followup enforcement) |
| lead.stage.changed.v1 | repo.transitionStage() | audit logging |
| invoice.overdue.v1 | billing service scheduler | WF-002 (collections reminder) |
| case.sla.breached.v1 | SLA monitor in support_console | WF-003 (SLA breach notify) |
| case.sla.first_response_breached.v1 | SLA monitor | WF-003 |
| opportunity.stage.changed.v1 | PATCH /opportunities/:id | WF-005 (stage notify) |
| opportunity.closed.v1 | PATCH /opportunities/:id (terminal stage) | audit, forecasting |

**Source:** src/event_bus/catalog_events.py, src/event_bus/catalog_schema.py

---

## Automation Workflows (src/automation_journeys/)

`src/automation_journeys/` handles multi-step marketing/sales automation journeys beyond event-based workflows. Journeys are sequences of timed/conditional steps mapped to campaigns and lead lifecycle stages.

Evidence: `backend/src/automation_journeys/workflow_mapping.py` — maps journey triggers to workflow events.

**API surface (confirmed Phase 3.25 from automation_journeys/api.py):**
- POST /api/v1/journeys — create journey (JourneyDefinition → JourneyService.create_journey)
- POST /api/v1/journeys/{journey_id}/activations — start journey (event-triggered → JourneyService.start_journey)
- POST /api/v1/journeys/{journey_id}/deactivations — stop journey (JourneyService.stop_journey)
- Journey execution triggered by InMemoryEventBus events; journey definitions in automation_journeys/entities.py
- Event integration via workflow_mapping.py which maps journey triggers to EVENT_NAME_SET events

---

## Integration Workflows

### WhatsApp Send/Receive
- **Receive:** 4 provider webhooks (Meta, Gupshup, Dialog360, Twilio) → idempotent processing → Conversation + Message creation
- **Send:** POST /inbox/conversations/:id/messages → MessagingAdapter → provider-specific SDK
- **Provider selection:** Configured at org level via integrations.html (G-05); adapter registry wired at startup

### Payment Webhooks
- **JazzCash:** POST /payment-webhooks/jazzcash → stub response (stub_mode=True)
- **Easypaisa:** POST /payment-webhooks/easypaisa → stub response (stub_mode=True)
- **Proof upload:** POST /payment-webhooks/log — payment proof logging
- **Note:** Real payment processing blocked until P-016 credentials received

---

## Cross-Module Dependencies

| Workflow | Depends On |
|---|---|
| Lead-to-Deal (WF-A) | Lead Management + Follow-up + Territory + Opportunities + CPQ + Invoice |
| Deal-to-Invoice (WF-B) | Opportunities + CPQ + Finance + Payment Rails + Collections |
| Case Lifecycle (WF-C) | Cases + Support + Knowledge Base + Audit |
| WhatsApp Conversation (WF-D) | Inbox + WhatsApp Adapters + Contacts + Intent Engine |
| Payment Collection (WF-E) | Finance + Collections + WhatsApp (WF-002) + Subscriptions |
| WF-001 Lead Enforcement | Lead Management + Follow-up + WhatsApp Engine |
| WF-002 Collections Reminder | Finance + WhatsApp Engine + Payment Webhooks |
| WF-003 SLA Breach | Cases + Audit + User (supervisor notification) |
| WF-004 Territory Assignment | Leads + Territory + RBAC |
| WF-005 Opp Stage Notify | Opportunities + Forecasting + User (team notification) |

---

*End PRODUCT_WORKFLOWS.md*
