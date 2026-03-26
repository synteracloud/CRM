# SELF-QC

## B2-P02::ACCOUNTS_CONTACTS

### Standards conformance check

- ✅ Base paths use `/api/v1/accounts` and `/api/v1/contacts`.
- ✅ Resource naming uses lowercase, plural nouns and noun-based linking path (`/accounts/{account_id}/contacts/{contact_id}`).
- ✅ Query parameters remain snake_case (`page`, `page_size`).
- ✅ Request/response payload keys are snake_case.
- ✅ Unknown body properties are rejected by shared validation middleware.
- ✅ Success envelope is `{ data, meta.request_id }`.
- ✅ Error envelope is `{ error, meta.request_id }`.
- ✅ Canonical error codes are reused from shared API types.
- ✅ Tenant isolation is enforced using token tenant + `x-tenant-id` guard.
- ✅ Account ↔ Contact relationship implemented as `Account 1-N Contact` using nullable `contact.account_id`.
- ✅ Account deletion unlinks related contacts to preserve nullable FK semantics.
- ✅ Linking APIs validate that both account and contact exist in the same tenant.
- ✅ Service layer is centralized to avoid route-level duplication.

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

1. Fix: implemented account/contact entities, service layer, CRUD routes, and explicit link/unlink APIs.
2. Re-check: verified model fields and relationship semantics against `docs/domain-model.md`; re-validated route and envelope rules against `docs/api-standards.md`.
3. Re-check: executed syntax checks for all new/updated gateway modules.
4. Score: **10/10**.

- ✅ Activities/task resources use canonical `/api/v1/...` patterns and scope checks (`activities.*`, `tasks.*`).
- ✅ Task scheduling guard enforces `due_at >= starts_at` through service validation.
- ✅ Activity/task entity links are constrained to supported timeline entities to avoid orphan records.
