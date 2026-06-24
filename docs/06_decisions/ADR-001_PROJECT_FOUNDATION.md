Status: Draft
Authority Level: High
Last Reviewed: 2026-06-21
Owner: Human

---

# ADR-001 — Project Foundation Architecture

**Date:** 2026-05-18 (original decisions); updated 2026-06-21 (governance expansion)
**Status:** Accepted
**Deciders:** synteracloud (project owner)

## Source

This document incorporates and expands upon three existing ADR files:
- `backend/docs/adr/ADR-001.md` — DDD + Microservices Architecture (2026-05-18)
- `backend/docs/adr/ADR-002.md` — Adapter Pattern for Pakistan Market Isolation (2026-05-18)
- `backend/docs/adr/ADR-003.md` — WhatsApp-First Interaction Model (2026-05-18)

---

## 1. Project Purpose

Pakistan CRM OS is a multi-tenant SaaS CRM built for Pakistani SME businesses. It is an execution platform, not a data store — the system enforces business rules (follow-up deadlines, payment collection, SLA escalation) across multiple domains that have different lifecycles and scaling requirements.

**Key differentiation from generic CRM products:**
- Operates natively in PKR (Pakistani Rupee) with Lakh/Crore formatting
- WhatsApp is the primary interaction layer (not an integration) — this is how Pakistani SMBs actually work
- JazzCash and Easypaisa are the primary payment rails (not Stripe or PayPal)
- Urdu language support is built into the architecture (RTL CSS, locale engine)
- Multi-tenant from the ground up with application-level isolation

---

## 2. Current Architecture

```
Frontend (Static HTML/CSS/JS — NexLink framework)
    ↕ Bearer JWT + x-tenant-id header
API Gateway (Node.js Express — 44 route groups, 228 endpoints)
    ↕ HTTP (localhost:5002 in dev; internal on Render)
Python Services (FastAPI — 34 domain modules)
    ↕ SQLAlchemy ORM
PostgreSQL 14 (20 domain schemas) + Redis (JWT JTI blocklist, rate limiting, OTP TTL)
```

**Deployment:** Render.com (5 services: gateway + services + frontend static + managed PostgreSQL + managed Redis)
**CI/CD:** GitHub Actions (11 jobs: lint, test at 80%, security scan, Docker build ×2, staging deploy, smoke, prod deploy)

---

## 3. Core Technology Choices and Rationale

### 3.1 DDD + Microservices (from ADR-001)

**Decision:** Domain-Driven Design across three strict layers:
- L1 — Core (domain models, business logic, engine implementations; country-agnostic)
- L2 — Interfaces (adapter contracts: MessagingAdapter, PaymentAdapter, etc.)
- L3 — Adapters (country/provider-specific implementations)

**Rationale:** Domains have different lifecycles and scaling needs (Follow-up cadence ≠ Collections cadence ≠ WhatsApp throughput). Monolith would entangle these. Six platform-owned engines handle cross-domain concerns: Follow-up, Collections, WhatsApp, Activity Control, Activation, Execution Control Plane.

**Enforcement:** ruff import rules (CI enforced); `core/*` → `adapters/pakistan/*` is FORBIDDEN

**Evidence:** `backend/docs/architecture/architecture-overview.md`, ADR-001

### 3.2 Adapter Pattern for Pakistan Market Isolation (from ADR-002)

**Decision:** All Pakistan-specific logic lives exclusively in `adapters/pakistan/`. Core interacts only with stable interface contracts in `adapters/interfaces/`.

**Adapters implemented:**
| Interface | Implementations |
|---|---|
| MessagingAdapter | Meta API, 360dialog, Gupshup, Twilio (all 4 built) |
| PaymentAdapter | JazzCash (stub), Easypaisa (stub) |
| ComplianceAdapter | Pakistan compliance hooks |
| PhoneFormatter | E.164 Pakistan formatter (+923xx) |
| LocaleAdapter | PKR formatting, Urdu locale |

**Rationale:** Adding a new country = new adapters/<country>/ directory + zero Core changes. JazzCash API change only touches adapters/pakistan/payments/jazzcash.py.

**Enforcement:** ruff import rule; `core/*` → `adapters/pakistan/*` caught in CI

**Evidence:** ADR-002, `backend/docs/adapters/pakistan-adapter-architecture.md`

### 3.3 WhatsApp-First Interaction Model (from ADR-003)

**Decision:** WhatsApp is the primary interaction layer, not a CRM integration.

**Concrete implications:**
1. Inbound WhatsApp messages auto-create Contacts and Leads (no manual entry required)
2. Follow-up reminders and collection notices are sent via WhatsApp first (not email)
3. The browser UI is a management + reporting layer, not the primary data entry surface
4. Provider abstraction via MessagingAdapter ensures no coupling to any single WhatsApp API

**Target activation metric:** Value delivered within 10 minutes of onboarding (first WhatsApp message processed + first deal stage moved)

**Rationale:** Pakistan SMB users do not change their communication habits for software. The software adapts to them.

**Evidence:** ADR-003, `backend/docs/adapters/whatsapp-execution-model.md`, `backend/docs/product/activation-model.md`

### 3.4 FastAPI (Python) for Domain Services

**Decision:** All domain service logic is implemented in Python 3.12 using FastAPI.

**Rationale:**
- Async support for high-throughput inbox/webhook scenarios
- SQLAlchemy ORM with Alembic migrations for schema management
- Rich ecosystem for data processing (Pandas available if needed for analytics)
- Type annotation support for entity and service layer clarity

**Evidence:** backend/src/ (34 module directories); requirements.txt; Dockerfile.services

### 3.5 Express.js (Node.js) API Gateway

**Decision:** A dedicated Node.js Express gateway handles all frontend↔backend traffic.

**Rationale:**
- Gateway separates auth/RBAC enforcement from business logic
- Node.js handles JWT parsing and scope checking without Python overhead
- Single entry point for all 44 route groups; simplifies CORS, rate limiting, security headers
- Gateway can be independently deployed and scaled

**Evidence:** backend/gateway/app.js; 44 v1-*.routes.js files

### 3.6 PostgreSQL 14 + Redis

**Decision:** PostgreSQL for all persistent data; Redis for ephemeral state.

**PostgreSQL responsibilities:** 20 domain schemas; 12 Alembic migrations; full relational data model; optimistic concurrency via version_no; soft deletes via deleted_at; immutable append-only tables (AuditLog, LeadHistory)

**Redis responsibilities:** JWT JTI blocklist (token revocation); rate limiting (in-memory token buckets replaced by Redis in C3); OTP TTL (6-digit forgot-password tokens, 15-min TTL); FeatureFlag evaluations cache (60s TTL, C3)

**Evidence:** render.yaml (crm-postgres, crm-redis); backend/db/ (20 schema directories); alembic/versions/

### 3.7 NexLink CSS Framework (Frontend)

**Decision:** All frontend pages use NexLink CSS framework built on top of Bootstrap 5.

**Rationale:** 96 NexLink library pages already built and retained as reference. Custom design phase (75 pages) extends NexLink with crm-custom.css overrides. Not switching frameworks.

**Evidence:** FRAMEWORK.md; frontend/src/app/*.html (all 169 pages use NexLink)

### 3.8 Application-Level Multi-Tenancy

**Decision:** Tenant isolation enforced at application layer via x-tenant-id header + every SQL binding tenant_id. Not using PostgreSQL Row-Level Security (RLS).

**Rationale:**
- Application-level isolation is simpler to implement and debug
- All queries already bind tenant_id; isolation is consistent
- RLS adds complexity with SQLAlchemy ORM integration

**Known trade-off:** Application bugs could theoretically bypass isolation (vs RLS which enforces at DB level). Mitigated by semgrep CI rule that blocks any SQL statement missing tenant_id binding.

**Evidence:** gateway/middleware/auth-rbac.js; .semgrep/tenant-isolation.yaml; ADR documentation in backend/docs/security/org-multi-tenancy.md

---

## 4. Known Constraints (Pakistan Market)

These are constraints imposed by the target market, not by design choices.

| Constraint | Details |
|---|---|
| WhatsApp Business API approval | Meta requires business verification before production API access. Sandbox works immediately; production requires ~1 week approval. |
| JazzCash integration | JazzCash provides sandbox credentials separately from production. P-016 blocker is specifically the credentials + full sandbox E2E test requirement. |
| Easypaisa integration | Same as JazzCash — separate sandbox credentials required. |
| Urdu strings | Requires native speaker review before any customer-facing Urdu text goes live. P-017 blocker. |
| Pakistan phone format | All phone numbers must be E.164 with +92 country code. Formatter is built (PhoneFormatter adapter). |
| PKR formatting | Lakh/Crore number system (not Western thousands). pkr() formatter in crm-components.js handles this. |
| PTA compliance | Pakistan Telecommunications Authority regulations apply to WhatsApp message content. Compliance adapter hooks are built (`adapters/pakistan/messaging/` with compliance checks). Full PTA compliance details require legal review — LEGAL/REGULATORY decision (cannot be resolved from code). |
| FBR (tax) compliance | Federal Board of Revenue requirements for invoice formatting. Invoice module is built with PKR + NUMERIC(18,2) amounts. Full FBR formatting compliance requires legal/accounting review — LEGAL/REGULATORY decision (cannot be resolved from code). |

---

## 5. Major Assumptions

These are assumptions the architecture makes that must be validated for the system to work correctly.

| Assumption | Risk if Wrong |
|---|---|
| Pakistani SMBs will adopt WhatsApp-triggered CRM workflows | If users still prefer manual data entry, the activation model (first WhatsApp + first deal = aha) would need rethinking |
| JazzCash and Easypaisa APIs are stable and well-documented | Adapter brittleness if API changes without notice |
| Single-region deployment (Singapore) is acceptable latency for Pakistan | If latency > 300ms causes user complaints, need Pakistan or Middle East region (not currently available on Render free tier) |
| 4 WhatsApp provider options (Meta, Gupshup, Dialog360, Twilio) covers the market | If a new dominant provider emerges, a new adapter is needed |
| Rule-based AI models are acceptable advisory outputs | If customers expect ML-grade accuracy, AI inference model selection (D-004) becomes urgent |
| Application-level tenant isolation is sufficient | If audit requires DB-level RLS, architectural change needed |
| SQLAlchemy ORM + gateway JS queries can maintain tenant isolation without RLS | A bug in either layer could expose cross-tenant data |

---

## 6. Known Risks (from U9 Test Planning)

| Risk | Severity | Mitigation |
|---|---|---|
| python-jose CVE in transitive dependency | Medium | 3.5.0 installed (resolved); monitor pip-audit on each deploy |
| starlette CVEs (3 known) | Medium | Accepted risk; FastAPI 0.115 compat constraint; monitor for upstream fix |
| Payment stub mode in production | High | JAZZCASH_STUB_MODE=true enforced; P-016 blocks going live; cannot accidentally enable |
| WhatsApp rate limiting | Medium | WF-002 has max_retries=3 with backoff; collections exec-002/exec-005 show retry behavior |
| C: drive writes (tool caches) | High (local) | C0 seal active; .env.local loaded at session start |
| No AI inference backend | Medium | M-01 is advisory-only; rule-based models work but accuracy is limited |
| Cross-tenant data leakage | Critical | semgrep CI rule enforces tenant_id binding; test_tenant_isolation.py tests this |
| Load capacity unknown | Medium | Load tests in C2d define p95 targets; free Render tier may need scaling |
| psycopg2-binary minor version drift | Low | No CVEs; forward-patch only; acceptable |

---

## 7. Architectural Principles

These principles govern all design and implementation decisions.

| Principle | Rule |
|---|---|
| Multi-tenancy first | Every entity has tenant_id; every query binds it; isolation is not optional |
| API-first | Browser UI and future mobile app both call the same API; no server-rendered HTML |
| WhatsApp-native | WhatsApp is an input/output channel, not a notification afterthought |
| PKR-native | All monetary values are PKR NUMERIC; no currency conversion |
| Adapter isolation | Core business logic never imports country-specific code |
| Default-deny RBAC | No implicit permission grants; every scope must be explicitly assigned |
| Immutable audit | AuditLog and LeadHistory are append-only; no modifications ever |
| Soft delete by default | CRM entities use deleted_at or status flags; no hard DELETE on domain data |
| Fail-safe stubs | Payment adapters default to stub_mode=True; WhatsApp has DUMMY_MODE fallback |
| Execution idempotency | Idempotency key (tenant_id + method + route + key) prevents duplicate processing |

---

## 8. Relationship to Other ADRs

| ADR | Topic | Status |
|---|---|---|
| ADR-001 (original) | DDD + Microservices | Accepted — incorporated into this document |
| ADR-002 (original) | Adapter Pattern | Accepted — incorporated into this document |
| ADR-003 (original) | WhatsApp-First Model | Accepted — incorporated into this document |
| ADR-006 (governance) | Multi-tenancy isolation strategy | Recommended — see RECOMMENDED_ADR_ROADMAP.md (renumbered from ADR-002-governance to avoid collision with original ADR-002) |
| ADR-007 (governance) | AI inference model selection | Recommended — see RECOMMENDED_ADR_ROADMAP.md (renumbered from ADR-003-governance to avoid collision with original ADR-003) |
| ADR-008 (governance) | Payment gateway production integration | Recommended — see RECOMMENDED_ADR_ROADMAP.md (renumbered from ADR-004-governance) |
| ADR-009 (governance) | WhatsApp Business API provider selection | Recommended — see RECOMMENDED_ADR_ROADMAP.md (renumbered from ADR-005-governance) |

---

*End ADR-001_PROJECT_FOUNDATION.md*
