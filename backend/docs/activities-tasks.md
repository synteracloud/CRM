# B2-P04::ACTIVITIES_TASKS

This spec materializes the activities/tasks capability from:

- `docs/domain-model.md`
- `docs/workflow-catalog.md`

## Relationship to FollowUp Entity

The `Task` entity (defined in this spec) is the generic actionable work item. The `FollowUp` entity (defined in `docs/domain-model.md`) is a lead-enforcement-specific record that may reference a linked `Task` but carries additional enforcement metadata (`rule_type`, `escalation_level`, `generated_by`).

- `Task` is general-purpose: used for cases, opportunities, manual reminders, etc.
- `FollowUp` is lead-specific: created and managed exclusively by the Follow-Up Engine.
- A `FollowUp` may have a linked `task_id` when an actionable task was auto-generated.
- Deleting a `Task` linked to an active `FollowUp` is blocked by the Follow-Up Engine's anti-bypass controls.

## Entities

### Activity

- Purpose: immutable timeline event for CRM entity history.
- Fields:
  - `activity_id (PK)`
  - `tenant_id`
  - `actor_user_id (nullable)`
  - `entity_type` (`lead|contact|account|opportunity|case|message_thread`)
  - `entity_id`
  - `event_type`
  - `event_time`
  - `payload_json`
  - `source_service`
  - `created_at`

### Task

- Purpose: actionable work item linked to a CRM entity.
- Fields:
  - `task_id (PK)`
  - `tenant_id`
  - `entity_type`
  - `entity_id`
  - `title`
  - `description`
  - `status` (`open|in_progress|completed|canceled`)
  - `priority` (`low|normal|high|urgent`)
  - `assigned_user_id`
  - `created_by_user_id`
  - `assignment_method` (`explicit|entity_owner_fallback|least_loaded_candidate`)
  - `starts_at`
  - `due_at`
  - `completed_at`
  - `created_at`
  - `updated_at`

## APIs

### Activity APIs

- `GET /api/v1/activities`
  - Scope: `activities.read`
  - Filters: `entity_type`, `entity_id`, plus standard pagination query parameters.
- `POST /api/v1/activities`
  - Scope: `activities.create`
  - Creates immutable activity rows.
  - Rejects unsupported `entity_type` and malformed timestamps.

### Task APIs

- `GET /api/v1/tasks`
  - Scope: `tasks.read`
  - Filters: `entity_type`, `entity_id`, `status`, plus standard pagination parameters.
- `POST /api/v1/tasks`
  - Scope: `tasks.create`
  - Creates tasks with assignment + scheduling defaults.
- `POST /api/v1/tasks/{task_id}/reschedule`
  - Scope: `tasks.update`
  - Updates `starts_at` / `due_at` with time-order validation.

## Assignment logic

Task creation assignment precedence:

1. Use `assigned_user_id` when explicitly provided.
2. Else, if `candidate_user_ids` are provided, choose the least-loaded candidate based on open/in-progress task count.
3. Else fallback to `entity_owner_user_id` or authenticated caller (`auth.sub`).

## Scheduling logic

Task runtime schedule behavior:

- `starts_at` defaults to current UTC time.
- `due_at` defaults by priority:
  - `urgent`: +2 hours
  - `high`: +4 hours
  - `normal`: +1 day
  - `low`: +3 days
- Hard validation: `due_at >= starts_at`.

Recurring/delayed schedule definitions are stored in `task_schedule` with safe shape constraints:

- `immediate`: no `cron`, no `run_at`
- `delayed`: requires `run_at`, no `cron`
- `recurring`: requires `cron`, no `run_at`

## Self-QC

- Tasks linked to correct entities: enforced by task constraints and API validation.
- No orphan activities: activity requires tenant and entity linkage fields and allowed entity type.

## Fix loop

- Fix: tightened assignment method and schedule shape constraints in DB schema.
- Re-check: validated API + schema constraints against required QC checks.
- Score: **10/10**.

---

## Ticket / Case Management

*Added from src/ticket_management overlay — 2026-04-02*

### Ticket (Case) Entity

Canonical support case lifecycle record. Named `Case` in `docs/domain-model.md`, implemented as `Ticket` in `src/ticket_management/entities.py`.

| Field | Type | Notes |
|---|---|---|
| `ticket_id` | PK | UUID |
| `tenant_id` | FK→Tenant | Required |
| `account_id` | FK→Account | Required |
| `contact_id` | FK→Contact | Nullable |
| `owner_user_id` | FK→User | Assigned agent |
| `subject` | str | Short description |
| `description` | str | Full issue detail |
| `priority` | str | `low\|normal\|high\|urgent` |
| `status` | str | See sequence below |
| `created_at` | datetime | Immutable |
| `response_due_at` | datetime | First response SLA deadline |
| `resolution_due_at` | datetime | Full resolution SLA deadline |
| `first_responded_at` | datetime\|None | Set on first agent reply |
| `resolved_at` | datetime\|None | Set when status→resolved |
| `closed_at` | datetime\|None | Set when status→closed |

**Status sequence:** `open → in_progress → resolved → closed`

### SLA States

Derived from `response_due_at` / `resolution_due_at` vs current time:

| State | Condition | Action triggered |
|---|---|---|
| `healthy` | Both SLA deadlines have >20% window remaining | None |
| `at_risk` | Either deadline has ≤20% window remaining | Proactive alert to owner |
| `breached` | Either deadline has passed without resolution | Escalation rule fires |

### Escalation Rules

Rule-based SLA escalation. Each rule fires when its threshold condition is met.

| Field | Notes |
|---|---|
| `rule_id` | PK |
| `tenant_id` | Tenant-scoped |
| `level` | Escalation tier (1=first, 2=second, etc.) |
| `trigger` | `sla_breach\|response_overdue\|custom` |
| `threshold_minutes` | Minutes past due before rule fires |
| `route_to` | Target user ID, team ID, or queue name |
| `condition_field/op/value` | Optional additional condition on Ticket fields |
| `active` | Boolean — enables/disables rule without deletion |

**Escalation action types:** `reassign \| raise_priority \| page_on_call \| request_manager_review`

### EscalationAuditRecord

Immutable audit entry written on every escalation event. Never updated or deleted.

### Queue Sort Orders

Support console queue sort options: `sla_due_asc` (default) \| `priority_desc` \| `updated_desc`

### APIs

- `GET /api/v1/tickets` — Scope: `tickets.read`. Filters: `status`, `priority`, `sla_state`, `owner_user_id`.
- `POST /api/v1/tickets` — Scope: `tickets.create`.
- `PATCH /api/v1/tickets/:id` — Scope: `tickets.update`. Status transitions enforced against sequence.
- `POST /api/v1/tickets/:id/escalate` — Scope: `tickets.escalate`. Fires escalation rule manually.
- `GET /api/v1/tickets/:id/sla` — Returns current `sla_state`, time remaining, breach risk.

**Reference:** `src/ticket_management/`, `src/support_console/`, `docs/domain-model.md — Case`
**DB schema needed:** `case_ticket_db` (pending P-025)
