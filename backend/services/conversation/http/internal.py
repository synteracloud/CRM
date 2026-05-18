"""Conversation / intent service internal HTTP endpoints.

Docs: docs/whatsapp-execution-model.md
      BEHAV-001 — intent classifier fires on every inbound message
      gateway/routes/v1-whatsapp-webhooks.routes.js (gateway consumer)

These routes are NOT exposed to end-users.  The gateway calls them from
WhatsApp webhook handlers over a trusted internal network.

Mount point (wired in services/app.py — P-019)::
    app.include_router(conversation_router, prefix="/internal")

Classification is stateless — no singleton needed.  Results are
deterministic for a given message body + context flags.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.conversation.intent import classify_intent

router = APIRouter(tags=["internal"])


# ── POST /internal/classify ───────────────────────────────────────────────────
class ClassifyRequest(BaseModel):
    message_body: str
    has_media_attachment: bool = False
    linked_invoice_id: str | None = None


@router.post("/classify")
def classify(body: ClassifyRequest) -> dict:
    """Classify the intent of an inbound WhatsApp message.

    Called by gateway/routes/v1-whatsapp-webhooks.routes.js on every
    inbound message before lead routing.  See BEHAV-001.

    Response::
        { "intent": str, "confidence": float | null, "raw": {...} }
    """
    try:
        result = classify_intent(
            message_body=body.message_body,
            has_media_attachment=body.has_media_attachment,
            linked_invoice_id=body.linked_invoice_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Classification error: {exc}")

    return {
        "intent":     result.intent,
        "confidence": getattr(result, "confidence", None),
        "raw":        getattr(result, "raw", {}),
    }


# ── POST /internal/messages ───────────────────────────────────────────────────
class InboundMessageRequest(BaseModel):
    """Canonical inbound message from a WhatsApp provider webhook."""
    provider:             str
    from_number:          str
    to_number:            str | None = None
    provider_message_id:  str
    text:                 str = ""
    occurred_at:          str
    has_media_attachment: bool = False
    linked_invoice_id:    str | None = None
    tenant_id:            str | None = None


@router.post("/messages")
def handle_inbound_message(body: InboundMessageRequest) -> dict:
    """Classify an inbound message and return routing intent for lead capture.

    The gateway calls this endpoint after normalising a provider webhook.
    The response tells the gateway which intent was detected so it can
    route the message to the appropriate lead / conversation pipeline.

    This endpoint is fire-and-forget safe — the WhatsApp provider has already
    received a 200; any failure here is logged but does not affect the provider.

    Response::
        { "intent": str, "from_number": str, "provider_message_id": str }
    """
    try:
        result = classify_intent(
            message_body=body.text,
            has_media_attachment=body.has_media_attachment,
            linked_invoice_id=body.linked_invoice_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Message handling error: {exc}")

    return {
        "intent":               result.intent,
        "confidence":           getattr(result, "confidence", None),
        "from_number":          body.from_number,
        "provider_message_id":  body.provider_message_id,
        "provider":             body.provider,
        "occurred_at":          body.occurred_at,
    }
