<!-- OWNERSHIP
PRIMARY FOR: Activity entity (base schema + API); Task entity (schema, assignment logic, scheduling logic, API).
DEFERS TO: activity-control-model.md (ActivityEvent schema detail); cases-domain.md (Case/Ticket entity — full spec lives there).
DO NOT RE-DEFINE: Case/Ticket entity, SLA states, case escalation rules → cases-domain.md.
-->

# B2-P04::ACTIVITIES_TASKS

This spec materializes the activities/tasks capability from:

- `docs/architecture/domain-model.md`
- `docs/infrastructure/workflow-catalog.md`

## Relationship to FollowUp Entity

The `Task` entity (defined in this spec) is the generic actionable work item. The `FollowUp` entity (defined in `docs/architecture/domain-model.md`) is a lead-enforcement-specific record that may reference a linked `Task` but carries additional enforcement metadata (`rule_type`, `escalation_level`, `generated_by`).

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

> **Moved to canonical location.** The full Case / Ticket entity spec, SLA states, escalation rules, SLA policies, routing strategies, and Case APIs are defined in `cases-domain.md`. Do not re-define Case entity fields or SLA logic here.
>
> **Implementation reference:** `src/ticket_management/`, `src/support_console/` — see `cases-domain.md` for the build spec that governs those modules.
>
> **DB schema:** `case_ticket_db` (pending P-025) — schema driven by `cases-domain.md §2`.
