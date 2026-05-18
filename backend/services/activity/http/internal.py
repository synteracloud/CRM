"""Activity service internal HTTP endpoints.

Docs: docs/observability-audit.md
      gap-register.md GAP-017
      services/activity/engine.py — ActivityControlEngine.verify_chain_integrity()

These routes are NOT exposed to end-users.  They are called by the gateway
(gateway/routes/v1-audit.routes.js GET /audits/chain-check) over a trusted
internal network.

Mount point (wired in services/app.py — P-019)::
    app.include_router(internal_router, prefix="/internal")

Engine lifecycle:
    The _engine singleton below is the authoritative in-memory instance.
    For the chain-check to report real data it must be the same instance used
    by the rest of the activity pipeline.  P-019 will wire this via
    dependency-injection at app startup using services/activity/state.py.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from services.activity.engine import ActivityControlEngine

router = APIRouter(tags=["internal"])

# Module-level engine singleton — replaced at startup via dependency injection
# (see services/activity/state.py, wired by services/app.py in P-019).
_engine = ActivityControlEngine()


def set_engine(engine: ActivityControlEngine) -> None:
    """Override the default engine singleton.  Called once at service startup."""
    global _engine  # noqa: PLW0603
    _engine = engine


# ── GET /internal/chain-check ─────────────────────────────────────────────────
@router.get("/chain-check")
def chain_check(
    tenant_id: str = Query(..., description="Tenant whose audit log chain to verify"),
) -> dict:
    """Verify the audit log hash chain is unbroken for the given tenant.

    Called by gateway/routes/v1-audit.routes.js GET /audits/chain-check.

    Response contract::
        {
          "valid": bool,
          "entries_checked": int,
          "first_broken_seq": int | null,
          "errors": list[str]
        }
    """
    if not tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id is required")

    result = _engine.verify_chain_integrity(tenant_id)
    return result
