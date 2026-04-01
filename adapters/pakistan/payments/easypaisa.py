"""Easypaisa adapter implementation."""

from __future__ import annotations

from typing import Any

from .base import PakistanPaymentAdapter


class EasypaisaAdapter(PakistanPaymentAdapter):
    provider_name = "easypaisa"

    def normalize_transaction(self, payload: dict[str, Any]) -> dict[str, Any]:
        settled = payload.get("settlement_ts")
        return {
            "provider_txn_id": payload["transaction_id"],
            "invoice_ref": payload.get("merchant_reference"),
            "customer_ref": payload["customer_ref"],
            "amount": float(payload["amount"]),
            "currency": payload.get("currency", "PKR"),
            "status": "succeeded" if payload.get("payment_status") == "SUCCESS" else "failed",
            "received_at": payload["event_time"],
            "settled_at": settled,
        }
