set search_path to transaction_db, public;

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
