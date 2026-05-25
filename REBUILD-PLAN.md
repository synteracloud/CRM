# Pakistan CRM OS — Rebuild Plan (10/10 Roadmap)

**Created:** 2026-05-18
**Revised:** 2026-05-25 — Phase 4 Stage 1 COMPLETE: 51 specs read line-by-line, 30 duplication clusters logged. Prior: 2026-05-22 — Sprint 0 COMPLETE (19/24 tasks done)
**Status:** Phase 1 — COMPLETE ✓ | Phase 2 — COMPLETE ✓ | Phase 3 — COMPLETE ✓ | Phase 4 — IN PROGRESS (Stage 0 + Stage 1 done · Stage 2 Code Overlay next) | Phase 5 — NOT STARTED | Phase 6 — NOT STARTED
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

## Phase 4 — Backend Hardening (~4 weeks) — IN PROGRESS
**Goal:** Normalise all docs, overlay docs on code, fix every gap found. Gates Phase 5.
**Progress:** 20/24 tasks done (83%) — design docs + pre-phase fixes DONE · Stage 1 DONE · Stage 2–3 pending

### Stage 0 — Design Docs + Pre-Phase Fixes ✓ COMPLETE (2026-05-19)
All 9 missing design docs written and catalogued. 9 pre-phase audit fixes applied.

### Stage 1 — Doc Normalisation ✓ COMPLETE (2026-05-23)
All 51 §F + §H specs read line-by-line. 30 duplication/overlap clusters identified and logged in `backend/docs/phase4-stage1-read-log.md`. Findings submitted for review.

### Stage 2 — Code Overlay
Overlay normalised docs on the codebase. For every entity, API endpoint, and business rule defined in the specs: verify it exists in code and is correctly implemented. Fix every gap found. Output: `backend/docs/phase4-gap-register.md` recording what was found and fixed.

### Stage 3 — Mapping Rebuild + Push
Rebuild `FRONTEND-BACKEND-MAPPING.md` to reflect true current state — every endpoint marked LIVE, BUILD, or MISSING. Verify all 96 existing pages still HTTP 200. GitHub push — Phase 4 complete.

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
