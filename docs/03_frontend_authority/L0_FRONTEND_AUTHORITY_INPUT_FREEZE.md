---
Status: L0 FROZEN
Authority Level: Critical
Freeze Date: 2026-06-24
Phase: C6 (Commercial Launch)
Derived From: FRONTEND_AUTHORITY_MASTER.md, FRONTEND_ROUTE_CATALOG.md, FRONTEND_SCREEN_CATALOG.md,
  FRONTEND_DASHBOARD_CATALOG.md, FRONTEND_NAVIGATION_MODEL.md, FRONTEND_ROLE_EXPERIENCE_MATRIX.md,
  FRONTEND_PERMISSION_MATRIX.md, FRONTEND_WORKFLOW_TO_SCREEN_MAP.md, FRONTEND_API_DEPENDENCY_MAP.md,
  FRONTEND_GAP_REGISTER.md, PRODUCT_DECISION_REGISTER.md, POST_COLLAPSE_FRONTEND_READINESS.md,
  DETERMINISM_CERTIFICATION_REPORT.md, SAFE_DEFAULT_REGISTER.md, DESIGN-SPEC.md
---

# L0 FRONTEND AUTHORITY INPUT FREEZE — Pakistan CRM OS

## FREEZE STATUS: L0 FROZEN

**Reason:** FRONTEND_GAP_REGISTER.md conclusion: "There are no gaps that block Frontend Authority Capture." DETERMINISM_CERTIFICATION_REPORT.md verdict: "REPOSITORY FULLY DETERMINED." POST_COLLAPSE_FRONTEND_READINESS.md verdict: "GO — Frontend Authority Capture may begin immediately and without restriction." Zero blocking gaps against C6 scope.

**Freeze Date:** 2026-06-24

**Scope:** 75 custom CRM pages (Archetypes A–M) + 94 NexLink library pages = 169 total pages

---

## Section 1 — Approved Routes (Complete List)

### Custom CRM Routes (75)

| Route | Title | Module | Phase | Status |
|---|---|---|---|---|
| /app/dashboard | Owner / Sales Dashboard | Core | Phase 1 | APPROVED |
| /app/followups | Follow-up Queue | Follow-up Enforcement | Phase 1 | APPROVED |
| /app/leads | Lead Queue | Lead Management | Phase 1 | APPROVED |
| /app/leads/:lead_id | Lead Detail | Lead Management | Phase 1 | APPROVED |
| /app/leads/new | New Lead Form | Lead Management | Phase 1 | APPROVED |
| /app/sales/leads/dashboard | Lead Funnel Dashboard | Lead Management | Phase 2 | APPROVED |
| /app/contacts | Contact List | Contacts | Phase 1 | APPROVED |
| /app/contacts/:contact_id/360 | Customer 360 | Contacts | Phase 8 | APPROVED |
| /app/contacts/new | New Contact Form | Contacts | Phase 8 | APPROVED |
| /app/contacts/health | Customer Health Dashboard | Contacts | Phase 8 | APPROVED |
| /app/accounts | Account List | Accounts | Phase 8 | APPROVED |
| /app/accounts/:account_id | Account Profile | Accounts | Phase 8 | APPROVED |
| /app/opportunities/:opportunity_id | Opportunity Detail | Sales | Phase 2 | APPROVED |
| /app/opportunities/new | New Opportunity Form | Sales | Phase 2 | APPROVED |
| /app/sales/cockpit | Sales Cockpit | Sales | Phase 2 | APPROVED |
| /app/sales/dashboard | Opportunity Pipeline Dashboard | Sales | Phase 2 | APPROVED |
| /app/sales/quotes/new | CPQ Quote Builder | CPQ | Phase 2 | APPROVED |
| /app/sales/quotes/:quote_id | Quote Detail | CPQ | Phase 2 | APPROVED |
| /app/sales/quotes/dashboard | Quote Approval Dashboard | CPQ | Phase 2 | APPROVED |
| /app/sales/orders/:order_id | Order Detail | CPQ | Phase 8 | APPROVED |
| /app/collections | Collections Queue | Finance | Phase 1 | APPROVED |
| /app/finance/invoices | Invoice Queue | Finance | Phase 3 | APPROVED |
| /app/finance/invoices/:invoice_id | Invoice Detail | Finance | Phase 3 | APPROVED |
| /app/reports/finance | Finance Analytics | Finance | Phase 3 | APPROVED |
| /app/finance/subscriptions/dashboard | Subscription Revenue Dashboard | Subscriptions | Phase 3 | APPROVED |
| /app/finance/subscriptions/:subscription_id | Subscription Detail | Subscriptions | Phase 3 | APPROVED |
| /app/settings/billing | Billing & Subscription Settings | Billing | Phase 6 | APPROVED |
| /app/support/cases | Ticket / Case Queue | Support | Phase 4 | APPROVED |
| /app/support/cases/:case_id | Case / Ticket Detail | Support | Phase 4 | APPROVED |
| /app/support/cases/new | New Case Form | Support | Phase 4 | APPROVED |
| /app/support/console | Support Console | Support | Phase 4 | APPROVED |
| /app/support/dashboard | Case SLA Operations Dashboard | Support | Phase 4 | APPROVED |
| /app/support/knowledge/:article_id | Knowledge Article Detail | Knowledge Base | Phase 4 | APPROVED |
| /app/support/knowledge/dashboard | Knowledge Effectiveness Dashboard | Knowledge Base | Phase 8 | APPROVED |
| /app/inbox | Omnichannel Inbox | Inbox | Phase 5 | APPROVED |
| /app/inbox/:thread_id | Conversation Thread | Inbox | Phase 5 | APPROVED |
| /app/admin/routing | Routing Configuration | Inbox | Phase 8 | APPROVED |
| /app/marketing/campaigns | Marketing Workspace | Marketing | Phase 7 | APPROVED |
| /app/marketing/campaigns/new | Journey / Campaign Builder | Marketing | Phase 7 | APPROVED |
| /app/reports/marketing | Marketing Analytics | Marketing | Phase 7 | APPROVED |
| /app/marketing/engagement | Communication Engagement Dashboard | Marketing | Phase 5 | APPROVED |
| /app/workflows/builder | Workflow Builder | Workflows | Phase 7 | APPROVED |
| /app/workflows/runs/:execution_id | Workflow Execution Detail | Workflows | Phase 8 | APPROVED |
| /app/workflows/dashboard | Workflow Automation Dashboard | Workflows | Phase 7 | APPROVED |
| /app/reports/workflows | Workflow Analytics | Workflows | Phase 8 | APPROVED |
| /app/ai/copilot | AI Copilot Panel | AI | Phase 8 | APPROVED |
| /app/ai/insights | AI Insights Dashboard | AI | Phase 8 | APPROVED |
| /app/admin/territories | Territory & Assignment Config | Territories | Phase 6 | APPROVED |
| /app/partners | Partner List | Partners | Phase 8 | APPROVED |
| /app/partners/:partner_id | Partner Detail | Partners | Phase 8 | APPROVED |
| /app/admin/users | User Directory | Identity | Phase 8 | APPROVED |
| /app/admin/users/manage | User Management | Identity | Phase 6 | APPROVED |
| /app/admin/identity | Identity & Access Posture Dashboard | Identity | Phase 8 | APPROVED |
| /app/audit | Audit Log | Audit | Phase 8 | APPROVED |
| /app/compliance | Compliance Report | Audit | Phase 8 | APPROVED |
| /app/admin/governance | Data Governance Console | Audit | Phase 8 | APPROVED |
| /app/admin/rbac-audit | RBAC Audit | Audit | Phase 8 | APPROVED |
| /app/settings/privacy | Consent & Privacy Manager | Audit | Phase 8 | APPROVED |
| /app/admin/audit/dashboard | Platform Audit & Reliability Dashboard | Audit | Phase 8 | APPROVED |
| /app/reports/audit | Audit Report | Audit | Phase 8 | APPROVED |
| /app/settings/org | Organization Settings | Settings | Phase 6 | APPROVED |
| /app/admin/roles | Role & Permission Editor | Settings | Phase 6 | APPROVED |
| /app/settings/integrations | Integration Settings | Settings | Phase 6 | APPROVED |
| /app/settings/notifications | Notification Settings | Settings | Phase 6 | APPROVED |
| /app/admin/feature-flags | Feature Flags | Settings | Phase 6 | APPROVED |
| /app/settings/compliance | Compliance Settings | Settings | Phase 6 | APPROVED |
| /app/admin/objects | Custom Object Layout Builder | Builder Tools | Phase 8 | APPROVED |
| /app/admin/rules | Rule / CPQ Logic Builder | Builder Tools | Phase 8 | APPROVED |
| /app/sales/approval-lanes | CPQ Approval Lane Board | Builder Tools | Phase 8 | APPROVED |
| /app/reports/builder | Custom Report Builder | Reports | Phase 8 | APPROVED |
| /app/reports/sales | Sales Analytics | Reports | Phase 8 | APPROVED |
| /app/reports/support | Support Analytics | Reports | Phase 8 | APPROVED |
| /app/admin/tenants | Tenant & Entitlement Dashboard | Tenant Admin | Phase 8 | APPROVED |
| /app/activity | Activity Feed | Activity | Phase 8 | APPROVED |
| /app/tasks | Task Queue | Tasks | Phase 8 | APPROVED |

### NexLink Library Routes (94)

94 library pages in frontend/src/app/ (accordion.html through your-chat.html). All are NexLink component demos. No custom CRM authority required. Not part of the 75 custom page scope. Full list in FRONTEND_ROUTE_CATALOG.md Section 2.

---

## Section 2 — Approved Screens (75 Custom Pages)

### Archetype A — Dashboard / KPI Overview (13 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| A-01 | dashboard.html | /app/dashboard | A — Dashboard/KPI | All roles | leads.read, opportunities.read, analytics.view_basic, ai.view_scores | GET /leads, GET /opportunities, GET /forecasts, GET /ai/copilot/suggestions | APPROVED |
| A-02 | leads-dashboard.html | /app/sales/leads/dashboard | A — Dashboard/KPI | All CRM roles | leads.read | GET /leads, GET /followups | APPROVED |
| A-03 | contacts-health.html | /app/contacts/health | A — Dashboard/KPI | manager, tenant_admin | contacts.read, cases.read | GET /contacts, GET /cases | APPROVED |
| A-04 | sales-dashboard.html | /app/sales/dashboard | A — Dashboard/KPI | manager, tenant_admin, tenant_owner | opportunities.read, ai.view_forecasts | GET /opportunities, GET /forecasts | APPROVED |
| A-05 | quotes-dashboard.html | /app/sales/quotes/dashboard | A — Dashboard/KPI | manager, tenant_admin, tenant_owner | quotes.read, quotes.approve | GET /quotes | APPROVED |
| A-06 | subscriptions-dashboard.html | /app/finance/subscriptions/dashboard | A — Dashboard/KPI | manager, tenant_admin, tenant_owner | analytics.view_basic, collections.view_overdue | GET /subscriptions | APPROVED |
| A-07 | support-dashboard.html | /app/support/dashboard | A — Dashboard/KPI | manager, tenant_admin | cases.read, analytics.view_basic | GET /cases | APPROVED |
| A-08 | engagement-dashboard.html | /app/marketing/engagement | A — Dashboard/KPI | manager, tenant_admin, tenant_owner | campaigns.read, analytics.view_basic | GET /communications/engagement, GET /campaigns | APPROVED |
| A-09 | knowledge-dashboard.html | /app/support/knowledge/dashboard | A — Dashboard/KPI | manager, tenant_admin | knowledge.read, analytics.view_basic | GET /knowledge | APPROVED |
| A-10 | workflows-dashboard.html | /app/workflows/dashboard | A — Dashboard/KPI | manager, tenant_admin, tenant_owner | workflows.read, analytics.view_basic | GET /workflows, GET /workflows/runs | APPROVED |
| A-11 | tenants-dashboard.html | /app/admin/tenants | A — Dashboard/KPI | tenant_owner only | admin.manage_tenants | GET /admin/tenants | APPROVED |
| A-12 | identity-dashboard.html | /app/admin/identity | A — Dashboard/KPI | tenant_admin, tenant_owner | admin.read_audit_logs, admin.manage_users | GET /admin/users, GET /admin/audit-logs | APPROVED |
| A-13 | audit-dashboard.html | /app/admin/audit/dashboard | A — Dashboard/KPI | tenant_admin, tenant_owner | admin.read_audit_logs | GET /admin/audit-logs | APPROVED |

### Archetype B — List / Queue / Table View (11 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| B-01 | followups.html | /app/followups | B — List/Queue | All CRM roles | tasks.read, tasks.complete, tasks.update | GET /followups, POST /followups/:id/complete, POST /followups/:id/snooze | APPROVED |
| B-02 | leads.html | /app/leads | B — List/Queue | All CRM roles | leads.read, leads.create, leads.assign | GET /leads, GET /leads/export | APPROVED |
| B-03 | contacts.html | /app/contacts | B — List/Queue | All CRM roles | contacts.read (delete: SD-001 hidden) | GET /contacts, GET /contacts/export, POST /contacts/import | APPROVED |
| B-04 | accounts.html | /app/accounts | B — List/Queue | All CRM roles | accounts.read | GET /accounts | APPROVED |
| B-05 | cases.html | /app/support/cases | B — List/Queue | All CRM roles | cases.read, cases.create | GET /cases | APPROVED |
| B-06 | activity.html | /app/activity | B — List/Queue | All CRM roles | activities.read | GET /activities | APPROVED |
| B-07 | tasks.html | /app/tasks | B — List/Queue | All CRM roles | tasks.read, tasks.complete, tasks.assign | GET /tasks, PATCH /tasks/:id | APPROVED |
| B-08 | collections.html | /app/collections | B — List/Queue | All CRM roles (write: agent+) | collections.read, collections.view_overdue, collections.reconcile | GET /collections, POST /collections/:id/reconcile | APPROVED |
| B-09 | invoices.html | /app/finance/invoices | B — List/Queue | All CRM roles | collections.read | GET /invoice-summaries | APPROVED |
| B-10 | users.html | /app/admin/users | B — List/Queue | tenant_admin, tenant_owner | admin.manage_users | GET /admin/users, PATCH /admin/users/:id, POST /admin/users/:id/reset-password | APPROVED |
| B-11 | partners.html | /app/partners | B — List/Queue | All CRM roles | partners.read | GET /partners | APPROVED |

### Archetype C — Entity Detail / 360 View (12 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| C-01 | leads-detail.html | /app/leads/:lead_id | C — Entity Detail | All CRM roles | leads.read, leads.update, leads.assign | GET /leads/:id, PATCH /leads/:id, GET /leads/:id/next-action, GET /followups/lead/:id/canonical | APPROVED |
| C-02 | contacts-detail.html | /app/contacts/:contact_id/360 | C — Entity Detail | All CRM roles | contacts.read, contacts.update (delete: SD-001 hidden) | GET /contacts/:id, PATCH /contacts/:id, GET /cases, GET /leads | APPROVED |
| C-03 | accounts-detail.html | /app/accounts/:account_id | C — Entity Detail | All CRM roles | accounts.read, accounts.update | GET /accounts/:id, GET /contacts, GET /opportunities, GET /invoice-summaries | APPROVED |
| C-04 | opportunities-detail.html | /app/opportunities/:opportunity_id | C — Entity Detail | All CRM roles | opportunities.read, opportunities.update, opportunities.close (manager+) | GET /opportunities/:id, PATCH /opportunities/:id, GET /opportunities/:id/line-items | APPROVED |
| C-05 | cases-detail.html | /app/support/cases/:case_id | C — Entity Detail | All CRM roles (write: agent+) | cases.read, cases.update, cases.assign, cases.close (manager+), cases.escalate (manager+) | GET /cases/:id, POST /cases/:id/assign, POST /cases/:id/comments, POST /cases/:id/resolve, POST /cases/:id/close, POST /cases/:id/escalate, POST /cases/:id/reopen, POST /cases/:id/link-article | APPROVED |
| C-06 | quotes-detail.html | /app/sales/quotes/:quote_id | C — Entity Detail | All CRM roles | quotes.read, quotes.approve (manager+), quotes.convert_to_order (manager+) | GET /quotes/:id, PATCH /quotes/:id, POST /quotes/:id/accept | APPROVED |
| C-07 | orders-detail.html | /app/sales/orders/:order_id | C — Entity Detail | All CRM roles | orders.read, orders.fulfil (manager+) | GET /orders/:id | APPROVED |
| C-08 | invoices-detail.html | /app/finance/invoices/:invoice_id | C — Entity Detail | All CRM roles | collections.read, collections.record_payment (agent+), collections.reconcile (manager+) | GET /invoice-summaries/:id, POST /payments (STUB), POST /collections/:id/reconcile | APPROVED |
| C-09 | subscriptions-detail.html | /app/finance/subscriptions/:subscription_id | C — Entity Detail | manager, tenant_admin, tenant_owner | collections.read, admin.system_config (pause/cancel) | GET /subscriptions/:id | APPROVED |
| C-10 | workflow-run-detail.html | /app/workflows/runs/:execution_id | C — Entity Detail | manager, tenant_admin, tenant_owner | workflows.read | GET /workflows/runs/:id, POST /workflows/:id/retry | APPROVED |
| C-11 | partners-detail.html | /app/partners/:partner_id | C — Entity Detail | All CRM roles | partners.read, partners.update (admin) | GET /partners/:id | APPROVED |
| C-12 | knowledge-article.html | /app/support/knowledge/:article_id | C — Entity Detail | All CRM roles (edit/publish: manager+) | knowledge.read, knowledge.update (manager+), knowledge.publish (manager+) | GET /knowledge/:id, PATCH /knowledge/:id, POST /knowledge/:id/publish | APPROVED |

### Archetype D — Sales Cockpit (1 page)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| D-01 | sales-cockpit.html | /app/sales/cockpit | D — Sales Cockpit | agent, manager, tenant_admin | opportunities.read, leads.read, ai.view_scores, ai.view_forecasts | GET /opportunities, GET /leads, GET /forecasts, GET /ai/copilot/suggestions | APPROVED |

### Archetype E — Support Console (1 page)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| E-01 | support-console.html | /app/support/console | E — Support Console | agent, manager, tenant_admin | cases.read, cases.assign, inbox.read, inbox.claim | GET /cases, GET /support/queues, POST /cases/:id/assign, POST /cases/:id/escalate | APPROVED |

### Archetype F — Marketing Workspace (1 page)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| F-01 | marketing-workspace.html | /app/marketing/campaigns | F — Marketing | manager, tenant_admin, tenant_owner | campaigns.read, campaigns.create, campaigns.activate | GET /campaigns | APPROVED |

### Archetype G — Settings / Admin / RBAC (9 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| G-01 | org-settings.html | /app/settings/org | G — Settings/Admin | tenant_admin, tenant_owner | admin.system_config | GET /admin/settings, PATCH /admin/settings | APPROVED |
| G-02 | user-management-crm.html | /app/admin/users/manage | G — Settings/Admin | tenant_admin, tenant_owner | admin.manage_users, admin.manage_roles | GET /admin/users, POST /admin/users/invite, PATCH /admin/users/:id | APPROVED |
| G-03 | roles.html | /app/admin/roles | G — Settings/Admin | tenant_admin, tenant_owner | admin.manage_roles | GET /admin/roles, POST /admin/roles, PATCH /admin/roles/:id, DELETE /admin/roles/:id | APPROVED |
| G-04 | billing-settings.html | /app/settings/billing | G — Settings/Admin | tenant_admin, tenant_owner | admin.system_config | GET /billing/subscription, GET /billing/invoices | APPROVED (SD-002 stub) |
| G-05 | integrations.html | /app/settings/integrations | G — Settings/Admin | tenant_admin, tenant_owner | admin.system_config | GET /integrations, POST /integrations/:provider/test | APPROVED |
| G-06 | notifications.html | /app/settings/notifications | G — Settings/Admin | tenant_admin, tenant_owner | admin.system_config, notifications.send | GET /admin/settings, PATCH /admin/settings | APPROVED (SD-004 EN only) |
| G-07 | feature-flags.html | /app/admin/feature-flags | G — Settings/Admin | tenant_owner only | admin.manage_feature_flags | GET /feature-flags, PATCH /feature-flags/:id | APPROVED |
| G-08 | compliance.html | /app/settings/compliance | G — Settings/Admin | tenant_admin, tenant_owner | admin.system_config, admin.export_compliance_data | GET /governance/retention, PATCH /governance/retention | APPROVED |
| G-09 | territories.html | /app/admin/territories | G — Settings/Admin | manager, tenant_admin, tenant_owner | territories.read, territories.create, territories.update, territories.assign | GET /territories, POST /territories, PATCH /territories/:id, DELETE /territories/:id | APPROVED |

### Archetype H — Reporting / Analytics (7 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| H-01 | sales-analytics.html | /app/reports/sales | H — Reporting | All CRM roles | analytics.view_basic, analytics.view_advanced | GET /opportunities, GET /leads, GET /forecasts | APPROVED |
| H-02 | marketing-analytics.html | /app/reports/marketing | H — Reporting | All CRM roles | analytics.view_basic, campaigns.read | GET /campaigns | APPROVED |
| H-03 | support-analytics.html | /app/reports/support | H — Reporting | All CRM roles | analytics.view_basic, cases.read | GET /cases | APPROVED |
| H-04 | finance-analytics.html | /app/reports/finance | H — Reporting | All CRM roles | analytics.view_basic, collections.view_overdue | GET /invoice-summaries, GET /collections | APPROVED |
| H-05 | workflow-analytics.html | /app/reports/workflows | H — Reporting | manager, tenant_admin, tenant_owner | analytics.view_basic, workflows.read | GET /workflows/runs | APPROVED |
| H-06 | audit-report.html | /app/reports/audit | H — Reporting | tenant_admin, tenant_owner | admin.read_audit_logs, admin.export_compliance_data | GET /admin/audit-logs | APPROVED |
| H-07 | report-builder.html | /app/reports/builder | H — Reporting | All CRM roles | analytics.view_basic, analytics.view_advanced, analytics.export | POST /reports/execute, POST /reports/definitions, GET /reports/definitions | APPROVED |

### Archetype I — Form / Wizard / CPQ (6 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| I-01 | lead-new.html | /app/leads/new | I — Form/Wizard | agent, manager, tenant_admin, tenant_owner | leads.create | POST /leads | APPROVED |
| I-02 | contact-new.html | /app/contacts/new | I — Form/Wizard | agent, manager, tenant_admin, tenant_owner | contacts.create | POST /contacts | APPROVED |
| I-03 | opportunity-new.html | /app/opportunities/new | I — Form/Wizard | agent, manager, tenant_admin, tenant_owner | opportunities.create | POST /opportunities | APPROVED |
| I-04 | case-new.html | /app/support/cases/new | I — Form/Wizard | agent, manager, tenant_admin, tenant_owner | cases.create | POST /cases, GET /contacts, GET /support/queues | APPROVED |
| I-05 | quote-builder.html | /app/sales/quotes/new | I — Form/Wizard | manager, tenant_admin, tenant_owner | quotes.create, quotes.approve | POST /quotes | APPROVED |
| I-06 | campaign-new.html | /app/marketing/campaigns/new | I — Form/Wizard | manager, tenant_admin, tenant_owner | campaigns.create, campaigns.activate | POST /campaigns, GET /segments | APPROVED |

### Archetype J — Audit / Compliance (5 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| J-01 | audit-log.html | /app/audit | J — Audit/Compliance | tenant_admin, tenant_owner | admin.read_audit_logs | GET /admin/audit-logs | APPROVED |
| J-02 | compliance-report.html | /app/compliance | J — Audit/Compliance | tenant_admin, tenant_owner | admin.export_compliance_data | GET /admin/audit-logs | APPROVED |
| J-03 | data-governance.html | /app/admin/governance | J — Audit/Compliance | tenant_admin, tenant_owner | admin.system_config | GET /governance/classification, GET /governance/retention, GET /governance/sar, GET /privacy/consent, POST /governance/sar | APPROVED |
| J-04 | rbac-audit.html | /app/admin/rbac-audit | J — Audit/Compliance | tenant_admin, tenant_owner | admin.read_audit_logs | GET /admin/users | APPROVED |
| J-05 | privacy.html | /app/settings/privacy | J — Audit/Compliance | tenant_admin, tenant_owner | admin.system_config, admin.export_compliance_data | GET /privacy/consent, GET /governance/sar, POST /governance/sar | APPROVED |

### Archetype K — Builder / Visual Canvas (4 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| K-01 | workflow-builder.html | /app/workflows/builder | K — Builder/Canvas | manager, tenant_admin, tenant_owner | workflows.create, workflows.update, workflows.publish | GET /workflows, POST /workflows, PATCH /workflows/:id, POST /workflows/:id/publish, POST /workflows/:id/simulate | APPROVED |
| K-02 | object-builder.html | /app/admin/objects | K — Builder/Canvas | tenant_admin, tenant_owner | admin.system_config | Advisory shell only (SD-009 — D-002 unresolved) | APPROVED (advisory shell) |
| K-03 | rule-builder.html | /app/admin/rules | K — Builder/Canvas | tenant_admin, tenant_owner | admin.system_config | Visual canvas — no live API confirmed | APPROVED (visual canvas) |
| K-04 | approval-lanes.html | /app/sales/approval-lanes | K — Builder/Canvas | manager, tenant_admin, tenant_owner | quotes.read, quotes.approve | GET /quotes | APPROVED |

### Archetype L — Inbox / Communication (3 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| L-01 | inbox.html | /app/inbox | L — Inbox/Comms | agent, manager, tenant_admin | inbox.read | GET /inbox/conversations, PATCH /inbox/presence | APPROVED |
| L-02 | inbox-thread.html | /app/inbox/:thread_id | L — Inbox/Comms | agent, manager, tenant_admin | inbox.read, inbox.claim, inbox.handoff (manager+) | GET /inbox/conversations/:id, POST /inbox/conversations/:id/claim, POST /inbox/conversations/:id/messages, POST /inbox/conversations/:id/handoff | APPROVED |
| L-03 | routing-config.html | /app/admin/routing | L — Inbox/Comms | manager, tenant_admin, tenant_owner | inbox.supervise, inbox.admin | GET /inbox/queues, POST /inbox/queues, PATCH /inbox/queues/:id, GET /inbox/presence | APPROVED |

### Archetype M — AI / Copilot (2 pages)

| ID | File | Route | Archetype | Roles Permitted | Key Permissions | Primary API(s) | Status |
|---|---|---|---|---|---|---|---|
| M-01 | ai-copilot.html | /app/ai/copilot | M — AI/Copilot | All CRM roles | ai.view_scores, ai.score_leads | GET /ai/copilot/suggestions, GET /ai/scores/leads, POST /ai/scores/leads/:id/recompute, GET /ai/copilot/chat | APPROVED (SD-003 rule-based) |
| M-02 | ai-insights.html | /app/ai/insights | M — AI/Copilot | manager, tenant_admin, tenant_owner | ai.view_scores, ai.view_forecasts, ai.generate_forecasts | GET /ai/scores/leads, GET /ai/predictions/churn, GET /ai/estimates/clv, GET /ai/models | APPROVED (SD-003 rule-based) |

---

## Section 3 — Approved Dashboards

All 13 Archetype A dashboards are approved. Each follows the 5-zone layout: posture strip → primary KPI cards → execution queue → trend chart → risk/anomaly panel.

| ID | File | Route | Target Role(s) | Key Widgets | Data Sources | Status |
|---|---|---|---|---|---|---|
| A-01 | dashboard.html | /app/dashboard | All roles (primary: tenant_owner, tenant_admin, manager) | Follow-up compliance %, Idle leads, Pipeline value (PKR), Open opportunities, Deals at risk, Follow-up overdue | GET /followups, GET /leads, GET /opportunities, GET /forecasts, GET /ai/copilot/suggestions | APPROVED |
| A-02 | leads-dashboard.html | /app/sales/leads/dashboard | All CRM roles | Total active leads, New this week, Stage distribution, Conversion rate, Avg time in stage | GET /leads, GET /followups | APPROVED |
| A-03 | contacts-health.html | /app/contacts/health | manager, tenant_admin | Total contacts, Avg completeness score, Contacts with open cases, Idle contacts 30d, Missing phone | GET /contacts, GET /cases | APPROVED |
| A-04 | sales-dashboard.html | /app/sales/dashboard | manager, tenant_admin, tenant_owner | Weighted pipeline (PKR), Commit forecast, Win rate MTD, Avg deal size (PKR), Pipeline velocity | GET /opportunities, GET /forecasts | APPROVED |
| A-05 | quotes-dashboard.html | /app/sales/quotes/dashboard | manager, tenant_admin, tenant_owner | Pending approvals, Total value pending (PKR), Approved this week, Avg discount | GET /quotes | APPROVED |
| A-06 | subscriptions-dashboard.html | /app/finance/subscriptions/dashboard | manager, tenant_admin, tenant_owner | MRR (PKR), ARR (PKR), Churn rate MTD, Renewal rate 90d, Delinquent count | GET /subscriptions | APPROVED |
| A-07 | support-dashboard.html | /app/support/dashboard | manager, tenant_admin | Active SLA breaches, At-risk cases, Resolution time avg, CSAT score, Cases closed today | GET /cases | APPROVED |
| A-08 | engagement-dashboard.html | /app/marketing/engagement | manager, tenant_admin, tenant_owner | Delivery rate, Open rate, Reply rate, WhatsApp opt-in rate, Active campaigns | GET /communications/engagement, GET /campaigns | APPROVED |
| A-09 | knowledge-dashboard.html | /app/support/knowledge/dashboard | manager, tenant_admin | Total articles published, Deflection rate, Stale articles, Articles linked to cases | GET /knowledge | APPROVED |
| A-10 | workflows-dashboard.html | /app/workflows/dashboard | manager, tenant_admin, tenant_owner | Total executions 7d, Success rate, Failed count, Avg execution time, Active workflows | GET /workflows, GET /workflows/runs | APPROVED |
| A-11 | tenants-dashboard.html | /app/admin/tenants | tenant_owner only | Total tenants, Active tenants 90d, Entitlements at limit, Revenue (PKR) | GET /admin/tenants | APPROVED |
| A-12 | identity-dashboard.html | /app/admin/identity | tenant_admin, tenant_owner | Total users, Active users 7d, Suspended users, Role distribution, Escalation events 30d | GET /admin/users, GET /admin/audit-logs | APPROVED |
| A-13 | audit-dashboard.html | /app/admin/audit/dashboard | tenant_admin, tenant_owner | Total events 24h, Allow events, Deny events, Warn events, Deny rate | GET /admin/audit-logs | APPROVED |

---

## Section 4 — Approved Navigation Groups

Full sidebar navigation injected by crm-shell.js. Pages must NOT contain their own aside elements.

| # | Item | Route | Roles Visible | Type |
|---|---|---|---|---|
| 1 | Dashboard | /app/dashboard | All roles | Direct link |
| 2 | Follow-ups | /app/followups | All roles | Direct link |
| 3 | Leads | /app/leads | All roles | Direct link |
| 4 | Contacts | /app/contacts | All roles | Direct link |
| 5 | Accounts | /app/accounts | All roles | Direct link |
| 6 | Collections | /app/collections | All roles | Direct link |
| 7 | Sales | (sub-menu) | All roles | Sub-menu |
| 8 | Finance | (sub-menu) | All roles | Sub-menu |
| 9 | Support | (sub-menu) | agent+ | Sub-menu |
| 10 | Inbox | /app/inbox | agent+ | Direct link |
| 11 | Marketing | (sub-menu) | manager+ | Sub-menu |
| 12 | Workflows | (sub-menu) | manager+ | Sub-menu |
| 13 | Partners | /app/partners | All roles | Direct link |
| 14 | AI | (sub-menu) | All roles | Sub-menu |
| 15 | Reports | (sub-menu) | All roles | Sub-menu |
| 16 | Activity | /app/activity | All roles | Direct link |
| 17 | Tasks | /app/tasks | All roles | Direct link |
| 18 | Admin | (sub-menu) | tenant_admin, tenant_owner | Sub-menu |
| 19 | Settings | (sub-menu) | tenant_admin, tenant_owner | Sub-menu |

**Role visibility rule:** Admin and Settings sub-menus hidden for manager, agent, analyst. "Tenants" item within Admin hidden for all except tenant_owner. "Feature Flags" item within Admin hidden for all except tenant_owner.

Status: APPROVED

---

## Section 5 — Approved Roles (Canonical 7)

Source: backend/gateway/config/rbac-scopes.js ROLE_SCOPES mapping.

| Role | Display Name | Scope Summary | Exclusive Access | Status |
|---|---|---|---|---|
| tenant_owner | Tenant Owner | All 91 scopes. Full access to all 75 pages including admin.manage_tenants and admin.manage_feature_flags. | tenants-dashboard.html (A-11), feature-flags.html (G-07), "Tenants" nav item | APPROVED |
| tenant_admin | Tenant Admin | 35 scopes. All domain entity scopes + admin scopes except admin.manage_tenants and admin.manage_feature_flags. Access to 73 of 75 pages. | Admin sub-menu (except Tenants and Feature Flags), Settings sub-menu, all audit/compliance pages | APPROVED |
| manager | Manager | 25 scopes. Manages teams, reviews pipelines, approves workflows. Access to core CRM + analytics + team management. Cannot access Settings/Admin sub-menus except Territories and Routing. | Quote approval, case close/escalate, opportunity close, campaign management, workflow management | APPROVED |
| agent | Agent | 12 scopes. Standard CRM agent — leads, contacts, cases, inbox. Limited to core operational pages. Cannot access analytics, admin, finance, or marketing. | Inbox claim (max 10 concurrent), case creation, lead creation | APPROVED |
| analyst | Analyst | Read-only across leads, contacts, accounts, collections, payments, cases, knowledge + AI scores/predictions. Observer/reporting role only. No write access anywhere. | Read-only view of accessible entity pages | APPROVED |
| auditor | Auditor | Audit log and compliance read access. admin.read_audit_logs scope. Limited to J-series and H-06 pages. | Audit pages only (J-01, J-02, H-06, A-13) | APPROVED |
| integration_service | Integration Service | Machine-to-machine scope set. Not a human-facing role. No frontend pages assigned. | API access only (no UI) | APPROVED |

Status: APPROVED

---

## Section 6 — Approved Workflows (10)

### Primary Workflows (5)

| ID | Name | Entry Screen | Exit Screen | Roles | Status |
|---|---|---|---|---|---|
| WF-A | Lead-to-Deal | lead-new.html (I-01) or leads.html (B-02) | invoices-detail.html (C-08) | agent (steps 1–6), manager+ (all steps) | APPROVED |
| WF-B | Deal-to-Invoice | orders-detail.html (C-07) | invoices-detail.html (C-08) with status=paid | manager+ (invoice), agent (collections), system (webhooks) | APPROVED |
| WF-C | Case Lifecycle | case-new.html (I-04) | cases-detail.html (C-05) with status=CLOSED | agent (create, comment), manager (resolve), manager+ (close, escalate) | APPROVED |
| WF-D | WhatsApp Conversation | inbox.html (L-01) | inbox-thread.html (L-02) with state=resolved | agent (claim, respond), manager+ (handoff), system (routing) | APPROVED |
| WF-E | Payment Collection | invoices.html (B-09) (overdue row) | invoices-detail.html (C-08) with status=paid | agent (queue), manager+ (reconcile), system (auto-reminder) | APPROVED |

### System Workflows (5)

| ID | workflow_key | Trigger | Primary Frontend Surfaces | Status |
|---|---|---|---|---|
| WF-001 | lead_followup_enforcement | lead.idle.v1 | followups.html (B-01), leads-detail.html (C-01), workflows-dashboard.html (A-10) | APPROVED |
| WF-002 | collections_reminder | invoice.overdue.v1 | collections.html (B-08), invoices.html (B-09), workflows-dashboard.html (A-10) | APPROVED |
| WF-003 | sla_breach_notify | case.sla.breached.v1 + case.sla.first_response_breached.v1 | cases-detail.html (C-05), support-console.html (E-01), support-dashboard.html (A-07) | APPROVED |
| WF-004 | lead_assignment | lead.created.v1 | leads-detail.html (C-01) owner_id, territories.html (G-09) config | APPROVED |
| WF-005 | opportunity_stage_notify | opportunity.stage.changed.v1 | opportunities-detail.html (C-04), sales-dashboard.html (A-04), workflows-dashboard.html (A-10) | APPROVED |

---

## Section 7 — Approved Safe Defaults

All 12 safe defaults from SAFE_DEFAULT_REGISTER.md. Frontend behavior column states what each means for UI.

| ID | Title | Frontend Behavior |
|---|---|---|
| SD-001 | contacts.delete RBAC scope missing | Hide delete button on contacts.html (B-03) and contacts-detail.html (C-02) for ALL roles. Document: "Delete not available — OA-001 pending scope grant." Handle 403 gracefully on DELETE /contacts/:id. |
| SD-002 | JazzCash/Easypaisa payment UI blocked (P-016) | Display stub state on billing-settings.html (G-04), invoices-detail.html (C-08), collections.html (B-08). Document: "Payment processing stub — P-016 pending credentials." JazzCash/Easypaisa payment buttons visible but show stub confirmation. |
| SD-003 | AI features rule-based only (AI-001) | Display "Rule-based advisory — LLM inference deferred to C7" banner on ai-copilot.html (M-01) and ai-insights.html (M-02). All suggestions reference observed data only. |
| SD-004 | Notification strings EN only (P-017) | notifications.html (G-06): display EN strings only. Urdu strings exist with UR_TODO: markers but are blocked. RTL CSS is built and ready. |
| SD-005 | Facebook/Instagram lead capture hidden (MR-001) | lead-new.html (I-01): Facebook/Instagram source option hidden with data-unblock="MR-001". Not visible in UI. |
| SD-006 | Voice note transcription disabled | inbox-thread.html (L-02): microphone/transcription icon disabled with visual disabled state. MR-003 pending. |
| SD-007 | Contracts page not in C6 scope (OOS-001) | No contracts page exists. No frontend routing for contracts. Deferred to C7. Do not build. |
| SD-008 | Kuickpay payment rail hidden | billing-settings.html (G-04): Kuickpay option hidden with data-unblock="MR-007". Not visible in UI. |
| SD-009 | Custom objects routing advisory shell only (D-002) | object-builder.html (K-02): advisory visual shell only. No live API calls. Document: "Custom object routing — D-002 pending gateway confirmation." |
| SD-010 | JWT logout does not revoke refresh token | Auth flow: note that refresh token remains valid 7 days post-logout. No UX change — security note only for auth contract documentation. |
| SD-011 | Password hashing SHA-256 for C6 | Auth flow: note SHA-256 used for C6. Bcrypt migration deferred to C7. No UX impact. Compliance note in auth documentation. |
| SD-012 | PTA/FBR compliance hooks built, legal review pending | WhatsApp campaigns (I-06), invoices: compliance hooks wired in adapters. Display compliance notes in UI where applicable. PTA approval pending before production activation. |

---

## Section 8 — Approved Frontend States

Every screen must handle all four states. Standard patterns approved for all 75 custom pages.

| State | Pattern | Required Elements |
|---|---|---|
| Loading | Skeleton cards/rows while API responds | Skeleton UI placeholders matching the live layout. No spinner-only — use skeleton cards that mirror the final card structure. |
| Empty | Descriptive message + primary action button | Empty state illustration (optional), clear message explaining why it is empty, primary CTA button (e.g. "Add First Lead", "Create Campaign"). |
| Error | User-friendly message + retry option | "Something went wrong" message, retry button, graceful fallback to crm-dummy.js data where applicable. Never expose raw API error messages. |
| Success | Live data rendered | KPI tiles, DataTables, charts fully populated from API response. 403 on permission-gated elements handled by hiding the control (not showing an error). |

**403 Handling Rule:** A 403 response on a permission-gated action must result in the UI hiding/disabling the control — not showing an error modal. The server is always the authority; frontend hides controls as a UX convenience.

---

## Section 9 — Blocked / Excluded Items

Items the frontend must NOT show, build, or activate for C6.

| Item | Reason | Safe Default | Unblock Condition |
|---|---|---|---|
| contacts.delete button | contacts.delete scope absent from rbac-scopes.js SCOPES constant — 403 for ALL roles | SD-001: hide for all roles | OA-001 owner confirmation + code change |
| JazzCash/Easypaisa live payment flow | P-016: merchant credentials not obtained | SD-002: show STUB state | OA-003 true owner decision (obtain credentials) |
| Easypaisa live webhook | P-016: same as above | SD-002 | OA-003 |
| Kuickpay payment rail | MR-007: not in scope | SD-008: hidden with data-unblock="MR-007" | Separate market research decision |
| Facebook/Instagram lead capture | MR-001: Meta Business Manager setup pending | SD-005: hidden with data-unblock="MR-001" | MR-001 resolution |
| Voice note transcription (inbox) | MR-003: pending vendor evaluation | SD-006: microphone icon disabled | MR-003 resolution |
| LLM AI inference | OA-004: AI model unselected for C6 | SD-003: rule-based advisory only | C7 AI sprint |
| Contracts module pages | OA-005 resolved: defer to C7 | SD-007: no page exists | C7 — requires v1-contracts.routes.js first |
| Urdu campaign templates | P-017: native speaker review pending | SD-004: EN strings only | P-017 review completion |
| Custom objects live API | D-002: gateway route unconfirmed | SD-009: K-02 advisory shell only | D-002 gateway route confirmation |

---

## Section 10 — Remaining Owner Confirmations

Based on PRODUCT_DECISION_REGISTER.md and FRONTEND_GAP_REGISTER.md:

| ID | Decision | Frontend Impact | Current Frontend State |
|---|---|---|---|
| OA-001 | contacts.delete RBAC code fix (2-line change in rbac-scopes.js) | When resolved: show delete button for tenant_admin and tenant_owner only | SD-001 in effect: delete hidden for all roles |
| OA-003 | JazzCash/Easypaisa credentials (TRUE_OWNER_DECISION — external vendor relationship) | When resolved: activate live payment form in G-04 and C-08 | SD-002 in effect: stub state displayed |

All other OA items (OA-002, OA-004 through OA-009) have zero frontend impact.

**Frontend action for OA-001:** Build delete button in contacts-detail.html (C-02) with scope-gated visibility (contacts.delete), hidden by default via SD-001 documentation. When OA-001 is resolved and code is deployed, the button becomes visible to tenant_admin and tenant_owner without any frontend HTML changes — only the JWT will now contain the scope.

---

## Freeze Verdict

**L0 FROZEN**

Basis:
1. FRONTEND_GAP_REGISTER.md conclusion: "There are no gaps that block Frontend Authority Capture."
2. DETERMINISM_CERTIFICATION_REPORT.md verdict: "REPOSITORY FULLY DETERMINED"
3. POST_COLLAPSE_FRONTEND_READINESS.md verdict: "GO — Frontend Authority Capture may begin immediately and without restriction."
4. 0 blocking gaps against 75 custom C6 pages.
5. All identified gaps are documented production constraints (safe defaults), post-C6 work items, or minor clarifications.
6. The one TRUE_OWNER_DECISION (OA-003) is isolated to a stub state that is already documented and built.

All 75 custom pages are fully specified. All 94 library pages are categorised. All 10 workflows are mapped to screens. All 7 roles are specified. All 91 permission scopes are mapped to UI elements. All 228 API endpoints are mapped to frontend consumers.

---

*End L0_FRONTEND_AUTHORITY_INPUT_FREEZE.md*
*Pakistan CRM OS — Phase C6 — L0 FROZEN — 2026-06-24*
