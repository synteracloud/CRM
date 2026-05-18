"""Easypaisa payment adapter — stub and live modes.

Docs: docs/integration-contracts.md — Pakistan Payments (Easypaisa)
      docs/pakistan-adapter-architecture.md §3.B

Live mode:
  Calls Easypaisa Payment Gateway API via OAuth2 Bearer token + HMAC.
  Endpoint (sandbox): https://easypaisa-pg-sandbox.com/payment/initiateTransaction
  Endpoint (prod):    https://easypaisa.com.pk/payment/initiateTransaction

  Required env vars (when stub_mode=False):
    EASYPAISA_STORE_ID       — store/merchant ID from Easypaisa portal
    EASYPAISA_STORE_PASSWORD — store password for HMAC construction
    EASYPAISA_API_URL        — override endpoint (optional; defaults to sandbox)

  HMAC: SHA-256 over concatenated storeId + orderId + transactionAmount +
        mobileAccountNo + emailAddress + transactionType + tokenExpiry +
        bankIdentificationNumber + merchantPaymentMethod (in this order),
        keyed with EASYPAISA_STORE_PASSWORD.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import urllib.request
from typing import Any

from adapters.interfaces.payment_adapter import (
    PaymentCreateInput,
    PaymentCreateResult,
    PaymentStatus,
)
from adapters.interfaces.types import AdapterContext, AdapterError, AdapterErrorCode, utcnow_iso

from .base import PakistanPaymentAdapter

_SANDBOX_URL = "https://easypaisa-pg-sandbox.com/payment/initiateTransaction"
_PROD_URL = "https://easypaisa.com.pk/payment/initiateTransaction"

_SUCCESS_STATUSES = {"SUCCESS", "PAID"}


def _build_ep_hash(fields: list[str], store_password: str) -> str:
    """Build Easypaisa HMAC-SHA256 signature over ordered field list."""
    data = "".join(str(f) for f in fields)
    return hmac.new(
        store_password.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class EasypaisaAdapter(PakistanPaymentAdapter):
    provider_name = "easypaisa"

    def __init__(
        self,
        merchant_id: str,
        secret: str,
        *,
        stub_mode: bool = True,
        store_password: str | None = None,
        api_url: str | None = None,
    ) -> None:
        super().__init__(merchant_id, secret, stub_mode=stub_mode)
        self._store_password = store_password or os.environ.get("EASYPAISA_STORE_PASSWORD", secret)
        self._api_url = api_url or os.environ.get("EASYPAISA_API_URL", _SANDBOX_URL)

    # ── Live API call ──────────────────────────────────────────────────────────

    def _create_payment_live(self, input: PaymentCreateInput, ctx: AdapterContext) -> PaymentCreateResult:
        """POST to Easypaisa payment initiation API."""
        amount_str = f"{input.amount_minor / 100:.2f}"
        mobile = input.metadata.get("mobile_number", "") if input.metadata else ""
        email = input.metadata.get("email", "") if input.metadata else ""
        token_expiry = "20" + utcnow_iso()[:10].replace("-", "") + "235959"  # end of today

        # Fields in HMAC signing order per Easypaisa spec
        hash_fields = [
            self.merchant_id,   # storeId
            input.order_id,     # orderId
            amount_str,         # transactionAmount
            mobile,             # mobileAccountNo
            email,              # emailAddress
            "MA",               # transactionType (MA = Mobile Account)
            token_expiry,       # tokenExpiry
            "",                 # bankIdentificationNumber (empty for MA)
            "MA",               # merchantPaymentMethod
        ]
        signature = _build_ep_hash(hash_fields, self._store_password)

        payload = {
            "storeId": self.merchant_id,
            "orderId": input.order_id,
            "transactionAmount": amount_str,
            "mobileAccountNo": mobile,
            "emailAddress": email,
            "transactionType": "MA",
            "tokenExpiry": token_expiry,
            "bankIdentificationNumber": "",
            "merchantPaymentMethod": "MA",
            "signature": signature,
        }

        # Easypaisa requires Basic auth: base64(storeId:storePassword)
        basic_cred = base64.b64encode(
            f"{self.merchant_id}:{self._store_password}".encode("utf-8")
        ).decode("utf-8")

        try:
            body = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self._api_url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {basic_cred}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise AdapterError(
                code=AdapterErrorCode.PROVIDER_UNAVAILABLE,
                message=f"Easypaisa API unreachable: {exc}",
                retryable=True,
                provider=self.provider_name,
                provider_code="NETWORK_ERROR",
                correlation_id=ctx.trace_id,
            ) from exc

        response_code = str(raw.get("responseCode") or raw.get("status") or "")
        if response_code not in _SUCCESS_STATUSES and response_code != "0000":
            raise AdapterError(
                code=AdapterErrorCode.PROVIDER_ERROR,
                message=raw.get("responseDesc", "Easypaisa declined"),
                retryable=False,
                provider=self.provider_name,
                provider_code=response_code,
                correlation_id=ctx.trace_id,
            )

        return PaymentCreateResult(
            payment_ref=input.order_id,
            status=PaymentStatus.INITIATED,
            provider_txn_id=raw.get("transactionId", input.order_id),
            next_action_url=raw.get("redirectUrl", input.callback_url),
            raw=raw,
        )

    # ── Normalisation ──────────────────────────────────────────────────────────

    def normalize_transaction(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Normalise Easypaisa callback/webhook payload to canonical shape."""
        raw_status = str(payload.get("transactionStatus") or payload.get("payment_status") or "")
        status = "succeeded" if raw_status in _SUCCESS_STATUSES else "failed"
        settled = payload.get("settlement_ts") or payload.get("settlementTs")

        return {
            "provider_txn_id": payload.get("transactionId") or payload.get("transaction_id", ""),
            "invoice_ref": payload.get("orderId") or payload.get("merchant_reference"),
            "customer_ref": payload.get("mobileAccountNo") or payload.get("customer_ref", ""),
            "amount": float(payload.get("transactionAmount") or payload.get("amount", 0)),
            "currency": payload.get("currency", "PKR"),
            "status": status,
            "received_at": payload.get("dateTime") or payload.get("event_time") or utcnow_iso(),
            "settled_at": settled,
        }
