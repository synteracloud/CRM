"""Payment event and ledger store implementations for the collections engine.

These stores implement the interfaces expected by record_payment_event_uow in
services/core/execution/transactions.py.  They own their own storage and are
injected into CollectionsService, making them swap-ready for DB-backed
implementations (e.g. a Python asyncpg client wrapping transaction_db.payment
and transaction_db.payment_status_history) without changes to the service.

Docs: docs/collections-engine-model.md
      db/transaction_db/schema.sql — payment, payment_status_history tables
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .entities import Payment


# ── Protocols (interface contracts) ──────────────────────────────────────────

@runtime_checkable
class EventStore(Protocol):
    """Append-only store for payment events.  UoW compensation calls delete."""

    def append(self, data: dict) -> dict:
        """Persist payment event; return dict containing at least 'event_id'."""
        ...

    def delete(self, event_id: str) -> None:
        """Compensate (roll back) an appended event by its event_id."""
        ...

    def get(self, payment_id: str) -> Payment | None:
        """Retrieve a payment by its ID; returns None if not found."""
        ...

    def all(self) -> dict[str, Payment]:
        """Return all payments keyed by payment_id."""
        ...


@runtime_checkable
class LedgerStore(Protocol):
    """Idempotency ledger for provider transactions.  UoW compensation calls delete."""

    def append(self, entry: dict) -> dict:
        """Record ledger entry; return entry dict containing at least 'ledger_id'."""
        ...

    def delete(self, ledger_id: str) -> None:
        """Compensate a ledger entry by its ledger_id."""
        ...

    def contains(self, key: tuple) -> bool:
        """Return True if the idempotency key has already been recorded."""
        ...


# ── In-memory implementations ─────────────────────────────────────────────────

class InMemoryPaymentEventStore:
    """In-memory EventStore — suitable for tests and single-process deployments.

    Swap for a DB-backed implementation (asyncpg / psycopg2 wrapping
    transaction_db.payment_event) to gain persistence across restarts.
    """

    def __init__(self) -> None:
        self._payments: dict[str, Payment] = {}

    def append(self, data: dict) -> dict:
        payment: Payment = data["payment"]
        self._payments[payment.payment_id] = payment
        return {"event_id": payment.payment_id, **data}

    def delete(self, event_id: str) -> None:
        self._payments.pop(event_id, None)

    def get(self, payment_id: str) -> Payment | None:
        return self._payments.get(payment_id)

    def all(self) -> dict[str, Payment]:
        return dict(self._payments)


class InMemoryPaymentLedgerStore:
    """In-memory LedgerStore — idempotency key deduplication for provider txns.

    Swap for a DB-backed implementation wrapping transaction_db.payment_event's
    (tenant_id, external_payment_ref) UNIQUE constraint for true distributed dedup.
    """

    def __init__(self) -> None:
        self._keys: set[tuple] = set()
        self._entries: dict[str, dict] = {}

    def append(self, entry: dict) -> dict:
        self._keys.add(entry["key"])
        self._entries[entry["ledger_id"]] = entry
        return entry

    def delete(self, ledger_id: str) -> None:
        removed = self._entries.pop(ledger_id, None)
        if removed:
            self._keys.discard(removed.get("key"))

    def contains(self, key: tuple) -> bool:
        return key in self._keys
