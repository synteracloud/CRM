"""Public REST endpoints for invoice management and payment callbacks.

Spec: backend/docs/collections-engine-model.md
API standards: backend/docs/api-standards.md

Routes:
    POST /api/v1/invoices                     — create invoice (JWT)
    GET  /api/v1/invoices                     — list invoices for tenant (JWT)
    GET  /api/v1/invoices/{invoice_id}        — get single invoice (JWT)
    POST /api/v1/payments/callback/{provider} — provider payment callback (API-key auth)
"""

from __future__ import annotations

import os
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.collections.entities import Invoice
from services.collections.service import CollectionsService

router = APIRouter(tags=["collections"])

_CALLBACK_API_KEY = os.environ.get("CALLBACK_API_KEY", "dev-callback-key")

_service = CollectionsService()


def set_service(svc: CollectionsService) -> None:
    global _service  # noqa: PLW0603
    _service = svc


def _meta(**extra: Any) -> dict[str, Any]:
    return {"request_id": str(uuid.uuid4()), **extra}


def _verify_callback_key(x_api_key: str | None = Header(None)) -> None:
    if x_api_key != _CALLBACK_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Api-Key",
        )


def _invoice_dict(inv: Invoice) -> dict[str, Any]:
    return {
        "invoice_id": inv.invoice_id,
        "invoice_number": inv.invoice_number,
        "customer_id": inv.customer_id,
        "total_amount": inv.total_amount,
        "amount_paid": inv.amount_paid,
        "amount_outstanding": inv.amount_outstanding,
        "currency": inv.currency,
        "state": inv.state,
        "issue_date": inv.issue_date,
        "due_date": inv.due_date,
        "overdue_days": inv.overdue_days,
        "escalation_level": inv.escalation_level,
    }


# ── Request schemas ───────────────────────────────────────────────────────────


class CreateInvoiceRequest(BaseModel):
    invoice_number: str
    customer_id: str
    issue_date: str   # ISO date YYYY-MM-DD
    due_date: str     # ISO date YYYY-MM-DD
    currency: str = "PKR"
    total_amount: float


class PaymentCallbackPayload(BaseModel):
    signature: str = ""
    payload: dict[str, Any]


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/api/v1/invoices", status_code=status.HTTP_201_CREATED)
def create_invoice(
    body: CreateInvoiceRequest,
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Create a new invoice. Anti-lead-loss: every invoice is tracked from creation."""
    invoice = Invoice(
        invoice_id=f"inv-{uuid.uuid4().hex[:12]}",
        invoice_number=body.invoice_number,
        customer_id=body.customer_id,
        issue_date=body.issue_date,
        due_date=body.due_date,
        currency=body.currency,
        total_amount=body.total_amount,
    )
    try:
        created = _service.create_invoice(invoice)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return {"data": _invoice_dict(created), "meta": _meta()}


@router.get("/api/v1/invoices")
def list_invoices(
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """List all invoices. Phase 2: in-memory store; Phase 5 swaps to DB with tenant filter."""
    invoices = list(_service._invoices.values())
    return {"data": [_invoice_dict(inv) for inv in invoices], "meta": _meta(total=len(invoices))}


@router.get("/api/v1/invoices/{invoice_id}")
def get_invoice(
    invoice_id: str,
    claims: TokenClaims = Depends(get_current_user),
) -> dict[str, Any]:
    """Retrieve a single invoice by ID."""
    try:
        inv = _service.get_invoice(invoice_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return {"data": _invoice_dict(inv), "meta": _meta()}


@router.post("/api/v1/payments/callback/{provider}", status_code=status.HTTP_200_OK)
def payment_callback(
    provider: str,
    body: PaymentCallbackPayload,
    _: None = Depends(_verify_callback_key),
) -> dict[str, Any]:
    """Receive a JazzCash/Easypaisa/bank payment callback and reconcile against open invoices."""
    try:
        payment, case = _service.ingest_payment(provider, body.signature, body.payload)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown payment provider: {provider}",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    return {
        "data": {
            "payment_id": payment.payment_id,
            "provider": payment.provider,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "reconciliation_case": {
                "case_id": case.case_id,
                "match_status": case.match_status,
            } if case else None,
        },
        "meta": _meta(),
    }
