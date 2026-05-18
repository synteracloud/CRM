"""Background eviction worker for GlobalIdempotencyLedger.

Docs: docs/global-idempotency.md — "Deduplication window: 24 hours minimum"
      gap-register.md GAP-016

Runs a daemon thread that calls ledger.evict_expired() on a configurable
interval.  Only terminal-status records are evicted; in-progress records
are never touched.

Usage (start once at application boot)::

    from services.core.execution.idempotency import GlobalIdempotencyLedger
    from services.core.execution.eviction_worker import start_eviction_worker

    ledger = GlobalIdempotencyLedger()
    stop = start_eviction_worker(ledger)          # starts daemon thread
    # ... at shutdown:
    stop()                                         # requests graceful stop

Environment variables:
    IDEMPOTENCY_TTL_SECONDS   — record TTL (default: 86400 = 24 h)
    IDEMPOTENCY_EVICT_INTERVAL — sweep interval in seconds (default: 3600 = 1 h)
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Callable

from .idempotency import GlobalIdempotencyLedger

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 86_400.0       # 24 hours
_DEFAULT_INTERVAL = 3_600.0   # 1 hour


def start_eviction_worker(
    ledger: GlobalIdempotencyLedger,
    *,
    ttl_seconds: float | None = None,
    interval_seconds: float | None = None,
) -> Callable[[], None]:
    """Start a background daemon thread that periodically evicts expired records.

    Args:
        ledger: The ledger instance to sweep.
        ttl_seconds: How old a terminal record must be to be evicted.
                     Defaults to IDEMPOTENCY_TTL_SECONDS env var or 86400.
        interval_seconds: How often to run the sweep.
                          Defaults to IDEMPOTENCY_EVICT_INTERVAL env var or 3600.

    Returns:
        A callable that signals the worker to stop (non-blocking).
    """
    ttl = ttl_seconds if ttl_seconds is not None else float(
        os.environ.get("IDEMPOTENCY_TTL_SECONDS", _DEFAULT_TTL)
    )
    interval = interval_seconds if interval_seconds is not None else float(
        os.environ.get("IDEMPOTENCY_EVICT_INTERVAL", _DEFAULT_INTERVAL)
    )

    stop_event = threading.Event()

    def _run() -> None:
        logger.info(
            "idempotency_eviction_worker started ttl=%.0fs interval=%.0fs",
            ttl,
            interval,
        )
        while not stop_event.wait(timeout=interval):
            try:
                evicted = ledger.evict_expired(ttl_seconds=ttl)
                if evicted:
                    logger.info("idempotency_eviction evicted=%d", evicted)
            except Exception:
                logger.exception("idempotency_eviction_worker error — continuing")
        logger.info("idempotency_eviction_worker stopped")

    thread = threading.Thread(target=_run, name="idempotency-eviction", daemon=True)
    thread.start()

    return stop_event.set
