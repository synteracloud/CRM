"""Public REST endpoints for Shared Inbox domain.

Spec: backend/docs/domain/shared-inbox.md §7
API standards: backend/docs/api-standards.md

Routes:
    GET    /api/v1/inbox/conversations
    GET    /api/v1/inbox/conversations/{conversation_id}
    POST   /api/v1/inbox/conversations/{conversation_id}/claim
    POST   /api/v1/inbox/conversations/{conversation_id}/handoff
    POST   /api/v1/inbox/conversations/{conversation_id}/messages
    PATCH  /api/v1/inbox/presence
    GET    /api/v1/inbox/queues
    GET    /api/v1/inbox/queues/{queue_id}/stats
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.models.conversations import Conversation, ConversationMessage
from services.db.models.inbox import AgentPresence, ConversationHandoff, InboxQueue
from services.inbox.entities import HandoffReason, PresenceStatus

router = APIRouter(tags=["inbox"])

VALID_PRESENCE_STATUSES = {s.value for s in PresenceStatus}
VALID_HANDOFF_REASONS = {r.value for r in HandoffReason}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


def _handoff_count(conversation_id: str, db: Session) -> int:
    return db.execute(
        select(func.count()).select_from(ConversationHandoff)
        .where(ConversationHandoff.conversation_id == conversation_id)
    ).scalar_one()


def _conversation_dict(c: Conversation, db: Session, include_messages: bool = False) -> dict[str, Any]:
    d: dict[str, Any] = {
        "conversation_id":  c.conversation_id,
        "tenant_id":        c.tenant_id,
        "contact_id":       c.contact_id,
        "lead_id":          c.lead_id,
        "channel":          c.channel,
        "state":            c.state,
        "assigned_agent_id": c.assigned_to,  # inbox alias
        "handoff_count":    _handoff_count(c.conversation_id, db),
        "created_at":       c.created_at.isoformat() if c.created_at else None,
        "updated_at":       c.updated_at.isoformat() if c.updated_at else None,
    }
    if include_messages:
        messages = db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == c.conversation_id)
            .order_by(ConversationMessage.created_at)
        ).scalars().all()
        d["messages"] = [_message_dict(m) for m in messages]
    return d


def _message_dict(m: ConversationMessage) -> dict[str, Any]:
    return {
        "message_id":      m.message_id,
        "conversation_id": m.conversation_id,
        "tenant_id":       m.tenant_id,
        "contact_id":      m.contact_id,
        "direction":       m.direction,
        "text":            m.text,
        "occurred_at":     m.occurred_at,
        "created_at":      m.created_at.isoformat() if m.created_at else None,
    }


def _queue_dict(q: InboxQueue) -> dict[str, Any]:
    return {
        "queue_id":         q.queue_id,
        "tenant_id":        q.tenant_id,
        "name":             q.name,
        "routing_strategy": q.routing_strategy,
        "skill_tags":       q.skill_tags,
        "team_id":          q.team_id,
        "auto_assign":      q.auto_assign,
        "is_active":        q.is_active,
        "created_at":       q.created_at.isoformat() if q.created_at else None,
        "updated_at":       q.updated_at.isoformat() if q.updated_at else None,
    }


def _presence_dict(p: AgentPresence) -> dict[str, Any]:
    return {
        "agent_id":               p.agent_id,
        "tenant_id":              p.tenant_id,
        "status":                 p.status,
        "open_conversation_count": p.open_conversation_count,
        "max_concurrent":         p.max_concurrent,
        "last_seen_at":           p.last_seen_at.isoformat() if p.last_seen_at else None,
        "updated_at":             p.updated_at.isoformat() if p.updated_at else None,
    }


def _get_conversation_or_404(conversation_id: str, tenant_id: str, db: Session) -> Conversation:
    row = db.execute(
        select(Conversation).where(
            Conversation.conversation_id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    ).scalars().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return row


def _get_queue_or_404(queue_id: str, tenant_id: str, db: Session) -> InboxQueue:
    row = db.execute(
        select(InboxQueue).where(
            InboxQueue.queue_id == queue_id,
            InboxQueue.tenant_id == tenant_id,
        )
    ).scalars().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue not found")
    return row


# ── Request schemas ───────────────────────────────────────────────────────────

class HandoffRequest(BaseModel):
    to_agent_id: Optional[str] = None
    reason: str

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if v not in VALID_HANDOFF_REASONS:
            raise ValueError(f"reason must be one of {sorted(VALID_HANDOFF_REASONS)}")
        return v


class SendMessageRequest(BaseModel):
    text: str


class UpdatePresenceRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_PRESENCE_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_PRESENCE_STATUSES)}")
        return v


# ── Conversation Endpoints ────────────────────────────────────────────────────

@router.get("/api/v1/inbox/conversations")
def list_conversations(
    channel: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    q = select(Conversation).where(Conversation.tenant_id == claims.tenant_id)
    if channel is not None:
        q = q.where(Conversation.channel == channel)
    if state is not None:
        q = q.where(Conversation.state == state)
    q = q.order_by(Conversation.updated_at.desc())
    rows = db.execute(q).scalars().all()
    return {"data": [_conversation_dict(r, db) for r in rows], "meta": _meta()}


@router.get("/api/v1/inbox/conversations/{conversation_id}")
def get_conversation(
    conversation_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_conversation_or_404(conversation_id, claims.tenant_id, db)
    return {"data": _conversation_dict(c, db, include_messages=True), "meta": _meta()}


@router.post("/api/v1/inbox/conversations/{conversation_id}/claim")
def claim_conversation(
    conversation_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_conversation_or_404(conversation_id, claims.tenant_id, db)
    if c.assigned_to is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conversation is already assigned to an agent",
        )
    now = datetime.now(timezone.utc)
    c.assigned_to = claims.sub
    c.updated_at = now
    db.commit()
    db.refresh(c)
    return {"data": _conversation_dict(c, db), "meta": _meta()}


@router.post("/api/v1/inbox/conversations/{conversation_id}/handoff", status_code=status.HTTP_201_CREATED)
def handoff_conversation(
    conversation_id: str,
    body: HandoffRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_conversation_or_404(conversation_id, claims.tenant_id, db)
    now = datetime.now(timezone.utc)
    from_agent = c.assigned_to
    handoff = ConversationHandoff(
        handoff_id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        tenant_id=claims.tenant_id,
        from_agent_id=from_agent,
        to_agent_id=body.to_agent_id,
        handoff_reason=body.reason,
        initiated_by=claims.sub,
        created_at=now,
    )
    db.add(handoff)
    c.assigned_to = body.to_agent_id
    c.updated_at = now
    db.commit()
    db.refresh(c)
    return {"conversation": _conversation_dict(c, db), "meta": _meta()}


@router.post("/api/v1/inbox/conversations/{conversation_id}/messages", status_code=status.HTTP_201_CREATED)
def send_message(
    conversation_id: str,
    body: SendMessageRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    c = _get_conversation_or_404(conversation_id, claims.tenant_id, db)
    now = datetime.now(timezone.utc)
    message = ConversationMessage(
        message_id=str(uuid.uuid4()),
        tenant_id=claims.tenant_id,
        conversation_id=conversation_id,
        contact_id=c.contact_id,
        direction="outbound",
        text=body.text,
        occurred_at=now.isoformat(),
        created_at=now,
    )
    db.add(message)
    c.updated_at = now
    db.commit()
    db.refresh(message)
    return {"data": _message_dict(message), "meta": _meta()}


# ── Presence Endpoints ────────────────────────────────────────────────────────

@router.patch("/api/v1/inbox/presence")
def update_presence(
    body: UpdatePresenceRequest,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    row = db.execute(
        select(AgentPresence).where(
            AgentPresence.agent_id == claims.sub,
            AgentPresence.tenant_id == claims.tenant_id,
        )
    ).scalars().first()
    if row is None:
        row = AgentPresence(
            agent_id=claims.sub,
            tenant_id=claims.tenant_id,
            status=body.status,
            open_conversation_count=0,
            max_concurrent=10,
            last_seen_at=now,
            updated_at=now,
        )
        db.add(row)
    else:
        row.status = body.status
        row.last_seen_at = now
        row.updated_at = now
    db.commit()
    db.refresh(row)
    return {"data": _presence_dict(row), "meta": _meta()}


# ── Queue Endpoints ───────────────────────────────────────────────────────────

@router.get("/api/v1/inbox/queues")
def list_queues(
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = db.execute(
        select(InboxQueue)
        .where(InboxQueue.tenant_id == claims.tenant_id, InboxQueue.is_active.is_(True))
        .order_by(InboxQueue.created_at)
    ).scalars().all()
    return {"data": [_queue_dict(r) for r in rows], "meta": _meta()}


@router.get("/api/v1/inbox/queues/{queue_id}/stats")
def queue_stats(
    queue_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _get_queue_or_404(queue_id, claims.tenant_id, db)

    open_count = db.execute(
        select(func.count()).select_from(Conversation).where(
            Conversation.tenant_id == claims.tenant_id,
            Conversation.state == "open",
        )
    ).scalar_one()

    unassigned_count = db.execute(
        select(func.count()).select_from(Conversation).where(
            Conversation.tenant_id == claims.tenant_id,
            Conversation.state == "open",
            Conversation.assigned_to.is_(None),
        )
    ).scalar_one()

    assigned_count = db.execute(
        select(func.count()).select_from(Conversation).where(
            Conversation.tenant_id == claims.tenant_id,
            Conversation.state == "open",
            Conversation.assigned_to.is_not(None),
        )
    ).scalar_one()

    return {
        "data": {
            "queue_id":        queue_id,
            "open_count":      open_count,
            "unassigned_count": unassigned_count,
            "assigned_count":  assigned_count,
        },
        "meta": _meta(),
    }
