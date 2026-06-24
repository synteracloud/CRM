Status: Draft
Authority Level: Critical
Last Reviewed: 2026-06-22
Owner: Shared

---

# FULLSTACK STITCHING CONTRACT — Pakistan CRM OS

## Purpose

This document traces each major feature through every layer of the stack: from user intent, through domain entity, to backend module, API endpoint, frontend page, permission gate, validation layer, test coverage, and deployment dependency.

**Scope:** Sections 1–10 cover the 10 primary workflows in full detail. Sections 11–22 cover the remaining 12 modules from FEATURE_SCOPE.md with confirmed API, entity, and page evidence from API_INVENTORY.md and ENTITY_INVENTORY.md. For modules marked with lower detail, refer to API_INVENTORY.md for complete endpoint lists.

**Reading instructions:**
- All TBDs from U0–U10 phases have been resolved in Phase 3.25 (2026-06-23). No open TBDs remain in this document.
- Source references point to actual files confirmed in the repository
- DUMMY_MODE status: DUMMY_MODE is false on all pages (crm-api.js line 14); live API with crm-dummy.js fallback

---

## Traceability Template

```
Feature → Workflow → Domain Entity → Backend Module → API Endpoint(s) → Frontend Page(s) → Permission Required → Validation Layer → Test Coverage → Deployment Dependency
```

---

## 1. Contact Creation and Management

**Feature:** Create, view, update, and manage Contacts (Customer 360)
**Workflow:** WF-A (Lead-to-Deal) step 1 — Contact created or linked when Lead captured

**Domain Entity:**
- Contact (contact_account_db)
- Key fields: contact_id, tenant_id, display_name, phone_e164 (E.164), email (nullable), account_id (nullable), completeness_score (0–100), tags

**Backend Module:**
- Python: `backend/src/customer_360_cdp/` (api.py, entities.py, services.py)
- Gateway: `backend/gateway/routes/v1-contacts.routes.js`

**API Endpoints:**
| Method | Path | Purpose |
|---|---|---|
| GET | /contacts | List contacts with health indicators |
| POST | /contacts | Create contact |
| GET | /contacts/:id | Contact detail |
| PATCH | /contacts/:id | Update contact (display_name, phone_e164, email, account_id, tags) |
| DELETE | /contacts/:id | Delete contact |
| GET | /contacts/export | CSV export |
| POST | /contacts/import | Bulk CSV import with phone dedup |

**Frontend Pages:**
| Page ID | File | DUMMY_MODE |
|---|---|---|
| B-03 | contacts.html | true (pending re-verification) |
| C-02 | contacts-detail.html | true |
| I-02 | contact-new.html | true |
| A-03 | contacts-health.html | true |

**Permissions Required:**
- contacts.read (CONTACTS_READ) — all CRM roles except auditor
- contacts.create (CONTACTS_CREATE) — tenant_owner, tenant_admin, manager, agent
- contacts.update (CONTACTS_UPDATE) — tenant_owner, tenant_admin, manager, agent
- contacts.delete — SECURITY GAP CONFIRMED: scope is referenced in v1-contacts.routes.js:139 (`requireScopes(['contacts.delete'])`) but is absent from rbac-scopes.js SCOPES constant. The DELETE endpoint is therefore inaccessible to ALL roles including tenant_owner (who gets Object.values(SCOPES) which does not include contacts.delete). Requires human decision: add CONTACTS_DELETE to rbac-scopes.js and grant to tenant_owner + tenant_admin (consistent with leads.delete pattern), or remove the endpoint. See H-002 in REMEDIATION_REPORT.md.

**Validation Layer:**
- Phone: E.164 format enforced (must start with + and country code)
- Email: TEXT nullable — CONFIRMED: no format enforcement in gateway or FastAPI (plain `str` type; `EmailStr` not used). Phase 3.25 verified.
- Tenant isolation: every query binds tenant_id (semgrep CI rule enforces)

**Test Coverage:**
- Backend: `backend/tests/test_customer_360_cdp.py` (confirmed Phase 3.25)
- E2E: test_datatable.py covers contacts.html rows; test_form_submit.py covers contact-new.html
- API contract: test_smoke_all_routes.py covers /contacts route

**Deployment Dependency:** contact_account_db PostgreSQL schema; Alembic migration applied

---

## 2. Lead Capture and Qualification

**Feature:** Capture new leads (manual, WhatsApp, import), qualify them through pipeline stages
**Workflow:** WF-A (Lead-to-Deal) steps 1–5; WF-001 (lead idle enforcement)

**Domain Entity:**
- Lead (lead_management_db)
- LeadAssignment, LeadHistory, FollowupTask (all in lead_management_db + activity_task_db)
- Key fields: lead_id, tenant_id, contact_id, owner_id (NOT NULL), stage, status, priority, source, version_no

**Backend Module:**
- Python: `backend/src/lead_management/` (api.py, entities.py, services.py, events.py, workflow_mapping.py)
- Gateway: `backend/gateway/routes/v1-leads.routes.js`, `v1-followups.routes.js`

**API Endpoints:**
| Method | Path | Purpose |
|---|---|---|
| GET | /leads | List leads with filters |
| POST | /leads | Create lead (emits lead.created.v1) |
| GET | /leads/:id | Lead detail |
| PATCH | /leads/:id | Update/stage transition |
| DELETE | /leads/:id | Soft delete (repo.softDelete) |
| GET | /leads/export | CSV export |
| POST | /leads/import | Bulk CSV/JSON import |
| GET | /leads/:id/next-action | AI next-action suggestion (proxies to followup service) |
| GET | /followups | List follow-ups |
| POST | /followups | Create follow-up task |
| GET | /followups/:task_id | Follow-up task detail |
| POST | /followups/:id/complete | Complete follow-up |
| POST | /followups/:id/snooze | Snooze follow-up |
| GET | /followups/lead/:id/canonical | Canonical pending task for lead |

**Frontend Pages:**
| Page ID | File | DUMMY_MODE |
|---|---|---|
| B-02 | leads.html | true |
| C-01 | leads-detail.html | true |
| I-01 | lead-new.html | true |
| A-02 | leads-dashboard.html | true |
| B-01 | followups.html | true |

**Permissions Required:**
- leads.read, leads.create, leads.update, leads.delete (delete: owner/admin only), leads.assign
- followups.read, followups.create, followups.complete, followups.snooze

**Validation Layer:**
- owner_id: NOT NULL — must be provided on create
- stage: must be in allowed enum (new/qualifying/nurturing/proposal/negotiation/won/lost/disqualified)
- phone_e164: E.164 format on linked Contact
- canonical constraint: DB unique constraint prevents 2+ canonical pending tasks per lead
- version_no: OCC enforcement on updates

**Test Coverage:**
- Backend: `backend/tests/test_lead_management.py` (confirmed Phase 3.25)
- E2E: test_datatable.py covers leads.html; test_form_submit.py covers lead-new.html
- E2E: test_workflow_onboarding.py covers register→first lead→first followup→mark complete

**Deployment Dependency:** lead_management_db, activity_task_db PostgreSQL schemas; WF-001 seeded in workflow_db

---

## 3. Deal Pipeline Management

**Feature:** Track opportunities through sales stages from qualification to close
**Workflow:** WF-A (Lead-to-Deal) steps 6–9; WF-005 (stage change notification)

**Domain Entity:**
- Opportunity (opportunity_db)
- OpportunityLineItem (opportunity_db)
- Key fields: opportunity_id, owner_id, amount (PKR), stage, probability, forecast_category, version_no

**Backend Module:**
- Python: `backend/src/sales_cockpit/` (api.py, workspace.py)
- Gateway: `backend/gateway/routes/v1-opportunities.routes.js`

**API Endpoints:**
| Method | Path | Purpose |
|---|---|---|
| GET | /opportunities | List with filters |
| POST | /opportunities | Create opportunity |
| GET | /opportunities/:id | Opportunity detail |
| PATCH | /opportunities/:id | Stage transition (atomic; emits stage event) |
| GET | /opportunities/:id/line-items | Line items sub-resource |
| POST | /opportunities/:id/line-items | Add line item |

**Frontend Pages:**
| Page ID | File | DUMMY_MODE |
|---|---|---|
| C-04 | opportunities-detail.html | true |
| D-01 | sales-cockpit.html | true |
| A-04 | sales-dashboard.html | true |
| I-03 | opportunity-new.html | true |

**Permissions Required:**
- opportunities.read, opportunities.create, opportunities.update
- opportunities.close (OPPORTUNITIES_CLOSE) — tenant_owner, tenant_admin, manager only

**Validation Layer:**
- version_no: OCC (optimistic concurrency) on PATCH
- stage: must follow state machine (qualification→discovery→proposal→negotiation→closed_won/closed_lost)
- forecast_category: must be one of (pipeline/best_case/commit/closed/omitted)
- amount: NUMERIC, PKR only

**Test Coverage:**
- Backend: `backend/tests/test_sales_cockpit_workspace.py` (confirmed Phase 3.25)
- E2E: test_datatable.py covers opportunities list pages

**Deployment Dependency:** opportunity_db schema; WF-005 seeded; predictive_forecasting module for forecast refresh

---

## 4. Invoice Generation and Payment

**Feature:** Generate invoices, collect PKR payments via JazzCash/Easypaisa, manage collections
**Workflow:** WF-B (Deal-to-Invoice); WF-E (Payment Collection); WF-002 (Collections Reminder)

**Domain Entities:**
- Invoice, Payment, Collection, Subscription (transaction_db)
- Order (quote_order_db)
- Key fields: invoice_id, total_amount (PKR), paid_amount, balance_amount, status, is_overdue

**Backend Modules:**
- Python: `backend/src/revenue_recognition/`, `src/usage_billing/`, `src/subscription_billing/`
- Gateway: v1-invoice-summaries.routes.js, v1-collections.routes.js, v1-payments.routes.js, v1-payment-webhooks.routes.js, v1-subscriptions.routes.js, v1-billing.routes.js

**API Endpoints:**
| Method | Path | Purpose |
|---|---|---|
| GET | /invoice-summaries | Invoice list |
| GET | /invoice-summaries/:id | Invoice detail |
| POST | /invoice-summaries | Create invoice (scope: invoices.create) — use this path, not /invoices |
| GET | /collections | Collections queue |
| GET | /collections/:id | Collection detail |
| POST | /collections/:id/reconcile | Mark as paid |
| POST | /payments | Initiate payment (STUB) |
| GET | /payments | Payment list |
| POST | /payment-webhooks/jazzcash | JazzCash webhook (STUB) |
| POST | /payment-webhooks/easypaisa | Easypaisa webhook (STUB) |
| POST | /payment-webhooks/log | Log payment proof |
| GET | /subscriptions | Subscription list |
| GET | /subscriptions/:id | Subscription detail |
| POST | /subscriptions | Create subscription |
| PATCH | /subscriptions/:id | Update subscription |

**Frontend Pages:**
| Page ID | File | DUMMY_MODE |
|---|---|---|
| B-08 | collections.html | true |
| B-09 | invoices.html | true |
| C-08 | invoices-detail.html | true |
| A-06 | subscriptions-dashboard.html | true |
| C-09 | subscriptions-detail.html | true |
| H-04 | finance-analytics.html | true |
| G-04 | billing-settings.html | true (blocked P-016) |

**Permissions Required:**
- collections.read, collections.invoice, collections.reconcile
- payments.read, payments.create, payments.update
- invoices.create, revenue.read
- subscriptions.read, subscriptions.create, subscriptions.update
- billing.read, billing.create, billing.manage

**Validation Layer:**
- Payment method: must be jazzcash/easypaisa/bank_transfer
- stub_mode: JAZZCASH_STUB_MODE and EASYPAISA_STUB_MODE env vars checked at adapter startup
- amount: NUMERIC PKR (no foreign currency)

**Test Coverage:**
- Backend: `backend/tests/test_revenue_recognition.py`, `backend/tests/test_subscription_billing.py`, `backend/tests/test_usage_billing.py` (confirmed Phase 3.25)
- E2E: test_workflow_invoice.py — create invoice→send→simulate payment callback→status=paid

**Deployment Dependency:** transaction_db schema; render.yaml JAZZCASH_STUB_MODE=true (P-016 blocker); WF-002 seeded

---

## 5. Case / Ticket Management

**Feature:** Full support case lifecycle with SLA tiers, escalation, and knowledge linking
**Workflow:** WF-C (Case Lifecycle); WF-003 (SLA Breach Notification)

**Domain Entities:**
- Case, CaseComment, CaseEscalation, SupportQueue (case_ticket_db)
- Key fields: case_id, case_number, status (7 states), sla_tier (4 tiers), version_no, escalation_level (0–3)

**Backend Modules:**
- Python: `backend/src/ticket_management/`, `backend/src/support_console/`
- Gateway: `backend/gateway/routes/v1-cases.routes.js`

**API Endpoints (14 total):**
| Method | Path | Permission |
|---|---|---|
| GET | /cases | cases.read |
| POST | /cases | cases.create |
| GET | /cases/:id | cases.read |
| PATCH | /cases/:id | cases.update |
| POST | /cases/:id/assign | cases.admin |
| POST | /cases/:id/comments | cases.update |
| POST | /cases/:id/resolve | cases.update |
| POST | /cases/:id/close | cases.admin |
| POST | /cases/:id/reopen | cases.update |
| POST | /cases/:id/escalate | cases.admin |
| POST | /cases/:id/link-article | cases.update |
| GET | /support/queues | cases.read |
| POST | /support/queues | cases.admin |
| PATCH | /support/queues/:id | cases.admin |

**Frontend Pages:** cases.html (B-05), cases-detail.html (C-05), case-new.html (I-04), support-console.html (E-01), support-dashboard.html (A-07)

**Validation Layer:**
- version_no: OCC (409 CONFLICT on stale version)
- Reopen: 14-day window enforced (422 REOPEN_WINDOW_EXPIRED)
- State machine: transitions validated server-side
- SLA timers: set at creation based on sla_tier; cannot be overridden by user

**Test Coverage:**
- Backend: ticket_management, support_console tests in 79 test files
- E2E: test_datatable.py covers cases.html; test_audit_pages.py covers J-series adjacent pages
- WF-003: workflow execution evidence in exec-003/exec-008

**Deployment Dependency:** case_ticket_db schema; WF-003 seeded; knowledge_db for article linking

---

## 6. WhatsApp Conversation

**Feature:** Receive inbound WhatsApp messages, classify intent, route to agents, send responses
**Workflow:** WF-D (WhatsApp Conversation Workflow)

**Domain Entities:**
- Conversation, Message, Handoff, AgentPresence, InboxQueue (messaging_db)
- Contact (contact_account_db) — linked on phone lookup

**Backend Modules:**
- Python: `backend/src/omnichannel_inbox/`
- Adapters: `backend/adapters/pakistan/messaging/` (meta_api_adapter.py, gupshup_adapter.py, dialog360_adapter.py, twilio_adapter.py)
- Gateway: `backend/gateway/routes/v1-inbox.routes.js`, `v1-whatsapp-webhooks.routes.js`

**API Endpoints:**
| Method | Path | Notes |
|---|---|---|
| POST | /whatsapp-webhooks/meta | Inbound from Meta API |
| POST | /whatsapp-webhooks/gupshup | Inbound from Gupshup |
| POST | /whatsapp-webhooks/360dialog | Inbound from 360dialog |
| POST | /whatsapp-webhooks/twilio | Inbound from Twilio |
| GET | /whatsapp-webhooks/meta | Meta verification handshake |
| POST | /whatsapp-webhooks/log | Log raw webhook payload |
| GET | /inbox/conversations | Conversation list |
| GET | /inbox/conversations/:id | Conversation thread |
| POST | /inbox/conversations/:id/claim | Claim from pool |
| POST | /inbox/conversations/:id/messages | Send outbound |
| POST | /inbox/conversations/:id/handoff | Transfer to agent |
| PATCH | /inbox/presence | Update own presence |
| GET | /inbox/presence | View presence board (admin) |
| GET | /inbox/queues | Queue list |
| POST | /inbox/queues | Create queue |
| PATCH | /inbox/queues/:id | Update queue |
| GET | /inbox/queues/:id/stats | Queue metrics |

**Frontend Pages:** inbox.html (L-01), inbox-thread.html (L-02), engagement-dashboard.html (A-08 — Wired), routing-config.html (L-03)

**Permissions:** inbox.read, inbox.write, inbox.admin

**Validation Layer:**
- Agent capacity: claim fails if open_conversation_count >= max_concurrent (10)
- Handoff authority: non-supervisor can only handoff own conversations; supervisor can handoff any
- Idempotent webhooks: duplicate webhook payloads are deduplicated (event_bus dedup module)

**Test Coverage:**
- Backend: `backend/tests/test_omnichannel_inbox.py` (confirmed Phase 3.25)
- E2E: engagement-dashboard.html (A-08) is confirmed wired to live API

**Deployment Dependency:** messaging_db schema; WhatsApp Business API credentials (provider-specific); WHATSAPP_TOKEN env var on Render

---

## 7. AI-Assisted Actions

**Feature:** Lead scoring, churn prediction, CLV estimation, copilot suggestions, NL query
**Workflow:** Background scoring (scheduler); copilot query on user request

**Domain Entities:**
- LeadScore, ChurnPrediction, CLVEstimate, CopilotSuggestion, ScoringModel (intelligence_db)

**Backend Modules:**
- Python: `backend/src/ai_copilot/`, `backend/src/ai_scoring/`, `backend/src/predictive_models/`, `backend/src/predictive_forecasting/`
- Gateway: `backend/gateway/routes/v1-ai.routes.js`

**API Endpoints (13 total):**
| Method | Path | Purpose |
|---|---|---|
| GET | /ai/scores/leads | All lead scores |
| GET | /ai/scores/leads/:id | Lead score detail |
| POST | /ai/scores/leads/:id/recompute | Force recompute |
| GET | /ai/predictions/churn | Churn predictions |
| GET | /ai/predictions/churn/:id | Account churn detail |
| GET | /ai/estimates/clv | CLV estimates |
| GET | /ai/estimates/clv/:id | Account CLV detail |
| GET | /ai/copilot/suggestions | Get suggestions for user |
| POST | /ai/copilot/suggestions/:id/dismiss | Dismiss suggestion |
| POST | /ai/copilot/suggestions/:id/action | Mark actioned |
| POST | /ai/copilot/query | NL query → intent classification |
| GET | /ai/models | Model registry |
| GET | /ai/models/:key | Model detail |

**Frontend Pages:** ai-copilot.html (M-01 — blocked — no inference), ai-insights.html (M-02)

**Permissions:** ai.scores.read, ai.scores.recompute, ai.predictions.read, ai.clv.read, ai.copilot, ai.models.read

**Validation Layer:**
- All models: algorithm=rule_based (no ML inference); no external API calls
- Copilot query: NL query classified via regex intent engine (v1-ai.routes.js:138–166)
- Score range: 0–100 enforced

**Known Gap:** No AI inference provider SDK (no OpenAI/Anthropic/Google in requirements.txt). All "AI" is rule-based computation. M-01 is advisory-only shell blocked pending model selection.

**Test Coverage:** `backend/tests/test_ai_copilot.py`, `backend/tests/test_ai_scoring.py`, `backend/tests/test_predictive_models.py` (confirmed Phase 3.25)

**Deployment Dependency:** intelligence_db schema; no external AI provider dependency in current state

---

## 8. User Authentication and RBAC

**Feature:** Login, register, token refresh, logout, password reset; role-based access control
**Workflow:** Auth workflow is a prerequisite for all other workflows

**Domain Entities:**
- User, Role, Permission, Session, RefreshToken (identity_auth_db)
- Tenant (org_tenant_db)

**Backend:** Gateway-native (Node.js Express); no Python service for auth
**Gateway files:** `backend/gateway/routes/v1-auth.routes.js`, `backend/gateway/config/rbac-scopes.js`, `backend/gateway/middleware/auth-rbac.js`, `backend/gateway/middleware/jti-blocklist.js`

**API Endpoints (7 auth + 4 user/role management):**
| Method | Path | Auth Required | Purpose |
|---|---|---|---|
| POST | /auth/login | None | Login; returns JWT pair |
| POST | /auth/register | None | Create tenant + user + seed pipeline |
| POST | /auth/refresh | None (refresh token) | Rotate access token |
| POST | /auth/forgot-password | None | Send 6-digit OTP via email |
| POST | /auth/reset-password | None | Validate OTP + update password |
| DELETE | /auth/sessions/current | JWT | Logout via JTI revocation |
| GET | /users | users.read | User list |
| POST | /users | users.create | Invite user |
| PATCH | /users/:id | users.update | Update user status/role |
| GET | /roles | users.read | Role list |

**Frontend Pages:** authentication/login.html, authentication/register.html, authentication/forgot-password.html, user-management-crm.html (G-02), roles.html (G-03)

**RBAC Architecture:**
- JWT carries: role (string), scopes (string[]), role_ids (string[]), territory_ids (string[])
- Every route calls requireScopes([...]) middleware
- Default-deny: scope not in ROLE_SCOPES[role] = denied
- Tenant isolation: x-tenant-id header must match JWT tenant_id on every request

**Token specs:** Access: 15-min HS256 JWT; Refresh: 7-day rotating single-use; Revocation: Redis JTI blocklist

**Validation Layer:**
- Email: unique per tenant (DB constraint)
- Password: sha256:salt:hash (confirmed from v1-auth.routes.js — see API_INVENTORY.md §AUTH)
- OTP: 6-digit, 15-min TTL in Redis
- JTI blocklist checked on every protected request

**Test Coverage:**
- API contract: test_auth_contract.py — invalid JWT → 401, missing tenant → 403
- E2E: test_workflow_onboarding.py covers register flow

**Deployment Dependency:** identity_auth_db schema; Redis for JTI blocklist + OTP TTL; SENDGRID_API_KEY for email OTP (prod-only)

---

## 9. Multi-Tenant Isolation

**Feature:** Complete data isolation between tenant organizations at application layer
**Workflow:** Prerequisite for all workflows; enforced on every API request

**Architecture:** Application-level isolation (not PostgreSQL RLS)
- Every database table: tenant_id UUID NOT NULL column
- Every API request: x-tenant-id header validated against JWT tenant_id
- Every gateway query: WHERE tenant_id = $1 parameter binding
- CI enforcement: semgrep rule (.semgrep/tenant-isolation.yaml) checks every SQL statement binds tenant_id

**Backend Module:** gateway/middleware/auth-rbac.js (tenant validation); DB-level: every schema in db/*/schema.sql

**No dedicated API endpoints** — tenant isolation is middleware-level, not a feature route

**Evidence of isolation:**
- POST /auth/register inserts tenant_ref rows into 6 domain schemas in one transaction
- GET /admin/tenants: admin-only endpoint; shows all tenants (requires tenant_admin role)
- Every in-memory store / DB query example has `WHERE tenant_id = :tenant_id` pattern

**Test Coverage:** test_tenant_isolation.py — tenant A cannot read tenant B data

**Deployment Dependency:** All domain schemas with tenant_id FK; semgrep CI gate enforcing isolation

**Known Gap:** Isolation is application-level (not database RLS). See ARCHITECTURAL_GAP_REGISTER.md for ADR-002 discussion.

---

## 10. Automation / Workflow Engine

**Feature:** Event-driven automation with 5 system workflows and custom workflow builder
**Workflow:** WF-001 through WF-005 system workflows; custom workflows via builder

**Domain Entities:**
- WorkflowDefinition, WorkflowExecution, WorkflowStepRecord (workflow_db)

**Backend Modules:**
- Python: `backend/src/workflow_engine/`, `backend/src/automation_journeys/`
- Gateway: `backend/gateway/routes/v1-workflows.routes.js`

**API Endpoints (11 total):**
| Method | Path | Permission |
|---|---|---|
| GET | /workflows | workflows.read |
| POST | /workflows | workflows.manage |
| GET | /workflows/:id | workflows.read |
| PATCH | /workflows/:id | workflows.manage |
| POST | /workflows/:id/publish | workflows.manage |
| POST | /workflows/:id/simulate | workflows.read |
| GET | /workflows/:id/stats | workflows.read |
| GET | /workflows/runs | workflows.read |
| GET | /workflows/runs/:id | workflows.read |
| POST | /workflows/runs/:id/retry | workflows.manage |
| POST | /workflows/runs/:id/cancel | workflows.manage |

**Frontend Pages:** workflow-builder.html (K-01), workflows-dashboard.html (A-10), workflow-run-detail.html, workflow-analytics.html (H-05)

**Validation Layer:**
- System workflows: PATCH blocked (403 FORBIDDEN) — is_system=true workflows cannot be modified
- Publish: requires ≥1 step in steps_dsl
- Archive: terminal state — cannot be undone
- Retry: max_retries enforced; creates new child execution (not modifies original)
- Simulate: POST /workflows/:id/simulate — no side effects; returns simulated step results

**Test Coverage:** `backend/tests/test_workflow_automation.py`, `backend/tests/test_workflow_engine.py` (confirmed Phase 3.25); WF-001 through WF-005 also have execution evidence in gateway seed data (exec-001 through exec-008)

**Deployment Dependency:** workflow_db schema; event_bus module (src/event_bus/); 5 system workflows seeded via v1-workflows.routes.js startup seed

---

---

## 11. Accounts

**Feature:** Account list, account detail with AI insights (churn risk, CLV), linked contacts and opportunities
**Domain Entity:** Account (contact_account_db)

**Backend Module:**
- Python: `backend/src/customer_360_cdp/`
- Gateway: `backend/gateway/routes/v1-accounts.routes.js`

**API Endpoints:**
| Method | Path | Permission |
|---|---|---|
| GET | /accounts | accounts.read |
| POST | /accounts | accounts.create |
| GET | /accounts/:account_id | accounts.read |
| PATCH | /accounts/:account_id | accounts.update |

**Frontend Pages:** accounts.html (B-04), accounts-detail.html (C-03)
**Permissions:** accounts.read, accounts.create, accounts.update
**Deployment Dependency:** contact_account_db schema

---

## 12. Knowledge Base

**Feature:** Knowledge article management with 2-step publication workflow and case linking
**Domain Entity:** KnowledgeArticle (knowledge_db)

**Backend Module:**
- Python: `backend/src/knowledge_base/`
- Gateway: `backend/gateway/routes/v1-knowledge.routes.js`

**API Endpoints:**
| Method | Path | Permission |
|---|---|---|
| GET | /knowledge | knowledge.read |
| POST | /knowledge | knowledge.manage |
| GET | /knowledge/:article_id | knowledge.read |
| PATCH | /knowledge/:article_id | knowledge.manage |
| POST | /knowledge/:article_id/publish | knowledge.manage |

**Frontend Pages:** knowledge-article.html (C-12), knowledge-dashboard.html (A-09)
**Permissions:** knowledge.read, knowledge.manage
**Deployment Dependency:** knowledge_db schema; articles linked to Cases via POST /cases/:id/link-article

---

## 13. Marketing / Campaigns

**Feature:** Campaign builder (WhatsApp blast/email/SMS), segment management, campaign analytics
**Domain Entities:** Campaign, Segment (campaign_db)

**Backend Modules:**
- Python: `backend/src/campaigns/`, `backend/src/automation_journeys/`
- Gateway: `backend/gateway/routes/v1-campaigns.routes.js`, `v1-segments.routes.js`, `v1-templates.routes.js`, `v1-emails.routes.js`, `v1-communications.routes.js`

**API Endpoints (key routes):**
| Method | Path | Permission |
|---|---|---|
| GET | /campaigns | campaigns.read |
| POST | /campaigns | campaigns.manage |
| GET | /campaigns/:id | campaigns.read |
| PATCH | /campaigns/:id | campaigns.manage |
| POST | /campaigns/:id/activate | campaigns.manage |
| POST | /campaigns/:id/pause | campaigns.manage |
| POST | /campaigns/:id/cancel | campaigns.manage |
| GET | /campaigns/:id/sends | campaigns.manage |
| GET | /campaigns/:id/conversions | campaigns.manage |
| GET | /segments | campaigns.read |
| POST | /segments | campaigns.manage |
| GET | /communications/engagement | marketing.read |

**Frontend Pages:** campaign-builder.html (F-01), marketing-workspace.html (I-06), marketing-analytics.html (H-02)
**Permissions:** campaigns.read, campaigns.manage, marketing.read
**Known constraint:** Urdu WhatsApp templates require urdu_approved_by — blocked by P-017
**Deployment Dependency:** campaign_db schema; WhatsApp provider configured; v1-templates.routes.js for template management

---

## 14. Report Builder

**Feature:** Custom report definitions, saved queries, report execution, analytics dashboards
**Domain Entities:** No dedicated entity — reports execute queries over existing domain entities
**Backend Module:**
- Python: `backend/src/reporting_dashboards/`
- Gateway: `backend/gateway/routes/v1-reports.routes.js`

**API Endpoints:**
| Method | Path | Permission |
|---|---|---|
| GET | /reports/definitions | reports.read |
| POST | /reports/definitions | reports.create |
| POST | /reports/execute | reports.read |

**Frontend Pages:** report-builder.html (H-01 to H-07 — H-07 wired to live API)
**Permissions:** reports.read, reports.create
**Deployment Dependency:** All domain schemas (reports query across domains)

---

## 15. Territories

**Feature:** Territory definition, rule management, auto-assignment of leads, performance tracking
**Domain Entities:** Territory, TerritoryRule (territory_db)

**Backend Module:**
- Python: `backend/src/territory_management/`
- Gateway: `backend/gateway/routes/v1-territories.routes.js`

**API Endpoints (11 total):**
| Method | Path | Permission |
|---|---|---|
| GET | /territories | territories.read |
| POST | /territories | territories.admin |
| GET | /territories/assignments | territories.read |
| POST | /territories/assignments/evaluate | territories.read |
| POST | /territories/assignments/:id/reassign | territories.write |
| GET | /territories/:id | territories.read |
| PATCH | /territories/:id | territories.admin |
| DELETE | /territories/:id | territories.admin |
| POST | /territories/:id/rules | territories.admin |
| DELETE | /territories/:id/rules/:rule_id | territories.admin |
| GET | /territories/:id/performance | territories.read |

**Frontend Pages:** territory-config.html (G-09)
**Permissions:** territories.read, territories.write, territories.admin
**Validation Layer:** criteria_type must be one of: geographic/postal/account_segment/rep_assigned/hybrid
**Integration:** WF-004 (lead_assignment) fires on lead.created.v1; evaluates TerritoryRules automatically
**Deployment Dependency:** territory_db schema; WF-004 seeded

---

## 16. Partners

**Feature:** Partner management, deal registration, commission tracking and approval
**Domain Entity:** Partner (contact_account_db.partners)

**Backend Module:**
- Python: `backend/src/partner_channel_management/`
- Gateway: `backend/gateway/routes/v1-partners.routes.js`

**API Endpoints (13 total):**
| Method | Path | Permission |
|---|---|---|
| GET | /partners | partners.read |
| POST | /partners | partners.manage |
| GET | /partners/:id | partners.read |
| PATCH | /partners/:id | partners.manage |
| GET | /partners/:id/opportunities | partners.read |
| GET | /partners/:id/commissions | partners.manage |
| POST | /partners/:id/commissions/:cid/approve | partners.manage |
| POST | /partners/:id/commissions/:cid/pay | partners.admin |
| GET | /partners/:id/activity | partners.manage |
| POST | /partners/:id/deal-registrations | partners.manage |
| GET | /partners/:id/deal-registrations | partners.read |
| POST | /deal-registrations/:id/approve | partners.manage |
| POST | /deal-registrations/:id/reject | partners.manage |

**Frontend Pages:** partners.html (B-11), partners-detail.html (C-11)
**Permissions:** partners.read, partners.manage, partners.admin
**Deployment Dependency:** contact_account_db schema (partners table)

---

## 17. Audit & Compliance

**Feature:** Immutable audit log with hash-chain verification, data governance, SAR, privacy consent
**Domain Entities:** AuditLog (audit_compliance_db), FeatureFlag (feature_flag_db)

**Backend Module:**
- Python: `backend/src/admin_control_center/`
- Gateway: `backend/gateway/routes/v1-audit.routes.js`, `v1-governance.routes.js`, `v1-compliance-settings.routes.js`, `v1-privacy.routes.js`

**API Endpoints:**
| Method | Path | Permission |
|---|---|---|
| GET | /audit | audit.logs.read |
| GET | /audit/export | audit.logs.read |
| GET | /governance/classification | compliance.read |
| GET | /governance/retention | compliance.read |
| POST | /governance/sar | privacy.manage |
| GET | /compliance-settings | compliance.read |
| PATCH | /compliance-settings | compliance.read |
| GET | /privacy/consent | privacy.read |
| POST | /privacy/consent | privacy.manage |

**Frontend Pages:** audit-log.html (J-01), audit-export.html (J-02), data-governance.html (J-03 — wired), compliance-report.html (J-04), audit-dashboard.html (A-13)
**Permissions:** audit.read, audit.logs.read, compliance.read, privacy.read, privacy.manage
**Key constraint:** AuditLog is immutable (no UPDATE or DELETE); hash-chain integrity verified on every export
**Deployment Dependency:** audit_compliance_db schema; feature_flag_db schema

---

## 18. Settings / Administration

**Feature:** Org settings, WhatsApp/payment integration config, notification preferences, feature flags, tenant admin
**Domain Entities:** FeatureFlag (feature_flag_db)

**Backend Module:**
- Python: `backend/src/admin_control_center/`, `backend/src/design_system/`
- Gateway: `backend/gateway/routes/v1-org-settings.routes.js`, `v1-integrations.routes.js`, `v1-feature-flags-mgmt.routes.js`, `v1-notification-preferences.routes.js`

**API Endpoints:**
| Method | Path | Permission |
|---|---|---|
| GET | /org-settings | integrations.read |
| PATCH | /org-settings | integrations.manage |
| GET | /integrations | integrations.read |
| PATCH | /integrations/:provider | integrations.manage |
| POST | /integrations/:provider/test | integrations.manage |
| GET | /admin/feature-flags | users.read |
| PATCH | /admin/feature-flags/:flag_id | users.update |
| GET | /notification-preferences | any (JWT required) |
| PATCH | /notification-preferences | any (JWT required) |
| GET | /tenants/current | users.read |

**Frontend Pages:** org-settings.html (G-01), integrations.html (G-05 — wired), notifications.html (G-06), feature-flags.html (G-07), tenant-admin.html (G-08)
**Permissions:** integrations.read, integrations.manage, users.read, users.update
**Key constraint:** Feature flags with requires_dual_approval=true need 2 approvals to toggle
**Deployment Dependency:** feature_flag_db schema; WhatsApp provider credentials; P-017 blocks Urdu notifications

---

## 19. Identity & Access Management

**Feature:** User directory, role management, RBAC permission matrix
**Domain Entities:** User, Role, Permission (identity_auth_db)

**Backend Module:** Gateway-native (Node.js); Python `backend/src/role_based_ui/`
**Gateway files:** `backend/gateway/routes/v1-users.routes.js`, `v1-roles.routes.js`

**API Endpoints:**
| Method | Path | Permission |
|---|---|---|
| GET | /users | users.read |
| POST | /users | users.create |
| GET | /users/:id | users.read |
| PATCH | /users/:id | users.update |
| POST | /users/:id/assign-role | users.manage_roles |
| GET | /roles | users.read |
| POST | /roles | users.update |
| PATCH | /roles/:id | users.update |
| DELETE | /roles/:id | users.update |

**Frontend Pages:** user-management-crm.html (B-10), user-management-settings.html (G-02), roles.html (G-03), identity-dashboard.html (A-12)
**Permissions:** users.read, users.create, users.update, users.manage_roles
**Deployment Dependency:** identity_auth_db schema

---

## 20. Subscriptions / Billing (Platform)

**Feature:** Tenant billing subscription management, invoice history, billing plan changes
**Domain Entities:** Subscription, Invoice (transaction_db)

**Backend Module:**
- Python: `backend/src/subscription_billing/`
- Gateway: `backend/gateway/routes/v1-billing.routes.js`

**API Endpoints:**
| Method | Path | Permission |
|---|---|---|
| GET | /billing/subscription | billing.read |
| GET | /billing/invoices | billing.read |
| POST | /billing/subscription | billing.create |
| PATCH | /billing/subscription | billing.manage |

**Frontend Pages:** billing-settings.html (G-04 — wired but content blocked P-016)
**Permissions:** billing.read, billing.create, billing.manage
**Note:** Distinct from customer-facing subscriptions at /subscriptions. This is the platform billing for CRM tenants.
**Deployment Dependency:** transaction_db schema; P-016 blocks live payment integration

---

## 21. Builder Tools

**Feature:** Custom object builder, rule builder, approval lanes builder
**Backend Module:** `backend/src/custom_object_framework/`, `backend/src/custom_objects/`, `backend/src/rule_engine/`
**Gateway:** CONFIRMED NO ROUTE for custom_objects (v1-custom-objects.routes.js absent). D-002 CLOSED (Phase 3.25).

**C6 Build Posture:** K-02 (object-builder.html) is a C6 **advisory shell** — confirmed by:
- `FEATURE_SCOPE.md` Module 22 Feature 129: "Custom object builder" Status = Built (advisory shell)
- `DESIGN-SPEC.md` line 204: K-02 Browser-approved as Cat 2
- No gateway route needed for advisory shell; crm-dummy.js data only

**API Endpoints:** No live API connectivity in C6. K-02 uses crm-dummy.js. Rule builder (K-03) and approval lanes (K-04) similarly use stub data in C6.

**Frontend Pages:** object-builder.html (K-02), rule-builder.html (K-03), approval-lanes.html (K-04)
**Permissions:** tenant_owner / tenant_admin only (inferred from admin-level nature; no gateway route guard to verify against in C6)
**Resolution:** D-002 CLOSED. K-02 is advisory shell in C6. Backend connectivity (v1-custom-objects.routes.js) is a C7 activation task.

---

## 22. Forecasting

**Feature:** Pipeline forecast aggregation by stage and forecast category; forecast refresh on opportunity stage change
**Domain Entity:** Forecast (computed — not persisted; derived from Opportunity data)

**Backend Module:**
- Python: `backend/src/predictive_forecasting/`
- Gateway: `backend/gateway/routes/v1-forecasts.routes.js`, `backend/gateway/services/forecasting.js`

**API Endpoints:**
| Method | Path | Permission |
|---|---|---|
| GET | /forecasts | forecasts.read |
| POST | /forecasts/model | forecasts.read |
| POST | /forecasts/aggregate | forecasts.read |

**Frontend Pages:** sales-dashboard.html (A-04 — forecast panel)
**Permissions:** forecasts.read
**Integration:** WF-005 (opportunity_stage_notify) triggers forecast refresh on opportunity.stage.changed.v1
**Validation Layer:** forecast_category must be one of: pipeline/best_case/commit/closed/omitted; category weights: pipeline=0.25, best_case=0.50, commit=0.75, closed=1.00, omitted=0.00
**Deployment Dependency:** opportunity_db schema (forecast computed from Opportunity records); predictive_forecasting Python module

---

---

## Phase 2 Backend Authority Capture Update — 2026-06-22

The following updates were applied as part of Phase 2 Backend Authority Capture. All reflect extraction from implementation code, not design changes.

### Confirmed facts (updated from code read)

| Topic | Previous status | Confirmed value |
|---|---|---|
| DB schema count | "20 schemas" in earlier docs | 18 confirmed schemas |
| Gateway route files | "44 v1-*.routes.js files" | Confirmed 44 |
| Alembic migrations | TBD | 12 migrations (0001-0012) |
| AI inference provider | Unconfirmed | NONE — all models are rule_based |
| JTI blocklist | Redis assumed | In-memory Set only (security risk) |
| Payment providers | "JazzCash + Easypaisa" | Both STUB (stub_mode=True) |
| WhatsApp providers | "4 providers" | Meta, Gupshup, 360dialog, Twilio — adapters confirmed |
| asyncio background tasks | Unconfirmed | 2: overdue scanner (60s), daily summary (daily) |
| Idempotency ledger (Python) | Unconfirmed | GlobalIdempotencyLedger (in-memory, thread-safe) with EvictionWorker daemon thread |
| Outbox pattern | Unconfirmed | Table defined (transaction_db.outbox_event); publisher NOT confirmed |
| contacts.delete scope gap | Identified | CONFIRMED — scope absent from SCOPES constant; all roles blocked from DELETE /contacts |

### New documentation produced (Phase 2)

**docs/01_backend/:**
- BACKEND_ARCHITECTURE.md
- DATABASE_SCHEMA.md
- API_CONTRACT.md
- ERROR_CONTRACT.md
- SERVICE_CATALOG.md
- INTEGRATION_CATALOG.md
- VALIDATION_RULES.md
- EVENT_AND_QUEUE_ARCHITECTURE.md

**docs/03_fullstack_contracts/:**
- AUTH_AND_TENANCY_CONTRACT.md
- USER_ROLES_AND_PERMISSIONS.md
- DATA_SHAPE_REGISTRY.md
- VALIDATION_PARITY.md
- CONTRACT_VERSION_REGISTRY.md

**docs/08_reports/:**
- BACKEND_AUTHORITY_CAPTURE_REPORT.md
- BACKEND_ARCHITECTURE_REPORT.md
- DATABASE_DISCOVERY_REPORT.md
- API_DISCOVERY_REPORT.md
- SECURITY_DISCOVERY_REPORT.md
- EVENT_DISCOVERY_REPORT.md
- BACKEND_GAP_REGISTER.md
- BACKEND_RISK_REGISTER.md

---

*End FULLSTACK_STITCHING_CONTRACT.md*
