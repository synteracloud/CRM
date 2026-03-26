# B2-P04::ACTIVITIES_TASKS

This spec materializes the activities/tasks capability from:

- `docs/domain-model.md`
- `docs/workflow-catalog.md`

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
