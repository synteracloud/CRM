---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Derived From: DESIGN-SPEC.md (75 custom pages), frontend/src/app/ directory listing (169 total)
---

# FRONTEND ROUTE CATALOG — Pakistan CRM OS

Every frontend route. 169 total pages. Custom pages have full authority entries. Library pages are one-line entries.

**Key:** ⏳ = HTML built, live-API re-verification pending | Library = NexLink component demo, no custom authority

---

## SECTION 1 — Custom CRM Pages (75 pages)

### Module: Lead Management

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/leads | Lead Queue | Lead Management | B — List/Queue | Phase 1 | All CRM roles | leads.read | GET /leads | ⏳ |
| app/leads/:lead_id | Lead Detail | Lead Management | C — Entity Detail | Phase 1 | All CRM roles (delete: tenant_admin+) | leads.read; leads.update; leads.delete (admin) | GET /leads/:id, PATCH /leads/:id | ⏳ |
| app/leads/new | New Lead Form | Lead Management | I — Form/Wizard | Phase 1 | agent, manager, tenant_admin, tenant_owner | leads.create | POST /leads | ⏳ |
| app/sales/leads/dashboard | Lead Funnel Dashboard | Lead Management | A — Dashboard/KPI | Phase 2 | All CRM roles | leads.read | GET /leads | ⏳ |

### Module: Follow-up Enforcement

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/followups | Follow-up Queue | Follow-up Enforcement | B — List/Queue | Phase 1 | All CRM roles | tasks.read | GET /followups | ⏳ |

### Module: Contacts

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/contacts | Contact List | Contacts | B — List/Queue | Phase 1 | All CRM roles | contacts.read | GET /contacts | ⏳ |
| app/contacts/:contact_id/360 | Customer 360 | Contacts | C — Entity Detail | Phase 8 | All CRM roles | contacts.read | GET /contacts/:id | ⏳ |
| app/contacts/new | New Contact Form | Contacts | I — Form/Wizard | Phase 8 | agent, manager, tenant_admin, tenant_owner | contacts.create | POST /contacts | ⏳ |
| app/contacts/health | Customer Health Dashboard | Contacts | A — Dashboard/KPI | Phase 8 | All CRM roles | contacts.read | GET /contacts | ⏳ |

### Module: Accounts

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/accounts | Account List | Accounts | B — List/Queue | Phase 8 | All CRM roles | accounts.read | GET /accounts | ⏳ |
| app/accounts/:account_id | Account Profile | Accounts | C — Entity Detail | Phase 8 | All CRM roles | accounts.read | GET /accounts/:id | ⏳ |

### Module: Sales / Opportunities

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/opportunities/:opportunity_id | Opportunity Detail | Sales | C — Entity Detail | Phase 2 | All CRM roles | opportunities.read; opportunities.update | GET /opportunities/:id | ⏳ |
| app/opportunities/new | New Opportunity Form | Sales | I — Form/Wizard | Phase 2 | agent, manager, tenant_admin, tenant_owner | opportunities.create | POST /opportunities | ⏳ |
| app/sales/cockpit | Sales Cockpit | Sales | D — Sales Cockpit | Phase 2 | All CRM roles | opportunities.read; leads.read | GET /opportunities, GET /leads | ⏳ |
| app/sales/dashboard | Opportunity Pipeline Dashboard | Sales | A — Dashboard/KPI | Phase 2 | All CRM roles | opportunities.read | GET /opportunities, GET /forecasts | ⏳ |

### Module: CPQ / Quotes & Orders

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/sales/quotes/new | CPQ Quote Builder | CPQ | I — Form/Wizard | Phase 2 | manager, tenant_admin, tenant_owner | quotes.create | POST /quotes | ⏳ |
| app/sales/quotes/:quote_id | Quote Detail | CPQ | C — Entity Detail | Phase 2 | All CRM roles | quotes.read; quotes.approve (admin) | GET /quotes/:id | ⏳ |
| app/sales/quotes/dashboard | Quote Approval Dashboard | CPQ | A — Dashboard/KPI | Phase 2 | manager, tenant_admin, tenant_owner | quotes.read | GET /quotes | ⏳ |
| app/sales/orders/:order_id | Order Detail | CPQ | C — Entity Detail | Phase 8 | All CRM roles | orders.read | GET /orders/:id | ⏳ |

### Module: Finance / Collections

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/collections | Collections Queue | Finance | B — List/Queue | Phase 1 | All CRM roles (write: collections roles) | collections.read | GET /collections | ⏳ |
| app/finance/invoices | Invoice Queue | Finance | B — List/Queue | Phase 3 | All CRM roles | collections.read | GET /invoice-summaries | ⏳ |
| app/finance/invoices/:invoice_id | Invoice Detail | Finance | C — Entity Detail | Phase 3 | All CRM roles | collections.read | GET /invoice-summaries/:id | ⏳ |
| app/reports/finance | Finance Analytics | Finance | H — Reporting | Phase 3 | All CRM roles | analytics.view_basic | GET /invoice-summaries, GET /collections | ⏳ |

### Module: Subscriptions / Billing

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/finance/subscriptions/dashboard | Subscription Revenue Dashboard | Subscriptions | A — Dashboard/KPI | Phase 3 | manager, tenant_admin, tenant_owner | analytics.view_basic | GET /subscriptions | ⏳ |
| app/finance/subscriptions/:subscription_id | Subscription Detail | Subscriptions | C — Entity Detail | Phase 3 | All CRM roles | collections.read | GET /subscriptions/:id | ⏳ |
| app/settings/billing | Billing & Subscription Settings | Billing | G — Settings/Admin | Phase 6 | tenant_admin, tenant_owner | admin.system_config | GET /billing/subscription, GET /billing/invoices | ⏳ (P-016 stub) |

### Module: Support / Cases

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/support/cases | Ticket / Case Queue | Support | B — List/Queue | Phase 4 | All CRM roles | cases.read | GET /cases | ⏳ |
| app/support/cases/:case_id | Case / Ticket Detail | Support | C — Entity Detail | Phase 4 | All CRM roles | cases.read; cases.update; cases.close (admin) | GET /cases/:id | ⏳ |
| app/support/cases/new | New Case Form | Support | I — Form/Wizard | Phase 4 | agent, manager, tenant_admin, tenant_owner | cases.create | POST /cases | ⏳ |
| app/support/console | Support Console | Support | E — Support Console | Phase 4 | agent, manager, tenant_admin, tenant_owner | cases.read; inbox.read | GET /cases, GET /support/queues | ⏳ |
| app/support/dashboard | Case SLA Operations Dashboard | Support | A — Dashboard/KPI | Phase 4 | All CRM roles | cases.read | GET /cases | ⏳ |

### Module: Knowledge Base

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/support/knowledge/:article_id | Knowledge Article Detail | Knowledge Base | C — Entity Detail | Phase 4 | All CRM roles | knowledge.read | GET /knowledge/:id | ⏳ |
| app/support/knowledge/dashboard | Knowledge Effectiveness Dashboard | Knowledge Base | A — Dashboard/KPI | Phase 8 | All CRM roles | knowledge.read | GET /knowledge | ⏳ |

### Module: Omnichannel Inbox

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/inbox | Omnichannel Inbox | Inbox | L — Inbox/Comms | Phase 5 | agent, manager, tenant_admin, tenant_owner | inbox.read | GET /inbox/conversations | ⏳ |
| app/inbox/:thread_id | Conversation Thread | Inbox | L — Inbox/Comms | Phase 5 | agent, manager, tenant_admin, tenant_owner | inbox.read; inbox.claim | GET /inbox/conversations/:id | ⏳ |
| app/admin/routing | Routing Configuration | Inbox | L — Inbox/Comms | Phase 8 | manager, tenant_admin, tenant_owner | inbox.admin | GET /inbox/queues | ⏳ |

### Module: Marketing / Campaigns

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/marketing/campaigns | Marketing Workspace | Marketing | F — Marketing | Phase 7 | manager, tenant_admin, tenant_owner | campaigns.read | GET /campaigns | ⏳ |
| app/marketing/campaigns/new | Journey / Campaign Builder | Marketing | I — Form/Wizard | Phase 7 | manager, tenant_admin, tenant_owner | campaigns.create | POST /campaigns | ⏳ |
| app/reports/marketing | Marketing Analytics | Marketing | H — Reporting | Phase 7 | All CRM roles | analytics.view_basic | GET /campaigns | ⏳ |
| app/marketing/engagement | Communication Engagement Dashboard | Marketing | A — Dashboard/KPI | Phase 5 | All CRM roles | analytics.view_basic | GET /communications/engagement, GET /campaigns | ⏳ (Wired 2026-05-31) |

### Module: Workflow Automation

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/workflows/builder | Workflow Builder | Workflows | K — Builder/Canvas | Phase 7 | manager, tenant_admin, tenant_owner | workflows.create; workflows.publish | GET /workflows, POST /workflows | ⏳ |
| app/workflows/runs/:execution_id | Workflow Execution Detail | Workflows | C — Entity Detail | Phase 8 | manager, tenant_admin, tenant_owner | workflows.read | GET /workflows/runs/:id | ⏳ |
| app/workflows/dashboard | Workflow Automation Dashboard | Workflows | A — Dashboard/KPI | Phase 7 | All CRM roles | workflows.read | GET /workflows, GET /workflows/runs | ⏳ |
| app/reports/workflows | Workflow Analytics | Workflows | H — Reporting | Phase 8 | All CRM roles | analytics.view_basic | GET /workflows/runs | ⏳ |

### Module: AI / Copilot

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/ai/copilot | AI Copilot Panel | AI | M — AI/Copilot | Phase 8 | All CRM roles | ai.view_scores | GET /ai/copilot/suggestions, GET /ai/scores/leads | ⏳ |
| app/ai/insights | AI Insights Dashboard | AI | M — AI/Copilot | Phase 8 | manager, tenant_admin, tenant_owner | ai.view_scores; ai.view_forecasts | GET /ai/scores/leads, GET /ai/predictions/churn, GET /ai/estimates/clv | ⏳ |

### Module: Territories

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/admin/territories | Territory & Assignment Config | Territories | G — Settings/Admin | Phase 6 | manager, tenant_admin, tenant_owner | territories.read; territories.create (admin) | GET /territories | ⏳ |

### Module: Partners

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/partners | Partner List | Partners | B — List/Queue | Phase 8 | All CRM roles | partners.read | GET /partners | ⏳ |
| app/partners/:partner_id | Partner Detail | Partners | C — Entity Detail | Phase 8 | All CRM roles | partners.read | GET /partners/:id | ⏳ |

### Module: Identity & Access Management

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/admin/users | User Directory | Identity | B — List/Queue | Phase 8 | tenant_admin, tenant_owner | admin.manage_users | GET /admin/users | ⏳ |
| app/admin/users/manage | User Management | Identity | G — Settings/Admin | Phase 6 | tenant_admin, tenant_owner | admin.manage_users | GET /admin/users, POST /admin/users/invite | ⏳ |
| app/admin/identity | Identity & Access Posture Dashboard | Identity | A — Dashboard/KPI | Phase 8 | tenant_admin, tenant_owner | admin.read_audit_logs | GET /admin/users, GET /admin/audit-logs | ⏳ |

### Module: Audit & Compliance

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/audit | Audit Log | Audit | J — Audit/Compliance | Phase 8 | tenant_admin, tenant_owner | admin.read_audit_logs | GET /admin/audit-logs | ⏳ |
| app/compliance | Compliance Report | Audit | J — Audit/Compliance | Phase 8 | tenant_admin, tenant_owner | admin.export_compliance_data | GET /admin/audit-logs | ⏳ |
| app/admin/governance | Data Governance Console | Audit | J — Audit/Compliance | Phase 8 | tenant_admin, tenant_owner | admin.system_config | GET /governance/classification, GET /governance/retention, GET /governance/sar, GET /privacy/consent | ⏳ (Wired) |
| app/admin/rbac-audit | RBAC Audit | Audit | J — Audit/Compliance | Phase 8 | tenant_admin, tenant_owner | admin.read_audit_logs | GET /admin/users | ⏳ |
| app/settings/privacy | Consent & Privacy Manager | Audit | J — Audit/Compliance | Phase 8 | tenant_admin, tenant_owner | admin.system_config | GET /privacy/consent | ⏳ |
| app/admin/audit/dashboard | Platform Audit & Reliability Dashboard | Audit | A — Dashboard/KPI | Phase 8 | tenant_admin, tenant_owner | admin.read_audit_logs | GET /admin/audit-logs | ⏳ |
| app/reports/audit | Audit Report | Audit | H — Reporting | Phase 8 | tenant_admin, tenant_owner | admin.read_audit_logs; admin.export_compliance_data | GET /admin/audit-logs | ⏳ |

### Module: Settings / Administration

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/settings/org | Organization Settings | Settings | G — Settings/Admin | Phase 6 | tenant_admin, tenant_owner | admin.system_config | GET /admin/settings | ⏳ |
| app/admin/roles | Role & Permission Editor | Settings | G — Settings/Admin | Phase 6 | tenant_admin, tenant_owner | admin.manage_roles | GET /admin/roles | ⏳ |
| app/settings/integrations | Integration Settings | Settings | G — Settings/Admin | Phase 6 | tenant_admin, tenant_owner | admin.system_config | GET /integrations, POST /integrations/:provider/test | ⏳ (Wired) |
| app/settings/notifications | Notification Settings | Settings | G — Settings/Admin | Phase 6 | tenant_admin, tenant_owner | admin.system_config | GET /admin/settings | ⏳ |
| app/admin/feature-flags | Feature Flags | Settings | G — Settings/Admin | Phase 6 | tenant_owner | admin.manage_feature_flags | GET /feature-flags | ⏳ |
| app/settings/compliance | Compliance Settings | Settings | G — Settings/Admin | Phase 6 | tenant_admin, tenant_owner | admin.system_config | N/A (static admin form) | ⏳ |

### Module: Builder Tools

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/admin/objects | Custom Object Layout Builder | Builder Tools | K — Builder/Canvas | Phase 8 | tenant_admin, tenant_owner | admin.system_config | N/A (advisory shell — D-002) | ⏳ |
| app/admin/rules | Rule / CPQ Logic Builder | Builder Tools | K — Builder/Canvas | Phase 8 | tenant_admin, tenant_owner | admin.system_config | N/A (visual canvas) | ⏳ |
| app/sales/approval-lanes | CPQ Approval Lane Board | Builder Tools | K — Builder/Canvas | Phase 8 | manager, tenant_admin, tenant_owner | quotes.approve | GET /quotes | ⏳ |

### Module: Report Builder

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/reports/builder | Custom Report Builder | Reports | H — Reporting | Phase 8 | All CRM roles | analytics.view_advanced | POST /reports/execute, POST /reports/definitions, GET /reports/definitions | ⏳ (Wired) |
| app/reports/sales | Sales Analytics | Reports | H — Reporting | Phase 8 | All CRM roles | analytics.view_basic | GET /opportunities, GET /leads | ⏳ |
| app/reports/support | Support Analytics | Reports | H — Reporting | Phase 8 | All CRM roles | analytics.view_basic | GET /cases | ⏳ |

### Module: Tenant Admin

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/admin/tenants | Tenant & Entitlement Dashboard | Tenant Admin | A — Dashboard/KPI | Phase 8 | tenant_owner | admin.manage_tenants | GET /admin/tenants | ⏳ |

### Module: Activity & Tasks

| Route (app/xxx.html) | Page Title | Module | Archetype | Phase | Roles Allowed | Key Permissions | Primary API | Status |
|---|---|---|---|---|---|---|---|---|
| app/activity | Activity Feed | Activity | B — List/Queue | Phase 8 | All CRM roles | activities.read | GET /activities | ⏳ |
| app/tasks | Task Queue | Tasks | B — List/Queue | Phase 8 | All CRM roles | tasks.read | GET /tasks | ⏳ |

---

## SECTION 2 — NexLink Library Pages (94 pages)

All entries below are NexLink component demos. No custom CRM authority required. Not part of the 75 custom page build scope.

| File | Description |
|---|---|
| accordion.html | Library — Bootstrap accordion component demo |
| activities.html | Library — NexLink activities template demo |
| alerts.html | Library — Bootstrap alerts component demo |
| apexchart.html | Library — ApexCharts integration demo |
| avatar.html | Library — Avatar component demo |
| badge.html | Library — Badge component demo |
| blog.html | Library — Blog page template |
| blog-details.html | Library — Blog detail template |
| blog-list.html | Library — Blog list template |
| breadcrumb.html | Library — Breadcrumb component demo |
| button-group.html | Library — Button group component demo |
| buttons.html | Library — Button variants demo |
| calendar.html | Library — Calendar component demo |
| card.html | Library — Card component demo |
| card-action.html | Library — Card action patterns demo |
| carousel.html | Library — Carousel component demo |
| chartjs.html | Library — Chart.js integration demo |
| chat.html | Library — Chat UI template demo |
| collapse.html | Library — Bootstrap collapse demo |
| customers.html | Library — Customers template demo |
| dashboard-rtl.html | Library — RTL dashboard demo |
| deals.html | Library — Deals template demo |
| drag-and-drop.html | Library — Drag and drop component demo |
| dropdowns.html | Library — Dropdown component demo |
| email-compose.html | Library — Email compose template |
| email-read.html | Library — Email read template |
| employee.html | Library — Employee template demo |
| error-404.html | Library — 404 error page |
| error-404-cover.html | Library — 404 cover variant |
| error-404-full.html | Library — 404 full-page variant |
| finance.html | Library — Finance template demo |
| flaticon.html | Library — Flaticon icon library demo |
| flatpickr.html | Library — Flatpickr date picker demo |
| fontawesome.html | Library — Font Awesome icon library demo |
| forgot-password-basic.html | Library — Forgot password basic template |
| forgot-password-cover.html | Library — Forgot password cover template |
| forgot-password-frame.html | Library — Forgot password frame template |
| form-elements.html | Library — Form elements demo |
| form-floating.html | Library — Floating label form demo |
| form-input-group.html | Library — Input group demo |
| form-layout.html | Library — Form layout demo |
| form-validation.html | Library — Form validation demo |
| inbox-email.html | Library — Email inbox template demo |
| investment.html | Library — Investment template demo |
| jsvectormap.html | Library — jsVectorMap integration demo |
| leaflet.html | Library — Leaflet.js map integration demo |
| list-group.html | Library — List group component demo |
| login-basic.html | Library — Login basic template |
| login-cover.html | Library — Login cover template |
| login-frame.html | Library — Login frame template |
| lucide.html | Library — Lucide icon library demo |
| marketing.html | Library — Marketing template demo |
| modal.html | Library — Modal component demo |
| navbar.html | Library — Navbar component demo |
| new-chat.html | Library — New chat template |
| new-password-basic.html | Library — New password basic template |
| new-password-cover.html | Library — New password cover template |
| new-password-frame.html | Library — New password frame template |
| new-project.html | Library — New project template |
| offcanvas.html | Library — Offcanvas component demo |
| pagination.html | Library — Pagination component demo |
| plans.html | Library — Pricing plans template |
| popovers.html | Library — Popover component demo |
| pricing.html | Library — Pricing page template |
| profile.html | Library — User profile template |
| progress.html | Library — Progress bar component demo |
| register-basic.html | Library — Registration basic template |
| register-cover.html | Library — Registration cover template |
| register-frame.html | Library — Registration frame template |
| review.html | Library — Review template demo |
| sales.html | Library — Sales template demo |
| scrollspy.html | Library — Scrollspy component demo |
| search-apps.html | Library — Search apps template |
| search-apps-details.html | Library — Search apps detail template |
| search-chat.html | Library — Search chat template |
| search-image.html | Library — Search image template |
| settings.html | Library — Settings template demo |
| simplebar.html | Library — Simplebar scroll demo |
| spinners.html | Library — Spinner component demo |
| swiper.html | Library — Swiper carousel demo |
| tables-basic.html | Library — Basic tables demo |
| tables-datatable.html | Library — DataTables demo |
| tabs.html | Library — Tab component demo |
| tagify.html | Library — Tagify input demo |
| task-management.html | Library — Task management template |
| team-management.html | Library — Team management template |
| toasts.html | Library — Toast notification demo |
| tooltips.html | Library — Tooltip component demo |
| typography.html | Library — Typography demo |
| under-construction.html | Library — Under construction page |
| under-construction-cover.html | Library — Under construction cover variant |
| under-construction-full.html | Library — Under construction full-page variant |
| user-management.html | Library — User management template demo |
| your-chat.html | Library — Chat template demo |

---

*End FRONTEND_ROUTE_CATALOG.md*
*Total: 169 pages (75 custom + 94 library)*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
