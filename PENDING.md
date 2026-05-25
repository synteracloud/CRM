# Pakistan CRM OS — Rebuild Pending Tasks

**Anchor:** `REBUILD-PLAN.md`
**Last updated:** 2026-05-25 — Stage 2 (Doc Fix + Restructure) COMPLETE (2A ownership blocks, 2B gap fills, 2C inconsistency fixes, 2D duplicate removal, 2E folder restructure). Next: Stage 3 — Code Overlay.
**Legend:** `[ ]` Pending · `[x]` Done · `[~]` In progress

---

## Completion Summary

| Phase | Total tasks | Done | % |
|---|---|---|---|
| Phase 1 — Foundation Seal | 14 | 14 | 100% ✓ |
| Phase 2 — Follow-up Engine | 19 | 19 | 100% ✓ |
| Phase 3 — 5 Engines | 27 | 27 | 100% ✓ |
| Phase 4 — Backend Hardening | 41 | 12 | 29% |
| Phase 5 — Frontend (75 pages) | 81 | 0 | 0% |
| Phase 6 — Market Research + Final Hardening | 10 | 0 | 0% |
| **Total** | **192** | **72** | **38%** |

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
**Goal:** Normalise all docs, overlay docs on code, fix every gap found. Gates Phase 5.

### Stage 0 — Design Docs + Pre-Phase Fixes ✓ COMPLETE (2026-05-19)

- [x] 9 missing design docs written and catalogued (2026-05-19)
- [x] collections-engine-model.md extended — Manual Payment Proof workflow
- [x] P3-A: Fix `Literal` import in `src/ticket_management/entities.py`
- [x] P3-B: Wire public router singletons in `app.py` lifespan
- [x] P2-A: RBAC role gates on followup endpoints
- [x] P2-B: Background scheduler worker — `services/followup/overdue.py`
- [x] P2-C: Fix double-query in `list_followups`
- [x] P3-C: Invoice "send" state transition endpoint
- [x] P3-F: `GET /api/v1/conversations/{id}` detail endpoint
- [x] P3-D: Tenant isolation in `list_invoices`
- [x] P3-E: Replace `datetime.utcnow()` with `datetime.now(timezone.utc)`

### Stage 1 — Doc Normalisation ✓ COMPLETE (2026-05-23)

- [x] Read all 51 specs in §F + §H line-by-line; 30 duplication/overlap clusters identified and logged in phase4-stage1-read-log.md; findings submitted for review

### Stage 2 — Doc Fix + Restructure ← CURRENT STAGE
**Non-destructive rule:** Max negative action = archiving. No file deletions.
**Report-back rule:** Complete one sub-stage → report back → wait for confirmation → proceed.
**Reference for all 30 clusters:** `backend/docs/_qc/phase4-stage1-read-log.md`

#### Stage 2A — Ownership Declaration ✓ COMPLETE (2026-05-25)
- [x] Add PRIMARY / DEFERS-TO / DO-NOT-RE-DEFINE header block to all 52 §F + §H spec files

#### Stage 2B — Gap Fills ✓ COMPLETE (2026-05-25)
- [x] `territory_ids` JWT claim added to `identity-auth-rbac.md`
- [x] `EmployeePerformanceRM` + `TerritoryPerformanceRM` added to `read-models.md`
- [x] `TenantUsageMetric` entity added to `domain-model.md`
- [x] 3 missing events added to `event-catalog.md` (`lead.conversion.failed.v1`, `case.sla.first_response_breached.v1`, `case.sla.resolution_breached.v1`)
- [x] `ProviderName` values canonicalised in `integration-contracts.md`

#### Stage 2C — Inconsistency Resolution ✓ COMPLETE (2026-05-25)
- [x] Payment status enum canonical — `payments-revenue.md` PRIMARY; `collections-engine-model.md` scope note added
- [x] Collections aging buckets canonical (1–7/8–30/31–60/61+) — `owner-dashboard.md` updated to 4-bucket
- [x] Audit hash schema — `integrity.hash/prev_hash/chain_seq` canonical; `data-governance-layer.md §2.6` fixed; deprecated `before_hash/after_hash` noted
- [x] Health endpoint contract PRIMARY in `runtime-deployment.md §3.2`; `observability-audit.md §3.2` now points there
- [x] SLA event naming fixed — `.v1` suffix applied in `cases-domain.md`
- [x] Urdu keyword canonical — `مینیجر سے بات کریں` fixed in `conversational-action-spec.md`
- [x] WhatsApp opt-out/opt-in keyword handling — §7.4 added to `whatsapp-execution-model.md`

#### Stage 2D — Duplicate Removal + Misplaced Content ✓ COMPLETE (2026-05-25)
- [x] Case/ticket section removed from `activities-tasks.md`; pointer stub added
- [x] Follow-up Queue API section removed from `opportunities-pipeline.md`; pointer stub added
- [x] `CustomFieldDefinition` merged into `FieldDefinition` in `custom-object-framework.md`
- [x] JWT claims full list replaced with pointer in `security-model.md`
- [x] Idempotency/authz/event-dedup pointer stubs added to `api-standards.md`
- [x] KPI formula pointer added to `activity-control-model.md §5.2`

#### Stage 2E — Rename + Folder Restructure ✓ COMPLETE (2026-05-25)
- [x] 9 subfolders created (`architecture/ security/ domain/ infrastructure/ adapters/ product/ ui/ _b9/ _qc/`)
- [x] All 71 spec files moved to new locations with `git mv` (history preserved)
- [x] All internal markdown hyperlinks updated to relative paths (`../category/filename.md`)
- [x] Text references (`docs/filename.md`) updated to new paths in all files, ADR files, and tracking docs
- [x] `DOC-CATALOGUE.md` paths updated to match new tree

### Stage 3 — Code Overlay
- [ ] Overlay normalised docs on code; fix every gap found across entity, API, and business logic layers
- [ ] Write `backend/docs/phase4-gap-register.md` — full record of all gaps found and fixed

### Stage 4 — Mapping Rebuild + Final Push
- [ ] Rebuild `FRONTEND-BACKEND-MAPPING.md` — every endpoint marked LIVE / BUILD / MISSING
- [ ] Verify: all 96 existing pages still HTTP 200
- [ ] Coverage gate — CI blocks merge if coverage < 80%
- [ ] Load test (locust) — follow-up queue + collections happy path
- [ ] Full E2E test — lead capture → follow-up → close → invoice → payment
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
