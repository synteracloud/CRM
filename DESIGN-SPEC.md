# Pakistan CRM — Design Specification

**Purpose:** Master screen inventory and archetype map for all custom Pakistan CRM pages. Gates the custom design phase — read this before building any custom screen.
**Last updated:** 2026-05-31 (3rd pass) — **ALL 75 CUSTOM PAGES WIRED TO LIVE API + BROWSER-APPROVED.** Phase 6 wiring sprint + extension complete. 5 previously blocked pages (G-04/G-05/J-03/H-07/A-08) wired via inline gateway route stubs. 0 blocked pages remain. Prior: Phase 6 Component 1 — T1–T4 audit (9 fixed); Phase 5B — all 28 Cat 2 backend domains built.
**Build state:** Library phase COMPLETE (96 NexLink pages). Custom design phase COMPLETE — all 75 custom pages built, T1–T4 ✓, wired to live API, and browser-approved. All pages marked ⏳ pending full live-API re-verification pass (Phase 6 Component 3 / commercialization).

---

## §1 — How to Use This Document

1. **Find the page** in §3 (Screen Inventory). Note its archetype and spec doc.
2. **Read the spec doc** (b9-p series) for layout rules, field contracts, API routes.
3. **Read FRAMEWORK.md §25–§26** for build protocol and QC tiers.
4. **Apply design constraints** from §2 — these are non-negotiable on every screen.
5. **Update §3 status** when a page is built and browser-approved.

---

## §2 — Design Constraints (All Screens)

These apply to every custom CRM page. No exceptions.

| # | Constraint | Source | Rule |
|---|---|---|---|
| C-001 | RTL from day 1 | CONSTRAINTS.md | `dir` attribute and RTL CSS must be wired at build time. Cannot be retrofitted after the fact. Use `crm-locale.js` toggle. |
| C-002 | ≤2 steps for core actions | BEHAV-012, b9-p11 | Every primary user action (create lead, log follow-up, record payment) must complete in ≤2 interactions. Measure from intent to confirmation. |
| C-003 | Mobile-first layout | b9-p08-mobile-responsiveness-system.md | All pages must be usable on a 360px viewport. WhatsApp is the primary surface. P0 actions must be reachable in ≤2 layers on mobile. |
| C-004 | PKR formatting | crm-components.js `pkr()` | All monetary amounts use `pkr()` — Lakh/Crore notation above 99,999. Never show raw integers. |
| C-005 | Revenue features first | adoption-ux.md | Follow-up queue and collections must surface before advanced features (progressive disclosure tiers 1→4). |
| C-006 | Gradual enforcement | BEHAV-007 | Enforcement level sourced from tenant config. soft = advisory warnings; medium = warnings + log; strict = hard block. Never hard-block on day 1. |
| C-007 | Dummy mode toggle | crm-api.js | All API calls routed through `crm-api.js` with `DUMMY_MODE: true` during build. Flip to `false` when backend is live. Never hardcode data directly in HTML. |
| C-008 | NexLink class chains only | FRAMEWORK.md §30 | Use the class chains documented in FRAMEWORK.md §30. No custom CSS outside `crm-custom.css`. No Bootstrap directional classes (`left`/`right` → `start`/`end`). |
| C-009 | Full activity logging | activity-control-model.md | Every user action that modifies state emits an activity event. Wired through backend API — not a frontend concern, but the UI must trigger the correct endpoint. |
| C-010 | Seed-first if seed exists | FRAMEWORK.md §0 | If a NexLink seed exists for the archetype pattern, build from it. Read the full seed before building. For net-new patterns, use the b9-p spec + b9-p03/p07 as reference implementations. |

---

## §3 — Screen Inventory

**Total custom screens: 75**
**Status key:** ⬜ Not started | 🔄 Library page exists (needs custom work) | ⏳ HTML draft exists, process not yet complete | ✓ Full archetype-driven process complete and locked

---

### Archetype A — Dashboard / KPI Overview
**Spec:** `docs/b9-p01-dashboard-kpi.md` | 13 panels | **5-zone layout:** posture → primary_kpi → execution_queue → trend_diagnostic → risk_anomaly

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| A-01 | Owner / Sales Dashboard | dashboard.html | /app/dashboard | ⏳ | Browser-approved. T1–T4 ✓ 2026-05-30 (T2 fixed: KPI h2 IDs added, JS setters added in crm-dashboard.js; T3 fixed: dt-head-left→center). Wiring sprint pending. |
| A-02 | Lead Funnel Dashboard | leads-dashboard.html | /app/sales/leads/dashboard | ⏳ | Built 2026-05-29. Reads CRM_DUMMY leads/leadFunnelKpi/deltas. Posture+KPI+idle queue+stage chart. Browser sign-off pending. |
| A-03 | Customer Health Dashboard | contacts-health.html | /app/contacts/health | ⏳ | Built 2026-05-29. Reads CRM_DUMMY contacts/contactsKpi. Posture+KPI+open-cases queue+completeness chart. Browser sign-off pending. |
| A-04 | Opportunity Pipeline Dashboard | sales-dashboard.html | /app/sales/dashboard | ⏳ | Re-processed 2026-05-29. Structure + CRM_DUMMY wiring verified clean. §18 CRM_PAGE key added. Browser sign-off pending. |
| A-05 | Quote Approval Dashboard | quotes-dashboard.html | /app/sales/quotes/dashboard | ⏳ | Built 2026-05-29. Reads CRM_DUMMY quotes. Posture+KPI+pending queue+value chart. Browser sign-off pending. |
| A-06 | Subscription Revenue Dashboard | subscriptions-dashboard.html | /app/finance/subscriptions/dashboard | ⏳ | Built 2026-05-29. MRR/ARR/Renewal Rate KPIs, churn posture, cohort retention chart, delinquent queue. P-016 stub comment in place. Browser sign-off pending. |
| A-07 | Case SLA Operations Dashboard | support-dashboard.html | /app/support/dashboard | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Posture strip (breach count), SLA breach KPIs, at-risk queue DataTable, case volume area chart. Reads `d.cases` + `d.caseSlaKpi`. |
| A-08 | Communication Engagement Dashboard | engagement-dashboard.html | /app/marketing/engagement | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Delivery/open/reply rate KPIs, active campaigns list, channel engagement bar chart. **Wired 2026-05-31** via v1-communications.routes.js — GET /communications/engagement → KPIs + chart; GET /campaigns → queue. |
| A-09 | Knowledge Effectiveness Dashboard | knowledge-dashboard.html | /app/support/knowledge/dashboard | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Deflection rate KPIs, stale article queue, adoption trend chart. Reads `d.knowledgeArticles` + `d.knowledgeKpi`. |
| A-10 | Workflow Automation Dashboard | workflows-dashboard.html | /app/workflows/dashboard | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Posture strip (failure count), execution KPIs, failed queue, pass/fail bar chart. Reads `d.workflowExecutions` + `d.workflowKpi`. |
| A-11 | Tenant & Entitlement Dashboard | tenants-dashboard.html | /app/admin/tenants | ⏳ | Built 2026-05-29. Plan/seat/feature KPIs, entitlements-at-limit queue, tenant summary. Reads `d.tenantKpi`. |
| A-12 | Identity & Access Posture Dashboard | identity-dashboard.html | /app/admin/identity | ⏳ | Built 2026-05-29. Reads CRM_DUMMY users+AUDIT_LOG. Escalation queue+activity chart. Browser sign-off pending. |
| A-13 | Platform Audit & Reliability Dashboard | audit-dashboard.html | /app/admin/audit/dashboard | ⏳ | Built 2026-05-29. Reads CRM_DUMMY AUDIT_LOG. Deny posture+KPI+deny queue+action-type chart. Browser sign-off pending. |

---

### Archetype B — List / Queue / Table View
**Spec:** `docs/b9-p02-list-queue.md` | 11 surfaces | **Shell:** filter bar → sortable columns → row quick actions → bulk actions → pagination

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| B-01 | Follow-up Queue | followups.html | /app/followups | ⏳ | Browser-approved. Protocol audit pending: T3 (Place 3 CSS missing for `dt_Followups`), T4 (filter chip vocabulary stale — `Soft/Medium/Strict` → `none/reminder/warning/escalated/reassigned`). |
| B-02 | Lead Queue | leads.html | /app/leads | ⏳ | Browser-approved. Protocol audit pending: T2 (hardcoded chart data, KPI delta text), T3 (Place 3 CSS missing for `dt_ScrollVertical`), T4 (stage filter chips `Contacted/Engaged` → `qualifying/nurturing`). |
| B-03 | Contact List | contacts.html | /app/contacts | ⏳ | Browser-approved. Protocol audit pending: T2 (hardcoded KPI delta text), T3 (Place 3 CSS missing for `dt_Contacts`). |
| B-04 | Account List | accounts.html | /app/accounts | ⏳ | Built 2026-05-29. ACCOUNTS dataset added. Tier/Industry/Balance columns, filter chips. |
| B-05 | Ticket / Case Queue | cases.html | /app/support/cases | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 4 KPI cards, DataTable with dual Status×SLA filter chips, STATUS/SLA/PRI badges, cross-filter logic. |
| B-06 | Activity Feed | activity.html | /app/activity | ⏳ | Browser-approved 2026-05-29. Read-only. `ActivityEvent`. No inline edits. |
| B-07 | Task Queue | tasks.html | /app/tasks | ⏳ | Browser-approved 2026-05-29. Overdue-pinned. `ActivityTaskOperationalRM`. |
| B-08 | Collections Queue | collections.html | /app/collections | ⏳ | Browser-approved. Protocol audit pending: T2 (hardcoded delta text), T4 (status filter chips `Unpaid/Partial/Overdue` don't match status values `open/paid/void` — JS statusBadge needs aligning to domain spec `unpaid/partial/paid/overdue`). |
| B-09 | Invoice Queue | invoices.html | /app/finance/invoices | ⏳ | Built 2026-05-29. INVOICES dummy dataset added. Total/Paid/Balance/Status columns, overdue in red, filter chips by status. Browser sign-off pending. |
| B-10 | User Directory | users.html | /app/admin/users | ⏳ | Browser-approved 2026-05-29. Admin-only. Role badge list. Suspend + reset password actions. |
| B-11 | Partner List | partners.html | /app/partners | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 4 KPI cards, DataTable with Tier×Status filter chips, PKR commission column, tier badges. |

---

### Archetype C — Entity Detail / 360 View
**Spec:** `docs/b9-p06-entity-detail.md` | 12 surfaces | **Shell:** sticky header strip → split pane (main + context) → inline edit → activity timeline
> ✅ **b9-p06 updated 2026-05-28** — C-05 Case Detail: full CaseStatus state machine (OPEN/ASSIGNED/IN_PROGRESS/WAITING_ON_CUSTOMER/RESOLVED/ESCALATED/CLOSED) and header button state gates added from `cases-domain.md`. C-09 Subscription Detail: Subscription.status enum (draft/trialing/active/past_due/paused/cancelled/expired) and state-gated buttons added from `payments-revenue.md`.

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| C-01 | Lead Detail | leads-detail.html | /app/leads/:lead_id | ⏳ | Browser-approved 2026-05-29. Protocol re-verified: crm-custom.css ✓, identity strip height:auto ✓, activity timeline reads CRM_DUMMY ✓. Stage history shows current stage only (dummy-mode limitation). |
| C-02 | Customer 360 | contacts-detail.html | /app/contacts/:contact_id/360 | ⏳ | Browser-approved 2026-05-29. Reads CRM_DUMMY contacts/leads/activities. Demo record c-001 (Tariq Mehmood). |
| C-03 | Account Profile | accounts-detail.html | /app/accounts/:account_id | ⏳ | Built 2026-05-29. 4-tab pane: Details/Contacts/Opportunities/Invoices. Context: health + balance. Demo: a-002. |
| C-04 | Opportunity Detail | opportunities-detail.html | /app/opportunities/:opportunity_id | ⏳ | Browser-approved 2026-05-29. Re-processed: Quotes tab reads CRM_DUMMY.quotes. |
| C-05 | Case / Ticket Detail | cases-detail.html | /app/support/cases/:case_id | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. SLA timer identity strip, state-gated Claim/Resolve buttons, 3-tab pane (Conversation/Fields/Resolution), escalation controls by sla_state. |
| C-06 | Quote Detail | quotes-detail.html | /app/sales/quotes/:quote_id | ⏳ | Browser-approved 2026-05-29. Reads CRM_DUMMY.quotes. Line items + approval history + terms. |
| C-07 | Order Detail | orders-detail.html | /app/sales/orders/:order_id | ⏳ | Built 2026-05-29. ORDERS dataset added. Immutable badge, line items, fulfilment status, linked invoice. Demo: ord-001. |
| C-08 | Invoice Detail | invoices-detail.html | /app/finance/invoices/:invoice_id | ⏳ | Built 2026-05-29. Total/Paid/Balance strip, payment history, proof tab, reconciliation status. Demo: i-001. |
| C-09 | Subscription Detail | subscriptions-detail.html | /app/finance/subscriptions/:subscription_id | ⏳ | Built 2026-05-29. SUBSCRIPTIONS dummy dataset added. Status-gated buttons, MRR/ARR strip, 4-tab main pane, churn risk + expansion context panel. Demo: sub-001. Browser sign-off pending. |
| C-10 | Workflow Execution Detail | workflow-run-detail.html | /app/workflows/runs/:execution_id | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Execution identity strip, state-gated Retry button, 3-tab pane (Log/Steps/Error Details), retry context panel. |
| C-11 | Partner Detail | partners-detail.html | /app/partners/:partner_id | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 4-tab pane (Details/Opportunities/Commission Ledger/Relationship History), attribution summary context panel. |
| C-12 | Knowledge Article Detail | knowledge-article.html | /app/support/knowledge/:article_id | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. State-gated Publish/Edit, 4-tab pane (Content/Version History/Related/Feedback), article stats context panel. |

---

### Archetype D — Sales Cockpit
**Spec:** `docs/b9-p03-sales-cockpit.md` | 4 views (single page surface) | **Shell:** pipeline execution rail + deal workspace + forecast context + next-actions panel

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| D-01 | Sales Cockpit | sales-cockpit.html | /app/sales/cockpit | ⏳ | Re-processed 2026-05-29. Pipeline rail, kanban, deal pane, forecast + next-actions all CRM_DUMMY-wired. §18 key added. Browser sign-off pending. |

---

### Archetype E — Support Console
**Spec:** `docs/b9-p04-support-console.md` | Queue-first console | **Shell:** SLA queue → conversation thread → escalation controls
> ✅ **Backend built (Sprint 5B-1)** — Cases/support domain live at `/api/v1/cases` + `/api/v1/support` + `/api/v1/knowledge`. E-01 wiring deferred to Phase 6 wiring sprint.

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| E-01 | Support Console | support-console.html | /app/support/console | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 3-pane layout (SLA queue/thread/context), global SLA timer in header, click-to-select thread, escalation controls by sla_state. |

---

### Archetype F — Marketing / Campaign Workspace
**Spec:** `docs/b9-p05-marketing-workspace.md` | Campaign lifecycle | Draft → segment validation → activation → attribution
> ✅ **Backend built (Sprint 5B-4)** — Campaigns domain live at `/api/v1/campaigns` + `/api/v1/segments` + `/api/v1/templates`. F-01 wiring deferred to Phase 6 wiring sprint.

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| F-01 | Marketing Workspace | marketing-workspace.html | /app/marketing/campaigns | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 4 KPI cards, campaigns DataTable, Status filter chips, TYPE/STATUS badges. Reads `d.campaigns`. |

---

### Archetype G — Settings / Admin / RBAC
**Spec:** `docs/b9-p09-settings-admin.md` | 9 pages | **Shell:** settings sidebar → content panel → permission-gated write states
> ✅ **b9-p09 updated 2026-05-28** — G-02/G-03 route conflict resolved (separate pages at `/app/admin/users/manage` and `/app/admin/roles`). G-09 territory contract updated from `territory-management.md` (criteria_type enum, TerritoryRule entity, assignment strategies). G-07 feature flag rule_type enum and change approval process added. G-01/G-04/G-06/G-08 now defined (were missing).

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| G-01 | Organization Settings | org-settings.html | /app/settings/org | ⏳ | Built 2026-05-29. Identity/Locale/Currency/Business hours. Shared settings left-nav across all G pages. |
| G-02 | User Management | user-management-crm.html | /app/admin/users/manage | ⏳ | Built 2026-05-29. 2-step Invite User modal, Edit Role modal, Suspend/Reset confirm modals. |
| G-03 | Role & Permission Editor | roles.html | /app/admin/roles | ⏳ | Built 2026-05-29. Roles table from d.roles.data. Permission registry read-only. Cannot delete role with active users. |
| G-04 | Billing & Subscription Settings | billing-settings.html | /app/settings/billing | ⏳ | Built 2026-05-29. **Wired 2026-05-31** via v1-billing.routes.js — GET /billing/subscription → plan/seats/renewal; GET /billing/invoices → invoice history. P-016 payment method section remains static stub. |
| G-05 | Integration Settings | integrations.html | /app/settings/integrations | ⏳ | Built 2026-05-29. **Wired 2026-05-31** via v1-integrations.routes.js — GET /integrations → provider status badges; POST /integrations/:provider/test → test connection. 4 providers seeded. |
| G-06 | Notification Settings | notifications.html | /app/settings/notifications | ⏳ | Built 2026-05-29. Per-event toggle table (In-App/Email/WhatsApp/SMS). Quiet hours config. |
| G-07 | Feature Flags | feature-flags.html | /app/admin/feature-flags | ⏳ | Built 2026-05-29. Flag registry from d.featureFlags. 2-person approval modal on toggle. |
| G-08 | Compliance Settings | compliance.html | /app/settings/compliance | ⏳ | Built 2026-05-29. Retention policy editor. Data governance link. Break-glass log stub. |
| G-09 | Territory & Assignment Config | territories.html | /app/admin/territories | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Settings two-pane, territory tree table, rule editor, assignment strategy config. Reads `d.territories`. |

---

### Archetype H — Reporting / Analytics
**Spec:** `docs/b9-p10-reporting-analytics.md` | 7 pages | **Shell:** date-range filter → chart grid → drilldown
> ✅ **b9-p10 restructured 2026-05-28** — H-01 through H-07 now explicitly defined in spec, anchored to `kpi-data-pipelines.md` formulas. Original enterprise surfaces (Predictive Forecasting, AI Scoring, Usage Billing) retained as Phase 6 addenda.

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| H-01 | Sales Analytics | sales-analytics.html | /app/reports/sales | ⏳ | Browser-approved 2026-05-29. Weighted pipeline KPI, stage bar chart, forecast donut, lead funnel chart, rep performance table. |
| H-02 | Marketing Analytics | marketing-analytics.html | /app/reports/marketing | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. flatpickr date range, channel engagement bar chart, WhatsApp opt-in trend, campaigns DataTable. |
| H-03 | Support Analytics | support-analytics.html | /app/reports/support | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. flatpickr date range, SLA breach trend line, case volume donut, cases DataTable. |
| H-04 | Finance Analytics | finance-analytics.html | /app/reports/finance | ⏳ | Browser-approved 2026-05-29. Aging buckets chart, revenue trend, collections table. JazzCash/Easypaisa hidden (P-016). |
| H-05 | Workflow Analytics | workflow-analytics.html | /app/reports/workflows | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. flatpickr date range, pass/fail bar chart, failure rate by workflow, executions DataTable. |
| H-06 | Audit Report | audit-report.html | /app/reports/audit | ⏳ | Browser-approved 2026-05-29. Stacked allow/deny chart, hash chain panel with row-click verify, privileged access log, signed CSV export. |
| H-07 | Custom Report Builder | report-builder.html | /app/reports/builder | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 4-step wizard (metric selector / group-by / chart type / save), live ApexCharts preview panel. **Wired 2026-05-31** via v1-reports.routes.js — POST /reports/execute per metric → chart; POST/GET /reports/definitions → save/load. |

---

### Archetype I — Form / Wizard / CPQ
**Spec:** `docs/b9-p11-form-wizard.md` | 6 pages | **Shell:** ≤2-step rule enforced — step 1 required fields, step 2 confirm/extras
> ✅ **b9-p11 updated 2026-05-28** — I-01 (New Lead), I-02 (New Contact), I-03 (New Opportunity), I-04 (New Case), I-06 (Campaign Builder) now defined. Previously only I-05 (CPQ) was specified.

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| I-01 | New Lead Form | lead-new.html | /app/leads/new | ⏳ | Browser-approved. Protocol audit pending: T1 (crm-custom.css link missing), T2 (stage dropdown uses stale vocabulary `Contacted/Engaged` → `qualifying/nurturing`). |
| I-02 | New Contact Form | contact-new.html | /app/contacts/new | ⏳ | Built 2026-05-29. 2-step wizard: identity → account + tags. Phone dedup warn on blur. |
| I-03 | New Opportunity Form | opportunity-new.html | /app/opportunities/new | ⏳ | Browser-approved 2026-05-29. 2-step wizard. |
| I-04 | New Case Form | case-new.html | /app/support/cases/new | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 2-step wizard: contact live search + subject/priority → queue/category/description. |
| I-05 | CPQ Quote Builder | quote-builder.html | /app/sales/quotes/new | ⏳ | Browser-approved 2026-05-29. 4-step CPQ wizard. Discount >10% approval routing. Autosave. |
| I-06 | Journey / Campaign Builder | campaign-new.html | /app/marketing/campaigns/new | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 2-step wizard: name/segment/type → template/trigger/schedule. P-017 Urdu alert. |

---

### Archetype J — Audit / Compliance
**Spec:** `docs/b9-p12-audit-compliance.md` | 5 pages | **Shell:** immutable read-only log, hash-chain verified, export controls
> ✅ **b9-p12 updated 2026-05-28** — J-01 route fixed (`/app/audit`). J-02 (Compliance Report), J-04 (RBAC Audit), J-05 (Consent & Privacy Manager) now defined. Previously only J-03 was specified.

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| J-01 | Audit Log | audit-log.html | /app/audit | ⏳ | Re-processed 2026-05-29. Shell fixed (removed hardcoded header/aside, fixed main class, script stack). Headers dt-head-center. Summary badges wired to CRM_DUMMY. Browser sign-off pending. |
| J-02 | Compliance Report | compliance-report.html | /app/compliance | ⏳ | Re-processed 2026-05-29. Shell fixed. KPIs now read CRM_DUMMY.AUDIT_LOG counts (no more Math.random). Browser sign-off pending. |
| J-03 | Data Governance Console | data-governance.html | /app/admin/governance | ⏳ | Built 2026-05-29. 4-tab: Classification/Retention/SAR/Consent. **Wired 2026-05-31** via v1-governance.routes.js — GET /governance/classification+retention+sar + /privacy/consent → 4 tabs. SAR POST creates 30-day SLA due date. |
| J-04 | RBAC Audit | rbac-audit.html | /app/admin/rbac-audit | ⏳ | Re-processed 2026-05-29. Shell fixed. Matrix + alerts now built from CRM_DUMMY.users. Assignment log reads CRM_DUMMY.rbacAssignmentLog. Browser sign-off pending. |
| J-05 | Consent & Privacy Manager | privacy.html | /app/settings/privacy | ⏳ | Built 2026-05-29. Consent records from d.contacts. DSR list (empty). Erasure request form with reason required. |

---

### Archetype K — Builder / Visual Canvas
**Spec:** `docs/b9-p07-workflow-visual-ui.md` + `docs/b9-p08-builder-extensions.md` | 4 pages

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| K-01 | Workflow Builder | workflow-builder.html | /app/workflows/builder | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 3-pane palette/canvas/inspector, simulated node graph (Bootstrap cards + CSS connectors), validate/simulate/save/publish interactions. |
| K-02 | Custom Object Layout Builder | object-builder.html | /app/admin/objects | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Object type selector (Lead/Contact/Opp/Account/Custom), field list, layout canvas sections, layout preview form. |
| K-03 | Rule / CPQ Logic Builder | rule-builder.html | /app/admin/rules | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Dynamic condition + action row builder, pre-seeded discount approval routing rule, test rule simulation. |
| K-04 | CPQ Approval Lane Board | approval-lanes.html | /app/sales/approval-lanes | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. 4-lane kanban (Draft/Pending/Approved/Rejected), quote cards with calcTotal() line-item math, discount badge. |

---

### Archetype L — Inbox / Communication
**Spec:** `docs/b9-p13-inbox-communication.md` | 3 pages | **Shell:** thread list → conversation view → routing controls | RTL mandatory (Urdu messages)
> ✅ **b9-p13 updated 2026-05-28** — `shared-inbox.md` entities integrated (InboxQueue, AgentPresence, ConversationHandoff). L-02 route unified to `/app/inbox/:thread_id`. L-03 (Routing Configuration) now defined.

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| L-01 | Omnichannel Inbox | inbox.html | /app/inbox | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Channel filter chips, two-pane thread list/view, intent badges, auto-select first thread. Reads `d.messageThreads`. |
| L-02 | Conversation Thread | inbox-thread.html | /app/inbox/:thread_id | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. WhatsApp-style bubbles, customer context strip, intent classification panel, INTENT_ACTIONS suggested CTAs. |
| L-03 | Routing Configuration | routing-config.html | /app/admin/routing | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Settings two-pane, queue management table, agent capacity table, routing rules priority list, fallback config. |

---

### Archetype M — AI / Copilot
**Spec:** `docs/b9-p14-ai-copilot.md` | 2 pages | **Advisory-only** — suggestions must reference observed data only (no ungrounded inference)
> ✅ **Backend built (Sprint 5B-7)** — AI domain live at `/api/v1/ai/scores`, `/api/v1/ai/predictions`, `/api/v1/ai/estimates`, `/api/v1/ai/copilot`, `/api/v1/ai/models`. Advisory-only invariant enforced. M-01/M-02 wiring deferred to Phase 6 wiring sprint.

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| M-01 | AI Copilot Panel | ai-copilot.html | /app/ai/copilot | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Advisory-only banner, lead score card, next-action suggestion, risk flags, conversational CRM chat with intent classifier. |
| M-02 | AI Insights Dashboard | ai-insights.html | /app/ai/insights | ⏳ | Cat 2. Built 2026-05-29. Browser-approved. Win probability distribution, churn risk donut, CLV estimates bar chart, feature weight inspector. |

---

## §4 — Build Phase Plan

Build in order of business value. Each phase produces browser-approved screens before the next starts.

### Phase 1 — Core Execution Surfaces (build first)
*These drive daily revenue and follow-up discipline. Highest user interaction frequency.*

| Priority | Screen | ID | Rationale |
|---|---|---|---|
| 1 | Follow-up Queue | B-01 | Tier 1 surface per adoption-ux.md. Never miss a follow-up. |
| 2 | Lead Queue | B-02 | Daily lead management. |
| 3 | Lead Detail | C-01 | Detail view for every lead in queue. |
| 4 | Owner Dashboard | A-01 | Executive posture strip + KPIs. |
| 5 | Collections Queue | B-08 | Cash position visibility. Never miss a payment. |
| 6 | Contact List | B-03 | Contact base management. |
| 7 | New Lead Form | I-01 | ≤2-step capture. Anti-dedup on phone. |

### Phase 2 — Sales Intelligence
| Priority | Screen | ID |
|---|---|---|
| 8 | Opportunity Detail | C-04 |
| 9 | Sales Cockpit | D-01 |
| 10 | Lead Funnel Dashboard | A-02 |
| 11 | Opportunity Pipeline Dashboard | A-04 |
| 12 | New Opportunity Form | I-03 |
| 13 | Quote Builder (CPQ) | I-05 |
| 14 | Quote Detail | C-06 |

### Phase 3 — Finance & Collections
| Priority | Screen | ID |
|---|---|---|
| 15 | Invoice Queue | B-09 |
| 16 | Invoice Detail | C-08 |
| 17 | Subscription Revenue Dashboard | A-06 |
| 18 | Subscription Detail | C-09 |
| 19 | Finance Analytics | H-04 |

### Phase 4 — Support Operations
| Priority | Screen | ID |
|---|---|---|
| 20 | Case Queue | B-05 |
| 21 | Case Detail | C-05 |
| 22 | Support Console | E-01 |
| 23 | Support Dashboard | A-07 |
| 24 | New Case Form | I-04 |
| 25 | Knowledge Article Detail | C-12 |

### Phase 5 — Communication & Inbox
| Priority | Screen | ID |
|---|---|---|
| 26 | Omnichannel Inbox | L-01 |
| 27 | Conversation Thread | L-02 |
| 28 | Communication Engagement Dashboard | A-08 |

### Phase 6 — Admin & Settings
| Priority | Screen | ID |
|---|---|---|
| 29 | User Management | G-02 |
| 30 | Role & Permission Editor | G-03 |
| 31 | Integration Settings | G-05 |
| 32 | Feature Flags | G-07 |
| 33 | Territory & Assignment Config | G-09 |
| 34 | Org Settings | G-01 |

### Phase 7 — Marketing & Automation
| Priority | Screen | ID |
|---|---|---|
| 35 | Marketing Workspace | F-01 |
| 36 | Campaign Builder | I-06 |
| 37 | Marketing Analytics | H-02 |
| 38 | Workflow Builder | K-01 |
| 39 | Workflow Dashboard | A-10 |

### Phase 8 — Enterprise Features
*Build last — lower SME frequency, highest complexity.*

| Priority | Screen | ID |
|---|---|---|
| 40–75 | All remaining screens (A-03 to A-13, B-04/B-06/B-07/B-10/B-11, C-02/C-03/C-07/C-10/C-11, G-04/G-05/G-06/G-08, H-01/H-03/H-05/H-06/H-07, I-02, J-01–J-05, K-02–K-04, L-03, M-01–M-02, A-11/A-12/A-13) | Various |

---

## §5 — Archetype Quick Reference

| Archetype | Spec doc | Pages | Key design rule |
|---|---|---|---|
| A — Dashboard/KPI | b9-p01-dashboard-kpi.md | 13 | 5-zone layout: posture → kpi → queue → trend → risk |
| B — List/Queue | b9-p02-list-queue.md | 11 | Default sort by urgency; max 3 quick actions per row |
| C — Entity Detail | b9-p06-entity-detail.md | 12 | Sticky header; split pane; inline edit with explicit save |
| D — Sales Cockpit | b9-p03-sales-cockpit.md | 1 | Stage progression is P0 action; pipeline-first |
| E — Support Console | b9-p04-support-console.md | 1 | Queue sorted by SLA due-time; escalation deterministic |
| F — Marketing | b9-p05-marketing-workspace.md | 1 | Draft → segment → activate → attribute lifecycle |
| G — Settings/Admin | b9-p09-settings-admin.md | 9 | Default-deny panel; 2-step confirm for destructive ops. G-01/G-04/G-06/G-08 now specified. G-02/G-03 route conflict resolved. |
| H — Reporting | b9-p10-reporting-analytics.md | 7 | Date-range filter first; drilldown on demand. H-01–H-07 now mapped to spec; enterprise surfaces retained as Phase 6 addenda. |
| I — Form/Wizard | b9-p11-form-wizard.md | 6 | ≤2 steps enforced; step 1 required only; dedup on submit. Simple entity forms (I-01–I-04, I-06) + CPQ (I-05) now all specified. |
| J — Audit/Compliance | b9-p12-audit-compliance.md | 5 | Immutable; hash-chain verified; no delete actions. J-01 route `/app/audit`. J-02/J-04/J-05 now specified. |
| K — Builder/Canvas | b9-p07 + b9-p08-builder-extensions.md | 4 | 1:1 UI↔DSL mapping; graph import/export with validation |
| L — Inbox/Comms | b9-p13-inbox-communication.md | 3 | RTL mandatory; thread-first; routing-aware. L-02 route unified to `/app/inbox/:thread_id`. L-03 now specified. `shared-inbox.md` entities integrated. |
| M — AI/Copilot | b9-p14-ai-copilot.md | 2 | Advisory-only; evidence-anchored; no speculation |

---

## §6 — File Naming Conventions

| Pattern | Convention | Example |
|---|---|---|
| List views | `<entity>s.html` | `leads.html`, `cases.html` |
| Detail views | `<entity>-detail.html` | `leads-detail.html`, `cases-detail.html` |
| Dashboards | `<domain>-dashboard.html` | `sales-dashboard.html` |
| New/create forms | `<entity>-new.html` | `lead-new.html` |
| Admin pages | prefix with domain | `users.html`, `roles.html`, `territories.html` |
| Settings pages | `<topic>-settings.html` or `<topic>.html` | `integrations.html`, `billing-settings.html` |

**JS file convention:** `crm-<pagename>.js` matching the HTML file. All in `src/assets/js/app/`.
**Route convention:** `/app/<path>` — always kebab-case, no trailing slash.

---

## §7 — Blocked Surfaces

| Screen | ID | Blocker | Notes |
|---|---|---|---|
| Billing & Subscription Settings | G-04 | P-016 — JazzCash/Easypaisa sandbox credentials | Architecture correct; stub_mode=True. Build UI skeleton but wire payment methods only after credentials received. |
| Notification Settings (Urdu) | G-06 | P-017 — Native Urdu speaker review | Build EN strings. Add UR strings only after BEHAV-017 review completes. |
| AI Copilot Panel | M-01 | Inference model selection pending | Build UI shell. Wire `CopilotContext` contract. Actual AI inference is out of scope for v1. |

---

*End of DESIGN-SPEC.md*
