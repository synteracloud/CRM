Status: Active
Authority Level: Medium
Last Reviewed: 2026-06-23
Owner: Shared

# EVENT_AND_QUEUE_ARCHITECTURE.md
> Source: backend/services/app.py, backend/services/bootstrap.py, backend/services/core/execution/*, backend/db/transaction_db/schema.sql (outbox_event), backend/db/messaging_db/schema.sql (sync_command_queue, webhook_dead_letter), backend/src/event_bus/

---

## 1. Summary

The Pakistan CRM backend uses a **minimal event architecture**. There is no external message broker (no Kafka, RabbitMQ, Celery, SQS, or Redis Pub/Sub). Event-like patterns are implemented as:

1. **FastAPI BackgroundTasks** — not found in use (no `background_tasks.add_task()` calls confirmed)
2. **asyncio background tasks** — used for overdue scanner and daily summary scheduler
3. **In-memory queue** — used by `FollowupJobQueue` within the FollowupEnforcementEngine
4. **Transactional outbox** — DB-level outbox table in `transaction_db` (defined; publisher CONFIRMED ABSENT — Phase 3.25)
5. **Sync command queue** — DB table in `messaging_db` for offline-first command persistence
6. **Webhook dead-letter** — DB table for failed webhook ingestion
7. **In-memory idempotency ledger** — thread-safe in-process record store in Python service layer
8. **In-memory audit log** — hash-chain in Node.js gateway (not Redis-backed)

---

## 2. AsyncIO Background Tasks (FastAPI)

Two background tasks are started in the FastAPI lifespan (`backend/services/app.py`):

### Overdue Scanner (`_overdue_scanner`)
- **Type:** asyncio task (persistent loop)
- **Interval:** 60 seconds
- **Purpose:** Scans all pending follow-up tasks and marks those past `due_at` as `overdue` in the DB
- **Implementation:** `from services.followup.overdue import scan_overdue_tasks`
- **Startup:** Created as asyncio task on lifespan startup
- **Shutdown:** `stop_scanner.set()` + `scanner_task.cancel()` on lifespan shutdown
- **Error handling:** `logger.exception()` on scan cycle error; continues to next cycle

### Daily Summary Scheduler (`_daily_summary_scheduler`)
- **Type:** asyncio task (persistent loop)
- **Interval:** Polls every 60 seconds; fires once per day at `DAILY_SUMMARY_UTC_HOUR` (default 03:00 UTC = 08:00 PKT)
- **Purpose:** Sends daily WhatsApp activity summary to managers
- **Dedup:** Date-keyed sentinel prevents duplicate sends within the same day
- **Dry-run:** When `DAILY_SUMMARY_ENABLED=false` or messaging engine not configured — logs only, no send
- **Configuration:** DAILY_SUMMARY_ENABLED, DAILY_SUMMARY_UTC_HOUR, DAILY_SUMMARY_OWNER_PHONE, DAILY_SUMMARY_TENANT_ID, DAILY_SUMMARY_LANG

---

## 3. Eviction Worker (Background Thread)

**Path:** `backend/services/core/execution/eviction_worker.py`
**Type:** Python daemon thread (started at FastAPI startup via `bootstrap.startup()`)
**Purpose:** Evicts expired records from the `GlobalIdempotencyLedger` (in-memory)
**Interval:** `IDEMPOTENCY_EVICT_INTERVAL` env var (default 3600 seconds = 1 hour)
**TTL:** `IDEMPOTENCY_TTL_SECONDS` env var (default 86400 seconds = 24 hours)
**Shutdown:** Via stop function returned by `start_eviction_worker()`; called in `bootstrap.shutdown()`

---

## 4. In-Memory Job Queue (FollowupEnforcementEngine)

**Path:** `backend/services/followup/scheduler.py`
**Class:** `FollowupJobQueue`
**Type:** In-process priority queue
**Purpose:** Schedules and triggers follow-up tasks within the enforcement engine
**Persistence:** In-memory only — resets on service restart; canonical state is in the DB
**Consumer:** `FollowupEnforcementEngine` processes jobs on scheduling triggers

---

## 5. Transactional Outbox Pattern (DB-level)

**Schema:** `transaction_db.outbox_event`
**Purpose:** Captures billing/payment domain events for reliable publishing (pattern only — publisher not confirmed as implemented)
**Key fields:**
- `aggregate_type` — entity type that emitted the event
- `aggregate_id` — entity UUID
- `event_type` — event name (e.g. 'payment.settled', 'subscription.created')
- `event_version` — schema version (default 1)
- `payload_json` — event payload JSONB
- `trace_id`, `correlation_id` — distributed tracing identifiers
- `published_at` — NULL = unpublished; set when event is dispatched
- `retry_count` — number of publish attempts

**Publisher:** CONFIRMED ABSENT (Phase 3.25). `grep -r "outbox" backend/src/` returns no matches. No outbox publisher or consumer code exists. The table is schema-only. G-HIGH-004 SAFE-DEFAULT applies: accept for C6 (payments in stub mode anyway); implement publisher when OA-003 activates payments.
**Consumers:** CONFIRMED NONE (Phase 3.25). No consumer code found. Same status as publisher.

---

## 6. Sync Command Queue (Offline-First)

**Schema:** `messaging_db.sync_command_queue`
**Purpose:** Persists offline field-device sync commands for ordered processing
**Operation types:** create/update/delete
**Status FSM:** pending → syncing → synced; OR pending → failed → dead_letter; OR syncing → conflict
**Concurrency:** `base_version` for optimistic concurrency during sync
**HTTP surface:** POST /sync (trigger batch processing), GET /sync/status, GET /sync/queue
**Processing:** `SyncService` (`backend/services/sync/service.py`)

---

## 7. Webhook Dead-Letter Queue

**Schema:** `messaging_db.webhook_dead_letter`
**Purpose:** Records failed webhook ingestion for investigation and replay
**Captured fields:** provider, endpoint, payload, headers, failure_reason, attempt_count, first/last failed timestamps
**Resolution:** `resolved_at` set when webhook is manually processed or discarded
**HTTP surface:** GET /api/v1/admin/dead-letters (dlq_public_router from ExecutionControlPlane)

---

## 8. Event Types Confirmed in Code

Events emitted within route handlers (in-memory; not published to external broker):

| Event | Where Emitted | Consumer |
|---|---|---|
| `opportunity.stage.changed.v1` | PATCH /opportunities/:id (on stage transition) | opportunity_stage_notify workflow trigger |
| `opportunity.closed.v1` | PATCH /opportunities/:id (terminal stage) | Workflow trigger |
| `lead.idle.v1` | Lead inactivity detection (overdue scanner) | lead_followup_enforcement workflow |
| `lead.created.v1` | POST /leads | lead_assignment workflow |
| `invoice.overdue.v1` | Overdue scanner | collections_reminder workflow |
| `case.sla.breached.v1` | `services/cases/service.py` (SLA breach logic confirmed G-MED-002 CLOSED) | sla_breach_notify workflow |

**Note:** These events are dispatched via the in-process `InMemoryEventBus` (`backend/src/event_bus/core.py`). The event bus is CONFIRMED as synchronous in-process publish/subscribe with retry (max 3 attempts) and dead-letter routing. No external broker. Confirmed Phase 3.25.

---

## 9. System Workflows (Event-Triggered)

5 system workflows are seeded with `is_system=true` and consume the above events:

| Workflow Key | Trigger Event | Purpose |
|---|---|---|
| lead_followup_enforcement | lead.idle.v1 | Auto-create follow-up task on idle lead |
| collections_reminder | invoice.overdue.v1 | WhatsApp reminder on overdue invoice |
| sla_breach_notify | case.sla.breached.v1 | Escalate + notify on SLA breach |
| lead_assignment | lead.created.v1 | Auto-assign lead to territory owner |
| opportunity_stage_notify | opportunity.stage.changed.v1 | Team notification + forecast refresh |

---

## 10. Scheduled Jobs

No external scheduler (Celery Beat, APScheduler, cron service) is confirmed. Scheduling is handled:
- **Overdue scanner**: asyncio loop (60-second interval) in FastAPI
- **Daily summary**: asyncio loop (60-second poll, fires once daily) in FastAPI
- **Task schedules**: `activity_task_db.task_schedule` table defines schedule configs; CONFIRMED NO JOB RUNNER (Phase 3.25, G-MED-001 SAFE-DEFAULT). Table is schema-only. Scheduler will be implemented in C7 (Celery Beat or APScheduler).

---

## 11. Async Processing Assessment

| Pattern | Status | Notes |
|---|---|---|
| Message broker (Kafka/RabbitMQ/SQS) | NOT IMPLEMENTED | No broker dependency in requirements.txt or package.json |
| Redis Pub/Sub | NOT IMPLEMENTED | Redis used only for rate limiting, OTP, JTI |
| Celery | NOT IMPLEMENTED | Not in requirements.txt |
| FastAPI BackgroundTasks | NOT CONFIRMED IN USE | Framework available; no confirmed usages found |
| asyncio background tasks | IMPLEMENTED | Overdue scanner, daily summary |
| In-process queue | IMPLEMENTED | FollowupJobQueue |
| Transactional outbox | SCHEMA ONLY | Table defined; publisher/consumer not confirmed |
| Sync command queue | IMPLEMENTED | For offline-first field sync |
| Webhook dead-letter | IMPLEMENTED | DB table + admin endpoint |

---

*End EVENT_AND_QUEUE_ARCHITECTURE.md*
