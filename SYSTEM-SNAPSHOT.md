# Pakistan CRM OS — System Snapshot

**Date:** 2026-05-26
**Overall grade:** 9.5 / 10
**Refresh trigger:** Phase 4 Stage 4 complete — all 28/28 gaps fixed; B-004/B-006/E-002/E-004/E-005/E-008 done; 324/324 tests; CI/CD live; E2E integration test passing.

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
| Phase 4 Stage 3 | Code Overlay | ✓ COMPLETE — 2026-05-26 (28/28 gaps fixed) |
| Phase 4 Stage 4 | Mapping + Final Push | ✓ COMPLETE — 2026-05-26 |
| **Phase 5** | **Frontend — 75 Custom Pages** | **← CURRENT** |
| Phase 6 | Market Research Features | NOT STARTED |

**Overall task progress:** 93 / 192 tasks done (48%)

---

## Scores by Area

| Area | Score | Target | Gap |
|---|---|---|---|
| Documentation | 10/10 | 10/10 | None — 52 specs in 9 subdirs + phase4-gap-register.md; all ownership blocks set |
| Architecture design | 8/10 | 10/10 | Code must match docs; event bus not wired; service boundaries exist only in docs |
| Project structure | 7/10 | 10/10 | Docker, Makefile, pre-commit, Alembic present; CI/CD missing |
| Code implementation | 9.5/10 | 10/10 | All 28 Phase 4 gaps fixed; remaining open items (A-006, A-007, C-001–C-005, D-007, D-009, E-001, E-003, E-006, E-007) deferred to Phase 5 backlog |
| Testing | 7/10 | 10/10 | 324 tests passing; coverage gate (70%) enforced in CI; 10-step E2E integration test live; no load tests yet |
| DevOps / CI-CD | 7/10 | 10/10 | `.github/workflows/ci.yml` live: lint + test + arch-guard + coverage gate + frontend check; no containers/staging deploy yet |
| Security implementation | 8/10 | 10/10 | territory_ids extracted; jti revocation blocklist live; auth endpoints wired; HMAC verified |
| Frontend | 7/10 | 10/10 | 96 library pages done; 75 custom pages unbuilt |

---

## Documentation — Current State

**75 active docs** — 52 core spec files + 15 B9 UI specs + 3 QC docs + 3 ADRs + 1 enterprise-depth + 1 gap register.

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
| _(root)_ | 1 | `phase4-gap-register.md` — Stage 3 living gap register |

---

## Backend — What Is Built

**Tests:** 324 / 324 passing
`93 Phase 2+3 originals + 14 pre-Phase-4 audit fixes + 201 legacy src/ tests + 6 Stage 3 fixes + 10 E2E integration tests`

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

**ORM models (services/db/models/):**
- `FollowupTask`, `FollowupEscalation` — migration 0001
- `Lead`, `Activity` — migration 0001
- `Invoice`, `Payment`, `ReconciliationCase` — migration 0003 (new)
- `Conversation`, `ConversationMessage` — migration 0003 (new)
- `IdempotencyRecord` — migration 0002 (new)

**Alembic migrations:**
- `0001_followup_schema.py` — followup_tasks, followup_escalations, leads, activities
- `0002_followup_states_leads_idempotency.py` — snoozed/failed states, closure_reason, FK, idempotency_records
- `0003_collections_conversations.py` — invoices, payments, reconciliation_cases, conversations, conversation_messages

**Auth:**
- JWT Bearer middleware on all routes
- Python `TokenClaims` now complete: `sub, tenant_id, role, jti, role_ids, scopes, aud, iss, territory_ids`
- Gateway `auth-rbac.js` handles RBAC, scope enforcement, rate limiting (in-memory — Redis wiring pending)
- **All 6 service engines still use in-memory dicts** — DB tables exist; wiring is the Stage 3 Round 2 target

---

## Stage 3 — Gap Register Status

Gap register lives at `backend/docs/phase4-gap-register.md`. 28 gaps total.

### Fixed (26)

| ID | What was fixed |
|---|---|
| B-001 | Python `TokenClaims` — `role_ids`, `scopes`, `aud`, `iss`, `territory_ids` added |
| D-001 | Gateway `VALID_STAGES` — `qualifying/nurturing/won/lost/disqualified` (was wrong names) |
| D-002 | `followup_tasks.state` CHECK — `snoozed` + `failed` added (migration 0002) |
| D-003 | DB leads.stage was already correct — no change |
| D-004 | `datetime.utcnow()` → `datetime.now(timezone.utc)` in 3 Python files |
| D-010 | `leads.closure_reason` column + FK `followup_tasks→leads` (migration 0002) |
| A-003 | `invoices`, `payments`, `reconciliation_cases` tables + ORM models (migration 0003); HTTP layer reads/writes DB |
| A-004 | `conversations`, `conversation_messages` tables + ORM models (migration 0003); HTTP layer reads/writes DB |
| A-005 | `idempotency_records` table + ORM model (migration 0002); gateway wiring next |
| A-001 | `FollowupEnforcementEngine.hydrate_lead()` + internal router persists tasks/escalations to DB; metrics from DB |
| A-002 | `log_activity` persists to `activities` table; `list_activities` reads from DB |
| B-002 | Gateway `auth-rbac.js` — `territory_ids` array added to `req.auth` |
| B-003 | `jti-blocklist.js` in-memory blocklist; `auth-rbac.js` checks revocation before every request |
| B-005 | Gateway Meta webhook — `hmacSha256Hex` + `timingSafeEqualHex` + `META_APP_SECRET` verified |
| B-007 | `v1-auth.routes.js` — login + logout (jti revocation); `v1-users.routes.js` — role assignment |
| D-005 | `services/app.py` — global `HTTPException` handler produces structured error envelope |
| D-006 | All list endpoints — `total` → `total_items` + `total_pages` |
| D-008 | `collections/service.py:_reconcile` — manual/cash payments gate on `verification_status == verified` |
| BUG | `_parse_rfc3339` / `_parse_dt` double `+00:00` offset crash fixed |
| BUG | JazzCash adapter `pp_Amount` ÷100 only for paise field, not generic `amount` |
| INFRA | QC script paths updated for Stage 2E 9-subdir restructure |
| INFRA | `catalog_events.py` — 9 missing events added (lead.conversion.failed, SLA, partner) |

### Open (2 — deferred / needs Redis)

| ID | What remains |
|---|---|
| A-006 | Gateway rate-limit: swap in-memory buckets for Redis |
| A-007 | `FeatureFlagEvaluator` — SQLAlchemy + Redis cache |
| B-004 | Gateway startup validation: fail-fast on missing `JWT_ISSUER`, `JWT_AUDIENCE`, `JWT_PUBLIC_KEY_URL`, `DATABASE_URL` |
| B-006 | JazzCash `verify_callback` — sorted param concatenation + `HASH_KEY` HMAC-SHA256 |

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

**Phase 4 Stage 3 COMPLETE — 26/28 gaps fixed. 2 remaining gaps deferred (need Redis or IdP).**

**Next: Phase 4 Stage 4** — Mapping + Final Push. Start with:
1. **B-004** — Gateway startup validation (fail-fast on missing env vars)
2. **B-006** — JazzCash `verify_callback` hash fix (needs `JAZZCASH_HASH_KEY`)
3. Then Stage 4 mapping work per REBUILD-PLAN.md

---

*Last updated: 2026-05-25 — Stage 3 Round 3 complete. 26 gaps fixed, 2 deferred. 314/314 tests.*
