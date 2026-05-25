# Pakistan CRM OS — System Snapshot

**Date:** 2026-05-19  
**Overall grade:** 8.5 / 10  
**Prepared from:** Full line-by-line audit of all §A, §B, §C, §D, §G files in DOC-CATALOGUE.md  

---

## Phase Completion

| Phase | Name | State |
|---|---|---|
| Phase 1 | Foundation Seal | ✓ COMPLETE |
| Phase 2 | Follow-up Engine | ✓ COMPLETE |
| Phase 3 | 5 Remaining Engines | ✓ COMPLETE |
| Phase 4 Sprint 0 | Missing Design Docs (10 PS gaps) | ✓ COMPLETE — 2026-05-19 |
| Phase 4 Sprints 1–5 | Backend Hardening | NOT STARTED |
| Phase 5 | Frontend — 75 Custom Pages | NOT STARTED |
| Phase 6 | Market Research Features | NOT STARTED |

---

## Scores by Area

| Area | Current | Target | Gap |
|---|---|---|---|
| Documentation | 10/10 | 10/10 | None — Sprint 0 complete, 99 active docs |
| Architecture design | 8/10 | 10/10 | Code must match docs; event bus; service boundaries in code |
| Project structure | 7/10 | 10/10 | Docker, Makefile, pre-commit, Alembic present; CI/CD missing |
| Code implementation | 7/10 | 10/10 | 44 audit gaps; 8 critical (no DB persistence, no RBAC, broken JWT) |
| Testing | 5/10 | 10/10 | 308 tests passing; no coverage gate; no E2E; no load tests |
| DevOps / CI-CD | 2/10 | 10/10 | No working pipeline; no containers in CI |
| Security implementation | 5/10 | 10/10 | No RBAC middleware; JWT claims wrong; no rate limiting |
| Frontend | 7/10 | 10/10 | 96 library pages done; 75 custom pages unbuilt |

---

## Backend — What Is Built

**Tests:** 308/308 passing  
`93 Phase 2+3 originals + 14 pre-Phase-4 audit fixes + 201 legacy src/ tests (visible after P3-A fix)`

### 6 Engines

| Engine | Key capabilities | Public endpoints |
|---|---|---|
| WhatsApp Engine | Inbound webhook (async 200 return), intent classification (payment_query > follow_up_response > lead_inquiry > support_request), conversation threading keyed by tenant_id+phone, auto lead creation, anti-lead-loss guarantee | `POST /api/v1/webhooks/whatsapp` · `GET /api/v1/conversations` · `GET /api/v1/conversations/{id}` |
| Follow-up Engine | Enforcement ladder T+0/+2h/+24h/+48h, overdue scanner (60s background job), escalation ladder, OCC version_no, RBAC-gated escalate (manager/admin only) | `GET/POST /api/v1/followups` · `PATCH /followups/{id}/complete` · `POST /followups/{id}/escalate` · `GET /followups/{id}` |
| Collections Engine | Invoice lifecycle (unpaid→partial→paid→overdue), JazzCash/Easypaisa payment callbacks, confidence scoring (≥85 auto-match / 40–84 manual review / <40 unmatched), WhatsApp reminder cadence (T-3/T-1/T+1/T+7/T+15), customer opt-out (STOP / لاگ آف), §N manual payment proof (submit/verify/reject) | `POST/GET /api/v1/invoices` · `GET /invoices/{id}` · `POST /invoices/{id}/send` · `POST /payments/callback/{provider}` |
| Activity Control Engine | Immutable append-only hash-chain audit log, dual event emission (activity + audit on every write), chain-integrity verification endpoint | `POST/GET /api/v1/activities` · `GET /api/v1/activities/chain-integrity` |
| Activation Engine | <10-minute onboarding path, seed pipeline + 5 contacts + 4 deals, WhatsApp sandbox simulation, sandbox→production transition (15-min dual-active window), Aha moment trigger | `POST /api/v1/activation/start` · `/whatsapp-sim` · `/move-deal` · `GET /api/v1/activation/status` |
| Execution Control Plane | Global idempotency ledger, exponential retry (1s base, 2× multiplier, ±20% jitter, 60s max, 8 attempts), DLQ with operator API (retry/requeue/cancel) | `GET /api/v1/admin/dead-letters` · `POST /{id}/retry` · `POST /{id}/requeue` |

### DB / Auth

- SQLAlchemy ORM models: `FollowupTask`, `FollowupEscalation`, `Lead`, `Activity`
- Alembic migration: `0001_followup_schema.py` (first real schema)
- JWT Bearer middleware on all routes via `get_current_user` FastAPI dependency
- **All other engines: in-memory dicts only** (Sprint 1 target — see Critical Gaps below)

---

## Backend — Critical Gaps (Phase 4 Sprints 1–5)

### Sprint 1 — Persistence (blocks everything else)

All 6 engines use in-memory state. Every restart wipes all data. Replace with DB-backed repositories:

| Component | Fix required |
|---|---|
| FollowupEnforcementEngine | SQLAlchemy (tables exist in 0001 migration) |
| ActivityControlEngine | SQLAlchemy |
| CollectionsService | SQLAlchemy |
| ConversationService | SQLAlchemy + persistent message store |
| GlobalIdempotencyLedger | PostgreSQL `idempotency_records` table |
| FeatureFlagEvaluator | SQLAlchemy + Redis cache |

### Sprint 2 — Security & Auth

- JWT claims incomplete: missing `role_ids` (array), `scopes`, `aud`, `iss`; no jti revocation check via Redis blocklist
- No RBAC middleware: per-route permission annotation + user active/suspended check missing
- No rate limiting: spec requires 10k/min per-tenant, 500/min per-principal
- WhatsApp webhook: uses API key auth; must be replaced with Meta X-Hub-Signature-256 HMAC
- JazzCash `base.py` `verify_callback` broken: uses wrong hash method (must be sorted params + HASH_KEY)
- Auth endpoints missing: `POST /api/v1/auth/sessions`, `DELETE` current session, `POST /users/{id}/roles`
- Startup validation missing: no fail-fast on missing JWT_ISSUER/AUDIENCE/PUBLIC_KEY_URL

### Sprint 3 — Missing Domain APIs

| API | Endpoints needed |
|---|---|
| Tasks | `GET/POST /api/v1/tasks` · `POST /tasks/{id}/reschedule` |
| Tickets/Cases | 5 endpoints: GET/POST/PATCH + escalate + SLA |
| Opportunity pipeline | `GET/POST /api/v1/opportunities` + stage transitions + mark-won/lost |
| Forecasts | `GET /api/v1/forecasts` (weighted pipeline by stage probability) |
| Audit query | `GET /api/v1/audits/events` + exports + integrity verify |

### Sprint 4 — API Standards & State Machines

- Error envelope: all HTTPException → `{"error":{"code":"..."},"meta":{"request_id":"..."}}` on every engine
- Pagination: add `total_pages`; rename `total` → `total_items`
- Unknown fields: `ConfigDict extra=forbid` on all request models
- FollowUp states: add SNOOZED + FAILED (currently: pending/overdue/completed only)
- Conversation states: add WAITING_ON_CONTACT/INTERNAL, RESOLVED, CLOSED, REOPENED
- Lead stage enum: add NURTURING, PROPOSAL, DISQUALIFIED; rename QUALIFIED → QUALIFYING
- Opt-out: "STOP" + "لاگ آف" must be wired into WhatsApp intent classifier
- Cash/manual payment: reconciliation must be gated behind `verification_status == verified`
- Collections reminder schedule: fix to spec cadence (T-3/T-1/T+1/T+7/T+15)
- `Idempotency-Key` header enforcement: wire on all critical write endpoints
- Schema: add `closure_reason` column to leads migration; add FK followup_tasks → leads
- Activity engine: scope in-memory dicts by tenant_id

### Sprint 5 — Observability, CI/CD & Testing

- Structured logging: expand to 16 required fields (trace_id, tenant_id, request_id per request)
- Daily Merkle root checkpoint + hourly integrity job + Sev-1 alerting
- W3C traceparent distributed trace headers
- GitHub Actions: lint + test + build + staging deploy
- Bandit + npm audit in CI pipeline
- Static import denylist: ruff rule blocking `core` → `adapters/pakistan`
- Replace ConcurrencyController stub with real Redis distributed lock
- Lead conversion saga: `Account → Contact → Opportunity` + compensation in services/
- Retry policy: fix to 1s/2×/60s/8 attempts; remove deterministic seed
- `datetime.utcnow()` → `datetime.now(timezone.utc)` everywhere; off-hours check → PKT (UTC+5)
- Coverage gate: CI blocks merge if < 80%
- Load test (locust): follow-up queue + collections happy path
- Full E2E: lead capture → follow-up → close → invoice → payment

---

## Documentation — What Exists

**99 active docs** across 8 catalogue sections (§A–§H).

### Phase 4 Sprint 0 — 9 New Docs Written (2026-05-19)

All 10 product-spec gaps (PS-001–PS-010) resolved. PS-007 was an extension to an existing doc.

| Doc | Gap ID | Phase-5 blocker? | Summary |
|---|---|---|---|
| `cases-domain.md` | PS-001 | Yes — gates B-05, C-05, E-01, A-07, I-04, C-12 | Case entity (23 fields), 7-state machine, SLA tiers, 4 routing strategies, 16 APIs, 3 scanner jobs |
| `shared-inbox.md` | PS-002 | No | Multi-agent assignment, claim endpoint (atomic race guard), handoff, agent presence, 11 APIs |
| `compliance-adapter.md` | PS-003 | No | ComplianceAdapter ABC (5 methods), PakistanComplianceAdapter, 24 PII fields, PDPA/GDPR rules, 9 call sites |
| `conversational-action-spec.md` | PS-004 | No | 9-command dictionary (EN + Urdu), context resolution pipeline, pending_command slot, 7 error conditions |
| `localization.md` | PS-005 | Yes — gates all 75 pages (C-001) | crm-rtl.css architecture, t() function, 2 locales (en-PK/ur-PK), 8 WhatsApp template pairs, P-017 gate |
| `employee-performance.md` | PS-006 | No | 8 KPI definitions with formulas, EmployeePerformanceRM schema, 4 periods, 4 APIs, RBAC visibility rules |
| `collections-engine-model.md §N` | PS-007 | No | PaymentProof entity, file upload spec (JPEG/PNG/PDF/HEIC ≤10MB), 5 APIs, RBAC gates |
| `territory-management.md` | PS-008 | Yes — gates G-09 territories.html | Territory entity + 3-level hierarchy, TerritoryRule JSONB schema, criteria evaluation pipeline, 11 APIs |
| `pricing-plans.md` | PS-009 | No | 4 plan tiers with PKR prices, feature entitlement matrix (21 features), EntitlementGuard pattern, 14-day trial |
| `integration-flow-traces.md` | PS-010 | No | 4 end-to-end flow traces with ordered steps, failure paths, end-state assertions, 6 cross-flow invariants |

---

## Frontend

### Library Phase — Complete

- **96 / 96** NexLink pages built and verified HTTP 200
- All browser-approved
- crm-shell.js, crm-api.js (DUMMY_MODE=true), crm-dummy.js, crm-components.js, crm-locale.js in place
- AI section pages (src/ai/*.html) are self-contained — own aside + header, no crm-shell.js

### Custom Design Phase — Not Started

**75 pages unbuilt.** 13 archetypes (A–M), 8 build phases.

Build Phase 1 queue (start here, in order):

| ID | Page | Archetype | Seed |
|---|---|---|---|
| B-01 | Follow-up Queue | B — List/Queue | customers.html |
| B-02 | Lead Queue | B — List/Queue | customers.html + leads.html |
| C-01 | Lead Detail | C — Entity Detail | profile.html |
| A-01 | Owner Dashboard | A — Dashboard | index.html + sales.html |
| B-08 | Collections Queue | B — List/Queue | customers.html |
| B-03 | Contact List | B — List/Queue | customers.html |
| I-01 | New Lead Form | I — Form/Wizard | — (BUILD) |

**Gate:** Phase 4 all Critical + High items must complete before Phase 5 starts.  
**Phase-5 build blockers all cleared:** cases-domain.md ✓ localization.md ✓ territory-management.md ✓

All custom pages live in: `D:\CRM\frontend\src\app\`  
Dev server: `npm run serve` from `D:\CRM\frontend` → `http://localhost:3001`

---

## Permanently Blocked Items

| ID | Item | Blocked by | What renders instead |
|---|---|---|---|
| P-016 | JazzCash/Easypaisa production payment callbacks | Real credentials + provider sandbox verification | `JAZZCASH_STUB_MODE=true` — stub badge "Payment integration pending" |
| P-017 | All Urdu-locale customer-facing strings | Native Urdu speaker sign-off | English placeholder + `<!-- UR_TODO: -->` comment |
| MR-001 | Facebook/Instagram lead capture automation | Meta Business Manager setup by user | Hidden div with `data-unblock="MR-001"` |
| MR-003 | Voice note transcription (Urdu/Roman Urdu/English) | Transcription provider + credentials | Microphone icon with `disabled` attribute |
| MR-007 | Kuickpay payment adapter | Kuickpay API credentials | Not rendered |

**Rule:** Never set `stub_mode=False` in production without running against the provider sandbox with real credentials and verifying the full payment → webhook → reconciliation cycle end-to-end.  
**Rule:** All `_STRINGS['ur']` values must be reviewed and approved by a native Urdu speaker before any Urdu-locale messages are sent to customers.

---

## Non-Negotiables (always in force)

| Rule | Source |
|---|---|
| RTL must be wired at build time — not retrofitted | CONSTRAINTS.md C-001 |
| All API calls via `crm-api.js` with `DUMMY_MODE` flag | CONSTRAINTS.md C-007 |
| `JAZZCASH_STUB_MODE=true` until P-016 resolved | CONSTRAINTS.md C-009 |
| No country-specific logic in `core/` | architecture-overview.md |
| `core/*` must never import `adapters/pakistan/*` | architecture-overview.md |
| All 96 existing library pages must stay at HTTP 200 after every push | REBUILD-PLAN.md |
| Every new doc must be added to DOC-CATALOGUE.md on the same day it is written | REBUILD-PLAN.md Sprint 0 rule |
| Never commit `.env` — use `.env.example` | .gitignore |

---

## Immediate Next Step

**Phase 4 Sprint 1 — Persistence layer.**

Replace all in-memory dicts with SQLAlchemy DB-backed repositories across all 6 engines. This is the single highest-leverage fix in the entire backlog: without it every restart wipes all data and the system cannot function as a real product regardless of what else is built.

Start with: `FollowupEnforcementEngine` (tables already exist in `0001_followup_schema.py` migration — least resistance path).

---

*Last updated: 2026-05-19 — authored from full §A/§B/§C/§D/§G re-read audit.*
