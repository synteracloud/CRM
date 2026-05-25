<!-- OWNERSHIP
PRIMARY FOR: Retry policy (exponential backoff: 1s base, 2× multiplier, ±20% jitter, 60s max); DLQ behaviour and drain procedures; VersionedRecord and LockLease overlay entities.
DEFERS TO: global-idempotency.md (idempotency 4-tuple); data-architecture.md (transactional outbox — primary); concurrency-control.md (full OCC and locking taxonomy).
DO NOT RE-DEFINE: Idempotency 4-tuple → global-idempotency.md §1.1; transactional outbox steps → data-architecture.md §3.1; OCC full spec → concurrency-control.md.
-->

# B0-P01::EXECUTION_HARDENING_DOC

## Purpose
This document defines the execution hardening model for critical CRM flows with explicit, testable guarantees for:
- ACID transaction boundaries.
- Idempotent command processing.
- Retry and rollback behavior.
- Concurrency control and lock acquisition.
- Failure recovery and operator runbooks.

The target is deterministic behavior under duplicate delivery, partial outages, and high contention without data corruption.

## Scope: critical flows
The following flows are **in scope** and must comply with every section of this document:
1. Quote acceptance → order creation.
2. Subscription create/upgrade/renew/cancel with invoice generation.
3. Payment event ingest and payment status advancement.
4. Workflow transition execution that mutates durable state.
5. Scheduler-based replay/recovery of stalled or dead-lettered jobs.

If a new flow introduces external side effects (payment capture, irreversible fulfillment, customer-visible state transition), it must be added to this list before release.

---

## 1) ACID boundaries

### 1.1 Unit-of-work (UoW) rule
Any operation that changes more than one persistence artifact (primary row, ledger row, outbox row, idempotency row, or workflow state) must execute inside a **single database transaction**.

### 1.2 Canonical UoWs (must be used)
The following server-side UoWs are authoritative and must not be bypassed:
- `create_subscription_with_invoice_uow`
- `advance_payment_status_uow`
- `record_payment_event_uow`

### 1.3 Boundary definition
Each UoW must:
- Begin transaction.
- Validate invariants and preconditions.
- Apply all state mutations.
- Write outbox events (if needed for async propagation) within the same transaction.
- Commit once; otherwise rollback all mutations.

### 1.4 Isolation and consistency
- Default isolation: `READ COMMITTED` with explicit row locks where required.
- Use `SELECT ... FOR UPDATE` on irreversible transitions or high-contention state rows.
- No side effects outside transaction before commit (no webhook dispatch, no external call that cannot be reversed).

### 1.5 Non-negotiable invariant
**No partial success** is allowed for a critical flow: either all durable writes commit, or none do.

---

## 2) Idempotency strategy

### 2.1 Global key contract
Idempotency scope is keyed by:
`(tenant_id, http_method, canonical_route, idempotency_key)`

### 2.2 Payload drift protection
For a repeated idempotency key:
- If payload hash matches: return prior successful response/result.
- If payload hash differs: reject with deterministic conflict error `idempotency_key_reused_with_different_payload`.

### 2.3 Storage model
Each idempotent command stores:
- key tuple (tenant/method/route/key),
- canonical payload hash,
- terminal status (`succeeded`/`failed_non_retryable`),
- response envelope reference,
- first-seen and last-seen timestamps.

### 2.4 TTL and retention
- Minimum retention: long enough to cover worst-case client retry windows and asynchronous redelivery windows.
- Expiry process must never delete records still referenced by in-flight recovery jobs.

### 2.5 External side effects
Any side effect adapter (payment, webhook, external API) must use:
- upstream idempotency token if provider supports it,
- or local dedupe ledger keyed by provider + operation + domain object + nonce.

---

## 3) Retry and rollback model

### 3.1 Error taxonomy
Errors must be classified into exactly one category:
1. **Retryable-transient** (timeouts, lock timeout, temporary dependency outage).
2. **Retryable-contention** (deadlock victim, optimistic version conflict under policy).
3. **Non-retryable-business** (validation/invariant failures).
4. **Non-retryable-system** (schema mismatch, serialization contract violation).

### 3.2 Retry policy
- Exponential backoff with jitter.
- Upper bound enforced: `retry_policy.backoff_seconds` cannot exceed `max_backoff_seconds`.
- Bounded attempts per job/command.
- Retry decision is deterministic from error taxonomy and attempt count.

**Default retry backoff values:**
- Initial delay: 1 second.
- Multiplier: 2x per attempt.
- Jitter: ±20% uniform jitter applied to each delay (prevents thundering herd).
- Maximum delay: 60 seconds.
- Maximum attempts: 8 (configurable per job type).

Example backoff sequence (with jitter): 1s, 2s, 4s, 8s, 16s, 32s, 60s, 60s.

### 3.3 Rollback policy
- Any exception before commit → immediate transaction rollback.
- Post-commit failures in async dispatch are handled by outbox replay, not transaction rewind.
- Compensating transactions are required for irreversible external effects when downstream stage fails after commit.

### 3.4 Idempotent retry guarantee
A retried command must be safe to execute N times and produce one of:
- exactly one committed state transition, or
- one stable non-retryable failure state.

No duplicate charge/order/subscription mutation is allowed.

---

## 4) Concurrency and locking

### 4.1 Baseline: optimistic concurrency control (OCC)
Mutable domain aggregates must carry `version_no`.
Write contract:
- Update where `id = ? AND version_no = expected`.
- On mismatch return `STALE_VERSION` conflict.
- Caller must refresh and reapply intent (not blind overwrite).

### 4.2 Pessimistic locking use cases
Use `FOR UPDATE` when both are true:
- operation is irreversible or high-value,
- conflict probability is high enough that OCC churn is unsafe/expensive.

Examples:
- Quote acceptance finalization.
- Payment status transitions around capture/refund boundary.
- Scheduler claim of exclusive recovery ownership.

**Escalation threshold:** Escalate from OCC to pessimistic when either condition is met:
- OCC retry rate for a given operation exceeds 15% of total attempts over a 5-minute window (measured via `stale_version_retries_total` metric).
- Operation p95 latency exceeds 3× the expected baseline due to OCC churn.

These thresholds are monitored via the observability dashboard. Escalation is a configuration change in the service, not a runtime switch.

### 4.3 Distributed lock policy
For cross-process exclusivity across workers/nodes:
- Acquire lock before critical section.
- Lock key must include tenant and domain object identity.
- Use finite lease + heartbeat/renewal.
- Enforce fencing token (or monotonic owner epoch) on write path.
- Release on success/failure; rely on lease expiry for crash safety.

Protected operations include:
- Quote acceptance → order creation transition.
- Single-owner replay of dead-letter batches.
- Subscription renewal batch per tenant-period shard.

**Checkpoint semantics for long-running operations:**
When an operation approaches the 15-minute maximum cumulative lease age, it must:
1. Persist current progress state to durable storage (e.g., `last_processed_cursor` on the job record).
2. Release the current lock.
3. Re-acquire the lock using the same lock key.
4. Resume from the persisted checkpoint.

If re-acquisition fails (lock held by another process), the operation exits. The scheduler will restart it from the last persisted checkpoint. Operations must be idempotent from any checkpoint.

### 4.4 Lock ordering and deadlock prevention
- Global lock acquisition order must be documented and stable.
- If multiple resource locks are needed, acquire by canonical sorted key.
- Timeout + retry on deadlock victims under bounded policy.

---

## 5) Failure recovery

### 5.1 Outbox and replay
- Domain commit writes outbox entry in same transaction.
- Dispatcher delivers outbox asynchronously.
- On dispatch failure, item remains replayable until success or dead-letter threshold reached.

### 5.2 Scheduler states
Recovery scheduler must support:
- `pending`
- `in_progress`
- `succeeded`
- `failed_retryable`
- `dead_lettered`

State transitions must be monotonic and auditable.

### 5.3 Replay safety rules
Before replaying a failed item:
- Re-check idempotency ledger.
- Verify domain object still eligible for transition.
- Reject stale replay attempts that would violate current version/state.

### 5.4 Dead-letter handling
For `dead_lettered` items:
- Persist failure reason, attempt history, and last stack/context snapshot.
- Expose operator action set: retry now, requeue with override, cancel with reason.
- Require explicit audit record for manual overrides.

**Operator action API contract:**

| Action | Endpoint | Auth required | Audit event |
|---|---|---|---|
| Retry dead-lettered item | `POST /api/v1/admin/dead-letters/{item_id}/retry` | `platform.ops.write` | `dead_letter.retry_requested` |
| Requeue with override | `POST /api/v1/admin/dead-letters/{item_id}/requeue` + `{ override_reason: string }` | `platform.ops.write` | `dead_letter.requeue_override` |
| Cancel with reason | `POST /api/v1/admin/dead-letters/{item_id}/cancel` + `{ cancel_reason: string }` | `platform.ops.write` | `dead_letter.cancelled` |

All actions require `override_reason` or `cancel_reason` (non-empty string). Audit record includes actor, tenant, item_id, action, reason, and timestamp.

### 5.5 Crash recovery
On worker restart:
- Reclaim abandoned `in_progress` tasks only after lease timeout.
- Ensure at-most-one active owner via distributed lock or atomic claim.
- Resume retries with preserved attempt counters.

---

## 6) End-to-end critical flow guarantees

### 6.1 Quote acceptance → order creation
Guarantees:
- Single accepted outcome per quote version.
- Duplicate requests return same committed order or deterministic conflict.
- No order exists without corresponding accepted quote state.

### 6.2 Subscription + invoice UoW
Guarantees:
- Subscription mutation and invoice creation commit atomically.
- Retry cannot generate duplicate invoice for same billing event.
- Failed mutation leaves prior subscription state intact.

### 6.3 Payment event ingest + status advancement
Guarantees:
- Duplicate provider events are deduplicated.
- Payload drift under same idempotency key is rejected.
- Status transitions are monotonic and lock-protected where irreversible.

### 6.4 Workflow transition execution
Guarantees:
- Transition preconditions evaluated inside transaction boundary.
- Concurrent transitions resolve by OCC or explicit lock policy.
- Retries preserve single logical transition outcome.

### 6.5 Recovery replay pipeline
Guarantees:
- Replay is idempotent and safe after partial prior progress.
- Dead-letter threshold is deterministic.
- Manual intervention path is fully auditable.

---

## 7) Verification gates (must pass)
1. ACID boundary policy implemented for all critical UoWs.
2. Idempotency conflict detection blocks payload drift.
3. Retry policy is bounded and deterministic.
4. Rollback semantics guarantee no partial commit.
5. OCC and `STALE_VERSION` path enforced on mutable aggregates.
6. `FOR UPDATE` used on declared irreversible/high-contention paths.
7. Distributed lock strategy protects listed cross-worker operations.
8. Recovery scheduler supports `dead_lettered` with replay safety checks.
9. Operator overrides produce immutable audit trails.
10. End-to-end QC score remains 10/10 after fix → re-fix loop.

---

## 8) Fix → re-fix enforcement loop
To enforce hardening quality without ambiguity:
1. **Fix**: implement the smallest safe change for failed gate(s).
2. **Re-fix**: if any gate still fails, apply corrective patch immediately.
3. **Re-run QC**: execute execution-hardening QC until score is 10/10.
4. **Block release** unless all 10 gates pass in the same run.

Recommended command:
- `PYTHONPATH=. python3 scripts/self_qc_execution_hardening.py`

Pass criterion:
- Output must be exactly `Self-QC score: 10/10`.

---

## Concurrency Control Implementation Entities

*Added from src/execution_hardening overlay — 2026-04-02*

### VersionedRecord

Immutable record with OCC version tracking and last fencing token.

| Field | Notes |
|---|---|
| `key` | Record identifier |
| `value` | Record payload dict |
| `version_no` | Monotonically increasing version; starts at 1 |
| `last_fencing_token` | Last accepted fencing token for this record |

**OCC check:** Write must supply `expected_version_no == current.version_no`; mismatch raises `StaleVersionError`.

### LockLease

Finite-lease distributed lock with fencing token.

| Field | Notes |
|---|---|
| `key` | Lock resource key |
| `owner_id` | Lock holder identifier |
| `fencing_token` | Monotonically increasing token; stale writers rejected |
| `expires_at_monotonic` | Lease expiry (monotonic clock float) |

**Fencing rule:** Any write using an expired or stale `fencing_token < record.last_fencing_token` raises `FencingTokenError`.

### Error Classes

| Class | Trigger |
|---|---|
| `StaleVersionError` | OCC detects stale `expected_version_no` |
| `LockAcquisitionTimeout` | Lock not available within `wait_timeout_seconds` |
| `LockOwnershipError` | Renew/release attempted by non-owner or after expiry |
| `FencingTokenError` | Stale fencing token attempts to write |

### Multi-Lock Canonical Ordering

When acquiring multiple locks simultaneously, keys are **sorted alphabetically** before acquisition. This prevents deadlocks from interleaved acquisition order across concurrent threads/processes.
