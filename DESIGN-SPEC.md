# Pakistan CRM — Design Specification

**Purpose:** Master screen inventory and archetype map for all custom Pakistan CRM pages. Gates the custom design phase — read this before building any custom screen.
**Last updated:** 2026-05-17
**Build state:** Library phase COMPLETE (96 NexLink pages, all browser-approved). Custom design phase NOT STARTED.

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
**Status key:** ⬜ Not started | 🔄 Library page exists (needs custom work) | ✓ Custom build complete

---

### Archetype A — Dashboard / KPI Overview
**Spec:** `docs/b9-p01-dashboard-kpi.md` | 13 panels | **5-zone layout:** posture → primary_kpi → execution_queue → trend_diagnostic → risk_anomaly

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| A-01 | Owner / Sales Dashboard | dashboard.html | /app/dashboard | 🔄 | Library page exists. Needs backend-wired KPIs from `OpportunityPipelineSnapshotRM` + `LeadFunnelPerformanceRM`. |
| A-02 | Lead Funnel Dashboard | leads-dashboard.html | /app/sales/leads/dashboard | ⬜ | Manager view. `LeadFunnelPerformanceRM`. Role gate: sales_manager, owner. |
| A-03 | Customer Health Dashboard | contacts-health.html | /app/contacts/health | ⬜ | `CustomerMasterHealthRM`. Duplicate merge queue. |
| A-04 | Opportunity Pipeline Dashboard | sales-dashboard.html | /app/sales/dashboard | ⬜ | `OpportunityPipelineSnapshotRM`. Forecast commit + gap to target. |
| A-05 | Quote Approval Dashboard | quotes-dashboard.html | /app/sales/quotes/dashboard | ⬜ | `QuoteApprovalCycleRM`. Stalled quotes risk indicator. |
| A-06 | Subscription Revenue Dashboard | subscriptions-dashboard.html | /app/finance/subscriptions/dashboard | ⬜ | `SubscriptionRevenueRetentionRM`. MRR/ARR/churn. Role: finance, owner. |
| A-07 | Case SLA Operations Dashboard | support-dashboard.html | /app/support/dashboard | ⬜ | `CaseSLAOperationalRM`. Breach count posture strip. |
| A-08 | Communication Engagement Dashboard | engagement-dashboard.html | /app/marketing/engagement | ⬜ | `CommunicationEngagementRM`. Channel delivery/open/reply rates. |
| A-09 | Knowledge Effectiveness Dashboard | knowledge-dashboard.html | /app/support/knowledge/dashboard | ⬜ | `KnowledgeEffectivenessRM`. Case deflection rate. |
| A-10 | Workflow Automation Dashboard | workflows-dashboard.html | /app/workflows/dashboard | ⬜ | `WorkflowAutomationOutcomeRM`. Failure count posture. |
| A-11 | Tenant & Entitlement Dashboard | tenants-dashboard.html | /app/admin/tenants | ⬜ | Super-admin only. `TenantEntitlementOverviewRM`. |
| A-12 | Identity & Access Posture Dashboard | identity-dashboard.html | /app/admin/identity | ⬜ | `IdentityAccessPostureRM`. Privileged account risk. |
| A-13 | Platform Audit & Reliability Dashboard | audit-dashboard.html | /app/admin/audit/dashboard | ⬜ | `PlatformReliabilityAuditRM`. Compliance officer view. |

---

### Archetype B — List / Queue / Table View
**Spec:** `docs/b9-p02-list-queue.md` | 11 surfaces | **Shell:** filter bar → sortable columns → row quick actions → bulk actions → pagination

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| B-01 | Follow-up Queue | followups.html | /app/followups | 🔄 | Library page exists. **Tier 1 priority surface.** Needs `FollowupTask` API wiring, enforcement strip, overdue-pinned sort. |
| B-02 | Lead Queue | leads.html | /app/leads | 🔄 | Library page exists. Needs `LeadFunnelPerformanceRM` KPIs + `Lead` API wiring. |
| B-03 | Contact List | contacts.html | /app/contacts | 🔄 | Library page exists. Needs `Contact` API + last touchpoint + open cases column. |
| B-04 | Account List | accounts.html | /app/accounts | ⬜ | `Account` + outstanding invoices in PKR. |
| B-05 | Ticket / Case Queue | cases.html | /app/support/cases | ⬜ | SLA-sorted, `response_due_at ASC`. Breach colour coding. |
| B-06 | Activity Feed | activity.html | /app/activity | ⬜ | Read-only. `ActivityEvent`. No inline edits. |
| B-07 | Task Queue | tasks.html | /app/tasks | ⬜ | Overdue-pinned. `ActivityTaskOperationalRM`. |
| B-08 | Collections Queue | collections.html | /app/collections | ⬜ | PKR amounts. Overdue-first sort. Reminder send action. |
| B-09 | Invoice Queue | invoices.html | /app/finance/invoices | ⬜ | `InvoiceSummary`. Balance column. PDF download action. |
| B-10 | User Directory | users.html | /app/admin/users | ⬜ | Admin-only. Role badge list. Suspend + reset password actions. |
| B-11 | Partner List | partners.html | /app/partners | ⬜ | `Partner`. Tier + attribution + deal registration count. |

---

### Archetype C — Entity Detail / 360 View
**Spec:** `docs/b9-p06-entity-detail.md` | 12 surfaces | **Shell:** sticky header strip → split pane (main + context) → inline edit → activity timeline

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| C-01 | Lead Detail | leads-detail.html | /app/leads/:lead_id | 🔄 | Library page exists. Needs next-action card, enforcement badge, follow-up panel. |
| C-02 | Customer 360 | contacts-detail.html | /app/contacts/:contact_id/360 | ⬜ | `Contact` + open leads + cases + invoice balance. Merge suggestions if feature-flagged. |
| C-03 | Account Profile | accounts-detail.html | /app/accounts/:account_id | ⬜ | Hierarchy panel. Subsidiary list. Outstanding balance in PKR. |
| C-04 | Opportunity Detail | opportunities-detail.html | /app/opportunities/:opportunity_id | ⬜ | Stage advance + Won/Lost actions. Forecast contribution context panel. |
| C-05 | Case / Ticket Detail | cases-detail.html | /app/support/cases/:case_id | ⬜ | SLA timer always visible. Escalation controls gated by SLA state. Conversation thread. |
| C-06 | Quote Detail | quotes-detail.html | /app/sales/quotes/:quote_id | ⬜ | Line items table. Approval history. Convert to Order action. |
| C-07 | Order Detail | orders-detail.html | /app/sales/orders/:order_id | ⬜ | Immutable post-creation. Invoice linkage. Fulfillment status. |
| C-08 | Invoice Detail | invoices-detail.html | /app/finance/invoices/:invoice_id | ⬜ | Payment history. Proof attachments. Reconciliation status. |
| C-09 | Subscription Detail | subscriptions-detail.html | /app/finance/subscriptions/:subscription_id | ⬜ | Plan change history. Renewal window. Churn risk indicator. |
| C-10 | Workflow Execution Detail | workflow-run-detail.html | /app/workflows/runs/:execution_id | ⬜ | Step-by-step execution log. Retry / dead-letter status. |
| C-11 | Partner Detail | partners-detail.html | /app/partners/:partner_id | ⬜ | Attribution lineage. Commission history. Deal registrations. |
| C-12 | Knowledge Article Detail | knowledge-article.html | /app/support/knowledge/:article_id | ⬜ | Version history. Case deflection count. Publish / archive actions. |

---

### Archetype D — Sales Cockpit
**Spec:** `docs/b9-p03-sales-cockpit.md` | 4 views (single page surface) | **Shell:** pipeline execution rail + deal workspace + forecast context + next-actions panel

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| D-01 | Sales Cockpit | sales-cockpit.html | /app/sales/cockpit | ⬜ | 4-view cockpit. Primary: pipeline execution rail (stage progression P0 action). KanBan or list toggle. |

---

### Archetype E — Support Console
**Spec:** `docs/b9-p04-support-console.md` | Queue-first console | **Shell:** SLA queue → conversation thread → escalation controls

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| E-01 | Support Console | support-console.html | /app/support/console | ⬜ | Queue sorted by SLA due-time. Always-visible SLA timer. Escalation deterministic by SLA state. |

---

### Archetype F — Marketing / Campaign Workspace
**Spec:** `docs/b9-p05-marketing-workspace.md` | Campaign lifecycle | Draft → segment validation → activation → attribution

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| F-01 | Marketing Workspace | marketing-workspace.html | /app/marketing/campaigns | ⬜ | Campaign lifecycle. Segment builder. Journey trigger on conversion. |

---

### Archetype G — Settings / Admin / RBAC
**Spec:** `docs/b9-p09-settings-admin.md` | 9 pages | **Shell:** settings sidebar → content panel → permission-gated write states

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| G-01 | Organization Settings | org-settings.html | /app/settings/org | ⬜ | Tenant name, logo, timezone, currency, locale. |
| G-02 | User Management | user-management-crm.html | /app/admin/users/manage | ⬜ | Invite, suspend, reset. RBAC role assignment. 2-step confirm for destructive actions. |
| G-03 | Role & Permission Editor | roles.html | /app/admin/roles | ⬜ | Role definition + scope assignment. Default-deny model. Break-glass controls. |
| G-04 | Billing & Subscription Settings | billing-settings.html | /app/settings/billing | ⬜ | Plan tier display. Upgrade/downgrade. JazzCash/Easypaisa payment method. |
| G-05 | Integration Settings | integrations.html | /app/settings/integrations | ⬜ | WhatsApp API key config. 360dialog / Gupshup toggle. Payment provider config. |
| G-06 | Notification Settings | notifications.html | /app/settings/notifications | ⬜ | Per-event notification rules. Channel preference (WhatsApp / email / in-app). |
| G-07 | Feature Flags | feature-flags.html | /app/admin/feature-flags | ⬜ | Admin-only. Toggle progressive disclosure tiers. Tenant-scoped overrides. |
| G-08 | Compliance Settings | compliance.html | /app/settings/compliance | ⬜ | Audit retention policy. Data governance controls. Break-glass log. |
| G-09 | Territory & Assignment Config | territories.html | /app/admin/territories | ⬜ | Territory hierarchy. Assignment rules. Anti-ambiguity checks. |

---

### Archetype H — Reporting / Analytics
**Spec:** `docs/b9-p10-reporting-analytics.md` | 7 pages | **Shell:** date-range filter → chart grid → drilldown

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| H-01 | Sales Analytics | sales-analytics.html | /app/reports/sales | ⬜ | Pipeline velocity, conversion funnel, rep performance. |
| H-02 | Marketing Analytics | marketing-analytics.html | /app/reports/marketing | ⬜ | Campaign attribution, channel engagement, journey conversion. |
| H-03 | Support Analytics | support-analytics.html | /app/reports/support | ⬜ | SLA breach rate, first-response time, resolution trends. |
| H-04 | Finance Analytics | finance-analytics.html | /app/reports/finance | ⬜ | Collections rate, overdue aging, PKR cash position. |
| H-05 | Workflow Analytics | workflow-analytics.html | /app/reports/workflows | ⬜ | Execution volume, failure rate, retry queue depth. |
| H-06 | Audit Report | audit-report.html | /app/reports/audit | ⬜ | Compliance officer view. Hash-chain verified. Immutable export. |
| H-07 | Custom Report Builder | report-builder.html | /app/reports/builder | ⬜ | Drag-and-drop metric selection. Save + schedule. |

---

### Archetype I — Form / Wizard / CPQ
**Spec:** `docs/b9-p11-form-wizard.md` | 6 pages | **Shell:** ≤2-step rule enforced — step 1 required fields, step 2 confirm/extras

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| I-01 | New Lead Form | lead-new.html | /app/leads/new | ⬜ | Step 1: phone + name. Step 2: stage + owner. Auto-dedup on phone E.164. |
| I-02 | New Contact Form | contact-new.html | /app/contacts/new | ⬜ | Step 1: name + phone. Step 2: account + tags. |
| I-03 | New Opportunity Form | opportunity-new.html | /app/opportunities/new | ⬜ | Step 1: account + amount. Step 2: close date + stage. |
| I-04 | New Case Form | case-new.html | /app/support/cases/new | ⬜ | Step 1: contact + subject + priority. Step 2: queue + description. |
| I-05 | CPQ Quote Builder | quote-builder.html | /app/sales/quotes/new | ⬜ | CPQ line item entry + rule engine validation + discount approval. |
| I-06 | Journey / Campaign Builder | campaign-new.html | /app/marketing/campaigns/new | ⬜ | Step 1: name + segment. Step 2: message + trigger. |

---

### Archetype J — Audit / Compliance
**Spec:** `docs/b9-p12-audit-compliance.md` | 5 pages | **Shell:** immutable read-only log, hash-chain verified, export controls

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| J-01 | Audit Log | audit-log.html | /app/audit | ⬜ | Immutable. Hash-chain verified. Filter by actor/entity/date. No delete action. |
| J-02 | Compliance Report | compliance-report.html | /app/compliance | ⬜ | Regulatory submission view. Export as PDF. |
| J-03 | Data Governance Console | data-governance.html | /app/admin/governance | ⬜ | Governance controls: retention, classification, masking rules. |
| J-04 | RBAC Audit | rbac-audit.html | /app/admin/rbac-audit | ⬜ | Who has what permissions. Privilege escalation alerts. |
| J-05 | Consent & Privacy Manager | privacy.html | /app/settings/privacy | ⬜ | Data subject requests. Consent records. Deletion workflows. |

---

### Archetype K — Builder / Visual Canvas
**Spec:** `docs/b9-p07-workflow-visual-ui.md` + `docs/b9-p08-builder-extensions.md` | 4 pages

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| K-01 | Workflow Builder | workflow-builder.html | /app/workflows/builder | ⬜ | Visual graph builder. 1:1 UI↔DSL mapping. Trigger → condition → action nodes. |
| K-02 | Custom Object Layout Builder | object-builder.html | /app/admin/objects | ⬜ | FieldDefinition drag-and-drop. Layout preview. |
| K-03 | Rule / CPQ Logic Builder | rule-builder.html | /app/admin/rules | ⬜ | Deterministic rule engine editor. Condition groups + action definitions. |
| K-04 | CPQ Approval Lane Board | approval-lanes.html | /app/sales/approval-lanes | ⬜ | Kanban-style approval stages. Discount band visibility. |

---

### Archetype L — Inbox / Communication
**Spec:** `docs/b9-p13-inbox-communication.md` | 3 pages | **Shell:** thread list → conversation view → routing controls | RTL mandatory (Urdu messages)

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| L-01 | Omnichannel Inbox | inbox.html | /app/inbox | ⬜ | WhatsApp + email + SMS thread list. Unread badge. Routing assignment. |
| L-02 | Conversation Thread | inbox-thread.html | /app/inbox/:thread_id | ⬜ | Chronological message thread. RTL-safe message bubbles. Send / template actions. |
| L-03 | Routing Configuration | routing-config.html | /app/admin/routing | ⬜ | Assignment rules editor. Queue + owner routing logic. |

---

### Archetype M — AI / Copilot
**Spec:** `docs/b9-p14-ai-copilot.md` | 2 pages | **Advisory-only** — suggestions must reference observed data only (no ungrounded inference)

| # | Screen | File | Route | Status | Notes |
|---|---|---|---|---|---|
| M-01 | AI Copilot Panel | ai-copilot.html | /app/ai/copilot | ⬜ | Evidence-anchored suggestions. `CopilotContext` → `CopilotSuggestion` contract. No speculative outputs. |
| M-02 | AI Insights Dashboard | ai-insights.html | /app/ai/insights | ⬜ | Win probability, churn prediction, CLV estimates from `src/predictive_models/`. |

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
| G — Settings/Admin | b9-p09-settings-admin.md | 9 | Default-deny panel; 2-step confirm for destructive ops |
| H — Reporting | b9-p10-reporting-analytics.md | 7 | Date-range filter first; drilldown on demand |
| I — Form/Wizard | b9-p11-form-wizard.md | 6 | ≤2 steps enforced; step 1 required only; dedup on submit |
| J — Audit/Compliance | b9-p12-audit-compliance.md | 5 | Immutable; hash-chain verified; no delete actions |
| K — Builder/Canvas | b9-p07 + b9-p08-builder-extensions.md | 4 | 1:1 UI↔DSL mapping; graph import/export with validation |
| L — Inbox/Comms | b9-p13-inbox-communication.md | 3 | RTL mandatory; thread-first; routing-aware |
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
