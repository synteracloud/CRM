# Pakistan CRM OS — Rebuild Plan (10/10 Roadmap)

**Created:** 2026-05-18
**Revised:** 2026-05-25 — Stage 2 (Doc Fix + Restructure) plan finalised; Session Resumption Protocol added; stage numbering updated (2=fix, 3=code overlay, 4=mapping); Phase 4 expanded to 41 tasks.
**Status:** Phase 1 ✓ | Phase 2 ✓ | Phase 3 ✓ | Phase 4 IN PROGRESS (Stage 0 ✓ · Stage 1 ✓ · Stage 2A NEXT) | Phase 5 NOT STARTED | Phase 6 NOT STARTED
**Anchor:** This file. Updated every session before closing. Read first every session.
**Task tracker:** `PENDING.md` (root) — checkbox list, mark `[x]` immediately on completion
**Session log:** `PROGRESS.md` — one-line summary added every session
**Estimated total duration:** ~21 weeks

---

## RESUME POINT — Read Before Every Session

**Current location:** Phase 4 · Stage 2A  
**Next task:** Add PRIMARY / DEFERS-TO / DO NOT RE-DEFINE header block to all 51 §F + §H spec files  
**First file to open:** `backend/docs/phase4-stage1-read-log.md` — 30 clusters with PRIMARY designations  
**Rule in force:** Non-destructive only. Max negative action = archiving. No deletions.  
**Report-back rule:** Finish one sub-stage completely → report back → wait for confirmation → start next.

| Phase | Stage | Status |
|---|---|---|
| 1 — Foundation Seal | — | ✓ COMPLETE |
| 2 — Follow-up Engine | — | ✓ COMPLETE |
| 3 — 5 Engines | — | ✓ COMPLETE |
| 4 — Backend Hardening | Stage 0 — Design Docs + Fixes | ✓ COMPLETE (2026-05-19) |
| 4 — Backend Hardening | Stage 1 — Doc Read + Identify | ✓ COMPLETE (2026-05-23) |
| **4 — Backend Hardening** | **Stage 2A — Ownership Declaration** | **← NEXT** |
| 4 — Backend Hardening | Stage 2B–2E — Fix + Restructure | Pending Stage 2A |
| 4 — Backend Hardening | Stage 3 — Code Overlay | Pending Stage 2 |
| 4 — Backend Hardening | Stage 4 — Mapping + Push | Pending Stage 3 |
| 5 — Frontend 75 pages | — | Pending Phase 4 complete |
| 6 — Market Research | — | Pending Phase 5 complete |

---

## Session Resumption Protocol

Every session — including fresh sessions with no prior memory — MUST follow this sequence before doing any work.

### Step 1 — Orient (read in order, do not skip)
1. `REBUILD-PLAN.md` — read RESUME POINT table above; current phase and stage are stated explicitly
2. `PENDING.md` — find the first unchecked `[ ]` task in the current phase; that is the start point
3. `DOC-CATALOGUE.md` §A How-to-use table — confirm file locations for current stage context

### Step 2 — Load stage context
| Stage | Files to read before starting |
|---|---|
| Phase 4 Stage 2 (any sub-stage) | `backend/docs/phase4-stage1-read-log.md` — 30 clusters + PRIMARY designations |
| Phase 4 Stage 3 — Code Overlay | `backend/docs/phase4-gap-register.md` (created during Stage 3) |
| Phase 4 Stage 4 — Mapping | `backend/FRONTEND-BACKEND-MAPPING.md` |
| Phase 5 — any page build | `DESIGN-SPEC.md` + `FRAMEWORK.md §25–32` + relevant `backend/docs/ui/pages/` spec |
| Phase 6 | `backend/market-research-gap-register.md` |

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

## Phase 4 — Backend Hardening (~6 weeks) — IN PROGRESS
**Goal:** Bullet-proof all docs, normalise structure, overlay docs on code, fix every gap. Gates Phase 5.
**Progress:** 12/41 tasks done (29%) — Stage 0 ✓ · Stage 1 ✓ · Stage 2 next

---

### Stage 0 — Design Docs + Pre-Phase Fixes ✓ COMPLETE (2026-05-19)
**What:** 9 missing design docs written and catalogued. 9 pre-phase code bugs fixed.
**Output:** 308 tests passing. 96/96 pages HTTP 200. 103 active .md files in DOC-CATALOGUE.md.

---

### Stage 1 — Doc Read + Identify ✓ COMPLETE (2026-05-23)
**What:** All 51 §F + §H specs read line-by-line by main session. 30 duplication/overlap clusters identified.
**Output:** `backend/docs/phase4-stage1-read-log.md` — 51 ✓ / 0 ⬜. Findings reviewed and approved.

---

### Stage 2 — Doc Fix + Restructure ← CURRENT STAGE
**What:** Execute all fixes for the 30 clusters. Normalise folder structure and file naming.
**Non-destructive rule:** Max negative action = archiving. No deletions, no content truncation.
**Report-back rule:** Complete each sub-stage fully → report back → get confirmation → start next.
**Cluster reference:** `backend/docs/phase4-stage1-read-log.md`

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
