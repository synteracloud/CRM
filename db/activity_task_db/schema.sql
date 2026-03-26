-- B2-P04::ACTIVITIES_TASKS
-- Postgres schema for Activity Timeline + Task Scheduling domain
-- Source alignment:
--   - docs/domain-model.md (ActivityEvent + task-style assignment entity patterns)
--   - docs/workflow-catalog.md (lead assignment, opportunity stage tasks, case SLA operations)

create extension if not exists pgcrypto;

create schema if not exists activity_task_db;
set search_path to activity_task_db, public;

create or replace function activity_task_db.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists tenant_ref (
  tenant_id uuid primary key,
  tenant_name text not null,
  status text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint tenant_ref_status_chk check (status in ('active', 'suspended', 'deactivated'))
);

create trigger trg_tenant_ref_updated_at
before update on tenant_ref
for each row
execute function activity_task_db.set_updated_at();

-- Activity entity (materialized activity/timeline record, immutable)
create table if not exists activity (
  activity_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  actor_user_id uuid,

  entity_type text not null,
  entity_id uuid not null,
  event_type text not null,
  event_time timestamptz not null,
  payload_json jsonb not null default '{}'::jsonb,
  source_service text not null,

  created_at timestamptz not null default now(),

  constraint activity_tenant_fk
    foreign key (tenant_id)
    references tenant_ref (tenant_id)
    on delete restrict,
  constraint activity_entity_type_chk
    check (entity_type in ('lead', 'contact', 'account', 'opportunity', 'case', 'message_thread'))
);

create index if not exists idx_activity_tenant_event_time
  on activity (tenant_id, event_time desc);
create index if not exists idx_activity_tenant_entity
  on activity (tenant_id, entity_type, entity_id, event_time desc);
create unique index if not exists uq_activity_tenant_activity
  on activity (tenant_id, activity_id);

-- Task entity (actionable work linked to a CRM entity)
create table if not exists task (
  task_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,

  entity_type text not null,
  entity_id uuid not null,

  title text not null,
  description text,
  status text not null default 'open',
  priority text not null default 'normal',

  assigned_user_id uuid,
  created_by_user_id uuid not null,
  assignment_method text not null,

  starts_at timestamptz not null,
  due_at timestamptz not null,
  completed_at timestamptz,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint task_tenant_fk
    foreign key (tenant_id)
    references tenant_ref (tenant_id)
    on delete restrict,
  constraint task_entity_type_chk
    check (entity_type in ('lead', 'contact', 'account', 'opportunity', 'case', 'message_thread')),
  constraint task_status_chk
    check (status in ('open', 'in_progress', 'completed', 'canceled')),
  constraint task_priority_chk
    check (priority in ('low', 'normal', 'high', 'urgent')),
  constraint task_schedule_chk
    check (due_at >= starts_at),
  constraint task_completion_chk
    check (completed_at is null or completed_at >= starts_at),
  constraint task_assignment_method_chk
    check (assignment_method in ('explicit', 'entity_owner_fallback', 'least_loaded_candidate'))
);

create index if not exists idx_task_tenant_due
  on task (tenant_id, due_at);
create index if not exists idx_task_tenant_status
  on task (tenant_id, status);
create index if not exists idx_task_tenant_entity
  on task (tenant_id, entity_type, entity_id);
create index if not exists idx_task_tenant_assignee_status
  on task (tenant_id, assigned_user_id, status)
  where status in ('open', 'in_progress');
create unique index if not exists uq_task_tenant_task
  on task (tenant_id, task_id);

create trigger trg_task_updated_at
before update on task
for each row
execute function activity_task_db.set_updated_at();

-- Scheduling cursor for recurring scans/actions (e.g., SLA checks, overdue nudges)
create table if not exists task_schedule (
  task_schedule_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,

  name text not null,
  schedule_type text not null,
  cron text,
  timezone text not null default 'UTC',
  run_at timestamptz,
  next_run_at timestamptz,
  enabled boolean not null default true,

  concurrency_policy text not null default 'forbid',
  misfire_policy text not null default 'fire_once',

  payload_template jsonb not null default '{}'::jsonb,
  last_run_at timestamptz,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint task_schedule_tenant_fk
    foreign key (tenant_id)
    references tenant_ref (tenant_id)
    on delete restrict,
  constraint task_schedule_type_chk
    check (schedule_type in ('immediate', 'delayed', 'recurring')),
  constraint task_schedule_concurrency_chk
    check (concurrency_policy in ('allow', 'forbid', 'replace')),
  constraint task_schedule_misfire_chk
    check (misfire_policy in ('skip', 'fire_once', 'catch_up')),
  constraint task_schedule_shape_chk
    check (
      (schedule_type = 'immediate' and cron is null and run_at is null)
      or (schedule_type = 'delayed' and run_at is not null and cron is null)
      or (schedule_type = 'recurring' and cron is not null and run_at is null)
    ),
  constraint uq_task_schedule_name unique (tenant_id, name)
);

create index if not exists idx_task_schedule_due
  on task_schedule (tenant_id, next_run_at)
  where enabled = true;

create trigger trg_task_schedule_updated_at
before update on task_schedule
for each row
execute function activity_task_db.set_updated_at();
