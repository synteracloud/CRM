# CRM Gap Register — Docs vs Code

**Generated:** 2026-04-02
**Scope:** All code in `adapters/`, `db/`, `gateway/`, `middleware/`, `services/`, `src/` cross-referenced against all docs in `docs/`
**Purpose:** Surgical fix guide. Gaps are ordered by dependency layer — fix Layer 0 first, each subsequent layer unblocks the next.

---

## Reading This Register

| Field | Meaning |
|---|---|
| **ID** | Stable reference for each gap (never reuse) |
| **Layer** | Dependency order — L0 has no blockers; L1 needs L0 done first, etc. |
| **Severity** | CRITICAL = blocks a core flow; HIGH = missing capability; MEDIUM = partial impl; LOW = polish |
| **State** | OPEN / IN PROGRESS / FIXED |
| **Complexity** | S = < 1 day; M = 1–3 days; L = 3–7 days |

---

## Layer 0 — Foundation (No Blockers)

These gaps block everything above them. Fix first.

---

### GAP-001
**Title:** Missing `ComplianceAdapter` interface
**Layer:** 0 | **Severity:** HIGH | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/architecture-overview.md` defines L2 Interfaces as: `MessagingAdapter`, `PaymentAdapter`, **`ComplianceAdapter``.
`docs/pakistan-adapter-architecture.md` §4.3 provides full interface spec with `preActionCheck()` and `postActionReport()`.

**Code reality:**
`adapters/interfaces/` contains only `messaging_adapter.py`, `payment_adapter.py`, `types.py`.
`ComplianceAdapter` does not exist at any path.

**What is needed:**
- Create `adapters/interfaces/compliance_adapter.py` with the `ComplianceAdapter` Protocol, `ComplianceCheckInput`, `ComplianceCheckResult`, `ComplianceReportInput`, `ComplianceReportResult` dataclasses, and `NoopComplianceAdapter` passthrough.

**Blocked by:** nothing
**Blocks:** GAP-005 (Pakistan compliance stubs), GAP-008 (adapter registry)

---

### GAP-002
**Title:** Missing DB schemas for identity, tenant, lead, contact, opportunity, order, workflow, audit, feature-flag, notification domains
**Layer:** 0 | **Severity:** CRITICAL | **Complexity:** L | **State:** FIXED

**Doc says:**
`docs/domain-model.md` defines 58 entities across 9 domains. `docs/data-architecture.md` requires domain-owned, tenant-scoped relational stores — one schema file per domain.

**Code reality:**
`db/` contains only three schema files:
- `db/activity_task_db/schema.sql` ✓
- `db/transaction_db/schema.sql` ✓
- `db/messaging_db/schema.sql` ✓

**What is missing (one schema file each):**

| Missing Schema | Key Tables | Doc Reference |
|---|---|---|
| `db/identity_auth_db/schema.sql` | `users`, `roles`, `permissions`, `user_roles`, `sessions`, `refresh_tokens` | `docs/identity-auth-rbac.md` |
| `db/org_tenant_db/schema.sql` | `tenants`, `tenant_entitlements`, `organizations`, `organization_memberships` | `docs/org-multi-tenancy.md` |
| `db/lead_management_db/schema.sql` | `leads`, `lead_assignments`, `lead_history` | `docs/domain-model.md` |
| `db/contact_account_db/schema.sql` | `contacts`, `accounts`, `account_hierarchy` | `docs/domain-model.md` |
| `db/opportunity_db/schema.sql` | `opportunities`, `opportunity_line_items`, `forecast_records` | `docs/opportunities-pipeline.md` |
| `db/quote_order_db/schema.sql` | `quotes`, `quote_line_items`, `orders`, `order_line_items` | `docs/cpq-quotes-orders.md` |
| `db/workflow_db/schema.sql` | `workflow_definitions`, `workflow_executions`, `workflow_steps` | `docs/workflow-dsl.md` |
| `db/audit_compliance_db/schema.sql` | `audit_log`, `compliance_events` | `docs/observability-audit.md` |
| `db/feature_flag_db/schema.sql` | `feature_flags`, `flag_rules`, `flag_evaluations` | `docs/feature-flags-config.md` |
| `db/notification_db/schema.sql` | `notifications`, `notification_templates`, `delivery_log` | `docs/service-map.md` |

**Blocked by:** nothing
**Blocks:** GAP-007 (sync persistence), GAP-010 (gateway leads route), GAP-011 (gateway opportunities route)

---

### GAP-003
**Title:** `db/messaging_db/schema.sql` missing offline sync queue, template versioning, and dead-letter tables
**Layer:** 0 | **Severity:** MEDIUM | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/offline-sync.md` §4 specifies a `CommandRecord` schema with `idempotency_key`, `status`, `retry_count`, etc.
`docs/integration-contracts.md` WhatsApp section requires dead-letter tracking for webhook failures.
`docs/whatsapp-execution-model.md` §7 references template policy and message template versioning.

**Code reality:**
`db/messaging_db/schema.sql` has `contacts`, `conversations`, `messages`, `message_events`, `message_idempotency` — functional but missing:
- `sync_command_queue` table (offline sync persistence)
- `message_templates` table (template versioning)
- `webhook_dead_letter` table (dead-letter for failed webhook processing)

**Blocked by:** nothing
**Blocks:** GAP-007 (sync persistence layer)

---

### GAP-004
**Title:** Pakistan payment adapters store state in-memory only — no real provider API calls
**Layer:** 0 | **Severity:** MEDIUM | **Complexity:** M | **State:** FIXED

**Doc says:**
`docs/pakistan-adapter-architecture.md` §3.B specifies: "Implement payment create/capture/refund/status for local gateways (Easypaisa, JazzCash). Normalize payment states to canonical status enum."
`docs/integration-contracts.md` Pakistan Payments section defines real provider API endpoints and HMAC signing contracts.

**Code reality:**
`adapters/pakistan/payments/base.py` implements the full `PaymentAdapter` Protocol but uses `self._payments: dict` as an in-memory store rather than calling real provider APIs. `create_payment()` generates a synthetic `provider_txn_id` (`jazzcash-txn-{key}`). `verify_callback()` at line 159 has a bug: `hmac.new()` should be `hmac.new()` — it is `hmac.new()` which doesn't exist; correct is `hmac.new` is not valid, should be `hmac.HMAC` constructor via `hmac.new` → actually should be `hmac.new(key, msg, digestmod)`.

`adapters/pakistan/payments/jazzcash.py` only implements `normalize_transaction()` — not a real JazzCash API call.

**What is needed:**
- `adapters/pakistan/payments/jazzcash.py` needs real JazzCash HMAC-signed POST to their API (or configurable stub mode for non-prod)
- `adapters/pakistan/payments/easypaisa.py` needs real Easypaisa OAuth2 + HMAC call
- `base.py` line 159: `hmac.new(...)` → `hmac.new(self.secret, str(payload).encode("utf-8"), hashlib.sha256)` is a bug — `hmac.new` doesn't exist; the correct call is `hmac.new(self.secret, str(payload).encode("utf-8"), hashlib.sha256)` → should be `hmac.HMAC` or just `hmac.new` which in Python is actually valid via `hmac.new` but the module-level function is `hmac.new()`. Actually wait, in Python `hmac` module has `hmac.new(key, msg=None, digestmod='')`. So `hmac.new(...)` is valid. Let me reconsider — this might be correct Python.

Actually, looking more carefully: Python's `hmac` module does have `hmac.new(key, msg, digestmod)`. So that's fine. The in-memory storage is the issue.

**Blocked by:** nothing
**Blocks:** GAP-009 (adapter registry needs production-ready adapters)

---

### GAP-005
**Title:** Missing Pakistan localization adapters (`LocaleAdapter`, `PhoneFormatter`)
**Layer:** 0 | **Severity:** LOW | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/pakistan-adapter-architecture.md` §3.C and §3.D specify:
- `PhoneFormatter` for E.164 normalization + Pakistan local input parsing
- `LocaleAdapter` for PKR currency formatting, date/time rendering
`docs/architecture-overview.md` Layer Model shows `PhoneFormatter` and `LocaleAdapter` as L2 interfaces.

**Code reality:**
- No `adapters/interfaces/locale_adapter.py`
- No `adapters/interfaces/phone_formatter.py`
- No `adapters/pakistan/localization/` directory at all
- Pakistan adapters hardcode `currency: "PKR"` directly

**Blocked by:** nothing
**Blocks:** GAP-008 (adapter registry requires all adapter types)

---

## Layer 1 — Adapter Completeness (Needs L0)

---

### GAP-006
**Title:** Missing 360dialog and Gupshup WhatsApp adapter implementations
**Layer:** 1 | **Severity:** CRITICAL | **Complexity:** M | **State:** FIXED

**Doc says:**
`docs/integration-contracts.md` WhatsApp Provider Contracts table lists 360dialog and Gupshup with explicit:
- Base URLs, endpoint paths, auth headers (`D360-API-KEY`, `apikey`)
- Webhook contracts: `POST /webhooks/whatsapp/360dialog` and `POST /webhooks/whatsapp/gupshup`
- Canonical deduplication keys: `messages[].id` and `payload.id` respectively
`docs/pakistan-adapter-architecture.md` §2 shows `whatsapp_360dialog_adapter.py` and `whatsapp_gupshup_adapter.py` in the directory tree.

**Code reality:**
`adapters/pakistan/messaging/` contains only:
- `meta_api_adapter.py` ✓ (functional)
- `twilio_adapter.py` ✓ (functional)

No 360dialog or Gupshup implementations exist.

**What is needed:**
- `adapters/pakistan/messaging/dialog360_adapter.py` implementing `MessagingAdapter` Protocol: `send_message`, `send_template`, `get_message_status`, `parse_webhook`, `parse_inbound` with 360dialog-specific headers and webhook format
- `adapters/pakistan/messaging/gupshup_adapter.py` implementing same Protocol with Gupshup-specific API structure
- Gateway webhook routes for both (covered by GAP-014)

**Blocked by:** nothing (MessagingAdapter interface already exists)
**Blocks:** GAP-008 (registry needs all providers), GAP-014 (webhook routes)

---

### GAP-007
**Title:** `SyncService` is in-memory only — no persistence, no per-entity conflict strategy
**Layer:** 1 | **Severity:** HIGH | **Complexity:** M | **State:** FIXED

**Doc says:**
`docs/offline-sync.md` specifies:
- §3: Queue persisted to device/server storage, not in-memory
- §4: `CommandRecord` schema with `idempotency_key = tenant_id + device_id + local_seq_no`
- §7.2: Per-entity conflict resolution strategy table (Lead stage: server wins; Activity: append; Contact fields: field-level merge; Payment: reject; Task: accept-if-open)
- §8: Idempotency contract tied to global idempotency ledger

**Code reality (`services/sync/service.py`):**
- Line 17: `self._queue: deque[OfflineAction] = deque()` — in-memory only, lost on restart
- Line 19: `self._store: dict[tuple[str, str], EntityEnvelope] = {}` — in-memory entity store
- Line 13: `conflict_policy: ConflictPolicy = "last_write_wins"` — single global policy, not per-entity-type
- `_resolve_conflict()` only handles `last_write_wins` and generic `merge` — no entity-type dispatch
- `OfflineAction.action_id` uses `act_{uuid}` — not `tenant_id + device_id + local_seq_no` format from spec

**What is needed:**
- Persist queue to `sync_command_queue` table (requires GAP-003)
- Per-entity conflict resolver: dispatch on `entity_type` → strategy
- `idempotency_key` field using `(tenant_id, device_id, seq_no)` composite
- Expose `SyncService` through gateway sync endpoint (covered by GAP-015)

**Blocked by:** GAP-003 (sync DB schema)
**Blocks:** GAP-015 (sync gateway route)

---

### GAP-008
**Title:** Missing adapter registry / bootstrap factory
**Layer:** 1 | **Severity:** MEDIUM | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/pakistan-adapter-architecture.md` §6 defines:
```
CountryAdapterBundle { payment, messaging, compliance, phone, locale }
function resolveAdapters(country_code) -> CountryAdapterBundle
```
`docs/architecture-overview.md` §7 states adapters are selected by tenant/country configuration.

**Code reality:**
No `adapters/pakistan/bootstrap/` directory exists.
No factory or registry pattern. Callers must manually instantiate `JazzCashAdapter(merchant_id, secret)` inline.

**What is needed:**
- `adapters/pakistan/bootstrap/__init__.py`
- `adapters/pakistan/bootstrap/registry.py` with `resolve_adapters(country_code: str) -> CountryAdapterBundle` reading config from environment

**Blocked by:** GAP-001 (ComplianceAdapter), GAP-005 (LocaleAdapter/PhoneFormatter)
**Blocks:** nothing directly, but makes GAP-004 and GAP-006 properly wired

---

## Layer 2 — Gateway Routes (Needs L0)

The following gateway routes are missing from `gateway/routes/index.js`. Each is a separate gap and can be fixed independently of each other but all need DB schemas (GAP-002) to be meaningful.

---

### GAP-009
**Title:** No `/api/v1/leads` gateway route
**Layer:** 2 | **Severity:** CRITICAL | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/capability-matrix.md` lists Lead Management as capability #1 with owning service Lead Management Service.
`docs/api-standards.md` defines REST conventions for CRM entities.
`docs/integration-end-to-end-auto-fix.md` Flow 1 starts with lead creation.

**Code reality:**
`gateway/routes/index.js` line 37 returns 404 for any unregistered route.
No `v1-leads.routes.js` file exists.
`services/leads/service.py` exists and is functional — the service layer is ready, only the gateway route is missing.

**What is needed:**
- `gateway/routes/v1-leads.routes.js` with: `GET /leads`, `POST /leads`, `GET /leads/:id`, `PATCH /leads/:id`, `DELETE /leads/:id`
- Import and mount in `gateway/routes/index.js`
- Apply auth-rbac, idempotency, request-validation, audit-log middleware

**Blocked by:** GAP-002 (lead DB schema for persistence)
**Blocks:** end-to-end Flow 1

---

### GAP-010
**Title:** No `/api/v1/opportunities` gateway route
**Layer:** 2 | **Severity:** CRITICAL | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/opportunities-pipeline.md` defines full opportunity CRUD and stage-change API.
`docs/event-catalog.md` requires `opportunity.stage.changed.v1` and `opportunity.closed.v1` events on state transitions.

**Code reality:**
No `v1-opportunities.routes.js` exists.
`services/deals/service.py` and `services/deals/entities.py` exist and implement deal/opportunity logic.

**What is needed:**
- `gateway/routes/v1-opportunities.routes.js` with stage-change endpoint emitting canonical events
- Mount in index.js

**Blocked by:** GAP-002 (opportunity DB schema)
**Blocks:** end-to-end Flow 1 (Lead → Close)

---

### GAP-011
**Title:** No `/api/v1/followups` gateway route
**Layer:** 2 | **Severity:** CRITICAL | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/followup-enforcement-model.md` defines follow-up creation, completion, snooze, and escalation APIs.
`docs/integration-end-to-end-auto-fix.md` Flow 1 and Flow 3 both depend on follow-up APIs.

**Code reality:**
No `v1-followups.routes.js`.
`services/followup/engine.py` — `FollowupEnforcementEngine` — is fully implemented with `register_lead()`, `log_activity()`, `hourly_sweep()`.

**What is needed:**
- `gateway/routes/v1-followups.routes.js`: `POST /followups`, `PATCH /followups/:id`, `GET /followups` (with lead_id filter), `POST /followups/:id/complete`, `POST /followups/:id/snooze`

**Blocked by:** GAP-002 (lead DB schema for FK reference)
**Blocks:** Flow 1, Flow 3

---

### GAP-012
**Title:** No `/api/v1/collections` gateway route
**Layer:** 2 | **Severity:** CRITICAL | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/collections-engine-model.md` defines invoice creation, payment ingestion, reconciliation, and reminder trigger APIs.
`docs/integration-end-to-end-auto-fix.md` Flow 2 (Lead → Invoice → Payment → Reconciliation) requires collections endpoints.

**Code reality:**
No `v1-collections.routes.js`.
`services/collections/service.py` is fully implemented.

**What is needed:**
- `gateway/routes/v1-collections.routes.js`: `POST /collections/invoices`, `GET /collections/invoices/:id`, `POST /collections/invoices/:id/payments`, `POST /collections/reconcile`, `GET /collections/overdue`

**Blocked by:** GAP-002 (transaction DB already exists ✓)
**Blocks:** Flow 2

---

### GAP-013
**Title:** No WhatsApp webhook ingestion route
**Layer:** 2 | **Severity:** CRITICAL | **Complexity:** M | **State:** FIXED

**Doc says:**
`docs/whatsapp-execution-model.md` §2.1 defines the full inbound message flow starting at "Provider Webhook."
`docs/integration-contracts.md` WhatsApp Webhooks section defines four webhook endpoints:
- `POST /webhooks/whatsapp/meta`
- `POST /webhooks/whatsapp/twilio`
- `POST /webhooks/whatsapp/360dialog`
- `POST /webhooks/whatsapp/gupshup`

**Code reality:**
No webhook route file for WhatsApp at all.
`adapters/pakistan/messaging/meta_api_adapter.py` and `twilio_adapter.py` have `parse_inbound()` ready.
`services/conversation/service.py` is ready to receive parsed inbound messages.

**What is needed:**
- `gateway/routes/v1-whatsapp-webhooks.routes.js` with POST handlers for each provider
- Each handler: verify signature → call `MessagingAdapter.parse_inbound()` → route to ConversationService → return 200 immediately
- Signature verification must use stored secret per provider (no secret = reject)

**Blocked by:** GAP-006 (360dialog/Gupshup adapters for full coverage)
**Blocks:** Domain Capability #1 (WhatsApp Lead Capture), Flow 1

---

### GAP-014
**Title:** No `/api/v1/sync` gateway route for offline sync
**Layer:** 2 | **Severity:** HIGH | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/offline-sync.md` §6.2 defines sync sequence: "Device sends batch of PENDING commands → Sync Service processes."
Requires authenticated POST endpoint that accepts `CommandRecord[]`.

**Code reality:**
No sync gateway route.
`services/sync/service.py` exists but is only accessible internally.

**What is needed:**
- `gateway/routes/v1-sync.routes.js`: `POST /sync/batch` (accepts command array), `GET /sync/status` (returns queue status for device)
- Must enforce idempotency per command via global ledger

**Blocked by:** GAP-007 (sync service persistence), GAP-002 (sync schema)
**Blocks:** Flow 4 (Offline → Sync → Consistent State)

---

### GAP-015
**Title:** Auth RBAC middleware has no defined scope registry
**Layer:** 2 | **Severity:** MEDIUM | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/identity-auth-rbac.md` defines 6 roles and their permissions. Roles: `tenant_owner`, `tenant_admin`, `manager`, `agent`, `analyst`, `auditor`, `integration_service`.
`docs/security-model.md` requires default-deny and least-privilege enforcement.

**Code reality:**
`gateway/middleware/auth-rbac.js` validates Bearer tokens and checks `scope`/`role` from JWT claims, but:
- No canonical scope list defined anywhere in gateway code
- Route handlers must hardcode `requiredScopes: ['lead:read']` etc. but these strings are not defined in a registry
- No role-to-allowed-scopes mapping exists; roles and scopes are independent unvalidated strings

**What is needed:**
- `gateway/config/rbac-scopes.js` defining the canonical scope list and role-to-scope mapping
- Auth middleware updated to validate scope against registry on each request

**Blocked by:** GAP-002 (identity DB schema to store roles)
**Blocks:** all route handlers needing proper permission enforcement

---

## Layer 3 — Hardening & Observability (Needs L1 + L2)

---

### GAP-016
**Title:** `GlobalIdempotencyLedger` is in-memory — no TTL expiry, no cross-process sharing
**Layer:** 3 | **Severity:** HIGH | **Complexity:** M | **State:** FIXED

**Doc says:**
`docs/global-idempotency.md` requires: "Deduplication window: 24 hours minimum. Scope: (tenant_id, http_method, canonical_route, idempotency_key). Must survive process restarts."

**Code reality:**
`services/core/execution/idempotency.py` — `GlobalIdempotencyLedger` uses `self._records: dict` in-memory.
- No TTL / expiry of old records (memory grows unboundedly)
- Dies on process restart (all deduplication state lost)
- Cannot share state across multiple gateway instances (not horizontally scalable)

**What is needed:**
- Back the ledger with Redis (or the existing `message_idempotency` table pattern from `db/messaging_db/schema.sql`)
- Add TTL enforcement (remove records older than 24h)
- Keep in-memory as L1 cache; Redis/DB as durable L2

**Blocked by:** GAP-002 (for DB-backed option)
**Blocks:** nothing, but production correctness requires this

---

### GAP-017
**Title:** `ActivityControlEngine` missing hash-chain verification
**Layer:** 3 | **Severity:** MEDIUM | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/activity-control-model.md` states: "Immutable chain with hash verification. Activity emitted on every CRM entity action."
`docs/observability-audit.md`: "Append-time hash-chain verification."
`docs/system-hardening-auto-fix.md` lists hash-chain verification as an applied fix.

**Code reality:**
`services/activity/engine.py` — activities are append-only (correct) but no hash field is computed or verified.
Activity records have no `prev_hash` or `chain_hash` field.

**What is needed:**
- Add `hash` and `prev_hash` fields to activity entity
- On `log_activity()`, compute `sha256(prev_hash + activity_payload)` and store
- On audit read, verify chain integrity from genesis entry

**Blocked by:** GAP-002 (identity and audit DB schemas)
**Blocks:** nothing, but audit immutability guarantee is unmet

---

### GAP-018
**Title:** No Unit-of-Work implementations for critical ACID boundaries
**Layer:** 3 | **Severity:** MEDIUM | **Complexity:** M | **State:** FIXED

**Doc says:**
`docs/execution-hardening.md` §2 specifies explicit Unit-of-Work contracts for:
- `create_subscription_with_invoice_uow` — subscription + invoice as atomic operation
- `advance_payment_status_uow` — payment status transition + ledger update atomic
- `record_payment_event_uow` — payment event ingest + dedup + outbox publish atomic

**Code reality:**
`services/core/execution/transactions.py` exists but contains only basic transaction wrapper — no named UoW implementations.
`services/collections/service.py` does not use explicit UoW for payment ingestion.

**What is needed:**
- Named UoW functions in `services/core/execution/transactions.py` for the three critical boundaries above
- `services/collections/service.py` to call `record_payment_event_uow` when ingesting payment webhooks

**Blocked by:** GAP-002 (schemas for proper DB transactions)
**Blocks:** nothing, but ACID safety on financial operations is not guaranteed

---

### GAP-019
**Title:** JazzCash/Easypaisa webhook route endpoints not wired into gateway
**Layer:** 3 | **Severity:** HIGH | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/integration-contracts.md` Pakistan Payments Webhooks defines:
- `POST /webhooks/payments/jazzcash` — with `pp_SecureHash` HMAC verification
- `POST /webhooks/payments/easypaisa` — with HMAC signature field verification

**Code reality:**
`adapters/pakistan/payments/base.py` has `parse_webhook()` with signature verification.
No gateway route exists to receive these webhooks.
`services/collections/service.py` has `ingest_payment()` ready to process normalized events.

**What is needed:**
- `gateway/routes/v1-payment-webhooks.routes.js` with POST handlers for each provider
- Each handler: verify HMAC → call `PaymentAdapter.parse_webhook()` → call `CollectionsService.ingest_payment()` → return 200

**Blocked by:** nothing (adapters are ready)
**Blocks:** Flow 2 (payment webhook → reconciliation)

---

### GAP-020
**Title:** FollowupEnforcementEngine escalation ladder is implicit — 4 levels not enumerated in code
**Layer:** 3 | **Severity:** LOW | **Complexity:** S | **State:** FIXED

**Doc says:**
`docs/followup-enforcement-model.md` specifies a "4-level escalation ladder" with explicit level definitions and actions at each level.

**Code reality:**
`services/followup/engine.py` — `hourly_sweep()` handles escalation via `EscalationLevel` enum but the four levels and their specific actions (notify → alert manager → reassign → block close) are not explicitly enumerated with named constants or config.

**What is needed:**
- Explicit `ESCALATION_LADDER: list[EscalationConfig]` in `services/followup/entities.py` with level number, threshold, action type, and notification target
- `hourly_sweep()` to iterate ladder config rather than implicit conditionals

**Blocked by:** nothing
**Blocks:** nothing, but observability of escalation level is degraded

---

## Summary Table

| ID | Title | Layer | Severity | Complexity | State | Blocked By |
|---|---|---|---|---|---|---|
| GAP-001 | Missing ComplianceAdapter interface | 0 | HIGH | S | FIXED | — |
| GAP-002 | Missing 10 DB schemas | 0 | CRITICAL | L | FIXED | — |
| GAP-003 | messaging_db missing sync/template/dead-letter tables | 0 | MEDIUM | S | FIXED | — |
| GAP-004 | Pakistan payment adapters in-memory only | 0 | MEDIUM | M | FIXED | — |
| GAP-005 | Missing LocaleAdapter and PhoneFormatter | 0 | LOW | S | FIXED | — |
| GAP-006 | Missing 360dialog and Gupshup adapters | 1 | CRITICAL | M | FIXED | — |
| GAP-007 | SyncService in-memory, no per-entity conflict strategy | 1 | HIGH | M | FIXED | GAP-003 |
| GAP-008 | Missing adapter registry / bootstrap | 1 | MEDIUM | S | FIXED | GAP-001, GAP-005 |
| GAP-009 | No `/api/v1/leads` route | 2 | CRITICAL | S | FIXED | GAP-002 |
| GAP-010 | No `/api/v1/opportunities` route | 2 | CRITICAL | S | FIXED | GAP-002 |
| GAP-011 | No `/api/v1/followups` route | 2 | CRITICAL | S | FIXED | GAP-002 |
| GAP-012 | No `/api/v1/collections` route | 2 | CRITICAL | S | FIXED | — |
| GAP-013 | No WhatsApp webhook ingestion route | 2 | CRITICAL | M | FIXED | GAP-006 |
| GAP-014 | No `/api/v1/sync` route | 2 | HIGH | S | FIXED | GAP-007 |
| GAP-015 | No RBAC scope registry | 2 | MEDIUM | S | FIXED | GAP-002 |
| GAP-016 | IdempotencyLedger in-memory, no TTL | 3 | HIGH | M | FIXED | GAP-002 |
| GAP-017 | Activity log missing hash-chain verification | 3 | MEDIUM | S | FIXED | GAP-002 |
| GAP-018 | No ACID Unit-of-Work implementations | 3 | MEDIUM | M | FIXED | GAP-002 |
| GAP-019 | Pakistan payment webhook routes missing | 3 | HIGH | S | FIXED | — |
| GAP-020 | Escalation ladder implicit, not enumerated | 3 | LOW | S | FIXED | — |

---

## Fix Order (Dependency-Resolved)

```
Round 1 (no blockers, do in parallel):
  GAP-001  ComplianceAdapter interface
  GAP-002  All missing DB schemas
  GAP-003  messaging_db additions
  GAP-004  Payment adapter real API calls
  GAP-005  LocaleAdapter + PhoneFormatter
  GAP-006  360dialog + Gupshup adapters
  GAP-019  Payment webhook gateway routes
  GAP-020  Escalation ladder enumeration

Round 2 (needs Round 1):
  GAP-007  SyncService persistence + per-entity conflict
  GAP-008  Adapter registry / bootstrap

Round 3 (needs Round 2 or GAP-002):
  GAP-009  Leads route
  GAP-010  Opportunities route
  GAP-011  Followups route
  GAP-012  Collections route
  GAP-013  WhatsApp webhook routes
  GAP-014  Sync route
  GAP-015  RBAC scope registry

Round 4 (needs Round 3):
  GAP-016  Idempotency persistence
  GAP-017  Activity hash-chain
  GAP-018  ACID UoW transactions
```

---

## What Is Already Correct

The following areas are implemented and match their docs — do not touch without a reason:

| Area | Files | Status |
|---|---|---|
| `MessagingAdapter` interface | `adapters/interfaces/messaging_adapter.py` | Matches doc spec exactly, includes `parse_inbound` |
| `PaymentAdapter` interface | `adapters/interfaces/payment_adapter.py` | Matches doc spec exactly |
| `PakistanPaymentAdapter` base | `adapters/pakistan/payments/base.py` | Full Protocol implementation; in-memory store only issue (GAP-004) |
| `FollowupEnforcementEngine` | `services/followup/engine.py` | Implemented; minor ladder config gap (GAP-020) |
| `GlobalIdempotencyLedger` | `services/core/execution/idempotency.py` | Correct scope key `(tenant, method, route, key)`; in-memory only (GAP-016) |
| Retry with backoff | `services/core/execution/retry.py` | Matches execution-hardening.md spec |
| OCC + distributed locks | `src/execution_hardening/concurrency.py` | Matches concurrency-control.md |
| Gateway idempotency middleware | `gateway/middleware/idempotency.js` | Correct; uses SHA-256 body hash for payload drift detection |
| `ActivityControlEngine` | `services/activity/engine.py` | Append-only, correct; hash-chain missing (GAP-017) |
| `CollectionsService` | `services/collections/service.py` | Fully implemented, integrates with payment adapters |
| `ActivationEngine` | `services/activation/service.py` | Matches activation-model.md spec |
| `ConversationService` | `services/conversation/service.py` | Matches whatsapp-execution-model.md |
| Activity + Transaction DB schemas | `db/activity_task_db/`, `db/transaction_db/` | Match domain-model.md |
| Messaging DB schema | `db/messaging_db/schema.sql` | Core tables correct; additions needed (GAP-003) |
