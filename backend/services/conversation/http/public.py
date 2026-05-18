"""Public REST endpoints for WhatsApp webhook ingestion and conversation queries.

Spec: backend/docs/whatsapp-execution-model.md
API standards: backend/docs/api-standards.md

Routes:
    POST /api/v1/webhooks/whatsapp   — inbound webhook (API-key auth)
    GET  /api/v1/conversations       — list conversations for tenant (JWT)
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.conversation.intent import classify_intent

router = APIRouter(tags=["whatsapp"])

_WEBHOOK_API_KEY = os.environ.get("WEBHOOK_API_KEY", "dev-webhook-key")

# In-memory conversation store (Phase 2 pattern — swapped for DB in Phase 5)
_conversations: dict[str, dict[str, Any]] = {}
_messages: dict[str, list[dict[str, Any]]] = {}


def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


def _verify_webhook_key(x_api_key: str | None = Header(None)) -> None:
    if x_api_key != _WEBHOOK_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Api-Key",
        )


# ── Request schemas ───────────────────────────────────────────────────────────


class WhatsAppWebhookPayload(BaseModel):
    provider: str = "meta"
    from_number: str
    to_number: str | None = None
    provider_message_id: str
    text: str = ""
    occurred_at: str
    has_media_attachment: bool = False
    linked_invoice_id: str | None = None
    tenant_id: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/api/v1/webhooks/whatsapp", status_code=status.HTTP_200_OK)
def inbound_webhook(
    body: WhatsAppWebhookPayload,
    _: None = Depends(_verify_webhook_key),
) -> dict[str, Any]:
    """Receive and classify an inbound WhatsApp message.

    Anti-lead-loss guarantee: every inbound creates/updates a Contact + Conversation.
    Intent classification runs synchronously; lead creation is advisory.
    """
    classification = classify_intent(
        message_body=body.text,
        has_media_attachment=body.has_media_attachment,
        linked_invoice_id=body.linked_invoice_id,
    )

    # Resolve or create conversation (keyed by tenant + phone)
    conv_key = f"{body.tenant_id}:{body.from_number}"
    if conv_key not in _conversations:
        _conversations[conv_key] = {
            "conversation_id": str(uuid.uuid4()),
            "tenant_id": body.tenant_id,
            "from_number": body.from_number,
            "state": "NEW",
            "created_at": body.occurred_at,
            "updated_at": body.occurred_at,
            "intent_history": [],
        }

    conv = _conversations[conv_key]
    conv["state"] = "ACTIVE"
    conv["updated_at"] = body.occurred_at
    conv["intent_history"].append(classification.intent)

    # Append message to conversation thread
    msg = {
        "message_id": str(uuid.uuid4()),
        "provider_message_id": body.provider_message_id,
        "direction": "inbound",
        "text": body.text,
        "intent": classification.intent,
        "matched_keyword": classification.matched_keyword,
        "occurred_at": body.occurred_at,
    }
    _messages.setdefault(conv["conversation_id"], []).append(msg)

    # Determine if a lead stub should be created (advisory — actual creation is CRM domain)
    should_create_lead = classification.intent == "lead_inquiry" and len(conv["intent_history"]) == 1

    return {
        "data": {
            "conversation_id": conv["conversation_id"],
            "from_number": body.from_number,
            "intent": classification.intent,
            "confidence": classification.confidence,
            "matched_keyword": classification.matched_keyword,
            "should_create_lead": should_create_lead,
            "message_id": msg["message_id"],
        },
        "meta": _meta(),
    }


@router.get("/api/v1/conversations/{conversation_id}")
def get_conversation(
    conversation_id: str,
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Get a single conversation by ID with its full message thread."""
    conv = next(
        (
            c for c in _conversations.values()
            if c["conversation_id"] == conversation_id and c["tenant_id"] == claims.tenant_id
        ),
        None,
    )
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    messages = _messages.get(conversation_id, [])
    return {
        "data": {**conv, "messages": messages},
        "meta": _meta(message_count=len(messages)),
    }


@router.get("/api/v1/conversations")
def list_conversations(
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """List all conversations for the authenticated tenant."""
    tenant_convs = [
        conv for key, conv in _conversations.items()
        if conv["tenant_id"] == claims.tenant_id
    ]
    return {
        "data": tenant_convs,
        "meta": _meta(total=len(tenant_convs)),
    }
