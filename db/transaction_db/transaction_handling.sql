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
  do update set request_hash = excluded.request_hash
  returning response_json into v_existing_response;

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
