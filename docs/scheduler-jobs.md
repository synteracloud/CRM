# Scheduler Jobs: Background Runner + Scheduling System

This document defines the CRM platform's canonical background execution model for delayed, recurring, and retryable jobs.

## 1) Scope

The Scheduler subsystem consists of:

- **Job Queue** (durable enqueue/dequeue, lease, ack/nack, dead-letter).
- **Scheduler API** (submit, schedule, inspect, cancel, replay).
- **Runner Workers** (execute handlers with retry + idempotency guarantees).

Primary goals:

1. Ensure jobs are **retry-safe**.
2. Prevent duplicate execution for the same semantic work unit.
3. Support one-off, delayed, and cron-based recurring execution.

## 2) Queue and Execution Model

### 2.1 Canonical Queue States

A job MUST move through one of the following states:

- `queued`
- `leased`
- `running`
- `succeeded`
- `retry_scheduled`
- `failed_terminal`
- `dead_lettered`
- `canceled`

### 2.2 Queue Record Shape

```json
{
  "job_id": "job_01JV6QXABR4M7Q4P4NQ6N9YFKS",
  "tenant_id": "ten_01JTQ8F9J7X2M4K1Y3R6S8T0VV",
  "job_type": "search.reindex.account",
  "idempotency_key": "account:acc_123:reindex:v1",
  "payload": {},
  "priority": 50,
  "available_at": "2026-03-26T12:00:00Z",
  "attempt": 0,
  "max_attempts": 8,
  "lease_timeout_seconds": 120,
  "retry_policy": {
    "strategy": "exponential_jitter",
    "base_delay_seconds": 10,
    "max_delay_seconds": 1800
  },
  "dedupe_window_seconds": 86400,
  "status": "queued",
  "created_at": "2026-03-26T12:00:00Z",
  "updated_at": "2026-03-26T12:00:00Z"
}
```

### 2.3 Leasing Rules (No Duplication)

- Workers MUST acquire jobs using an atomic lease operation (`status=queued|retry_scheduled -> leased`).
- Lease MUST include `lease_owner` and `lease_expires_at`.
- A second worker MUST NOT execute a non-expired lease.
- Expired leases MAY be reclaimed by other workers.

### 2.4 Acknowledgement Rules

- `ack` transitions `running -> succeeded`.
- `nack` transitions:
  - to `retry_scheduled` if attempts remain
  - to `failed_terminal` (and optionally `dead_lettered`) when attempts are exhausted.

## 3) Retry Safety + Idempotency Contract

### 3.1 Required Idempotency

Each submitted job MUST include an `idempotency_key` that identifies semantic work, not transport attempts.

Examples:

- `invoice:inv_874:send-reminder:v1`
- `contact:ct_552:normalize-email:v1`

### 3.2 Deduplication Guarantees

- Queue MUST enforce uniqueness on `(tenant_id, idempotency_key)` within `dedupe_window_seconds`.
- If duplicate submission occurs inside the dedupe window:
  - API returns existing `job_id` with `deduplicated=true`
  - no second executable queue record is created.

### 3.3 Handler Safety Rules

Job handlers MUST:

1. Treat execution as **at-least-once** delivery.
2. Be side-effect idempotent using domain-level natural keys.
3. Persist completion markers/versions before external side effects when possible.
4. Emit consistent outcome events (success/failure) exactly once per terminal transition.

## 4) Scheduling System

### 4.1 Schedule Types

- **Immediate**: run as soon as capacity is available.
- **Delayed**: run at `run_at` timestamp.
- **Recurring**: cron expression with timezone.

### 4.2 Schedule Record Shape

```json
{
  "schedule_id": "sch_01JV6R26V9JWMV9S7B4D9F2D5G",
  "tenant_id": "ten_01JTQ8F9J7X2M4K1Y3R6S8T0VV",
  "name": "nightly-account-reindex",
  "job_type": "search.reindex.account",
  "payload_template": {
    "scope": "changed_since_last_run"
  },
  "cron": "0 2 * * *",
  "timezone": "America/New_York",
  "enabled": true,
  "concurrency_policy": "forbid",
  "misfire_policy": "fire_once",
  "next_run_at": "2026-03-27T06:00:00Z",
  "last_run_at": "2026-03-26T06:00:00Z",
  "created_at": "2026-03-26T12:00:00Z",
  "updated_at": "2026-03-26T12:00:00Z"
}
```

### 4.3 Recurring Schedule Safety

- Scheduler MUST materialize each due run into a unique job using `schedule_id + scheduled_for` idempotency seed.
- `concurrency_policy` values:
  - `allow` (overlap allowed)
  - `forbid` (skip while prior run active)
  - `replace` (cancel running and enqueue latest)
- Missed executions during outage are controlled by `misfire_policy` (`skip`, `fire_once`, `catch_up`).

## 5) Scheduler APIs

All endpoints follow `docs/api-standards.md` envelope and naming rules.

### 5.1 Job APIs

- `POST /api/v1/jobs` — enqueue immediate/delayed job.
- `GET /api/v1/jobs/{job_id}` — get job status + attempts.
- `GET /api/v1/jobs` — list jobs by tenant filters.
- `POST /api/v1/jobs/{job_id}/cancel` — cancel queued/retry jobs.
- `POST /api/v1/jobs/{job_id}/replay` — clone/replay terminal failed job.

#### Create Job Request

```json
{
  "job_type": "notification.send",
  "idempotency_key": "notification:notif_123:dispatch:v1",
  "payload": {
    "notification_id": "notif_123"
  },
  "run_at": "2026-03-26T12:05:00Z",
  "max_attempts": 5,
  "dedupe_window_seconds": 86400
}
```

### 5.2 Schedule APIs

- `POST /api/v1/job-schedules` — create recurring schedule.
- `GET /api/v1/job-schedules/{schedule_id}` — fetch schedule state.
- `GET /api/v1/job-schedules` — list schedules.
- `PATCH /api/v1/job-schedules/{schedule_id}` — enable/disable/update cron/policies.
- `POST /api/v1/job-schedules/{schedule_id}/run-now` — enqueue immediate ad-hoc run.
- `DELETE /api/v1/job-schedules/{schedule_id}` — soft-delete schedule.

#### Create Schedule Request

```json
{
  "name": "daily-sla-escalation-scan",
  "job_type": "case.sla.scan",
  "payload_template": {
    "priority_scope": ["high", "urgent"]
  },
  "cron": "*/15 * * * *",
  "timezone": "UTC",
  "concurrency_policy": "forbid",
  "misfire_policy": "fire_once",
  "enabled": true
}
```

## 6) Platform Events

The scheduler publishes the following canonical events:

- `job.enqueued.v1`
- `job.started.v1`
- `job.succeeded.v1`
- `job.retry.scheduled.v1`
- `job.failed.v1`
- `job.dead_lettered.v1`
- `schedule.created.v1`
- `schedule.updated.v1`
- `schedule.deleted.v1`

Event names and schemas are cataloged in `docs/event-catalog.md`.

## 7) Self-QC Checklist (10/10 Gate)

Release readiness MUST satisfy all checks:

1. **Retry-safe handlers**: forced duplicate delivery yields no incorrect side effects.
2. **No duplicate execution**: lease contention test shows one active runner per lease.
3. **Dedupe correctness**: duplicate API submits return existing `job_id`.
4. **Backoff behavior**: retry delays increase with jitter and cap correctly.
5. **Dead-letter path**: exhausted retries emit dead-letter event and retain payload.
6. **Schedule materialization**: each due slot creates at most one executable job.
7. **Run-now behavior**: ad-hoc schedule run does not corrupt recurring cursor.
8. **Cancellation**: canceled queued jobs are not executed by workers.
9. **Observability**: metrics/logs include `job_id`, `tenant_id`, `attempt`, `idempotency_key`.
10. **Replay safety**: replayed terminal jobs require explicit operator action and new audit trail.

If any check fails, apply **Fix → Re-check** until all ten pass.
