"""Collections service internal HTTP endpoints.

Docs: docs/collections-engine-model.md
      gateway/routes/v1-collections.routes.js (gateway consumer)

These routes are NOT exposed to end-users.  The gateway calls them over a
trusted internal network for payment ingestion and invoice lifecycle management.

Mount point (wired in services/app.py — P-019)::
    app.include_router(collections_router, prefix="/internal")

Service lifecycle:
    The _service singleton is the authoritative in-memory instance.
    P-019 wires the shared instance via set_service() at app startup.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.collections.service import CollectionsService
from services.collections.entities import Invoice

router = APIRouter(tags=["internal"])

_service = CollectionsService()


def set_service(service: CollectionsService) -> None:
    """Override the default service singleton.  Called once at service startup."""
    global _service  # noqa: PLW0603
    _service = service


# ── POST /internal/payments ───────────────────────────────────────────────────
class IngestPaymentRequest(BaseModel):
    provider: str
    signature: str
    payload: dict[str, Any]


@router.post("/payments")
def ingest_payment(body: IngestPaymentRequest) -> dict:
    """Ingest and reconcile a provider payment callback.

    Called by gateway/routes/v1-collections.routes.js payment webhook handlers
    (JazzCash, Easypaisa, etc.) after provider-specific signature verification.

    Response::
        { "payment": {...}, "reconciliation_case": {...} | null }
    """
    try:
        payment, case = _service.ingest_payment(body.provider, body.signature, body.payload)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown payment provider: {body.provider}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return {
        "payment": {
            "payment_id":     payment.payment_id,
            "provider":       payment.provider,
            "provider_txn_id": payment.provider_txn_id,
            "invoice_ref":    payment.invoice_ref,
            "customer_ref":   payment.customer_ref,
            "amount":         payment.amount,
            "currency":       payment.currency,
            "status":         payment.status,
            "received_at":    payment.received_at,
        },
        "reconciliation_case": {
            "case_id":          case.case_id,
            "payment_id":       case.payment_id,
            "invoice_id":       case.invoice_id,
            "match_status":     case.match_status,
            "mismatch_reason":  case.mismatch_reason,
            "resolution_action": case.resolution_action,
        } if case else None,
    }


# ── GET /internal/invoices/{invoice_id} ───────────────────────────────────────
@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: str) -> dict:
    """Return a single invoice by ID."""
    try:
        inv = _service.get_invoice(invoice_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Invoice not found: {invoice_id}")

    return {
        "invoice_id":        inv.invoice_id,
        "invoice_number":    inv.invoice_number,
        "customer_id":       inv.customer_id,
        "total_amount":      inv.total_amount,
        "amount_paid":       inv.amount_paid,
        "amount_outstanding": inv.amount_outstanding,
        "currency":          inv.currency,
        "state":             inv.state,
        "due_date":          inv.due_date,
        "overdue_days":      inv.overdue_days,
    }


# ── POST /internal/invoices/overdue-rollup ────────────────────────────────────
class OverdueRollupRequest(BaseModel):
    as_of: str  # ISO-8601 date string, e.g. "2026-04-09"


@router.post("/invoices/overdue-rollup")
def overdue_rollup(body: OverdueRollupRequest) -> dict:
    """Mark all overdue invoices and return the updated set.

    Intended to be called nightly by a cron job or the gateway scheduler.
    """
    try:
        updated = _service.run_overdue_rollup(body.as_of)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return {
        "updated_count": len(updated),
        "invoices": [
            {
                "invoice_id":    inv.invoice_id,
                "invoice_number": inv.invoice_number,
                "state":         inv.state,
                "overdue_days":  inv.overdue_days,
            }
            for inv in updated
        ],
    }
