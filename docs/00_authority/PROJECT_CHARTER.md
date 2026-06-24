Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: Human

---

# PROJECT CHARTER — Pakistan CRM OS

## 1. Project Name and Purpose

**Project:** Pakistan CRM OS
**Purpose:** A multi-tenant SaaS CRM platform built specifically for Pakistani SME businesses. The system is designed to operate as an execution platform — enforcing business rules (follow-up deadlines, payment collection, SLA escalation) rather than merely storing data. It closes the gap between how Pakistani SMBs actually work (WhatsApp-first, PKR-denominated, informal sales workflows) and the tooling they have available (generic Western CRM products that do not fit their context).

**Evidence:** crm-components.js `pkr()` formatter; E.164 +923xx phone validation; JazzCash/Easypaisa payment adapters; WhatsApp-first interaction model documented in ADR-003.

---

## 2. Target Market

**Primary:** Pakistani SME businesses (Small and Medium Enterprises)
**Geography:** Pakistan (primary); architecture supports multi-country expansion without core changes
**Currency:** PKR (Pakistani Rupee) — Lakh/Crore formatting; no multi-currency in v1
**Communication channel:** WhatsApp-first; users do not adopt new communication tools for software
**Phone format:** E.164 with PK country code (+923xx)
**Language:** English primary; Urdu RTL support built (styles-rtl.css, crm-locale.js); Urdu strings pending native speaker review (P-017)
**Data region:** Singapore (Render.com) — closest region to Pakistan

**Who the users are (7 canonical roles):**
- `tenant_owner` — business owner; full access
- `tenant_admin` — IT/operations lead; full admin minus leads.delete
- `manager` — sales/support manager; full CRM operations
- `agent` — sales agent or support agent; day-to-day CRM
- `analyst` — read-only across all CRM data plus AI models
- `auditor` — read-only on audit, payments, revenue, collections
- `integration_service` — machine service account; full access

---

## 3. Core Value Proposition

Pakistani SMBs lose leads and revenue because:
1. WhatsApp conversations are never captured — leads fall through gaps
2. Follow-ups are tracked in notebooks or memory — no enforcement
3. Collections are manual — no automated reminders via WhatsApp
4. No visibility into pipeline, SLA compliance, or revenue trends

Pakistan CRM OS solves all four:
- Auto-creates Contacts and Leads from inbound WhatsApp messages
- Enforces follow-up tasks with escalation ladder (4 levels)
- Sends WhatsApp payment reminders automatically on overdue invoices
- Provides dashboards for pipeline, SLA, collections, and AI-based forecasting

**Value delivery target:** First WhatsApp message processed + first deal stage moved = aha-moment. Target: value within 10 minutes of onboarding. Source: ADR-003, activation-model.md.

---

## 4. Product Scope

### In-Scope (v1 — all built)
- Lead management with follow-up enforcement
- Contact and Account management (Customer 360)
- Sales pipeline / Opportunities
- CPQ (Configure-Price-Quote) with approval routing
- Finance: invoices, collections, PKR payments (JazzCash/Easypaisa adapters built; live credentials blocked by P-016)
- Subscriptions and recurring billing
- Case/ticket management with SLA tiers
- Knowledge base
- Omnichannel inbox (WhatsApp primary, email)
- Marketing campaigns and segments
- Workflow automation engine (event-driven, 5 system workflows WF-001 to WF-005 is_system=true + custom; separately, 5 business workflow archetypes WF-A to WF-E are documentation-only end-to-end journey maps — see PRODUCT_WORKFLOWS.md)
- AI copilot (rule-based advisory; inference model not yet selected)
- Lead scoring, churn prediction, CLV estimation (all rule-based)
- Report builder
- Territory management
- Partner channel management
- Identity and access management (7 roles, 91 scopes)
- Audit and compliance (hash-chain immutable log)
- Admin and settings (org, integrations, feature flags, notifications)
- Custom object builder
- Rule and approval builder

### Explicitly Out of Scope (v1)
- Facebook/Instagram lead capture — blocked by Meta Business Manager setup (MR-001)
- Voice note transcription — no transcription provider selected (MR-003)
- Kuickpay payment adapter — no API credentials (MR-007)
- SMS (non-WhatsApp) — no SMS gateway adapter
- AI inference backend — no OpenAI/Anthropic/Google SDK; models are rule-based
- Multi-currency — PKR only in v1
- Native mobile app — browser-based only; responsive for mobile
- Multi-country adapters beyond Pakistan — architecture ready but not implemented

### Deferred (blocked externally)
- JazzCash/Easypaisa live integration — blocked P-016 (credentials not yet received)
- Urdu customer-facing strings — blocked P-017 (native speaker review pending)

---

## 5. Current Status

**Phase:** C6 — Commercial Launch
**As of:** 2026-06-21

| Layer | Status |
|---|---|
| Frontend HTML pages | 75/75 custom pages built and browser-approved |
| Backend Python modules | 34 FastAPI modules built |
| Gateway API routes | 44 route groups, 228 endpoints |
| Database schemas | 20 domain schemas + 12 Alembic migrations applied (local) |
| CI/CD pipeline | GitHub Actions — 11 jobs; Render.com deploy configured |
| Deployment | Render.com — 3 services + PostgreSQL + Redis live on free tier |
| Test suite | 79 backend pytest files + 23 Playwright E2E files + 8 API contract tests |
| Frontend-to-API wiring | 5 pages confirmed wired; remainder use DUMMY_MODE graceful fallback |
| Payment rails | Stub mode only (P-016 blocker) |
| AI inference | Not implemented — rule-based models only |

**Phase history:**
- C0 (Environment Seal): COMPLETE 2026-05-31
- C1 (DB Wiring): COMPLETE 2026-05-31
- C2 (Automated Test Suite): COMPLETE 2026-06-01
- C3 (Code Hardening): COMPLETE 2026-06-01
- C4 (Infrastructure Deployment): COMPLETE 2026-06-01
- C5 (Post-Deploy Smoke + Production Sign-Off): COMPLETE 2026-06-02
- C6 (Commercial Launch): CURRENT

---

## 6. Stakeholders

Inferred from COMMERCIALISATION-PLAN.md and repository structure:

| Stakeholder | Role | Interest |
|---|---|---|
| synteracloud (Git user) | Project lead / owner | Full product control; all human decisions |
| Tenant owners (customers) | End-users | CRM operations, WhatsApp integration, PKR billing |
| Tenant agents/managers | End-users | Day-to-day CRM, lead management, case resolution |
| Integration partners | Technical | WhatsApp Business API, JazzCash, Easypaisa |
| Render.com | Infrastructure | Hosting; 3 services + DB + Redis |

---

## 7. Commercial Model

Source: COMMERCIALISATION-PLAN.md; backend/docs/product/pricing-plans.md (exists in repository)

- **Deployment model:** Multi-tenant SaaS (application-level tenant isolation)
- **Self-registration:** POST /auth/register creates tenant, seeds default pipeline, returns JWT
- **Plans:** Starter plan mentioned in schema (tenant.plan field); full plan structure in pricing-plans.md
- **Payment collection from customers:** JazzCash/Easypaisa adapters built and tested; currently in STUB mode (OA-003 — vendor credentials pending). Stub mode IS the C6 production behavior. Live activation requires merchant account credentials (2–4 week vendor process). Platform billing for CRM subscriptions tracks via subscription_billing module; monetization model is subscription + usage-based per COMMERCIALISATION-PLAN.md.
- **Regional focus:** Pakistan SMB market first; architecture supports expansion to other countries

---

## 8. Success Metrics

Source: COMMERCIALISATION-PLAN.md, backend/docs/product/activation-model.md

- **Activation metric:** First WhatsApp message processed + first deal stage moved within 10 minutes of onboarding
- **Lead capture:** Zero lead slippage from WhatsApp (auto-create Contact + Lead on inbound message)
- **Follow-up compliance:** No lead idle beyond configured threshold (enforced by WF-001)
- **Collections efficiency:** 98% invoice-to-payment match rate target (Collections Engine spec)
- **SLA compliance:** 99.5% SLA reminder delivery (SLA Engine spec)
- **Coverage gate:** 80% backend test coverage (enforced in CI)
- **Uptime:** Render.com deployment with Redis + PostgreSQL managed services
- **Additional commercial KPIs:** Revenue from subscription plans (Starter/Growth/Enterprise tiers per COMMERCIALISATION-PLAN.md); seat-based pricing; payment processing activation (OA-003); Urdu campaign activation (G-MED-005)

---

## 9. Frozen Decisions

These decisions are made, architectural, and must not be changed without explicit human sign-off:

| Decision | Rationale | Source |
|---|---|---|
| PKR as primary currency — no multi-currency in v1 | Pakistan SMB market; Lakh/Crore formatting already built | ADR-003; crm-components.js |
| WhatsApp as primary communication channel | Pakistan SMBs run on WhatsApp; zero-friction adoption | ADR-003 |
| FastAPI (Python) backend | Domain service layer; async; SQLAlchemy ORM | Architecture-overview.md |
| Express.js API gateway (Node.js) | Gateway layer; 44 route groups implemented | gateway/app.js |
| PostgreSQL 14 database | 20 domain schemas; Alembic migrations | render.yaml; db/ |
| Redis for token store + rate limiting | JWT JTI blocklist; rate-limit middleware | render.yaml; gateway/middleware/ |
| NexLink CSS framework for frontend | 96 library pages + 75 custom pages built on it | FRAMEWORK.md |
| JWT (HS256) + Redis authentication | 15-min access + 7-day refresh; JTI revocation | gateway/config/rbac-scopes.js |
| Multi-tenant: application-level isolation | x-tenant-id header on every request; every SQL binds tenant_id | backend/docs/security/org-multi-tenancy.md |
| Render.com deployment | 3 services + managed PostgreSQL + Redis | render.yaml |
| DDD + L1/L2/L3 adapter pattern | Country isolation; core/* cannot import adapters/pakistan/* | ADR-001; ADR-002 |
| Default-deny RBAC (91 scopes) | Every ungranted scope denied; no implicit access | gateway/config/rbac-scopes.js |
| JAZZCASH_STUB_MODE=true until P-016 resolved | No live payment calls without verified sandbox E2E | CONSTRAINTS.md C-009 |

---

*End PROJECT_CHARTER.md*
