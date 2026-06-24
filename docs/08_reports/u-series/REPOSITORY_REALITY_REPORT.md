# REPOSITORY_REALITY_REPORT.md
> Generated: 2026-06-20 — U0 Discovery Pass — evidence from code only, no doc trust

---

## 1. What This Project Is (Code Evidence)

This is a **Pakistan-market SaaS CRM** built for SME businesses. Evidence:

- All dummy data uses Pakistani names, PKR currency, E.164 Pakistan phone numbers (+923xx), and references JazzCash/Easypaisa (Pakistani payment rails)
- crm-components.js implements `pkr()` — a Lakh/Crore number formatter for PKR amounts
- Adapter layer has explicit `pakistan/` directory with JazzCash, Easypaisa, WhatsApp (Dialog360, Gupshup, Meta, Twilio), and Pakistan locale/phone formatters
- Design constraints in DESIGN-SPEC.md specify RTL-first (Urdu), WhatsApp as primary communication surface, and mobile-first for 360px (WhatsApp mobile)
- Backend is multi-tenant (tenant isolation semgrep rule, v1-tenants.routes.js, org_tenant_db schema)

**Architecture:** 3-tier
1. **Frontend** — pure static HTML (no build step, NexLink Bootstrap theme, jQuery + DataTables)
2. **Gateway** — Node.js Express API gateway (auth, routing, RBAC enforcement, rate limiting, idempotency)
3. **Python Services** — FastAPI microservices (business logic, domain models, Alembic-managed PostgreSQL)

---

## 2. Module Inventory (Actual Implemented)

### Frontend Custom Pages (75 — all HTML files confirmed present)

**Archetype A — Dashboard/KPI (13 pages)**
- dashboard.html — Owner/Sales Dashboard
- leads-dashboard.html — Lead Funnel Dashboard
- contacts-health.html — Customer Health Dashboard
- sales-dashboard.html — Opportunity Pipeline Dashboard
- quotes-dashboard.html — Quote Approval Dashboard
- subscriptions-dashboard.html — Subscription Revenue Dashboard
- support-dashboard.html — Case SLA Operations Dashboard
- engagement-dashboard.html — Communication Engagement Dashboard
- knowledge-dashboard.html — Knowledge Effectiveness Dashboard
- workflows-dashboard.html — Workflow Automation Dashboard
- tenants-dashboard.html — Tenant & Entitlement Dashboard
- identity-dashboard.html — Identity & Access Posture Dashboard
- audit-dashboard.html — Platform Audit & Reliability Dashboard

**Archetype B — List/Queue (11 pages)**
- followups.html — Follow-up Queue
- leads.html — Lead Queue
- contacts.html — Contact List
- accounts.html — Account List
- cases.html — Case/Ticket Queue
- activity.html — Activity Feed
- tasks.html — Task Queue
- collections.html — Collections Queue
- invoices.html — Invoice Queue
- users.html — User Directory
- partners.html — Partner List

**Archetype C — Entity Detail (12 pages)**
- leads-detail.html, contacts-detail.html, accounts-detail.html
- opportunities-detail.html, cases-detail.html, quotes-detail.html
- orders-detail.html, invoices-detail.html, subscriptions-detail.html
- workflow-run-detail.html, partners-detail.html, knowledge-article.html

**Archetype D — Sales Cockpit (1 page)**
- sales-cockpit.html

**Archetype E — Support Console (1 page)**
- support-console.html

**Archetype F — Marketing Workspace (1 page)**
- marketing-workspace.html

**Archetype G — Settings/Admin (9 pages)**
- org-settings.html, user-management-crm.html, roles.html, billing-settings.html
- integrations.html, notifications.html, feature-flags.html, compliance.html, territories.html

**Archetype H — Reporting/Analytics (7 pages)**
- sales-analytics.html, marketing-analytics.html, support-analytics.html, finance-analytics.html
- workflow-analytics.html, audit-report.html, report-builder.html

**Archetype I — Form/Wizard (6 pages)**
- lead-new.html, contact-new.html, opportunity-new.html, case-new.html
- quote-builder.html, campaign-new.html

**Archetype J — Audit/Compliance (5 pages)**
- audit-log.html, compliance-report.html, data-governance.html, rbac-audit.html, privacy.html

**Archetype K — Builder/Canvas (4 pages)**
- workflow-builder.html, object-builder.html, rule-builder.html, approval-lanes.html

**Archetype L — Inbox/Communication (3 pages)**
- inbox.html, inbox-thread.html, routing-config.html

**Archetype M — AI/Copilot (2 pages)**
- ai-copilot.html, ai-insights.html

### Backend Python Modules (34 — all confirmed in src/)

| Module | Entities | Services | API | Notes |
|---|---|---|---|---|
| admin_control_center | ✓ | ✓ | ✓ | |
| ai_copilot | ✓ | ✓ | ✓ | Advisory-only by design |
| ai_scoring | ✓ | ✓ | ✓ | |
| automation_journeys | ✓ | ✓ | ✓ | +events.py, workflow_mapping.py |
| campaigns | ✓ | ✓ | ✓ | +segmentation.py, workspace.py, workflow_mapping.py |
| communication_integrations | ✓ | ✓ | ✓ | |
| contract_lifecycle_management | ✓ | ✓ | ✓ | |
| custom_object_framework | ✓ | ✓ | ✓ | +layout.py |
| custom_objects | ✓ | ✓ | ✓ | |
| customer_360_cdp | ✓ | ✓ | ✓ | |
| data_deduplication_engine | ✓ | ✓ | — | No api.py (internal service) |
| design_system | ✓ | ✓ | ✓ | |
| event_bus | — | — | ✓ | +core.py, handlers.py, interfaces.py, store.py, catalog |
| execution_hardening | — | — | — | concurrency.py only |
| external_apis_webhooks | ✓ | ✓ | ✓ | +auth.py, mapping.py, public_api_sdk.py, self_qc.py |
| knowledge_base | ✓ | ✓ | ✓ | |
| lead_management | ✓ | ✓ | ✓ | +events.py, workflow_mapping.py |
| marketing_admin_workflow_ui | ✓ | ✓ | ✓ | |
| omnichannel_inbox | ✓ | ✓ | ✓ | |
| partner_channel_management | ✓ | ✓ | ✓ | |
| plugin_framework | ✓ | ✓ | ✓ | +self_qc.py |
| predictive_forecasting | ✓ | ✓ | ✓ | |
| predictive_models | ✓ | ✓ | ✓ | |
| reporting_dashboards | ✓ | ✓ | ✓ | |
| revenue_recognition | ✓ | ✓ | ✓ | |
| role_based_ui | ✓ | ✓ | ✓ | |
| rule_engine | ✓ | ✓ | ✓ | +cpq_api.py, cpq_rules.py |
| sales_cockpit | — | — | ✓ | +workspace.py |
| subscription_billing | ✓ | ✓ | ✓ | +workflow_mapping.py |
| support_console | ✓ | ✓ | ✓ | |
| territory_management | ✓ | ✓ | ✓ | |
| ticket_management | ✓ | ✓ | ✓ | |
| usage_billing | ✓ | ✓ | ✓ | |
| workflow_engine | ✓ | ✓ | ✓ | +catalog.py |

### Gateway API Route Groups (43 — all v1-*.routes.js confirmed)
accounts, activities, ai, audit, auth, billing, campaigns, cases, collections, communications, compliance-settings, contacts, emails, feature-flags-mgmt, followups, forecasts, governance, inbox, integrations, invoice-summaries, knowledge, leads, notification-preferences, opportunities, orders, org-settings, partners, payments, payment-webhooks, price-books, privacy, quotes, reports, roles, segments, subscriptions, sync, tasks, templates, tenants, territories, users, whatsapp-webhooks, workflows

---

## 3. Entity Inventory (from crm-dummy.js + db/*/schema.sql)

**Core CRM Entities** (from crm-dummy.js — confirmed field shapes):
- **USERS** — id, display_name, email, role, avatar
- **LEADS** — lead_id, contact_name, contact_phone_e164, contact_email, stage (new/qualifying/proposal/negotiation/won/lost), source (whatsapp/web/referral/manual/campaign/import), owner_id, priority (hot/warm/cold), estimated_value, currency (PKR), created_at, updated_at
- **FOLLOWUPS** — task_id, lead_id, lead_name, state (overdue/pending/completed), escalation_level (escalated/warning/reminder/none), due_at, owner_id, rule_type (first_contact/idle_lead/stage_stall/proposal_followup/negotiation_check), action_type (Call/WhatsApp/Reminder), attempts_count
- **OPPORTUNITIES** — opportunity_id, name, account_id, account_name, stage (discovery/qualification/proposal/negotiation/closed_won/closed_lost), amount, currency, forecast_category (pipeline/best_case/commit/closed/omitted), close_date, owner_id, probability
- **CONTACTS** — contact_id, display_name, phone_e164, email, account_id, account_name, completeness_score, open_cases, idle, tags, last_touchpoint
- **ACCOUNTS** — account_id, name, tier, industry, balance (PKR)
- **CASES/TICKETS** — with SLA state machine (OPEN/ASSIGNED/IN_PROGRESS/WAITING_ON_CUSTOMER/RESOLVED/ESCALATED/CLOSED)
- **INVOICES** — total/paid/balance amounts, status, overdue flag
- **SUBSCRIPTIONS** — status enum (draft/trialing/active/past_due/paused/cancelled/expired), MRR/ARR metrics
- **QUOTES** — with line items, approval history, discount routing (>10% requires approval)
- **ORDERS** — immutable post-fulfilment, linked invoice
- **CAMPAIGNS** — status, type, segment targeting
- **WORKFLOWS/EXECUTIONS** — pass/fail states, retry logic
- **PARTNERS** — tier, commission ledger, attribution
- **KNOWLEDGE_ARTICLES** — state-gated publish/edit, version history
- **TERRITORIES** — criteria_type enum, TerritoryRule entity, assignment strategies
- **AUDIT_LOG** — hash-chain verified, allow/deny actions, signed CSV export
- **TENANTS** — plan/seat/feature entitlements, multi-tenant isolation
- **ROLES/PERMISSIONS** — RBAC matrix, assignment log
- **FEATURE_FLAGS** — 2-person approval on toggle
- **MESSAGE_THREADS** — channel, intent badges (WhatsApp primary)

**DB Schema Files** (20 domains confirmed in db/):
activity_task, audit_compliance, campaign, case_ticket, contact_account, feature_flag, identity_auth, intelligence, knowledge, lead_management, messaging, notification, opportunity, org_tenant, quote_order, territory, transaction (with 4 SQL migrations), workflow

---

## 4. API Inventory (Actual Routes Found)

**All routes are under /api/v1/** — confirmed from gateway route files.

| Domain | Routes |
|---|---|
| Auth | /auth/login, /auth/refresh, /auth/logout, /auth/register, /dev-token (dev mode) |
| Leads | /leads, /leads/:id, /leads (POST), /leads/dashboard |
| Contacts | /contacts, /contacts/:id, /contacts (POST) |
| Accounts | /accounts, /accounts/:id |
| Opportunities | /opportunities, /opportunities/:id, /opportunities (POST) |
| Follow-ups | /followups, /followups/:id, /followups (POST/PATCH) |
| Activities | /activities, /activities/:id |
| Cases | /cases, /cases/:id, /cases (POST), /support (dashboard) |
| Collections | /collections, /collections/:id |
| Campaigns | /campaigns, /campaigns/:id, /campaigns (POST) |
| Communications | /communications/engagement |
| Inbox | /inbox, /inbox/:thread_id, /inbox/routing |
| Quotes | /quotes, /quotes/:id, /quotes (POST) |
| Orders | /orders, /orders/:id |
| Invoices | /invoice-summaries |
| Subscriptions | /subscriptions, /subscriptions/:id |
| Payments | /payments (POST), /payment-webhooks (POST) |
| WhatsApp | /whatsapp-webhooks (POST) |
| Billing | /billing/subscription, /billing/invoices |
| Workflows | /workflows, /workflows/:id, /workflows/runs/:id |
| Tasks | /tasks, /tasks/:id |
| Users | /users, /users/:id, /users (POST/PATCH) |
| Roles | /roles, /roles/:id |
| Tenants | /admin/tenants, /admin/tenants/:id |
| Territories | /territories, /territories/:id |
| Partners | /partners, /partners/:id |
| Knowledge | /knowledge, /knowledge/:id |
| Reports | /reports/execute (POST), /reports/definitions (POST/GET) |
| AI | /ai/scores, /ai/predictions, /ai/estimates, /ai/copilot, /ai/models |
| Audit | /audit, /audit/export |
| Segments | /segments |
| Templates | /templates |
| Org Settings | /org-settings |
| Integrations | /integrations, /integrations/:provider/test |
| Feature Flags | /admin/feature-flags, /admin/feature-flags/:id |
| Governance | /governance/classification, /governance/retention, /governance/sar |
| Compliance | /compliance-settings |
| Privacy | /privacy/consent |
| Notifications | /notification-preferences |
| Forecasts | /forecasts |
| Price Books | /price-books |
| Emails | /emails |
| Sync | /sync |

**Health:** /health (confirmed in render.yaml healthCheckPath)

---

## 5. Integration Inventory (Actual Implementations Found)

| Integration | Status | Evidence |
|---|---|---|
| JazzCash (payment) | **STUB — stub_mode=True** | adapters/pakistan/payments/jazzcash.py, render.yaml JAZZCASH_STUB_MODE=true |
| Easypaisa (payment) | **STUB — stub_mode=True** | adapters/pakistan/payments/easypaisa.py, render.yaml EASYPAISA_STUB_MODE=true |
| WhatsApp via Meta API | Adapter implemented | adapters/pakistan/messaging/meta_api_adapter.py |
| WhatsApp via Gupshup | Adapter implemented | adapters/pakistan/messaging/gupshup_adapter.py |
| WhatsApp via Dialog360 | Adapter implemented | adapters/pakistan/messaging/dialog360_adapter.py |
| WhatsApp via Twilio | Adapter implemented | adapters/pakistan/messaging/twilio_adapter.py |
| PostgreSQL | Live | requirements.txt, alembic/, render.yaml |
| Redis | Live | render.yaml, gateway env vars |
| Render.com | Configured | render.yaml, ci.yml deploy hooks |

**Not found:**
- Email provider (SendGrid/Mailgun/SES) — no adapter, no credentials in render.yaml
- SMS gateway beyond WhatsApp — not implemented
- AI inference provider — M-01 notes "inference model selection pending"; no OpenAI/Anthropic SDK in requirements.txt

---

## 6. Test Coverage Reality

### Backend Tests (backend/tests/ — 54 test files)
Coverage is enforced at **≥80%** by CI (ci.yml: `--cov-fail-under=80`).
A `.coverage` file exists at backend/.coverage — indicating tests have been run locally.

Confirmed test files cover:
- All 34 src/ modules have matching test files (test_lead_management.py, test_campaigns.py, etc.)
- E2E flow: test_e2e_lead_to_payment.py (lead → payment full flow)
- Contract tests: test_public_api.py
- Security: test_enforcement.py, test_tenant_isolation.py (also in root tests/)
- Performance: test_concurrency_lock_cluster.py
- System: test_final_supervisor_qc.py, test_system_hardening_qc.py, test_integration_end_to_end_qc.py
- Pakistan-specific: test_pakistan_payment_adapters.py, test_whatsapp_lead_capture.py, test_whatsapp_public.py

### Frontend E2E Tests (tests/ root — ~30 test files, Playwright)
- Playwright screenshots confirm tests were actually run (200+ .png files)
- Batch run logs (batch1–batch8) show iterative test results
- Coverage areas confirmed by screenshots: page loads, DataTable population, filter chips, form submission, KPI rendering, settings pages, audit pages, functional flows per domain

### Contract Tests (tests/ root)
7 contract test files: auth, billing, communications, governance, integrations, reports, tenant isolation, smoke (all routes)

### Load Testing
tests/locustfile.py — Locust load test exists (locust.log also present)

### Security Scans
- c5_api_security_scan.py with JSON/HTML report outputs
- semgrep-*.json files in tests/
- pip-audit.json in tests/

---

## 7. Gaps Between Documentation Claims and Code Reality

| Claim (Documentation) | Reality (Code Evidence) |
|---|---|
| "All 75 pages browser-approved" (DESIGN-SPEC.md) | 75 HTML files confirmed present. Browser-approval evidence in SCREEN-ARTEFACTS.md (not re-read but referenced) and Playwright PNG screenshots |
| "All pages wired to live API" (DESIGN-SPEC.md header) | crm-api.js has DUMMY_MODE flag; all page JS files use crm-api.js. DESIGN-SPEC notes that wiring was done for specific pages only (G-04, G-05, H-07, J-03) with "full live-API re-verification pass" still pending for all 75 |
| "Phase 6 wiring sprint complete" | Partial — specific pages noted as wired, most still ⏳ awaiting Phase 6 Component 3 re-verification |
| "Backend built" (multiple references) | 34 Python modules confirmed with entities/services/api, 43 gateway route files confirmed, 12 Alembic migrations present |
| JazzCash/Easypaisa payment integration | Adapters built but stub_mode=True in production config — real credentials not yet integrated (P-016 blocker) |
| AI inference (M-01, M-02) | UI built; AI pages are advisory-only shells. No AI inference provider SDK in requirements.txt |
| "80% test coverage" | CI enforces this; .coverage file exists confirming local runs; cannot verify current pass/fail without running tests |
| NexLink library phase "96 pages complete" | 169 total HTML in app/; 75 custom confirmed; remainder (~94) are NexLink demo pages |

---

*End REPOSITORY_REALITY_REPORT.md*
