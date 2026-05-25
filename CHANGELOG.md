# Changelog

All notable changes to the Pakistan CRM OS are documented here.

Format: [Semantic Versioning](https://semver.org). Each entry covers a build session or phase.

---

## [Unreleased]

---

## [0.25.0] — 2026-05-25 — Phase 4 Stage 3: Code Overlay Round 1

### Added
- `backend/docs/phase4-gap-register.md` — living gap register; 28 gaps catalogued across Groups A–E (persistence, security, domain APIs, API standards, observability/CI)
- `backend/alembic/versions/0002_followup_states_leads_idempotency.py` — migration: `snoozed`+`failed` followup states, `leads.closure_reason`, FK `followup_tasks→leads`, `idempotency_records` table
- `backend/alembic/versions/0003_collections_conversations.py` — migration: `invoices`, `payments`, `reconciliation_cases`, `conversations`, `conversation_messages` tables
- `backend/services/db/models/collections.py` — `Invoice`, `Payment`, `ReconciliationCase` ORM models
- `backend/services/db/models/conversations.py` — `Conversation`, `ConversationMessage` ORM models
- `backend/services/db/models/idempotency.py` — `IdempotencyRecord` ORM model (4-tuple key, state: in_flight/complete/conflict)

### Fixed — Security / Auth
- `services/auth/jwt_deps.py` (B-001) — `TokenClaims` extended from 4 → 9 claims: added `role_ids`, `scopes`, `aud`, `iss`, `territory_ids`; conditional aud/iss verification from env vars

### Fixed — API Correctness
- `gateway/routes/v1-leads.routes.js` (D-001) — `VALID_STAGES` aligned to DB + spec: `qualifying, nurturing, won, lost, disqualified` (was `new, contacted, qualified, proposal, negotiation, closed_won, closed_lost`)

### Fixed — State Machines
- Migration 0002 (D-002) — `followup_tasks.state` CHECK extended to include `snoozed` + `failed` states
- Migration 0002 (D-010) — `leads.closure_reason TEXT NULL` column + FK `followup_tasks → leads`

### Fixed — Bugs
- `services/activity/engine.py` — `_parse_rfc3339`: `.replace("Z", "+00:00")` → `.rstrip("Z")` — prevented double-offset `+00:00+00:00` crash (`ValueError: Invalid isoformat string`)
- `services/dashboard/owner/service.py` — `_parse_dt`: same double-offset fix
- `adapters/pakistan/payments/jazzcash.py` — `normalize_transaction`: only divide by 100 for `pp_Amount` (native JazzCash paise format); `amount` fallback key is already PKR
- `services/collections/service.py` — `_payments` dict added; fixes `AttributeError` from dashboard service

### Fixed — Infrastructure
- `src/event_bus/catalog_schema.py` — path updated for Stage 2E subdirectory restructure
- `src/event_bus/catalog_events.py` — 9 missing events added: `lead.conversion.failed.v1`, 2 `case.sla.*`, 6 `partner.*` events
- `scripts/self_qc_event_bus.py`, `self_qc_execution_hardening.py`, `self_qc_final_supervisor.py` — all doc paths updated for Stage 2E 9-subdir structure

### Verified
- 314/314 tests passing (was 308 before Stage 3)
- 96/96 library pages HTTP 200

---

## [0.24.0] — 2026-05-25 — Phase 4 Stage 2: Doc Fix + Restructure

### Changed
- All 71 flat `backend/docs/*.md` files reorganised into 9 subdirectories (Diátaxis + DDD taxonomy): `architecture/`, `security/`, `domain/`, `infrastructure/`, `adapters/`, `product/`, `ui/`, `_b9/`, `_qc/`
- Ownership blocks (PRIMARY / Defers to / Do not re-define) added to all 51 core spec files (Stage 2A)
- 6 gap fills added to owning spec files (Stage 2B): `territory_ids` JWT claim, EmployeePerformanceRM, TerritoryPerformanceRM, TenantUsageMetric, deny-by-default, tone tiers
- 6 inconsistencies resolved — canonical values locked, non-PRIMARY files updated (Stage 2C)
- 14 duplicate definitions replaced with cross-reference pointers; 4 misplaced content blocks moved (Stage 2D)
- All cross-references + `DOC-CATALOGUE.md` paths updated for new subdirectory structure (Stage 2E)
- `DOC-CATALOGUE.md` — 103 active docs catalogued (75 backend + others)

### Verified
- 308/308 tests passing
- 96/96 library pages HTTP 200

---

## [0.23.1] — 2026-05-18 — Pre-Phase-4 Audit: 9 Fixes

### Fixed — Critical / High
- `src/ticket_management/entities.py` — added `Literal` to typing import; `pytest` from backend/ root no longer aborts on collection (was hidden by collection error)
- `services/app.py` — lifespan now wires public router singletons in production (`PYTEST_CURRENT_TEST` gate preserves test isolation); activity + collections public routers share same in-memory instance as internal routers

### Fixed — Security / Auth
- `services/followup/http/public.py` — `POST /api/v1/followups/{id}/escalate` now requires `manager` or `admin` role; `sales_rep` returns 403; `_require_manager()` helper added; `client_manager` test fixture added

### Fixed — Business Logic
- `services/followup/overdue.py` (new) — `scan_overdue_tasks(db)` scans for pending tasks past `due_at` and marks them `overdue`
- `services/app.py` — asyncio background task `_overdue_scanner` runs every 60 s in production; starts in lifespan, cancelled cleanly on shutdown

### Fixed — API Correctness
- `services/followup/http/public.py` — `list_followups` double-query replaced with single `SELECT COUNT(*)` via `func.count()`
- `services/collections/http/public.py` — `POST /api/v1/invoices/{id}/send` endpoint added; returns scheduled WhatsApp reminder dates
- `services/conversation/http/public.py` — `GET /api/v1/conversations/{id}` detail endpoint added; returns conversation + full message thread

### Fixed — Data Correctness
- `services/collections/entities.py` — `tenant_id: str = ""` field added to `Invoice`; stamped from `claims.tenant_id` on creation; `list_invoices` now filters by tenant

### Fixed — Code Quality
- `services/activity/entities.py`, `services/collections/entities.py` — `datetime.utcnow()` replaced with `datetime.now(timezone.utc)`

### Tests
- `tests/followup/test_overdue_scanner.py` (new) — 4 tests for overdue scanner
- `tests/followup/test_public_api.py` — updated escalation tests to use `client_manager`; +1 test (`test_sales_rep_cannot_escalate`)
- `tests/coll/test_collections_public.py` — +3 tests (`TestSendInvoice`) + 2 tests (`TestTenantIsolation`)
- `tests/conversation/test_whatsapp_public.py` — +4 tests (`TestGetConversation`)

### Verified
- 308/308 tests passing (93 original Phase 2+3 + 14 new from audit fixes + 201 legacy src/ tests now visible after P3-A fix)
- 96/96 library pages HTTP 200

---

## [0.23.0] — 2026-05-18 — Phase 3: 5 Engines — Public API Layer

### Added — Sprint 1: WhatsApp Engine
- `backend/services/conversation/http/public.py` — `POST /api/v1/webhooks/whatsapp` (API-key auth) + `GET /api/v1/conversations` (JWT)
- Intent classification via keyword rules (payment_query > follow_up_response > lead_inquiry > support_request)
- Anti-lead-loss guarantee: every inbound message creates/updates a conversation record
- `backend/tests/conversation/test_whatsapp_public.py` — 12 tests

### Added — Sprint 2: Collections Engine
- `backend/services/collections/http/public.py` — `POST/GET /api/v1/invoices` (JWT) + `POST /api/v1/payments/callback/{provider}` (API-key auth)
- JazzCash/Easypaisa payment callback → auto-reconciliation against open invoices
- `backend/tests/coll/test_collections_public.py` — 11 tests

### Added — Sprint 3: Activity Control Engine
- `backend/services/activity/http/public.py` — `POST /api/v1/activities` + `GET /api/v1/activities` + `GET /api/v1/activities/chain-integrity` (JWT)
- Immutable audit hash chain exposed via public endpoint
- `backend/tests/activity/test_activity_public.py` — 10 tests

### Added — Sprint 4: Activation Engine
- `backend/services/activation/http/__init__.py` + `public.py` — `POST /api/v1/activation/start` + `/whatsapp-sim` + `/move-deal` + `GET /api/v1/activation/status` (JWT)
- <10-minute activation path: seed 5 contacts + 4 deals + pipeline; Aha triggered by first inbound + deal move
- `backend/tests/activation/test_activation_public.py` — 10 tests

### Added — Sprint 5: Execution Control Plane (DLQ Operator API)
- `backend/services/core/execution/http/__init__.py` + `public.py` — `GET /api/v1/admin/dead-letters` + `POST /{id}/retry` + `POST /{id}/requeue` (JWT, admin role)
- `backend/tests/execution/test_dlq_public.py` — 10 tests

### Changed
- `backend/services/app.py` — mounted all 5 new public routers

### Verified
- 93/93 tests passing (38 Phase 2 + 55 Phase 3)
- 96/96 library pages HTTP 200

---

## [0.22.0] — 2026-05-18 — Phase 2: Follow-up Engine

### Added
- `backend/services/db/base.py` — SQLAlchemy declarative base
- `backend/services/db/__init__.py` — lazy session factory (no import-time Postgres connection)
- `backend/services/db/models/followup.py` — `FollowupTask` + `FollowupEscalation` ORM models
- `backend/services/db/models/lead.py` — `Lead` ORM model
- `backend/services/db/models/activity.py` — `Activity` ORM model
- `backend/alembic/versions/0001_followup_schema.py` — first real schema migration
- `backend/services/auth/jwt_deps.py` — `get_current_user` FastAPI dependency (JWT Bearer validation)
- `backend/services/followup/http/public.py` — public REST router: 5 endpoints at `/api/v1/followups`
- `backend/tests/followup/test_enforcement.py` — 18 unit tests (timers, escalation ladder, closure gate)
- `backend/tests/followup/test_public_api.py` — 20 integration tests (all endpoints, happy path + error states)
- `pytest`, `httpx`, `python-jose[cryptography]` added to `requirements.txt`

### Changed
- `backend/alembic/env.py` — wired to `Base.metadata` (autogenerate-ready)
- `backend/services/app.py` — public followup router mounted at `/api/v1/followups`

### Verified
- 38/38 tests passing
- 96/96 library pages HTTP 200

---

## [0.21.0] — 2026-05-18 — Phase 1: Foundation Seal

### Added
- `README.md` (root) — GitHub landing page with quick start, architecture diagram, doc index
- `CHANGELOG.md` — this file
- `CONTRIBUTING.md` — branch naming, commit format, PR process
- `Makefile` — make dev, make test, make migrate, make lint
- `.pre-commit-config.yaml` — ruff + black enforced on every commit
- `backend/docs/adr/ADR-001.md` — DDD + microservices architecture decision
- `backend/docs/adr/ADR-002.md` — Adapter pattern for Pakistan isolation
- `backend/docs/adr/ADR-003.md` — WhatsApp-first interaction model
- Alembic migration framework — configured in `backend/alembic/`
- `REBUILD-PLAN.md` — 5-phase 10/10 roadmap
- `PENDING.md` (root) — 155-task rebuild checklist

---

## [0.20.0] — 2026-05-18 — Infrastructure Seal

### Added
- Python 3.12.10 runtime at `D:\Python` — zero C: leakage
- Python venv at `D:\CRM\backend\.venv` — fastapi 0.115.0, uvicorn 0.30.6, pydantic 2.8.2 installed
- `frontend/.npmrc` — npm cache locked to `D:\CRM\.npm-cache`
- `C:\Users\Admin\AppData\Roaming\pip\pip.ini` — pip cache locked to `D:\CRM\.pip-cache`
- `backend/.gitignore` — full Python ignore rules added
- `.gitignore` (root) — cache and runtime dirs locked to D:\CRM

### Changed
- Dev server path confirmed: `npm run serve` from `D:\CRM\frontend` — port 3001

### Fixed
- All 96 library pages verified HTTP 200 after folder restructure

---

## [0.19.0] — 2026-05-17 — Doc Production Readiness

### Changed
- 93 production-readiness gaps fixed across 26 backend docs
- 11 linkage/cross-reference issues resolved across all docs
- Naming normalisation: ALL-CAPS authority files, kebab-case QC/domain docs
- `DOC-CATALOGUE.md` overhauled as ground-truth document index

---

## [0.18.0] — 2026-05-17 — Workspace Restructure

### Changed
- Folder restructure: `V4_extracted/CRM-main` → `backend/`; nexlink triple-wrap → `frontend/`
- All internal paths updated across all docs

---

## [0.17.0] — 2026-05-15 — Library Phase Complete

### Added
- Session 17: AI section pages (investment, new-chat, new-project, plans, search-chat, search-image, your-chat, search-apps, search-apps-details) — self-contained pages with own aside + header, no crm-shell.js

### Changed
- All 96/96 NexLink library pages complete — all browser-approved

---

## [0.10.0–0.16.0] — 2026-05-12 to 2026-05-15 — Library Build Phase

### Added
- 96 NexLink library pages built across 17 batches
- crm-shell.js, crm-api.js (DUMMY_MODE), crm-dummy.js
- All authentication, error, chart, map, icon, component, form pages complete

---

## [0.1.0] — Project Initialisation

### Added
- Pakistan CRM OS project initialised
- DDD microservices backend architecture designed
- 47 domain spec documents written
- 13-archetype UI spec system (b9-p series)
- Pakistan adapter architecture (JazzCash, Easypaisa, WhatsApp)
- Database schemas for all core domains
