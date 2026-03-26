# SELF-QC (B1-P05::TRANSACTION_DB)

## Alignment check vs domain model

- `subscription` implements: `subscription_id`, `tenant_id`, `account_id`, `quote_id`, `external_subscription_ref`, `plan_code`, `status`, `start_date`, `end_date`, `renewal_date`, `created_at`. (+ `updated_at` for operational consistency)
- `invoice_summary` implements: `invoice_summary_id`, `tenant_id`, `subscription_id`, `external_invoice_ref`, `invoice_number`, `amount_due`, `amount_paid`, `currency`, `status`, `due_date`, `issued_at`. (+ `created_at`, `updated_at`)
- `payment_event` implements: `payment_event_id`, `tenant_id`, `subscription_id`, `invoice_summary_id`, `external_payment_ref`, `event_type`, `amount`, `currency`, `event_time`, `status`. (+ `created_at`)

Result: **match achieved**.

## Relation completeness check

- `Subscription` 1-N `InvoiceSummary`: FK on `invoice_summary.subscription_id` + tenant-safe composite FK.
- `Subscription` 1-N `PaymentEvent`: optional FK on `payment_event.subscription_id` + tenant-safe composite FK.
- `InvoiceSummary` 1-N `PaymentEvent`: optional FK on `payment_event.invoice_summary_id` + tenant-safe composite FK.
- Tenant isolation: mandatory `tenant_id` for all domain tables and outbox/idempotency tables.

Result: **no missing in-domain relations**.

## Architecture conformance check

- Domain-owned DB boundary preserved: no hard FKs to cross-service entities (`account_id`, `quote_id` left as external references).
- Transactional outbox included for reliable event publication.
- Idempotency ledger included for webhook/event replay safety.

Result: **aligned with data architecture guidance**.

## Score

**10/10** after align -> re-check loop.
