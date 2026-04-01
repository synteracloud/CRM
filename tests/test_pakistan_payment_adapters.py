from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
import unittest

from adapters.interfaces.payment_adapter import (
    PaymentCaptureInput,
    PaymentCreateInput,
    PaymentStatusInput,
    RawWebhookInput,
)
from adapters.interfaces.types import AdapterContext, AdapterError, AdapterErrorCode
from adapters.pakistan.payments import EasypaisaAdapter, JazzCashAdapter


REPO_ROOT = Path(__file__).resolve().parents[1]


def sign(secret: str, payload: dict[str, object]) -> str:
    return hmac.new(secret.encode("utf-8"), str(payload).encode("utf-8"), hashlib.sha256).hexdigest()


class PakistanPaymentAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ctx = AdapterContext(tenant_id="tenant-1", trace_id="trace-1", country_code="PK", channel="payments")
        self.jazz = JazzCashAdapter(merchant_id="m-1", secret="jc-secret")
        self.easy = EasypaisaAdapter(merchant_id="m-2", secret="ep-secret")

    def test_jazzcash_create_capture_and_status(self) -> None:
        created = self.jazz.create_payment(
            PaymentCreateInput(
                idempotency_key="idem-1",
                order_id="ORD-1",
                customer_id="cust-1",
                amount_minor=15000,
                currency="PKR",
                callback_url="https://example.com/callback",
            ),
            self.ctx,
        )
        self.assertEqual(created.status.value, "initiated")

        captured = self.jazz.capture_payment(PaymentCaptureInput(payment_ref=created.payment_ref), self.ctx)
        self.assertEqual(captured.status.value, "succeeded")

        status = self.jazz.get_payment_status(PaymentStatusInput(payment_ref=created.payment_ref), self.ctx)
        self.assertEqual(status.status.value, "succeeded")

    def test_easypaisa_webhook_confirmation_and_mismatch(self) -> None:
        success_payload = {
            "transaction_id": "EP-1",
            "merchant_reference": "INV-100",
            "customer_ref": "cust-1",
            "amount": 700,
            "payment_status": "SUCCESS",
            "event_time": "2026-03-06T12:00:00Z",
            "expected_amount_minor": 70000,
        }
        success_event = self.easy.parse_webhook(
            RawWebhookInput(headers={"x-signature": sign("ep-secret", success_payload)}, body=success_payload),
            self.ctx,
        )
        self.assertEqual(success_event.event_type, "payment.confirmed")

        mismatch_payload = dict(success_payload)
        mismatch_payload["expected_amount_minor"] = 69900
        mismatch_event = self.easy.parse_webhook(
            RawWebhookInput(headers={"x-signature": sign("ep-secret", mismatch_payload)}, body=mismatch_payload),
            self.ctx,
        )
        self.assertEqual(mismatch_event.event_type, "payment.mismatch")

    def test_retry_policy_and_validation_error(self) -> None:
        with self.assertRaises(AdapterError) as err:
            self.jazz.create_payment(
                PaymentCreateInput(
                    idempotency_key="idem-2",
                    order_id="ORD-2",
                    customer_id="cust-1",
                    amount_minor=0,
                    currency="PKR",
                ),
                self.ctx,
            )
        self.assertEqual(err.exception.code, AdapterErrorCode.VALIDATION_ERROR)
        self.assertFalse(self.jazz.should_retry(err.exception, attempt=1))

        transient = AdapterError(
            code=AdapterErrorCode.PROVIDER_UNAVAILABLE,
            message="Temporary outage",
            retryable=True,
            provider="jazzcash",
        )
        self.assertTrue(self.jazz.should_retry(transient, attempt=1, max_attempts=3))
        self.assertFalse(self.jazz.should_retry(transient, attempt=3, max_attempts=3))


class AdapterIsolationTests(unittest.TestCase):
    def test_core_and_services_do_not_import_country_adapters(self) -> None:
        leaked: list[str] = []
        for scope in ("services", "src"):
            for py_file in (REPO_ROOT / scope).rglob("*.py"):
                text = py_file.read_text(encoding="utf-8")
                if "adapters.pakistan" in text:
                    leaked.append(str(py_file.relative_to(REPO_ROOT)))
        self.assertEqual(leaked, [], f"core leakage detected: {leaked}")


if __name__ == "__main__":
    unittest.main()
