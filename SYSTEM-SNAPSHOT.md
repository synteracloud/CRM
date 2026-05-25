# Pakistan CRM OS — System Snapshot

**Date:** 2026-05-25
**Overall grade:** 8.5 / 10
**Refresh trigger:** Phase 4 Stage 2 complete — doc tree restructured, all gaps and inconsistencies resolved.

> **How to use this file:** Read it first at the start of every session. 60-second bird's-eye view — where we are, what is built, what is broken, what is next. Then open `REBUILD-PLAN.md` for the exact resume point and `PENDING.md` for the checkbox queue.

---

## Phase Completion

| Phase | Name | State |
|---|---|---|
| Phase 1 | Foundation Seal | ✓ COMPLETE |
| Phase 2 | Follow-up Engine | ✓ COMPLETE |
| Phase 3 | 5 Remaining Engines | ✓ COMPLETE |
| Phase 4 Stage 0 | Design Docs + Pre-Phase Fixes | ✓ COMPLETE — 2026-05-19 |
| Phase 4 Stage 1 | Doc Read + Identify (30 clusters) | ✓ COMPLETE — 2026-05-23 |
| Phase 4 Stage 2 | Doc Fix + Restructure | ✓ COMPLETE — 2026-05-25 |
| **Phase 4 Stage 3** | **Code Overlay** | **← CURRENT** |
| Phase 4 Stage 4 | Mapping + Final Push | Pending Stage 3 |
| Phase 5 | Frontend — 75 Custom Pages | NOT STARTED |
| Phase 6 | Market Research Features | NOT STARTED |

**Overall task progress:** 72 / 192 tasks done (38%)

---

## Scores by Area

| Area | Score | Target | Gap |
|---|---|---|---|
| Documentation | 10/10 | 10/10 | None — 52 specs in 9 subdirs, all ownership blocks set, all inconsistencies resolved |
| Architecture design | 8/10 | 10/10 | Code must match docs; event bus not wired; service boundaries exist only in docs |
| Project structure | 7/10 | 10/10 | Docker, Makefile, pre-commit, Alembic present; CI/CD missing |
| Code implementation | 7/10 | 10/10 | 44 audit gaps outstanding; 8 critical (no DB persistence, no RBAC, broken JWT) |
| Testing | 5/10 | 10/10 | 308 tests passing; no coverage gate; no E2E; no load tests |
| DevOps / CI-CD | 2/10 | 10/10 | No working pipeline; no containers in CI |
| Security implementation | 5/10 | 10/10 | No RBAC middleware; JWT claims incomplete; no rate limiting |
| Frontend | 7/10 | 10/10 | 96 library pages done; 75 custom pages unbuilt |

---

## Documentation — Current State

**74 active docs** — 52 core spec files + 15 B9 UI specs + 3 QC docs + 3 ADRs + 1 enterprise-depth.

### Doc Tree (`backend/docs/`)

| Folder | Files | What lives here |
|---|---|---|
| `architecture/` | 5 | domain-model, architecture-overview, service-map, capability-matrix, data-architecture |
| `security/` | 3 | identity-auth-rbac, org-multi-tenancy, security-model |
| `domain/` | 18 | All business domain specs (followup, activities, payments, cases, collections, opportunities, etc.) |
| `infrastructure/` | 15 | api-standards, event-catalog, execution-hardening, observability-audit, scheduler-jobs, workflow-catalog, etc. |
| `adapters/` | 5 | pakistan-adapter-architecture, whatsapp-execution-model, integration-flow-traces, compliance-adapter, conversational-action-spec |
| `product/` | 4 | activation-model, adoption-ux, localization, pricing-plans |
| `ui/` | 3 | ui-foundations, ui-system, read-models |
| `_b9/` | 15 | B9 phase UI specs (b9-p01 through b9-p14) |
| `_qc/` | 3 | phase4-stage1-read-log, qc-integration, qc-intelligence-data |
| `adr/` | 3 | ADR-001 (DDD), ADR-002 (Adapter pattern), ADR-003 (WhatsApp-first) |

### Stage 2 — What Was Fixed (2026-05-25)

Every spec file now has a `<!-- OWNERSHIP -->` block declaring PRIMARY FOR / DEFERS TO / DO NOT RE-DEFINE. Key fixes:

- `territory_ids` JWT claim added to `security/identity-auth-rbac.md §3.2`
- `EmployeePerformanceRM` + `TerritoryPerformanceRM` + `TenantUsageMetric` added to architecture docs
- 3 missing events added: `lead.conversion.failed.v1`, `case.sla.first_response_breached.v1`, `case.sla.resolution_breached.v1`
- Audit hash schema canonical: `integrity.hash/prev_hash/chain_seq` (deprecated `before_hash/after_hash`)
- SLA event names — `.v1` suffix enforced in `domain/cases-domain.md`
- Urdu escalation keyword canonical: `مینیجر سے بات کریں` in `adapters/conversational-action-spec.md`
- WhatsApp opt-out handling: `STOP / بند کرو` wired to ComplianceAdapter in `adapters/whatsapp-execution-model.md §7.4`
- Duplicate sections removed from 6 files; pointer stubs left in place

---

## Backend — What Is Built

**Tests:** 308 / 308 passing
`93 Phase 2+3 originals + 14 pre-Phase-4 audit fixes + 201 legacy src/ tests`

### 6 Engines

| Engine | Key capabilities | Public endpoints |
|---|---|---|
| **WhatsApp Engine** | Inbound webhook (async 200 return), intent classification (payment_query → follow_up_response → lead_inquiry → support_request), conversation threading keyed by tenant_id+phone, auto lead creation, anti-lead-loss guarantee | `POST /api/v1/webhooks/whatsapp` · `GET /api/v1/conversations` · `GET /api/v1/conversations/{id}` |
| **Follow-up Engine** | Enforcement ladder T+0/+2h/+24h/+48h, overdue scanner (60s background job), escalation ladder, OCC version_no, RBAC-gated escalate (manager/admin only) | `GET/POST /api/v1/followups` · `PATCH /followups/{id}/complete` · `POST /followups/{id}/escalate` · `GET /followups/{id}` |
| **Collections Engine** | Invoice lifecycle (unpaid→partial→paid→overdue), JazzCash/Easypaisa payment callbacks, confidence scoring (≥85 auto-match / 40–84 manual / <40 unmatched), WhatsApp reminder cadence (T-3/T-1/T+1/T+7/T+15), customer opt-out (STOP / لاگ آف), manual payment proof (submit/verify/reject) | `POST/GET /api/v1/invoices` · `GET /invoices/{id}` · `POST /invoices/{id}/send` · `POST /payments/callback/{provider}` |
| **Activity Control Engine** | Immutable append-only hash-chain audit log, dual event emission, chain-integrity verification | `POST/GET /api/v1/activities` · `GET /api/v1/activities/chain-integrity` |
| **Activation Engine** | <10-minute onboarding, seed pipeline + 5 contacts + 4 deals, WhatsApp sandbox simulation, sandbox→production transition, Aha moment trigger | `POST /api/v1/activation/start` · `/whatsapp-sim` · `/move-deal` · `GET /api/v1/activation/status` |
| **Execution Control Plane** | Global idempotency ledger, exponential retry (1s base / 2× / 60s max / 8 attempts), DLQ with operator API | `GET /api/v1/admin/dead-letters` · `POST /{id}/retry` · `POST /{id}/requeue` |

### DB / Auth State

- SQLAlchemy ORM models: `FollowupTask`, `FollowupEscalation`, `Lead`, `Activity`
- Alembic migration: `0001_followup_schema.py`
- JWT Bearer middleware on all routes
- **All other engines: in-memory dicts** — Stage 3 target: replace with DB-backed repositories

---

## Stage 3 — Code Overlay Targets

These are the 44 audit gaps to fix in Stage 3. Grouped by area.

### A — Persistence (blocks everything)

All 6 engines use in-memory state. Every restart wipes all data.

| Component | Fix |
|---|---|
| FollowupEnforcementEngine | SQLAlchemy (tables exist in 0001 migration) |
| ActivityControlEngine | SQLAlchemy |
| CollectionsService | SQLAlchemy |
| ConversationService | SQLAlchemy + persistent message store |
| GlobalIdempotencyLedger | PostgreSQL `idempotency_records` table |
| FeatureFlagEvaluator | SQLAlchemy + Redis cache |

### B — Security & Auth

- JWT claims incomplete: missing `role_ids` (array), `scopes`, `aud`, `iss`, `territory_ids`; no `jti` revocation check via Redis blocklist
- No RBAC middleware: per-route permission annotation + active/suspended check missing
- No rate limiting: spec requires 10k/min per-tenant, 500/min per-principal
- WhatsApp webhook: uses API key; must be Meta X-Hub-Signature-256 HMAC
- JazzCash `verify_callback` broken: wrong hash method (must be sorted params + HASH_KEY)
- Auth endpoints missing: `POST /api/v1/auth/sessions`, `DELETE` session, `POST /users/{id}/roles`
- Startup validation missing: no fail-fast on missing JWT_ISSUER/AUDIENCE/PUBLIC_KEY_URL

### C — Missing Domain APIs

| API | Endpoints |
|---|---|
| Tasks | `GET/POST /api/v1/tasks` · `POST /tasks/{id}/reschedule` |
| Cases | 5 endpoints: GET/POST/PATCH + escalate + SLA |
| Opportunities | `GET/POST /api/v1/opportunities` + stage transitions + mark-won/lost |
| Forecasts | `GET /api/v1/forecasts` |
| Audit query | `GET /api/v1/audits/events` + exports + integrity verify |

### D — API Standards & State Machines

- Error envelope: all HTTPException → `{"error":{"code":"..."},"meta":{"request_id":"..."}}` everywhere
- Pagination: add `total_pages`; rename `total` → `total_items`
- Unknown fields: `ConfigDict extra=forbid` on all request models
- FollowUp states: add SNOOZED + FAILED (currently: pending/overdue/completed only)
- Conversation states: add WAITING_ON_CONTACT / RESOLVED / CLOSED / REOPENED
- Lead stage enum: add NURTURING / PROPOSAL / DISQUALIFIED; rename QUALIFIED → QUALIFYING
- Opt-out: STOP + `لاگ آف` wired into WhatsApp intent classifier
- Manual payment: reconciliation must be gated behind `verification_status == verified`
- `Idempotency-Key` header enforcement on all critical write endpoints
- Schema: add `closure_reason` to leads migration; add FK followup_tasks → leads

### E — Observability, CI/CD & Testing

- Structured logging: 16 required fields (trace_id, tenant_id, request_id per request)
- W3C traceparent distributed trace headers
- Daily Merkle root checkpoint + hourly integrity job + Sev-1 alerting
- GitHub Actions: lint + test + build + staging deploy
- Bandit + npm audit in CI
- Static import denylist: ruff rule blocking `core` → `adapters/pakistan`
- Replace ConcurrencyController stub with real Redis distributed lock
- Lead conversion saga: `Account → Contact → Opportunity` + compensation
- `datetime.utcnow()` → `datetime.now(timezone.utc)` everywhere; off-hours check → PKT (UTC+5)
- Coverage gate: CI blocks merge if < 80%
- Load test (locust): follow-up queue + collections happy path
- Full E2E: lead capture → follow-up → close → invoice → payment

---

## Frontend

### Library Phase — Complete

- **96 / 96** NexLink pages built and verified HTTP 200
- `crm-shell.js`, `crm-api.js` (DUMMY_MODE=true), `crm-dummy.js`, `crm-components.js`, `crm-locale.js` in place
- AI section pages (`src/ai/*.html`) self-contained — own aside + header, no crm-shell.js

### Custom Design Phase — Not Started (gates on Phase 4 complete)

**75 pages unbuilt.** 13 archetypes (A–M), 8 build phases. All pages → `frontend/src/app/`

Build Phase 1 queue (start here, in order):

| ID | Page | Archetype |
|---|---|---|
| B-01 | Follow-up Queue | B — List/Queue |
| B-02 | Lead Queue | B — List/Queue |
| C-01 | Lead Detail | C — Entity Detail |
| A-01 | Owner Dashboard | A — Dashboard |
| B-08 | Collections Queue | B — List/Queue |
| B-03 | Contact List | B — List/Queue |
| I-01 | New Lead Form | I — Form/Wizard |

Phase-5 doc blockers all cleared: `cases-domain.md` ✓ · `localization.md` ✓ · `territory-management.md` ✓

Dev server: `npm run serve` from `D:\CRM\frontend` → `http://localhost:3001`

---

## Permanently Blocked Items

| ID | Item | Blocked by | Runtime behaviour |
|---|---|---|---|
| P-016 | JazzCash/Easypaisa production callbacks | Real credentials + sandbox verification | `JAZZCASH_STUB_MODE=true` — stub badge shown |
| P-017 | All Urdu customer-facing strings | Native Urdu speaker sign-off | English placeholder + `<!-- UR_TODO: -->` |
| MR-001 | Facebook/Instagram lead capture | Meta Business Manager setup | Hidden div `data-unblock="MR-001"` |
| MR-003 | Voice note transcription | Transcription provider + credentials | Microphone icon `disabled` |
| MR-007 | Kuickpay adapter | Kuickpay API credentials | Not rendered |

**Rule:** Never set `stub_mode=False` without sandbox verification + full payment → webhook → reconciliation cycle end-to-end.
**Rule:** All `_STRINGS['ur']` values need native Urdu speaker sign-off before any customer send.

---

## Non-Negotiables (always in force)

| Rule | Source |
|---|---|
| RTL wired at build time — never retrofitted | CONSTRAINTS.md C-001 |
| All API calls via `crm-api.js` with DUMMY_MODE flag | CONSTRAINTS.md C-007 |
| `JAZZCASH_STUB_MODE=true` until P-016 resolved | CONSTRAINTS.md C-009 |
| No country-specific logic in `core/` | `architecture/architecture-overview.md` |
| `core/*` must never import `adapters/pakistan/*` | `architecture/architecture-overview.md` |
| All 96 library pages must stay HTTP 200 after every push | REBUILD-PLAN.md |
| Every new doc added to DOC-CATALOGUE.md same day it is written | REBUILD-PLAN.md |
| Never commit `.env` — use `.env.example` | .gitignore |

---

## Immediate Next Step

**Phase 4 Stage 3 — Code Overlay.**

Open `backend/docs/_qc/phase4-stage1-read-log.md` — 30 duplication/overlap clusters, each with a PRIMARY file designation. For each cluster, read the PRIMARY file and compare it against the running code. Record every gap found in `backend/docs/phase4-gap-register.md`. Fix gaps as you go.

**Highest-leverage first:** Start with Cluster A (persistence) — replacing in-memory dicts with SQLAlchemy repositories is the single most critical fix. Nothing else is durable without it.

---

*Last updated: 2026-05-25 — refreshed after Phase 4 Stage 2 complete.*
