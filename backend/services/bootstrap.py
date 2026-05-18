"""Application bootstrap — call once at Python service startup.

Starts background workers, initialises shared singletons, and wires
infrastructure that must be alive before request handling begins.

Docs: gap-register.md GAP-016 (idempotency eviction)
      services/core/execution/eviction_worker.py
      services/core/execution/idempotency.py

Usage (called from FastAPI lifespan — see services/app.py, built in P-019)::

    from services.bootstrap import startup, shutdown

    stop_fns = startup()
    # ... at process shutdown:
    shutdown(stop_fns)

Environment variables consumed:
    IDEMPOTENCY_TTL_SECONDS    — record TTL before eviction (default 86400 = 24 h)
    IDEMPOTENCY_EVICT_INTERVAL — eviction sweep interval in seconds (default 3600 = 1 h)
"""

from __future__ import annotations

import logging
from typing import Callable

from services.core.execution.eviction_worker import start_eviction_worker
from services.core.execution.idempotency import GlobalIdempotencyLedger

logger = logging.getLogger(__name__)

# ── Shared singletons ──────────────────────────────────────────────────────────
# Initialised at startup(); imported by service modules that need them.
# Only access these after startup() has been called.

idempotency_ledger: GlobalIdempotencyLedger | None = None


def startup() -> list[Callable[[], None]]:
    """Initialise singletons and start background workers.

    Returns a list of stop-functions; pass to shutdown() for graceful teardown.
    Call exactly once per process, before serving requests.
    """
    global idempotency_ledger  # noqa: PLW0603

    logger.info("services.bootstrap: starting up")

    # Idempotency ledger — shared across all HTTP handlers
    idempotency_ledger = GlobalIdempotencyLedger()

    # Eviction worker — background daemon thread, runs until stop() is called
    stop_eviction = start_eviction_worker(idempotency_ledger)
    logger.info("services.bootstrap: idempotency eviction worker started")

    return [stop_eviction]


def shutdown(stop_fns: list[Callable[[], None]]) -> None:
    """Signal all background workers to stop.  Non-blocking — workers drain on their own."""
    logger.info("services.bootstrap: shutting down %d worker(s)", len(stop_fns))
    for stop in stop_fns:
        stop()
