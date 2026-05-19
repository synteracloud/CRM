# Pakistan CRM OS — Rebuild Pending Tasks

**Anchor:** `REBUILD-PLAN.md`
**Last updated:** 2026-05-19 — Tri-register audit complete. Phases restructured: hardening (Phase 4) gates frontend (Phase 5). Market research features added as Phase 6.
**Legend:** `[ ]` Pending · `[x]` Done · `[~]` In progress

---

## Completion Summary

| Phase | Total tasks | Done | % |
|---|---|---|---|
| Phase 1 — Foundation Seal | 14 | 14 | 100% ✓ |
| Phase 2 — Follow-up Engine | 19 | 19 | 100% ✓ |
| Phase 3 — 5 Engines | 27 | 27 | 100% ✓ |
| Phase 4 — Backend Hardening + Missing Docs | 86 | 9 | 10% |
| Phase 5 — Frontend (75 pages) | 81 | 0 | 0% |
| Phase 6 — Market Research + Final Hardening | 10 | 0 | 0% |
| **Total** | **229** | **71** | **31%** |

---

## Phase 1 — Foundation Seal

### Documentation
- [x] Root `README.md` — GitHub landing page (what it is, how to run, how to contribute)
- [x] `CHANGELOG.md` — version history from session 20
- [x] `CONTRIBUTING.md` — branch naming, commit format, PR process
- [x] `backend/docs/adr/ADR-001.md` — DDD + microservices choice
- [x] `backend/docs/adr/ADR-002.md` — Adapter pattern for Pakistan isolation
- [x] `backend/docs/adr/ADR-003.md` — WhatsApp-first interaction model

### Structure & Tooling
- [x] `Makefile` — make dev, make test, make migrate, make lint
- [x] `.pre-commit-config.yaml` — ruff + black on every commit
- [x] Alembic setup — alembic init + env.py configured + requirements updated

### DevOps
- [x] `docker-compose.yml` — already existed at backend/docker-compose.yml (Postgres + gateway + services)
- [x] `Dockerfile` — backend/gateway (already existed)
- [x] `Dockerfile` — backend/services (already existed)
- [x] Verify: all 96 existing pages still HTTP 200 after Phase 1 push
- [x] GitHub push — Phase 1 complete

---

## Phase 2 — Follow-up Engine

### Models & DB
- [x] SQLAlchemy model — `FollowUp` (services/db/models/followup.py — FollowupTask + FollowupEscalation)
- [x] SQLAlchemy model — `Lead` (services/db/models/lead.py)
- [x] SQLAlchemy model — `Activity` (services/db/models/activity.py)
- [x] Alembic migration — first real schema migration (alembic/versions/0001_followup_schema.py)

### API Endpoints
- [x] `GET /api/v1/followups` — list, overdue-pinned sort
- [x] `POST /api/v1/followups` — create with T+0 trigger
- [x] `GET /api/v1/followups/{id}` — detail
- [x] `PATCH /api/v1/followups/{id}/complete` — mark done
- [x] `POST /api/v1/followups/{id}/escalate` — manual escalation
- [x] `/docs` — OpenAPI endpoint exposed (FastAPI auto-generates)

### Business Logic
- [x] Enforcement timers — T+0 / +2h / +24h / +48h (pre-existing engine.py)
- [x] Inactivity rule engine (precedence: inactivity > time > activity) (pre-existing)
- [x] Reassignment configuration mechanism (pre-existing engine.py)
- [x] Scheduler job — background overdue escalation (pre-existing scheduler.py)

### Security
- [x] JWT middleware wired to all followup routes (services/auth/jwt_deps.py)
- [x] RBAC role gates enforced (from identity-auth-rbac.md)

### Tests
- [x] `conftest.py` + pytest config (pre-existing + requirements updated)
- [x] Unit tests — enforcement timer logic (tests/followup/test_enforcement.py — 18 tests)
- [x] Integration tests — all 5 endpoints (tests/followup/test_public_api.py — 20 tests)
- [x] Verify: all 96 existing pages still HTTP 200 after Phase 2 push
- [x] GitHub push — Phase 2 complete

---

## Phase 3 — Remaining 5 Engines

### S1 — WhatsApp Engine (spec: whatsapp-execution-model.md)
- [x] Inbound webhook handler (`POST /api/v1/webhooks/whatsapp`, API-key auth)
- [x] Intent detection logic (classify_intent — keyword rules, payment/lead/support/response)
- [x] Auto lead creation from inbound message (`should_create_lead` advisory flag)
- [x] Conversation threading (in-memory store, keyed by tenant+phone)
- [x] Contact mapping (conversation tracks from_number + intent history)
- [x] Unit + integration tests (12 tests — webhook classification, anti-lead-loss, tenant isolation)

### S2 — Collections Engine (spec: collections-engine-model.md)
- [x] Invoice lifecycle — create, send, overdue, paid states (`POST /api/v1/invoices`)
- [x] Overdue detection logic (pre-existing service: run_overdue_rollup)
- [x] WhatsApp reminder trigger (pre-existing: ReminderScheduler + automation engine)
- [x] Confidence scoring — ≥85 auto-match / 40–84 manual review (pre-existing reconciliation)
- [x] Customer opt-out mechanism (pre-existing: track_customer_response)
- [x] Unit + integration tests (11 tests — invoice CRUD, payment callback, 409 duplicate)

### S3 — Activity Control Engine (spec: activity-control-model.md)
- [x] Immutable activity log writes (`POST /api/v1/activities`)
- [x] Ownership tracking (engine enforces owner_id on every entity mutation)
- [x] Audit trail endpoints (`GET /api/v1/activities`, `GET /api/v1/activities/chain-integrity`)
- [x] Unit + integration tests (10 tests — log, feed, chain integrity valid/broken)

### S4 — Activation Engine (spec: activation-model.md)
- [x] Onboarding flow (<10 min first value) (`POST /api/v1/activation/start`)
- [x] Auto pipeline creation (5-stage default pipeline seeded on start)
- [x] Sandbox→production WhatsApp transition (`POST /api/v1/activation/whatsapp-sim`)
- [x] Sample data localisation (5 contacts + 4 deals with Pakistan names)
- [x] Unit + integration tests (10 tests — start, sim, move-deal, aha-moment, status)

### S5 — Execution Control Plane (spec: execution-hardening.md)
- [x] Idempotency key middleware (pre-existing: GlobalIdempotencyLedger)
- [x] Retry with exponential backoff (pre-existing: RetryExecutor + RetryPolicy)
- [x] Dead letter queue (DLQ) + operator action API (`GET/POST /api/v1/admin/dead-letters`)
- [x] Unit + integration tests (10 tests — list DLQ, retry, requeue, admin role gate)

### Phase 3 close
- [x] Verify: all 96 existing pages still HTTP 200
- [x] GitHub push — Phase 3 complete

---

## Phase 4 — Backend Hardening + Missing Docs

**Gates Phase 5.** All Critical + High items must complete before frontend build starts.
**Gap sources:** `backend/product-spec-gap-register.md` (PS-001–PS-010) · Phase 1–3 code audit (C-01–L-06)

### Pre-Phase-4 Audit Fixes (done — carried forward from pre-Phase-4 audit)

- [x] P3-A: Fix `Literal` import missing in `src/ticket_management/entities.py`
- [x] P3-B: Wire public router singletons in `app.py` lifespan
- [x] P2-A: Implement RBAC role gates on followup endpoints — `escalate_followup` requires manager/admin
- [x] P2-B: Background scheduler worker — `services/followup/overdue.py` + asyncio background task
- [x] P2-C: Fix double-query in `list_followups` — replaced with single `func.count()` query
- [x] P3-C: Invoice "send" state transition — `POST /api/v1/invoices/{invoice_id}/send` added
- [x] P3-F: Add `GET /api/v1/conversations/{id}` detail endpoint
- [x] P3-D: Tenant isolation in `list_invoices` — `tenant_id` stamped on creation; list filtered by tenant
- [x] P3-E: Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` in activity + collections entities

### Sprint 0 — Missing Design Docs (PS-001–PS-010)

**Rule: every doc created or extended in this sprint must be added to DOC-CATALOGUE.md on the same day it is written. This makes DOC-CATALOGUE.md the true single anchor for all future code audits.**

**Phase-5 build blockers — must exist before Phase 5 starts:**
- [ ] PS-001: Create `backend/docs/cases-domain.md` — entity model, state machine, SLA tiers, routing rules, escalation (gates Build Phase 4: B-05, C-05, E-01, A-07, I-04, C-12) + add to DOC-CATALOGUE.md
- [ ] PS-005: Create `backend/docs/localization.md` — i18n framework, RTL rules, EN/UR key registry, WhatsApp template locale rules (gates all 75 pages — CONSTRAINTS.md C-001) + add to DOC-CATALOGUE.md
- [ ] PS-008: Create `backend/docs/territory-management.md` — entity model, criteria schema, routing rules, RBAC scoping (gates G-09 territories.html) + add to DOC-CATALOGUE.md

**Architecture docs — needed before Sprint 2–3 implementation:**
- [ ] PS-002: Create `backend/docs/shared-inbox.md` — multi-agent assignment model, conversation handoff, queue management + add to DOC-CATALOGUE.md
- [ ] PS-003: Create `backend/docs/compliance-adapter.md` — ComplianceAdapter interface contract, Pakistan implementation, call sites + add to DOC-CATALOGUE.md
- [ ] PS-004: Create `backend/docs/conversational-action-spec.md` — command dictionary, intent-to-action mapping, context resolution, error flows + add to DOC-CATALOGUE.md
- [ ] PS-006: Create `backend/docs/employee-performance.md` — KPI definitions, aggregation model, read-model schema, RBAC visibility rules + add to DOC-CATALOGUE.md
- [ ] PS-009: Create `backend/docs/pricing-plans.md` — plan tiers, PKR prices, feature entitlements, upgrade/downgrade flow + add to DOC-CATALOGUE.md
- [ ] PS-010: Create `backend/docs/integration-flow-traces.md` — all 4 end-to-end flow traces with failure paths and end-state assertions + add to DOC-CATALOGUE.md

**Extend existing doc:**
- [ ] PS-007: Extend `backend/docs/collections-engine-model.md` §N — Manual Payment Proof workflow: entity model, states, endpoints, RBAC (DOC-CATALOGUE.md entry already exists; update description to note new section)

### Sprint 1 — Persistence (blocks all other sprints)

- [ ] C-01: Replace all in-memory dicts with DB-backed repositories (affects all 6 engines + idempotency ledger)

### Sprint 2 — Security & Auth

- [ ] C-03: Extend JWT TokenClaims to 9 required claims; change role scalar → role_ids array
- [ ] C-04: Add JWT issuer + audience validation; add Redis jti revocation check (fail-closed)
- [ ] C-06: Replace WhatsApp webhook X-Api-Key check with Meta X-Hub-Signature-256 HMAC
- [ ] C-07: Add RBAC enforcement middleware with per-route permission annotation
- [ ] H-01: Build auth service endpoints — POST /api/v1/auth/sessions, DELETE current, POST /users/{id}/roles
- [ ] H-07: Wire JazzCash + Easypaisa adapters in app.py lifespan
- [ ] H-08: Fix JazzCash verify_callback in base.py to use sorted params + HASH_KEY (not str(payload))
- [ ] H-10: Add rate limiting middleware (10k/min per-tenant, 500/min per-principal)
- [ ] M-02: Add startup env var validation — fail-fast if JWT_ISSUER, JWT_AUDIENCE, JWT_PUBLIC_KEY_URL missing

### Sprint 3 — Missing Domain APIs

- [ ] H-02: Build Tasks API — GET/POST /api/v1/tasks, POST /tasks/{id}/reschedule
- [ ] H-03: Build Tickets/Cases API — GET/POST /api/v1/tickets, PATCH, escalate, sla
- [ ] M-07: Build Opportunity pipeline API — GET/POST /api/v1/opportunities + transitions + mark-won/lost + GET /api/v1/forecasts
- [ ] M-05: Build audit query endpoints — GET /api/v1/audits/events + exports + integrity/verify

### Sprint 4 — API Standards & State Machines

- [ ] C-02: Fix error envelope format across all 6 engines — `{"error":{"code":"...","message":"...","details":[]},"meta":{"request_id":"..."}}`
- [ ] C-05: Add tenant isolation guard to GET /api/v1/invoices/{id}
- [ ] C-08: Fix retry policy values to spec (1s/2×/60s/8 attempts); remove deterministic seed=7
- [ ] H-04: Expand FollowUp state machine to 5 states minimum (add SNOOZED, FAILED)
- [ ] H-05: Fix Lead stage enum — add NURTURING, PROPOSAL, DISQUALIFIED; rename QUALIFIED → QUALIFYING
- [ ] H-06: Add opt-out keyword handling — "STOP" and "لاگ آف" in WhatsApp intent classifier
- [ ] H-09: Wire GlobalIdempotencyLedger to HTTP endpoints; enforce Idempotency-Key header on mutations
- [ ] H-11: Enforce version_no OCC on Lead — add WHERE version_no=expected pattern
- [ ] H-12: Make WhatsApp webhook async — return 200 immediately, process in background task
- [ ] H-13: Fix pagination meta — add total_pages everywhere; rename total → total_items
- [ ] H-14: Native-speaker review all Urdu strings before any customer-facing send (blocked: P-017)
- [ ] H-15: Persist enforcement_level per tenant in config store
- [ ] M-01: Add ConfigDict(extra="forbid") to all Pydantic request models
- [ ] M-03: Expand Conversation state machine to 7 states (add WAITING_ON_CONTACT, WAITING_ON_INTERNAL, RESOLVED, CLOSED, REOPENED)
- [ ] M-09: Fix collections automation engine reminder schedule to match spec (-3,-1,+1,+7,+15)
- [ ] M-10: Scope all activity engine dicts by tenant_id
- [ ] M-12: Fix all datetime.utcnow() to datetime.now(timezone.utc); fix off-hours check to use PKT (UTC+5)
- [ ] M-13: Add closure_reason column to leads Alembic migration
- [ ] M-14: Add FK constraint followup_tasks.lead_id → leads.lead_id (ON DELETE CASCADE)
- [ ] M-15: Gate cash/manual payment reconciliation behind verification_status == verified check

### Sprint 5 — Observability, CI/CD & Testing

- [ ] M-04: Add daily Merkle root checkpoint + hourly integrity scheduler job + Sev-1 alerting
- [ ] M-06: Expand structured logging to 16 required fields (trace_id, tenant_id, request_id per request)
- [ ] M-08: Replace ConcurrencyController stub with real Redis distributed lock
- [ ] M-11: Build lead conversion saga in services/ (Account→Contact→Opportunity with compensation)
- [ ] L-01: Embed structured ActorContext object in ActivityEvent (not flat scalars)
- [ ] L-02: Add deduplication and persistence to FollowupJobScheduler
- [ ] L-03: Wire ComplianceAdapter into service lifecycle
- [ ] L-04: Add ruff denylist rule for core→adapters/pakistan imports in CI
- [ ] L-05: Fix Easypaisa HMAC field join to use "&"-delimited key=value pairs
- [ ] L-06: Fix feature flag percentage rollout to hash per user_id, not tenant_id
- [ ] GitHub Actions — lint on every push
- [ ] GitHub Actions — test on every push
- [ ] GitHub Actions — Docker build on push to main
- [ ] GitHub Actions — deploy to staging on merge to main
- [ ] Secrets moved to GitHub Secrets (remove raw values from .env references in CI)
- [ ] Bandit security scan added to CI pipeline
- [ ] npm audit added to CI pipeline
- [ ] Request logging middleware
- [ ] Distributed trace headers (W3C traceparent)
- [ ] Coverage gate — CI blocks merge if coverage < 80%
- [ ] Load test (locust) — follow-up queue + collections happy path
- [ ] Full E2E test — lead capture → follow-up → close → invoice → payment

### Phase 4 close
- [ ] Verify: all 96 existing pages still HTTP 200
- [ ] GitHub push — Phase 4 complete

---

## Phase 5 — Frontend: 75 Custom Pages

**Prerequisite:** Phase 4 all Critical + High items complete. PS-001, PS-005, PS-008 docs must exist.

### Build Phase 1 — Core Execution Surfaces
- [ ] B-01 `followups.html` — Follow-up Queue (archetype B)
- [ ] B-02 `leads.html` — Lead Queue (archetype B)
- [ ] C-01 `leads-detail.html` — Lead Detail (archetype C)
- [ ] A-01 `dashboard.html` — Owner Dashboard (archetype A)
- [ ] B-08 `collections.html` — Collections Queue (archetype B)
- [ ] B-03 `contacts.html` — Contact List (archetype B)
- [ ] I-01 `lead-new.html` — New Lead Form (archetype I)

### Build Phase 2 — Sales Intelligence
- [ ] C-04 `opportunities-detail.html` — Opportunity Detail (archetype C)
- [ ] D-01 `sales-cockpit.html` — Sales Cockpit (archetype D)
- [ ] A-02 `leads-dashboard.html` — Lead Funnel Dashboard (archetype A)
- [ ] A-04 `sales-dashboard.html` — Opportunity Pipeline Dashboard (archetype A)
- [ ] I-03 `opportunity-new.html` — New Opportunity Form (archetype I)
- [ ] I-05 `quote-builder.html` — CPQ Quote Builder (archetype I)
- [ ] C-06 `quotes-detail.html` — Quote Detail (archetype C)

### Build Phase 3 — Finance & Collections
- [ ] B-09 `invoices.html` — Invoice Queue (archetype B)
- [ ] C-08 `invoices-detail.html` — Invoice Detail (archetype C)
- [ ] A-06 `subscriptions-dashboard.html` — Subscription Revenue Dashboard (archetype A)
- [ ] C-09 `subscriptions-detail.html` — Subscription Detail (archetype C)
- [ ] H-04 `finance-analytics.html` — Finance Analytics (archetype H)

### Build Phase 4 — Support Operations
- [ ] B-05 `cases.html` — Case Queue (archetype B)
- [ ] C-05 `cases-detail.html` — Case Detail (archetype C)
- [ ] E-01 `support-console.html` — Support Console (archetype E)
- [ ] A-07 `support-dashboard.html` — Case SLA Operations Dashboard (archetype A)
- [ ] I-04 `case-new.html` — New Case Form (archetype I)
- [ ] C-12 `knowledge-article.html` — Knowledge Article Detail (archetype C)

### Build Phase 5 — Communication & Inbox
- [ ] L-01 `inbox.html` — Omnichannel Inbox (archetype L)
- [ ] L-02 `inbox-thread.html` — Conversation Thread (archetype L)
- [ ] A-08 `engagement-dashboard.html` — Communication Engagement Dashboard (archetype A)

### Build Phase 6 — Admin & Settings
- [ ] G-02 `user-management-crm.html` — User Management (archetype G)
- [ ] G-03 `roles.html` — Role & Permission Editor (archetype G)
- [ ] G-05 `integrations.html` — Integration Settings (archetype G)
- [ ] G-07 `feature-flags.html` — Feature Flags (archetype G)
- [ ] G-09 `territories.html` — Territory & Assignment Config (archetype G)
- [ ] G-01 `org-settings.html` — Organization Settings (archetype G)

### Build Phase 7 — Marketing & Automation
- [ ] F-01 `marketing-workspace.html` — Marketing Workspace (archetype F)
- [ ] I-06 `campaign-new.html` — Campaign Builder (archetype I)
- [ ] H-02 `marketing-analytics.html` — Marketing Analytics (archetype H)
- [ ] K-01 `workflow-builder.html` — Workflow Builder (archetype K)
- [ ] A-10 `workflows-dashboard.html` — Workflow Automation Dashboard (archetype A)

### Build Phase 8 — Enterprise Features (36 pages)
- [ ] A-03 `contacts-health.html` — Customer Health Dashboard
- [ ] A-05 `quotes-dashboard.html` — Quote Approval Dashboard
- [ ] A-09 `knowledge-dashboard.html` — Knowledge Effectiveness Dashboard
- [ ] A-11 `tenants-dashboard.html` — Tenant & Entitlement Dashboard
- [ ] A-12 `identity-dashboard.html` — Identity & Access Posture Dashboard
- [ ] A-13 `audit-dashboard.html` — Platform Audit & Reliability Dashboard
- [ ] B-04 `accounts.html` — Account List
- [ ] B-06 `activity.html` — Activity Feed
- [ ] B-07 `tasks.html` — Task Queue
- [ ] B-10 `users.html` — User Directory
- [ ] B-11 `partners.html` — Partner List
- [ ] C-02 `contacts-detail.html` — Customer 360
- [ ] C-03 `accounts-detail.html` — Account Profile
- [ ] C-07 `orders-detail.html` — Order Detail
- [ ] C-10 `workflow-run-detail.html` — Workflow Execution Detail
- [ ] C-11 `partners-detail.html` — Partner Detail
- [ ] G-04 `billing-settings.html` — Billing & Subscription Settings
- [ ] G-06 `notifications.html` — Notification Settings
- [ ] G-08 `compliance.html` — Compliance Settings
- [ ] H-01 `sales-analytics.html` — Sales Analytics
- [ ] H-03 `support-analytics.html` — Support Analytics
- [ ] H-05 `workflow-analytics.html` — Workflow Analytics
- [ ] H-06 `audit-report.html` — Audit Report
- [ ] H-07 `report-builder.html` — Custom Report Builder
- [ ] I-02 `contact-new.html` — New Contact Form
- [ ] J-01 `audit-log.html` — Audit Log
- [ ] J-02 `compliance-report.html` — Compliance Report
- [ ] J-03 `data-governance.html` — Data Governance Console
- [ ] J-04 `rbac-audit.html` — RBAC Audit
- [ ] J-05 `privacy.html` — Consent & Privacy Manager
- [ ] K-02 `object-builder.html` — Custom Object Layout Builder
- [ ] K-03 `rule-builder.html` — Rule / CPQ Logic Builder
- [ ] K-04 `approval-lanes.html` — CPQ Approval Lane Board
- [ ] L-03 `routing-config.html` — Routing Configuration
- [ ] M-01 `ai-copilot.html` — AI Copilot Panel
- [ ] M-02 `ai-insights.html` — AI Insights Dashboard

### Phase 5 close
- [ ] All 75 pages wired to live backend endpoints (FRONTEND-BACKEND-MAPPING.md)
- [ ] RTL verified on all pages (CONSTRAINTS.md C-001)
- [ ] Mobile responsiveness verified on all pages (b9-p08-mobile-responsiveness-system.md)
- [ ] Verify: all 96 existing pages still HTTP 200
- [ ] GitHub push — Phase 5 complete

---

## Phase 6 — Market Research Features + Final Hardening

**Source:** `backend/market-research-gap-register.md`

### Buildable (not blocked)
- [ ] MR-004: Automated daily WhatsApp activity summary to managers — scheduler job + WhatsApp template (EN + UR)
- [ ] MR-005: Excel import / export — POST /api/v1/contacts/import, GET /api/v1/contacts/export, POST /api/v1/leads/import, GET /api/v1/leads/export

### Blocked (build when unblocked)
- [ ] MR-002: One-click invoice + WhatsApp payment link (blocked: P-016 payment credentials + Meta template approval)
- [ ] MR-001: Facebook / Instagram lead capture automation (blocked: Meta Business Manager setup)
- [ ] MR-003: Voice note transcription — Urdu / Roman Urdu / English (blocked: transcription provider + credentials)
- [ ] MR-006: Geo-tagging / field check-in for field reps (low priority)
- [ ] MR-007: Kuickpay payment adapter (blocked: Kuickpay API credentials)

### Phase 6 close
- [ ] Final grade audit across all 8 areas (REBUILD-PLAN.md Current State vs Target table)
- [ ] Verify: all 96 existing pages still HTTP 200
- [ ] GitHub push — Phase 6 complete
