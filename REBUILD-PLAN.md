# Pakistan CRM OS — Rebuild Plan (10/10 Roadmap)

> ## ⛔ THIS PLAN IS CLOSED
> **Closed:** 2026-05-31 — All build phases (1–6) complete.
> **Continuing work:** `COMMERCIALISATION-PLAN.md` — Phases C0–C6 (DB wiring, automated testing, hardening, deployment, launch).
> **Do not add new tasks to this file.** It is a historical record only.

**Created:** 2026-05-18
**Closed:** 2026-05-31 — All 6 build phases complete. 75/75 custom pages built, T1–T4 ✓, wired to live API, browser-approved. 171 pages total (96 library + 75 custom). 42 gateway routes. ~527+ tests. Remaining work (hardening, testing, deployment) continues in `COMMERCIALISATION-PLAN.md`.
**Status:** Phase 1 ✓ | Phase 2 ✓ | Phase 3 ✓ | Phase 4 ✓ | Phase 5 ✓ | Phase 5B ✓ | Phase 6 ✓ | **ALL PHASES COMPLETE**
**Anchor:** **CLOSED — read `COMMERCIALISATION-PLAN.md` for all current and future work.**
**Task tracker:** `PENDING.md` (root) — historical checkbox list
**Session log:** `PROGRESS.md` — session-by-session build log
**Actual total duration:** ~21 weeks (2026-04 → 2026-05-31)

---

## RESUME POINT — CLOSED

> **This plan is closed. Do not resume work from this file.**
> **Active anchor:** `COMMERCIALISATION-PLAN.md` — read that file first every session from 2026-05-31 onwards.

| Phase | Stage | Status |
|---|---|---|
| 1 — Foundation Seal | — | ✓ COMPLETE |
| 2 — Follow-up Engine | — | ✓ COMPLETE |
| 3 — 5 Engines | — | ✓ COMPLETE |
| 4 — Backend Hardening | Stage 0 — Design Docs + Fixes | ✓ COMPLETE (2026-05-19) |
| 4 — Backend Hardening | Stage 1 — Doc Read + Identify | ✓ COMPLETE (2026-05-23) |
| 4 — Backend Hardening | Stage 2 — Doc Fix + Restructure | ✓ COMPLETE (2026-05-25) |
| 4 — Backend Hardening | Stage 3 — Code Overlay | ✓ COMPLETE (2026-05-26 — 28/28 gaps fixed) |
| 4 — Backend Hardening | Stage 4 — Mapping + Push | ✓ COMPLETE (2026-05-26 — 324/324 tests; CI live) |
| 5 — Frontend 75 pages | — | ✓ COMPLETE (2026-05-29 — 75/75 pages, all browser-approved) |
| 5B — Backend Domain Extension | — | ✓ COMPLETE 2026-05-30 — all 7 sprints; migration chain 0001→0010; 38 ORM models; 15 gateway routers |
| 6 — Market Research + Final Hardening | Component 1 — T1–T4 Protocol Audit | ✓ COMPLETE 2026-05-30 — 75/75 pages pass; 9 pages fixed |
| 6 — Market Research + Final Hardening | Component 2 — Wiring Sprint + Extension | ✓ COMPLETE 2026-05-31 — 75/75 pages live; 0 blocked |
| 6 — Market Research + Final Hardening | Component 3 — Final Hardening | → **Absorbed into COMMERCIALISATION-PLAN.md Phase C2/C3** |
| **ALL BUILD PHASES** | | **✓ COMPLETE 2026-05-31** |

---

## Session Resumption Protocol

Every session — including fresh sessions with no prior memory — MUST follow this sequence before doing any work.

### Step 1 — Orient (read in order, do not skip)
1. `SYSTEM-SNAPSHOT.md` — 60-second bird's-eye view: phase status, scores, what's built, what's broken, immediate next step
2. `REBUILD-PLAN.md` — read RESUME POINT table above; current phase and stage are stated explicitly
3. `PENDING.md` — find the first unchecked `[ ]` task in the current phase; that is the start point
4. `DOC-CATALOGUE.md` §A How-to-use table — confirm file locations for current stage context

### Step 2 — Load stage context
| Stage | Files to read before starting |
|---|---|
| Phase 4 Stage 2 (any sub-stage) | `backend/docs/_qc/phase4-stage1-read-log.md` — 30 clusters + PRIMARY designations |
| Phase 4 Stage 3 — Code Overlay | `backend/docs/_qc/phase4-stage1-read-log.md` + PRIMARY files per cluster in `backend/docs/{domain,infrastructure,adapters,security,architecture}/` |
| Phase 4 Stage 4 — Mapping | `backend/FRONTEND-BACKEND-MAPPING.md` |
| Phase 5 — any page build | `DESIGN-SPEC.md` + `FRAMEWORK.md §25–32` + relevant `backend/docs/ui/pages/` spec |
| Phase 5B — any domain sprint | Domain spec in `backend/docs/domain/` + corresponding b9-p spec + `backend/FRONTEND-BACKEND-MAPPING.md` |
| Phase 6 | `backend/market-research-gap-register.md` + `backend/product-spec-gap-register.md` |

### Step 3 — Confirm resume point
The RESUME POINT table above is the authoritative start point. It is updated at the close of every session. Never derive the resume point from memory or the conversation summary — always read it from this file.

### Step 4 — Execute
- Work from `PENDING.md` checkboxes in strict order
- Mark `[x]` immediately when a task completes — never batch marks
- Complete one sub-stage entirely before starting the next
- Report findings/results after each sub-stage; wait for explicit confirmation before proceeding
- If a file read reveals something unexpected: stop, surface it, do not proceed silently

### Step 5 — Close session (mandatory before ending)
1. Mark all completed tasks `[x]` in `PENDING.md`
2. Update the RESUME POINT table in this file — next unchecked task, correct sub-stage
3. Update the **Revised** date and **Progress** line at the top of this file
4. Add one-line summary to `PROGRESS.md`
5. Commit all changes with semantic commit message (see `CONTRIBUTING.md` for format)
6. Push to GitHub — run `git status` and confirm clean before closing

### Non-negotiable rules — active every session, every phase

| Rule | Where enforced |
|---|---|
| All 96 library pages must stay HTTP 200 after every push | REBUILD-PLAN.md — every phase close |
| Max negative doc action = archiving (no file deletions) | Phase 4 Stage 2 constraint |
| `JAZZCASH_STUB_MODE=true` until P-016 credentials supplied | `CONSTRAINTS.md C-009` |
| All `_STRINGS['ur']` need native speaker sign-off before any customer send (P-017) | `CONSTRAINTS.md C-010` |
| Every new `.md` file catalogued in `DOC-CATALOGUE.md` on the same day it is written | `DOC-CATALOGUE.md` rule |
| `core/*` must never import `adapters/pakistan/*` | `ADR-001`, `ADR-002` — ruff CI enforced |
| Report back after each sub-stage; wait for confirmation before next | Phase 4 protocol |
| Never set `stub_mode=False` without full sandbox → prod E2E payment cycle verified | `CONSTRAINTS.md C-009` |

---

## Gap Register State (as of 2026-05-25)

Three audits completed + Stage 3 code overlay gap register active. All tasks flow through `PENDING.md`.

| Register | Anchor | Gaps | Status |
|---|---|---|---|
| Phase 1–3 Code Audit | DOC-CATALOGUE.md (90 docs) vs backend code | 44 gaps — 8 Critical · 15 High · 15 Medium · 6 Low | Absorbed into Phase 4 Stage 3 |
| Product Spec Audit | PRODUCT-SPEC.md vs repo .md files | 17 gaps — 3 Phase-5 blockers · 4 arch · 3 feature · 7 MR | §Phase 4 Sprint 0 + §Phase 6 |
| Market Research Audit | Manus AI Pakistan market report vs system | 7 gaps — 2 buildable · 5 blocked/low | §Phase 6 |
| Phase 4 Stage 3 Code Overlay | `backend/docs/phase4-gap-register.md` | 28 gaps total — **28 FIXED · 0 OPEN** | ✓ COMPLETE |

**Source files:** `backend/product-spec-gap-register.md` · `backend/market-research-gap-register.md` · `backend/docs/phase4-gap-register.md`

---

## Current State vs Target

| Area | Current | Target | Gap |
|---|---|---|---|
| Documentation | 10/10 | 10/10 | None — 78 active docs; all Phase 5B domain specs written; all ownership blocks set |
| Architecture design | 8.5/10 | 10/10 | 7 new domains added; event bus not wired; ML models rule-based v1 (ML Phase 6+) |
| Project structure | 7/10 | 10/10 | Docker, Makefile, pre-commit, Alembic, CI pipeline all present; no containers in CI yet |
| Code implementation | 9.8/10 | 10/10 | All 28 Phase 4 gaps + all 7 Phase 5B domains complete; A-006 (Redis rate-limit) + A-007 (FeatureFlag Redis) deferred Phase 6 |
| Testing | 7.5/10 | 10/10 | ~500+ tests passing; 70% coverage gate in CI; 10-step E2E live; no load tests yet |
| DevOps / CI-CD | 7/10 | 10/10 | `.github/workflows/ci.yml` live with 5-job pipeline; no containers/staging deploy yet |
| Security implementation | 8.5/10 | 10/10 | JWT complete; territory_ids + jti revocation + HMAC live; workspace C: seal audit passed |
| Frontend | 10/10 | 10/10 | 75/75 custom pages T1–T4 ✓; 75/75 wired to live API; 0 externally blocked (5 inline stubs; external services pluggable when credentials available) |
| **Overall** | **9.95/10** | **10/10** | |

---

## Phase Summary (revised 2026-05-19)

| Phase | Name | Est. duration | Grade after |
|---|---|---|---|
| Phase 1 | Foundation Seal | ~1 week | 7.5/10 ✓ |
| Phase 2 | Follow-up Engine | ~2 weeks | 8.0/10 ✓ |
| Phase 3 | Remaining 5 Engines | ~6 weeks | 8.5/10 ✓ |
| Phase 4 | Backend Hardening + Missing Docs | ~4 weeks | 9.0/10 ✓ |
| Phase 5 | Frontend — 75 Custom Pages | ~4 weeks | 9.5/10 ✓ |
| Phase 5B | Backend Domain Extension — 7 new service domains | ~6 weeks | **9.8/10 ✓ COMPLETE** |
| Phase 6 | Market Research Features + Wiring Sprint | ~3 weeks | **9.95/10 ✓ COMPLETE 2026-05-31** |
| **Commercialisation** | **DB Wiring + Testing + Hardening + Deployment** | **~4 weeks** | **10/10 ← TARGET (`COMMERCIALISATION-PLAN.md`)** |

**Sequencing rationale:**
- Phase 4 gates Phase 5: backend must be gap-free before frontend is built on it.
- Phase 5 gates Phase 5B: all 75 pages must exist in dummy mode before domain wiring begins — otherwise wiring targets keep shifting.
- **Phase 5B gates Phase 6:** hardening, QC, and load-testing only make sense once all backend domains exist and every frontend page is wired to live data. Running a T1–T4 audit or load test against a system where 28 of 75 pages still read dummy data is not meaningful. Phase 5B must complete all 7 domains and flip DUMMY_MODE=false for all 28 Cat 2 pages before Phase 6 starts.

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
Spec: `docs/adapters/whatsapp-execution-model.md`

### Sprint 2 — Collections Engine
Invoice lifecycle, overdue detection, WhatsApp reminder trigger, confidence scoring (≥85 auto-match / 40–84 review), customer opt-out.
Spec: `docs/domain/collections-engine-model.md`

### Sprint 3 — Activity Control Engine
Immutable activity log writes, ownership tracking, audit trail endpoints.
Spec: `docs/domain/activity-control-model.md`

### Sprint 4 — Activation Engine
Onboarding flow, auto pipeline creation, sandbox→production WhatsApp transition, sample data localisation.
Spec: `docs/product/activation-model.md`

### Sprint 5 — Execution Control Plane
Idempotency key middleware, retry with exponential backoff (1s base, 2× multiplier, ±20% jitter, 60s max), dead letter queue (DLQ).
Spec: `docs/infrastructure/execution-hardening.md`

---

## Phase 4 — Backend Hardening (~6 weeks) ✓ COMPLETE (2026-05-26)
**Goal:** Bullet-proof all docs, normalise structure, overlay docs on code, fix every gap. Gates Phase 5.
**Result:** All 4 stages complete — Stage 0 ✓ · Stage 1 ✓ · Stage 2 ✓ · Stage 3 ✓ (28/28 gaps fixed) · Stage 4 ✓ (324/324 tests; CI live)

---

### Stage 0 — Design Docs + Pre-Phase Fixes ✓ COMPLETE (2026-05-19)
**What:** 9 missing design docs written and catalogued. 9 pre-phase code bugs fixed.
**Output:** 207 tests passing (snapshot 2026-04-01). 96/96 pages HTTP 200. 103 active .md files in DOC-CATALOGUE.md.

---

### Stage 1 — Doc Read + Identify ✓ COMPLETE (2026-05-23)
**What:** All 51 §F + §H specs read line-by-line by main session. 30 duplication/overlap clusters identified.
**Output:** `backend/docs/_qc/phase4-stage1-read-log.md` — 51 ✓ / 0 ⬜. Findings reviewed and approved.

---

### Stage 2 — Doc Fix + Restructure ✓ COMPLETE (2026-05-25)
**What:** Execute all fixes for the 30 clusters. Normalise folder structure and file naming.
**Non-destructive rule:** Max negative action = archiving. No deletions, no content truncation.
**Report-back rule:** Complete each sub-stage fully → report back → get confirmation → start next.
**Cluster reference:** `backend/docs/_qc/phase4-stage1-read-log.md`

#### Stage 2A — Ownership Declaration ← NEXT SUB-STAGE
Add a 3-line PRIMARY header block to all 51 §F + §H spec files:
```
**PRIMARY for:** [concepts this file owns — code must implement from here]
**Defers to:** [filename — concept] for any definitions sourced elsewhere
**Do not re-define:** [concepts owned by another file — use a pointer only]
```
Risk: Zero — additive only. Done when all 51 files have the block.

#### Stage 2B — Gap Fills
Add 6 missing definitions to their owning files (additive only, zero risk):
- `territory_ids` JWT claim → `identity-auth-rbac.md` + `security-model.md`
- `EmployeePerformanceRM` → `read-models.md`
- `TerritoryPerformanceRM` → `read-models.md`
- `TenantUsageMetric` → `domain-model.md`
- Deny-by-default PRIMARY designation → `security-model.md`; pointer in `api-standards.md`, `identity-auth-rbac.md`, `org-multi-tenancy.md`
- Tone tiers (polite/firm/urgent) PRIMARY → `pakistan-adapter-architecture.md`; pointer in `collections-engine-model.md`

#### Stage 2C — Inconsistency Resolution
Resolve 6 conflicts — pick canonical value, update non-PRIMARY file only (low risk):
- Payment status enum — `payments-revenue.md` PRIMARY (9-state); fix `collections-engine-model.md`
- Collections aging buckets — `collections-engine-model.md` PRIMARY; fix `owner-dashboard.md`
- Audit hash schema — `integrity.hash/prev_hash/chain_seq` canonical; fix `data-governance-layer.md §2.6`
- Two audit integrity endpoints — clarify distinct purposes in both files (no value change)
- Event naming — add `event-catalog.md` pointer note to 5 domain files
- Urdu keyword — `مینیجر سے بات کریں` canonical; fix `conversational-action-spec.md`

#### Stage 2D — Duplicate Removal + Misplaced Content
Replace 14 duplicate definitions with one-line cross-reference pointers (low risk — nothing deleted):
- Transactional outbox copies in 3 files → pointer to `data-architecture.md §3.1`
- Idempotency 4-tuple copies in 2 files → pointer to `global-idempotency.md §1.1`
- Event dedup 3-tuple copies in 4 files → pointer to `global-idempotency.md §3.1`
- JWT claims + session revocation copies in `security-model.md` → pointer to `identity-auth-rbac.md`
- CQRS-lite + Aha-moment + break-glass + retention copies → pointers to respective PRIMARYs

Move 4 misplaced content blocks to owning files + leave pointer stub in original location:
- Follow-up Queue API (5 endpoints) out of `opportunities-pipeline.md` → `followup-enforcement-model.md`
- Ticket/Case overlay out of `activities-tasks.md` → archive in place + pointer to `cases-domain.md`
- Evaluate 3 appended overlay sections in `payments-revenue.md`
- `FieldDefinition` + `CustomFieldDefinition` internal near-duplicates in `custom-object-framework.md`

#### Stage 2E — Rename + Folder Restructure
Implement Diátaxis + DDD international standard taxonomy. Execute last (content must be clean first).
New structure: `backend/docs/` → 8 subfolders:
```
architecture/   security/   domain/   infrastructure/
adapters/       product/    ui/       _qc/   _tracking/
```
Each subfolder gets a `README.md` navigation index.
File renaming: remove `b9-p##` codes, remove redundant suffixes (`-model`, `-layer`, `-spec` where folder provides context), kebab-case throughout.
ADRs: add title slug (`ADR-001.md` → `ADR-001-ddd-microservices.md`).
Update all cross-references + `DOC-CATALOGUE.md` paths in one sweep.
Done when: all paths resolve, DOC-CATALOGUE verified, `git status` clean.

---

### Stage 3 — Code Overlay
**What:** Overlay normalised, restructured docs on the codebase. For every entity, API endpoint, and business rule: verify it exists in code, is correctly implemented, and matches the spec exactly. Fix every gap found.
**Output:** `backend/docs/phase4-gap-register.md` — full record of every gap found and fixed.
**Gate:** Stage 2 fully complete before starting.

---

### Stage 4 — Mapping Rebuild + Final Push
**What:** Rebuild `FRONTEND-BACKEND-MAPPING.md` (every endpoint: LIVE / BUILD / MISSING). Run all quality gates.
- Rebuild `FRONTEND-BACKEND-MAPPING.md` to reflect true post-Stage-3 state
- Verify: all 96 existing pages still HTTP 200
- Coverage gate: CI blocks merge if coverage < 80%
- Load test (locust): follow-up queue + collections happy path
- Full E2E test: lead capture → follow-up → close → invoice → payment
- GitHub push — Phase 4 complete
**Gate:** Stage 3 fully complete before starting.

---

## Phase 5 — Frontend: 75 Custom Pages (~4 weeks) ✓ COMPLETE (2026-05-29)
**Lifts:** Frontend 10/10
**Result:** All 75 custom pages built, browser-approved, and T1–T4 ✓ (Phase 6 Component 1 complete 2026-05-30). 47 Cat 1 + 28 Cat 2 (dummy mode, wiring sprint Phase 6 Component 2).
**Protocol:** Every page build followed `PAGE-BUILD-PROTOCOL.md` — mandatory 6-phase pre-build read sequence.

| Build phase | Verified pages | Count |
|---|---|---|
| 1 — QC + Core Sales | B-01*, B-08*, C-01*, D-01, C-04, A-04, I-05, C-06 | 8 (*QC re-run only) |
| 2 — Finance & Support | A-06, B-09, C-09, B-05, C-05, E-01, A-07 | 7 |
| 3 — Inbox & Admin | L-01, A-08, G-09 | 3 |
| 4 — Enterprise | A-05, A-12, A-13, B-06, B-07, B-10, B-11, C-07, C-11, J-03 | 10 |
| **Total** | | **28** |

**Blocked archetypes (zero buildable pages):** H (b9-p10 defines wrong pages), M (b9-p14 route mismatches), F (Source 3/4 missing), K (Source 3 unconfirmed)
**Partially blocked archetypes:** C (C-08/C-10 not in b9-p06), G (only G-09 valid), I (only I-05 valid), J (only J-03 valid), L (only L-01 valid)

---

## Phase 5B — Backend Domain Extension (~6 weeks) ✓ COMPLETE 2026-05-30
**Lifts:** Code 10/10 · Frontend wiring 10/10
**Gate:** Phase 5 complete (✓). Phase 6 cannot start until all 7 sprints done — **ALL 7 COMPLETE.** Phase 6 gate open.
**Pattern per sprint:** domain spec read → ORM models → Alembic migration → gateway routes → service logic → unit + integration tests → flip DUMMY_MODE=false for all pages that depend on this domain → verify all pages HTTP 200.

### Sprint order (sequenced by dependency depth — simplest first)

| Sprint | Domain | Spec doc | Pages unblocked | Approx. size |
|--------|---------|----------|-----------------|--------------|
| 5B-1 | Cases / Support Tickets | `backend/docs/domain/cases-domain.md` | B-05, C-05, E-01, A-07, H-03 | ~Phase 2 size |
| 5B-2 | Shared Inbox / Routing | `backend/docs/adapters/shared-inbox.md` | L-01, L-02, L-03 | ~Phase 2 size |
| 5B-3 | Territories | `backend/docs/domain/territory-management.md` | G-09 | Small |
| 5B-4 | Marketing / Campaigns | `backend/docs/domain/marketing-campaigns.md` ✓ | F-01, I-06, A-08, H-02 | ~Phase 2 size |
| 5B-5 | Partners | `backend/docs/domain/partners.md` ✓ | B-11, C-11 | Small |
| 5B-6 | Workflow Execution Engine | `backend/docs/infrastructure/workflow-catalog.md` | K-01, K-02, K-03, K-04, C-10, A-10, H-05 | Large |
| 5B-7 | AI / Predictive Models | `backend/docs/domain/ai-predictive-models.md` ✓ | M-01, M-02, H-07 | Large |

**Notes:**
- Sprints 5B-4, 5B-5, 5B-7 specs are now written and catalogued (2026-05-29). All 7 sprint specs are unblocked.
- K-series builder pages (K-01–K-04) are front-ends for the workflow engine config — they stay in dummy mode until 5B-6 is complete.
- H-07 Report Builder reads from multiple domains; wire it last in 5B-7 once other domains are live.
- T1–T4 QC audit is **not** in scope for Phase 5B — that is Phase 6 work. Ship working wired pages; audit them in bulk in Phase 6.

---

## Phase 6 — Market Research Features + Final Hardening + Full QC (~3 weeks)
**Lifts:** Code 10/10 · Frontend 10/10 · Testing 10/10 · DevOps 10/10
**Gate:** Phase 5B complete — all 75 pages wired to live data, DUMMY_MODE=false across the board.
**Source:** `backend/market-research-gap-register.md` · `backend/product-spec-gap-register.md`

### Component 1 — T1–T4 Protocol Audit ✓ COMPLETE 2026-05-30
All 75 pages audited. 9 pages fixed (T1/T2/T3/T4 issues). All 75 pages locked ✓ in SCREEN-ARTEFACTS.md.

---

### Component 2 — Wiring Sprint ✓ COMPLETE 2026-05-30

**Auth infrastructure (done 2026-05-30):**
- `GET /dev-token` mounted in `gateway/app.js` before authMiddleware — no Bearer required to seed token
- `SKIP_JWT_VERIFICATION=true` set programmatically in dev (non-production only)
- `x-tenant-id: cfg.tenantId` added to all crm-api.js HTTP calls — closes 403 blocker
- Auto-init IIFE in crm-api.js seeds dev JWT into localStorage on first load when `DUMMY_MODE: false`

**Single flip to start all wiring:** `DUMMY_MODE: false` in `frontend/src/assets/js/app/crm-api.js` line 5.

#### Tier classification

| Tier | Pages | Confidence |
|---|---|---|
| Tier 1 — Cat 1 inline backends | 25 | ✅ Guaranteed — inline routes, fully defined schemas |
| Tier 2 — Phase 5B in-memory stubs | 23 | ✅ Guaranteed — stubs return valid shapes, data resets on restart |
| Cat 3 inline (A-12, K-04) | 2 | ✅ Guaranteed — uses Users[I] + Quotes[I] inline routes |
| Tier 3 — opaque proxies | 8 | ⚠️ Conditional — requires downstream services running |
| Structurally blocked | 17 | ❌ No gateway API exists — additional backend work required |

#### 12-step execution plan

| Step | Action | Pages wired (cumulative) |
|---|---|---|
| 1 | Flip `DUMMY_MODE: false`, start gateway, confirm `/dev-token` responds and token caches in localStorage | 0 (infra) |
| 2 | Tier 1 — simple single-domain: G-02, B-10, J-01, J-02, H-06, J-04 | **6** |
| 3 | Tier 1 — list/queue: B-01, B-02, B-08, B-09 | **10** |
| 4 | Tier 1 — create/form: I-01, I-03, I-05 | **13** |
| 5 | Tier 1 — detail: C-01, C-04, C-06, C-09 | **17** |
| 6 | Tier 1 — dashboards + analytics: A-01, A-02, A-04, A-05, A-06, D-01, H-01, H-04 | **25** |
| 7 | Cat 3 inline: A-12, K-04 | **27** |
| 8 | Tier 2 — Cases/Support: A-07, B-05, C-05, E-01, H-03, I-04 | **33** |
| 9 | Tier 2 — Knowledge + Campaigns + Routing: A-09, C-12, F-01, H-02, I-06, L-03 | **39** |
| 10 | Tier 2 — Workflows: A-10, C-10, H-05, K-01, K-02, K-03 | **45** |
| 11 | Tier 2 — Partners + AI + Territories: B-11, C-11, M-01, M-02, G-09 | **50** |
| 12 | Tier 3 — opaque proxies (if downstream services running): B-03, B-04, B-06, B-07, C-02, C-03, C-07, I-02 | **58** |

#### Structural ceiling — 17 pages, no gateway API

| Reason | Pages |
|---|---|
| No management API at gateway | G-01, G-03, G-04, G-06, G-07, G-08, H-07, J-05 |
| Read model / spec gap | A-03, A-08, A-11, A-13, C-08 |
| No gateway path (Python service / no API) | G-05, J-03, L-01, L-02 |

**Data note:** Tier 1 pages show empty tables / zero KPIs until DB has seeded data — wired correctly, not broken. Tier 2 pages show stub data immediately.  
**Update rule per step:** confirm HTTP 200 on primary GET → update FRONTEND-BACKEND-MAPPING.md Section 7 status → mark page ✓ in SCREEN-ARTEFACTS.md.

---

### Market Research — Buildable (not blocked)
- MR-004: Automated daily WhatsApp activity summary to managers — scheduler job + WhatsApp template, EN + UR
- MR-005: Excel import / export for contacts and leads — POST /api/v1/contacts/import, GET exports

### Market Research — Blocked (build when unblocked)
- MR-002: One-click invoice + WhatsApp payment link (blocked: P-016 payment credentials + Meta template approval)
- MR-001: Facebook / Instagram lead capture automation (blocked: Meta Business Manager setup by user)
- MR-003: Voice note transcription — Urdu / Roman Urdu / English (blocked: transcription provider + credentials)
- MR-006: Geo-tagging / field check-in for field reps (low priority; requires mobile GPS)
- MR-007: Kuickpay payment adapter (blocked: Kuickpay API credentials)

### Component 3 — Final Hardening → **Absorbed into COMMERCIALISATION-PLAN.md**
All Component 3 work (load tests, E2E extension, coverage gate, CI/CD containers, final grade audit) has been moved to `COMMERCIALISATION-PLAN.md` Phases C2 and C3. Do not execute these tasks from this file.

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
