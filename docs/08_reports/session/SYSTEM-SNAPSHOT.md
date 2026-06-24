# Pakistan CRM OS — System Snapshot

> **STALE HEADER — Updated 2026-06-21:** The phase completion table below is correct. C3, C4, and C5 are all COMPLETE. C6 is the current phase. See `docs/07_governance/AI_OPERATING_CONTEXT.md` for the authoritative session orientation document.

**Date:** 2026-06-01
**Overall grade:** 9.97 / 10
**Refresh trigger:** 2026-06-21 — **C5 Post-Deploy Smoke COMPLETE. C6 Commercial Launch is current (ACTIVE).**
C0 ✓ Environment Seal (2026-05-31) · C1 ✓ DB Wiring 44/44 routes (2026-05-31) · C2 ✓ Full test suite (2026-06-01) · C3 ✓ Code Hardening (2026-06-01) · C4 ✓ Infrastructure Deployment Render.com (2026-06-01) · C5 ✓ Post-Deploy Smoke (2026-06-02):
- C2a: 761/761 pytest, 87% coverage | C2b: 63/63 API contracts | C2c: 75-page Playwright E2E
- C2d: Locust p95=28ms 0 5xx | C2e: semgrep 0 ERRORs, npm/pip clean
- New: 7 FastAPI HTTP service modules (AI, campaigns, cases, inbox, territories, workflows, partners)

> **How to use this file:** Read `docs/07_governance/AI_OPERATING_CONTEXT.md` FIRST every session — it is the authoritative session orientation document as of Governance Phase 1 (2026-06-21). This file is a historical snapshot (2026-06-01); the phase completion table below is accurate but the header was stale (now corrected — C6 is current). Use this file for system detail (what is built, what is wired, gap register) after reading AI_OPERATING_CONTEXT.md.
> - `docs/07_governance/AI_OPERATING_CONTEXT.md` — **PRIMARY session opener** — current phase, frozen decisions, known constraints
> - `COMMERCIALISATION-PLAN.md` — **active anchor from 2026-05-31** — read this second every session; has RESUME POINT, phase gates C0–C6, all process details
> - `SESSION-HANDOFF.md` — read this if resuming mid-phase; has exact gap list and next steps
> - `PENDING.md` — full checkbox task queue (Commercialisation section is current)
> - `PROGRESS.md` — page-by-page build tracker (what is locked, what is ⏳)
> - `SCREEN-ARTEFACTS.md` — QC records and browser sign-offs for all built pages
> - `REBUILD-PLAN.md` — **CLOSED** — build phases 1–6 historical record only
> - `docs/reports/u-series/DOC_CATALOGUE.md` — master index of every .md file in the project
> - `PAGE-BUILD-PROTOCOL.md` — mandatory anchor for every page fix during C2c/C5

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
| Phase 5 | Frontend — 75 Custom Pages | ✓ COMPLETE 2026-05-29 — all 75 pages built and browser-approved |
| Phase M | Mapping & Convergence | ✓ COMPLETE 2026-05-27 — 27 gaps closed, 0 deferred |
| Phase 5B | Backend Domain Extension — 7 new service domains | ✓ COMPLETE 2026-05-30 — all 7 sprints done |
| **Phase 6** | **Market Research + Final Hardening + Full QC** | **✓ COMPLETE 2026-05-31 — all components done** |
| **C0** | **Environment Seal** | **✓ COMPLETE 2026-05-31** |
| **C1** | **DB Wiring (local)** | **✓ COMPLETE 2026-05-31 — 44/44 gateway routes, PostgreSQL seeded** |
| **C2** | **Automated Test Suite** | **✓ COMPLETE 2026-06-01 — 761 tests, 87%, E2E, load, security** |
| **C3** | **Code Hardening** | **✓ COMPLETE 2026-06-01** |
| **C4** | **Infrastructure Deployment (Render.com)** | **✓ COMPLETE 2026-06-01 — all 5 services LIVE on free tier** |
| **C5** | **Post-Deploy Smoke** | **✓ COMPLETE 2026-06-02 — all production gates pass** |
| **C6** | **Commercial Launch** | **← CURRENT** |

**Overall task progress:** 176 / 176 tasks done (100%) — all build phases complete. Commercialisation: C0–C5 COMPLETE. C6 Commercial Launch is current (ACTIVE).

---

## Scores by Area

| Area | Score | Target | Gap |
|---|---|---|---|
| Documentation | 10/10 | 10/10 | 78 active docs in 9 subdirs; all ownership blocks set; 3 new domain specs added (marketing-campaigns, partners, ai-predictive-models) |
| Architecture design | 8.5/10 | 10/10 | 7 new domain services added in Phase 5B; event bus not wired; ML models rule-based v1 (ML upgrade Phase 6+) |
| Project structure | 7/10 | 10/10 | Docker, Makefile, pre-commit, Alembic present; CI/CD pipeline live; no containers/staging deploy yet |
| Code implementation | 9.8/10 | 10/10 | All 28 Phase 4 gaps + all 7 Phase 5B domains complete; A-006 (Redis rate-limit) and A-007 (FeatureFlag Redis) deferred to Phase 6 |
| Testing | 9.5/10 | 10/10 | 761/761 tests, 87% coverage; 63 API contracts; Playwright E2E 75 pages; Locust p95=28ms; semgrep 0 ERRORs |
| DevOps / CI-CD | 7/10 | 10/10 | `.github/workflows/ci.yml` live; no containers/staging deploy yet (C4) |
| Security implementation | 9.0/10 | 10/10 | jti revocation, HMAC, C: seal, prototype-pollution fix (contacts route), 0 CVEs Critical; Redis rate-limit deferred to C3 |
| Frontend | 10/10 | 10/10 | 96 library pages done; **75/75 custom pages T1–T4 ✓**; **75/75 wired to live API**; 0 externally blocked — all browser-approved 2026-05-31 |

---

## Documentation — Current State

**78 active docs** — 55 core spec files + 15 B9 UI specs + 3 QC docs + 3 ADRs + 1 enterprise-depth + 1 gap register. (3 domain specs added in Phase 5B: marketing-campaigns.md, partners.md, ai-predictive-models.md)

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

**Tests:** 761/761 passing (87% coverage — C2a gate ✓)
`93 Phase 2+3 originals + 14 pre-Phase-4 audit fixes + 201 legacy src/ tests + 6 Stage 3 fixes + 10 E2E + 29 cases + 34 inbox + 36 territories + 40 campaigns + 40 partners + 45 workflows + 47 AI + 63 API contracts + 7 Playwright E2E + new HTTP route tests (ai/campaigns/cases/inbox/territories/workflows/partners)`

**API contract tests:** `D:\CRM\tests\api\` — 63 tests: smoke (44 routes), auth, tenant isolation, billing, integrations, governance, reports, communications

**E2E Playwright:** `D:\CRM\tests\e2e\playwright\` — 75-page load, KPI render, DataTable rows, filter chips, form submit, settings, audit pages

**Load tests:** `D:\CRM\tests\load\locustfile.py` — 6 Locust scenarios. Last run: p95=28ms aggregated, 0 5xx

**Security reports:** `D:\CRM\tests\security\` — semgrep-report.json (0 ERRORs), pip-audit.json

### 6 Engines (Phase 2–3) + 7 Phase 5B Domains

| Engine | Key capabilities | Public endpoints |
|---|---|---|
| **WhatsApp Engine** | Inbound webhook (async 200 return), intent classification (payment_query → follow_up_response → lead_inquiry → support_request), conversation threading keyed by tenant_id+phone, auto lead creation, anti-lead-loss guarantee | `POST /api/v1/webhooks/whatsapp` · `GET /api/v1/conversations` · `GET /api/v1/conversations/{id}` |
| **Follow-up Engine** | Enforcement ladder T+0/+2h/+24h/+48h, overdue scanner (60s background job), escalation ladder, OCC version_no, RBAC-gated escalate (manager/admin only) | `GET/POST /api/v1/followups` · `PATCH /followups/{id}/complete` · `POST /followups/{id}/escalate` · `GET /followups/{id}` |
| **Collections Engine** | Invoice lifecycle (unpaid→partial→paid→overdue), JazzCash/Easypaisa payment callbacks, confidence scoring (≥85 auto-match / 40–84 manual / <40 unmatched), WhatsApp reminder cadence (T-3/T-1/T+1/T+7/T+15), customer opt-out (STOP / لاگ آف), manual payment proof (submit/verify/reject) | `POST/GET /api/v1/invoices` · `GET /invoices/{id}` · `POST /invoices/{id}/send` · `POST /payments/callback/{provider}` |
| **Activity Control Engine** | Immutable append-only hash-chain audit log, dual event emission, chain-integrity verification | `POST/GET /api/v1/activities` · `GET /api/v1/activities/chain-integrity` |
| **Activation Engine** | <10-minute onboarding, seed pipeline + 5 contacts + 4 deals, WhatsApp sandbox simulation, sandbox→production transition, Aha moment trigger | `POST /api/v1/activation/start` · `/whatsapp-sim` · `/move-deal` · `GET /api/v1/activation/status` |
| **Execution Control Plane** | Global idempotency ledger, exponential retry (1s base / 2× / 60s max / 8 attempts), DLQ with operator API | `GET /api/v1/admin/dead-letters` · `POST /{id}/retry` · `POST /{id}/requeue` |

**Phase 5B Domains (Sprint 5B-1 → 5B-7):**

| Domain | Key capabilities | Gateway prefix |
|---|---|---|
| **Cases / Support** | State machine (open→investigating→pending→resolved→closed), PKT business-hour SLA timers, escalation ladder, knowledge base | `/api/v1/cases` · `/support` · `/knowledge` |
| **Shared Inbox** | Conversation claim/handoff, round-robin + least-loaded auto-assign, agent presence tracking, queue management | `/api/v1/inbox` |
| **Territories** | 9-rule type evaluation (city/region/tier/industry/rep_explicit), AND logic, priority conflict resolution, manual override supersedes chain | `/api/v1/territories` |
| **Marketing / Campaigns** | State machine (draft→scheduled→active→paused→completed), WhatsApp opt-in gate, P-017 Urdu activation guard, attribution 30-day window | `/api/v1/campaigns` · `/segments` · `/templates` |
| **Partners** | Tier-based commission rates (platinum 15%/gold 10%/silver 5%), deal registration expiry, `status=paid` immutability (409) | `/api/v1/partners` · `/deal-registrations` |
| **Workflow Engine** | DSL validation, publish guard, simulate dry-run, retry with parent_execution_id chain, cancel terminal-state guard | `/api/v1/workflows` (incl. `/runs`) |
| **AI / Predictive Models** | lead_score_v1 (9-feature weighted sum, hot/warm/cold/disqualified), churn_predict_v1 (risk accumulation), clv_estimate_v1, copilot suggestions (6 types), 5-class intent classifier | `/api/v1/ai/scores` · `/predictions` · `/estimates` · `/copilot` · `/models` |

### DB / Auth State

**ORM models (services/db/models/) — 38 models across 11 files:**
- `FollowupTask`, `FollowupEscalation` — migration 0001
- `Lead`, `Activity` — migration 0001
- `Invoice`, `Payment`, `ReconciliationCase` — migration 0003
- `Conversation`, `ConversationMessage` — migration 0003
- `IdempotencyRecord` — migration 0002
- `Case`, `CaseComment`, `CaseEscalation`, `SupportQueue`, `SLAPolicy`, `KnowledgeArticle` — migration 0004
- `InboxQueue`, `AgentPresence`, `ConversationHandoff` — migration 0005
- `Territory`, `TerritoryRule`, `TerritoryAssignment` — migration 0006
- `Campaign`, `CampaignSegment`, `MessageTemplate`, `CampaignSend`, `CampaignConversion` — migration 0007
- `Partner`, `DealRegistration`, `PartnerCommission`, `PartnerActivityLog` — migration 0008
- `WorkflowDefinition`, `WorkflowExecution`, `WorkflowStep` — migration 0009
- `LeadScore`, `ChurnPrediction`, `CLVEstimate`, `CopilotSuggestion` — migration 0010

**Alembic migrations — chain 0001→0010 (sealed):**
- `0001` — followup_tasks, followup_escalations, leads, activities
- `0002` — snoozed/failed states, closure_reason, FK, idempotency_records
- `0003` — invoices, payments, reconciliation_cases, conversations, conversation_messages
- `0004` — cases (6 tables, SLA timers, PKT business hours)
- `0005` — inbox (extends conversations + 3 new tables)
- `0006` — territories (3 tables, 2 partial unique indexes)
- `0007` — campaigns (5 tables, P-017 Urdu guard)
- `0008` — partners (4 tables, commission immutability)
- `0009` — workflows (3 tables, unique workflow_key per tenant)
- `0010` — AI scores (4 tables: lead_scores, churn_predictions, clv_estimates, copilot_suggestions)

**FastAPI HTTP Route Modules (added C2, mounted in services/app.py):**
- `services/territories/http/public.py` — CRUD + rule eval + performance + assignment
- `services/workflows/http/public.py` — definition CRUD + publish/simulate + execution runs + retry/cancel
- `services/partners/http/public.py` — partner CRUD + commissions + deal registrations
- `services/ai/http/public.py` — lead scores + churn predictions + CLV + copilot suggestions + query
- `services/campaigns/http/public.py` — campaign CRUD + state machine + segments + templates
- `services/cases/http/public.py` — case CRUD + state machine + comments + escalate
- `services/inbox/http/public.py` — conversations + claim + handoff + send message + presence + queues

**Auth:**
- JWT Bearer middleware on all routes
- Python `TokenClaims`: `sub, tenant_id, role, jti, role_ids, scopes, aud, iss, territory_ids`
- Gateway `auth-rbac.js` handles RBAC, scope enforcement, rate limiting (in-memory — Redis wiring is C3 A-006)
- Gateway dev token uses UUID tenant_id `00000000-0000-0000-0000-000000000001` (fixed C1)
- 20 missing scopes added to `rbac-scopes.js` (tasks, activities, emails, forecasts, billing, reports, integrations, compliance, privacy, marketing, audit.logs)

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

### Open (2 — C3 targets)

| ID | What remains | C-phase |
|---|---|---|
| A-006 | Gateway rate-limit: swap in-memory token buckets for Redis (`ioredis`) writing to `D:\DockerData` | C3 |
| A-007 | `FeatureFlagEvaluator` — Redis cache with 60s TTL (SQLAlchemy already wired) | C3 |

**Additional C3 items from COMMERCIALISATION-PLAN.md §C3:**
- JWT refresh token flow (`POST /auth/refresh` — 15min access + 7d refresh, httpOnly cookie)
- Password reset OTP flow (`POST /auth/forgot-password` + `POST /auth/reset-password`)
- Multi-tenant signup (`POST /auth/register` → create tenant → seed pipeline → return JWT)
- `helmet()` active on all gateway routes (XSS, HSTS, CSP headers)
- CORS restricted to origin whitelist
- PostgreSQL stability on Windows — EDB pg16 stops under heavy load; mitigation: pg config tuning
- Fix `leads.repository.js` VALID_STAGES/VALID_PRIORITIES mismatch with DB CHECK constraints

---

## Frontend

### Library Phase — Complete

- **96 / 96** NexLink pages built and verified HTTP 200
- `crm-shell.js`, `crm-api.js` (DUMMY_MODE=true), `crm-dummy.js`, `crm-components.js`, `crm-locale.js` in place
- AI section pages (`src/ai/*.html`) self-contained — own aside + header, no crm-shell.js

### Custom Design Phase — FRONTEND COMPLETE / BACKEND UNBLOCKED

**State as of 2026-05-30:**
- **75 of 75 custom pages built** — all Cat 1 browser-approved; Cat 2 built in DUMMY_MODE=true
- **All 28 Cat 2 backend domains now exist** — Phase 5B complete unblocked all Cat 2 pages
- **b9-p spec alignment complete** (2026-05-28) — all 13 archetypes fully covered
- **75-page 3-category mapping complete** — `backend/FRONTEND-BACKEND-MAPPING.md` Section 7
- **T1–T4 protocol audit ✓ COMPLETE 2026-05-30** — all 75 pages pass all 4 tiers; 9 pages fixed (lead-new, dashboard, followups, leads, contacts, collections, leads-detail, ai-insights, identity-dashboard); all locked in SCREEN-ARTEFACTS.md

**Build state by category:**

| Category | Total | Built | Backend domain | Wired live |
|---|---|---|---|---|
| Cat 1 — Both sides exist | 47 | **47 ✓** | ✓ | ✓ 47 live |
| Cat 2 — No backend domain | 28 | **28 ✓** | ✓ Phase 5B complete | ✓ 28 live |
| **Total custom** | **75** | **75 ✓** | **75 ✓** | **75 live · 0 blocked · all browser-approved 2026-05-31** |

**Archetype b9-p spec status (2026-05-28 update):**

| Archetype | b9-p Spec | Spec status | Mapping category |
|---|---|---|---|
| A Dashboard | b9-p01 | ✓ Valid | Mixed (A-04/05/06 Cat1; A-07/09/10 Cat2; A-12 Cat3) |
| B List/Queue | b9-p02 | ✓ Valid — vocab updated | Mixed (B-01/02/08/09/10 Cat1; B-03/04/05/07/11 Cat2; B-06 Cat3) |
| C Entity Detail | b9-p06 | ✓ Valid — case/subscription states added | Mixed (C-01/04/06/09 Cat1; C-02/03/05/08/11/12 Cat2; C-07 Cat3) |
| D Sales Cockpit | b9-p03 | ✓ Valid | D-01 Cat1 |
| E Support Console | b9-p04 | ✓ Valid — CaseStatus added | E-01 Cat2 (no case backend) |
| F Marketing | b9-p05 | ✓ Valid | F-01 Cat2 (no backend) |
| G Settings/Admin | b9-p09 | ✓ Updated — 4 missing pages added, routes fixed | Mixed (G-02 Cat1; G-03/04/06/07/08/09 Cat2; G-05 Cat3) |
| H Reporting | b9-p10 | ✓ Restructured — H-01–H-07 now defined | Mixed (H-01/04/06 Cat1; H-02/03/05/07 Cat2) |
| I Form/Wizard | b9-p11 | ✓ Updated — I-01–I-04/I-06 added | Mixed (I-01/03/05 Cat1; I-02/04/06 Cat2) |
| J Audit/Compliance | b9-p12 | ✓ Updated — J-02/J-04/J-05 added | Mixed (J-01/02/04 Cat1; J-05 Cat2; J-03 Cat3) |
| K Builder | b9-p07/p08 | ✓ Valid | Mixed (K-04 Cat3; K-01/02/03 Cat2) |
| L Inbox | b9-p13 | ✓ Updated — shared-inbox entities, L-03 added | Mixed (L-01/02 Cat3 — Python service not at gateway; L-03 Cat2) |
| M AI/Copilot | b9-p14 | ✓ Valid | M-01/02 Cat2 (no AI backend) |

**Protocol:** `PAGE-BUILD-PROTOCOL.md` — read before every build. Phase gate = your approval before next phase starts.
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
| Every new doc added to `docs/reports/u-series/DOC_CATALOGUE.md` same day it is written | REBUILD-PLAN.md |
| Never commit `.env` — use `.env.example` | .gitignore |

---

## Immediate Next Step

**Phase 6 wiring extension DONE. All 75 pages live + browser-approved. Commercialization phase is next.**

**Phase 6 queue — current state:**
1. ✓ **T1–T4 protocol audit** — COMPLETE 2026-05-30. 75/75 pages pass.
2. ✓ **Wiring sprint** — COMPLETE 2026-05-31. 75/75 pages live (incl. 5 inline stub routes). 0 blocked.
3. ✓ **MR-004** — COMPLETE 2026-05-30. Daily WhatsApp summary scheduler + 9 tests.
4. ✓ **MR-005** — COMPLETE 2026-05-30. Excel import/export (leads + contacts) + 18 tests.
5. ← **Commercialization** — DB wiring, full automated test suite (Playwright/Locust/OWASP), code hardening, Render.com deployment. See commercialization plan.

**Blocked (do not start):** MR-001 (Meta Business Manager), MR-002 (P-016 credentials), MR-003 (transcription provider), MR-007 (Kuickpay credentials).

**Before any build:** Read `PAGE-BUILD-PROTOCOL.md` in full.

---

*Last updated: 2026-06-21 (Remediation pass — CF-001 fix) — Phase header updated: C6 is CURRENT. C3/C4/C5 are COMPLETE. 44 total gateway route files (corrected from 42 by U10 remediation 2026-06-21). 75/75 pages wired to live API + browser-approved. See docs/07_governance/AI_OPERATING_CONTEXT.md for authoritative current-session orientation.*
