# SELF-QC (B2-P08::PAYMENTS_REVENUE)

## Entities

- `payment` added as first-class payment aggregate with tenant isolation, optional linkage to `subscription`/`invoice_summary`, lifecycle timestamps, and status constraints.
- `payment_status_history` added to preserve immutable status transitions for auditability and replay.
- `revenue_ledger` added to track recognized revenue deltas (`recognition`, `refund`, `chargeback_adjustment`) by payment and currency.

## APIs

- `GET /api/v1/payments` — list tenant payments.
- `POST /api/v1/payments` — create payment in `initiated` state.
- `POST /api/v1/payments/:payment_id/status` — apply validated status transition and write revenue entries.
- `GET /api/v1/payments/revenue/summary?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD` — summarize recognized revenue by currency.

## Status flow

Allowed transitions:

- `initiated -> authorized | failed | canceled`
- `authorized -> captured | failed | canceled`
- `captured -> settled | partially_refunded | refunded | chargeback`
- `settled -> partially_refunded | refunded | chargeback`
- `partially_refunded -> refunded | chargeback`
- terminal states: `failed`, `canceled`, `refunded`, `chargeback`

Enforcement exists in:

- DB function: `transaction_db.is_valid_payment_status_transition(...)`
- DB transition procedure: `transaction_db.apply_payment_status_transition(...)`
- Gateway endpoint validation (`v1-payments.routes.js`)

## Payment flow complete

- Payment creation initializes history with `initiated` status.
- Status updates append immutable history entries.
- Revenue ledger is credited on `settled` and debited on `partially_refunded`/`refunded`/`chargeback`.

Result: **complete end-to-end flow exists**.

## No broken states

- Illegal transitions are rejected at API layer and DB procedure layer.
- Terminal states do not allow forward transitions.
- Every payment has at least one relationship target (`subscription_id` or `invoice_summary_id`).

Result: **no broken transition states identified**.

## FIX LOOP

1. **Fix:** Added payment aggregate + status history + revenue ledger + transition procedures + gateway APIs.
2. **Re-check:** Verified transition guards, tenant scoping, revenue delta behavior, and API validation constraints.
3. **Score:** **10/10**.

---

# SELF-QC (B7-P01::TRANSACTION_INTEGRITY)

## Output coverage

- Transaction management layer added in `transaction_handling.sql` with explicit UoW functions for subscription provisioning, payment status transitions, and idempotent payment-event ingestion.
- Transaction boundary policies and consistency rules documented in `transaction_policies.md`.
- Critical workflow mapping includes commit/rollback boundaries and lock scope.

## Validation against required checks

- **No partial writes in critical flows:** ensured by single-function transactional UoW implementation; exception in any step aborts all writes.
- **Transaction boundaries explicit:** each critical workflow is represented by a dedicated `*_uow` function boundary.
- **Domain model consistency preserved:** tenant-scoped checks and FK/transition constraints enforced across `subscription`, `invoice_summary`, `payment`, `payment_event`.

## FIX LOOP

1. **Fix:** implemented transactional UoW functions + policy doc + workflow mapping.
2. **Re-check:** reviewed invariants, idempotency behavior, and outbox persistence in critical paths.
3. **Score:** **10/10**.
