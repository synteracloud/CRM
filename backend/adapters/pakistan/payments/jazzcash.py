"""JazzCash payment adapter — stub and live modes.

Docs: docs/integration-contracts.md — Pakistan Payments (JazzCash)
      docs/pakistan-adapter-architecture.md §3.B

Live mode:
  Calls JazzCash Mobile Wallet (MWallet) API.
  Endpoint (sandbox): https://sandbox.jazzcash.com.pk/ApplicationAPI/API/2.0/Purchase/DoMWalletTransaction
  Endpoint (prod):    https://payments.jazzcash.com.pk/ApplicationAPI/API/2.0/Purchase/DoMWalletTransaction

  Required env vars (when stub_mode=False):
    JAZZCASH_MERCHANT_ID   — merchant ID from JazzCash dashboard
    JAZZCASH_PASSWORD      — API password from JazzCash dashboard
    JAZZCASH_HASH_KEY      — hash integrity key for pp_SecureHash
    JAZZCASH_API_URL       — override endpoint (optional; defaults to sandbox)

  HMAC: SHA-256 over sorted pp_* fields (excluding pp_SecureHash itself),
        joined by & with hash key prepended: "HASH_KEY&pp_field1=val1&...".
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import urllib.request
from datetime import datetime, timezone
from typing import Any

from adapters.interfaces.payment_adapter import (
    PaymentCreateInput,
    PaymentCreateResult,
    PaymentStatus,
)
from adapters.interfaces.types import AdapterContext, AdapterError, AdapterErrorCode, utcnow_iso

from .base import PakistanPaymentAdapter

_SANDBOX_URL = "https://sandbox.jazzcash.com.pk/ApplicationAPI/API/2.0/Purchase/DoMWalletTransaction"
_PROD_URL = "https://payments.jazzcash.com.pk/ApplicationAPI/API/2.0/Purchase/DoMWalletTransaction"

# JazzCash canonical response codes
_SUCCESS_CODES = {"000"}


def _jazzcash_datetime() -> str:
    """Return datetime in JazzCash format: yyyyMMddHHmmss (UTC)."""
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")


def _build_secure_hash(params: dict[str, str], hash_key: str) -> str:
    """Build pp_SecureHash per JazzCash spec.

    Sort all pp_* keys alphabetically, join values with '&', prepend hash_key,
    then HMAC-SHA256.
    """
    sorted_keys = sorted(k for k in params if k != "pp_SecureHash")
    data = "&".join(f"{params[k]}" for k in sorted_keys)
    payload = f"{hash_key}&{data}"
    return hmac.new(
        hash_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


class JazzCashAdapter(PakistanPaymentAdapter):
    provider_name = "jazzcash"

    def __init__(
        self,
        merchant_id: str,
        secret: str,
        *,
        stub_mode: bool = True,
        password: str | None = None,
        hash_key: str | None = None,
        api_url: str | None = None,
    ) -> None:
        super().__init__(merchant_id, secret, stub_mode=stub_mode)
        # Live-mode credentials — fall back to env vars if not passed directly.
        self._password = password or os.environ.get("JAZZCASH_PASSWORD", "")
        self._hash_key = hash_key or os.environ.get("JAZZCASH_HASH_KEY", secret)
        self._api_url = api_url or os.environ.get("JAZZCASH_API_URL", _SANDBOX_URL)

    # ── Live API call ──────────────────────────────────────────────────────────

    def _create_payment_live(self, input: PaymentCreateInput, ctx: AdapterContext) -> PaymentCreateResult:
        """POST to JazzCash MWallet API and return normalised result."""
        txn_ref = f"T{_jazzcash_datetime()}{input.order_id[:8].replace('-', '')}"
        amount_str = f"{input.amount_minor / 100:.2f}"  # minor units → PKR string

        params: dict[str, str] = {
            "pp_Version": "2.0",
            "pp_TxnType": "MWALLET",
            "pp_Language": "EN",
            "pp_MerchantID": self.merchant_id,
            "pp_Password": self._password,
            "pp_TxnRefNo": txn_ref,
            "pp_Amount": amount_str.replace(".", ""),  # JazzCash wants paise without decimal
            "pp_TxnCurrency": input.currency,
            "pp_TxnDateTime": _jazzcash_datetime(),
            "pp_BillReference": input.order_id,
            "pp_Description": f"Payment for order {input.order_id}",
            "pp_MobileNumber": input.metadata.get("mobile_number", "") if input.metadata else "",
            "pp_CNIC": input.metadata.get("cnic", "") if input.metadata else "",
        }
        params["pp_SecureHash"] = _build_secure_hash(params, self._hash_key)

        try:
            body = json.dumps(params).encode("utf-8")
            req = urllib.request.Request(
                self._api_url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise AdapterError(
                code=AdapterErrorCode.PROVIDER_UNAVAILABLE,
                message=f"JazzCash API unreachable: {exc}",
                retryable=True,
                provider=self.provider_name,
                provider_code="NETWORK_ERROR",
                correlation_id=ctx.trace_id,
            ) from exc

        response_code = raw.get("pp_ResponseCode", "")
        if response_code not in _SUCCESS_CODES:
            raise AdapterError(
                code=AdapterErrorCode.PROVIDER_ERROR,
                message=raw.get("pp_ResponseMessage", "JazzCash declined"),
                retryable=False,
                provider=self.provider_name,
                provider_code=response_code,
                correlation_id=ctx.trace_id,
            )

        return PaymentCreateResult(
            payment_ref=txn_ref,
            status=PaymentStatus.INITIATED,
            provider_txn_id=raw.get("pp_TxnRefNo", txn_ref),
            next_action_url=input.callback_url,
            raw=raw,
        )

    # ── Normalisation ──────────────────────────────────────────────────────────

    def normalize_transaction(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Normalise JazzCash callback/webhook payload to canonical shape."""
        raw_status = str(payload.get("pp_ResponseCode") or payload.get("status") or "")
        status = "succeeded" if raw_status in _SUCCESS_CODES or raw_status in {"paid", "success"} else "failed"

        if "pp_Amount" in payload:
            # JazzCash native format: paise string without decimal → divide by 100 → PKR
            try:
                amount = float(str(payload["pp_Amount"])) / 100
            except ValueError:
                amount = 0.0
        else:
            # Normalised/webhook format: amount already in PKR
            amount = float(payload.get("amount", 0))

        timestamp = payload.get("pp_TxnDateTime") or payload.get("timestamp") or utcnow_iso()

        return {
            "provider_txn_id": payload.get("pp_TxnRefNo") or payload.get("txn_id", ""),
            "invoice_ref": payload.get("pp_BillReference") or payload.get("invoice_number"),
            "customer_ref": payload.get("pp_MobileNumber") or payload.get("customer_id", ""),
            "amount": amount,
            "currency": payload.get("pp_TxnCurrency") or payload.get("currency", "PKR"),
            "status": status,
            "received_at": timestamp,
            "settled_at": payload.get("settled_at"),
        }
