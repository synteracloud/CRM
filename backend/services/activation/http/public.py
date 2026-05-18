"""Public REST endpoints for tenant activation orchestration.

Spec: backend/docs/activation-model.md
API standards: backend/docs/api-standards.md

Routes:
    POST /api/v1/activation/start        — start activation session (JWT)
    POST /api/v1/activation/whatsapp-sim — simulate first WhatsApp inbound (JWT)
    POST /api/v1/activation/move-deal    — move a sample deal to next stage (JWT)
    GET  /api/v1/activation/status       — get activation metrics (JWT)
"""

from __future__ import annotations

import uuid
from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from services.activation.service import ActivationOrchestrator
from services.auth.jwt_deps import TokenClaims, get_current_user

router = APIRouter(tags=["activation"])

_orchestrator = ActivationOrchestrator()


def set_orchestrator(orch: ActivationOrchestrator) -> None:
    global _orchestrator  # noqa: PLW0603
    _orchestrator = orch


def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


# ── Request schemas ───────────────────────────────────────────────────────────


class WhatsAppSimRequest(BaseModel):
    contact_id: str = "c1"


class MoveDealRequest(BaseModel):
    deal_id: str
    to_stage: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/api/v1/activation/start", status_code=status.HTTP_201_CREATED)
def start_activation(
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Start the <10-minute activation path for a new tenant.

    Seeds sample data (5 contacts, 4 deals), creates default pipeline,
    and advances state to SAMPLE_DATA_READY immediately.
    """
    if claims.tenant_id in _orchestrator._sessions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Activation already started for this tenant",
        )
    try:
        snapshot = _orchestrator.start(claims.tenant_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return {
        "data": {
            "session_id": snapshot.session.session_id,
            "state": snapshot.session.state.value,
            "pipeline": {
                "pipeline_id": snapshot.pipeline.pipeline_id,
                "stages": list(snapshot.pipeline.stages),
            },
            "sample_contacts": len(snapshot.contacts),
            "sample_deals": len(snapshot.deals),
            "checklist": [
                {"key": s.key, "label": s.label, "completed": s.completed}
                for s in snapshot.session.checklist
            ],
        },
        "meta": _meta(),
    }


@router.post("/api/v1/activation/whatsapp-sim")
def simulate_whatsapp(
    body: WhatsAppSimRequest,
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Simulate first WhatsApp inbound to tick the whatsapp_test checklist step."""
    try:
        _orchestrator.simulate_whatsapp_inbound(claims.tenant_id, body.contact_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    session = _orchestrator._sessions[claims.tenant_id]
    return {
        "data": {
            "state": session.state.value,
            "first_inbound_at": session.first_inbound_at.isoformat() if session.first_inbound_at else None,
        },
        "meta": _meta(),
    }


@router.post("/api/v1/activation/move-deal")
def move_deal(
    body: MoveDealRequest,
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Move a sample deal to the next stage to trigger the Aha moment."""
    try:
        deal = _orchestrator.move_deal_stage(claims.tenant_id, body.deal_id, body.to_stage)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    session = _orchestrator._sessions[claims.tenant_id]
    return {
        "data": {
            "deal_id": deal.deal_id,
            "stage": deal.stage,
            "state": session.state.value,
            "aha_reached": session.aha_at is not None,
        },
        "meta": _meta(),
    }


@router.get("/api/v1/activation/status")
def activation_status(
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Return activation metrics for the authenticated tenant."""
    try:
        metrics = _orchestrator.metrics(claims.tenant_id)
        session = _orchestrator._sessions[claims.tenant_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activation not started for this tenant",
        )
    checklist = [
        {"key": s.key, "label": s.label, "completed": s.completed}
        for s in session.checklist
    ]
    return {
        "data": {
            "state": session.state.value,
            "checklist": checklist,
            "metrics": {
                "time_to_pipeline_ready_seconds": metrics.time_to_pipeline_ready_seconds,
                "time_to_whatsapp_ready_seconds": metrics.time_to_whatsapp_ready_seconds,
                "time_to_first_inbound_seconds": metrics.time_to_first_inbound_seconds,
                "time_to_first_stage_move_seconds": metrics.time_to_first_stage_move_seconds,
                "time_to_aha_seconds": metrics.time_to_aha_seconds,
            },
        },
        "meta": _meta(),
    }
