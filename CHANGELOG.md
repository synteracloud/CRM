# Changelog

All notable changes to the Pakistan CRM OS are documented here.

Format: [Semantic Versioning](https://semver.org). Each entry covers a build session or phase.

---

## [Unreleased] — Rebuild Phase 4 next (75 frontend custom pages)

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
