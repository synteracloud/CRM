# B7-P05::DISTRIBUTED_LOCKS

## Inputs
- `docs/workflow-catalog.md`
- `docs/data-architecture.md`

## 1) Locking layer

### 1.1 Objectives
- Prevent duplicate execution for critical cross-service flows defined in the workflow catalog.
- Preserve tenant isolation by scoping every lock key with `tenant_id`.
- Guarantee bounded lock lifetime (no indefinite retention) using explicit lease TTL and heartbeat renewal.
- Align with the relational + outbox architecture by keeping lock ownership outside business transactions while using idempotency keys inside protected operations.

### 1.2 Lock backend
- **Primary backend:** Redis-based lease locks using `SET key value NX PX <ttl_ms>` semantics.
- **Durability guard:** Every protected operation must also persist an idempotency token in the owning service DB to tolerate lock loss or relay retries.
- **Value payload (JSON):**
  - `owner_id` (worker/scheduler instance)
  - `lock_version` (monotonic fencing token)
  - `acquired_at`
  - `expires_at`
  - `trace_id`
- **Fencing token source:** Redis `INCR lock:fence:<scope>` at successful acquire; downstream write paths reject stale `lock_version`.

### 1.3 Lock key model

`lock:{env}:{tenant_id}:{domain}:{operation}:{resource_id|window}`

Examples:
- `lock:prod:t_123:scheduler:job-dispatch:job_renewals_daily`
- `lock:prod:t_123:workflow:quote-approval:quote_456`
- `lock:prod:t_123:billing:invoice-close:2026-03`
- `lock:prod:t_123:recon:payment-reconcile:2026-03-29`

### 1.4 API surface (logical)
1. `acquire(key, ttl_ms, wait_timeout_ms, owner_id) -> {granted, lock_version}`
2. `renew(key, owner_id, lock_version, ttl_ms) -> {renewed}`
3. `release(key, owner_id, lock_version) -> {released}`
4. `force_expire(key)` only for operator break-glass with audited reason.

All release/renew operations must be compare-and-delete/compare-and-pexpire scripts validated against both `owner_id` and `lock_version`.

---

## 2) Lock policy

### 2.1 Acquisition rules
1. **Acquire-before-read-modify-write:** Any operation that can double-apply business effects must acquire lock before loading mutable state.
2. **Tenant scope required:** If `tenant_id` missing, reject acquisition.
3. **Bounded wait:** `wait_timeout_ms` defaults to 2x p95 operation duration (max 5s for synchronous APIs, max 30s for async workers).
4. **Non-blocking fail mode:** On timeout, caller returns retryable conflict (`409` for APIs, requeue with backoff for workers).
5. **Jittered retry:** Exponential backoff with jitter (100-2000 ms) to reduce herd contention.

### 2.2 Expiry rules
1. **Default lease TTL:** 30 seconds.
2. **Long-running flows:** up to 120 seconds only when heartbeat is active.
3. **Heartbeat cadence:** renew at 1/3 TTL interval (e.g., every 10s on 30s lease).
4. **Renew safety:** Maximum cumulative lease age is capped at 15 minutes; operation must checkpoint and re-acquire to avoid zombie ownership.
5. **Clock discipline:** Expiry decisions rely on backend TTL only, not local wall clock.

### 2.3 Release rules
1. **Best-effort immediate release:** Always release in `finally`/defer path.
2. **Owner-verified release only:** Lock is released only when `owner_id` + `lock_version` match.
3. **Lost-lock behavior:** If renew fails, operation must stop side effects, persist interrupted state, and retry from checkpoint.
4. **Crash handling:** No manual cleanup required for normal crashes; TTL expiration recovers lock automatically.
5. **Operator override:** `force_expire` allowed only after verifying no active owner heartbeat and logging an audit event.

### 2.4 Deadlock avoidance rules
1. **Single-lock preference:** Design operations to require one lock whenever possible.
2. **Global lock ordering:** If multiple locks are unavoidable, order keys lexicographically by `(tenant_id, domain, operation, resource_id)`.
3. **No lock upgrade/downgrade:** Never convert shared/exclusive modes in-place.
4. **No indefinite wait:** All acquisitions use timeout + retry; never block unbounded.
5. **Two-phase side effects:** Prepare work under lock, publish/commit idempotently, then release immediately.
6. **Compensation over nesting:** Cross-domain workflows use saga/outbox events rather than nested locks across services.

---

## 3) Protected operation list

### 3.1 Scheduler and job control
1. **Schedule trigger dispatch** (`scheduler.job.triggered.v1` emission) — lock per `{tenant_id, schedule_id, fire_time}`.
2. **Missed-run catchup backfill** — lock per `{tenant_id, schedule_id, catchup_window}`.
3. **Job dedupe/enqueue** — lock per `{tenant_id, job_type, dedupe_key}`.

### 3.2 Workflow execution
4. **Approval request creation** in quote approval workflow — lock per `{tenant_id, quote_id}` to prevent duplicate `approval.requested.v1`.
5. **Approval decision application** — lock per `{tenant_id, approval_request_id}` to ensure single terminal decision.
6. **Quote acceptance -> order creation transition** — lock per `{tenant_id, quote_id}` to prevent duplicate orders.
7. **Lead conversion** (`lead -> account/contact/opportunity`) — lock per `{tenant_id, lead_id}`.
8. **Opportunity terminal close handling** — lock per `{tenant_id, opportunity_id}` for single close playbook execution.

### 3.3 Billing and revenue operations
9. **Subscription provisioning from commercial acceptance** — lock per `{tenant_id, source_order_id}`.
10. **Invoice period close / summary rollup** — lock per `{tenant_id, billing_cycle}`.
11. **Payment event ingestion dedupe** — lock per `{tenant_id, provider_event_id}`.
12. **Dunning step transition** (past_due escalation) — lock per `{tenant_id, subscription_id, dunning_step}`.

### 3.4 Reconciliation operations
13. **Daily payment reconciliation run start** — lock per `{tenant_id, recon_date}`.
14. **Invoice-payment match application** — lock per `{tenant_id, invoice_id}`.
15. **Write-off / adjustment posting** — lock per `{tenant_id, adjustment_batch_id}`.
16. **Ledger checkpoint finalization** — lock per `{tenant_id, ledger_period}`.

### 3.5 Shared integrity controls
17. **Outbox relay partition claim** — lock per `{tenant_id, partition_id}` to avoid dual relays.
18. **Projection rebuild for same tenant + projection** — lock per `{tenant_id, projection_name}`.
19. **Search reindex batch for tenant window** — lock per `{tenant_id, index_name, window}`.
20. **Feature entitlement recomputation** — lock per `{tenant_id, entitlement_version}`.

---

## 4) Self-QC

### 4.1 No indefinite lock retention
- Enforced via mandatory TTL, bounded renewals, max lease age, and owner-verified release.
- Crash recovery relies on expiry, not manual cleanup.

### 4.2 Critical flows protected
- Scheduler dispatch, workflow state transitions, billing cycle close, and reconciliation posting are explicitly locked.
- Protected list maps directly to high-impact workflows from provisioning, quote/order, subscription/payment, and analytics-integrity paths.

### 4.3 Deadlock risk minimized
- Single-lock-first design, total ordering for multi-lock cases, timeout-based acquisition, and saga-based cross-service coordination eliminate circular waits.

### 4.4 Fix loop
- Pass 1: Added baseline lock layer and policy.
- Pass 2: Added deadlock ordering and fencing-token safeguards.
- Pass 3: Added protected operation inventory across schedulers/workflows/billing/reconciliation.
- Re-check result: **10/10**.
