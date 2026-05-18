from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Callable, Iterator


@dataclass
class TransactionContext:
    rollback_actions: list[Callable[[], None]] = field(default_factory=list)
    committed: bool = False


class TransactionManager:
    """Simple atomic transaction + compensation coordinator."""

    def __init__(self) -> None:
        self._lock = RLock()

    @contextmanager
    def unit_of_work(self) -> Iterator[TransactionContext]:
        ctx = TransactionContext()
        with self._lock:
            try:
                yield ctx
                ctx.committed = True
            except Exception:
                for action in reversed(ctx.rollback_actions):
                    action()
                raise

    @staticmethod
    def add_compensation(ctx: TransactionContext, action: Callable[[], None]) -> None:
        ctx.rollback_actions.append(action)


# ── Named ACID Unit-of-Work boundaries (docs/execution-hardening.md §3) ──────

@contextmanager
def create_subscription_with_invoice_uow(
    tm: TransactionManager,
    *,
    subscription_store: Any,
    invoice_store: Any,
    subscription_data: dict[str, Any],
    invoice_data: dict[str, Any],
) -> Iterator[dict[str, Any]]:
    """Atomic boundary: persist subscription + first invoice together.

    If invoice creation fails, the subscription insert is compensated (rolled back).
    Yields a result dict that is populated with {'subscription': ..., 'invoice': ...}
    once both writes succeed.

    Usage::
        async with create_subscription_with_invoice_uow(tm, ...) as result:
            # result['subscription'] and result['invoice'] are set
    """
    result: dict[str, Any] = {}
    with tm.unit_of_work() as ctx:
        sub = subscription_store.insert(subscription_data)
        tm.add_compensation(ctx, lambda: subscription_store.delete(sub["subscription_id"]))

        inv = invoice_store.insert({**invoice_data, "subscription_id": sub["subscription_id"]})
        tm.add_compensation(ctx, lambda: invoice_store.delete(inv["invoice_id"]))

        result["subscription"] = sub
        result["invoice"] = inv
        yield result


@contextmanager
def advance_payment_status_uow(
    tm: TransactionManager,
    *,
    payment_store: Any,
    payment_id: str,
    new_status: str,
    invoice_store: Any | None = None,
    invoice_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Atomic boundary: update payment status and optionally mark invoice paid.

    Compensation: reverts payment to its prior status if anything fails after
    the payment write but before the invoice update (or the UoW exit).

    Yields result dict populated with {'payment': ..., 'invoice': ...}.
    """
    result: dict[str, Any] = {}
    with tm.unit_of_work() as ctx:
        prior = payment_store.get(payment_id)
        payment = payment_store.set_status(payment_id, new_status)
        prior_status = prior["status"]
        tm.add_compensation(ctx, lambda: payment_store.set_status(payment_id, prior_status))

        result["payment"] = payment

        if invoice_store is not None and invoice_id is not None:
            prior_inv = invoice_store.get(invoice_id)
            invoice = invoice_store.mark_paid(invoice_id)
            prior_inv_status = prior_inv["status"]
            tm.add_compensation(ctx, lambda: invoice_store.set_status(invoice_id, prior_inv_status))
            result["invoice"] = invoice

        yield result


@contextmanager
def record_payment_event_uow(
    tm: TransactionManager,
    *,
    event_store: Any,
    ledger_store: Any,
    event_data: dict[str, Any],
    ledger_entry: dict[str, Any],
) -> Iterator[dict[str, Any]]:
    """Atomic boundary: append payment event + ledger entry together.

    Both writes must succeed or both are compensated.  The ledger entry is the
    authoritative financial record; the event is the observable side-effect.

    Yields result dict populated with {'event': ..., 'ledger': ...}.
    """
    result: dict[str, Any] = {}
    with tm.unit_of_work() as ctx:
        evt = event_store.append(event_data)
        tm.add_compensation(ctx, lambda: event_store.delete(evt["event_id"]))

        entry = ledger_store.append(ledger_entry)
        tm.add_compensation(ctx, lambda: ledger_store.delete(entry["ledger_id"]))

        result["event"] = evt
        result["ledger"] = entry
        yield result
