set search_path to transaction_db, public;

-- Atomic payment ingestion with outbox append.
-- Ensures idempotent processing for provider webhook/event keys.
create or replace function transaction_db.record_payment_event(
  p_tenant_id uuid,
  p_operation_name text,
  p_idempotency_key text,
  p_request_hash text,
  p_subscription_id uuid,
  p_invoice_summary_id uuid,
  p_external_payment_ref text,
  p_event_type text,
  p_amount numeric,
  p_currency char(3),
  p_event_time timestamptz,
  p_status text,
  p_trace_id text,
  p_correlation_id text
)
returns uuid
language plpgsql
as $$
declare
  v_payment_event_id uuid;
  v_existing_response jsonb;
  v_existing_request_hash text;
begin
  -- 1) Idempotency gate (single transaction).
  insert into idempotency_key (
    tenant_id,
    operation_name,
    idempotency_key,
    request_hash,
    expires_at
  ) values (
    p_tenant_id,
    p_operation_name,
    p_idempotency_key,
    p_request_hash,
    now() + interval '7 days'
  )
  on conflict (tenant_id, operation_name, idempotency_key)
  do update set request_hash = idempotency_key.request_hash
  returning request_hash, response_json into v_existing_request_hash, v_existing_response;

  if v_existing_request_hash <> p_request_hash then
    raise exception 'idempotency_key_reused_with_different_payload';
  end if;

  if v_existing_response is not null then
    return (v_existing_response ->> 'payment_event_id')::uuid;
  end if;

  -- 2) Domain state write.
  insert into payment_event (
    tenant_id,
    subscription_id,
    invoice_summary_id,
    external_payment_ref,
    event_type,
    amount,
    currency,
    event_time,
    status
  ) values (
    p_tenant_id,
    p_subscription_id,
    p_invoice_summary_id,
    p_external_payment_ref,
    p_event_type,
    p_amount,
    p_currency,
    p_event_time,
    p_status
  )
  returning payment_event_id into v_payment_event_id;

  -- 3) Optional invoice balance update.
  if p_invoice_summary_id is not null and p_status = 'succeeded' then
    update invoice_summary
    set amount_paid = least(amount_due, amount_paid + p_amount)
    where tenant_id = p_tenant_id
      and invoice_summary_id = p_invoice_summary_id;
  end if;

  -- 4) Transactional outbox event.
  insert into outbox_event (
    tenant_id,
    aggregate_type,
    aggregate_id,
    event_type,
    payload_json,
    trace_id,
    correlation_id,
    occurred_at
  ) values (
    p_tenant_id,
    'PaymentEvent',
    v_payment_event_id,
    'payment.event.recorded.v1',
    jsonb_build_object(
      'payment_event_id', v_payment_event_id,
      'subscription_id', p_subscription_id,
      'invoice_summary_id', p_invoice_summary_id,
      'status', p_status,
      'amount', p_amount,
      'currency', p_currency,
      'event_type', p_event_type,
      'event_time', p_event_time
    ),
    p_trace_id,
    p_correlation_id,
    p_event_time
  );

  -- 5) Store deterministic idempotency response.
  update idempotency_key
  set response_json = jsonb_build_object('payment_event_id', v_payment_event_id)
  where tenant_id = p_tenant_id
    and operation_name = p_operation_name
    and idempotency_key = p_idempotency_key;

  return v_payment_event_id;
end;
$$;

-- Mark outbox messages as published by relay workers.
create or replace function transaction_db.mark_outbox_published(
  p_outbox_event_ids uuid[]
)
returns integer
language sql
as $$
  with updated as (
    update outbox_event
    set published_at = now()
    where outbox_event_id = any(p_outbox_event_ids)
      and published_at is null
    returning 1
  )
  select count(*)::integer from updated;
$$;

-- Payment creation with initial history + outbox append.
create or replace function transaction_db.create_payment(
  p_tenant_id uuid,
  p_subscription_id uuid,
  p_invoice_summary_id uuid,
  p_external_payment_ref text,
  p_payment_method_type text,
  p_amount numeric,
  p_currency char(3),
  p_trace_id text,
  p_correlation_id text,
  p_changed_by_user_id uuid default null
)
returns uuid
language plpgsql
as $$
declare
  v_payment_id uuid;
begin
  insert into payment (
    tenant_id,
    subscription_id,
    invoice_summary_id,
    external_payment_ref,
    payment_method_type,
    amount,
    currency,
    status,
    initiated_at
  ) values (
    p_tenant_id,
    p_subscription_id,
    p_invoice_summary_id,
    p_external_payment_ref,
    p_payment_method_type,
    p_amount,
    p_currency,
    'initiated',
    now()
  )
  returning payment_id into v_payment_id;

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
    v_payment_id,
    null,
    'initiated',
    'payment_created',
    now(),
    p_changed_by_user_id
  );

  insert into outbox_event (
    tenant_id,
    aggregate_type,
    aggregate_id,
    event_type,
    payload_json,
    trace_id,
    correlation_id,
    occurred_at
  ) values (
    p_tenant_id,
    'Payment',
    v_payment_id,
    'payment.created.v1',
    jsonb_build_object(
      'payment_id', v_payment_id,
      'subscription_id', p_subscription_id,
      'invoice_summary_id', p_invoice_summary_id,
      'status', 'initiated',
      'amount', p_amount,
      'currency', p_currency,
      'payment_method_type', p_payment_method_type
    ),
    p_trace_id,
    p_correlation_id,
    now()
  );

  return v_payment_id;
end;
$$;

create or replace function transaction_db.get_revenue_summary(
  p_tenant_id uuid,
  p_from timestamptz,
  p_to timestamptz
)
returns table(currency char(3), recognized_revenue numeric(18,2))
language sql
stable
as $$
  select
    rl.currency,
    coalesce(sum(rl.amount_delta), 0)::numeric(18,2) as recognized_revenue
  from revenue_ledger rl
  where rl.tenant_id = p_tenant_id
    and rl.recognized_at >= p_from
    and rl.recognized_at < p_to
  group by rl.currency
  order by rl.currency;
$$;

-- -----------------------------------------------------------------------------
-- B7-P01::TRANSACTION_INTEGRITY
-- Transaction management layer with explicit unit-of-work workflows.
-- -----------------------------------------------------------------------------

-- Internal helper: assert invoice belongs to tenant.
create or replace function transaction_db.assert_invoice_tenant(
  p_tenant_id uuid,
  p_invoice_summary_id uuid
)
returns void
language plpgsql
as $$
begin
  if p_invoice_summary_id is null then
    return;
  end if;

  if not exists (
    select 1
    from invoice_summary i
    where i.invoice_summary_id = p_invoice_summary_id
      and i.tenant_id = p_tenant_id
  ) then
    raise exception 'invoice_tenant_mismatch_or_not_found';
  end if;
end;
$$;

-- Unit-of-work: create subscription and first invoice atomically + outbox append.
create or replace function transaction_db.create_subscription_with_invoice_uow(
  p_tenant_id uuid,
  p_account_id uuid,
  p_quote_id uuid,
  p_external_subscription_ref text,
  p_plan_code text,
  p_subscription_status text,
  p_start_date date,
  p_renewal_date date,
  p_external_invoice_ref text,
  p_invoice_number text,
  p_amount_due numeric,
  p_currency char(3),
  p_due_date date,
  p_issued_at timestamptz,
  p_trace_id text,
  p_correlation_id text
)
returns table(subscription_id uuid, invoice_summary_id uuid)
language plpgsql
as $$
declare
  v_subscription_id uuid;
  v_invoice_summary_id uuid;
begin
  insert into subscription (
    tenant_id,
    account_id,
    quote_id,
    external_subscription_ref,
    plan_code,
    status,
    start_date,
    renewal_date
  ) values (
    p_tenant_id,
    p_account_id,
    p_quote_id,
    p_external_subscription_ref,
    p_plan_code,
    p_subscription_status,
    p_start_date,
    p_renewal_date
  )
  returning subscription.subscription_id into v_subscription_id;

  insert into invoice_summary (
    tenant_id,
    subscription_id,
    external_invoice_ref,
    invoice_number,
    amount_due,
    amount_paid,
    currency,
    status,
    due_date,
    issued_at
  ) values (
    p_tenant_id,
    v_subscription_id,
    p_external_invoice_ref,
    p_invoice_number,
    p_amount_due,
    0,
    p_currency,
    'open',
    p_due_date,
    p_issued_at
  )
  returning invoice_summary.invoice_summary_id into v_invoice_summary_id;

  insert into outbox_event (
    tenant_id,
    aggregate_type,
    aggregate_id,
    event_type,
    payload_json,
    trace_id,
    correlation_id,
    occurred_at
  ) values (
    p_tenant_id,
    'Subscription',
    v_subscription_id,
    'subscription.provisioned.v1',
    jsonb_build_object(
      'subscription_id', v_subscription_id,
      'invoice_summary_id', v_invoice_summary_id,
      'account_id', p_account_id,
      'plan_code', p_plan_code,
      'subscription_status', p_subscription_status,
      'invoice_status', 'open',
      'amount_due', p_amount_due,
      'currency', p_currency
    ),
    p_trace_id,
    p_correlation_id,
    coalesce(p_issued_at, now())
  );

  return query select v_subscription_id, v_invoice_summary_id;
end;
$$;

-- Unit-of-work: advance payment status and keep invoice consistency in same tx.
create or replace function transaction_db.advance_payment_status_uow(
  p_tenant_id uuid,
  p_payment_id uuid,
  p_new_status text,
  p_changed_at timestamptz,
  p_reason text default null,
  p_changed_by_user_id uuid default null,
  p_trace_id text default null,
  p_correlation_id text default null
)
returns table(payment_id uuid, previous_status text, current_status text)
language plpgsql
as $$
declare
  v_payment payment%rowtype;
  v_effective_at timestamptz := coalesce(p_changed_at, now());
  v_invoice invoice_summary%rowtype;
  v_settled_amount numeric(18,2);
  v_refund_amount numeric(18,2);
begin
  select * into v_payment
  from payment p
  where p.tenant_id = p_tenant_id
    and p.payment_id = p_payment_id
  for update;

  if not found then
    raise exception 'payment_not_found';
  end if;

  -- apply guarded transition + history + revenue ledger in same transaction
  perform 1
  from transaction_db.apply_payment_status_transition(
    p_tenant_id,
    p_payment_id,
    p_new_status,
    v_effective_at,
    p_reason,
    p_changed_by_user_id
  );

  -- keep invoice balance/status consistent with payment outcome
  if v_payment.invoice_summary_id is not null and p_new_status in ('settled', 'partially_refunded', 'refunded', 'chargeback') then
    perform transaction_db.assert_invoice_tenant(p_tenant_id, v_payment.invoice_summary_id);

    select * into v_invoice
    from invoice_summary i
    where i.tenant_id = p_tenant_id
      and i.invoice_summary_id = v_payment.invoice_summary_id
    for update;

    if p_new_status = 'settled' then
      v_settled_amount := v_payment.amount;
      update invoice_summary
      set amount_paid = least(amount_due, amount_paid + v_settled_amount),
          status = case
            when least(amount_due, amount_paid + v_settled_amount) >= amount_due then 'paid'
            else 'open'
          end
      where tenant_id = p_tenant_id
        and invoice_summary_id = v_payment.invoice_summary_id;
    else
      v_refund_amount := v_payment.amount;
      update invoice_summary
      set amount_paid = greatest(0, amount_paid - v_refund_amount),
          status = case
            when greatest(0, amount_paid - v_refund_amount) >= amount_due then 'paid'
            else 'open'
          end
      where tenant_id = p_tenant_id
        and invoice_summary_id = v_payment.invoice_summary_id;
    end if;
  end if;

  insert into outbox_event (
    tenant_id,
    aggregate_type,
    aggregate_id,
    event_type,
    payload_json,
    trace_id,
    correlation_id,
    occurred_at
  ) values (
    p_tenant_id,
    'Payment',
    p_payment_id,
    'payment.status.changed.v1',
    jsonb_build_object(
      'payment_id', p_payment_id,
      'previous_status', v_payment.status,
      'current_status', p_new_status,
      'invoice_summary_id', v_payment.invoice_summary_id,
      'effective_at', v_effective_at
    ),
    p_trace_id,
    p_correlation_id,
    v_effective_at
  );

  return query
  select p_payment_id, v_payment.status, p_new_status;
end;
$$;

-- Unit-of-work: idempotent payment event ingestion with deterministic replay safety.
create or replace function transaction_db.record_payment_event_uow(
  p_tenant_id uuid,
  p_operation_name text,
  p_idempotency_key text,
  p_request_hash text,
  p_subscription_id uuid,
  p_invoice_summary_id uuid,
  p_external_payment_ref text,
  p_event_type text,
  p_amount numeric,
  p_currency char(3),
  p_event_time timestamptz,
  p_status text,
  p_trace_id text,
  p_correlation_id text
)
returns uuid
language plpgsql
as $$
declare
  v_idempotency idempotency_key%rowtype;
  v_payment_event_id uuid;
begin
  insert into idempotency_key (
    tenant_id,
    operation_name,
    idempotency_key,
    request_hash,
    expires_at
  ) values (
    p_tenant_id,
    p_operation_name,
    p_idempotency_key,
    p_request_hash,
    now() + interval '7 days'
  )
  on conflict (tenant_id, operation_name, idempotency_key)
  do update set request_hash = idempotency_key.request_hash
  returning * into v_idempotency;

  if v_idempotency.request_hash <> p_request_hash then
    raise exception 'idempotency_key_reused_with_different_payload';
  end if;

  if v_idempotency.response_json is not null then
    return (v_idempotency.response_json ->> 'payment_event_id')::uuid;
  end if;

  if p_invoice_summary_id is not null then
    perform transaction_db.assert_invoice_tenant(p_tenant_id, p_invoice_summary_id);
  end if;

  v_payment_event_id := transaction_db.record_payment_event(
    p_tenant_id,
    p_operation_name,
    p_idempotency_key,
    p_request_hash,
    p_subscription_id,
    p_invoice_summary_id,
    p_external_payment_ref,
    p_event_type,
    p_amount,
    p_currency,
    p_event_time,
    p_status,
    p_trace_id,
    p_correlation_id
  );

  return v_payment_event_id;
end;
$$;
