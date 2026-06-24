---
Status: L0 FROZEN
Authority Level: Critical
Freeze Date: 2026-06-24
Phase: C6 (Commercial Launch)
Derived From: FRONTEND_ROUTE_CATALOG.md, FRONTEND_SCREEN_CATALOG.md, FRONTEND_WORKFLOW_TO_SCREEN_MAP.md,
  FRONTEND_API_DEPENDENCY_MAP.md, FRONTEND_PERMISSION_MATRIX.md, DESIGN-SPEC.md
---

# L0 ROUTE-SCREEN-WORKFLOW MATRIX — Pakistan CRM OS

Complete cross-reference: every route × screen × module × archetype × workflows × APIs × roles × permissions × phase.

**Use this as the single reference for any page's full context.**
**Total: 169 pages (75 custom + 94 library)**

---

## PART 1 — Custom CRM Pages (75 pages)

### How to Read This Table
- **Workflows Supported**: WF-A through WF-E (primary) or WF-001 through WF-005 (system). "—" means no primary workflow but page may appear in system workflow monitoring.
- **Phase**: Build phase from DESIGN-SPEC.md. All phases are BUILT.
- **Freeze Status**: FROZEN — inputs are locked; no new routes, screens, or APIs may be added for C6.

| Route | Screen Title | Module | Archetype | Workflows Supported | APIs Called | Roles | Key Permissions | Phase | Freeze Status |
|---|---|---|---|---|---|---|---|---|---|
| /app/dashboard | Owner / Sales Dashboard | Core | A — Dashboard/KPI | WF-A monitoring, WF-001 monitoring | GET /leads, GET /opportunities, GET /forecasts, GET /ai/copilot/suggestions | All roles | leads.read, opportunities.read, analytics.view_basic, ai.view_scores | Phase 1 | FROZEN |
| /app/followups | Follow-up Queue | Follow-up Enforcement | B — List/Queue | WF-001 (primary), WF-A steps 3+5 | GET /followups, POST /followups/:id/complete, POST /followups/:id/snooze | All roles | tasks.read, tasks.complete, tasks.update | Phase 1 | FROZEN |
| /app/leads | Lead Queue | Lead Management | B — List/Queue | WF-A entry, WF-001 monitoring | GET /leads, GET /leads/export | All roles | leads.read, leads.create, leads.assign | Phase 1 | FROZEN |
| /app/leads/:lead_id | Lead Detail | Lead Management | C — Entity Detail | WF-A steps 3–5, WF-001 | GET /leads/:id, PATCH /leads/:id, GET /leads/:id/next-action, GET /followups/lead/:id/canonical | All roles | leads.read, leads.update, leads.assign | Phase 1 | FROZEN |
| /app/leads/new | New Lead Form | Lead Management | I — Form/Wizard | WF-A step 1 (entry), triggers WF-004 | POST /leads | agent, manager, tenant_admin, tenant_owner | leads.create | Phase 1 | FROZEN |
| /app/sales/leads/dashboard | Lead Funnel Dashboard | Lead Management | A — Dashboard/KPI | WF-A stage monitoring | GET /leads, GET /followups | All roles | leads.read | Phase 2 | FROZEN |
| /app/contacts | Contact List | Contacts | B — List/Queue | WF-A step 1 (contact lookup), WF-C contact link | GET /contacts, GET /contacts/export, POST /contacts/import | All roles | contacts.read (delete: SD-001 hidden) | Phase 1 | FROZEN |
| /app/contacts/:contact_id/360 | Customer 360 | Contacts | C — Entity Detail | WF-A step 1, WF-C step 1 | GET /contacts/:id, PATCH /contacts/:id, GET /cases, GET /leads | All roles | contacts.read, contacts.update (delete: SD-001 hidden) | Phase 8 | FROZEN |
| /app/contacts/new | New Contact Form | Contacts | I — Form/Wizard | WF-A step 1 (new contact) | POST /contacts | agent, manager, tenant_admin, tenant_owner | contacts.create | Phase 8 | FROZEN |
| /app/contacts/health | Customer Health Dashboard | Contacts | A — Dashboard/KPI | Contact health monitoring | GET /contacts, GET /cases | manager, tenant_admin | contacts.read, cases.read | Phase 8 | FROZEN |
| /app/accounts | Account List | Accounts | B — List/Queue | Account lifecycle monitoring | GET /accounts | All roles | accounts.read | Phase 8 | FROZEN |
| /app/accounts/:account_id | Account Profile | Accounts | C — Entity Detail | Account lifecycle | GET /accounts/:id, GET /contacts, GET /opportunities, GET /invoice-summaries | All roles | accounts.read, accounts.update | Phase 8 | FROZEN |
| /app/opportunities/:opportunity_id | Opportunity Detail | Sales | C — Entity Detail | WF-A steps 6–9, WF-005 trigger | GET /opportunities/:id, PATCH /opportunities/:id, GET /opportunities/:id/line-items, GET /quotes | All roles | opportunities.read, opportunities.update, opportunities.close (manager+) | Phase 2 | FROZEN |
| /app/opportunities/new | New Opportunity Form | Sales | I — Form/Wizard | WF-A step 6 | POST /opportunities | agent, manager, tenant_admin, tenant_owner | opportunities.create | Phase 2 | FROZEN |
| /app/sales/cockpit | Sales Cockpit | Sales | D — Sales Cockpit | WF-A stage progression (6–9), WF-005 trigger | GET /opportunities, GET /leads, GET /forecasts, GET /ai/copilot/suggestions | agent, manager, tenant_admin | opportunities.read, leads.read, ai.view_scores, ai.view_forecasts | Phase 2 | FROZEN |
| /app/sales/dashboard | Opportunity Pipeline Dashboard | Sales | A — Dashboard/KPI | WF-005 monitoring | GET /opportunities, GET /forecasts | manager, tenant_admin, tenant_owner | opportunities.read, ai.view_forecasts | Phase 2 | FROZEN |
| /app/sales/quotes/new | CPQ Quote Builder | CPQ | I — Form/Wizard | WF-A step 7 (discount >10% triggers approval) | POST /quotes | manager, tenant_admin, tenant_owner | quotes.create, quotes.approve | Phase 2 | FROZEN |
| /app/sales/quotes/:quote_id | Quote Detail | CPQ | C — Entity Detail | WF-A step 8 (approval), step 9 (order creation) | GET /quotes/:id, PATCH /quotes/:id, POST /quotes/:id/accept | All roles | quotes.read, quotes.approve (manager+), quotes.convert_to_order (manager+) | Phase 2 | FROZEN |
| /app/sales/quotes/dashboard | Quote Approval Dashboard | CPQ | A — Dashboard/KPI | WF-A step 8 monitoring | GET /quotes | manager, tenant_admin, tenant_owner | quotes.read, quotes.approve | Phase 2 | FROZEN |
| /app/sales/orders/:order_id | Order Detail | CPQ | C — Entity Detail | WF-B step 1 (order from quote), step 2 (invoice link) | GET /orders/:id | All roles | orders.read, orders.fulfil (manager+) | Phase 8 | FROZEN |
| /app/collections | Collections Queue | Finance | B — List/Queue | WF-E (primary), WF-002 monitoring | GET /collections, POST /collections/:id/reconcile | All roles (write: agent+) | collections.read, collections.view_overdue, collections.reconcile | Phase 1 | FROZEN |
| /app/finance/invoices | Invoice Queue | Finance | B — List/Queue | WF-B step 2 monitoring, WF-B step 7 monitoring | GET /invoice-summaries | All roles | collections.read | Phase 3 | FROZEN |
| /app/finance/invoices/:invoice_id | Invoice Detail | Finance | C — Entity Detail | WF-B steps 4–7, WF-E steps 3–6 | GET /invoice-summaries/:id, POST /payments (STUB), POST /collections/:id/reconcile | All roles | collections.read, collections.record_payment (agent+), collections.reconcile (manager+) | Phase 3 | FROZEN |
| /app/reports/finance | Finance Analytics | Finance | H — Reporting | — | GET /invoice-summaries, GET /collections | All roles | analytics.view_basic, collections.view_overdue | Phase 3 | FROZEN |
| /app/finance/subscriptions/dashboard | Subscription Revenue Dashboard | Subscriptions | A — Dashboard/KPI | WF-E delinquent monitoring | GET /subscriptions | manager, tenant_admin, tenant_owner | analytics.view_basic, collections.view_overdue | Phase 3 | FROZEN |
| /app/finance/subscriptions/:subscription_id | Subscription Detail | Subscriptions | C — Entity Detail | WF-E (collections for past_due) | GET /subscriptions/:id | manager, tenant_admin, tenant_owner | collections.read, admin.system_config (pause/cancel) | Phase 3 | FROZEN |
| /app/settings/billing | Billing & Subscription Settings | Billing | G — Settings/Admin | — | GET /billing/subscription, GET /billing/invoices | tenant_admin, tenant_owner | admin.system_config | Phase 6 | FROZEN |
| /app/support/cases | Ticket / Case Queue | Support | B — List/Queue | WF-C steps 2–3 (queue routing + assignment) | GET /cases | All roles | cases.read, cases.create | Phase 4 | FROZEN |
| /app/support/cases/:case_id | Case / Ticket Detail | Support | C — Entity Detail | WF-C steps 3–11, WF-003 monitoring | GET /cases/:id, POST /cases/:id/assign, POST /cases/:id/comments, POST /cases/:id/resolve, POST /cases/:id/close, POST /cases/:id/escalate, POST /cases/:id/reopen, POST /cases/:id/link-article | All roles (write: agent+) | cases.read, cases.update, cases.assign, cases.close (manager+), cases.escalate (manager+) | Phase 4 | FROZEN |
| /app/support/cases/new | New Case Form | Support | I — Form/Wizard | WF-C step 1 | POST /cases, GET /contacts, GET /support/queues | agent, manager, tenant_admin, tenant_owner | cases.create | Phase 4 | FROZEN |
| /app/support/console | Support Console | Support | E — Support Console | WF-C steps 2–7, WF-003 monitoring | GET /cases, GET /support/queues, POST /cases/:id/assign, POST /cases/:id/escalate | agent, manager, tenant_admin | cases.read, cases.assign, inbox.read, inbox.claim | Phase 4 | FROZEN |
| /app/support/dashboard | Case SLA Operations Dashboard | Support | A — Dashboard/KPI | WF-C monitoring, WF-003 audit | GET /cases | manager, tenant_admin | cases.read, analytics.view_basic | Phase 4 | FROZEN |
| /app/support/knowledge/:article_id | Knowledge Article Detail | Knowledge Base | C — Entity Detail | WF-C step 8 (link to case) | GET /knowledge/:id, PATCH /knowledge/:id, POST /knowledge/:id/publish | All roles (edit/publish: manager+) | knowledge.read, knowledge.update (manager+), knowledge.publish (manager+) | Phase 4 | FROZEN |
| /app/support/knowledge/dashboard | Knowledge Effectiveness Dashboard | Knowledge Base | A — Dashboard/KPI | WF-C step 8 visibility | GET /knowledge | manager, tenant_admin | knowledge.read, analytics.view_basic | Phase 8 | FROZEN |
| /app/inbox | Omnichannel Inbox | Inbox | L — Inbox/Comms | WF-D steps 4–8 | GET /inbox/conversations, PATCH /inbox/presence | agent, manager, tenant_admin | inbox.read | Phase 5 | FROZEN |
| /app/inbox/:thread_id | Conversation Thread | Inbox | L — Inbox/Comms | WF-D steps 5–8 | GET /inbox/conversations/:id, POST /inbox/conversations/:id/claim, POST /inbox/conversations/:id/messages, POST /inbox/conversations/:id/handoff | agent, manager, tenant_admin | inbox.read, inbox.claim, inbox.handoff (manager+) | Phase 5 | FROZEN |
| /app/admin/routing | Routing Configuration | Inbox | L — Inbox/Comms | WF-D step 2 (config) | GET /inbox/queues, POST /inbox/queues, PATCH /inbox/queues/:id, GET /inbox/presence | manager, tenant_admin, tenant_owner | inbox.supervise, inbox.admin | Phase 8 | FROZEN |
| /app/marketing/campaigns | Marketing Workspace | Marketing | F — Marketing | Campaign lifecycle | GET /campaigns | manager, tenant_admin, tenant_owner | campaigns.read, campaigns.create, campaigns.activate | Phase 7 | FROZEN |
| /app/marketing/campaigns/new | Journey / Campaign Builder | Marketing | I — Form/Wizard | Campaign lifecycle | POST /campaigns, GET /segments | manager, tenant_admin, tenant_owner | campaigns.create, campaigns.activate | Phase 7 | FROZEN |
| /app/reports/marketing | Marketing Analytics | Marketing | H — Reporting | — | GET /campaigns | All roles | analytics.view_basic, campaigns.read | Phase 7 | FROZEN |
| /app/marketing/engagement | Communication Engagement Dashboard | Marketing | A — Dashboard/KPI | WF-D monitoring | GET /communications/engagement, GET /campaigns | All roles | campaigns.read, analytics.view_basic | Phase 5 | FROZEN |
| /app/workflows/builder | Workflow Builder | Workflows | K — Builder/Canvas | Custom workflow creation | GET /workflows, POST /workflows, PATCH /workflows/:id, POST /workflows/:id/publish, POST /workflows/:id/simulate | manager, tenant_admin, tenant_owner | workflows.create, workflows.update, workflows.publish | Phase 7 | FROZEN |
| /app/workflows/runs/:execution_id | Workflow Execution Detail | Workflows | C — Entity Detail | All system workflows monitoring | GET /workflows/runs/:id, POST /workflows/:id/retry | manager, tenant_admin, tenant_owner | workflows.read | Phase 8 | FROZEN |
| /app/workflows/dashboard | Workflow Automation Dashboard | Workflows | A — Dashboard/KPI | All 5 system workflows monitoring | GET /workflows, GET /workflows/runs | manager, tenant_admin, tenant_owner | workflows.read, analytics.view_basic | Phase 7 | FROZEN |
| /app/reports/workflows | Workflow Analytics | Workflows | H — Reporting | — | GET /workflows/runs | manager, tenant_admin, tenant_owner | analytics.view_basic, workflows.read | Phase 8 | FROZEN |
| /app/ai/copilot | AI Copilot Panel | AI | M — AI/Copilot | Advisory only (SD-003) | GET /ai/copilot/suggestions, GET /ai/scores/leads, POST /ai/scores/leads/:id/recompute, GET /ai/copilot/chat | All roles | ai.view_scores, ai.score_leads | Phase 8 | FROZEN |
| /app/ai/insights | AI Insights Dashboard | AI | M — AI/Copilot | Advisory only (SD-003) | GET /ai/scores/leads, GET /ai/predictions/churn, GET /ai/estimates/clv, GET /ai/models | manager, tenant_admin, tenant_owner | ai.view_scores, ai.view_forecasts, ai.generate_forecasts | Phase 8 | FROZEN |
| /app/admin/territories | Territory & Assignment Config | Territories | G — Settings/Admin | WF-004 config | GET /territories, POST /territories, PATCH /territories/:id, DELETE /territories/:id | manager, tenant_admin, tenant_owner | territories.read, territories.create, territories.update, territories.assign | Phase 6 | FROZEN |
| /app/partners | Partner List | Partners | B — List/Queue | Partner attribution | GET /partners | All roles | partners.read | Phase 8 | FROZEN |
| /app/partners/:partner_id | Partner Detail | Partners | C — Entity Detail | Partner attribution | GET /partners/:id | All roles | partners.read, partners.update (admin) | Phase 8 | FROZEN |
| /app/admin/users | User Directory | Identity | B — List/Queue | User lifecycle | GET /admin/users, PATCH /admin/users/:id, POST /admin/users/:id/reset-password | tenant_admin, tenant_owner | admin.manage_users | Phase 8 | FROZEN |
| /app/admin/users/manage | User Management | Identity | G — Settings/Admin | User lifecycle | GET /admin/users, POST /admin/users/invite, PATCH /admin/users/:id | tenant_admin, tenant_owner | admin.manage_users, admin.manage_roles | Phase 6 | FROZEN |
| /app/admin/identity | Identity & Access Posture Dashboard | Identity | A — Dashboard/KPI | RBAC audit monitoring | GET /admin/users, GET /admin/audit-logs | tenant_admin, tenant_owner | admin.read_audit_logs, admin.manage_users | Phase 8 | FROZEN |
| /app/audit | Audit Log | Audit | J — Audit/Compliance | Compliance monitoring | GET /admin/audit-logs | tenant_admin, tenant_owner | admin.read_audit_logs | Phase 8 | FROZEN |
| /app/compliance | Compliance Report | Audit | J — Audit/Compliance | Compliance monitoring | GET /admin/audit-logs | tenant_admin, tenant_owner | admin.export_compliance_data | Phase 8 | FROZEN |
| /app/admin/governance | Data Governance Console | Audit | J — Audit/Compliance | — | GET /governance/classification, GET /governance/retention, GET /governance/sar, GET /privacy/consent, POST /governance/sar | tenant_admin, tenant_owner | admin.system_config | Phase 8 | FROZEN |
| /app/admin/rbac-audit | RBAC Audit | Audit | J — Audit/Compliance | — | GET /admin/users | tenant_admin, tenant_owner | admin.read_audit_logs | Phase 8 | FROZEN |
| /app/settings/privacy | Consent & Privacy Manager | Audit | J — Audit/Compliance | — | GET /privacy/consent, GET /governance/sar, POST /governance/sar | tenant_admin, tenant_owner | admin.system_config, admin.export_compliance_data | Phase 8 | FROZEN |
| /app/admin/audit/dashboard | Platform Audit & Reliability Dashboard | Audit | A — Dashboard/KPI | Compliance monitoring | GET /admin/audit-logs | tenant_admin, tenant_owner | admin.read_audit_logs | Phase 8 | FROZEN |
| /app/reports/audit | Audit Report | Audit | H — Reporting | Compliance monitoring | GET /admin/audit-logs, GET /admin/audit-logs/export | tenant_admin, tenant_owner | admin.read_audit_logs, admin.export_compliance_data | Phase 8 | FROZEN |
| /app/settings/org | Organization Settings | Settings | G — Settings/Admin | — | GET /admin/settings, PATCH /admin/settings | tenant_admin, tenant_owner | admin.system_config | Phase 6 | FROZEN |
| /app/admin/roles | Role & Permission Editor | Settings | G — Settings/Admin | — | GET /admin/roles, POST /admin/roles, PATCH /admin/roles/:id, DELETE /admin/roles/:id | tenant_admin, tenant_owner | admin.manage_roles | Phase 6 | FROZEN |
| /app/settings/integrations | Integration Settings | Settings | G — Settings/Admin | WF-D provider config | GET /integrations, POST /integrations/:provider/test | tenant_admin, tenant_owner | admin.system_config | Phase 6 | FROZEN |
| /app/settings/notifications | Notification Settings | Settings | G — Settings/Admin | — | GET /admin/settings, PATCH /admin/settings | tenant_admin, tenant_owner | admin.system_config, notifications.send | Phase 6 | FROZEN |
| /app/admin/feature-flags | Feature Flags | Settings | G — Settings/Admin | — | GET /feature-flags, PATCH /feature-flags/:id | tenant_owner only | admin.manage_feature_flags | Phase 6 | FROZEN |
| /app/settings/compliance | Compliance Settings | Settings | G — Settings/Admin | — | GET /governance/retention, PATCH /governance/retention | tenant_admin, tenant_owner | admin.system_config, admin.export_compliance_data | Phase 6 | FROZEN |
| /app/admin/objects | Custom Object Layout Builder | Builder Tools | K — Builder/Canvas | — (advisory shell SD-009) | Advisory shell only — D-002 unresolved | tenant_admin, tenant_owner | admin.system_config | Phase 8 | FROZEN |
| /app/admin/rules | Rule / CPQ Logic Builder | Builder Tools | K — Builder/Canvas | WF-A step 7 (discount rule config) | Visual canvas — no live API confirmed | tenant_admin, tenant_owner | admin.system_config | Phase 8 | FROZEN |
| /app/sales/approval-lanes | CPQ Approval Lane Board | Builder Tools | K — Builder/Canvas | WF-A step 8 | GET /quotes | manager, tenant_admin, tenant_owner | quotes.read, quotes.approve | Phase 8 | FROZEN |
| /app/reports/builder | Custom Report Builder | Reports | H — Reporting | — | POST /reports/execute, POST /reports/definitions, GET /reports/definitions | All roles | analytics.view_basic, analytics.view_advanced, analytics.export | Phase 8 | FROZEN |
| /app/reports/sales | Sales Analytics | Reports | H — Reporting | — | GET /opportunities, GET /leads, GET /forecasts | All roles | analytics.view_basic, analytics.view_advanced | Phase 8 | FROZEN |
| /app/reports/support | Support Analytics | Reports | H — Reporting | — | GET /cases | All roles | analytics.view_basic, cases.read | Phase 8 | FROZEN |
| /app/admin/tenants | Tenant & Entitlement Dashboard | Tenant Admin | A — Dashboard/KPI | Tenant provisioning monitoring | GET /admin/tenants | tenant_owner only | admin.manage_tenants | Phase 8 | FROZEN |
| /app/activity | Activity Feed | Activity | B — List/Queue | Audit trail browsing | GET /activities | All roles | activities.read | Phase 8 | FROZEN |
| /app/tasks | Task Queue | Tasks | B — List/Queue | General task management | GET /tasks, PATCH /tasks/:id | All roles | tasks.read, tasks.complete, tasks.assign | Phase 8 | FROZEN |

---

## PART 2 — NexLink Library Pages (94 pages)

All entries are NexLink component demos. No custom CRM authority. No workflows. No permissions. Not in 75 custom page scope.

| File | Description | Freeze Status |
|---|---|---|
| accordion.html | Library — Bootstrap accordion component demo | FROZEN (library, no authority) |
| activities.html | Library — NexLink activities template demo (NOTE: NOT the same as activity.html B-06) | FROZEN (library, no authority) |
| alerts.html | Library — Bootstrap alerts component demo | FROZEN (library, no authority) |
| apexchart.html | Library — ApexCharts integration demo | FROZEN (library, no authority) |
| avatar.html | Library — Avatar component demo | FROZEN (library, no authority) |
| badge.html | Library — Badge component demo | FROZEN (library, no authority) |
| blog.html | Library — Blog page template | FROZEN (library, no authority) |
| blog-details.html | Library — Blog detail template | FROZEN (library, no authority) |
| blog-list.html | Library — Blog list template | FROZEN (library, no authority) |
| breadcrumb.html | Library — Breadcrumb component demo | FROZEN (library, no authority) |
| button-group.html | Library — Button group component demo | FROZEN (library, no authority) |
| buttons.html | Library — Button variants demo | FROZEN (library, no authority) |
| calendar.html | Library — Calendar component demo | FROZEN (library, no authority) |
| card.html | Library — Card component demo | FROZEN (library, no authority) |
| card-action.html | Library — Card action patterns demo | FROZEN (library, no authority) |
| carousel.html | Library — Carousel component demo | FROZEN (library, no authority) |
| chartjs.html | Library — Chart.js integration demo | FROZEN (library, no authority) |
| chat.html | Library — Chat UI template demo | FROZEN (library, no authority) |
| collapse.html | Library — Bootstrap collapse demo | FROZEN (library, no authority) |
| customers.html | Library — Customers template demo | FROZEN (library, no authority) |
| dashboard-rtl.html | Library — RTL dashboard demo | FROZEN (library, no authority) |
| deals.html | Library — Deals template demo | FROZEN (library, no authority) |
| drag-and-drop.html | Library — Drag and drop component demo | FROZEN (library, no authority) |
| dropdowns.html | Library — Dropdown component demo | FROZEN (library, no authority) |
| email-compose.html | Library — Email compose template | FROZEN (library, no authority) |
| email-read.html | Library — Email read template | FROZEN (library, no authority) |
| employee.html | Library — Employee template demo | FROZEN (library, no authority) |
| error-404.html | Library — 404 error page | FROZEN (library, no authority) |
| error-404-cover.html | Library — 404 cover variant | FROZEN (library, no authority) |
| error-404-full.html | Library — 404 full-page variant | FROZEN (library, no authority) |
| finance.html | Library — Finance template demo | FROZEN (library, no authority) |
| flaticon.html | Library — Flaticon icon library demo | FROZEN (library, no authority) |
| flatpickr.html | Library — Flatpickr date picker demo | FROZEN (library, no authority) |
| fontawesome.html | Library — Font Awesome icon library demo | FROZEN (library, no authority) |
| forgot-password-basic.html | Library — Forgot password basic template | FROZEN (library, no authority) |
| forgot-password-cover.html | Library — Forgot password cover template | FROZEN (library, no authority) |
| forgot-password-frame.html | Library — Forgot password frame template | FROZEN (library, no authority) |
| form-elements.html | Library — Form elements demo | FROZEN (library, no authority) |
| form-floating.html | Library — Floating label form demo | FROZEN (library, no authority) |
| form-input-group.html | Library — Input group demo | FROZEN (library, no authority) |
| form-layout.html | Library — Form layout demo | FROZEN (library, no authority) |
| form-validation.html | Library — Form validation demo | FROZEN (library, no authority) |
| inbox-email.html | Library — Email inbox template demo | FROZEN (library, no authority) |
| investment.html | Library — Investment template demo | FROZEN (library, no authority) |
| jsvectormap.html | Library — jsVectorMap integration demo | FROZEN (library, no authority) |
| leaflet.html | Library — Leaflet.js map integration demo | FROZEN (library, no authority) |
| list-group.html | Library — List group component demo | FROZEN (library, no authority) |
| login-basic.html | Library — Login basic template | FROZEN (library, no authority) |
| login-cover.html | Library — Login cover template | FROZEN (library, no authority) |
| login-frame.html | Library — Login frame template | FROZEN (library, no authority) |
| lucide.html | Library — Lucide icon library demo | FROZEN (library, no authority) |
| marketing.html | Library — Marketing template demo | FROZEN (library, no authority) |
| modal.html | Library — Modal component demo | FROZEN (library, no authority) |
| navbar.html | Library — Navbar component demo | FROZEN (library, no authority) |
| new-chat.html | Library — New chat template | FROZEN (library, no authority) |
| new-password-basic.html | Library — New password basic template | FROZEN (library, no authority) |
| new-password-cover.html | Library — New password cover template | FROZEN (library, no authority) |
| new-password-frame.html | Library — New password frame template | FROZEN (library, no authority) |
| new-project.html | Library — New project template | FROZEN (library, no authority) |
| offcanvas.html | Library — Offcanvas component demo | FROZEN (library, no authority) |
| pagination.html | Library — Pagination component demo | FROZEN (library, no authority) |
| plans.html | Library — Pricing plans template | FROZEN (library, no authority) |
| popovers.html | Library — Popover component demo | FROZEN (library, no authority) |
| pricing.html | Library — Pricing page template | FROZEN (library, no authority) |
| profile.html | Library — User profile template | FROZEN (library, no authority) |
| progress.html | Library — Progress bar component demo | FROZEN (library, no authority) |
| register-basic.html | Library — Registration basic template | FROZEN (library, no authority) |
| register-cover.html | Library — Registration cover template | FROZEN (library, no authority) |
| register-frame.html | Library — Registration frame template | FROZEN (library, no authority) |
| review.html | Library — Review template demo | FROZEN (library, no authority) |
| sales.html | Library — Sales template demo | FROZEN (library, no authority) |
| scrollspy.html | Library — Scrollspy component demo | FROZEN (library, no authority) |
| search-apps.html | Library — Search apps template | FROZEN (library, no authority) |
| search-apps-details.html | Library — Search apps detail template | FROZEN (library, no authority) |
| search-chat.html | Library — Search chat template | FROZEN (library, no authority) |
| search-image.html | Library — Search image template | FROZEN (library, no authority) |
| settings.html | Library — Settings template demo | FROZEN (library, no authority) |
| simplebar.html | Library — Simplebar scroll demo | FROZEN (library, no authority) |
| spinners.html | Library — Spinner component demo | FROZEN (library, no authority) |
| swiper.html | Library — Swiper carousel demo | FROZEN (library, no authority) |
| tables-basic.html | Library — Basic tables demo | FROZEN (library, no authority) |
| tables-datatable.html | Library — DataTables demo | FROZEN (library, no authority) |
| tabs.html | Library — Tab component demo | FROZEN (library, no authority) |
| tagify.html | Library — Tagify input demo | FROZEN (library, no authority) |
| task-management.html | Library — Task management template | FROZEN (library, no authority) |
| team-management.html | Library — Team management template | FROZEN (library, no authority) |
| toasts.html | Library — Toast notification demo | FROZEN (library, no authority) |
| tooltips.html | Library — Tooltip component demo | FROZEN (library, no authority) |
| typography.html | Library — Typography demo | FROZEN (library, no authority) |
| under-construction.html | Library — Under construction page | FROZEN (library, no authority) |
| under-construction-cover.html | Library — Under construction cover variant | FROZEN (library, no authority) |
| under-construction-full.html | Library — Under construction full-page variant | FROZEN (library, no authority) |
| user-management.html | Library — User management template demo | FROZEN (library, no authority) |
| your-chat.html | Library — Chat template demo | FROZEN (library, no authority) |

---

## Important Disambiguations

**activities.html vs activity.html:** Two files with similar names. `activities.html` is a NexLink library demo (no custom authority). `activity.html` is B-06 (Activity Feed) at /app/activity — the authoritative custom page. Always build/maintain `activity.html` for the CRM activity feed.

**user-management.html (library) vs user-management-crm.html (G-02 custom):** `user-management.html` is a library template demo. `user-management-crm.html` is G-02 at /app/admin/users/manage — the authoritative custom page for user management.

---

*End L0_ROUTE_SCREEN_WORKFLOW_MATRIX.md*
*169 pages total: 75 custom (FROZEN) + 94 library (FROZEN)*
*Pakistan CRM OS — Phase C6 — L0 FROZEN — 2026-06-24*
