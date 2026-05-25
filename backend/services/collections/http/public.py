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
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.auth.jwt_deps import TokenClaims, get_current_user
from services.collections.entities import Invoice
from services.collections.service import CollectionsService
from services.db import get_db
from services.db.models.collections import (
    Invoice as InvoiceORM,
    Payment as PaymentORM,
    ReconciliationCase as ReconciliationCaseORM,
)

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
        "tenant_id": inv.tenant_id,
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


def _orm_invoice_dict(row: InvoiceORM) -> dict[str, Any]:
    return {
        "invoice_id": row.invoice_id,
        "invoice_number": row.invoice_number,
        "customer_id": row.customer_id,
        "tenant_id": row.tenant_id,
        "total_amount": float(row.total_amount),
        "amount_paid": float(row.amount_paid),
        "amount_outstanding": float(row.amount_outstanding),
        "currency": row.currency,
        "state": row.state,
        "issue_date": row.issue_date,
        "due_date": row.due_date,
        "overdue_days": row.overdue_days,
        "escalation_level": row.escalation_level,
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
    db: Session = Depends(get_db),
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
        tenant_id=claims.tenant_id,
    )
    try:
        created = _service.create_invoice(invoice)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    db_invoice = InvoiceORM(
        invoice_id=created.invoice_id,
        invoice_number=created.invoice_number,
        tenant_id=created.tenant_id,
        customer_id=created.customer_id,
        issue_date=created.issue_date,
        due_date=created.due_date,
        currency=created.currency,
        total_amount=created.total_amount,
        amount_paid=created.amount_paid,
        amount_outstanding=created.amount_outstanding,
        state=created.state,
        overdue_days=created.overdue_days,
        escalation_level=created.escalation_level,
    )
    db.merge(db_invoice)
    db.commit()

    return {"data": _invoice_dict(created), "meta": _meta()}


@router.get("/api/v1/invoices")
def list_invoices(
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List all invoices for the authenticated tenant from DB."""
    rows = db.execute(
        select(InvoiceORM).where(InvoiceORM.tenant_id == claims.tenant_id)
        .order_by(InvoiceORM.created_at.desc())
    ).scalars().all()
    data = [_orm_invoice_dict(r) for r in rows]
    return {"data": data, "meta": _meta(total=len(data))}


@router.get("/api/v1/invoices/{invoice_id}")
def get_invoice(
    invoice_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve a single invoice by ID from DB."""
    row = db.get(InvoiceORM, invoice_id)
    if row is None or row.tenant_id != claims.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return {"data": _orm_invoice_dict(row), "meta": _meta()}


@router.post("/api/v1/invoices/{invoice_id}/send")
def send_invoice(
    invoice_id: str,
    claims: TokenClaims = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Mark invoice as dispatched to customer and return scheduled WhatsApp reminder dates."""
    row = db.get(InvoiceORM, invoice_id)
    if row is None or row.tenant_id != claims.tenant_id:
        # Fall back to in-memory service for backwards compatibility
        try:
            inv = _service.get_invoice(invoice_id)
        except KeyError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        reminders = _service.list_invoice_reminders(invoice_id)
        return {
            "data": {
                "invoice_id": inv.invoice_id,
                "customer_id": inv.customer_id,
                "action": "sent",
                "reminders_scheduled": reminders,
            },
            "meta": _meta(),
        }
    reminders = _service.list_invoice_reminders(invoice_id)
    return {
        "data": {
            "invoice_id": row.invoice_id,
            "customer_id": row.customer_id,
            "action": "sent",
            "reminders_scheduled": reminders,
        },
        "meta": _meta(),
    }


@router.post("/api/v1/payments/callback/{provider}", status_code=status.HTTP_200_OK)
def payment_callback(
    provider: str,
    body: PaymentCallbackPayload,
    _: None = Depends(_verify_callback_key),
    db: Session = Depends(get_db),
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

    # Persist payment to DB
    db_payment = PaymentORM(
        payment_id=payment.payment_id,
        tenant_id="",  # payment callbacks don't carry tenant_id; resolved via invoice_ref
        provider=payment.provider,
        provider_txn_id=payment.provider_txn_id,
        invoice_ref=payment.invoice_ref,
        customer_ref=payment.customer_ref,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
        received_at=payment.received_at,
        settled_at=payment.settled_at,
        raw_payload=payment.raw_payload,
    )
    db.merge(db_payment)

    if case:
        db_case = ReconciliationCaseORM(
            case_id=case.case_id,
            tenant_id="",
            payment_id=payment.payment_id,
            invoice_id=case.invoice_id,
            match_status=case.match_status,
            mismatch_reason=case.mismatch_reason,
        )
        db.merge(db_case)

    db.commit()

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
