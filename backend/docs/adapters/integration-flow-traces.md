<!-- OWNERSHIP
PRIMARY FOR: Cross-service end-to-end integration flow traces (ordered steps, events emitted per step, failure paths per step); end-state assertions for integration test validation; Phase 5 integration contract validation anchors.
DEFERS TO: workflow-catalog.md (business workflow step definitions — this doc applies those steps to concrete scenarios; do not redefine step semantics); execution-hardening.md (retry/DLQ behaviour referenced in failure paths); event-catalog.md (canonical event names emitted at each step).
DO NOT RE-DEFINE: Workflow step business logic → workflow-catalog.md; retry/DLQ policy → execution-hardening.md; event payload schemas → event-catalog.md; domain entity rules → respective domain spec files.
-->

# Integration Flow Traces

## Purpose

This document traces 4 cross-service end-to-end flows defined in PRODUCT-SPEC.md §1/§12 as "mandatory integration flows that must function without failure." Each trace provides: ordered steps across services, events emitted at each step, failure paths per step, and end-state assertions. These traces are the spec for integration testing and Phase 5 contract validation.

**Relationship to other docs:** `workflow-catalog.md` defines business workflows with ordered steps. `execution-hardening.md` defines retry/DLQ behavior. This document applies those rules to specific cross-service scenarios with concrete end states.

---

## Flow 1: WhatsApp → Lead → Follow-up → Close

**Description:** An inbound WhatsApp message creates a lead, triggers an enforced follow-up, the follow-up is completed, and the deal is closed.

**Start state:** No existing conversation or lead for the inbound phone number.  
**End state:** Lead in `CLOSED_WON` stage; Follow-up in `COMPLETED` status; ActivityEvent chain intact; no orphaned follow-up tasks.

### Steps

| Step | Service | Action | Event emitted | Failure path |
|---|---|---|---|---|
| 1 | WhatsApp Engine | Inbound message received at `POST /api/v1/webhooks/whatsapp` | `whatsapp.message.received` | Webhook returns 200 immediately (async processing). If processing fails: retry with exponential backoff. On 8th failure: DLQ entry. |
| 2 | WhatsApp Engine | Intent classified as `lead_inquiry` | — | If classification service unavailable: default to `lead_inquiry` (safe default). |
| 3 | WhatsApp Engine | Conversation created (keyed by `tenant_id + phone`) | `conversation.created` | If DB write fails: retry. Webhook already returned 200 — failure is non-user-visible but logged. |
| 4 | Lead Management Service | Lead auto-created from conversation: `source=whatsapp_inbound`, `stage=OPEN` | `lead.created` | If Lead creation fails: emit `lead.creation_failed`; DLQ entry; do NOT retry silently — alert to operator. |
| 5 | Lead Management Service | Shared with Conversation: `Conversation.lead_id = lead.id` | `conversation.lead_linked` | Soft failure: conversation proceeds without lead link if lead was not created. |
| 6 | Follow-up Engine | T+0 follow-up task auto-created: `assigned_to = territory_assignment.assigned_rep_id`, `due_at = now() + SLA_hours` | `followup.created` | If territory service unavailable: assign to default queue. Follow-up is still created — never skip. |
| 7 | Notification Service | WhatsApp message sent to assigned rep: "New lead [name/phone] — follow up now" | `notification.sent` | If WhatsApp send fails: log; do not block lead creation. Rep will see lead in queue. |
| 8 | [Time passes — rep calls customer] | | | |
| 9 | Activity Control | Rep logs activity (call): `POST /api/v1/activities` | `activity.logged` | Retry on transient failure. Activity is idempotent (Idempotency-Key header). |
| 10 | Follow-up Engine | Follow-up marked complete by rep: `PATCH /followups/{id}/complete` | `followup.completed` | OCC check: `version_no` must match. On OCC conflict: return 409; rep retries. |
| 11 | Follow-up Engine | Next follow-up auto-scheduled (if lead still open) | `followup.created` | See step 6. |
| 12 | Opportunity Service | Rep creates opportunity from lead: `POST /api/v1/opportunities` | `lead.converted`, `opportunity.created` | Saga pattern: Lead → Opportunity (see workflow-catalog.md lead_intake_assignment_conversion). Compensation: soft-delete opportunity if lead conversion fails. |
| 13 | Opportunity Service | Rep moves deal to Won: `PATCH /opportunities/{id}` with `stage=WON` | `opportunity.won` | OCC check on opportunity. Stage change triggers final follow-up closure. |
| 14 | Activity Control | Win event logged: `activity_type = deal_won` | `activity.logged` | Non-blocking; retry if transient. |
| 15 | Follow-up Engine | All pending follow-ups for this lead auto-completed on `opportunity.won` event | `followup.completed` (bulk) | If any follow-up closure fails: log; do not block opportunity close. Run orphan-cleanup scanner. |

### End-State Assertions

- `Lead.stage = CLOSED_WON`
- `Opportunity.stage = WON`, `Opportunity.closed_at` is set
- `FollowupTask.status = COMPLETED` for all tasks linked to this lead
- `Conversation.status != OPEN` (linked conversation marked handled)
- `ActivityEvent` chain: lead.created → followup.created → activity.logged → lead.converted → opportunity.won — all present with correct entity refs
- No orphaned `FollowupTask` in PENDING status for this lead

---

## Flow 2: Lead → Invoice → Payment → Reconciliation

**Description:** A closed deal triggers invoice creation, the invoice is sent to the customer via WhatsApp, the customer pays via JazzCash, and the payment is reconciled against the invoice.

**Start state:** Lead in `CLOSED_WON`, Opportunity in `WON` stage.  
**End state:** Invoice in `PAID` status; PaymentEvent confirmed; AccountsReceivable balance decremented; audit trail complete.

### Steps

| Step | Service | Action | Event emitted | Failure path |
|---|---|---|---|---|
| 1 | Opportunity Service | `opportunity.won` event emitted | `opportunity.won` | — |
| 2 | Collections Engine | Invoice auto-created (if auto-invoice = true for tenant): `POST /api/v1/invoices` | `invoice.created` | Idempotent: `Idempotency-Key = opportunity_id + "_invoice"`. Retry on transient failure. |
| 3 | Collections Engine | `POST /api/v1/invoices/{id}/send` called (manually by rep or auto-triggered) | `invoice.sent` | If WhatsApp send fails: invoice stays in `CREATED` state; retry next hour. Invoice not lost. |
| 4 | WhatsApp Engine | Invoice message delivered to customer with payment instructions (JazzCash number + amount) | `whatsapp.message.delivered` | WhatsApp delivery failure: retry 3×. On 3rd failure: email fallback (if email on file). |
| 5 | [Customer initiates JazzCash payment] | | | |
| 6 | Collections Engine | JazzCash payment callback received: `POST /api/v1/payments/callback/jazzcash` | `payment.callback_received` | Webhook returns 200 immediately. All processing async. Callback logged before processing. |
| 7 | Collections Engine | Payment amount extracted; confidence scoring run | — | Scoring algorithm failure: default to `manual_review` (confidence = 0). Do not auto-match. |
| 8a | Collections Engine (confidence ≥85) | Auto-reconciliation: invoice matched to payment | `payment.auto_reconciled` | OCC on invoice update. On conflict: retry reconciliation. Max 3 retries. Then DLQ. |
| 8b | Collections Engine (confidence 40–84) | Payment flagged for manual review: `invoice.manual_review_required` | `payment.pending_review` | No mutation to invoice status yet. Alert sent to rep. |
| 8c | Collections Engine (confidence <40) | Payment unmatched: logged as `UNMATCHED_PAYMENT` | `payment.unmatched` | Rep manually reviews. No auto-action. |
| 9 | Collections Engine (path 8a) | Invoice status updated to `PAID`: atomic UPDATE WHERE version_no=expected | `invoice.paid` | If atomic update fails (version conflict): retry path 7. |
| 10 | Activity Control | Payment event logged: `activity_type = payment_received` | `activity.logged` | Non-blocking audit log. Retry if transient. |
| 11 | Notification Service | Customer WhatsApp confirmation: "Payment of Rs X confirmed" | `whatsapp.message.sent` | Non-blocking. Failure logged. Customer does not receive confirmation but payment is still recorded. |

### End-State Assertions

- `Invoice.status = PAID`, `Invoice.paid_at` is set
- `PaymentEvent` record exists with `status = confirmed`, linked to invoice
- `ActivityEvent`: invoice.created → invoice.sent → payment.callback_received → invoice.paid — all present
- No orphaned payment callback in DLQ (unless permanently failed after 8 retries)
- If manual review path (8b): `Invoice.status = OPEN` with `manual_review_flag = true`; rep can see in collections queue

---

## Flow 3: Follow-up → Escalation → Reassignment

**Description:** A follow-up task passes its due date without action, triggering the overdue scanner, escalation notifications, manager reassignment, and activity log updates.

**Start state:** `FollowupTask.status = PENDING`, `due_at < now()`.  
**End state:** Task reassigned to new owner; original assignee notified; manager notified; audit trail complete; no task stuck in OVERDUE without an active owner.

### Steps

| Step | Service | Action | Event emitted | Failure path |
|---|---|---|---|---|
| 1 | Follow-up Engine | Overdue scanner job runs (every 5 minutes) | — | Scanner failure: alert and retry next cycle. No tasks are permanently stuck — scanner is stateless. |
| 2 | Follow-up Engine | Task found: `due_at < now()` AND `status = PENDING` | — | — |
| 3 | Follow-up Engine | Status updated: `PENDING → OVERDUE` | `followup.overdue` | Atomic update. OCC version check. On conflict: skip this cycle; scanner will catch it next run. |
| 4 | Follow-up Engine | Lead status updated: `stage → OVERDUE` (if not already escalated) | `lead.stage_changed` | Non-atomic with step 3. If lead update fails: log; lead scanner will repair on next pass. |
| 5 | Escalation Engine | Level 1 escalation triggered (T+0 overdue): notify assigned rep via WhatsApp | `escalation.level_1` | WhatsApp send failure: retry 3×. Log if all retries fail. Escalation event still created. |
| 6 | [T+24h: no action taken] | | | |
| 7 | Escalation Engine | Level 3 escalation triggered (T+24h): notify manager | `escalation.level_3` | Manager notification failure: retry 3×. In-app notification as fallback. |
| 8 | Follow-up Engine | Manager receives alert: views lead in queue | — | — |
| 9 | Follow-up Engine | Manager reassigns: `PATCH /followups/{id}` with `assigned_to = new_rep_id` | `followup.reassigned` | OCC check. On conflict: return 409; manager retries. |
| 10 | Activity Control | Reassignment logged: `activity_type = task_reassigned`, includes `from_rep_id` + `to_rep_id` | `activity.logged` | Retry if transient. |
| 11 | Notification Service | New rep notified via WhatsApp: "Lead [name] assigned to you. Follow up required." | `whatsapp.message.sent` | Failure logged. Rep will see assignment in queue view. |
| 12 | Follow-up Engine | Task status updated: `OVERDUE → PENDING` (fresh due_at set by manager or default +24h) | `followup.rescheduled` | OCC check. On conflict: retry. |
| 13 | Escalation Engine | Escalation record marked `resolved_at = now()` | `escalation.resolved` | Non-blocking. Escalation history preserved even if resolution marking fails. |

### End-State Assertions

- `FollowupTask.status = PENDING` (not OVERDUE) after reassignment
- `FollowupTask.assigned_to = new_rep_id`
- `CaseEscalation` / `FollowupEscalation` record exists with `escalation_level = 3`, `triggered_at` set
- `ActivityEvent` chain: followup.overdue → escalation.level_1 → escalation.level_3 → followup.reassigned — all present
- Original rep received Level 1 notification
- Manager received Level 3 notification
- New rep received assignment notification
- No task in `OVERDUE` status with no active owner

---

## Flow 4: Offline Action → Sync → Consistent State

**Description:** A field sales rep takes an action while offline (creates a lead). When connectivity is restored, the command syncs to the server, conflict detection runs, and the device state reconciles.

**Start state:** Rep is offline. No existing lead for the target contact in the server state.  
**End state:** Lead created on server; device state matches server; no data lost; ActivityEvent logged.

### Steps

| Step | Service | Action | Event emitted | Failure path |
|---|---|---|---|---|
| 1 | Mobile Client | Rep submits "Create Lead" form while offline | — | Action queued in encrypted local `CommandRecord` store. |
| 2 | Offline Sync Engine (client) | `CommandRecord` created: `command_type = CREATE_LEAD`, `payload = {name, phone, ...}`, `status = PENDING`, `idempotency_key = UUID` | — | If local storage write fails: alert user "Action could not be saved." Do not lose data silently. |
| 3 | [Connectivity restored] | | | |
| 4 | Offline Sync Engine (client) | Client detects connectivity; begins sync: `POST /api/v1/sync/commands` with `CommandRecord[]` | — | Network error: retry with exponential backoff (1s, 2s, 4s, 8s max). |
| 5 | Sync Service (server) | Receives batch of `CommandRecord[]` | — | Validate each command schema. Invalid commands: return 422 per command (do not fail entire batch). |
| 6 | Sync Service (server) | Idempotency check: `SELECT FROM idempotency_ledger WHERE idempotency_key = cmd.idempotency_key` | — | If key already exists: return cached response body; skip re-execution (idempotent). |
| 7 | Sync Service (server) | Command dispatched to Lead Management Service: `CREATE_LEAD` → `POST /api/v1/leads` | `lead.created` | Lead creation failure: record `CommandRecord.status = FAILED` with `error_message`. Return failure to client in batch response. |
| 8 | Sync Service (server) | Conflict detection: check if a lead with same phone exists | — | If duplicate found: apply entity-level conflict rule (see offline-sync.md): for Lead, `server_wins` — existing server record takes precedence. |
| 9a | No conflict | Sync Service marks `CommandRecord.status = COMPLETED`; returns lead_id in response | `sync.command_completed` | — |
| 9b | Conflict detected | Sync Service marks `CommandRecord.status = CONFLICT`; returns server entity in response body | `sync.command_conflict` | Client receives server entity; UI shows conflict resolution prompt to user. |
| 10 | Mobile Client | Device state updated with server response: local lead record replaced with server canonical record | — | If client-side update fails: refresh from server on next app open. |
| 11 | Activity Control | Lead creation activity logged: `source = offline_sync` | `activity.logged` | Retry if transient. |
| 12 | [Remaining commands in batch processed] | | | |
| 13 | Sync Service (server) | Batch response returned: per-command status array | — | Client processes status array: completed = update local state; failed = surface error to user; conflict = surface conflict UI. |

### Partial Batch Failure Rules (from offline-sync.md)
- If 8 of 10 commands succeed: the batch response includes 2 failures.
- "Sync complete" is NOT shown until ALL commands are in terminal state (completed, failed, or conflict).
- Failed commands remain in local queue for retry (up to 3 retries). After 3 failures: mark as `PERMANENTLY_FAILED`; notify user.
- Conflict commands are cleared after user resolves or dismisses the conflict UI.

### End-State Assertions

- Server `Lead` record exists with `source = offline_sync`
- `CommandRecord.status = COMPLETED` (or `CONFLICT` if duplicate)
- Device local state matches server canonical record for the lead
- `ActivityEvent`: lead.created with `source = offline_sync` — present and linked to lead
- Idempotency ledger entry exists for the command's `idempotency_key`
- No duplicate leads created even if sync request was sent twice (idempotent)
- User was notified if any command permanently failed (not silently dropped)

---

## Cross-Flow Invariants

These hold across all 4 flows:

1. **WhatsApp webhook always returns 200 immediately.** Processing is async. No flow blocks on WhatsApp delivery confirmation.
2. **All mutations are idempotent.** Every write operation carries an `Idempotency-Key`. Retries never create duplicate records.
3. **ActivityEvent chain is always complete.** Every step that mutates a domain entity emits an `ActivityEvent`. Missing events in the chain are a test failure.
4. **No silent data loss.** Every failure path produces either a retry, a DLQ entry, or a user notification. Dropping data without trace is not permitted.
5. **OCC (optimistic concurrency control) on all aggregate updates.** Version conflicts produce `409`; callers retry. No last-write-wins overwrites.
6. **tenant_id isolation enforced at every step.** No cross-tenant data leakage in any of these flows.
