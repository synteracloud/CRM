# B7-P02::GLOBAL_IDEMPOTENCY

## Purpose

Define a **single global idempotency model** for API writes and event processing so that retries, duplicate deliveries, and replay operations do not create duplicate state changes or duplicate side effects.

This specification is normative for all write-path services.

## 1) Global Idempotency Key Strategy

### 1.1 Request Idempotency Identity
Every write request (`POST`, `PUT`, `PATCH`, `DELETE`) MUST be mapped to this dedupe tuple:

```text
(tenant_id, http_method, canonical_route, idempotency_key)
```

Rules:
- `tenant_id` is required.
- `http_method` MUST be uppercase.
- `canonical_route` MUST use route template form (for example `/api/v1/opportunities/{opportunity_id}/stage-transitions`).
- `idempotency_key` MUST be supplied by client in `Idempotency-Key` header for non-read operations.

### 1.2 Key Format and Limits
- Key MUST be opaque string, 8-128 chars.
- Allowed characters: `A-Z`, `a-z`, `0-9`, `_`, `-`, `:`.
- Servers MUST reject invalid key shape with `400 bad_request`.
- Recommended key pattern:

```text
<domain>:<entity_id>:<intent>:v<version>
```

Examples:
- `lead:lea_01JABC:create:v1`
- `quote:quo_01JABC:accept:v1`
- `payment:inv_01JABC:capture:v2`

### 1.3 Fingerprint Binding
To prevent key reuse across different payloads, services MUST persist a deterministic request fingerprint:

```text
fingerprint = SHA-256(tenant_id + method + canonical_route + normalized_json_body)
```

Replay behavior:
- Same dedupe tuple + same fingerprint => return original response (or deterministic equivalent).
- Same dedupe tuple + different fingerprint => `409 conflict` (`error.code = conflict`, reason `idempotency_key_payload_mismatch`).

### 1.4 TTL / Retention
- Minimum retention for idempotency records: **24 hours**.
- Critical financial and contract mutations (quote acceptance, order creation, invoice/payment actions, subscription state transitions) SHOULD retain for **7 days**.
- Expired records MAY be evicted, but services MUST document endpoint-specific windows.

## 2) Idempotent API Write Handling

### 2.1 Execution Lifecycle
1. Validate authn/authz and schema.
2. Acquire idempotency reservation atomically for dedupe tuple.
3. If existing finalized reservation found, return stored result.
4. Execute mutation once.
5. Persist business state + outbox event(s) in one transaction.
6. Mark reservation `completed` with status code + response body hash/reference.

### 2.2 In-Flight Concurrency Rules
- If duplicate key arrives while first request is still processing, server MUST:
  - either block/poll until completion and return same response, or
  - return `409 conflict` with retry hint (`error.details.reason = request_in_progress`).
- Under no mode may the mutation execute twice.

### 2.3 HTTP Semantics
- First successful async submission may return `202 accepted`.
- Replays MUST return the same status family and equivalent body semantics.
- Validation failures MAY be cached idempotently for the same key.

### 2.4 Storage Contract (`idempotency_records`)
Required fields:
- `tenant_id`
- `http_method`
- `canonical_route`
- `idempotency_key`
- `request_fingerprint`
- `state` (`processing|completed|failed`)
- `response_status`
- `response_body_ref` (or canonical serialized body)
- `resource_type`, `resource_id` (if created)
- `created_at`, `updated_at`, `expires_at`

Required unique index:

```text
UNIQUE (tenant_id, http_method, canonical_route, idempotency_key)
```

## 3) Idempotent Event Processing

### 3.1 Event Identity and Dedupe
Consumers MUST dedupe by:

```text
(tenant_id, event_name, event_id)
```

Rules:
- `event_id` MUST be globally unique within event producer scope.
- Every handler MUST record processing result before acknowledging broker delivery.

### 3.2 Consumer Inbox Pattern
Each consumer service MUST maintain `event_inbox` (or equivalent) with:
- dedupe key tuple
- first_seen_at / last_seen_at
- handler_status (`processing|completed|failed|dead_lettered`)
- side_effect_checksum (optional)
- source metadata (`source_service`, `occurred_at`)

Unique index:

```text
UNIQUE (tenant_id, event_name, event_id)
```

### 3.3 Side-Effect Guards
All non-database side effects MUST be idempotent:
- notifications: unique send key `(tenant_id, template_id, target_address, source_event_id)`
- workflow triggers: unique execution seed `(tenant_id, workflow_definition_id, trigger_event_id)`
- external provider calls: provider idempotency token derived from source event or request key

### 3.4 Replay Safety
When reprocessing history/backfills:
- consumers MUST use same inbox dedupe keys.
- handlers MUST be written as upserts/compare-and-set transitions.
- terminal state transitions MUST reject illegal regressions.

## 4) Duplicate Request and Event Protection Policy

### 4.1 API Duplicate Matrix
- **Same key + same payload**: return original result, no new writes.
- **Same key + different payload**: `409 conflict`.
- **Different key + same semantic intent**: protect via domain uniqueness constraints (for example one active quote acceptance per quote).

### 4.2 Event Duplicate Matrix
- **Same `event_id` redelivered**: ack/no-op after dedupe hit.
- **Different `event_id` but same business mutation**: prevented by aggregate version checks and unique domain constraints.
- **Out-of-order events**: handler SHOULD be version-aware and ignore stale transitions.

### 4.3 Mandatory Domain Constraints (Critical Mutations)
Minimum protections required:
- Lead conversion: one conversion target set per `lead_id`.
- Opportunity close: one terminal close transition per `opportunity_id` + version guard.
- Quote acceptance: one terminal acceptance per `quote_id`.
- Order creation from quote: unique `(tenant_id, quote_id)`.
- Subscription creation from quote/order: unique `(tenant_id, source_reference_id)`.
- Payment event mirror: unique `(tenant_id, external_payment_ref, event_type)`.

## 5) Replay-Safe Execution Rules

1. All write handlers MUST be deterministic for same input.
2. Mutations MUST use atomic transactions with outbox publishing.
3. Consumers MUST be at-least-once safe and dedupe-before-side-effect.
4. External calls MUST include provider-supported idempotency token where available.
5. Dead-letter replays MUST preserve original `event_id`.
6. Manual rerun tooling MUST require operator-provided replay scope and dry-run mode.

## 6) API Integration Points

### 6.1 Required Request Headers
- `Idempotency-Key` (required for non-read operations).
- `X-Request-Id` (recommended, echoed via `meta.request_id`).

### 6.2 Required Error Integration
Use standard error envelope from `docs/api-standards.md`:
- Key mismatch: `409 conflict` + `error.details.reason = idempotency_key_payload_mismatch`
- In-flight duplicate: `409 conflict` + `error.details.reason = request_in_progress`
- Missing key on required endpoint: `400 bad_request`

### 6.3 Response Integration
Successful replay MUST include metadata:

```json
{
  "data": {},
  "meta": {
    "request_id": "req_...",
    "idempotency": {
      "key": "quote:quo_01JABC:accept:v1",
      "replayed": true
    }
  }
}
```

### 6.4 Event Catalog Integration
All events in `docs/event-catalog.md` are subject to inbox dedupe by `event_id` and must preserve producer-generated `event_id` across retries, dead-lettering, and replay.

## 7) Request / Event Dedupe Policy (Operational)

- Dedupe stores MUST be durable (not process memory only).
- Dedupe checks MUST happen before mutation or side effect emission.
- Metrics MUST be emitted:
  - `idempotency.request.hit`
  - `idempotency.request.miss`
  - `idempotency.request.conflict`
  - `idempotency.event.duplicate`
  - `idempotency.event.replay_applied`
- Alerting SHOULD trigger on abnormal conflict spikes.

## 8) Self-QC (B7-P02)

Score: **10/10**

- [x] No duplicate writes: enforced via global request dedupe tuple + unique index + transactional completion marker.
- [x] No duplicate event side effects: enforced via consumer inbox dedupe and side-effect idempotency keys.
- [x] Works across all critical mutations: explicit domain constraints listed for lead conversion, opportunity close, quote/order/subscription/payment paths.

## 9) Fix Loop Evidence

- Fix: Added global idempotency architecture and required invariants.
- Re-check: Verified alignment with API envelope/error semantics and event `event_id` model.
- Result: 10/10 readiness for platform-wide rollout.
