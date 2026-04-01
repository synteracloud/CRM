-- Activity Control Engine audit schema
-- Implements immutable logging, ownership control, audit hash chain, visibility feeds, and alerts.

create extension if not exists pgcrypto;

create schema if not exists activity_task_db;
set search_path to activity_task_db, public;

create table if not exists entity_ownership (
  tenant_id uuid not null,
  entity_type text not null,
  entity_id uuid not null,
  owner_user_id uuid not null,
  owner_team_id uuid,
  ownership_version bigint not null default 1,
  assigned_at timestamptz not null default now(),
  assigned_by_user_id uuid not null,
  primary key (tenant_id, entity_type, entity_id),
  constraint entity_ownership_type_chk check (entity_type in ('lead', 'deal'))
);

create index if not exists idx_entity_ownership_owner
  on entity_ownership (tenant_id, owner_user_id, entity_type);

create table if not exists ownership_transfer_history (
  transfer_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  entity_type text not null,
  entity_id uuid not null,
  from_owner_user_id uuid not null,
  to_owner_user_id uuid not null,
  requested_by_user_id uuid not null,
  approved_by_user_id uuid,
  from_team_id uuid,
  to_team_id uuid,
  reason_code text not null,
  reason_note text not null,
  status text not null,
  requested_at timestamptz not null default now(),
  decided_at timestamptz,
  executed_at timestamptz,
  constraint ownership_transfer_type_chk check (entity_type in ('lead', 'deal')),
  constraint ownership_transfer_status_chk check (status in ('requested', 'approved', 'executed', 'rejected', 'expired'))
);

create index if not exists idx_ownership_transfer_entity
  on ownership_transfer_history (tenant_id, entity_type, entity_id, requested_at desc);

create table if not exists activity_event_log (
  event_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  event_ts timestamptz not null default now(),
  actor_type text not null,
  actor_id uuid not null,
  actor_role text not null,
  actor_team_id uuid,
  on_behalf_of_user_id uuid,
  entity_type text not null,
  entity_id uuid not null,
  owner_user_id uuid,
  action text not null,
  result text not null,
  request_id text not null,
  trace_id text not null,
  field_changes_json jsonb not null default '[]'::jsonb,
  payload_json jsonb not null default '{}'::jsonb,
  constraint activity_event_entity_type_chk check (entity_type in ('lead', 'deal')),
  constraint activity_event_result_chk check (result in ('success', 'denied', 'failed', 'pending'))
);

create index if not exists idx_activity_event_tenant_ts
  on activity_event_log (tenant_id, event_ts desc);
create index if not exists idx_activity_event_actor
  on activity_event_log (tenant_id, actor_id, event_ts desc);
create index if not exists idx_activity_event_entity
  on activity_event_log (tenant_id, entity_type, entity_id, event_ts desc);

create table if not exists audit_event_log (
  audit_id uuid primary key default gen_random_uuid(),
  event_id uuid not null,
  tenant_id uuid not null,
  chain_seq bigint not null,
  prev_hash text not null,
  hash_value text not null,
  event_ts timestamptz not null default now(),
  actor_id uuid not null,
  entity_type text not null,
  entity_id uuid not null,
  action text not null,
  payload_json jsonb not null default '{}'::jsonb,
  constraint audit_event_chain_unique unique (tenant_id, chain_seq),
  constraint audit_event_hash_unique unique (tenant_id, hash_value),
  constraint audit_event_entity_type_chk check (entity_type in ('lead', 'deal')),
  constraint audit_event_ref_fk foreign key (event_id) references activity_event_log(event_id) on delete restrict
);

create index if not exists idx_audit_event_tenant_ts
  on audit_event_log (tenant_id, event_ts desc);

revoke update, delete on activity_event_log from public;
revoke update, delete on audit_event_log from public;
revoke update, delete on ownership_transfer_history from public;

create table if not exists activity_alert_log (
  alert_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  alert_type text not null,
  severity text not null,
  actor_id uuid,
  entity_type text,
  entity_id uuid,
  rule_name text not null,
  details_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  constraint activity_alert_type_chk check (alert_type in ('inactivity', 'misuse')),
  constraint activity_alert_severity_chk check (severity in ('low', 'medium', 'high', 'critical'))
);

create index if not exists idx_activity_alert_tenant_ts
  on activity_alert_log (tenant_id, created_at desc);
