create extension if not exists pgcrypto;
create schema if not exists transaction_db;
set search_path to transaction_db, public;

create or replace function transaction_db.set_updated_at()
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
execute function transaction_db.set_updated_at();

create table if not exists subscription (
  subscription_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
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
  constraint subscription_tenant_fk foreign key (tenant_id) references tenant_ref (tenant_id) on delete restrict,
  constraint subscription_status_chk check (status in ('draft', 'trialing', 'active', 'paused', 'past_due', 'canceled', 'expired')),
  constraint subscription_dates_chk check (end_date is null or end_date >= start_date),
  constraint subscription_renewal_chk check (renewal_date is null or renewal_date >= start_date),
  constraint uq_subscription_external_ref unique (tenant_id, external_subscription_ref)
);

create index if not exists idx_subscription_tenant_created on subscription (tenant_id, created_at desc);
create index if not exists idx_subscription_tenant_account on subscription (tenant_id, account_id);
create index if not exists idx_subscription_tenant_status on subscription (tenant_id, status);
create unique index if not exists uq_subscription_tenant_subscription on subscription (tenant_id, subscription_id);

create trigger trg_subscription_updated_at
before update on subscription
for each row
execute function transaction_db.set_updated_at();

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
  constraint invoice_summary_status_chk check (status in ('draft', 'open', 'paid', 'void', 'uncollectible')),
  constraint invoice_summary_currency_chk check (currency ~ '^[A-Z]{3}$'),
  constraint invoice_summary_subscription_fk foreign key (subscription_id) references subscription (subscription_id) on delete cascade,
  constraint invoice_summary_tenant_subscription_fk foreign key (tenant_id, subscription_id) references subscription (tenant_id, subscription_id) on delete cascade,
  constraint uq_invoice_summary_invoice_number unique (tenant_id, invoice_number),
  constraint uq_invoice_summary_external_ref unique (tenant_id, external_invoice_ref)
);

create unique index if not exists uq_invoice_summary_tenant_invoice on invoice_summary (tenant_id, invoice_summary_id);
create index if not exists idx_invoice_summary_tenant_due on invoice_summary (tenant_id, due_date);
create index if not exists idx_invoice_summary_tenant_status on invoice_summary (tenant_id, status);

create trigger trg_invoice_summary_updated_at
before update on invoice_summary
for each row
execute function transaction_db.set_updated_at();

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
  constraint payment_event_subscription_fk foreign key (subscription_id) references subscription (subscription_id) on delete set null,
  constraint payment_event_invoice_fk foreign key (invoice_summary_id) references invoice_summary (invoice_summary_id) on delete set null,
  constraint payment_event_tenant_subscription_fk foreign key (tenant_id, subscription_id) references subscription (tenant_id, subscription_id) on delete set null,
  constraint payment_event_tenant_invoice_fk foreign key (tenant_id, invoice_summary_id) references invoice_summary (tenant_id, invoice_summary_id) on delete set null,
  constraint payment_event_amount_chk check (amount >= 0),
  constraint payment_event_currency_chk check (currency ~ '^[A-Z]{3}$'),
  constraint payment_event_status_chk check (status in ('pending', 'succeeded', 'failed', 'refunded', 'reversed')),
  constraint payment_event_type_chk check (event_type in ('authorized', 'captured', 'settled', 'failed', 'refunded', 'chargeback')),
  constraint payment_event_relation_chk check (subscription_id is not null or invoice_summary_id is not null),
  constraint uq_payment_event_external_ref unique (tenant_id, external_payment_ref)
);

create index if not exists idx_payment_event_tenant_event_time on payment_event (tenant_id, event_time desc);
create index if not exists idx_payment_event_tenant_status on payment_event (tenant_id, status);
create index if not exists idx_payment_event_tenant_invoice on payment_event (tenant_id, invoice_summary_id);
