set search_path to transaction_db, public;

create table if not exists outbox_event (
  outbox_event_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  aggregate_type text not null,
  aggregate_id uuid not null,
  event_type text not null,
  event_version integer not null default 1,
  payload_json jsonb not null,
  trace_id text,
  correlation_id text,
  occurred_at timestamptz not null,
  recorded_at timestamptz not null default now(),
  published_at timestamptz,
  retry_count integer not null default 0,
  constraint outbox_event_tenant_fk foreign key (tenant_id) references tenant_ref (tenant_id) on delete restrict,
  constraint outbox_event_retry_chk check (retry_count >= 0)
);

create index if not exists idx_outbox_event_unpublished
  on outbox_event (published_at, recorded_at)
  where published_at is null;
create index if not exists idx_outbox_event_tenant_recorded
  on outbox_event (tenant_id, recorded_at desc);

create table if not exists idempotency_key (
  idempotency_key_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  operation_name text not null,
  idempotency_key text not null,
  request_hash text not null,
  response_json jsonb,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  constraint idempotency_key_tenant_fk foreign key (tenant_id) references tenant_ref (tenant_id) on delete restrict,
  constraint uq_idempotency_scope unique (tenant_id, operation_name, idempotency_key)
);

create index if not exists idx_idempotency_expiry on idempotency_key (expires_at);
