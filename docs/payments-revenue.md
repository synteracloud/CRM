# B2-P08::PAYMENTS_REVENUE

## Entities

### Payment

- `payment_id (PK)`
- `tenant_id (FK->TenantRef)`
- `subscription_id (FK->Subscription, nullable)`
- `invoice_summary_id (FK->InvoiceSummary, nullable)`
- `external_payment_ref`
- `payment_method_type` (`card|bank_transfer|wallet|ach|other`)
- `amount`
- `currency`
- `status` (`initiated|authorized|captured|settled|failed|canceled|partially_refunded|refunded|chargeback`)
- lifecycle timestamps (`initiated_at`, `authorized_at`, etc.)
- `created_at`, `updated_at`

### PaymentStatusHistory

- immutable status transition records per payment:
  - `from_status`, `to_status`, `reason`, `changed_at`, `changed_by_user_id`

### RevenueLedger

- revenue delta entries linked to payment:
  - `entry_type` (`recognition|refund|chargeback_adjustment`)
  - `amount_delta`
  - `currency`
  - `recognized_at`

## APIs

- `GET /api/v1/payments`
- `POST /api/v1/payments`
- `POST /api/v1/payments/:payment_id/status`
- `GET /api/v1/payments/revenue/summary?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD`

## Status flow

- `initiated -> authorized | failed | canceled`
- `authorized -> captured | failed | canceled`
- `captured -> settled | partially_refunded | refunded | chargeback`
- `settled -> partially_refunded | refunded | chargeback`
- `partially_refunded -> refunded | chargeback`
- terminal: `failed`, `canceled`, `refunded`, `chargeback`

Transition enforcement:

- DB helper: `is_valid_payment_status_transition`
- DB mutator: `apply_payment_status_transition`
- API guard in `v1-payments.routes.js`

## Revenue tracking behavior

- On `settled`, add positive recognition entry.
- On `partially_refunded`/`refunded`, add negative refund entry.
- On `chargeback`, add negative chargeback adjustment entry.
