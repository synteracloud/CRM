# transaction_db

This folder contains schema and migration artifacts for **B1-P05::TRANSACTION_DB**.

## Migration setup

Migrations are ordered and idempotent (`if not exists` where applicable):

1. `migrations/0001_create_transaction_core.up.sql`
2. `migrations/0002_add_outbox_and_idempotency.up.sql`

Rollback order:

1. `migrations/0002_add_outbox_and_idempotency.down.sql`
2. `migrations/0001_create_transaction_core.down.sql`

### Example apply flow (psql)

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/transaction_db/migrations/0001_create_transaction_core.up.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/transaction_db/migrations/0002_add_outbox_and_idempotency.up.sql
```

## Transaction handling

Use database transactions to atomically:

- mutate billing aggregates (`subscription`, `invoice_summary`, `payment_event`)
- append `outbox_event`
- upsert idempotency markers in `idempotency_key`

See `transaction_handling.sql` for concrete transaction-safe procedures.
