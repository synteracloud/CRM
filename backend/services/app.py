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

import asyncio
import contextlib
import json
from datetime import date, datetime, timezone
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

import uuid as _uuid_mod

from fastapi import FastAPI, HTTPException, Request
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

from services.followup.http.public import router as followup_public_router
from services.conversation.http.public import router as conversation_public_router
from services.collections.http.public import router as collections_public_router
from services.activity.http.public import router as activity_public_router
from services.activation.http.public import router as activation_public_router
from services.core.execution.http.public import router as dlq_public_router
from services.territories.http.public import router as territories_public_router
from services.workflows.http.public import router as workflows_public_router
from services.partners.http.public import router as partners_public_router
from services.ai.http.public import router as ai_public_router
from services.campaigns.http.public import router as campaigns_public_router
from services.cases.http.public import router as cases_public_router
from services.inbox.http.public import router as inbox_public_router

# Public router singleton injectors (P3-B: share instances with internal routers)
from services.activity.http.public import set_engine as set_activity_public_engine
from services.collections.http.public import set_service as set_collections_public_service
from services.activation.http.public import set_orchestrator as set_activation_orchestrator
from services.core.execution.http.public import set_plane as set_execution_plane
from services.activation.service import ActivationOrchestrator
from services.core.execution.control_plane import ExecutionControlPlane

logger = logging.getLogger(__name__)


# ── Background daily summary scheduler (MR-004) ───────────────────────────────

async def _daily_summary_scheduler(stop_event: asyncio.Event) -> None:
    """Background task: sends a WhatsApp daily activity summary to managers.

    Fires once per day at DAILY_SUMMARY_UTC_HOUR (default 03:00 UTC = 08:00 PKT).
    Uses a date-keyed sentinel to prevent duplicate sends within the same day.
    Operates in dry-run mode (log only) when DAILY_SUMMARY_ENABLED=false or when
    the messaging engine is not configured.
    """
    from services.summary.daily_summary import send_daily_summary

    ENABLED       = os.getenv("DAILY_SUMMARY_ENABLED", "true").lower() != "false"
    TARGET_HOUR   = int(os.getenv("DAILY_SUMMARY_UTC_HOUR", "3"))   # 08:00 PKT
    OWNER_PHONE   = os.getenv("DAILY_SUMMARY_OWNER_PHONE", "")
    TENANT_ID     = os.getenv("DAILY_SUMMARY_TENANT_ID",  "tenant-dev-001")
    LANG          = os.getenv("DAILY_SUMMARY_LANG",       "en")

    last_sent_date: date | None = None

    while not stop_event.is_set():
        await asyncio.sleep(60)
        if stop_event.is_set():
            break

        if not ENABLED:
            continue

        now = datetime.now(timezone.utc)
        if now.hour != TARGET_HOUR:
            continue
        if last_sent_date == now.date():
            continue  # already sent today

        logger.info("daily_summary_scheduler: firing for tenant=%s date=%s", TENANT_ID, now.date())
        try:
            from services.db import _get_engine
            _, SessionLocal = _get_engine()
            db = SessionLocal()
            try:
                sent = send_daily_summary(
                    tenant_id=TENANT_ID,
                    owner_phone=OWNER_PHONE,
                    lang=LANG,
                    db=db,
                    messaging_engine=None,   # no live adapter wired in dev
                )
                if sent:
                    last_sent_date = now.date()
                    logger.info("daily_summary_scheduler: sent for date=%s", now.date())
            finally:
                db.close()
        except Exception:
            logger.exception("daily_summary_scheduler: error during send")


# ── Background overdue scanner (P2-B) ─────────────────────────────────────────

async def _overdue_scanner(stop_event: asyncio.Event) -> None:
    """Background task: marks pending follow-ups past due_at as overdue every 60 s."""
    from services.db import _get_engine
    from services.followup.overdue import scan_overdue_tasks
    while not stop_event.is_set():
        await asyncio.sleep(60)
        if stop_event.is_set():
            break
        try:
            _, SessionLocal = _get_engine()
            db = SessionLocal()
            try:
                count = scan_overdue_tasks(db)
                if count:
                    logger.info("overdue_scanner: marked %d tasks overdue", count)
            finally:
                db.close()
        except Exception:
            logger.exception("overdue_scanner: error in scan cycle")


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

    # Inject into internal HTTP router modules
    set_activity_engine(activity_engine)
    set_followup_engine(followup_engine)
    set_collections_service(collections_svc)
    set_sync_service(sync_svc)

    # P3-B: wire public routers — share same singletons so internal+public see the same state.
    # Skipped during tests (PYTEST_CURRENT_TEST is set by pytest) so test autouse fixtures
    # retain full control of module-level singletons via set_*() injection.
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        activation_orchestrator = ActivationOrchestrator()
        execution_plane = ExecutionControlPlane()
        set_activity_public_engine(activity_engine)
        set_collections_public_service(collections_svc)
        set_activation_orchestrator(activation_orchestrator)
        set_execution_plane(execution_plane)

    logger.info("services.app: all service singletons wired")

    # P2-B: start background overdue scanner
    stop_scanner = asyncio.Event()
    scanner_task = asyncio.create_task(_overdue_scanner(stop_scanner))

    # MR-004: start daily WhatsApp summary scheduler
    stop_summary = asyncio.Event()
    summary_task = asyncio.create_task(_daily_summary_scheduler(stop_summary))

    yield  # ── application runs here ──────────────────────────────────────────

    # Stop background tasks cleanly
    stop_scanner.set()
    scanner_task.cancel()
    with contextlib.suppress(asyncio.CancelledError, Exception):
        await scanner_task

    stop_summary.set()
    summary_task.cancel()
    with contextlib.suppress(asyncio.CancelledError, Exception):
        await summary_task

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


@app.post("/internal/migrate")
def run_migrations(secret: str = "") -> dict:
    """One-shot Alembic migration endpoint — only runs when MIGRATE_SECRET matches."""
    import os, subprocess, sys
    expected = os.getenv("MIGRATE_SECRET", "")
    if not expected or secret != expected:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Invalid or missing migration secret")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True, text=True, timeout=120,
            env={**os.environ},
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-1000:] if result.stderr else "",
        }
    except Exception as e:
        return {"returncode": -1, "error": str(e)}


# ── Mount internal routers ────────────────────────────────────────────────────
# All routes are under /internal to signal they are not public-facing.

app.include_router(activity_router,       prefix="/internal")
app.include_router(followup_router,       prefix="/internal")
app.include_router(collections_router,    prefix="/internal")
app.include_router(conversation_router,   prefix="/internal")
app.include_router(sync_router,           prefix="/internal")
app.include_router(followup_public_router)       # /api/v1/followups
app.include_router(conversation_public_router)  # /api/v1/webhooks/whatsapp + /api/v1/conversations
app.include_router(collections_public_router)   # /api/v1/invoices + /api/v1/payments/callback
app.include_router(activity_public_router)      # /api/v1/activities
app.include_router(activation_public_router)    # /api/v1/activation
app.include_router(dlq_public_router)           # /api/v1/admin/dead-letters
app.include_router(territories_public_router)   # /api/v1/territories
app.include_router(workflows_public_router)     # /api/v1/workflows
app.include_router(partners_public_router)      # /api/v1/partners + /api/v1/deal-registrations
app.include_router(ai_public_router)            # /api/v1/ai/*
app.include_router(campaigns_public_router)     # /api/v1/campaigns + /api/v1/segments + /api/v1/templates
app.include_router(cases_public_router)         # /api/v1/cases
app.include_router(inbox_public_router)         # /api/v1/inbox/*


# ── Global exception handlers ─────────────────────────────────────────────────

_STATUS_CODE_MAP: dict[int, str] = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    429: "rate_limited",
    500: "internal_error",
    503: "service_unavailable",
}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = _STATUS_CODE_MAP.get(exc.status_code, "error")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {"code": code, "message": str(exc.detail) if exc.detail else ""},
            "meta": {"request_id": str(_uuid_mod.uuid4())},
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {"code": "internal_error", "message": "An unexpected error occurred."},
            "meta": {"request_id": str(_uuid_mod.uuid4())},
        },
    )
