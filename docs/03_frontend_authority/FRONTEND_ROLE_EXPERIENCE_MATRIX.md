---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Derived From: USER_ROLES_AND_PERMISSIONS.md (from rbac-scopes.js), DESIGN-SPEC.md, FEATURE_SCOPE.md
---

# FRONTEND ROLE EXPERIENCE MATRIX — Pakistan CRM OS

For each of the 7 canonical roles: accessible pages, inaccessible pages, available actions, dashboard widgets, navigation, key workflows, and restrictions.

**Source of truth:** `backend/gateway/config/rbac-scopes.js` ROLE_SCOPES mapping, as documented in USER_ROLES_AND_PERMISSIONS.md.

**Canonical roles (from rbac-scopes.js):** tenant_owner, tenant_admin, manager, agent, analyst, auditor, integration_service. All role names in this document use the canonical names. Previous drafts used incorrect names (super_admin, senior_agent, collections_agent, read_only) — those have been corrected. See FRONTEND_GAP_REGISTER.md Gap G-008.

---

## Role 1: tenant_owner

**Display Name:** Tenant Owner
**Description:** Highest privilege role. Full access to all scopes.
**Scope Count:** All scopes (including admin.manage_tenants and admin.manage_feature_flags)

### Accessible Pages (all 75 custom pages)
All pages accessible. Includes tenant-exclusive pages:
- tenants-dashboard.html (A-11) — only role with admin.manage_tenants
- feature-flags.html (G-07) — only role with admin.manage_feature_flags
- Both pages are inaccessible to tenant_admin and below

### Inaccessible Pages
None — tenant_owner has access to all 75 custom pages.

### Available Actions
All actions across all pages including:
- Create/edit/delete any entity across any tenant
- Manage feature flags (dual-approval required for high-risk flags)
- View cross-tenant tenant dashboard
- Export compliance data (admin.export_compliance_data)
- Manage all roles, users, territories, workflows
- Force-close cases; close opportunities; approve quotes
- Generate AI forecasts; train AI models

### Dashboard Widgets Visible
All widgets on all 13 dashboards (A-01 through A-13).

### Navigation Items Visible
All navigation items including:
- Admin sub-menu (including "Tenants" — tenant_owner only)
- Settings sub-menu
- Feature Flags menu item

### Key Workflows Available
- WF-A Lead-to-Deal (all steps, all roles)
- WF-B Deal-to-Invoice (all steps)
- WF-C Case Lifecycle (all steps including force-close)
- WF-D WhatsApp Conversation (all steps)
- WF-E Payment Collection (all steps)

### Restrictions
- Feature flags with requires_dual_approval=true require second approver
- System workflows (is_system=true) cannot be edited (403 on PATCH)
- JazzCash/Easypaisa blocked by P-016 (not a role restriction — production constraint)
- contacts.delete requires OA-001 resolution (SD-001 in effect)

---

## Role 2: tenant_admin

**Display Name:** Tenant Admin
**Description:** Full administrative rights within a single tenant. Most common admin role in production.
**Scope Count:** 35 (all domain entity scopes + admin scopes except admin.manage_tenants and admin.manage_feature_flags)

### Accessible Pages (all 75 except tenant_owner-only)
All 75 custom pages EXCEPT:
- tenants-dashboard.html (A-11) — requires admin.manage_tenants
- feature-flags.html (G-07) — requires admin.manage_feature_flags

### Inaccessible Pages
- tenants-dashboard.html (A-11) — 403 on GET /admin/tenants
- feature-flags.html (G-07) — 403 on GET /feature-flags

### Available Actions
All actions within the tenant:
- leads.delete, accounts.delete, opportunities.delete/close
- quotes.approve, quotes.convert_to_order, orders.fulfil
- cases.close, cases.assign, cases.escalate
- inbox.supervise; campaigns.activate; workflows.publish
- territories.delete/assign; tasks.assign
- collections.approve_payment, collections.reconcile
- ai.train_models, ai.generate_forecasts
- analytics.view_advanced, analytics.export
- knowledge.publish; notifications.send
- partners.create, partners.update
- admin.read_audit_logs, admin.manage_users, admin.manage_roles, admin.system_config

### Dashboard Widgets Visible
All widgets on A-01 through A-10, A-12, A-13 (all except A-11 Tenant Dashboard).

### Navigation Items Visible
All navigation items except "Tenants" in Admin sub-menu and "Feature Flags".

### Key Workflows Available
All 10 workflows (5 primary + 5 system) — full execution authority.

### Restrictions
- Cannot access cross-tenant data (x-tenant-id enforced by gateway middleware)
- Cannot toggle feature flags (tenant_owner only)
- contacts.delete — SD-001 in effect; OA-001 pending
- JazzCash/Easypaisa — P-016 stub state

---

## Role 3: manager

**Display Name:** Manager
**Description:** Manages teams, reviews pipelines, approves workflows. Standard leadership role.
**Scope Count:** 25

### Accessible Pages
Accessible (most pages):
- All Archetype A dashboards: A-01 through A-10 (not A-11, A-12, A-13)
- All Archetype B lists: B-01 through B-11
- All Archetype C detail pages: C-01 through C-12
- D-01 (Sales Cockpit), E-01 (Support Console), F-01 (Marketing Workspace)
- H-01 through H-05 (Analytics — not H-06 Audit Report, not admin.read_audit_logs)
- H-07 (Report Builder)
- I-01 through I-06 (all forms)
- K-04 (Approval Lanes)
- L-01, L-02, L-03 (Routing Config — inbox.supervise required)
- M-01, M-02 (AI pages)
- G-09 (Territories — territories.read)

### Inaccessible Pages
- A-11 (Tenant Dashboard — admin.manage_tenants required)
- A-12 (Identity Dashboard — admin.read_audit_logs required)
- A-13 (Audit Dashboard — admin.read_audit_logs required)
- G-01 through G-08 (Settings — admin.system_config required)
- G-09 only if territories.create required (territories.read is enough to view)
- J-01 through J-05 (Audit/Compliance — admin.read_audit_logs or admin.system_config required)
- H-06 (Audit Report — admin.read_audit_logs required)
- K-01 (Workflow Builder — workflows.create required — manager has workflows.read only)
- K-02, K-03 (Builder tools — admin.system_config required)
- B-10, G-02, G-03 (User Management / Roles — admin.manage_users required)
- feature-flags.html (G-07), tenants-dashboard.html (A-11)

### Available Actions
- leads.read/create/update/export/assign (no delete)
- contacts.read/create/update (no delete)
- accounts.read/create/update (no delete)
- opportunities.read/create/update/close
- cases.read/update/close/assign/escalate
- inbox.read/claim/supervise
- campaigns.read; workflows.read; territories.read
- tasks.read/create/update/complete/assign
- collections.read/view_overdue
- ai.view_scores/view_forecasts/generate_forecasts
- analytics.view_advanced; knowledge.read
- quotes.read/create/update/approve (no quotes.convert_to_order)
- orders.read

### Dashboard Widgets Visible
All standard business KPIs. No admin/audit platform health widgets.

### Navigation Items Visible
All except Admin sub-menu (except Territories and Routing) and Settings sub-menu.

### Key Workflows Available
- WF-A (Lead-to-Deal) — all steps; can approve quotes
- WF-B (Deal-to-Invoice) — can create invoices; cannot configure payment rails
- WF-C (Case Lifecycle) — full case management including close and escalate
- WF-D (WhatsApp Conversation) — can supervise agent handoffs
- WF-E (Payment Collection) — can view; collections.view_overdue

### Restrictions
- Cannot manage users or roles (admin.manage_users required)
- Cannot change system settings (admin.system_config required)
- Cannot publish workflows (workflows.publish — tenant_admin only)
- Cannot delete leads, contacts, accounts
- Cannot create territories (territories.create — tenant_admin only)

---

## Role 4: manager (senior operational — see also Role 3)

**Display Name:** Manager
**Description:** Lead and contact management with supervisor capabilities. Collections scopes included on agent role in rbac-scopes.js.
**Scope Count:** 20 (senior operational sub-set; Role 3 describes full manager scope set)

### Accessible Pages
- All B-series lists: B-01 to B-11 (read-only on some)
- C-01, C-02, C-03, C-04, C-05 (detail pages for core entities)
- D-01 (Sales Cockpit), E-01 (Support Console)
- I-01 to I-04 (core forms); I-05 (CPQ — quotes.create)
- L-01, L-02 (Inbox — inbox.handoff enabled)
- M-01 (AI Copilot)
- H-01 (Sales Analytics — analytics.view_basic)

### Inaccessible Pages
- All G-series (Settings/Admin)
- All J-series (Audit/Compliance)
- All H-series except H-01 (analytics.view_advanced not granted)
- A-11, A-12, A-13 (admin dashboards)
- F-01 (Marketing Workspace — campaigns.read not in scope)
- I-06 (Campaign Builder — campaigns.create not in scope)
- K-01 to K-04 (Builder tools)
- Workflow pages (workflows.read not granted to this role)
- M-02 (AI Insights — ai.view_forecasts not granted)
- report-builder.html (H-07 — analytics.view_advanced needed)

### Available Actions
- leads.read/create/update/assign (no delete)
- contacts.read/create/update (no delete)
- accounts.read/create/update (no delete)
- opportunities.read/create/update (no close)
- cases.read/create/update/assign (no close — cases.close not granted)
- inbox.read/claim/handoff (can handoff conversations)
- activities.read/create; tasks.read/create/update/complete
- collections.read/view_overdue
- ai.view_scores; analytics.view_basic; knowledge.read

### Navigation Items Visible
Core CRM navigation (Follow-ups, Leads, Contacts, Accounts, Sales, Support, Inbox, Partners, AI Copilot, Reports basic, Activity, Tasks).

### Key Workflows Available
- WF-A (Lead-to-Deal) — steps 1–7 (cannot close opportunity — no opportunities.close)
- WF-C (Case Lifecycle) — steps 1–7 (cannot close case — no cases.close)
- WF-D (WhatsApp Conversation) — steps 5–8 (claim, respond, handoff)

### Restrictions
- Cannot close opportunities or cases (escalate to manager)
- Cannot approve quotes (quotes.approve not granted)
- Cannot access analytics beyond basic (analytics.view_advanced not granted)
- Cannot manage campaigns or workflows

---

## Role 5: agent

**Display Name:** Agent
**Description:** Standard CRM agent — leads, contacts, calls, cases.
**Scope Count:** 12

### Accessible Pages
- B-01 (Follow-ups), B-02 (Leads), B-03 (Contacts), B-05 (Cases), B-06 (Activity), B-07 (Tasks)
- C-01 (Lead Detail), C-02 (Customer 360), C-04 (Opportunity Detail), C-05 (Case Detail)
- D-01 (Sales Cockpit — opportunities.read)
- E-01 (Support Console — cases.read + inbox.read)
- I-01 (New Lead), I-02 (New Contact), I-03 (New Opportunity), I-04 (New Case)
- L-01, L-02 (Inbox — inbox.claim but NOT inbox.handoff)
- M-01 (AI Copilot — ai.view_scores — CONFIRM: agent scope list in USER_ROLES doc doesn't include ai.view_scores, but it's listed in notes)

### Inaccessible Pages (majority of admin/finance/marketing pages)
- All G-series (Settings/Admin)
- All J-series (Audit/Compliance)
- All H-series Analytics (no analytics scope granted)
- All A-series dashboards except A-01 (if reads.leads is enough)
- F-01, I-06 (Marketing — no campaigns scope)
- K-01 to K-04 (Builder tools)
- B-04 (Accounts — accounts.read YES, accessible for read)
- B-08, B-09 (Collections, Invoices — no collections scope)
- B-10, B-11 (Users, Partners — no admin or partners.read scope)

### Available Actions
- leads.read/create/update (no assign, delete, import, export)
- contacts.read/create (no update — contacts.update not in agent scope)
- accounts.read (read-only)
- opportunities.read/create (no update — opportunities.update not in agent scope)
- cases.read/create (no update, assign, close)
- inbox.read/claim (no handoff, supervise)
- activities.read/create; tasks.read/create/update/complete
- notifications.read; knowledge.read

### Navigation Items Visible
Core: Dashboard, Follow-ups, Leads, Contacts, Support (Cases, Console), Inbox, Activity, Tasks.

### Key Workflows Available
- WF-A steps 1–5 (capture lead, schedule follow-up, qualify through stages)
- WF-C steps 1, 3, 4, 5, 7 (create case, receive assignment, respond, communicate)
- WF-D steps 5–6 (claim conversation, respond — no handoff)

### Restrictions
- Cannot update contacts (contacts.update not in agent scope)
- Cannot update opportunities (opportunities.update not in agent scope)
- Cannot assign leads or cases
- Cannot claim conversations beyond max_concurrent=10 cap
- Cannot view analytics, reports, or any admin surfaces
- Cannot access billing, integrations, or compliance

---

## Role 6: agent (collections-focused — see also Role 5)

**Display Name:** Agent
**Description:** Collections and billing specialist. Collections scopes are included on the agent role in rbac-scopes.js.
**Scope Count:** 8 (collections sub-set of agent scopes; Role 5 describes full agent scope set)

### Accessible Pages
- B-03 (Contacts — contacts.read)
- B-04 (Accounts — accounts.read)
- B-02 (Leads — leads.read)
- B-08 (Collections Queue — primary workspace)
- B-09 (Invoice Queue — collections.read)
- C-08 (Invoice Detail — collections.read)
- H-04 (Finance Analytics — analytics.view_basic)

### Inaccessible Pages
All pages except the 7 listed above. This is the most restricted human-user role.

Key inaccessible pages:
- All A-series dashboards (except possibly A-01 if leads.read is sufficient)
- All G-series, J-series (admin)
- All support, marketing, workflow, AI, inbox pages
- C-01 through C-07, C-09 through C-12 (no entity.read scope beyond contacts/accounts/invoices)

### Available Actions
- collections.read (view collections queue)
- collections.create_invoice (POST /collections/invoices)
- collections.record_payment (POST /payments — STUB)
- collections.view_overdue (view overdue filter)
- contacts.read, accounts.read, leads.read
- analytics.view_basic
- notifications.read

### Navigation Items Visible
Contacts, Accounts, Collections, Finance (Invoices), Reports (Finance Analytics only).

### Key Workflows Available
- WF-B steps 6–7 (collections follow-up + reconciliation)
- WF-E steps 4–6 (agent follow-up, payment receipt, reconciliation)

### Restrictions
- Cannot create, update, or delete any CRM entity except invoices/collections
- Cannot view any support, marketing, or workflow pages
- Cannot access any admin or settings pages
- Cannot handoff conversations (no inbox scope)
- Cannot approve payments without collections.approve_payment (not in scope — confirm against rbac-scopes.js)

---

## Role 7: analyst

**Display Name:** Analyst
**Description:** Read-only access plus analytics and AI reads. Observer/reporting role.
**Scope Count:** Read-only across leads, opportunities, contacts, accounts, collections, payments, revenue, subscriptions, cases, knowledge, plus ai.view_scores, ai.view_predictions, ai.view_clv, ai.view_models

### Accessible Pages (read-only view of core entity pages)
- B-02 (Leads — leads.read)
- B-03 (Contacts — contacts.read)
- B-04 (Accounts — accounts.read)
- B-06 (Activity — activities.read)
- B-07 (Tasks — tasks.read)
- B-08, B-09 (Collections, Invoices — collections.read)
- C-01 (Lead Detail — leads.read)
- C-02 (Customer 360 — contacts.read)
- C-03 (Account Profile — accounts.read)
- C-04 (Opportunity Detail — opportunities.read)
- C-05 (Case Detail — cases.read)
- C-08 (Invoice Detail — collections.read)
- C-12 (Knowledge Article — knowledge.read)
- H-01, H-03, H-04 (basic analytics)

### Inaccessible Pages
All write-enabled pages, all admin/settings pages, all marketing/workflow/AI pages.

### Available Actions
Read-only on all accessible pages. No create, update, delete, or action buttons visible.

### Dashboard Widgets Visible
Limited: leads and contacts read-only tiles on A-01 (if accessible). No admin dashboards.

### Navigation Items Visible
Only read-accessible modules: Leads, Contacts, Accounts, Activity, Tasks, Collections, Finance, Reports (basic), Knowledge.

### Key Workflows Available
None — analyst cannot execute any workflow step. Observer role only.

### Restrictions
- No write access anywhere
- No admin, settings, or compliance access
- No AI, marketing, or workflow access
- No inbox or communication access

---

*End FRONTEND_ROLE_EXPERIENCE_MATRIX.md*
*7 canonical roles: tenant_owner, tenant_admin, manager, agent, analyst, auditor, integration_service*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
