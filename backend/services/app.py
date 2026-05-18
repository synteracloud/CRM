"""FastAPI application — Python service layer entry point.

Mounts all internal service routers and manages the service lifecycle.

Docs: pending.md P-019 — Python HTTP layer
      services/bootstrap.py — shared infrastructure startup
      docs/api-standards.md — health check convention

Services exposed under /internal:
    Activity service    → GET  /internal/chain-check
    Followup service    → GET  /internal/leads/{id}/next-action
                          POST /internal/leads/{id}/register
                          POST /internal/process-due
                          GET  /internal/metrics
    Collections service → POST /internal/payments
                          GET  /internal/invoices/{id}
                          POST /internal/invoices/overdue-rollup
    Conversation service→ POST /internal/classify
                          POST /internal/messages
    Sync service        → POST /internal/sync/batch
                          GET  /internal/sync/status
                          GET  /internal/sync/queue

Run with::
    uvicorn services.app:app --host 0.0.0.0 --port 5002

Environment variables:
    PORT                    — HTTP port (default 5002; passed to uvicorn externally)
    IDEMPOTENCY_TTL_SECONDS — record TTL before eviction (default 86400)
    IDEMPOTENCY_EVICT_INTERVAL — eviction sweep interval (default 3600)
"""

from __future__ import annotations

import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator


# ── JSON logging formatter (P-022) ────────────────────────────────────────────
class _JsonFormatter(logging.Formatter):
    """Emit one JSON object per log record — Docker log-driver and CloudWatch friendly."""

    SERVICE = os.getenv("SERVICE_NAME", "crm-python-services")
    ENV     = os.getenv("NODE_ENV", "development")

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level":     record.levelname.lower(),
            "service":   self.SERVICE,
            "env":       self.ENV,
            "logger":    record.name,
            "message":   record.getMessage(),
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry)


def _configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level, handlers=[handler], force=True)


_configure_logging()

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from services.bootstrap import startup, shutdown

# ── Service imports ───────────────────────────────────────────────────────────

from services.activity.engine import ActivityControlEngine
from services.activity.http.internal import router as activity_router
from services.activity.http.internal import set_engine as set_activity_engine

from services.followup.engine import FollowupEnforcementEngine
from services.followup.http.internal import router as followup_router
from services.followup.http.internal import set_engine as set_followup_engine

from services.collections.service import CollectionsService
from services.collections.http.internal import router as collections_router
from services.collections.http.internal import set_service as set_collections_service

from services.conversation.http.internal import router as conversation_router

from services.sync.service import SyncService
from services.sync.http.internal import router as sync_router
from services.sync.http.internal import set_service as set_sync_service

logger = logging.getLogger(__name__)

# ── Lifespan (startup + shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialise all service singletons and background workers on startup.

    Called automatically by FastAPI before the first request is served.
    All set_*() calls inject shared instances into the HTTP router modules
    so every request hits the same in-memory state.
    """
    logger.info("services.app: lifespan startup")

    # Infrastructure (idempotency ledger + eviction worker)
    stop_fns = startup()

    # Instantiate service singletons
    activity_engine    = ActivityControlEngine()
    followup_engine    = FollowupEnforcementEngine()
    collections_svc    = CollectionsService()
    sync_svc           = SyncService()

    # Inject into HTTP router modules
    set_activity_engine(activity_engine)
    set_followup_engine(followup_engine)
    set_collections_service(collections_svc)
    set_sync_service(sync_svc)

    logger.info("services.app: all service singletons wired")

    yield  # ── application runs here ──────────────────────────────────────────

    logger.info("services.app: lifespan shutdown")
    shutdown(stop_fns)


# ── FastAPI application ───────────────────────────────────────────────────────

app = FastAPI(
    title="CRM Python Services",
    description="Internal service layer for followup, collections, activity, conversation, and sync.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> dict:
    """Liveness probe — returns 200 when the process is alive and routers are mounted."""
    return {"status": "ok", "service": "crm-python-services"}


# ── Mount internal routers ────────────────────────────────────────────────────
# All routes are under /internal to signal they are not public-facing.

app.include_router(activity_router,     prefix="/internal")
app.include_router(followup_router,     prefix="/internal")
app.include_router(collections_router,  prefix="/internal")
app.include_router(conversation_router, prefix="/internal")
app.include_router(sync_router,         prefix="/internal")


# ── Global exception handler ──────────────────────────────────────────────────

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )
