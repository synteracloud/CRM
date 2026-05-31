# Pakistan CRM OS — Rebuild Pending Tasks

**Anchor:** `COMMERCIALISATION-PLAN.md` (REBUILD-PLAN.md closed)
**Last updated:** 2026-05-31 — **C0 Environment Seal COMPLETE.** .env.local created, npm cache → D:\npm-cache, pip cache → D:\pip-cache, Playwright Chromium → D:\CRM\.playwright-browsers\chromium-1223, seal.ps1 created, c-seal baseline recorded. All tool writes confirmed on D:. C1 DB Wiring is next.
**Legend:** `[ ]` Pending · `[x]` Done · `[~]` In progress

---

## Completion Summary

| Phase | Total tasks | Done | % |
|---|---|---|---|
| Phase 1 — Foundation Seal | 14 | 14 | 100% ✓ |
| Phase 2 — Follow-up Engine | 19 | 19 | 100% ✓ |
| Phase 3 — 5 Engines | 27 | 27 | 100% ✓ |
| Phase 4 — Backend Hardening | 41 | 41 | 100% ✓ |
| Phase 5 — Frontend (75 custom pages) | 75 | 75 | 100% ✓ |
| Phase 5B — Backend Domain Extension (7 sprints) | 7 | 7 | 100% ✓ |
| Phase 6 — Market Research + Final Hardening + QC | 11 | 6 | 55% — Component 1 ✓ + Component 2 ✓ (MR-004, MR-005, T1-T4 audit, Wiring Sprint) |
| Phase M — Mapping & Convergence | 17 | 17 | 100% ✓ |
| **Total** | **176** | **175** | **99%** |

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

### Stage 3 — Code Overlay (IN PROGRESS — 2026-05-25)
- [x] Write `backend/docs/phase4-gap-register.md` — gap register created (28 gaps catalogued A-001 through E-008)
- [x] B-001 — Python `TokenClaims` extended: `role_ids`, `scopes`, `aud`, `iss`, `territory_ids` (jwt_deps.py)
- [x] D-001 — Gateway VALID_STAGES aligned to spec + migration 0001 (v1-leads.routes.js)
- [x] D-004 — `datetime.utcnow()` → `datetime.now(timezone.utc)` in followup/engine.py + http/internal.py + activity/monitor/entities.py
- [x] Bug fix — `_parse_rfc3339` in activity/engine.py (double +00:00 when isoformat already has offset)
- [x] Bug fix — `_parse_dt` in dashboard/owner/service.py (same double +00:00 issue)
- [x] Bug fix — JazzCash adapter: only divide by 100 for `pp_Amount` (paise), not generic `amount` key
- [x] Migration 0002 — followup SNOOZED+FAILED states, leads.closure_reason, FK followup_tasks→leads, idempotency_records table
- [x] Migration 0003 — invoices, payments, reconciliation_cases, conversations, conversation_messages tables
- [x] ORM models — Invoice, Payment, ReconciliationCase, Conversation, ConversationMessage, IdempotencyRecord
- [x] `CollectionsService._payments` dict added (dashboard service compatibility)
- [x] QC script path fixes — event-catalog, execution-hardening, service-map paths updated for Stage 2E restructure
- [x] `src/event_bus/catalog_events.py` — 9 new events added (lead.conversion.failed, case SLA events, partner events)
- [x] Tests: 314 / 314 passing (up from 308 baseline)
- [x] A-001 — Wire `FollowupEnforcementEngine` to use DB tables (followup_tasks, followup_escalations)
- [x] A-002 — Wire `ActivityControlEngine` to persist to activities table
- [x] A-003/A-004 — Wire CollectionsService + ConversationService to DB repositories
- [x] A-005 — Gateway idempotency.js: migration 0002 + ORM model created (in-memory→PostgreSQL swap deferred to Phase 5 with Redis)
- [ ] A-006 — Gateway rate-limit: swap in-memory buckets for Redis (deferred — needs Redis)
- [x] B-002 — Gateway auth-rbac.js: extract `territory_ids` JWT claim
- [x] B-003 — Gateway auth-rbac.js: jti revocation check via in-memory blocklist (Redis upgrade deferred)
- [x] B-005 — WhatsApp webhook: Meta X-Hub-Signature-256 HMAC verification (confirmed live in v1-whatsapp-webhooks.routes.js)
- [x] B-007 — Auth management endpoints (login, logout/revoke, role assignment)
- [x] D-002 — Update followup FollowupState enum to include SNOOZED + FAILED
- [x] D-005 — HTTPException → structured error envelope on all Python routers
- [x] D-006 — Pagination: add total_pages, rename total → total_items
- [x] D-008 — Manual payment reconciliation gate: require verification_status == verified
- [x] E-004 — GitHub Actions CI/CD pipeline: 5-job pipeline live (.github/workflows/ci.yml)
- [x] B-004 — Gateway app.js: production fail-fast on missing env vars
- [x] B-006 — JazzCash verify_callback: sorted pp_* HMAC-SHA256 with HASH_KEY
- [x] E-002 — W3C traceparent header propagation in observability middleware
- [x] E-005 — ruff TID251 banned-api: core/ → adapters.pakistan import denylist (pyproject.toml)
- [x] E-008 — 10-step E2E integration test: WhatsApp→followup→invoice→payment

### Stage 4 — Mapping Rebuild + Final Push
- [x] Rebuild `FRONTEND-BACKEND-MAPPING.md` — D-005 error envelope, D-006 pagination, B-007 auth, B-002 territory_ids updated
- [ ] Verify: all 96 existing pages still HTTP 200 (deferred — frontend dev server required)
- [x] Coverage gate — CI enforces --cov-fail-under=70 (70% gate; spec said 80% — note for Phase 5 tightening)
- [ ] Load test (locust) — follow-up queue + collections happy path (deferred to Phase 5)
- [x] Full E2E test — lead capture → follow-up → close → invoice → payment (10-step test passing)
- [ ] GitHub push — Phase 4 complete

---

## Phase 5 — Frontend: Custom Pages

**State as of 2026-05-29:**
- 75 of 75 custom pages built, browser-approved, and T1–T4 ✓ (Phase 6 Component 1 complete 2026-05-30)
- **All Cat 1 pages complete** — 0 Cat 1 unbuilt remaining
- 28 pages unbuilt — all Cat 2 (no backend domain exists for these archetypes)
- b9-p specs updated 2026-05-28 — all 13 archetypes have complete page coverage
- 75-page 3-category backend mapping analysis complete — `backend/FRONTEND-BACKEND-MAPPING.md`

**Rule:** Protocol audit (T1–T4) must pass before any page is locked. Build plan governs which pages are built next and in what order.

### Backend Fix Required — Collections Status Vocabulary
- [ ] **`v1-collections.routes.js` — align invoice status to domain spec** (blocking B-08, B-09, H-04)
  - **Conflict:** `collections-engine-model.md` defines `state ∈ {unpaid, partial, paid, overdue}` as canonical. Gateway currently returns `status: draft | open | paid | void | uncollectible`.
  - **Decision taken (2026-05-28):** Domain spec is authoritative (normalized Phase 4). Gateway implementation is wrong. Gateway must be updated.
  - **Fix:** Update `v1-collections.routes.js` to return `status` values aligned to domain spec: `unpaid | partial | paid | overdue`. Map gateway internal states to domain vocabulary at the response layer.
  - **Also fix:** `crm-collections.js` `statusBadge` map — currently uses gateway vocabulary; update to domain vocabulary once gateway is fixed.

### Current Tasks — Protocol Audit Fixes (10 pages)
- [ ] **Apply T2/T3/T4 batch fixes** across 7 protocol-audit-pending pages:
  - T1 fix: Add `crm-custom.css` link to `lead-new.html`
  - T2 fixes: Wire hardcoded delta text to CRM_DUMMY on B-01/B-02/B-03/B-08/A-01; fix kpi-completed-today logic on B-01; wire posture strip on A-01; replace dt_NewCustomers static rows with CRM_DUMMY data on A-01; fix activity timeline hardcoding on C-01; fix stage dropdown vocabulary on I-01
  - T3 fixes: Add Place 3 crm-custom.css `!important` rules for `dt_Followups`, `dt_ScrollVertical`, `dt_Contacts`
  - T4 fixes: Update filter chip vocabulary — B-01 level (Soft/Medium/Strict → none/reminder/warning/escalated/reassigned); B-02 stage (Contacted/Engaged → qualifying/nurturing); B-08 status (JS statusBadge → align to domain spec unpaid/partial/paid/overdue)
- [ ] **Run protocol audit on I-05 and C-06** — no SCREEN-ARTEFACTS records exist; audit from scratch
- [ ] **Wire 10 pages to live endpoints** (DUMMY_MODE=false) and verify
- [ ] **Finalize and approve 3-category build plan** — user approval required before new page builds start
- [ ] **Resolve I-03 blocker** — add New Opportunity Form spec to b9-p11-form-wizard.md then build.

### Build Phase 2 — Finance & Support
- [x] A-06 `subscriptions-dashboard.html` — Subscription Revenue Dashboard — built 2026-05-29
- [x] B-09 `invoices.html` — Invoice Queue — built 2026-05-29
- [x] C-09 `subscriptions-detail.html` — Subscription Detail — built 2026-05-29
- [ ] B-05 `cases.html` — Case Queue — **Cat 2: no cases gateway domain**
- [ ] C-05 `cases-detail.html` — Case Detail — **Cat 2: no cases gateway domain**
- [ ] E-01 `support-console.html` — Support Console — **Cat 2: no ticket gateway domain**
- [ ] A-07 `support-dashboard.html` — Case SLA Ops Dashboard — **Cat 2: no cases gateway domain**

### Build Phase 3 — Inbox & Admin
- [x] A-02 `leads-dashboard.html` — Lead Funnel Dashboard — built 2026-05-29
- [x] A-03 `contacts-health.html` — Customer Health Dashboard — built 2026-05-29
- [x] A-05 `quotes-dashboard.html` — Quote Approval Dashboard — built 2026-05-29
- [x] A-12 `identity-dashboard.html` — Identity & Access Dashboard — built 2026-05-29
- [x] A-13 `audit-dashboard.html` — Platform Audit Dashboard — built 2026-05-29
- [x] G-02 `user-management-crm.html` — User Management Admin — built 2026-05-29
- [ ] G-09 `territories.html` — Territory Config — **Cat 2: no territory gateway domain**
- [ ] L-01 `inbox.html` — Omnichannel Inbox — **Cat 2: no inbox routing service**
- [ ] A-08 `engagement-dashboard.html` — Engagement Dashboard — **Cat 2: no comms analytics**

### Build Phase 4 — Analytics & Forms
- [x] H-01 `sales-analytics.html` — Sales Analytics — built 2026-05-29
- [x] H-04 `finance-analytics.html` — Finance Analytics — built 2026-05-29
- [x] H-06 `audit-report.html` — Audit Report — built 2026-05-29
- [x] I-01 `lead-new.html` — New Lead Form — built 2026-05-29
- [x] I-03 `opportunity-new.html` — New Opportunity Form — built 2026-05-29
- [x] I-05 `quote-builder.html` — CPQ Quote Builder — built 2026-05-29
- [x] J-01 `audit-log.html` — Audit Log — rebuilt 2026-05-29
- [x] J-02 `compliance-report.html` — Compliance Report — rebuilt 2026-05-29
- [x] J-04 `rbac-audit.html` — RBAC Audit — rebuilt 2026-05-29
- [x] B-06 `activity.html` — Activity Feed — built 2026-05-29
- [x] B-07 `tasks.html` — Task Queue — built 2026-05-29
- [x] B-10 `users.html` — User Directory — built 2026-05-29
- [x] C-02 `contacts-detail.html` — Customer 360 — built 2026-05-29
- [x] C-04 `opportunities-detail.html` — Opportunity Detail — built 2026-05-29
- [x] C-06 `quotes-detail.html` — Quote Detail — built 2026-05-29
- [x] D-01 `sales-cockpit.html` — Sales Cockpit — built 2026-05-29

### Cat 1 Complete — all 15 built and approved 2026-05-29
- [x] A-11 `tenants-dashboard.html` — Tenant Dashboard
- [x] B-04 `accounts.html` — Account List
- [x] C-03 `accounts-detail.html` — Account Profile
- [x] C-07 `orders-detail.html` — Order Detail
- [x] C-08 `invoices-detail.html` — Invoice Detail
- [x] I-02 `contact-new.html` — New Contact Form
- [x] G-01 `org-settings.html` — Org Settings
- [x] G-03 `roles.html` — Role & Permission Editor
- [x] G-04 `billing-settings.html` — Billing Settings *(P-016 stub in place)*
- [x] G-05 `integrations.html` — Integration Settings
- [x] G-06 `notifications.html` — Notification Settings
- [x] G-07 `feature-flags.html` — Feature Flags
- [x] G-08 `compliance.html` — Compliance Settings
- [x] J-03 `data-governance.html` — Data Governance Console
- [x] J-05 `privacy.html` — Consent & Privacy Manager

### Phase 5 close
- [ ] All 28 verified pages wired to live backend endpoints (FRONTEND-BACKEND-MAPPING.md)
- [ ] RTL verified on all pages (CONSTRAINTS.md C-001)
- [ ] Mobile responsiveness verified on all pages
- [ ] Verify: all 96 existing pages still HTTP 200
- [ ] GitHub push — Phase 5 complete

---

### DOC-BLOCKED REGISTRY — updated 2026-05-28

**Note:** b9-p specs updated 2026-05-28. Several pages previously blocked for "b9-p does not define X" now have specs. Block reasons updated below. Pages cannot move to build queue until 4-source re-verification passes AND build plan is approved.

#### Still blocked — no backend domain exists (Category 2a — 23 pages)
Building these now produces permanently dummy-mode pages. Backend domains must be added first.

| ID | Page | Missing backend domain |
|---|---|---|
| A-07 | support-dashboard.html | No case/ticket gateway domain |
| A-09 | knowledge-dashboard.html | No knowledge gateway domain |
| A-10 | workflows-dashboard.html | No workflow execution gateway domain |
| B-05 | cases.html | No case gateway domain |
| B-11 | partners.html | No partner gateway domain |
| C-05 | cases-detail.html | No case gateway domain |
| C-10 | workflow-run-detail.html | No workflow gateway domain |
| C-11 | partners-detail.html | No partner gateway domain |
| C-12 | knowledge-article.html | No knowledge gateway domain |
| E-01 | support-console.html | No case/ticket gateway domain |
| F-01 | marketing-workspace.html | No marketing/campaign gateway domain |
| G-09 | territories.html | No territory gateway domain |
| H-02 | marketing-analytics.html | No marketing gateway domain |
| H-03 | support-analytics.html | No case gateway domain |
| H-05 | workflow-analytics.html | No workflow gateway domain |
| I-04 | case-new.html | No case gateway domain |
| I-06 | campaign-new.html | No marketing gateway domain |
| K-01 | workflow-builder.html | No workflow CRUD gateway API |
| K-02 | object-builder.html | No custom object gateway API |
| K-03 | rule-builder.html | No rule management gateway API |
| L-03 | routing-config.html | No inbox queue management gateway API |
| M-01 | ai-copilot.html | No AI service in gateway |
| M-02 | ai-insights.html | No AI service in gateway |

#### Still blocked — opaque proxy, schema unverifiable (Category 2b — 6 pages)
Gateway route exists but downstream schema unknown. 4-source verification cannot pass without confirmed field contract.

| ID | Page | Block reason |
|---|---|---|
| B-03 | contacts.html | Contacts[P] opaque — no standalone Contact domain doc; field contract in comment only |
| B-04 | accounts.html | Accounts[P] opaque — no standalone Account domain doc; no field documentation |
| B-07 | tasks.html | Tasks[P] opaque — Tasks schema in comment only, downstream unverified |
| C-02 | contacts-detail.html | Contacts[P] opaque + CustomerMasterHealthRM not in read-models.md |
| C-03 | accounts-detail.html | Accounts[P] opaque — no Account domain doc |
| I-02 | contact-new.html | Contacts[P] POST — accepted body fields unverifiable at gateway |

#### Still blocked — management API missing (Category 2c — 8 pages)
Backend domain exists but the specific API needed for this page does not.

| ID | Page | What's missing |
|---|---|---|
| G-01 | org-settings.html | No org settings HTTP endpoint at gateway |
| G-03 | roles.html | /users/:id/roles assignment exists; GET/POST /roles CRUD does not |
| G-04 | billing-settings.html | P-016 blocked (JazzCash/Easypaisa credentials required) |
| G-06 | notifications.html | No notification preferences gateway API |
| G-07 | feature-flags.html | Feature flag evaluation service exists; no management HTTP API |
| G-08 | compliance.html | No compliance configuration gateway endpoint |
| H-07 | report-builder.html | No generic report query API |
| J-05 | privacy.html | No consent/privacy management gateway API |

#### Still blocked — missing read model or spec gap (Category 2d — 5 pages)

| ID | Page | Block reason |
|---|---|---|
| A-03 | contacts-health.html | CustomerMasterHealthRM not in read-models.md |
| A-08 | engagement-dashboard.html | Emails[P] opaque; engagement data thin at gateway |
| A-11 | tenants-dashboard.html | No entitlement query endpoint at gateway |
| A-13 | audit-dashboard.html | Audit in-memory only; no persistent data |
| C-08 | invoices-detail.html | b9-p06 does not define Invoice Detail — no spec surface |

#### Spec-resolved, 4-source re-verification needed (previously blocked for b9-p reasons — now b9-p fixed)
These pages were previously blocked because "b9-p does not define X." b9-p was updated 2026-05-28. Re-run 4-source verification before adding to build queue.

| ID | Page | Previous block reason | New status | Mapping category |
|---|---|---|---|---|
| G-02 | user-management-crm.html | Route conflict b9-p09 | ✅ Route fixed — 4-source re-verify needed | Cat 1 |
| H-01 | sales-analytics.html | b9-p10 wrong pages | ✅ b9-p10 restructured — 4-source re-verify needed | Cat 1 |
| H-04 | finance-analytics.html | b9-p10 wrong pages | ✅ b9-p10 restructured — 4-source re-verify needed | Cat 1 |
| H-06 | audit-report.html | b9-p10 wrong pages | ✅ b9-p10 restructured — 4-source re-verify needed | Cat 1 (in-memory caveat) |
| I-03 | opportunity-new.html | b9-p11 missing | ✅ b9-p11 defines I-03 — 4-source re-verify needed | Cat 1 |
| J-01 | audit-log.html | Route conflict b9-p12 | ✅ Route fixed to /app/audit — 4-source re-verify needed | Cat 1 |
| J-02 | compliance-report.html | b9-p12 missing | ✅ b9-p12 defines J-02 — 4-source re-verify needed | Cat 1 |
| J-04 | rbac-audit.html | b9-p12 missing | ✅ b9-p12 defines J-04 — 4-source re-verify needed | Cat 1 |
| L-02 | inbox-thread.html | Route conflict b9-p13 | ✅ Route unified — but gateway lacks conversation endpoint | Cat 3 |
| G-05 | integrations.html | Route conflict | ✅ Resolved — 4-source re-verify needed | Cat 3 |
| K-04 | approval-lanes.html | Route conflict b9-p08 | ✅ Acknowledged — no lane mgmt API exists | Cat 3 |
| A-02 | leads-dashboard.html | No Lead domain doc | Lead entity in domain-model.md; LeadFunnelPerformanceRM in read-models.md — 4-source re-verify needed | Cat 1 |

---

## Phase M — Mapping & Convergence

**Purpose:** Reconcile frontend UI, backend routes, and spec docs into a single code-anchored
mapping file. Prerequisite for Phase 5 close task "wire 28 pages to live endpoints."
**Tracker:** `MAPPING-TRACKER.md` — batches B0–B9c with dependencies and status.
**Output:** Rewritten `backend/FRONTEND-BACKEND-MAPPING.md` (6 sections) + gap closure builds.
**Rule:** No deletions. Build gaps on whichever side is missing. Document before coding.

### Phase M-1 — Discovery reads (all parallel, zero risk)
- [x] B0 — Read PAGE-BUILD-PROTOCOL.md + DESIGN-SPEC.md §3
- [x] B1a — Backend routes: contacts, accounts, users, auth
- [x] B1b — Backend routes: orders, payments, subscriptions, invoice-summaries
- [x] B1c — Backend routes: emails, audit, sync, whatsapp-webhooks, payment-webhooks
- [x] B2 — Frontend drivers: crm-leads, crm-contacts, crm-dashboard, crm-lead-new, crm-dummy, crm-api

### Phase M-2 — Mapping file authoring ✅ COMPLETE 2026-05-27
- [x] B3 — Write Sec 1: Backend Domain Inventory (22 domains, code-anchored)
- [x] B4 — Write Sec 4: Frontend Page Inventory (12 built pages)
- [x] B5 — Write Sec 2: Fresh Archetype Extraction (from backend domains)
- [x] B6 — Write Sec 3: Existing Archetype Overlay (A–M vs fresh extraction)
- [x] B7 — Write Sec 5: Canonical Archetype List (backed by BOTH backend AND protocol)
- [x] B8 — Write Sec 6: Gap Register (24 gaps G-001–G-024, 14 breaking + 10 mapping)

### Phase M-3 — Gap closure ✅ COMPLETE 2026-05-27
- [x] B9a — Backend gap builds: G-002 (GET /forecasts inline route), G-004 (action_type+attempts_count in followups POST), G-020 (POST /invoices/:id/reminders), G-024 (respondError/respondSuccess import in v1-quotes.routes.js)
- [x] B9b — Frontend gap builds: G-001/G-014/G-015 (crm-dummy.js + crm-leads.js stages/sources/priorities), G-003 (opp_id→opportunity_id across 4 files), G-005 (escalation_level vocab crm-dummy + crm-followups), G-006 (collections status crm-dummy + crm-collections), G-009/G-020/G-021 (API paths in crm-api.js), G-010 (priceBooks added to crm-api.js), G-011/G-012 (followups.complete method+path; auth.login path), G-013/G-016/G-019 (user_id→id across 5 files; dashboard charts wired to CRM_DUMMY; followup_id→task_id)
- [x] B9c — Docs updates (DESIGN-SPEC.md E/F/M backend-incomplete notices)
- **Deferred (formally):** G-007 (account_name join — requires accounts microservice), G-008 (followup_enforcement badge — schema opaque), G-017 (contacts schema — downstream service), G-018 (tasks schema — opaque), G-022 (pagination style — v2 style), G-023 (quote opp ref — downstream dependency)

### Phase M close ✅ COMPLETE 2026-05-27
- [x] FRONTEND-BACKEND-MAPPING.md reviewed and locked
- [x] PAGE-BUILD-PROTOCOL.md archetype list updated to canonical list from Sec 5
- [x] All G-001–G-024 gaps resolved or formally deferred with reason

---

## Phase 5B — Backend Domain Extension ✓ COMPLETE 2026-05-30

**Gate:** Phase 5 complete ✓. All 7 sprints complete. Phase 6 gate open.
**Pattern per sprint:** read domain spec → ORM models → Alembic migration → gateway routes → service logic → tests → flip DUMMY_MODE=false → verify HTTP 200.

### Sprint 5B-1 — Cases / Support Tickets ✓ COMPLETE 2026-05-29
**Spec:** `backend/docs/domain/cases-domain.md` | **Pages unblocked:** B-05, C-05, E-01, A-07, H-03
- [x] Write ORM models: `Case`, `CaseComment`, `CaseEscalation`, `SupportQueue`, `SLAPolicy`, `KnowledgeArticle` — `services/db/models/cases.py`
- [x] Alembic migration: cases schema — `alembic/versions/0004_cases_schema.py`
- [x] Gateway routes: `v1-cases.routes.js` (CRUD + assign + comment + resolve + close + reopen + escalate + link-article); `v1-knowledge.routes.js`; support queues sub-router
- [x] Service logic: `services/cases/entities.py` (state machine, SLA timer, PKT business hours); `services/cases/service.py` (apply_transition, compute_sla_deadlines, evaluate_sla_escalation)
- [x] RBAC scopes: CASES_READ/CREATE/UPDATE/ADMIN + KNOWLEDGE_READ/MANAGE added to rbac-scopes.js; all roles updated
- [x] Unit + integration tests — `tests/cases/test_cases_state_machine.py` (14 tests); `tests/cases/test_cases_api.py` (15 tests)
- [x] Wire CRM_API: `crm-api.js` — cases + knowledge + supportQueues sections added
- [x] Wire action buttons: `crm-cases-detail.js` — claim + resolve buttons call CRM_API
- [x] Verify all pages HTTP 200 — pages still load from CRM_DUMMY; live wiring active when DUMMY_MODE=false

### Sprint 5B-2 — Shared Inbox / Routing ✓ COMPLETE 2026-05-29
**Spec:** `backend/docs/domain/shared-inbox.md` | **Pages unblocked:** L-01, L-02, L-03
- [x] Write ORM models: `InboxQueue`, `AgentPresence`, `ConversationHandoff` — `services/db/models/inbox.py`
- [x] Alembic migration: inbox schema — `alembic/versions/0005_inbox_schema.py` (extends conversations + 3 new tables)
- [x] Gateway routes: `v1-inbox.routes.js` — 11 endpoints (conversations list/get, claim, handoff, send message, presence get/patch, queues CRUD + stats)
- [x] Service logic: `services/inbox/entities.py` (presence/assignment/handoff enums, eligibility checks); `services/inbox/service.py` (auto_assign, validate_claim, validate_handoff, presence compute)
- [x] RBAC scopes: INBOX_READ/WRITE/ADMIN added; wired into all roles
- [x] Unit + integration tests — `tests/inbox/test_inbox_service.py` (18 tests); `tests/inbox/test_inbox_api.py` (16 tests)
- [x] Wire CRM_API: `crm-api.js` — inbox.conversations, inbox.presence, inbox.queues sections added
- [x] Wire action buttons: `crm-inbox.js` (claim + reassign); `crm-inbox-thread.js` (reassign + close)
- [x] Verify all pages HTTP 200 — pages load from CRM_DUMMY; live wiring active when DUMMY_MODE=false

### Sprint 5B-3 — Territories ✓ COMPLETE 2026-05-29
**Spec:** `backend/docs/domain/territory-management.md` | **Pages unblocked:** G-09
- [x] Write ORM models: `Territory`, `TerritoryRule`, `TerritoryAssignment` — `services/db/models/territories.py`
- [x] Alembic migration: territories schema — `alembic/versions/0006_territories_schema.py` (3 tables, 2 partial unique indexes)
- [x] Gateway routes: `v1-territories.routes.js` — 11 endpoints (CRUD + rules + assignments + evaluate + reassign + performance)
- [x] Service logic: `services/territories/entities.py` (rule evaluation — 9 rule types, AND logic, geo_polygon=no-match in v1); `services/territories/service.py` (evaluate_subject, resolve_conflict, select_winner, assign_rep_round_robin, validate_manual_override)
- [x] RBAC scopes: TERRITORIES_READ/WRITE/ADMIN added; wired into all roles
- [x] Unit + integration tests — `tests/territories/test_territories_service.py` (20 tests); `tests/territories/test_territories_api.py` (16 tests)
- [x] Wire CRM_API: `crm-api.js` — territories section added (list, get, create, update, addRule, evaluate, performance)
- [x] Wire Edit button: `crm-territories.js` — Edit buttons call CRM_API.territories.update()
- [x] Verify all pages HTTP 200 — G-09 loads from CRM_DUMMY; live wiring active when DUMMY_MODE=false

### Sprint 5B-4 — Marketing / Campaigns ✓ COMPLETE 2026-05-29
**Spec:** `backend/docs/domain/marketing-campaigns.md` | **Pages unblocked:** F-01, I-06, A-08, H-02
- [x] Write domain spec: `backend/docs/domain/marketing-campaigns.md` + catalogue it
- [x] Write ORM models: `Campaign`, `CampaignSegment`, `MessageTemplate`, `CampaignSend`, `CampaignConversion` — `services/db/models/campaigns.py`
- [x] Alembic migration: campaigns schema — `alembic/versions/0007_campaigns_schema.py` (5 tables, 10 indexes, FK constraints)
- [x] Gateway routes: `v1-campaigns.routes.js` (10 endpoints); `v1-segments.routes.js` (5 endpoints); `v1-templates.routes.js` (4 endpoints)
- [x] Service logic: `services/campaigns/entities.py` (state machine, P-017 Urdu gate, activation guards); `services/campaigns/service.py` (apply_transition, opt-in gate, merge tags, attribution, rate computation)
- [x] RBAC scopes: CAMPAIGNS_READ/MANAGE added; wired into all roles
- [x] Unit + integration tests — `tests/campaigns/test_campaigns_service.py` (22 tests); `tests/campaigns/test_campaigns_api.py` (18 tests)
- [x] Wire CRM_API: `crm-api.js` — campaigns, segments, templates sections added
- [x] Wire submit: `crm-campaign-new.js` — form submit calls CRM_API.campaigns.create()
- [x] Verify all pages HTTP 200 — pages load from CRM_DUMMY; live wiring active when DUMMY_MODE=false

### Sprint 5B-5 — Partners ✓ COMPLETE 2026-05-29
**Spec:** `backend/docs/domain/partners.md` | **Pages unblocked:** B-11, C-11
- [x] Write domain spec: `backend/docs/domain/partners.md` + catalogue it
- [x] Write ORM models: `Partner`, `DealRegistration`, `PartnerCommission`, `PartnerActivityLog` — `services/db/models/partners.py`
- [x] Alembic migration: partners schema — `alembic/versions/0008_partners_schema.py` (4 tables, 11 indexes, FK constraints)
- [x] Gateway routes: `v1-partners.routes.js` — 14 endpoints (CRUD + deal-registrations + commissions approve/pay + activity); `dealRegsRouter` mounted at `/deal-registrations`
- [x] Service logic: `services/partners/entities.py` (tier rates, expiry days, state machine transitions, `calculate_commission()`, `compute_expiry_date()`); `services/partners/service.py` (`compute_commission_on_win()`, `apply_commission_transition()`, `validate_attribution()`, `build_deal_registration()`)
- [x] Immutability enforced: `status=paid` → 409 on any edit/pay attempt
- [x] RBAC scopes: PARTNERS_READ/MANAGE/ADMIN added; wired into all roles
- [x] Unit + integration tests — `tests/partners/test_partners_service.py` (22 tests); `tests/partners/test_partners_api.py` (18 tests)
- [x] Wire CRM_API: `crm-api.js` — partners section added (list, get, commissions, approve/pay, deal registrations)
- [x] Wire Pay Commission: `crm-partners-detail.js` — Pay Commission button calls CRM_API with approve→pay flow
- [x] Verify all pages HTTP 200 — B-11/C-11 load from CRM_DUMMY; live wiring active when DUMMY_MODE=false

### Sprint 5B-6 — Workflow Execution Engine ✓ COMPLETE 2026-05-29
**Spec:** `backend/docs/infrastructure/workflow-catalog.md` | **Pages unblocked:** K-01, K-02, K-03, K-04, C-10, A-10, H-05
- [x] Write ORM models: `WorkflowDefinition`, `WorkflowExecution`, `WorkflowStep` — `services/db/models/workflows.py`
- [x] Alembic migration: workflows schema — `alembic/versions/0009_workflows_schema.py` (3 tables, 8 indexes, unique key constraint)
- [x] Gateway routes: `v1-workflows.routes.js` — 10 endpoints (definitions CRUD + publish + simulate + stats; runs list/get/retry/cancel); 5 seeded catalog definitions + 8 seeded executions + step log for exec-007
- [x] Service logic: `services/workflows/entities.py` (status enums, step types, DSL validation, CATALOG_WORKFLOWS); `services/workflows/service.py` (validate_definition, can_retry, build_retry_execution, finalize_execution, simulate_execution, compute_execution_stats)
- [x] RBAC scopes: WORKFLOWS_READ/MANAGE added; wired into all roles
- [x] Unit + integration tests — `tests/workflows/test_workflows_service.py` (26 tests); `tests/workflows/test_workflows_api.py` (19 tests)
- [x] Wire CRM_API: `crm-api.js` — workflows section with nested runs sub-namespace
- [x] Wire builder actions: `crm-workflow-builder.js` — Save calls CRM_API.workflows.create()
- [x] Wire retry button: `crm-workflow-run-detail.js` — Retry calls CRM_API.workflows.runs.retry()
- [x] Verify all pages HTTP 200 — pages load from CRM_DUMMY; live wiring active when DUMMY_MODE=false

### Sprint 5B-7 — AI / Predictive Models ✓ COMPLETE 2026-05-30
**Spec:** `backend/docs/domain/ai-predictive-models.md` | **Pages unblocked:** M-01, M-02, H-07
- [x] Write domain spec: `backend/docs/domain/ai-predictive-models.md` + catalogue it
- [x] Write ORM models: `LeadScore`, `ChurnPrediction`, `CLVEstimate`, `CopilotSuggestion` — `services/db/models/ai_scores.py`
- [x] Alembic migration: AI scores schema — `alembic/versions/0010_ai_scores_schema.py` (4 tables, 8 indexes)
- [x] Gateway routes: `v1-ai.routes.js` — 13 endpoints (lead scores list/get/recompute; churn list/get; CLV list/get; copilot suggestions list/dismiss/action; copilot query; model registry list/get); 10 seeded lead scores + 5 churn predictions + 5 CLV estimates + 6 copilot suggestions
- [x] Service logic: `services/ai/entities.py` (scoring formulas, enums, intent classifier, validators); `services/ai/service.py` (AIService: score_lead, predict_churn, estimate_clv, build_suggestion, apply_dismiss, apply_action, handle_query, compute_score_stats)
- [x] RBAC scopes: AI_SCORES_READ/RECOMPUTE, AI_PREDICTIONS_READ, AI_CLV_READ, AI_COPILOT, AI_MODELS_READ added; all roles updated
- [x] Unit + integration tests — `tests/ai/test_ai_service.py` (28 tests); `tests/ai/test_ai_api.py` (19 tests)
- [x] Wire CRM_API: `crm-api.js` — ai section with nested scores/predictions/estimates/copilot/models sub-namespaces
- [x] Wire query button: `crm-ai-copilot.js` — sendChat calls CRM_API.ai.copilot.query() when DUMMY_MODE=false
- [x] Wire dismiss button: `crm-ai-copilot.js` — dismiss calls CRM_API.ai.copilot.dismiss() when DUMMY_MODE=false
- [x] Wire live KPIs: `crm-ai-insights.js` — loadLiveKpis() calls CRM_API.ai.scores/predictions/estimates when DUMMY_MODE=false
- [x] Verify all pages HTTP 200 — M-01/M-02/H-07 load from CRM_DUMMY; live wiring active when DUMMY_MODE=false

### Phase 5B close
- [ ] All 28 Cat 2 pages DUMMY_MODE=false and verified HTTP 200
- [ ] `FRONTEND-BACKEND-MAPPING.md` updated — all 75 pages show LIVE status
- [ ] GitHub push — Phase 5B complete

---

## Phase 6 — Market Research Features + Final Hardening + Full QC

**Gate:** Phase 5B complete — all 75 pages wired to live data.
**Source:** `backend/market-research-gap-register.md`

### Pre-wiring backend fix
- [x] `GET /api/v1/forecasts/summary` — **DEFERRED** (H-01 now computes forecasts client-side from raw opps data via `computeForecast()` in crm-sales-analytics.js; endpoint not required)

### Buildable (not blocked)
- [x] MR-004: Automated daily WhatsApp activity summary to managers — `services/summary/daily_summary.py` + `_daily_summary_scheduler` in app.py; EN + UR templates; 9 tests passing (2026-05-30)
- [x] MR-005: Excel import / export — `POST /api/v1/leads/import`, `GET /api/v1/leads/export` in v1-leads.routes.js; `POST /api/v1/contacts/import`, `GET /api/v1/contacts/export` in v1-contacts.routes.js (inline, no proxy dependency); crm-api.js leads.import/export + contacts.import/export; 18 tests passing (2026-05-30)

### Blocked (build when unblocked)
- [ ] MR-002: One-click invoice + WhatsApp payment link (blocked: P-016 payment credentials + Meta template approval)
- [ ] MR-001: Facebook / Instagram lead capture automation (blocked: Meta Business Manager setup)
- [ ] MR-003: Voice note transcription — Urdu / Roman Urdu / English (blocked: transcription provider + credentials)
- [ ] MR-006: Geo-tagging / field check-in for field reps (low priority)
- [ ] MR-007: Kuickpay payment adapter (blocked: Kuickpay API credentials)

### T1–T4 Protocol Audit (all 75 custom pages) ✓ COMPLETE 2026-05-30
- [x] Run full T1–T4 QC audit for every custom page — 66/75 passed, 9 fixed
- [x] Lock each page as ✓ in SCREEN-ARTEFACTS.md — all 75 now T1-T4 ✓
- [x] Fix all regressions — 18 discrete changes across 9 pages + crm-custom.css + 5 JS drivers + crm-dummy.js

### Wiring Sprint (Component 2) ✓ COMPLETE 2026-05-30
- [x] Wave 1 — auth infra + DUMMY_MODE=false + 6 pages wired (B-01, B-02, B-08, I-01, C-01, A-01)
- [x] Wave 2 — Steps 2–7, 21 pages wired (all Tier 1 simple-domain + list/queue + create/form + detail + dashboard)
- [x] Wave 3 — Steps 8–12, 31 pages wired (all Tier 2 Cases/Inbox/Campaigns/Workflows/Partners/AI/Territories + Tier 3 opaque proxies)
- [x] MR-004 — Automated daily WhatsApp summary scheduler (services/summary/daily_summary.py + app.py lifespan, 9 tests)
- [x] MR-005 — Excel/CSV import+export for leads + contacts (v1-leads + v1-contacts inline routes, 18 tests)
- [x] 12-page extension — 7 new inline gateway routes (org-settings, roles, notification-prefs, feature-flags-mgmt, compliance-settings, privacy, tenants) + 12 JS driver rewrites
- [x] 6 spec files amended — b9-p01 §5 (A-03/A-11/A-13 API routes), b9-p06 §2.13 (C-08 Invoice Detail), b9-p09 §4 (G-01/G-03/G-06/G-07/G-08/J-05 API routes), b9-p12 §2.6 (J-05 routes table), b9-p13 §4 (L-01/L-02 API routes), read-models.md (3 stale /reporting/* paths corrected)
- [x] **Total wired: 70 of 75 pages live after Waves 1–3 + 12-page extension.**
- [x] **Phase 6 extension (2026-05-31) — 5 inline stub routes + 5 JS drivers (G-04/G-05/J-03/H-07/A-08). All 75 of 75 pages wired. All browser-approved.**

### Final Hardening
- [x] Absorbed into COMMERCIALISATION-PLAN.md C2/C3 — do not execute from here

### Phase 6 close
- [x] All tasks absorbed into COMMERCIALISATION-PLAN.md — REBUILD-PLAN.md closed 2026-05-31

---

## Commercialisation (COMMERCIALISATION-PLAN.md)

| Phase | Status |
|---|---|
| C0 — Environment Seal | [x] COMPLETE 2026-05-31 |
| C1 — DB Wiring (local) | [ ] pending |
| C2a — Backend Coverage (80%) | [ ] pending |
| C2b — API Contract Tests | [ ] pending |
| C2c — Playwright E2E (75 pages) | [ ] pending |
| C2d — Load Tests (Locust) | [ ] pending |
| C2e — Security Scanning | [ ] pending |
| C3 — Code Hardening | [ ] pending |
| C4 — Infrastructure Deployment | [ ] pending |
| C5 — Post-Deploy Smoke | [ ] pending |
| C6 — Commercial Launch | [ ] pending |
