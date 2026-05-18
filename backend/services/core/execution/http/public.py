"""Admin REST endpoints for Dead Letter Queue (DLQ) operator operations.

Spec: backend/docs/execution-hardening.md
      backend/docs/global-idempotency.md
API standards: backend/docs/api-standards.md

Routes:
    GET  /api/v1/admin/dead-letters              — list dead-lettered jobs (JWT, admin)
    POST /api/v1/admin/dead-letters/{id}/retry   — claim job for operator retry (JWT, admin)
    POST /api/v1/admin/dead-letters/{id}/requeue — reset job to pending (JWT, admin)
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.core.execution.control_plane import ExecutionControlPlane

router = APIRouter(tags=["admin"])

_plane = ExecutionControlPlane()


def set_plane(p: ExecutionControlPlane) -> None:
    global _plane  # noqa: PLW0603
    _plane = p


def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


def _require_admin(claims: TokenClaims) -> None:
    if claims.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )


def _job_dict(job: Any) -> dict[str, Any]:
    return {
        "job_id": job.job_id,
        "state": job.state,
        "attempts": job.attempts,
        "max_attempts": job.max_attempts,
        "last_error": job.last_error,
        "updated_at": job.updated_at,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/api/v1/admin/dead-letters")
def list_dead_letters(
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """List all jobs in the dead_lettered state. Requires admin role."""
    _require_admin(claims)
    all_jobs = _plane.recovery.snapshot()
    dead = [_job_dict(j) for j in all_jobs.values() if j.state == "dead_lettered"]
    return {"data": dead, "meta": _meta(total=len(dead))}


@router.post("/api/v1/admin/dead-letters/{job_id}/retry")
def retry_dead_letter(
    job_id: str,
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Claim a dead-lettered job for operator retry (transitions to in_progress)."""
    _require_admin(claims)
    jobs = _plane.recovery.snapshot()
    if job_id not in jobs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    job = jobs[job_id]
    if job.state != "dead_lettered":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job is not dead_lettered (current state: {job.state})",
        )
    # Requeue resets dead_lettered → pending; claim then transitions pending → in_progress
    _plane.recovery.requeue(job_id)
    updated = _plane.recovery.claim(job_id)
    return {"data": _job_dict(updated), "meta": _meta()}


@router.post("/api/v1/admin/dead-letters/{job_id}/requeue")
def requeue_dead_letter(
    job_id: str,
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Reset a dead-lettered job to pending so the scheduler can retry it."""
    _require_admin(claims)
    jobs = _plane.recovery.snapshot()
    if job_id not in jobs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    job = jobs[job_id]
    if job.state != "dead_lettered":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Job is not dead_lettered (current state: {job.state})",
        )
    updated = _plane.recovery.requeue(job_id)
    return {"data": _job_dict(updated), "meta": _meta()}
