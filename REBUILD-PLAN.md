# Pakistan CRM OS — Rebuild Plan (10/10 Roadmap)

**Created:** 2026-05-18
**Status:** Phase 1 — COMPLETE ✓ | Phase 2 — NOT STARTED
**Anchor:** This file. Update on every phase start and completion.
**Task tracker:** `PENDING.md` (root) — checkbox list, updated as work completes
**Session log:** `PROGRESS.md` — updated every session
**Estimated total duration:** ~15 weeks

---

## Current State vs Target

| Area | Current | Target | Gap |
|---|---|---|---|
| Documentation | 9/10 | 10/10 | CHANGELOG, root README, CONTRIBUTING, ADRs, OpenAPI |
| Architecture design | 8/10 | 10/10 | Code must match docs; event bus; service boundaries in code |
| Project structure | 7/10 | 10/10 | Docker, Makefile, pre-commit, Alembic |
| Code implementation | 3/10 | 10/10 | All 6 engines unimplemented; only stubs exist |
| Testing | 0/10 | 10/10 | Zero tests anywhere |
| DevOps / CI-CD | 2/10 | 10/10 | No working pipeline; no containers |
| Security implementation | 4/10 | 10/10 | Docs solid; code enforces nothing yet |
| Frontend | 7/10 | 10/10 | 75 custom pages unbuilt; no API wiring |
| **Overall** | **6.5/10** | **10/10** | |

---

## Phase Summary

| Phase | Name | Est. duration | Grade after |
|---|---|---|---|
| Phase 1 | Foundation Seal | ~1 week | 7.5/10 |
| Phase 2 | Follow-up Engine (first full vertical) | ~2 weeks | 8.0/10 |
| Phase 3 | Remaining 5 Engines | ~6 weeks | 8.5/10 |
| Phase 4 | Frontend — 75 Custom Pages | ~4 weeks | 9.0/10 |
| Phase 5 | Hardening (CI/CD, security, testing) | ~2 weeks | 10/10 |

---

## Phase 1 — Foundation Seal (~1 week)
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

## Phase 2 — Follow-up Engine (~2 weeks)
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

## Phase 3 — Remaining 5 Engines (~6 weeks)
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

## Phase 4 — Frontend: 75 Custom Pages (~4 weeks)
**Lifts:** Frontend 10/10

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

## Phase 5 — Hardening (~2 weeks)
**Lifts:** DevOps 10/10 · Security 10/10 · Testing 10/10

### CI/CD
- GitHub Actions: lint on every push
- GitHub Actions: test on every push
- GitHub Actions: build on push to main
- GitHub Actions: deploy to staging on merge to main

### Security
- Rate limiting middleware: 10k/min per-tenant from `security-model.md`
- Secrets moved to GitHub Secrets (remove all raw .env from CI)
- Bandit (Python security scan) in CI pipeline
- npm audit in CI pipeline

### Observability
- structlog wired to all services
- Request logging middleware
- Distributed trace headers

### Testing
- Coverage gate: CI blocks merge if coverage < 80%
- Load test (locust): happy path — follow-up queue + collections
- Full E2E: lead capture → follow-up → close → invoice → payment

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
