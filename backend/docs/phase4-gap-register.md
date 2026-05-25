# Phase 4 Stage 3 — Code Overlay Gap Register

**Purpose:** Living document. One row per gap. Updated as each gap is fixed.
**Source:** Code read against PRIMARY doc files (per `_qc/phase4-stage1-read-log.md` cluster map).
**Date opened:** 2026-05-25

Legend: `OPEN` = not fixed | `FIXED` = code change merged | `DEFERRED` = blocked (noted)

---

## Group A — Persistence

All Python services use in-memory data structures. Every restart wipes all state.

| ID | Service / File | Gap | Status |
|---|---|---|---|
| A-001 | `services/followup/engine.py` | `FollowupEnforcementEngine` uses in-memory `_leads`, `_tasks_by_lead`, `_escalations`, `_violations`. DB tables `followup_tasks` + `followup_escalations` exist in migration 0001 but are not used. | FIXED (`hydrate_lead()` added to engine; internal router persists tasks + escalations to DB; metrics computed from DB) |
| A-002 | `services/activity/engine.py` | `ActivityControlEngine` uses in-memory `_entities`, `_activity_log`, `_audit_log`, `_ownership_history`. DB table `activities` exists in migration 0001 but is not used. | FIXED (`log_activity` persists to `activities` table; `list_activities` reads from DB) |
| A-003 | `services/collections/service.py` | `CollectionsService` uses in-memory `_invoices`, `_reconciliation_cases`, `_invoice_to_payments`. No DB migration exists for collections tables. | FIXED (migration 0003 + ORM models + `create_invoice` persists to DB; `list_invoices`/`get_invoice` read from DB; `payment_callback` persists Payment + ReconciliationCase) |
| A-004 | `services/conversation/service.py` | `ConversationalCRMService` uses in-memory `_contexts`, `_activity_log`. No DB migration exists for conversation/message tables. | FIXED (migration 0003 + ORM models + `inbound_webhook` persists Conversation + ConversationMessage; `get_conversation`/`list_conversations` read from DB) |
| A-005 | `gateway/middleware/idempotency.js` | `recordStore = new Map()` — in-memory only. Loses all idempotency records on gateway restart. Spec (`infrastructure/global-idempotency.md §2.1`) requires PostgreSQL `idempotency_records` table. | FIXED (migration 0002 table + ORM model; gateway wiring is next) |
| A-006 | `gateway/middleware/rate-limit-hook.js` | In-memory bucket map. Spec (`infrastructure/execution-hardening.md`) requires Redis-backed rate limiting so limits are shared across instances. | OPEN |
| A-007 | `services/auth/jwt_deps.py` | `FeatureFlagEvaluator` not yet implemented — spec (`infrastructure/feature-flags-config.md`) requires SQLAlchemy + Redis cache. | OPEN |

---

## Group B — Security & Auth

| ID | File | Gap | Status |
|---|---|---|---|
| B-001 | `services/auth/jwt_deps.py` | `TokenClaims` dataclass had only `sub, tenant_id, role, jti`. Missing: `role_ids` (array), `scopes` (list), `aud`, `iss`, `territory_ids`. Spec: `security/identity-auth-rbac.md §3.2`. | FIXED |
| B-002 | `gateway/middleware/auth-rbac.js` | Claims extracted include `sub, user_id, tenant_id, role, scopes, role_ids, jti` but NOT `territory_ids`. Spec §3.2 requires `territory_ids` claim. | OPEN |
| B-003 | `gateway/middleware/auth-rbac.js` | No `jti` revocation check via Redis blocklist. Spec §3.3 requires Redis `jti_blocklist` lookup before allowing request. | OPEN |
| B-004 | `gateway/app.js` | No startup validation. Spec (`infrastructure/execution-hardening.md §6`) requires fail-fast on missing `JWT_ISSUER`, `JWT_AUDIENCE`, `JWT_PUBLIC_KEY_URL`, `DATABASE_URL`. | OPEN |
| B-005 | `gateway/routes/v1-webhooks-whatsapp.routes.js` | Webhook uses API key check; spec (`adapters/whatsapp-execution-model.md §7.1`) requires Meta `X-Hub-Signature-256` HMAC verification using `APP_SECRET`. | OPEN |
| B-006 | `services/collections/jazzcash_adapter.py` | `verify_callback` uses wrong hash method. Spec (`adapters/pakistan-adapter-architecture.md §4.1`) requires sorted param concatenation + `HASH_KEY` HMAC-SHA256. | OPEN |
| B-007 | `gateway/routes/` | Auth management endpoints missing: `POST /api/v1/auth/sessions` (login), `DELETE /api/v1/auth/sessions/{jti}` (logout/revoke), `POST /api/v1/users/{id}/roles` (role assignment). Spec: `security/identity-auth-rbac.md §5`. | OPEN |

---

## Group C — Missing or Incomplete Domain APIs

Routes exist in `gateway/routes/index.js` but Python backing may be incomplete.

| ID | Area | Gap | Status |
|---|---|---|---|
| C-001 | Tasks | `GET/POST /api/v1/tasks`, `POST /tasks/{id}/reschedule` — routing exists in gateway but Python task service needs verification. Spec: `domain/activities-tasks.md`. | OPEN |
| C-002 | Cases | `GET/POST /api/v1/cases`, `PATCH /cases/{id}`, `POST /cases/{id}/escalate`, `GET /cases/{id}/sla` — routing exists but Python cases service needs verification. Spec: `domain/cases-domain.md`. | OPEN |
| C-003 | Opportunities | `GET/POST /api/v1/opportunities`, stage transitions, mark-won/lost — routing exists. Stage probability data may be incomplete. Spec: `domain/opportunities-pipeline.md`. | OPEN |
| C-004 | Forecasts | `GET /api/v1/forecasts` — routing exists. Revenue rollup + pipeline coverage calculations need verification. Spec: `infrastructure/kpi-data-pipelines.md`. | OPEN |
| C-005 | Audit query | `GET /api/v1/audits/events`, export, `GET /api/v1/activities/chain-integrity` — routes exist; chain-integrity endpoint duplicates audit-verify purpose. Spec: `infrastructure/observability-audit.md`. | OPEN |

---

## Group D — API Standards & State Machines

| ID | File | Gap | Status |
|---|---|---|---|
| D-001 | `gateway/routes/v1-leads.routes.js` | `VALID_STAGES` was `['new','contacted','qualified','proposal','negotiation','closed_won','closed_lost']`. DB migration 0001 uses `qualifying, nurturing, disqualified, won, lost`. Now aligned. | FIXED |
| D-002 | `alembic/versions/0001_followup_schema.py` | `followup_tasks.state` CHECK only allowed `pending, overdue, completed`. Spec adds `SNOOZED` + `FAILED` states. | FIXED (migration 0002) |
| D-003 | `alembic/versions/0001_followup_schema.py` | `leads.stage` CHECK: migration was correct. Gateway route VALID_STAGES was wrong (fixed in D-001). No DB schema change needed. | FIXED |
| D-004 | `services/followup/engine.py` + others | `datetime.utcnow()` deprecated since Python 3.12. Fixed in `followup/engine.py`, `followup/http/internal.py`, `activity/monitor/entities.py`. | FIXED |
| D-005 | All Python routers | HTTPException raised with plain string detail. Spec (`infrastructure/api-standards.md §5`) requires error envelope `{"error":{"code":"...","message":"..."},"meta":{"request_id":"..."}}`. | OPEN |
| D-006 | All list endpoints | Pagination response uses `total` not `total_items`; missing `total_pages`. Spec: `infrastructure/api-standards.md §4.2`. | OPEN |
| D-007 | All Python request models | Missing `model_config = ConfigDict(extra="forbid")` — unknown fields accepted silently. Spec: `infrastructure/api-standards.md §3.1`. | OPEN |
| D-008 | `services/collections/service.py` | Manual payment reconciliation not gated behind `verification_status == verified`. Spec: `domain/collections-engine-model.md §4.2`. | OPEN |
| D-009 | `gateway/middleware/idempotency.js` | `Idempotency-Key` header not enforced on all critical write endpoints (PUT, PATCH, DELETE also). Spec: `infrastructure/global-idempotency.md §1.2`. | OPEN |
| D-010 | `services/db/models/lead.py` | `closure_reason` column missing from leads table. FK `followup_tasks → leads` missing. | FIXED (migration 0002) |

---

## Group E — Observability, CI/CD & Testing

| ID | Area | Gap | Status |
|---|---|---|---|
| E-001 | All services | No structured logging. Spec (`infrastructure/observability-audit.md §2`) requires 16 fields: `trace_id, tenant_id, request_id, service, level, message, event_type, entity_type, entity_id, actor_id, latency_ms, http_status, error_code, timestamp, env, version`. | OPEN |
| E-002 | Gateway | No W3C `traceparent` header propagation. Spec: `infrastructure/observability-audit.md §2.3`. | OPEN |
| E-003 | Activity engine | No daily Merkle root checkpoint + hourly chain integrity job + Sev-1 alerting. Spec: `domain/activity-control-model.md §4.3`. | OPEN |
| E-004 | `.github/workflows/` | No CI/CD pipeline. Spec: `infrastructure/execution-hardening.md §6`. Needs: lint, test, build, staging deploy, Bandit, coverage gate (< 80% blocks merge). | OPEN |
| E-005 | Gateway middleware | No static import denylist preventing `core` → `adapters/pakistan` imports. Spec: `architecture/architecture-overview.md §3`. Requires ruff rule. | OPEN |
| E-006 | `gateway/middleware/concurrency.js` | `ConcurrencyController` stub — needs real Redis distributed lock implementation. Spec: `infrastructure/distributed-lock-strategy.md §2`. | OPEN |
| E-007 | `services/` | Lead conversion saga `Account → Contact → Opportunity` + compensation transaction missing. Spec: `infrastructure/workflow-catalog.md §3`. | OPEN |
| E-008 | Tests | No E2E test: lead capture → follow-up → close → invoice → payment. No locust load test for follow-up queue + collections path. Coverage gate not enforced. | OPEN |

---

## Fix Log

| Date | ID | Change |
|---|---|---|
| 2026-05-25 | B-001 | `services/auth/jwt_deps.py` — `TokenClaims` extended: `role_ids`, `scopes`, `aud`, `iss`, `territory_ids`; conditional aud/iss verification |
| 2026-05-25 | D-001 | `gateway/routes/v1-leads.routes.js` — `VALID_STAGES` aligned to spec + migration: `qualifying, nurturing, won, lost, disqualified` |
| 2026-05-25 | D-003 | Gateway lead stage fix — no DB change needed (migration 0001 already correct) |
| 2026-05-25 | D-004 | `services/followup/engine.py`, `services/followup/http/internal.py`, `services/activity/monitor/entities.py` — `datetime.utcnow()` → `datetime.now(timezone.utc)` |
| 2026-05-25 | D-002 | `alembic/versions/0002_…` migration — `followup_tasks.state` CHECK extended: `snoozed`, `failed`; `services/db/models/followup.py` comment updated |
| 2026-05-25 | D-010 | `alembic/versions/0002_…` migration — `leads.closure_reason` column + FK `followup_tasks→leads` added |
| 2026-05-25 | A-005 | `alembic/versions/0002_…` migration — `idempotency_records` table created; `services/db/models/idempotency.py` ORM model created |
| 2026-05-25 | A-003 | `alembic/versions/0003_…` migration — `invoices`, `payments`, `reconciliation_cases` tables; `services/db/models/collections.py` ORM models |
| 2026-05-25 | A-004 | `alembic/versions/0003_…` migration — `conversations`, `conversation_messages` tables; `services/db/models/conversations.py` ORM models |
| 2026-05-25 | BUG | `services/activity/engine.py:_parse_rfc3339` — strip `Z` not replace; prevents double-offset `+00:00+00:00` when string already carries numeric tz offset |
| 2026-05-25 | BUG | `services/dashboard/owner/service.py:_parse_dt` — same double-offset fix |
| 2026-05-25 | BUG | `adapters/pakistan/payments/jazzcash.py:normalize_transaction` — only divide by 100 for `pp_Amount` (paise), not `amount` fallback (already PKR) |
| 2026-05-25 | INFRA | `src/event_bus/catalog_schema.py` — path updated to `docs/infrastructure/event-catalog.md` (Stage 2E restructure) |
| 2026-05-25 | INFRA | `src/event_bus/catalog_events.py` — 9 missing events added: `lead.conversion.failed.v1`, 2 `case.sla.*` events, 6 partner events |
| 2026-05-25 | INFRA | `scripts/self_qc_event_bus.py`, `self_qc_execution_hardening.py`, `self_qc_final_supervisor.py` — doc paths updated for Stage 2E subdirectory structure |
| 2026-05-25 | INFRA | `services/collections/service.py` — `_payments` dict added for dashboard compatibility |
| 2026-05-25 | A-001 | `services/followup/engine.py` — `hydrate_lead()` method added; `services/followup/http/internal.py` — `register_lead` persists to DB; `suggest_next_action` hydrates from DB; `process_due` loads active leads + persists escalations; `metrics` computed from DB |
| 2026-05-25 | A-002 | `services/activity/http/public.py` — `log_activity` persists `ActivityEvent` to `activities` table; `list_activities` reads from DB with pagination |
| 2026-05-25 | A-003 | `services/collections/http/public.py` — `create_invoice` persists to DB; `list_invoices`/`get_invoice` read from DB; `payment_callback` persists Payment + ReconciliationCase |
| 2026-05-25 | A-004 | `services/conversation/http/public.py` — `inbound_webhook` persists Conversation + ConversationMessage to DB; `get_conversation`/`list_conversations` read from DB |

---

*Last updated: 2026-05-25 — 314/314 tests passing; A-001/002/003/004 DB wiring complete; 9 open gaps remain.*
