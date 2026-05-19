# Pakistan CRM OS — Rebuild Plan (10/10 Roadmap)

**Created:** 2026-05-18
**Revised:** 2026-05-19 — Phases restructured after tri-register gap audit
**Status:** Phase 1 — COMPLETE ✓ | Phase 2 — COMPLETE ✓ | Phase 3 — COMPLETE ✓ | Phase 4 — NOT STARTED | Phase 5 — NOT STARTED | Phase 6 — NOT STARTED
**Anchor:** This file. Update on every phase start and completion.
**Task tracker:** `PENDING.md` (root) — checkbox list, updated as work completes
**Session log:** `PROGRESS.md` — updated every session
**Estimated total duration:** ~21 weeks

---

## Gap Register State (as of 2026-05-19)

Three audits completed. All tasks flow through `PENDING.md`.

| Register | Anchor | Gaps | PENDING.md location |
|---|---|---|---|
| Phase 1–3 Code Audit | DOC-CATALOGUE.md (90 docs) vs backend code | 44 gaps — 8 Critical · 15 High · 15 Medium · 6 Low | §Phase 4 Sprints 1–5 |
| Product Spec Audit | PRODUCT-SPEC.md vs repo .md files | 17 gaps — 3 Phase-5 blockers · 4 arch · 3 feature · 7 MR | §Phase 4 Sprint 0 + §Phase 6 |
| Market Research Audit | Manus AI Pakistan market report vs system | 7 gaps — 2 buildable · 5 blocked/low | §Phase 6 |

**Source files:** `backend/product-spec-gap-register.md` · `backend/market-research-gap-register.md`

---

## Current State vs Target

| Area | Current | Target | Gap |
|---|---|---|---|
| Documentation | 9/10 | 10/10 | 10 product-spec docs missing (PS-001–PS-010) |
| Architecture design | 8/10 | 10/10 | Code must match docs; event bus; service boundaries in code |
| Project structure | 7/10 | 10/10 | Docker, Makefile, pre-commit, Alembic |
| Code implementation | 7/10 | 10/10 | 44 audit gaps; 8 critical (no DB persistence, no RBAC, broken JWT) |
| Testing | 5/10 | 10/10 | 308 tests passing; no coverage gate; no E2E; no load tests |
| DevOps / CI-CD | 2/10 | 10/10 | No working pipeline; no containers |
| Security implementation | 5/10 | 10/10 | No RBAC middleware; JWT claims wrong; no rate limiting |
| Frontend | 7/10 | 10/10 | 75 custom pages unbuilt; no API wiring |
| **Overall** | **6.5/10** | **10/10** | |

---

## Phase Summary (revised 2026-05-19)

| Phase | Name | Est. duration | Grade after |
|---|---|---|---|
| Phase 1 | Foundation Seal | ~1 week | 7.5/10 ✓ |
| Phase 2 | Follow-up Engine | ~2 weeks | 8.0/10 ✓ |
| Phase 3 | Remaining 5 Engines | ~6 weeks | 8.5/10 ✓ |
| **Phase 4** | **Backend Hardening + Missing Docs** | **~4 weeks** | **9.0/10** |
| **Phase 5** | **Frontend — 75 Custom Pages** | **~4 weeks** | **9.5/10** |
| **Phase 6** | **Market Research Features + Final Hardening** | **~2 weeks** | **10/10** |

**Sequencing rationale:** Phase 4 (Hardening) gates Phase 5 (Frontend). The tri-register audit found 8 Critical and 15 High backend gaps — including no DB persistence, no RBAC middleware, broken JWT claims, and missing domain APIs (Tasks, Tickets, Opportunities, Auth). Three design docs required by Phase 5 pages do not yet exist (cases-domain.md, localization.md, territory-management.md). Building 75 frontend pages on this foundation requires immediate rework. Phase 4 must complete all Critical + High items before Phase 5 starts.

---

## Phase 1 — Foundation Seal (~1 week) ✓ COMPLETE
**Lifts:** Structure 10/10 · Docs 10/10 · DevOps 6/10

### Documentation
- Root `README.md` — GitHub landing page: what the system is, how to run it, how to contribute
- `CHANGELOG.md` — version history starting from today (session 20)
- `CONTRIBUTING.md` — branch naming convention, commit format, PR process
- `docs/adr/ADR-001.md` — DDD + microservices architecture choice
- `docs/adr/ADR-002.md` — Adapter pattern for Pakistan isolation
- `docs/adr/ADR-003.md` — WhatsApp-first interaction model

### Structure & Tooling
- `Makefile` — `make dev`, `make test`, `make migrate`, `make lint` commands
- `.pre-commit-config.yaml` — ruff + black enforced on every commit
- Alembic wired — `alembic init` + `env.py` configured + first empty migration

### DevOps
- `docker-compose.yml` — Postgres + Redis + API gateway + one service
- `Dockerfile` for `backend/gateway`
- `Dockerfile` for `backend/services`

---

## Phase 2 — Follow-up Engine (~2 weeks) ✓ COMPLETE
**Lifts:** Code 5/10 · Testing 5/10 · Security 6/10

**Why first:** Simplest complete vertical — one service, one DB table, clear state machine, no external dependencies. Proves the full stack works end to end.

### Models & DB
- SQLAlchemy models: `FollowUp`, `Lead`, `Activity`
- Alembic migration: first real schema — matches `domain-model.md` field spec

### API Endpoints
- `GET /api/v1/followups` — list with overdue-pinned sort
- `POST /api/v1/followups` — create with T+0 enforcement trigger
- `PATCH /api/v1/followups/{id}/complete` — mark done
- `POST /api/v1/followups/{id}/escalate` — manual escalation
- `GET /api/v1/followups/{id}` — detail
- `/docs` — OpenAPI auto-exposed (zero effort from FastAPI)

### Business Logic
- Enforcement timers: T+0 / +2h / +24h / +48h from `followup-enforcement-model.md`
- Inactivity rule engine (rule precedence: inactivity > time > activity)
- Reassignment configuration mechanism
- Scheduler job: background overdue escalation

### Security
- JWT middleware on all routes
- RBAC enforcement: role gates from `identity-auth-rbac.md`

### Tests
- `conftest.py` + pytest config
- Unit tests: enforcement logic (timer rules, escalation triggers)
- Integration tests: all 5 endpoints (happy path + error states)

---

## Phase 3 — Remaining 5 Engines (~6 weeks) ✓ COMPLETE
**Lifts:** Code 8/10 · Testing 7/10 · Security 8/10

Each sprint follows Phase 2 pattern: models → migrations → endpoints → logic → tests.

### Sprint 1 — WhatsApp Engine
Inbound webhook, intent detection, auto lead creation, conversation threading, contact mapping.
Spec: `docs/whatsapp-execution-model.md`

### Sprint 2 — Collections Engine
Invoice lifecycle, overdue detection, WhatsApp reminder trigger, confidence scoring (≥85 auto-match / 40–84 review), customer opt-out.
Spec: `docs/collections-engine-model.md`

### Sprint 3 — Activity Control Engine
Immutable activity log writes, ownership tracking, audit trail endpoints.
Spec: `docs/activity-control-model.md`

### Sprint 4 — Activation Engine
Onboarding flow, auto pipeline creation, sandbox→production WhatsApp transition, sample data localisation.
Spec: `docs/activation-model.md`

### Sprint 5 — Execution Control Plane
Idempotency key middleware, retry with exponential backoff (1s base, 2× multiplier, ±20% jitter, 60s max), dead letter queue (DLQ).
Spec: `docs/execution-hardening.md`

---

## Phase 4 — Backend Hardening + Missing Docs (~4 weeks)
**Lifts:** Code 9/10 · Security 9/10 · Testing 8/10 · Docs 10/10
**Gates Phase 5.** All Critical and High items must complete before frontend build starts.
**Gap sources:** 44-gap code audit (PENDING.md C-01–L-06) · product-spec-gap-register.md (PS-001–PS-010)

### Sprint 0 — Missing Design Docs
These docs do not exist yet. Three are Phase-5 build blockers; the rest gate Sprint 2–3 implementation.

**Rule: every doc created or extended in this sprint must be added to DOC-CATALOGUE.md on the same day it is written. DOC-CATALOGUE.md is the single anchor for all future code audits — a doc that exists but is not catalogued is invisible to audit.**

**Phase-5 build blockers (must exist before Phase 5 starts):**
- `backend/docs/cases-domain.md` — entity model, state machine, SLA tiers, routing rules, escalation (PS-001; gates Phase 5 Build Phase 4: B-05, C-05, E-01, A-07, I-04, C-12)
- `backend/docs/localization.md` — i18n framework, RTL rules, EN/UR key registry, WhatsApp template locale rules (PS-005; gates all 75 pages — CONSTRAINTS.md C-001)
- `backend/docs/territory-management.md` — entity model, criteria schema, routing rules, RBAC scoping (PS-008; gates G-09 territories.html)

**Architecture docs (needed for Sprint 2–3 implementation):**
- `backend/docs/shared-inbox.md` — multi-agent assignment model, conversation handoff, queue management (PS-002)
- `backend/docs/compliance-adapter.md` — ComplianceAdapter interface contract, Pakistan implementation, call sites (PS-003)
- `backend/docs/conversational-action-spec.md` — command dictionary, intent-to-action mapping, context resolution, error flows (PS-004)
- `backend/docs/employee-performance.md` — KPI definitions, aggregation model, read-model schema, RBAC visibility rules (PS-006)
- `backend/docs/pricing-plans.md` — plan tiers, PKR prices, feature entitlements, upgrade/downgrade flow (PS-009)
- `backend/docs/integration-flow-traces.md` — all 4 end-to-end flow traces with failure paths and end-state assertions (PS-010)

**Extend existing doc:**
- `backend/docs/collections-engine-model.md` §N — Manual Payment Proof workflow: entity model, states, endpoints, RBAC (PS-007)

### Sprint 1 — Persistence (blocks everything else)
All 6 engines + idempotency ledger use in-memory state. Replace with DB-backed repositories.
- FollowupEnforcementEngine → SQLAlchemy (tables exist in 0001 migration)
- ActivityControlEngine → SQLAlchemy
- CollectionsService → SQLAlchemy
- ConversationService → SQLAlchemy + persistent message store
- GlobalIdempotencyLedger → PostgreSQL idempotency_records table
- FeatureFlagEvaluator → SQLAlchemy + Redis cache

### Sprint 2 — Security & Auth
- JWT claims fix: add role_ids (array), scopes, aud, iss; add revocation check (Redis jti blocklist)
- RBAC middleware: per-route permission annotation + user active/suspended check
- Rate limiting: 10k/min per-tenant, 500/min per-principal (security-model.md)
- WhatsApp webhook: replace API key with Meta X-Hub-Signature-256 HMAC
- Auth service endpoints: POST /api/v1/auth/sessions, DELETE current, POST /users/{id}/roles
- Fix JazzCash base.py verify_callback (sorted params + HASH_KEY, not str(payload))
- Startup env var validation: fail-fast if JWT_ISSUER/AUDIENCE/PUBLIC_KEY_URL missing

### Sprint 3 — Missing Domain APIs
- Tasks API: GET/POST /api/v1/tasks, POST /tasks/{id}/reschedule
- Tickets/Cases API: 5 endpoints (GET/POST/PATCH/escalate/sla)
- Opportunity pipeline API: GET/POST /api/v1/opportunities + transitions + mark-won/lost
- GET /api/v1/forecasts (weighted pipeline by stage probability)
- Audit query API: GET /api/v1/audits/events + exports + integrity/verify

### Sprint 4 — API Standards & State Machines
- Error envelope: all HTTPException → `{"error":{"code":"..."},"meta":{"request_id":"..."}}` on every engine
- Pagination: add total_pages + rename total → total_items everywhere
- Unknown fields rejected (ConfigDict extra=forbid on all request models)
- FollowUp states: add SNOOZED + FAILED; expand to 7 for WhatsApp execution path
- Conversation states: add WAITING_ON_CONTACT/INTERNAL, RESOLVED, CLOSED, REOPENED
- Lead stage enum: add NURTURING, PROPOSAL, DISQUALIFIED; rename QUALIFIED → QUALIFYING
- Opt-out: "STOP" + "لاگ آف" intent in WhatsApp classifier
- Cash/manual payment reconciliation gated behind verification_status == verified
- Fix collections automation engine reminder schedule (spec: -3,-1,+1,+7,+15)
- Wire Idempotency-Key header enforcement on all critical write endpoints
- Add closure_reason column to leads migration; FK followup_tasks → leads
- Scope activity engine dicts by tenant_id

### Sprint 5 — Observability, CI/CD & Testing
- Structured logging: expand to 16 required fields (trace_id, tenant_id, request_id per request)
- Daily Merkle root checkpoint + hourly integrity job + Sev-1 alerting
- Distributed trace headers (W3C traceparent)
- GitHub Actions: lint + test + build + staging deploy
- Bandit + npm audit in CI pipeline
- Static import denylist: ruff rule blocking core → adapters/pakistan
- Replace ConcurrencyController stub with real Redis distributed lock
- Lead conversion saga in services/ (Account→Contact→Opportunity + compensation)
- Retry policy: fix to 1s/2×/60s/8 attempts; remove deterministic seed
- Fix datetime.utcnow() → datetime.now(timezone.utc) everywhere; off-hours check → PKT (UTC+5)
- Coverage gate: CI blocks merge if < 80%
- Load test (locust): follow-up queue + collections happy path
- Full E2E: lead capture → follow-up → close → invoice → payment

---

## Phase 5 — Frontend: 75 Custom Pages (~4 weeks)
**Lifts:** Frontend 10/10
**Prerequisite:** Phase 4 all Critical + High items complete. Sprint 0 docs (cases-domain.md, localization.md, territory-management.md) must exist before Phase 5 starts.

All 75 pages from `DESIGN-SPEC.md`. Built in 8 build phases, each browser-approved before next starts. Every page wired to live backend via `FRONTEND-BACKEND-MAPPING.md`. RTL + mobile enforced per `CONSTRAINTS.md`.

| Build phase | Pages | Count |
|---|---|---|
| 1 — Core Execution | B-01, B-02, C-01, A-01, B-08, B-03, I-01 | 7 |
| 2 — Sales Intelligence | C-04, D-01, A-02, A-04, I-03, I-05, C-06 | 7 |
| 3 — Finance & Collections | B-09, C-08, A-06, C-09, H-04 | 5 |
| 4 — Support Operations | B-05, C-05, E-01, A-07, I-04, C-12 | 6 |
| 5 — Communication & Inbox | L-01, L-02, A-08 | 3 |
| 6 — Admin & Settings | G-02, G-03, G-05, G-07, G-09, G-01 | 6 |
| 7 — Marketing & Automation | F-01, I-06, H-02, K-01, A-10 | 5 |
| 8 — Enterprise Features | All remaining 36 pages | 36 |

---

## Phase 6 — Market Research Features + Final Hardening (~2 weeks)
**Lifts:** Code 10/10 · Frontend 10/10
**Source:** `backend/market-research-gap-register.md`

### Buildable (not blocked)
- MR-004: Automated daily WhatsApp activity summary to managers — scheduler job + WhatsApp template, EN + UR
- MR-005: Excel import / export for contacts and leads — POST /api/v1/contacts/import, GET exports

### Blocked (build when unblocked)
- MR-002: One-click invoice + WhatsApp payment link (blocked: P-016 payment credentials + Meta template approval)
- MR-001: Facebook / Instagram lead capture automation (blocked: Meta Business Manager setup by user)
- MR-003: Voice note transcription — Urdu / Roman Urdu / English (blocked: transcription provider + credentials)
- MR-006: Geo-tagging / field check-in for field reps (low priority; requires mobile GPS)
- MR-007: Kuickpay payment adapter (blocked: Kuickpay API credentials)

### Final Grade Audit
- Full audit across all 8 areas in Current State vs Target table above

---

## Non-negotiable rule for every phase
Every phase ends with a GitHub push. All 96 existing library pages must still return HTTP 200 after every push. Nothing regresses.

---

## Reference Documents
- `DESIGN-SPEC.md` — 75 custom pages, archetypes A–M
- `PENDING.md` (root) — full task checklist with progress checkboxes
- `PROGRESS.md` — session-by-session build log
- `DOC-CATALOGUE.md` — full document index
- `backend/CONSTRAINTS.md` — 17 build constraints, read before any new layer
- `backend/PENDING.md` — backend-specific blocked items (P-016, P-017)
- `backend/product-spec-gap-register.md` — 17 product spec gaps (PS-001–PS-010 + 7 MR items)
- `backend/market-research-gap-register.md` — 7 Pakistan market research feature gaps
