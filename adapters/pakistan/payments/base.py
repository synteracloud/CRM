"""Pakistan payment adapter contract and shared behavior."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from adapters.interfaces.payment_adapter import (
    PaymentCaptureInput,
    PaymentCaptureResult,
    PaymentCreateInput,
    PaymentCreateResult,
    PaymentRefundInput,
    PaymentRefundResult,
    PaymentStatus,
    PaymentStatusInput,
    PaymentStatusResult,
    PaymentWebhookEvent,
    RawWebhookInput,
)
from adapters.interfaces.types import AdapterContext, AdapterError, AdapterErrorCode, utcnow_iso


class PakistanPaymentAdapter:
    provider_name: str = "unknown"

    def __init__(self, merchant_id: str, secret: str) -> None:
        self.merchant_id = merchant_id
        self.secret = secret.encode("utf-8")
        self._payments: dict[str, dict[str, Any]] = {}

    # Canonical PaymentAdapter methods
    def create_payment(self, input: PaymentCreateInput, ctx: AdapterContext) -> PaymentCreateResult:
        self._assert_pk_context(ctx)
        self._validate_amount(input.amount_minor, ctx)
        payment_ref = f"{self.provider_name}-{input.order_id}"
        record = {
            "payment_ref": payment_ref,
            "status": PaymentStatus.INITIATED,
            "provider_txn_id": f"{self.provider_name}-txn-{input.idempotency_key}",
            "amount_minor": input.amount_minor,
            "currency": input.currency,
            "customer_id": input.customer_id,
            "order_id": input.order_id,
            "updated_at": utcnow_iso(),
        }
        if payment_ref in self._payments:
            existing = self._payments[payment_ref]
            if existing["amount_minor"] != input.amount_minor:
                raise AdapterError(
                    code=AdapterErrorCode.CONFLICT_IDEMPOTENCY,
                    message="Idempotency key replayed with a different amount.",
                    retryable=False,
                    provider=self.provider_name,
                    provider_code="IDEMPOTENCY_CONFLICT",
                    correlation_id=ctx.trace_id,
                )
            return PaymentCreateResult(
                payment_ref=payment_ref,
                status=existing["status"],
                provider_txn_id=str(existing["provider_txn_id"]),
                next_action_url=input.callback_url,
                raw=existing,
            )

        self._payments[payment_ref] = record
        return PaymentCreateResult(
            payment_ref=payment_ref,
            status=PaymentStatus.INITIATED,
            provider_txn_id=record["provider_txn_id"],
            next_action_url=input.callback_url,
            raw=record,
        )

    def capture_payment(self, input: PaymentCaptureInput, ctx: AdapterContext) -> PaymentCaptureResult:
        record = self._get_payment_or_raise(input.payment_ref, ctx)
        record["status"] = PaymentStatus.SUCCEEDED
        record["updated_at"] = utcnow_iso()
        return PaymentCaptureResult(
            payment_ref=input.payment_ref,
            status=PaymentStatus.SUCCEEDED,
            provider_txn_id=str(record["provider_txn_id"]),
            raw=record,
        )

    def refund_payment(self, input: PaymentRefundInput, ctx: AdapterContext) -> PaymentRefundResult:
        self._validate_amount(input.amount_minor, ctx)
        record = self._get_payment_or_raise(input.payment_ref, ctx)
        record["status"] = PaymentStatus.REFUNDED
        record["updated_at"] = utcnow_iso()
        record["refund_ref"] = input.refund_ref
        record["refund_reason"] = input.reason
        return PaymentRefundResult(
            payment_ref=input.payment_ref,
            status=PaymentStatus.REFUNDED,
            provider_txn_id=str(record["provider_txn_id"]),
            raw=record,
        )

    def get_payment_status(self, input: PaymentStatusInput, ctx: AdapterContext) -> PaymentStatusResult:
        record = self._get_payment_or_raise(input.payment_ref, ctx)
        return PaymentStatusResult(
            payment_ref=input.payment_ref,
            status=record["status"],
            last_updated_at=str(record["updated_at"]),
            raw=record,
        )

    def parse_webhook(self, input: RawWebhookInput, ctx: AdapterContext) -> PaymentWebhookEvent:
        signature = input.headers.get("x-signature", "")
        if not self.verify_callback(signature, input.body):
            raise AdapterError(
                code=AdapterErrorCode.AUTH_ERROR,
                message="Invalid webhook signature.",
                retryable=False,
                provider=self.provider_name,
                provider_code="BAD_SIGNATURE",
                correlation_id=ctx.trace_id,
            )

        normalized = self.normalize_transaction(input.body)
        payment_ref = str(normalized.get("invoice_ref") or normalized["provider_txn_id"])
        status = PaymentStatus.SUCCEEDED if normalized["status"] == "succeeded" else PaymentStatus.FAILED

        expected_amount_minor = input.body.get("expected_amount_minor")
        if expected_amount_minor is not None and int(expected_amount_minor) != int(float(normalized["amount"]) * 100):
            return PaymentWebhookEvent(
                event_id=f"{self.provider_name}-mismatch-{normalized['provider_txn_id']}",
                event_type="payment.mismatch",
                payment_ref=payment_ref,
                status=PaymentStatus.FAILED,
                occurred_at=str(normalized["received_at"]),
                raw={"reason": "amount_mismatch", "normalized": normalized, "body": input.body},
            )

        return PaymentWebhookEvent(
            event_id=f"{self.provider_name}-confirm-{normalized['provider_txn_id']}",
            event_type="payment.confirmed" if status == PaymentStatus.SUCCEEDED else "payment.failed",
            payment_ref=payment_ref,
            status=status,
            occurred_at=str(normalized["received_at"]),
            raw=normalized,
        )

    # Existing collections engine compatibility methods
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

    def should_retry(self, error: AdapterError, *, attempt: int, max_attempts: int = 3) -> bool:
        if not error.retryable:
            return False
        return attempt < max_attempts

    def _validate_amount(self, amount_minor: int, ctx: AdapterContext) -> None:
        if amount_minor <= 0:
            raise AdapterError(
                code=AdapterErrorCode.VALIDATION_ERROR,
                message="Amount must be greater than zero.",
                retryable=False,
                provider=self.provider_name,
                provider_code="INVALID_AMOUNT",
                correlation_id=ctx.trace_id,
            )

    def _assert_pk_context(self, ctx: AdapterContext) -> None:
        if ctx.country_code.upper() != "PK":
            raise AdapterError(
                code=AdapterErrorCode.VALIDATION_ERROR,
                message="Pakistan adapter invoked for non-PK context.",
                retryable=False,
                provider=self.provider_name,
                provider_code="COUNTRY_MISMATCH",
                correlation_id=ctx.trace_id,
            )

    def _get_payment_or_raise(self, payment_ref: str, ctx: AdapterContext) -> dict[str, Any]:
        payment = self._payments.get(payment_ref)
        if payment is None:
            raise AdapterError(
                code=AdapterErrorCode.PROVIDER_UNAVAILABLE,
                message="Payment reference not found.",
                retryable=True,
                provider=self.provider_name,
                provider_code="NOT_FOUND",
                correlation_id=ctx.trace_id,
            )
        return payment

    def normalize_transaction(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
