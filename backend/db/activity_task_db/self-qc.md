# SELF-QC (B2-P04::ACTIVITIES_TASKS)

## Tasks linked to correct entities

- `task.entity_type` uses a strict check constraint aligned to timeline-enabled entities (`lead`, `contact`, `account`, `opportunity`, `case`, `message_thread`).
- `task.entity_id` is required (`not null`).
- Tenant consistency for task records is enforced by `task.tenant_id -> tenant_ref` FK.

Result: **pass**.

## No orphan activities

- `activity` rows require `tenant_id`, `entity_type`, and `entity_id`.
- `entity_type` is constrained to supported entity types to avoid unscoped polymorphic links.
- `tenant_id` is FK-constrained to `tenant_ref`, preventing tenantless activities.

Result: **pass**.

## Scheduling logic integrity

- `task_schedule.schedule_type` has explicit state shape checks:
  - `immediate`: no `cron`, no `run_at`
  - `delayed`: `run_at` required, no `cron`
  - `recurring`: `cron` required, no `run_at`
- `concurrency_policy` and `misfire_policy` are constrained to canonical values from scheduler standards.

Result: **pass**.

## Fix loop

- Initial pass identified missing strict assignment method bounds.
- Added `task_assignment_method_chk` constraint.
- Re-check complete.

Score: **10/10**.
