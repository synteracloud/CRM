"""JazzCash adapter implementation."""

from __future__ import annotations

from typing import Any

from .base import PakistanPaymentAdapter


class JazzCashAdapter(PakistanPaymentAdapter):
    provider_name = "jazzcash"

    def normalize_transaction(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider_txn_id": payload["txn_id"],
            "invoice_ref": payload.get("invoice_number"),
            "customer_ref": payload["customer_id"],
            "amount": float(payload["amount"]),
            "currency": payload.get("currency", "PKR"),
            "status": "succeeded" if payload.get("status") in {"paid", "success"} else "failed",
            "received_at": payload["timestamp"],
            "settled_at": payload.get("settled_at"),
        }
