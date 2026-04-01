"""Pakistan payment adapter contract and shared behavior."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any


class PakistanPaymentAdapter:
    provider_name: str = "unknown"

    def __init__(self, merchant_id: str, secret: str) -> None:
        self.merchant_id = merchant_id
        self.secret = secret.encode("utf-8")

    def create_payment_intent(self, invoice_number: str, amount: float, currency: str = "PKR") -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "merchant_id": self.merchant_id,
            "invoice_number": invoice_number,
            "amount": amount,
            "currency": currency,
            "intent_id": f"{self.provider_name}-{invoice_number}",
            "status": "initiated",
        }

    def verify_callback(self, signature: str, payload: dict[str, Any]) -> bool:
        digest = hmac.new(self.secret, str(payload).encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, digest)

    def query_transaction(self, provider_txn_id: str) -> dict[str, str]:
        return {
            "provider_txn_id": provider_txn_id,
            "status": "succeeded",
        }

    def refund_or_reverse(self, payment_id: str, amount: float) -> dict[str, Any]:
        return {
            "payment_id": payment_id,
            "provider": self.provider_name,
            "amount": amount,
            "status": "reversed",
        }
