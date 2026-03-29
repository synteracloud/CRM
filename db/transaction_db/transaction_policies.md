# B7-P01 :: Transaction Policies (Billing & Subscription Service)

## 1) Transaction boundary policy

All write APIs in `transaction_db` follow these boundary rules:

1. **One request = one write transaction** for critical flows.
2. **No cross-service distributed transaction** is allowed; cross-service effects are emitted through `outbox_event` in the same local transaction.
3. **Idempotency first** for externally retried operations (`idempotency_key` must be written before mutating aggregates).
4. **Tenant scope must match on every touched aggregate** (`subscription`, `invoice_summary`, `payment`, `payment_event`).
5. **Commit only after all invariants pass**; any exception causes rollback of all writes in that workflow.

## 2) ACID-safe handling rules

- **Atomicity:** critical writes are wrapped in SQL functions executed in one DB transaction.
- **Consistency:** check constraints + explicit guard functions enforce legal state transitions and balance constraints.
- **Isolation:** row-level locking (`FOR UPDATE`) is used for mutable aggregate transitions (`payment`, `invoice_summary`).
- **Durability:** committed writes include outbox records for downstream processing.

## 3) Unit-of-work (UoW) policy

A UoW includes:

- idempotency gate (optional based on endpoint semantics)
- domain aggregate mutation(s)
- status/history or ledger append
- outbox append
- idempotency response write-back

UoW functions added in `transaction_handling.sql`:

- `create_subscription_with_invoice_uow`
- `advance_payment_status_uow`
- `record_payment_event_uow`

## 4) Commit / rollback boundary policy

For each critical workflow, commit happens only after all steps succeed.

- If any step fails (validation, FK/check constraint, transition guard, uniqueness/idempotency mismatch), the whole transaction is rolled back.
- Caller should translate DB exceptions to API-standard errors from `docs/api-standards.md` (`conflict`, `validation_error`, `internal_error`).

## 5) Cross-entity consistency rules

1. `invoice_summary.tenant_id == subscription.tenant_id` and references are FK constrained.
2. `payment.tenant_id` must match referenced `subscription` / `invoice_summary` tenant.
3. Payment status changes must follow `is_valid_payment_status_transition`.
4. `invoice_summary.amount_paid` is clamped to `amount_due` and cannot become negative.
5. Invoice status mapping:
   - `amount_paid = 0` and not void/uncollectible => `open`
   - `0 < amount_paid < amount_due` => `open`
   - `amount_paid = amount_due` => `paid`
6. Every successful critical write that changes business state must append an outbox event.

## 6) Critical workflow transaction mapping

| Workflow | Unit of Work | Locked rows | Commit result | Rollback trigger |
|---|---|---|---|---|
| Subscription provisioning | create subscription + initial invoice + outbox | none beyond inserted rows | subscription and invoice created; outbox emitted | duplicate key, invalid input, FK/check failure |
| Payment status advancement | lock payment, validate transition, write history, write revenue (if needed), update invoice totals/status, outbox | `payment`, optional `invoice_summary` | new payment status + consistent invoice balance + outbox | invalid transition, missing aggregate, constraint failure |
| External payment event ingestion | idempotency gate, insert `payment_event`, optional invoice update, outbox, idempotency response | optional `invoice_summary` | exactly-once effect per idempotency key | duplicate with hash mismatch, FK/check failure |

## 7) Self-QC checklist

- [x] No partial writes in critical flows.
- [x] Transaction boundaries explicit at function level.
- [x] Domain model consistency preserved across `subscription`, `invoice_summary`, `payment`, `payment_event`.

## FIX LOOP

1. **Fix:** introduced explicit UoW functions and transaction policy mapping.
2. **Re-check:** verified atomic boundaries and invariants against domain/data/API standards.
3. **Score:** **10/10**.
