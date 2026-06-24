---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Derived From: DESIGN-SPEC.md, FEATURE_SCOPE.md, FULLSTACK_STITCHING_CONTRACT.md, DOMAIN_MODEL.md
---

# FRONTEND SCREEN CATALOG — Pakistan CRM OS

Full screen authority for each of the 75 custom CRM pages. Organized by archetype. Each entry documents purpose, users, permissions, APIs, entities, workflows, actions, navigation, related screens, and UI states.

---

## ARCHETYPE A — Dashboard / KPI Overview (13 pages)

Spec: docs/b9-p01-dashboard-kpi.md
Layout: 5-zone — posture strip → primary KPIs → execution queue → trend chart → risk/anomaly panel

---

### A-01 — Owner / Sales Dashboard

**File:** dashboard.html
**Route:** /app/dashboard
**Purpose:** Executive posture strip and primary KPIs for tenant owner and sales managers. Entry point after login.

**Primary Users:** tenant_owner, tenant_admin, manager
**Required Permissions:** leads.read, opportunities.read, analytics.view_basic
**API Dependencies:**
- GET /leads (KPI counts, idle flags)
- GET /opportunities (pipeline value, stage distribution)
- GET /forecasts (weighted pipeline value)
- GET /ai/copilot/suggestions (risk flags zone)

**Data Dependencies (Entities):** Lead, Opportunity, Forecast, CopilotSuggestion
**Workflows Supported:** WF-A (Lead-to-Deal) entry monitoring, WF-001 (follow-up compliance)
**Actions Available:** Navigate to follow-up queue, navigate to at-risk deals, navigate to lead queue
**Navigation Entry Points:** Sidebar "Dashboard" (home icon); direct URL post-login
**Related Screens:** followups.html (B-01), leads.html (B-02), sales-dashboard.html (A-04)

**UI States:**
- Loading: Skeleton cards while API responds
- Empty: No leads/opportunities yet — onboarding prompt shown
- Error: Graceful fallback to crm-dummy.js data
- Live: KPI tiles, posture strip, execution queue DataTable, trend chart

---

### A-02 — Lead Funnel Dashboard

**File:** leads-dashboard.html
**Route:** /app/sales/leads/dashboard
**Purpose:** Lead funnel visualization with KPI tiles and stage distribution chart.

**Primary Users:** All CRM roles
**Required Permissions:** leads.read
**API Dependencies:** GET /leads (stage breakdown), GET /followups (idle count)
**Data Dependencies:** Lead, LeadHistory, FollowupTask
**Workflows Supported:** WF-A step monitoring (stages new→won/lost)
**Actions Available:** Navigate to lead queue, navigate to follow-up queue
**Navigation Entry Points:** Sidebar "Sales" → "Lead Dashboard"
**Related Screens:** leads.html (B-02), followups.html (B-01)

**UI States:** Loading / Funnel chart with stage counts / Empty (no leads yet) / Error fallback

---

### A-03 — Customer Health Dashboard

**File:** contacts-health.html
**Route:** /app/contacts/health
**Purpose:** Contact completeness and health KPIs — completeness score distribution, open cases, idle contacts.

**Primary Users:** manager, tenant_admin
**Required Permissions:** contacts.read, cases.read
**API Dependencies:** GET /contacts (completeness_score), GET /cases (open_cases count)
**Data Dependencies:** Contact, Case
**Workflows Supported:** Contact health monitoring; support escalation visibility
**Actions Available:** Navigate to contact list, navigate to case queue
**Navigation Entry Points:** Sidebar "Contacts" → "Health Dashboard"
**Related Screens:** contacts.html (B-03), cases.html (B-05)

**UI States:** Loading / KPI tiles + completeness distribution chart / Empty / Error fallback

---

### A-04 — Opportunity Pipeline Dashboard

**File:** sales-dashboard.html
**Route:** /app/sales/dashboard
**Purpose:** Pipeline overview with forecast categories, stage funnel, and deal value by rep.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** opportunities.read, ai.view_forecasts
**API Dependencies:** GET /opportunities, GET /forecasts
**Data Dependencies:** Opportunity, OpportunityLineItem, Forecast
**Workflows Supported:** WF-005 (opportunity stage change) monitoring
**Actions Available:** Navigate to cockpit, navigate to opportunity detail
**Navigation Entry Points:** Sidebar "Sales" → "Pipeline Dashboard"
**Related Screens:** sales-cockpit.html (D-01), opportunities-detail.html (C-04)

**UI States:** Loading / Pipeline KPIs + forecast donut + stage bar chart / Empty / Error fallback

---

### A-05 — Quote Approval Dashboard

**File:** quotes-dashboard.html
**Route:** /app/sales/quotes/dashboard
**Purpose:** Pending quote approvals queue with value totals and approval status breakdown.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** quotes.read, quotes.approve
**API Dependencies:** GET /quotes (status=pending, requires_approval=true)
**Data Dependencies:** Quote
**Workflows Supported:** WF-A step 8 (quote approval)
**Actions Available:** Navigate to quote detail, approve/reject inline
**Navigation Entry Points:** Sidebar "Sales" → "Quotes" → "Approval Dashboard"
**Related Screens:** quotes-detail.html (C-06), quote-builder.html (I-05)

**UI States:** Loading / Pending queue DataTable + value KPIs / Empty (no pending quotes) / Error fallback

---

### A-06 — Subscription Revenue Dashboard

**File:** subscriptions-dashboard.html
**Route:** /app/finance/subscriptions/dashboard
**Purpose:** MRR, ARR, churn rate, renewal rate KPIs with cohort retention chart and delinquent subscription queue.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** analytics.view_basic, collections.view_overdue
**API Dependencies:** GET /subscriptions (status breakdown, MRR/ARR aggregate)
**Data Dependencies:** Subscription, Account
**Workflows Supported:** WF-E (Payment Collection) delinquent monitoring
**Actions Available:** Navigate to subscription detail, navigate to collections
**Navigation Entry Points:** Sidebar "Finance" → "Subscriptions"
**Related Screens:** subscriptions-detail.html (C-09), collections.html (B-08)

**Pakistan-Market:** MRR/ARR displayed in PKR with lakh/crore notation. P-016 stub comment visible in billing section.

**UI States:** Loading / MRR KPIs + cohort chart + delinquent queue / Empty / Error fallback

---

### A-07 — Case SLA Operations Dashboard

**File:** support-dashboard.html
**Route:** /app/support/dashboard
**Purpose:** SLA compliance posture — breach count, SLA KPIs, at-risk case queue, case volume trend.

**Primary Users:** manager, tenant_admin
**Required Permissions:** cases.read, analytics.view_basic
**API Dependencies:** GET /cases (SLA breach status), GET /cases (volume by day)
**Data Dependencies:** Case, CaseEscalation, SupportQueue
**Workflows Supported:** WF-C monitoring; WF-003 (SLA breach) audit
**Actions Available:** Navigate to at-risk cases, navigate to support console
**Navigation Entry Points:** Sidebar "Support" → "Dashboard"
**Related Screens:** cases.html (B-05), support-console.html (E-01), cases-detail.html (C-05)

**UI States:** Loading / Breach posture strip + KPI tiles + at-risk DataTable + area chart / Empty / Error fallback

---

### A-08 — Communication Engagement Dashboard

**File:** engagement-dashboard.html
**Route:** /app/marketing/engagement
**Purpose:** WhatsApp/email delivery, open rate, reply rate KPIs with channel engagement bar chart and active campaigns list.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** campaigns.read, analytics.view_basic
**API Dependencies:**
- GET /communications/engagement (delivery/open/reply KPIs)
- GET /campaigns (active campaigns queue)

**Data Dependencies:** Campaign, Conversation
**Workflows Supported:** WF-D (WhatsApp Conversation) monitoring
**Wired:** Yes (2026-05-31 via v1-communications.routes.js)
**Actions Available:** Navigate to marketing workspace, navigate to campaign
**Navigation Entry Points:** Sidebar "Marketing" → "Engagement"
**Related Screens:** marketing-workspace.html (F-01), inbox.html (L-01)

**Pakistan-Market:** WhatsApp opt-in rate and delivery stats are primary metrics. SMS stats secondary.

**UI States:** Loading / KPI tiles + channel bar chart + campaigns list / Empty / Error fallback

---

### A-09 — Knowledge Effectiveness Dashboard

**File:** knowledge-dashboard.html
**Route:** /app/support/knowledge/dashboard
**Purpose:** Article deflection rate, stale article queue, adoption trend chart.

**Primary Users:** manager, tenant_admin
**Required Permissions:** knowledge.read, analytics.view_basic
**API Dependencies:** GET /knowledge (articles list, last_published, view_count)
**Data Dependencies:** KnowledgeArticle
**Workflows Supported:** WF-C step 8 (knowledge linking)
**Actions Available:** Navigate to article detail, publish stale article
**Navigation Entry Points:** Sidebar "Support" → "Knowledge Base"
**Related Screens:** knowledge-article.html (C-12), cases.html (B-05)

**UI States:** Loading / KPI tiles + stale queue + trend chart / Empty / Error fallback

---

### A-10 — Workflow Automation Dashboard

**File:** workflows-dashboard.html
**Route:** /app/workflows/dashboard
**Purpose:** Workflow execution KPIs — success rate, failure count, execution volume; failed queue; pass/fail bar chart.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** workflows.read, analytics.view_basic
**API Dependencies:** GET /workflows, GET /workflows/runs
**Data Dependencies:** WorkflowDefinition, WorkflowExecution
**Workflows Supported:** All 5 system workflows + custom workflows monitoring
**Actions Available:** Navigate to workflow detail, retry failed workflow
**Navigation Entry Points:** Sidebar "Workflows" → "Dashboard"
**Related Screens:** workflow-run-detail.html (C-10), workflow-builder.html (K-01)

**UI States:** Loading / Failure posture strip + KPI tiles + failed queue + bar chart / Empty / Error fallback

---

### A-11 — Tenant & Entitlement Dashboard

**File:** tenants-dashboard.html
**Route:** /app/admin/tenants
**Purpose:** Super-admin view of all tenants — plan distribution, seat usage, entitlements at limit.

**Primary Users:** tenant_owner only
**Required Permissions:** admin.manage_tenants
**API Dependencies:** GET /admin/tenants
**Data Dependencies:** Tenant
**Workflows Supported:** Tenant provisioning monitoring
**Actions Available:** Navigate to tenant detail
**Navigation Entry Points:** Sidebar "Admin" → "Tenants" (tenant_owner only)
**Related Screens:** identity-dashboard.html (A-12), audit-dashboard.html (A-13)

**UI States:** Loading / Plan KPI tiles + entitlement queue + tenant summary table / Empty / Error fallback

---

### A-12 — Identity & Access Posture Dashboard

**File:** identity-dashboard.html
**Route:** /app/admin/identity
**Purpose:** Role distribution, escalation events queue, login activity chart.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.read_audit_logs, admin.manage_users
**API Dependencies:** GET /admin/users, GET /admin/audit-logs
**Data Dependencies:** User, Role, AuditLog
**Workflows Supported:** RBAC audit monitoring
**Actions Available:** Navigate to user management, navigate to RBAC audit
**Navigation Entry Points:** Sidebar "Admin" → "Identity"
**Related Screens:** user-management-crm.html (G-02), rbac-audit.html (J-04)

**UI States:** Loading / Role distribution KPIs + escalation queue + login heatmap / Empty / Error fallback

---

### A-13 — Platform Audit & Reliability Dashboard

**File:** audit-dashboard.html
**Route:** /app/admin/audit/dashboard
**Purpose:** Deny events posture, audit KPIs (allow/deny/warn), deny queue, action-type breakdown chart.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.read_audit_logs
**API Dependencies:** GET /admin/audit-logs
**Data Dependencies:** AuditLog
**Workflows Supported:** Compliance monitoring; security event review
**Actions Available:** Navigate to audit log, export audit data
**Navigation Entry Points:** Sidebar "Admin" → "Audit"
**Related Screens:** audit-log.html (J-01), audit-report.html (H-06)

**UI States:** Loading / Deny posture strip + KPI tiles + deny queue + action-type chart / Empty / Error fallback

---

## ARCHETYPE B — List / Queue / Table View (11 pages)

Spec: docs/b9-p02-list-queue.md
Shell: filter bar → sortable columns → row quick actions → bulk actions → pagination

---

### B-01 — Follow-up Queue

**File:** followups.html
**Route:** /app/followups
**Purpose:** Overdue-first queue of all follow-up tasks; escalation level badges; complete and snooze actions inline.

**Primary Users:** All CRM roles
**Required Permissions:** tasks.read, tasks.complete, tasks.update
**API Dependencies:** GET /followups, POST /followups/:id/complete, POST /followups/:id/snooze
**Data Dependencies:** FollowupTask, Lead, User
**Workflows Supported:** WF-001 (lead follow-up enforcement); WF-A step 3 and 5
**Actions Available:** Mark complete, snooze, view lead detail
**Filter Chips:** escalation_level — none/reminder/warning/escalated/reassigned
**Navigation Entry Points:** Sidebar "Follow-ups" (primary nav — Tier 1 surface per adoption-ux.md)
**Related Screens:** leads-detail.html (C-01), leads.html (B-02)

**Known Issue:** T3 Place 3 CSS missing for dt_Followups (see DESIGN-SPEC.md B-01 notes)

**UI States:** Loading skeleton / Overdue-pinned DataTable / Empty (all caught up) / Error fallback

---

### B-02 — Lead Queue

**File:** leads.html
**Route:** /app/leads
**Purpose:** All leads with stage, priority, source filter chips and quick actions (view, reassign, new follow-up).

**Primary Users:** All CRM roles
**Required Permissions:** leads.read; leads.create (new lead button); leads.assign (reassign action)
**API Dependencies:** GET /leads, GET /leads/export
**Data Dependencies:** Lead, User, FollowupTask
**Workflows Supported:** WF-A entry; WF-001 monitoring
**Actions Available:** View lead, new lead, export CSV, reassign
**Filter Chips:** stage (new/qualifying/nurturing/proposal/negotiation/won/lost/disqualified), priority (hot/warm/cold)
**Navigation Entry Points:** Sidebar "Leads"
**Related Screens:** leads-detail.html (C-01), lead-new.html (I-01), followups.html (B-01)

**UI States:** Loading / DataTable with filter chips / Empty (no leads) / Error fallback

---

### B-03 — Contact List

**File:** contacts.html
**Route:** /app/contacts
**Purpose:** All contacts with health indicators — completeness score, open cases, idle flag; CSV export.

**Primary Users:** All CRM roles
**Required Permissions:** contacts.read; contacts.delete (SD-001 — hidden until OA-001 resolved)
**API Dependencies:** GET /contacts, GET /contacts/export, POST /contacts/import
**Data Dependencies:** Contact, Account
**Workflows Supported:** WF-A step 1 (contact lookup on lead capture); WF-C (case contact link)
**Actions Available:** View contact, new contact, CSV export, bulk import
**Navigation Entry Points:** Sidebar "Contacts"
**Related Screens:** contacts-detail.html (C-02), contact-new.html (I-02)

**Constraint (SD-001):** Delete button hidden for all roles. OA-001 pending.

**UI States:** Loading / DataTable + health badges / Empty / Error fallback

---

### B-04 — Account List

**File:** accounts.html
**Route:** /app/accounts
**Purpose:** Business account list with tier, industry, and balance columns; tier and industry filter chips.

**Primary Users:** All CRM roles
**Required Permissions:** accounts.read
**API Dependencies:** GET /accounts
**Data Dependencies:** Account, Contact
**Workflows Supported:** Account-level contact and opportunity management
**Actions Available:** View account, new account (admin)
**Filter Chips:** tier (enterprise/mid_market/sme), industry
**Navigation Entry Points:** Sidebar "Accounts"
**Related Screens:** accounts-detail.html (C-03), contacts.html (B-03)

**UI States:** Loading / DataTable with PKR balance column / Empty / Error fallback

---

### B-05 — Ticket / Case Queue

**File:** cases.html
**Route:** /app/support/cases
**Purpose:** Support case queue with dual Status × SLA filter chips, SLA/priority/status badges, cross-filter JS logic.

**Primary Users:** All CRM roles
**Required Permissions:** cases.read; cases.create (new case button)
**API Dependencies:** GET /cases
**Data Dependencies:** Case, SupportQueue, User (agent)
**Workflows Supported:** WF-C step 2–3 (queue routing + agent assignment)
**Actions Available:** View case, new case, filter by status + SLA
**Filter Chips:** status (OPEN/ASSIGNED/IN_PROGRESS/WAITING_ON_CUSTOMER/RESOLVED/ESCALATED/CLOSED) + SLA state (on_track/at_risk/breached)
**Navigation Entry Points:** Sidebar "Support" → "Cases"
**Related Screens:** cases-detail.html (C-05), case-new.html (I-04), support-console.html (E-01)

**UI States:** Loading / DataTable with dual filter / Empty / Error fallback

---

### B-06 — Activity Feed

**File:** activity.html
**Route:** /app/activity
**Purpose:** Read-only chronological activity feed — calls, WhatsApp messages, emails, meetings, notes across all entities.

**Primary Users:** All CRM roles
**Required Permissions:** activities.read
**API Dependencies:** GET /activities
**Data Dependencies:** ActivityEvent
**Workflows Supported:** Audit trail browsing
**Actions Available:** Read-only; no inline edits
**Navigation Entry Points:** Sidebar "Activity"
**Related Screens:** leads-detail.html (C-01), contacts-detail.html (C-02)

**UI States:** Loading / Timeline list / Empty (no recent activity) / Error fallback

---

### B-07 — Task Queue

**File:** tasks.html
**Route:** /app/tasks
**Purpose:** General task queue with overdue-pinned sort; task completion and assignment actions.

**Primary Users:** All CRM roles
**Required Permissions:** tasks.read; tasks.complete; tasks.assign
**API Dependencies:** GET /tasks, PATCH /tasks/:id
**Data Dependencies:** Task, User
**Workflows Supported:** General task management outside of lead follow-up
**Actions Available:** Mark complete, reassign, view linked entity
**Navigation Entry Points:** Sidebar "Tasks"
**Related Screens:** followups.html (B-01), leads-detail.html (C-01)

**UI States:** Loading / Overdue-pinned DataTable / Empty / Error fallback

---

### B-08 — Collections Queue

**File:** collections.html
**Route:** /app/collections
**Purpose:** Overdue invoice collection queue — days overdue, contact, next action; reconcile action.

**Primary Users:** All CRM roles (write: agent, manager, tenant_admin)
**Required Permissions:** collections.read; collections.view_overdue; collections.reconcile (reconcile action)
**API Dependencies:** GET /collections, POST /collections/:id/reconcile
**Data Dependencies:** Collection, Invoice, Contact, Account
**Workflows Supported:** WF-E (Payment Collection); WF-002 (Collections Auto-Reminder) monitoring
**Actions Available:** Mark contacted, reconcile (mark paid), view invoice
**Filter Chips:** status (pending/contacted/promised/paid/escalated/written_off)
**Navigation Entry Points:** Sidebar "Collections" (Tier 1 surface per adoption-ux.md)
**Related Screens:** invoices-detail.html (C-08), invoices.html (B-09)

**Pakistan-Market:** PKR amounts with lakh/crore formatting. JazzCash/Easypaisa reconciliation STUB (P-016).

**Known Issues:** T2 hardcoded delta text; T4 status filter chips misaligned with domain spec (DESIGN-SPEC B-08)

**UI States:** Loading / DataTable sorted by days_overdue DESC / Empty / Error fallback

---

### B-09 — Invoice Queue

**File:** invoices.html
**Route:** /app/finance/invoices
**Purpose:** All invoices with total, paid, balance, status columns; overdue rows in red; status filter chips.

**Primary Users:** All CRM roles
**Required Permissions:** collections.read
**API Dependencies:** GET /invoice-summaries
**Data Dependencies:** Invoice, Account, Contact
**Workflows Supported:** WF-B step 2 (invoice issuance); WF-B step 7 (reconciliation) monitoring
**Actions Available:** View invoice detail, download PDF (if supported)
**Filter Chips:** status (draft/sent/paid/overdue/partially_paid/cancelled)
**Navigation Entry Points:** Sidebar "Finance" → "Invoices"
**Related Screens:** invoices-detail.html (C-08), collections.html (B-08)

**Pakistan-Market:** PKR totals, overdue flag, JazzCash/Easypaisa STUB notice.

**UI States:** Loading / DataTable with overdue highlight / Empty / Error fallback

---

### B-10 — User Directory

**File:** users.html
**Route:** /app/admin/users
**Purpose:** Admin-only user directory with role badges, suspend and reset-password quick actions.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.manage_users
**API Dependencies:** GET /admin/users, PATCH /admin/users/:id (suspend), POST /admin/users/:id/reset-password
**Data Dependencies:** User, Role
**Workflows Supported:** User lifecycle (invite → suspend → deactivate)
**Actions Available:** Suspend user, reset password, view user
**Navigation Entry Points:** Sidebar "Admin" → "Users"
**Related Screens:** user-management-crm.html (G-02), identity-dashboard.html (A-12)

**UI States:** Loading / DataTable with role badges / Empty / Error fallback

---

### B-11 — Partner List

**File:** partners.html
**Route:** /app/partners
**Purpose:** Channel partner list with tier, YTD revenue (PKR), and commission columns; tier and status filter chips.

**Primary Users:** All CRM roles
**Required Permissions:** partners.read
**API Dependencies:** GET /partners
**Data Dependencies:** Partner, CommissionLedger
**Workflows Supported:** Partner deal registration and attribution tracking
**Actions Available:** View partner detail
**Filter Chips:** tier (gold/silver/bronze), status (active/inactive)
**Navigation Entry Points:** Sidebar "Partners"
**Related Screens:** partners-detail.html (C-11)

**Pakistan-Market:** PKR commission amounts.

**UI States:** Loading / DataTable with PKR column / Empty / Error fallback

---

## ARCHETYPE C — Entity Detail / 360 View (12 pages)

Spec: docs/b9-p06-entity-detail.md
Shell: sticky header strip → split pane (main + context) → inline edit → activity timeline

---

### C-01 — Lead Detail

**File:** leads-detail.html
**Route:** /app/leads/:lead_id
**Purpose:** Full lead view — stage badge, follow-up panel, activity timeline, lead score, assignment history.

**Primary Users:** All CRM roles
**Required Permissions:** leads.read; leads.update; leads.assign (reassign button)
**API Dependencies:** GET /leads/:id, PATCH /leads/:id, GET /leads/:id/next-action, GET /followups/lead/:id/canonical
**Data Dependencies:** Lead, LeadHistory, LeadAssignment, FollowupTask, Contact, CopilotSuggestion
**Workflows Supported:** WF-A stages 3–5 (follow-up + qualification); WF-001
**Actions Available:** Update stage, update priority, create follow-up, reassign, log activity
**Navigation Entry Points:** leads.html (B-02) row click; followups.html (B-01) lead link
**Related Screens:** contacts-detail.html (C-02), followups.html (B-01), opportunities-detail.html (C-04)

**UI States:** Loading / Sticky identity strip + tabbed pane + context panel / Not found / Error fallback

---

### C-02 — Customer 360

**File:** contacts-detail.html
**Route:** /app/contacts/:contact_id/360
**Purpose:** Full contact view — touchpoint timeline, linked account, cases, opportunities, tags.

**Primary Users:** All CRM roles
**Required Permissions:** contacts.read; contacts.update; contacts.delete (SD-001 — hidden)
**API Dependencies:** GET /contacts/:id, PATCH /contacts/:id, GET /cases (contact_id filter), GET /leads (contact_id filter)
**Data Dependencies:** Contact, Account, Lead, Case, ActivityEvent
**Workflows Supported:** WF-A contact lookup (step 1); WF-C contact linking (step 1)
**Actions Available:** Update contact fields, tag management, log activity; delete (SD-001 hidden)
**Navigation Entry Points:** contacts.html (B-03), cases-detail.html (C-05)
**Related Screens:** accounts-detail.html (C-03), leads-detail.html (C-01), cases-detail.html (C-05)

**UI States:** Loading / Identity strip + timeline + tab pane / Not found / Error fallback

---

### C-03 — Account Profile

**File:** accounts-detail.html
**Route:** /app/accounts/:account_id
**Purpose:** Business account view — contacts tab, opportunities tab, invoices tab, health and balance context.

**Primary Users:** All CRM roles
**Required Permissions:** accounts.read; accounts.update
**API Dependencies:** GET /accounts/:id, GET /contacts (account_id), GET /opportunities (account_id), GET /invoice-summaries (account_id)
**Data Dependencies:** Account, Contact, Opportunity, Invoice, ChurnPrediction
**Workflows Supported:** Account-level lifecycle monitoring
**Actions Available:** Update account, navigate to linked entities
**Tabs:** Details / Contacts / Opportunities / Invoices
**Navigation Entry Points:** accounts.html (B-04)
**Related Screens:** contacts-detail.html (C-02), opportunities-detail.html (C-04)

**UI States:** Loading / 4-tab split pane + context health panel / Not found / Error fallback

---

### C-04 — Opportunity Detail

**File:** opportunities-detail.html
**Route:** /app/opportunities/:opportunity_id
**Purpose:** Deal detail — stage, forecast category, amount, line items, linked quotes and activities.

**Primary Users:** All CRM roles
**Required Permissions:** opportunities.read; opportunities.update; opportunities.close (close deal button — manager+)
**API Dependencies:** GET /opportunities/:id, PATCH /opportunities/:id, GET /opportunities/:id/line-items, GET /quotes (opportunity_id)
**Data Dependencies:** Opportunity, OpportunityLineItem, Quote, Account, Contact
**Workflows Supported:** WF-A steps 6–9 (opportunity → quote → close); WF-005 trigger
**Actions Available:** Update stage, add line item, create quote, close won/lost (manager+)
**State Machine (stages):** qualification → discovery → proposal → negotiation → closed_won | closed_lost
**Navigation Entry Points:** sales-cockpit.html (D-01), leads-detail.html (C-01)
**Related Screens:** quotes-detail.html (C-06), sales-cockpit.html (D-01)

**Pakistan-Market:** Amount in PKR with lakh/crore formatting.

**UI States:** Loading / Sticky header + line items table + quotes tab / Not found / Error fallback

---

### C-05 — Case / Ticket Detail

**File:** cases-detail.html
**Route:** /app/support/cases/:case_id
**Purpose:** Case lifecycle management — SLA timer in header, state-gated Claim/Resolve buttons, conversation/fields/resolution tabs.

**Primary Users:** agent, manager, tenant_admin (read: all)
**Required Permissions:** cases.read; cases.update; cases.assign (Claim — agent+); cases.close (Resolve — manager+); cases.escalate (Escalate — manager+)
**API Dependencies:** GET /cases/:id, POST /cases/:id/assign, POST /cases/:id/comments, POST /cases/:id/resolve, POST /cases/:id/close, POST /cases/:id/escalate, POST /cases/:id/reopen, POST /cases/:id/link-article
**Data Dependencies:** Case, CaseComment, CaseEscalation, SupportQueue, KnowledgeArticle, User
**Workflows Supported:** WF-C steps 3–11 (assignment through closure); WF-003 monitoring
**Actions Available:** Claim, comment (internal/customer), resolve, close (admin), escalate, reopen (14-day window), link knowledge article
**State Machine (Case status):** OPEN → ASSIGNED | CLOSED; ASSIGNED → IN_PROGRESS | OPEN | ESCALATED; IN_PROGRESS → WAITING_ON_CUSTOMER | RESOLVED | ESCALATED; RESOLVED → CLOSED | IN_PROGRESS; CLOSED → OPEN (14-day window only)
**SLA Tiers:** tier_1_critical: 1h/8h; tier_2_high: 4h/24h; tier_3_standard: 8h/72h; tier_4_low: 24h/168h
**Tabs:** Conversation / Fields / Resolution
**Navigation Entry Points:** cases.html (B-05), support-console.html (E-01)
**Related Screens:** knowledge-article.html (C-12), cases.html (B-05)

**UI States:** Loading / Sticky SLA timer strip + state-gated buttons + 3-tab pane / Not found / Error fallback

---

### C-06 — Quote Detail

**File:** quotes-detail.html
**Route:** /app/sales/quotes/:quote_id
**Purpose:** Quote view — line items, discount, approval history, terms; approve/reject controls for managers.

**Primary Users:** All CRM roles
**Required Permissions:** quotes.read; quotes.approve (approve/reject — manager+); quotes.convert_to_order (accept — manager+)
**API Dependencies:** GET /quotes/:id, PATCH /quotes/:id, POST /quotes/:id/accept
**Data Dependencies:** Quote, Order (created on acceptance)
**Workflows Supported:** WF-A step 8 (approval); WF-A step 9 (order creation on acceptance)
**Actions Available:** Approve, reject, accept (→ creates Order), view line items, view approval history
**State Machine (Quote status):** draft → sent → approved | rejected | expired; approved → accepted → Order
**Navigation Entry Points:** quotes-dashboard.html (A-05), opportunities-detail.html (C-04)
**Related Screens:** orders-detail.html (C-07), approval-lanes.html (K-04)

**Pakistan-Market:** Line item amounts and discount in PKR.

**UI States:** Loading / Line items table + approval history + terms / Not found / Error fallback

---

### C-07 — Order Detail

**File:** orders-detail.html
**Route:** /app/sales/orders/:order_id
**Purpose:** Confirmed order view — immutable badge, line items, fulfilment status, linked invoice.

**Primary Users:** All CRM roles
**Required Permissions:** orders.read; orders.fulfil (fulfil action — manager+)
**API Dependencies:** GET /orders/:id
**Data Dependencies:** Order, Invoice (linked)
**Workflows Supported:** WF-B step 1 (order creation from quote); WF-B step 2 (invoice linking)
**Actions Available:** View only (immutable post-fulfilment); fulfil order (manager+)
**State Machine (Order status):** processing → fulfilled | cancelled
**Navigation Entry Points:** quotes-detail.html (C-06)
**Related Screens:** invoices-detail.html (C-08)

**Pakistan-Market:** Total in PKR.

**UI States:** Loading / Identity strip + line items + fulfilment status + linked invoice / Not found / Error fallback

---

### C-08 — Invoice Detail

**File:** invoices-detail.html
**Route:** /app/finance/invoices/:invoice_id
**Purpose:** Invoice view — total/paid/balance strip, payment history, proof tab, reconciliation status.

**Primary Users:** All CRM roles
**Required Permissions:** collections.read; collections.record_payment (record payment — collections role+); collections.reconcile (reconcile)
**API Dependencies:** GET /invoice-summaries/:id, POST /payments (stub), POST /collections/:id/reconcile
**Data Dependencies:** Invoice, Payment, Collection, Account, Contact
**Workflows Supported:** WF-B steps 4–7 (payment → reconciliation); WF-E steps 3–6
**Actions Available:** Record payment (stub), reconcile, download PDF, view proof
**Tabs:** Overview / Payment History / Proof Upload / Reconciliation
**Navigation Entry Points:** invoices.html (B-09), collections.html (B-08)
**Related Screens:** collections.html (B-08), orders-detail.html (C-07)

**Pakistan-Market:** PKR amounts. JazzCash/Easypaisa payment buttons in STUB state (P-016).

**UI States:** Loading / Total/Paid/Balance strip + payment history DataTable + tabs / Not found / Error fallback

---

### C-09 — Subscription Detail

**File:** subscriptions-detail.html
**Route:** /app/finance/subscriptions/:subscription_id
**Purpose:** Subscription lifecycle — status-gated action buttons, MRR/ARR strip, billing history, churn risk context.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** collections.read; admin.system_config (pause/cancel — admin)
**API Dependencies:** GET /subscriptions/:id
**Data Dependencies:** Subscription, Account, ChurnPrediction
**Workflows Supported:** WF-E (collections monitoring for past_due subscriptions)
**Actions Available:** Pause (active), cancel (active/trialing), reactivate (paused/past_due) — status-gated
**State Machine (Subscription status):** draft → trialing → active → past_due | paused → cancelled | expired
**Tabs:** Details / Billing History / Usage / Plan History
**Navigation Entry Points:** subscriptions-dashboard.html (A-06)
**Related Screens:** accounts-detail.html (C-03), invoices-detail.html (C-08)

**Pakistan-Market:** MRR/ARR in PKR. P-016 payment method stub.

**UI States:** Loading / MRR strip + status-gated buttons + 4-tab pane / Not found / Error fallback

---

### C-10 — Workflow Execution Detail

**File:** workflow-run-detail.html
**Route:** /app/workflows/runs/:execution_id
**Purpose:** Single workflow run — execution identity strip, state-gated Retry button, step log, error details.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** workflows.read
**API Dependencies:** GET /workflows/runs/:id, POST /workflows/:id/retry
**Data Dependencies:** WorkflowExecution, WorkflowStepRecord, WorkflowDefinition
**Workflows Supported:** All 5 system workflows + custom; monitoring of WF-001 through WF-005
**Actions Available:** Retry (failed/retrying executions only — creates new child execution); view step trace
**State Machine (Execution status):** running → succeeded | failed | retrying | cancelled
**Tabs:** Execution Log / Step Trace / Error Details
**Navigation Entry Points:** workflows-dashboard.html (A-10)
**Related Screens:** workflow-builder.html (K-01), workflows-dashboard.html (A-10)

**UI States:** Loading / Identity strip + step trace DataTable + error details / Not found / Error fallback

---

### C-11 — Partner Detail

**File:** partners-detail.html
**Route:** /app/partners/:partner_id
**Purpose:** Partner profile — deal registrations, commission ledger, relationship history, attribution summary.

**Primary Users:** All CRM roles
**Required Permissions:** partners.read; partners.update (admin)
**API Dependencies:** GET /partners/:id
**Data Dependencies:** Partner, CommissionLedger, DealRegistration
**Workflows Supported:** Partner attribution and commission tracking
**Actions Available:** View commission ledger, view deal registrations, update partner (admin)
**Tabs:** Details / Opportunities / Commission Ledger / Relationship History
**Navigation Entry Points:** partners.html (B-11)
**Related Screens:** opportunities-detail.html (C-04)

**Pakistan-Market:** Commission amounts in PKR.

**UI States:** Loading / Identity strip + 4-tab pane + attribution context / Not found / Error fallback

---

### C-12 — Knowledge Article Detail

**File:** knowledge-article.html
**Route:** /app/support/knowledge/:article_id
**Purpose:** Knowledge article view — state-gated Publish/Edit buttons, content tabs, article performance stats.

**Primary Users:** All CRM roles (edit/publish: manager+, tenant_admin)
**Required Permissions:** knowledge.read; knowledge.update (edit); knowledge.publish (publish/unpublish)
**API Dependencies:** GET /knowledge/:id, PATCH /knowledge/:id, POST /knowledge/:id/publish
**Data Dependencies:** KnowledgeArticle
**Workflows Supported:** WF-C step 8 (link article to case); Feature 62 (publish workflow: draft→review→published)
**Actions Available:** Read (all); Edit (knowledge.update); Publish (knowledge.publish); Unpublish; Link to case
**State Machine (Article status):** draft → review → published; published → unpublished
**Tabs:** Content / Version History / Related / Feedback
**Navigation Entry Points:** knowledge-dashboard.html (A-09), support-console.html (E-01)
**Related Screens:** cases-detail.html (C-05), knowledge-dashboard.html (A-09)

**UI States:** Loading / State-gated buttons + 4-tab content pane + stats context / Not found / Error fallback

---

## ARCHETYPE D — Sales Cockpit (1 page)

Spec: docs/b9-p03-sales-cockpit.md

### D-01 — Sales Cockpit

**File:** sales-cockpit.html
**Route:** /app/sales/cockpit
**Purpose:** Pipeline execution workspace — kanban deal board, deal workspace panel, forecast context, next-actions queue.

**Primary Users:** agent, manager, tenant_admin
**Required Permissions:** opportunities.read; leads.read; ai.view_scores; ai.view_forecasts
**API Dependencies:** GET /opportunities, GET /leads, GET /forecasts, GET /ai/copilot/suggestions
**Data Dependencies:** Opportunity, Lead, Forecast, CopilotSuggestion
**Workflows Supported:** WF-A stage progression (stages 6–9); WF-005 trigger
**Actions Available:** Move deal to next stage (kanban drag), view deal workspace, follow next-action suggestion
**Zones:** Pipeline execution rail / Kanban board / Deal workspace pane / Forecast + next-actions context
**Navigation Entry Points:** Sidebar "Sales" → "Cockpit"
**Related Screens:** opportunities-detail.html (C-04), leads.html (B-02)

**Pakistan-Market:** Pipeline values in PKR with lakh/crore notation.

**UI States:** Loading / Pipeline kanban + deal pane / Empty (no opportunities) / Error fallback

---

## ARCHETYPE E — Support Console (1 page)

Spec: docs/b9-p04-support-console.md

### E-01 — Support Console

**File:** support-console.html
**Route:** /app/support/console
**Purpose:** Agent workspace — SLA queue sorted by due time, conversation thread view, escalation controls.

**Primary Users:** agent, manager, tenant_admin
**Required Permissions:** cases.read; cases.assign; inbox.read; inbox.claim
**API Dependencies:** GET /cases, GET /support/queues, POST /cases/:id/assign, POST /cases/:id/escalate
**Data Dependencies:** Case, CaseEscalation, SupportQueue, User
**Workflows Supported:** WF-C steps 2–7 (queue routing through resolution); WF-003 monitoring
**Actions Available:** Claim case, reply, escalate, view thread, select from queue
**Layout:** 3-pane — SLA queue (left) / Conversation thread (center) / Context panel (right)
**SLA Queue Sort:** sla_first_response_due_at ASC (most urgent first)
**Navigation Entry Points:** Sidebar "Support" → "Console"
**Related Screens:** cases-detail.html (C-05), cases.html (B-05)

**UI States:** Loading / 3-pane layout with SLA timer in header / Empty queue / Error fallback

---

## ARCHETYPE F — Marketing / Campaign Workspace (1 page)

Spec: docs/b9-p05-marketing-workspace.md

### F-01 — Marketing Workspace

**File:** marketing-workspace.html
**Route:** /app/marketing/campaigns
**Purpose:** Campaign lifecycle dashboard — active campaigns DataTable, status filter chips, campaign KPIs.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** campaigns.read; campaigns.create (new button); campaigns.activate
**API Dependencies:** GET /campaigns
**Data Dependencies:** Campaign, Segment
**Workflows Supported:** Campaign draft → segment validation → activation → attribution lifecycle
**Actions Available:** View campaign, new campaign, filter by status/type
**Filter Chips:** status (draft/active/paused/completed); type (whatsapp_blast/email/sms)
**Navigation Entry Points:** Sidebar "Marketing" → "Campaigns"
**Related Screens:** campaign-new.html (I-06), marketing-analytics.html (H-02), engagement-dashboard.html (A-08)

**Pakistan-Market:** WhatsApp blast is the primary campaign type. PTA compliance hook wired in adapters.

**UI States:** Loading / KPI cards + DataTable + filter chips / Empty (no campaigns) / Error fallback

---

## ARCHETYPE G — Settings / Admin / RBAC (9 pages)

Spec: docs/b9-p09-settings-admin.md
Shell: settings sidebar (list-group, NOT nav-pills) → content panel → permission-gated write states

---

### G-01 — Organization Settings

**File:** org-settings.html
**Route:** /app/settings/org
**Purpose:** Tenant-level configuration — identity/branding, locale (PKR/PKT), business hours.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.system_config
**API Dependencies:** GET /admin/settings, PATCH /admin/settings
**Data Dependencies:** Tenant
**Actions Available:** Edit org name, logo, timezone, currency (PKR fixed), business hours
**Navigation Entry Points:** Sidebar "Settings" → "Organization"; shared settings left-nav
**Related Screens:** All G-pages share the settings left-nav

---

### G-02 — User Management

**File:** user-management-crm.html
**Route:** /app/admin/users/manage
**Purpose:** User lifecycle — 2-step Invite User modal, Edit Role modal, Suspend and Reset Password confirm modals.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.manage_users; admin.manage_roles (role edit)
**API Dependencies:** GET /admin/users, POST /admin/users/invite, PATCH /admin/users/:id, POST /admin/users/:id/reset-password
**Data Dependencies:** User, Role
**Actions Available:** Invite user (2-step modal), edit role, suspend (confirm modal), reset password (confirm modal)
**Navigation Entry Points:** Sidebar "Admin" → "User Management"
**Related Screens:** roles.html (G-03), users.html (B-10), identity-dashboard.html (A-12)

---

### G-03 — Role & Permission Editor

**File:** roles.html
**Route:** /app/admin/roles
**Purpose:** Role registry — roles table, permission scope registry (read-only). Cannot delete role with active users.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.manage_roles
**API Dependencies:** GET /admin/roles, POST /admin/roles, PATCH /admin/roles/:id, DELETE /admin/roles/:id
**Data Dependencies:** Role, Permission
**Actions Available:** Create custom role, edit role permissions, delete role (blocked if active users); view scope registry
**Business Rule:** System roles (is_system=true) cannot be deleted
**Navigation Entry Points:** Sidebar "Admin" → "Roles"
**Related Screens:** user-management-crm.html (G-02), rbac-audit.html (J-04)

---

### G-04 — Billing & Subscription Settings

**File:** billing-settings.html
**Route:** /app/settings/billing
**Purpose:** Tenant billing plan, seat count, renewal date, invoice history. Payment methods section is STUB.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.system_config
**API Dependencies:** GET /billing/subscription, GET /billing/invoices
**Wired:** Yes (2026-05-31 via v1-billing.routes.js)
**Data Dependencies:** Subscription, Invoice
**Actions Available:** View plan/seats/renewal; view invoice history; payment method (STUB — P-016)
**Navigation Entry Points:** Sidebar "Settings" → "Billing"

**Constraint (SD-002):** Payment method section displays stub state. P-016 pending JazzCash/Easypaisa credentials.

---

### G-05 — Integration Settings

**File:** integrations.html
**Route:** /app/settings/integrations
**Purpose:** 3rd-party integrations — WhatsApp provider status, payment rails status, connection test.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.system_config
**API Dependencies:** GET /integrations, POST /integrations/:provider/test
**Wired:** Yes (2026-05-31 via v1-integrations.routes.js)
**Data Dependencies:** Integration configs (WhatsApp provider, JazzCash, Easypaisa)
**Actions Available:** View provider status badges, test connection (POST)
**4 Providers Seeded:** WhatsApp (Twilio/Meta/Gupshup/360dialog), JazzCash (STUB), Easypaisa (STUB)
**Navigation Entry Points:** Sidebar "Settings" → "Integrations"

---

### G-06 — Notification Settings

**File:** notifications.html
**Route:** /app/settings/notifications
**Purpose:** Per-event notification toggle table (In-App/Email/WhatsApp/SMS channels) and quiet hours config.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.system_config; notifications.send
**API Dependencies:** GET /admin/settings, PATCH /admin/settings
**Data Dependencies:** Tenant notification preferences
**Actions Available:** Toggle per-event per-channel; set quiet hours
**Constraint (SD-004):** EN strings only. Urdu strings blocked by P-017 pending native speaker review.
**Navigation Entry Points:** Sidebar "Settings" → "Notifications"

---

### G-07 — Feature Flags

**File:** feature-flags.html
**Route:** /app/admin/feature-flags
**Purpose:** Feature flag registry with dual-approval toggle for high-risk flags.

**Primary Users:** tenant_owner only
**Required Permissions:** admin.manage_feature_flags
**API Dependencies:** GET /feature-flags, PATCH /feature-flags/:id
**Data Dependencies:** FeatureFlag
**Actions Available:** Toggle flag (requires_dual_approval=true → 2-person approval modal)
**Business Rule:** Flags with requires_dual_approval=true require second approver confirmation
**Navigation Entry Points:** Sidebar "Admin" → "Feature Flags" (tenant_owner only)
**Related Screens:** audit-log.html (J-01) — flag changes are audited

---

### G-08 — Compliance Settings

**File:** compliance.html
**Route:** /app/settings/compliance
**Purpose:** Data retention policy editor, data governance link, break-glass log stub.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.system_config; admin.export_compliance_data
**API Dependencies:** GET /governance/retention, PATCH /governance/retention
**Data Dependencies:** Retention policies
**Actions Available:** Edit retention policy, view governance console link, view break-glass log
**Navigation Entry Points:** Sidebar "Settings" → "Compliance"
**Related Screens:** data-governance.html (J-03), privacy.html (J-05)

---

### G-09 — Territory & Assignment Config

**File:** territories.html
**Route:** /app/admin/territories
**Purpose:** Territory tree table, rule editor (geography/industry/account_size criteria), assignment strategy config.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** territories.read; territories.create; territories.update; territories.assign
**API Dependencies:** GET /territories, POST /territories, PATCH /territories/:id, DELETE /territories/:id
**Data Dependencies:** Territory, TerritoryRule
**Workflows Supported:** WF-004 (Lead Territory Assignment) configuration
**Actions Available:** Create territory, edit rules, configure assignment strategy (round_robin/least_loaded/manual), assign
**Business Rule:** TerritoryRule criteria_type enum: geography/industry/account_size
**Navigation Entry Points:** Sidebar "Admin" → "Territories"

---

## ARCHETYPE H — Reporting / Analytics (7 pages)

Spec: docs/b9-p10-reporting-analytics.md
Shell: date-range filter (flatpickr) → chart grid → drilldown DataTable

---

### H-01 — Sales Analytics

**File:** sales-analytics.html
**Route:** /app/reports/sales
**Purpose:** Win rate, pipeline velocity, rep performance — weighted pipeline KPI, stage bar chart, forecast donut, funnel chart.

**Primary Users:** All CRM roles
**Required Permissions:** analytics.view_basic; analytics.view_advanced (rep-level breakdown)
**API Dependencies:** GET /opportunities, GET /leads, GET /forecasts
**Data Dependencies:** Opportunity, Lead, Forecast
**Actions Available:** Filter by date range, drilldown to opportunity list
**Navigation Entry Points:** Sidebar "Reports" → "Sales"
**Related Screens:** sales-dashboard.html (A-04), sales-cockpit.html (D-01)

---

### H-02 — Marketing Analytics

**File:** marketing-analytics.html
**Route:** /app/reports/marketing
**Purpose:** Channel engagement bar chart, WhatsApp opt-in trend, campaigns DataTable. flatpickr date range.

**Primary Users:** All CRM roles
**Required Permissions:** analytics.view_basic; campaigns.read
**API Dependencies:** GET /campaigns
**Data Dependencies:** Campaign
**Actions Available:** Filter by date range, drilldown to campaign
**Navigation Entry Points:** Sidebar "Reports" → "Marketing"
**Related Screens:** marketing-workspace.html (F-01), engagement-dashboard.html (A-08)

**Pakistan-Market:** WhatsApp opt-in rate is primary chart metric.

---

### H-03 — Support Analytics

**File:** support-analytics.html
**Route:** /app/reports/support
**Purpose:** SLA breach trend line, case volume donut, cases DataTable. flatpickr date range.

**Primary Users:** All CRM roles
**Required Permissions:** analytics.view_basic; cases.read
**API Dependencies:** GET /cases
**Data Dependencies:** Case, CaseEscalation
**Actions Available:** Filter by date range, drilldown to case
**Navigation Entry Points:** Sidebar "Reports" → "Support"
**Related Screens:** support-dashboard.html (A-07), cases.html (B-05)

---

### H-04 — Finance Analytics

**File:** finance-analytics.html
**Route:** /app/reports/finance
**Purpose:** Revenue trends, aging buckets chart, collections efficiency, collections table. JazzCash/Easypaisa hidden (P-016).

**Primary Users:** All CRM roles
**Required Permissions:** analytics.view_basic; collections.view_overdue
**API Dependencies:** GET /invoice-summaries, GET /collections
**Data Dependencies:** Invoice, Collection, Payment
**Actions Available:** Filter by date range, drilldown to invoice
**Navigation Entry Points:** Sidebar "Reports" → "Finance"
**Related Screens:** invoices.html (B-09), collections.html (B-08)

**Pakistan-Market:** PKR amounts, lakh/crore formatting. JazzCash/Easypaisa chart sections hidden (P-016).

---

### H-05 — Workflow Analytics

**File:** workflow-analytics.html
**Route:** /app/reports/workflows
**Purpose:** Pass/fail bar chart, failure rate by workflow, executions DataTable. flatpickr date range.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** analytics.view_basic; workflows.read
**API Dependencies:** GET /workflows/runs
**Data Dependencies:** WorkflowExecution, WorkflowStepRecord
**Actions Available:** Filter by date range, drilldown to run detail
**Navigation Entry Points:** Sidebar "Reports" → "Workflows"
**Related Screens:** workflows-dashboard.html (A-10), workflow-run-detail.html (C-10)

---

### H-06 — Audit Report

**File:** audit-report.html
**Route:** /app/reports/audit
**Purpose:** Stacked allow/deny chart, hash-chain verification panel, privileged access log, signed CSV export.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.read_audit_logs; admin.export_compliance_data
**API Dependencies:** GET /admin/audit-logs
**Data Dependencies:** AuditLog
**Actions Available:** Verify hash chain (row click), export signed CSV
**Navigation Entry Points:** Sidebar "Reports" → "Audit"; audit-dashboard.html (A-13)
**Related Screens:** audit-log.html (J-01), compliance-report.html (J-02)

---

### H-07 — Custom Report Builder

**File:** report-builder.html
**Route:** /app/reports/builder
**Purpose:** 4-step wizard — metric selector / group-by / chart type / save. Live ApexCharts preview.

**Primary Users:** All CRM roles (advanced metrics: analytics.view_advanced)
**Required Permissions:** analytics.view_basic; analytics.view_advanced (advanced metrics); analytics.export
**API Dependencies:** POST /reports/execute (per metric → chart), POST /reports/definitions (save), GET /reports/definitions (load)
**Wired:** Yes (2026-05-31 via v1-reports.routes.js)
**Data Dependencies:** ReportDefinition (custom report entity)
**Actions Available:** Select metrics, group by dimension, choose chart type, live preview, save, load saved reports
**Navigation Entry Points:** Sidebar "Reports" → "Builder"

---

## ARCHETYPE I — Form / Wizard / CPQ (6 pages)

Spec: docs/b9-p11-form-wizard.md
Rule: ≤2 steps enforced; step 1 required fields only; dedup on submit

---

### I-01 — New Lead Form

**File:** lead-new.html
**Route:** /app/leads/new
**Purpose:** 2-step lead capture — step 1: required fields (phone/name/stage/priority/source); step 2: confirm.

**Primary Users:** agent, manager, tenant_admin, tenant_owner
**Required Permissions:** leads.create
**API Dependencies:** POST /leads
**Data Dependencies:** Lead, Contact (auto-linked)
**Workflows Supported:** WF-A step 1 (lead capture); triggers WF-004 (territory assignment)
**Validation:** phone_e164 E.164 format (anti-dedup on phone); stage enum; owner_id required
**Known Issues:** T1 crm-custom.css link missing; T2 stage dropdown stale vocabulary
**Navigation Entry Points:** leads.html (B-02) "New Lead" button; dashboard.html quick-add
**Related Screens:** leads-detail.html (C-01) (redirect on success)

---

### I-02 — New Contact Form

**File:** contact-new.html
**Route:** /app/contacts/new
**Purpose:** 2-step contact creation — step 1: identity (phone/name/source); step 2: account link + tags. Phone dedup warn on blur.

**Primary Users:** agent, manager, tenant_admin, tenant_owner
**Required Permissions:** contacts.create
**API Dependencies:** POST /contacts
**Data Dependencies:** Contact, Account (optional link)
**Validation:** phone_e164 E.164 format; dedup warning on existing phone
**Navigation Entry Points:** contacts.html (B-03) "New Contact" button
**Related Screens:** contacts-detail.html (C-02) (redirect on success)

---

### I-03 — New Opportunity Form

**File:** opportunity-new.html
**Route:** /app/opportunities/new
**Purpose:** 2-step opportunity creation — step 1: name/stage/amount/account; step 2: confirm.

**Primary Users:** agent, manager, tenant_admin, tenant_owner
**Required Permissions:** opportunities.create
**API Dependencies:** POST /opportunities
**Data Dependencies:** Opportunity, Account, Contact
**Workflows Supported:** WF-A step 6 (opportunity creation)
**Validation:** amount NUMERIC PKR; stage enum; owner_id required
**Navigation Entry Points:** sales-cockpit.html (D-01) "New Opportunity"; leads-detail.html (C-01)
**Related Screens:** opportunities-detail.html (C-04) (redirect on success)

---

### I-04 — New Case Form

**File:** case-new.html
**Route:** /app/support/cases/new
**Purpose:** 2-step case creation — step 1: contact live search + subject/priority/source; step 2: queue/category/description.

**Primary Users:** agent, manager, tenant_admin, tenant_owner
**Required Permissions:** cases.create
**API Dependencies:** POST /cases, GET /contacts (live search), GET /support/queues
**Data Dependencies:** Case, Contact, SupportQueue
**Workflows Supported:** WF-C step 1 (case creation); SLA timer set on creation
**Validation:** sla_tier enum; priority enum; queue assignment
**Navigation Entry Points:** cases.html (B-05) "New Case"; support-console.html (E-01)
**Related Screens:** cases-detail.html (C-05) (redirect on success)

---

### I-05 — CPQ Quote Builder

**File:** quote-builder.html
**Route:** /app/sales/quotes/new
**Purpose:** 4-step CPQ wizard — line items / pricing / discount / confirm. Discount >10% auto-routes to approval. Autosave.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** quotes.create; quotes.approve (if approver)
**API Dependencies:** POST /quotes
**Data Dependencies:** Quote, OpportunityLineItem, Order (on acceptance)
**Workflows Supported:** WF-A step 7 (CPQ quote); discount >10% triggers approval routing via rule_engine
**Business Rule:** discount_pct > 10% → requires_approval=true; routes to manager approval
**Validation:** line items required; discount_pct NUMERIC; opportunity_id (optional link)
**Actions Available:** Add line item, set discount, autosave, submit (→ routes to approval if needed)
**Navigation Entry Points:** opportunities-detail.html (C-04) "New Quote"; quotes-dashboard.html (A-05)
**Related Screens:** quotes-detail.html (C-06) (redirect on success); approval-lanes.html (K-04)

**Pakistan-Market:** All amounts in PKR.

---

### I-06 — Journey / Campaign Builder

**File:** campaign-new.html
**Route:** /app/marketing/campaigns/new
**Purpose:** 2-step campaign wizard — step 1: name/segment/type (WhatsApp blast/email/SMS); step 2: template/trigger/schedule.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** campaigns.create; campaigns.activate
**API Dependencies:** POST /campaigns, GET /segments
**Data Dependencies:** Campaign, Segment
**Workflows Supported:** Marketing campaign lifecycle: draft → segment validation → activate → attribute
**Validation:** segment required; template required; trigger type enum
**Actions Available:** Select segment, choose template, set schedule, activate
**Navigation Entry Points:** marketing-workspace.html (F-01) "New Campaign"
**Related Screens:** marketing-workspace.html (F-01) (redirect on success)

**Pakistan-Market:** WhatsApp blast is primary type. P-017 Urdu alert in template preview.

---

## ARCHETYPE J — Audit / Compliance (5 pages)

Spec: docs/b9-p12-audit-compliance.md
Rule: Immutable read-only; hash-chain verified; no delete actions

---

### J-01 — Audit Log

**File:** audit-log.html
**Route:** /app/audit
**Purpose:** Immutable hash-chain audit log — actor/action/entity, allow/deny/warn events, hash verification.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.read_audit_logs
**API Dependencies:** GET /admin/audit-logs
**Data Dependencies:** AuditLog
**Actions Available:** View (read-only); filter by event type, actor, date; verify hash chain
**Navigation Entry Points:** Sidebar "Compliance" → "Audit Log"
**Related Screens:** audit-report.html (H-06), audit-dashboard.html (A-13)

---

### J-02 — Compliance Report

**File:** compliance-report.html
**Route:** /app/compliance
**Purpose:** Compliance KPI report — allow/deny counts, top deny reasons, data retention status.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.export_compliance_data
**API Dependencies:** GET /admin/audit-logs
**Data Dependencies:** AuditLog
**Actions Available:** View KPIs; export compliance data
**Navigation Entry Points:** Sidebar "Compliance" → "Compliance Report"
**Related Screens:** audit-log.html (J-01), data-governance.html (J-03)

---

### J-03 — Data Governance Console

**File:** data-governance.html
**Route:** /app/admin/governance
**Purpose:** 4-tab governance console — Classification / Retention / SAR / Consent. SAR POST creates 30-day SLA.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.system_config
**API Dependencies:** GET /governance/classification, GET /governance/retention, GET /governance/sar, GET /privacy/consent, POST /governance/sar (creates SAR with 30-day SLA)
**Wired:** Yes (2026-05-31 via v1-governance.routes.js)
**Data Dependencies:** Classification policies, RetentionPolicy, SAR records, Consent records
**Tabs:** Classification / Retention / SAR / Consent
**Actions Available:** View/edit classification, edit retention policy, create SAR request, view consent records
**Navigation Entry Points:** Sidebar "Admin" → "Governance"
**Related Screens:** compliance.html (G-08), privacy.html (J-05)

---

### J-04 — RBAC Audit

**File:** rbac-audit.html
**Route:** /app/admin/rbac-audit
**Purpose:** Permission matrix view — user×scope grid, escalation alerts, assignment log.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.read_audit_logs
**API Dependencies:** GET /admin/users (role/scope list)
**Data Dependencies:** User, Role, Permission, AuditLog (rbacAssignmentLog)
**Actions Available:** View permission matrix (read-only); view escalation alerts; view assignment log
**Navigation Entry Points:** Sidebar "Admin" → "RBAC Audit"
**Related Screens:** roles.html (G-03), user-management-crm.html (G-02)

---

### J-05 — Consent & Privacy Manager

**File:** privacy.html
**Route:** /app/settings/privacy
**Purpose:** Consent records from contacts, DSR (Data Subject Request) list, erasure request form.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.system_config; admin.export_compliance_data
**API Dependencies:** GET /privacy/consent, GET /governance/sar, POST /governance/sar (erasure)
**Data Dependencies:** Contact (consent), SAR records
**Actions Available:** View consent records, submit DSR, erasure request (reason required)
**Navigation Entry Points:** Sidebar "Settings" → "Privacy"
**Related Screens:** data-governance.html (J-03), compliance.html (G-08)

---

## ARCHETYPE K — Builder / Visual Canvas (4 pages)

Spec: docs/b9-p07-workflow-visual-ui.md + docs/b9-p08-builder-extensions.md

---

### K-01 — Workflow Builder

**File:** workflow-builder.html
**Route:** /app/workflows/builder
**Purpose:** 3-pane canvas — node palette / visual canvas / inspector. Trigger + step DSL visual editor.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** workflows.create; workflows.update; workflows.publish
**API Dependencies:** GET /workflows, POST /workflows, PATCH /workflows/:id, POST /workflows/:id/publish, POST /workflows/:id/simulate
**Data Dependencies:** WorkflowDefinition, WorkflowStepRecord
**Workflows Supported:** Custom workflow creation; WF-001 to WF-005 are is_system=true (not editable)
**Actions Available:** Add node from palette, configure step in inspector, validate, simulate (dry-run — no side effects), save, publish
**Business Rule:** is_system=true workflows return 403 FORBIDDEN on PATCH
**Navigation Entry Points:** Sidebar "Workflows" → "Builder"
**Related Screens:** workflow-run-detail.html (C-10), workflows-dashboard.html (A-10)

---

### K-02 — Custom Object Layout Builder

**File:** object-builder.html
**Route:** /app/admin/objects
**Purpose:** Object type selector, field list, layout canvas sections, layout preview form.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.system_config
**API Dependencies:** Advisory shell — D-002 pending (no v1-custom-objects.routes.js confirmed in gateway)
**Constraint (SD-009):** D-002 unresolved — gateway route for custom objects not confirmed. Advisory shell only.
**Actions Available:** Select object type, arrange fields in sections, preview layout (visual only — no live API)
**Navigation Entry Points:** Sidebar "Admin" → "Objects"

---

### K-03 — Rule / CPQ Logic Builder

**File:** rule-builder.html
**Route:** /app/admin/rules
**Purpose:** Dynamic condition + action row builder; pre-seeded discount approval routing rule; test rule simulation.

**Primary Users:** tenant_admin, tenant_owner
**Required Permissions:** admin.system_config
**API Dependencies:** Visual canvas — no direct API endpoints confirmed
**Actions Available:** Add condition row, add action row, test simulation
**Business Rule:** Discount >10% routing rule is pre-seeded
**Navigation Entry Points:** Sidebar "Admin" → "Rules"
**Related Screens:** quote-builder.html (I-05)

---

### K-04 — CPQ Approval Lane Board

**File:** approval-lanes.html
**Route:** /app/sales/approval-lanes
**Purpose:** 4-lane kanban (Draft/Pending/Approved/Rejected) for quote approvals — quote cards with line-item totals and discount badges.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** quotes.read; quotes.approve
**API Dependencies:** GET /quotes (status filter)
**Data Dependencies:** Quote
**Workflows Supported:** WF-A step 8 (approval lane board)
**Actions Available:** Move quote card between lanes (approve/reject), view quote detail
**Navigation Entry Points:** Sidebar "Sales" → "Approval Lanes"; quotes-dashboard.html (A-05)
**Related Screens:** quotes-detail.html (C-06)

**Pakistan-Market:** Quote totals in PKR.

---

## ARCHETYPE L — Inbox / Communication (3 pages)

Spec: docs/b9-p13-inbox-communication.md
Rule: RTL mandatory (Urdu messages); thread-first; routing-aware

---

### L-01 — Omnichannel Inbox

**File:** inbox.html
**Route:** /app/inbox
**Purpose:** Channel filter chips (WhatsApp/email/SMS), two-pane thread list and preview, intent badges, auto-select first thread.

**Primary Users:** agent, manager, tenant_admin
**Required Permissions:** inbox.read
**API Dependencies:** GET /inbox/conversations, PATCH /inbox/presence
**Data Dependencies:** Conversation, Message, AgentPresence, InboxQueue
**Workflows Supported:** WF-D steps 4–8 (intent detection through resolution)
**Actions Available:** Filter by channel, select thread, view presence status
**Filter Chips:** channel (whatsapp/email/sms), state (open/resolved/closed)
**Navigation Entry Points:** Sidebar "Inbox"
**Related Screens:** inbox-thread.html (L-02), routing-config.html (L-03)

**Pakistan-Market:** WhatsApp is primary channel. RTL mandatory for Urdu message content.

---

### L-02 — Conversation Thread

**File:** inbox-thread.html
**Route:** /app/inbox/:thread_id
**Purpose:** WhatsApp-style message bubbles, customer context strip, intent classification panel, suggested CTAs.

**Primary Users:** agent, manager, tenant_admin
**Required Permissions:** inbox.read; inbox.claim (claim conversation); inbox.handoff (transfer)
**API Dependencies:** GET /inbox/conversations/:id, POST /inbox/conversations/:id/claim, POST /inbox/conversations/:id/messages, POST /inbox/conversations/:id/handoff
**Data Dependencies:** Conversation, Message, Handoff, Contact
**Workflows Supported:** WF-D steps 5–8 (claim, respond, handoff, resolve)
**Actions Available:** Claim conversation, send message, handoff to agent (inbox.handoff), resolve
**Agent Capacity Rule:** Claim fails if open_conversation_count >= max_concurrent (10)
**Constraint (SD-006):** Voice note transcription disabled (MR-003 pending)
**Navigation Entry Points:** inbox.html (L-01) thread selection
**Related Screens:** contacts-detail.html (C-02), inbox.html (L-01)

**Pakistan-Market:** WhatsApp bubble layout RTL. Intent badges in English (P-017 for Urdu pending).

---

### L-03 — Routing Configuration

**File:** routing-config.html
**Route:** /app/admin/routing
**Purpose:** Settings two-pane — queue management table, agent capacity table, routing rules priority list, fallback config.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** inbox.supervise; inbox.admin
**API Dependencies:** GET /inbox/queues, POST /inbox/queues, PATCH /inbox/queues/:id, GET /inbox/presence
**Data Dependencies:** InboxQueue, AgentPresence, Handoff
**Workflows Supported:** WF-D step 2 (auto-routing configuration)
**Actions Available:** Create queue, edit routing strategy (round_robin/least_loaded/claim_first/skill_based), set fallback, set agent capacity
**Navigation Entry Points:** Sidebar "Admin" → "Routing"
**Related Screens:** inbox.html (L-01), identity-dashboard.html (A-12)

---

## ARCHETYPE M — AI / Copilot (2 pages)

Spec: docs/b9-p14-ai-copilot.md
Rule: Advisory-only; evidence-anchored suggestions only; no ungrounded inference

---

### M-01 — AI Copilot Panel

**File:** ai-copilot.html
**Route:** /app/ai/copilot
**Purpose:** Advisory panel — lead score card, next-action suggestion, risk flags, conversational CRM chat (intent classifier).

**Primary Users:** All CRM roles
**Required Permissions:** ai.view_scores; ai.score_leads (force recompute)
**API Dependencies:** GET /ai/copilot/suggestions, GET /ai/scores/leads, POST /ai/scores/leads/:id/recompute, GET /ai/copilot/chat
**Data Dependencies:** LeadScore, CopilotSuggestion
**Constraint (SD-003):** Rule-based advisory only. No LLM inference. AI provider deferred to C7.
**Actions Available:** View lead score, view suggestions, dismiss/action suggestion, send chat query (intent: payment_query/follow_up_response/lead_inquiry/support_request)
**Advisory-Only Invariant:** All suggestions reference observed data (no speculation)
**Navigation Entry Points:** Sidebar "AI" → "Copilot"
**Related Screens:** ai-insights.html (M-02), leads-detail.html (C-01)

---

### M-02 — AI Insights Dashboard

**File:** ai-insights.html
**Route:** /app/ai/insights
**Purpose:** Win probability distribution, churn risk donut, CLV estimates bar chart, feature weight inspector.

**Primary Users:** manager, tenant_admin, tenant_owner
**Required Permissions:** ai.view_scores; ai.view_forecasts; ai.generate_forecasts
**API Dependencies:** GET /ai/scores/leads, GET /ai/predictions/churn, GET /ai/estimates/clv, GET /ai/models
**Data Dependencies:** LeadScore, ChurnPrediction, CLVEstimate, ScoringModel
**Constraint (SD-003):** Rule-based scoring only. No ML/LLM. All models: rule_based algorithm.
**Actions Available:** View score distributions; view feature weights; view model registry
**Models:** lead_score_v1, churn_predict_v1, clv_estimate_v1 (all rule_based)
**Navigation Entry Points:** Sidebar "AI" → "Insights"
**Related Screens:** ai-copilot.html (M-01), sales-dashboard.html (A-04)

**Pakistan-Market:** CLV estimated in PKR, 24-month horizon.

---

*End FRONTEND_SCREEN_CATALOG.md*
*75 custom pages fully documented*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
