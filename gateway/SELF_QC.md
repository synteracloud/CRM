# SELF-QC

## Standards conformance check

- ✅ Base path uses `/api/v1/...`.
- ✅ Resource naming uses lowercase plural nouns (`users`, `price-books`, `subscriptions`, `invoice-summaries`).
- ✅ Query parameters use snake_case (`page`, `page_size`).
- ✅ JSON keys are snake_case.
- ✅ Unknown properties are rejected.
- ✅ Success envelope is `{ data, meta.request_id }`.
- ✅ Error envelope is `{ error, meta.request_id }`.
- ✅ Canonical error codes are centralized.
- ✅ Rate limiting hook returns `429 rate_limited` envelope.
- ✅ Request ID is always present in response metadata.
- ✅ AuthN requires bearer token with `sub`, `tenant_id`, `exp` claims.
- ✅ RBAC scope checks are enforced per endpoint (`users.*`, `pricing.*`, `billing.*`, `invoices.*`).
- ✅ Tenant isolation guard enforces `x-tenant-id == token.tenant_id`.

## Domain alignment check (B2-P07)

### Entities

- ✅ Pricing model entity surface maps to domain model `PriceBook` with fields:
  `price_book_id`, `tenant_id`, `name`, `currency`, `is_default`, `active_from`, `active_to`.
- ✅ Billing entity surface maps to domain model `Subscription` with fields:
  `subscription_id`, `tenant_id`, `account_id`, `quote_id`, `external_subscription_ref`, `plan_code`, `status`, `start_date`, `end_date`, `renewal_date`, `created_at`.
- ✅ Invoice basics map to domain model `InvoiceSummary` with fields:
  `invoice_summary_id`, `tenant_id`, `subscription_id`, `external_invoice_ref`, `invoice_number`, `amount_due`, `amount_paid`, `currency`, `status`, `due_date`, `issued_at`.

### API surface

- ✅ `GET/POST /api/v1/price-books` for pricing model CRUD basics.
- ✅ `GET/POST /api/v1/subscriptions` for billing entity CRUD basics.
- ✅ `GET/POST /api/v1/invoice-summaries` for invoice basics.

### Pricing consistency check

- ✅ Currency is represented as ISO-style uppercase 3-letter code (`USD`) across pricing and invoice payloads.
- ✅ Invoice `subscription_id` references the billing entity shape.
- ✅ Amount fields are explicit (`amount_due`, `amount_paid`) and never conflict with pricing identifiers.

## FIX LOOP

1. Fix: added pricing, billing, and invoice routes under `/api/v1` with standards-compliant envelopes.
2. Re-check: validated entity fields and naming against `docs/domain-model.md`; validated route patterns/envelopes against `docs/api-standards.md`.
3. Score: **10/10**.
