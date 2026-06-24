Status: Draft
Authority Level: Medium
Last Reviewed: 2026-06-22
Owner: Shared

# EVENT_DISCOVERY_REPORT.md
> Event and queue architecture discovery findings from Phase 2 Backend Authority Capture

---

## 1. Discovery Summary

The Pakistan CRM backend uses a minimal, in-process event architecture. No external message broker (Kafka, RabbitMQ, Celery, SQS) exists. Event-like patterns are implemented through asyncio background tasks, in-memory queues, DB tables, and a src/event_bus module.

---

## 2. Background Tasks Confirmed

### Overdue Scanner
- **File:** `backend/services/app.py` (asyncio task) + `backend/services/followup/overdue.py` (scan function)
- **Poll interval:** 60 seconds
- **Action:** Finds all follow-up tasks with `state=pending AND due_at < NOW()`, sets `state=overdue`
- **Error handling:** Logs exception, continues to next cycle (non-fatal)
- **Shutdown:** Graceful via `stop_scanner.set()` event in lifespan shutdown

### Daily Summary Scheduler
- **File:** `backend/services/app.py` (asyncio task) + `backend/services/summary/daily_summary.py`
- **Poll interval:** 60-second polling loop; fires once daily
- **Fire time:** `DAILY_SUMMARY_UTC_HOUR` env var (default 03:00 UTC = 08:00 PKT)
- **Deduplication:** Date-keyed sentinel prevents duplicate sends in same day
- **Channels:** WhatsApp message to manager phone (`DAILY_SUMMARY_OWNER_PHONE`)
- **Dry-run:** `DAILY_SUMMARY_ENABLED=false` → no send, log only

### Eviction Worker
- **File:** `backend/services/core/execution/eviction_worker.py`
- **Type:** Python daemon thread (not asyncio — thread-based)
- **Interval:** `IDEMPOTENCY_EVICT_INTERVAL` env var (default 3600s = 1 hour)
- **Action:** Removes expired entries from GlobalIdempotencyLedger
- **TTL:** `IDEMPOTENCY_TTL_SECONDS` env var (default 86400s = 24 hours)

---

## 3. Event Types Confirmed

6 event types referenced in workflow `trigger_events` DSL fields:

| Event name | Version | Emitted by | Consumed by |
|---|---|---|---|
| `lead.created.v1` | v1 | POST /leads route handler | lead_assignment workflow |
| `lead.idle.v1` | v1 | Overdue scanner / inactivity detection | lead_followup_enforcement workflow |
| `opportunity.stage.changed.v1` | v1 | PATCH /opportunities/:id | opportunity_stage_notify workflow |
| `opportunity.closed.v1` | v1 | PATCH /opportunities/:id (terminal stage) | Workflow trigger |
| `invoice.overdue.v1` | v1 | Overdue scanner | collections_reminder workflow |
| `case.sla.breached.v1` | v1 | SLA scanner (TBD) | sla_breach_notify workflow |

**Important:** These events are named in workflow definitions. How they are published and consumed is not fully confirmed. The `src/event_bus/` module likely handles in-process dispatch, but this was not read in full.

---

## 4. In-Memory Queues

### FollowupJobQueue
- **File:** `backend/services/followup/scheduler.py`
- **Class:** `FollowupJobQueue`
- **Type:** In-process Python priority queue
- **State persistence:** None — resets on service restart
- **Canonical state:** Always in DB; queue is scheduling cache only

### Gateway Idempotency Store (recordStore)
- **File:** `backend/gateway/middleware/idempotency.js`
- **Type:** In-memory Map (Node.js)
- **Purpose:** Cache completed response for idempotent replay
- **In-flight TTL:** 5 minutes
- **Survival:** Process lifetime only

---

## 5. DB-Backed Event Patterns

### Transactional Outbox (transaction_db.outbox_event)
- **Status:** SCHEMA EXISTS; publisher NOT CONFIRMED
- **Table:** `transaction_db.outbox_event`
- **Fields:** aggregate_type, aggregate_id, event_type, event_version, payload_json, trace_id, correlation_id, published_at (NULL = unpublished), retry_count
- **Finding:** The outbox table is defined and ready but no code was found that writes to it or reads from it to publish. May be pending implementation.

### Sync Command Queue (messaging_db.sync_command_queue)
- **Status:** ACTIVE
- **Purpose:** Offline-first field device sync
- **Status FSM:** pending → syncing → synced / pending → failed → dead_letter / syncing → conflict
- **Processor:** `SyncService` (`backend/services/sync/service.py`)

### Webhook Dead-Letter (messaging_db.webhook_dead_letter)
- **Status:** ACTIVE
- **Purpose:** Failed webhook ingestion with investigation trail
- **Admin route:** GET /api/v1/admin/dead-letters

---

## 6. System Workflows

5 system workflows seeded with `is_system=true` (cannot be modified by users):

| Workflow key | Trigger event | Action |
|---|---|---|
| lead_followup_enforcement | lead.idle.v1 | Auto-create follow-up task |
| collections_reminder | invoice.overdue.v1 | WhatsApp reminder to contact |
| sla_breach_notify | case.sla.breached.v1 | Escalate case + notify team |
| lead_assignment | lead.created.v1 | Auto-assign to territory owner |
| opportunity_stage_notify | opportunity.stage.changed.v1 | Notify team + refresh forecast |

---

## 7. Gaps and Recommendations

| Gap | Detail |
|---|---|
| No external message broker | All events in-process; no durability guarantees on crash |
| Outbox publisher missing | transaction_db.outbox_event has no confirmed consumer |
| Event bus module unread | src/event_bus/ module exists; internal dispatch mechanism not confirmed |
| No retry for failed events | No retry queue for events that fail processing (except webhook dead-letter) |
| SLA scanner not confirmed | case.sla.breached.v1 source: scanner implementation not found in code read |
| Task schedule table unused | activity_task_db.task_schedule defines cron/delayed/recurring configs; no job runner confirmed |

---

*End EVENT_DISCOVERY_REPORT.md*
