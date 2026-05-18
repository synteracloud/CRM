"""Sync service internal HTTP endpoints.

Docs: docs/offline-sync.md
      gateway/routes/v1-sync.routes.js (gateway consumer)

These routes are NOT exposed to end-users.  The gateway calls them from
the sync route handlers over a trusted internal network.

Mount point (wired in services/app.py — P-019)::
    app.include_router(sync_router, prefix="/internal")

Service lifecycle:
    The _service singleton is the authoritative in-memory instance.
    P-019 wires the shared instance via set_service() at app startup.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from services.sync.service import SyncService

router = APIRouter(tags=["internal"])

_service = SyncService()


def set_service(service: SyncService) -> None:
    """Override the default service singleton.  Called once at service startup."""
    global _service  # noqa: PLW0603
    _service = service


# ── POST /internal/sync/batch ─────────────────────────────────────────────────
class BatchActionRequest(BaseModel):
    entity_type:      str
    entity_id:        str
    op:               str          # create | update | delete
    payload:          dict[str, Any]
    base_version:     int = 0
    client_timestamp: str | None = None
    tenant_id:        str = "default"
    device_id:        str = "default"
    seq_no:           int | None = None


@router.post("/sync/batch")
def batch(body: BatchActionRequest) -> dict:
    """Enqueue an offline action and immediately attempt to sync.

    Called by gateway/routes/v1-sync.routes.js when a client pushes
    pending offline changes on reconnect.

    Response::
        {
          "action_id": str,
          "results": [{ "action_id", "status", "server_version", "conflict_detected" }]
        }
    """
    action = _service.enqueue_action(
        entity_type=body.entity_type,
        entity_id=body.entity_id,
        op=body.op,
        payload=body.payload,
        base_version=body.base_version,
        client_timestamp=body.client_timestamp,
        tenant_id=body.tenant_id,
        device_id=body.device_id,
        seq_no=body.seq_no,
    )

    results = _service.sync_pending()

    return {
        "action_id": action.action_id,
        "results": [
            {
                "action_id":        r.action_id,
                "status":           r.status,
                "server_version":   r.server_version,
                "conflict_detected": r.conflict_detected,
                "resolved_with":    r.resolved_with,
                "message":          r.message,
            }
            for r in results
        ],
    }


# ── GET /internal/sync/status ─────────────────────────────────────────────────
@router.get("/sync/status")
def status() -> dict:
    """Return the current sync reliability report.

    Called by gateway/routes/v1-sync.routes.js GET /sync/status.

    Response::
        { "queued", "synced", "failed", "dead_letter", "conflict_count",
          "data_loss_risk", "alignment_percent", "score" }
    """
    report = _service.reliability_report()
    return {
        "queued":            report.queued,
        "synced":            report.synced,
        "failed":            report.failed,
        "dead_letter":       report.dead_letter,
        "conflict_count":    report.conflict_count,
        "data_loss_risk":    report.data_loss_risk,
        "alignment_percent": report.alignment_percent,
        "score":             report.score,
    }


# ── GET /internal/sync/queue ──────────────────────────────────────────────────
@router.get("/sync/queue")
def queue_snapshot() -> dict:
    """Return the current pending action queue snapshot (debug/ops)."""
    from dataclasses import asdict
    items = _service.queue_snapshot()
    return {"count": len(items), "items": [asdict(a) for a in items]}
