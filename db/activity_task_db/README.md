# activity_task_db

This folder contains schema artifacts for **B2-P04::ACTIVITIES_TASKS**.

## Scope

- `activity`: immutable timeline/activity records linked to supported CRM entities.
- `task`: actionable work items with explicit assignment + due-date scheduling.
- `task_schedule`: recurring/delayed schedule definitions for background task scans/executions.

## Self-QC target

Use `self_qc.md` to validate:

1. Tasks are linked to valid supported entity types.
2. Activities cannot exist without a scoped tenant/entity link.
3. Scheduling constraints avoid invalid run definitions.
