"""Public REST endpoints for AI / Predictive Models domain.

Spec: backend/docs/domain/ai-predictive-models.md
API standards: backend/docs/api-standards.md

Routes:
    GET    /api/v1/ai/scores/leads
    GET    /api/v1/ai/scores/leads/{lead_id}
    POST   /api/v1/ai/scores/leads/{lead_id}/recompute
    GET    /api/v1/ai/predictions/churn
    GET    /api/v1/ai/predictions/churn/{account_id}
    GET    /api/v1/ai/estimates/clv
    GET    /api/v1/ai/estimates/clv/{account_id}
    GET    /api/v1/ai/copilot/suggestions
    POST   /api/v1/ai/copilot/suggestions/{suggestion_id}/dismiss
    POST   /api/v1/ai/copilot/suggestions/{suggestion_id}/action
    POST   /api/v1/ai/copilot/query
    GET    /api/v1/ai/models
    GET    /api/v1/ai/models/{model_key}
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.models.ai_scores import (
    ChurnPrediction,
    CLVEstimate,
    CopilotSuggestion,
    LeadScore,
)
from services.ai.service import AIService
from services.ai.entities import SCORING_MODELS

router = APIRouter(tags=["ai"])

_svc = AIService()

PRIORITY_WEIGHT = {"urgent": 4, "high": 3, "medium": 2, "low": 1}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


def _lead_score_dict(s: LeadScore) -> dict[str, Any]:
    return {
        "score_id":         s.score_id,
        "tenant_id":        s.tenant_id,
        "lead_id":          s.lead_id,
        "model_id":         s.model_id,
        "score":            s.score,
        "score_band":       s.score_band,
        "trend":            s.trend,
        "trend_delta":      s.trend_delta,
        "top_drivers":      s.top_drivers,
        "confidence_score": float(s.confidence_score) if s.confidence_score is not None else None,
        "is_stale":         s.is_stale,
        "computed_at":      s.computed_at.isoformat() if s.computed_at else None,
        "created_at":       s.created_at.isoformat() if s.created_at else None,
    }


def _churn_dict(p: ChurnPrediction) -> dict[str, Any]:
    return {
        "prediction_id":     p.prediction_id,
        "tenant_id":         p.tenant_id,
        "account_id":        p.account_id,
        "model_id":          p.model_id,
        "churn_probability": float(p.churn_probability) if p.churn_probability is not None else None,
        "risk_band":         p.risk_band,
        "top_drivers":       p.top_drivers,
        "recommended_action": p.recommended_action,
        "confidence_score":  float(p.confidence_score) if p.confidence_score is not None else None,
        "evidence_anchor":   p.evidence_anchor,
        "is_stale":          p.is_stale,
        "computed_at":       p.computed_at.isoformat() if p.computed_at else None,
        "created_at":        p.created_at.isoformat() if p.created_at else None,
    }


def _clv_dict(e: CLVEstimate) -> dict[str, Any]:
    return {
        "estimate_id":        e.estimate_id,
        "tenant_id":          e.tenant_id,
        "account_id":         e.account_id,
        "model_id":           e.model_id,
        "estimated_clv":      float(e.estimated_clv) if e.estimated_clv is not None else None,
        "clv_horizon_months": e.clv_horizon_months,
        "confidence_score":   float(e.confidence_score) if e.confidence_score is not None else None,
        "evidence_anchor":    e.evidence_anchor,
        "is_stale":           e.is_stale,
        "computed_at":        e.computed_at.isoformat() if e.computed_at else None,
        "created_at":         e.created_at.isoformat() if e.created_at else None,
    }


def _suggestion_dict(s: CopilotSuggestion) -> dict[str, Any]:
    return {
        "suggestion_id":    s.suggestion_id,
        "tenant_id":        s.tenant_id,
        "target_user_id":   s.target_user_id,
        "suggestion_type":  s.suggestion_type,
        "priority":         s.priority,
        "title":            s.title,
        "body":             s.body,
        "action_label":     s.action_label,
        "action_href":      s.action_href,
        "evidence_anchor":  s.evidence_anchor,
        "entity_type":      s.entity_type,
        "entity_id":        s.entity_id,
        "confidence_score": float(s.confidence_score) if s.confidence_score is not None else None,
        "is_dismissed":     s.is_dismissed,
        "dismissed_at":     s.dismissed_at.isoformat() if s.dismissed_at else None,
        "is_actioned":      s.is_actioned,
        "actioned_at":      s.actioned_at.isoformat() if s.actioned_at else None,
        "expires_at":       s.expires_at.isoformat() if s.expires_at else None,
        "created_at":       s.created_at.isoformat() if s.created_at else None,
        "updated_at":       s.updated_at.isoformat() if s.updated_at else None,
    }


def _get_lead_score_or_404(lead_id: str, tenant_id: str, db: Session) -> LeadScore:
    row = db.execute(
        select(LeadScore)
        .where(LeadScore.tenant_id == tenant_id, LeadScore.lead_id == lead_id)
        .order_by(LeadScore.created_at.desc())
    ).scalars().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead score not found")
    return row


# ── Request schemas ───────────────────────────────────────────────────────────

class CopilotQueryRequest(BaseModel):
    query: str


# ── Lead Score Endpoints ──────────────────────────────────────────────────────

@router.get("/api/v1/ai/scores/leads")
def list_lead_scores(
    score_band: Optional[str] = Query(None),
    lead_id: Optional[str] = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(LeadScore).where(LeadScore.tenant_id == claims.tenant_id)
    if score_band is not None:
        q = q.where(LeadScore.score_band == score_band)
    if lead_id is not None:
        q = q.where(LeadScore.lead_id == lead_id)
    q = q.order_by(LeadScore.score.desc())
    rows = db.execute(q).scalars().all()
    return {"data": [_lead_score_dict(r) for r in rows], "meta": _meta()}


@router.get("/api/v1/ai/scores/leads/{lead_id}")
def get_lead_score(
    lead_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = _get_lead_score_or_404(lead_id, claims.tenant_id, db)
    return {"data": _lead_score_dict(row), "meta": _meta()}


@router.post("/api/v1/ai/scores/leads/{lead_id}/recompute")
def recompute_lead_score(
    lead_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = _get_lead_score_or_404(lead_id, claims.tenant_id, db)
    now = datetime.now(timezone.utc)
    row.is_stale = False
    row.computed_at = now
    db.commit()
    db.refresh(row)
    return {"data": _lead_score_dict(row), "meta": _meta()}


# ── Churn Prediction Endpoints ────────────────────────────────────────────────

@router.get("/api/v1/ai/predictions/churn")
def list_churn_predictions(
    risk_band: Optional[str] = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(ChurnPrediction).where(ChurnPrediction.tenant_id == claims.tenant_id)
    if risk_band is not None:
        q = q.where(ChurnPrediction.risk_band == risk_band)
    q = q.order_by(ChurnPrediction.churn_probability.desc())
    rows = db.execute(q).scalars().all()
    return {"data": [_churn_dict(r) for r in rows], "meta": _meta()}


@router.get("/api/v1/ai/predictions/churn/{account_id}")
def get_churn_prediction(
    account_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = db.execute(
        select(ChurnPrediction)
        .where(
            ChurnPrediction.tenant_id == claims.tenant_id,
            ChurnPrediction.account_id == account_id,
        )
        .order_by(ChurnPrediction.created_at.desc())
    ).scalars().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Churn prediction not found")
    return {"data": _churn_dict(row), "meta": _meta()}


# ── CLV Estimate Endpoints ────────────────────────────────────────────────────

@router.get("/api/v1/ai/estimates/clv")
def list_clv_estimates(
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = (
        select(CLVEstimate)
        .where(CLVEstimate.tenant_id == claims.tenant_id)
        .order_by(CLVEstimate.estimated_clv.desc())
    )
    rows = db.execute(q).scalars().all()
    return {"data": [_clv_dict(r) for r in rows], "meta": _meta()}


@router.get("/api/v1/ai/estimates/clv/{account_id}")
def get_clv_estimate(
    account_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = db.execute(
        select(CLVEstimate)
        .where(
            CLVEstimate.tenant_id == claims.tenant_id,
            CLVEstimate.account_id == account_id,
        )
        .order_by(CLVEstimate.created_at.desc())
    ).scalars().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CLV estimate not found")
    return {"data": _clv_dict(row), "meta": _meta()}


# ── Copilot Suggestion Endpoints ──────────────────────────────────────────────

@router.get("/api/v1/ai/copilot/suggestions")
def list_suggestions(
    priority: Optional[str] = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(CopilotSuggestion).where(
        CopilotSuggestion.tenant_id == claims.tenant_id,
        CopilotSuggestion.is_dismissed.is_(False),
    )
    if priority is not None:
        q = q.where(CopilotSuggestion.priority == priority)
    rows = db.execute(q).scalars().all()
    # Sort by priority weight descending
    rows_sorted = sorted(rows, key=lambda s: PRIORITY_WEIGHT.get(s.priority, 0), reverse=True)
    return {"data": [_suggestion_dict(r) for r in rows_sorted], "meta": _meta()}


@router.post("/api/v1/ai/copilot/suggestions/{suggestion_id}/dismiss")
def dismiss_suggestion(
    suggestion_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = db.execute(
        select(CopilotSuggestion).where(
            CopilotSuggestion.tenant_id == claims.tenant_id,
            CopilotSuggestion.suggestion_id == suggestion_id,
        )
    ).scalars().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
    now = datetime.now(timezone.utc)
    row.is_dismissed = True
    row.dismissed_at = now
    row.updated_at = now
    db.commit()
    db.refresh(row)
    return {"data": _suggestion_dict(row), "meta": _meta()}


@router.post("/api/v1/ai/copilot/suggestions/{suggestion_id}/action")
def action_suggestion(
    suggestion_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    row = db.execute(
        select(CopilotSuggestion).where(
            CopilotSuggestion.tenant_id == claims.tenant_id,
            CopilotSuggestion.suggestion_id == suggestion_id,
        )
    ).scalars().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
    now = datetime.now(timezone.utc)
    row.is_actioned = True
    row.actioned_at = now
    row.updated_at = now
    db.commit()
    db.refresh(row)
    return {"data": _suggestion_dict(row), "meta": _meta()}


# ── Copilot Query Endpoint ────────────────────────────────────────────────────

@router.post("/api/v1/ai/copilot/query")
def copilot_query(
    body: CopilotQueryRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = _svc.handle_query(body.query, claims.tenant_id)
    return {"data": result, "meta": _meta()}


# ── Model Registry Endpoints ──────────────────────────────────────────────────

@router.get("/api/v1/ai/models")
def list_models(
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return {"data": SCORING_MODELS, "meta": _meta()}


@router.get("/api/v1/ai/models/{model_key}")
def get_model(
    model_key: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    model = _svc.get_model(model_key)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    return {"data": model, "meta": _meta()}
