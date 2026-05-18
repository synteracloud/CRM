-- B1-P05::TRANSACTION_DB
-- Postgres schema for Billing & Subscription Service (transaction_db)
-- Source alignment:
--   - docs/data-architecture.md (domain-owned service DB, tenant-first keys, transactional outbox)
--   - docs/domain-model.md (Subscription, InvoiceSummary, PaymentEvent)

create extension if not exists pgcrypto;

create schema if not exists transaction_db;
set search_path to transaction_db, public;

-- Timestamp trigger helper
create or replace function transaction_db.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Root tenant reference (local mirror, no cross-service FK dependency)
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
execute function transaction_db.set_updated_at();

-- Subscription
create table if not exists subscription (
  subscription_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,

  -- cross-service references (not FK constrained by design)
  account_id uuid not null,
  quote_id uuid,

  external_subscription_ref text,
  plan_code text not null,
  status text not null,
  start_date date not null,
  end_date date,
  renewal_date date,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint subscription_tenant_fk
    foreign key (tenant_id)
    references tenant_ref (tenant_id)
    on delete restrict,
  constraint subscription_status_chk
    check (status in ('draft', 'trialing', 'active', 'paused', 'past_due', 'canceled', 'expired')),
  constraint subscription_dates_chk
    check (end_date is null or end_date >= start_date),
  constraint subscription_renewal_chk
    check (renewal_date is null or renewal_date >= start_date),
  constraint uq_subscription_external_ref unique (tenant_id, external_subscription_ref)
);

create index if not exists idx_subscription_tenant_created
  on subscription (tenant_id, created_at desc);
create index if not exists idx_subscription_tenant_account
  on subscription (tenant_id, account_id);
create index if not exists idx_subscription_tenant_status
  on subscription (tenant_id, status);
create unique index if not exists uq_subscription_tenant_subscription
  on subscription (tenant_id, subscription_id);

create trigger trg_subscription_updated_at
before update on subscription
for each row
execute function transaction_db.set_updated_at();

-- InvoiceSummary
create table if not exists invoice_summary (
  invoice_summary_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  subscription_id uuid not null,

  external_invoice_ref text,
  invoice_number text not null,
  amount_due numeric(18,2) not null,
  amount_paid numeric(18,2) not null default 0,
  currency char(3) not null,
  status text not null,
  due_date date not null,
  issued_at timestamptz not null,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint invoice_summary_amount_due_chk check (amount_due >= 0),
  constraint invoice_summary_amount_paid_chk check (amount_paid >= 0),
  constraint invoice_summary_amount_balance_chk check (amount_paid <= amount_due),
  constraint invoice_summary_status_chk
    check (status in ('draft', 'open', 'paid', 'void', 'uncollectible')),
  constraint invoice_summary_currency_chk check (currency ~ '^[A-Z]{3}$'),
  constraint invoice_summary_subscription_fk
    foreign key (subscription_id)
    references subscription (subscription_id)
    on delete cascade,
  constraint invoice_summary_tenant_subscription_fk
    foreign key (tenant_id, subscription_id)
    references subscription (tenant_id, subscription_id)
    on delete cascade,
  constraint uq_invoice_summary_invoice_number unique (tenant_id, invoice_number),
  constraint uq_invoice_summary_external_ref unique (tenant_id, external_invoice_ref)
);

create index if not exists idx_invoice_summary_tenant_due
  on invoice_summary (tenant_id, due_date);
create index if not exists idx_invoice_summary_tenant_status
  on invoice_summary (tenant_id, status);

create trigger trg_invoice_summary_updated_at
before update on invoice_summary
for each row
execute function transaction_db.set_updated_at();

-- PaymentEvent
create table if not exists payment_event (
  payment_event_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,

  subscription_id uuid,
  invoice_summary_id uuid,

  external_payment_ref text,
  event_type text not null,
  amount numeric(18,2) not null,
  currency char(3) not null,
  event_time timestamptz not null,
  status text not null,

  created_at timestamptz not null default now(),

  constraint payment_event_subscription_fk
    foreign key (subscription_id)
    references subscription (subscription_id)
    on delete set null,
  constraint payment_event_invoice_fk
    foreign key (invoice_summary_id)
    references invoice_summary (invoice_summary_id)
    on delete set null,
  constraint payment_event_tenant_subscription_fk
    foreign key (tenant_id, subscription_id)
    references subscription (tenant_id, subscription_id)
    on delete set null,
  constraint payment_event_tenant_invoice_fk
    foreign key (tenant_id, invoice_summary_id)
    references invoice_summary (tenant_id, invoice_summary_id)
    on delete set null,
  constraint payment_event_amount_chk check (amount >= 0),
  constraint payment_event_currency_chk check (currency ~ '^[A-Z]{3}$'),
  constraint payment_event_status_chk
    check (status in ('pending', 'succeeded', 'failed', 'refunded', 'reversed')),
  constraint payment_event_type_chk
    check (event_type in ('authorized', 'captured', 'settled', 'failed', 'refunded', 'chargeback')),
  constraint payment_event_relation_chk
    check (subscription_id is not null or invoice_summary_id is not null),
  constraint uq_payment_event_external_ref unique (tenant_id, external_payment_ref)
);

create unique index if not exists uq_invoice_summary_tenant_invoice
  on invoice_summary (tenant_id, invoice_summary_id);

create index if not exists idx_payment_event_tenant_event_time
  on payment_event (tenant_id, event_time desc);
create index if not exists idx_payment_event_tenant_status
  on payment_event (tenant_id, status);
create index if not exists idx_payment_event_tenant_invoice
  on payment_event (tenant_id, invoice_summary_id);


-- Payment aggregate (B2-P08::PAYMENTS_REVENUE)
create table if not exists payment (
  payment_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,

  subscription_id uuid,
  invoice_summary_id uuid,

  external_payment_ref text,
  payment_method_type text not null,
  amount numeric(18,2) not null,
  currency char(3) not null,
  status text not null,

  initiated_at timestamptz not null default now(),
  authorized_at timestamptz,
  captured_at timestamptz,
  settled_at timestamptz,
  failed_at timestamptz,
  canceled_at timestamptz,
  refunded_at timestamptz,
  chargeback_at timestamptz,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint payment_subscription_fk
    foreign key (subscription_id)
    references subscription (subscription_id)
    on delete set null,
  constraint payment_invoice_fk
    foreign key (invoice_summary_id)
    references invoice_summary (invoice_summary_id)
    on delete set null,
  constraint payment_tenant_subscription_fk
    foreign key (tenant_id, subscription_id)
    references subscription (tenant_id, subscription_id)
    on delete set null,
  constraint payment_tenant_invoice_fk
    foreign key (tenant_id, invoice_summary_id)
    references invoice_summary (tenant_id, invoice_summary_id)
    on delete set null,
  constraint payment_amount_chk check (amount > 0),
  constraint payment_currency_chk check (currency ~ '^[A-Z]{3}$'),
  constraint payment_status_chk
    check (status in ('initiated', 'authorized', 'captured', 'settled', 'failed', 'canceled', 'partially_refunded', 'refunded', 'chargeback')),
  constraint payment_method_type_chk
    check (payment_method_type in ('card', 'bank_transfer', 'wallet', 'ach', 'other')),
  constraint payment_relation_chk
    check (subscription_id is not null or invoice_summary_id is not null),
  constraint uq_payment_external_ref unique (tenant_id, external_payment_ref)
);

create unique index if not exists uq_payment_tenant_payment
  on payment (tenant_id, payment_id);
create index if not exists idx_payment_tenant_status
  on payment (tenant_id, status);
create index if not exists idx_payment_tenant_created
  on payment (tenant_id, created_at desc);

create trigger trg_payment_updated_at
before update on payment
for each row
execute function transaction_db.set_updated_at();

create table if not exists payment_status_history (
  payment_status_history_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  payment_id uuid not null,
  from_status text,
  to_status text not null,
  reason text,
  changed_at timestamptz not null,
  changed_by_user_id uuid,
  created_at timestamptz not null default now(),

  constraint payment_status_history_payment_fk
    foreign key (payment_id)
    references payment (payment_id)
    on delete cascade,
  constraint payment_status_history_tenant_payment_fk
    foreign key (tenant_id, payment_id)
    references payment (tenant_id, payment_id)
    on delete cascade,
  constraint payment_status_history_to_status_chk
    check (to_status in ('initiated', 'authorized', 'captured', 'settled', 'failed', 'canceled', 'partially_refunded', 'refunded', 'chargeback')),
  constraint payment_status_history_from_status_chk
    check (from_status is null or from_status in ('initiated', 'authorized', 'captured', 'settled', 'failed', 'canceled', 'partially_refunded', 'refunded', 'chargeback'))
);

create index if not exists idx_payment_status_history_tenant_payment
  on payment_status_history (tenant_id, payment_id, changed_at desc);

create table if not exists revenue_ledger (
  revenue_ledger_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  payment_id uuid not null,
  entry_type text not null,
  amount_delta numeric(18,2) not null,
  currency char(3) not null,
  recognized_at timestamptz not null,
  note text,
  created_at timestamptz not null default now(),

  constraint revenue_ledger_payment_fk
    foreign key (payment_id)
    references payment (payment_id)
    on delete cascade,
  constraint revenue_ledger_tenant_payment_fk
    foreign key (tenant_id, payment_id)
    references payment (tenant_id, payment_id)
    on delete cascade,
  constraint revenue_ledger_entry_type_chk
    check (entry_type in ('recognition', 'refund', 'chargeback_adjustment')),
  constraint revenue_ledger_currency_chk check (currency ~ '^[A-Z]{3}$')
);

create index if not exists idx_revenue_ledger_tenant_recognized
  on revenue_ledger (tenant_id, recognized_at desc);

create or replace function transaction_db.is_valid_payment_status_transition(
  p_from_status text,
  p_to_status text
)
returns boolean
language sql
immutable
as $$
  select case
    when p_from_status = p_to_status then true
    when p_from_status = 'initiated' and p_to_status in ('authorized', 'failed', 'canceled') then true
    when p_from_status = 'authorized' and p_to_status in ('captured', 'failed', 'canceled') then true
    when p_from_status = 'captured' and p_to_status in ('settled', 'partially_refunded', 'refunded', 'chargeback') then true
    when p_from_status = 'settled' and p_to_status in ('partially_refunded', 'refunded', 'chargeback') then true
    when p_from_status = 'partially_refunded' and p_to_status in ('refunded', 'chargeback') then true
    else false
  end;
$$;

create or replace function transaction_db.apply_payment_status_transition(
  p_tenant_id uuid,
  p_payment_id uuid,
  p_new_status text,
  p_changed_at timestamptz,
  p_reason text default null,
  p_changed_by_user_id uuid default null
)
returns table(payment_id uuid, previous_status text, current_status text)
language plpgsql
as $$
declare
  v_payment payment%rowtype;
  v_effective_at timestamptz := coalesce(p_changed_at, now());
begin
  select *
  into v_payment
  from payment
  where tenant_id = p_tenant_id
    and payment.payment_id = p_payment_id
  for update;

  if not found then
    raise exception 'payment_not_found';
  end if;

  if not transaction_db.is_valid_payment_status_transition(v_payment.status, p_new_status) then
    raise exception 'invalid_status_transition: % -> %', v_payment.status, p_new_status;
  end if;

  update payment
  set status = p_new_status,
      authorized_at = case when p_new_status = 'authorized' then v_effective_at else authorized_at end,
      captured_at = case when p_new_status = 'captured' then v_effective_at else captured_at end,
      settled_at = case when p_new_status = 'settled' then v_effective_at else settled_at end,
      failed_at = case when p_new_status = 'failed' then v_effective_at else failed_at end,
      canceled_at = case when p_new_status = 'canceled' then v_effective_at else canceled_at end,
      refunded_at = case when p_new_status = 'refunded' then v_effective_at else refunded_at end,
      chargeback_at = case when p_new_status = 'chargeback' then v_effective_at else chargeback_at end
  where payment.payment_id = p_payment_id
    and payment.tenant_id = p_tenant_id;

  insert into payment_status_history (
    tenant_id,
    payment_id,
    from_status,
    to_status,
    reason,
    changed_at,
    changed_by_user_id
  ) values (
    p_tenant_id,
    p_payment_id,
    v_payment.status,
    p_new_status,
    p_reason,
    v_effective_at,
    p_changed_by_user_id
  );

  if p_new_status = 'settled' then
    insert into revenue_ledger (tenant_id, payment_id, entry_type, amount_delta, currency, recognized_at, note)
    values (p_tenant_id, p_payment_id, 'recognition', v_payment.amount, v_payment.currency, v_effective_at, 'payment_settled');
  elsif p_new_status in ('partially_refunded', 'refunded') then
    insert into revenue_ledger (tenant_id, payment_id, entry_type, amount_delta, currency, recognized_at, note)
    values (p_tenant_id, p_payment_id, 'refund', -v_payment.amount, v_payment.currency, v_effective_at, 'payment_refunded');
  elsif p_new_status = 'chargeback' then
    insert into revenue_ledger (tenant_id, payment_id, entry_type, amount_delta, currency, recognized_at, note)
    values (p_tenant_id, p_payment_id, 'chargeback_adjustment', -v_payment.amount, v_payment.currency, v_effective_at, 'payment_chargeback');
  end if;

  return query
  select p_payment_id, v_payment.status, p_new_status;
end;
$$;

-- Transactional outbox (from data architecture pattern)
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

  constraint outbox_event_tenant_fk
    foreign key (tenant_id)
    references tenant_ref (tenant_id)
    on delete restrict,
  constraint outbox_event_retry_chk check (retry_count >= 0)
);

create index if not exists idx_outbox_event_unpublished
  on outbox_event (published_at, recorded_at)
  where published_at is null;
create index if not exists idx_outbox_event_tenant_recorded
  on outbox_event (tenant_id, recorded_at desc);

-- Idempotency ledger for external billing webhooks / payment processor callbacks
create table if not exists idempotency_key (
  idempotency_key_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  operation_name text not null,
  idempotency_key text not null,
  request_hash text not null,
  response_json jsonb,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,

  constraint idempotency_key_tenant_fk
    foreign key (tenant_id)
    references tenant_ref (tenant_id)
    on delete restrict,
  constraint uq_idempotency_scope unique (tenant_id, operation_name, idempotency_key)
);

create index if not exists idx_idempotency_expiry
  on idempotency_key (expires_at);
