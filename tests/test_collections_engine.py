from __future__ import annotations

import hashlib
import hmac
import unittest

from adapters.pakistan.payments import EasypaisaAdapter, JazzCashAdapter
from services.collections import CollectionsService, Invoice


class StubWhatsApp:
    def send_template(self, *, to: str, template_id: str, params: dict[str, str]) -> str:
        return "sent"


def sign(secret: str, payload: dict[str, object]) -> str:
    return hmac.new(secret.encode("utf-8"), str(payload).encode("utf-8"), hashlib.sha256).hexdigest()


class CollectionsEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jazz = JazzCashAdapter(merchant_id="m-1", secret="jc-secret")
        self.easy = EasypaisaAdapter(merchant_id="m-2", secret="ep-secret")
        self.service = CollectionsService(adapters={"jazzcash": self.jazz, "easypaisa": self.easy})

    def test_full_lifecycle_invoice_payment_reconciliation_and_review(self) -> None:
        invoice = self.service.create_invoice(
            Invoice(
                invoice_id="inv-1",
                invoice_number="INV-100",
                customer_id="cust-1",
                issue_date="2026-03-01",
                due_date="2026-03-10",
                currency="PKR",
                total_amount=1000.0,
            )
        )
        self.assertEqual(invoice.state, "unpaid")
        self.assertEqual(len(self.service.list_invoice_reminders("inv-1")), 5)

        payload_partial = {
            "txn_id": "JZ-1",
            "invoice_number": "INV-100",
            "customer_id": "cust-1",
            "amount": 300,
            "currency": "PKR",
            "status": "paid",
            "timestamp": "2026-03-05T10:00:00Z",
        }
        payment, rec_case = self.service.ingest_payment("jazzcash", sign("jc-secret", payload_partial), payload_partial)
        self.assertEqual(payment.status, "succeeded")
        self.assertIsNotNone(rec_case)
        self.assertEqual(self.service.get_invoice("inv-1").state, "partial")

        payload_full = {
            "transaction_id": "EP-1",
            "merchant_reference": "INV-100",
            "customer_ref": "cust-1",
            "amount": 700,
            "payment_status": "SUCCESS",
            "event_time": "2026-03-06T12:00:00Z",
        }
        self.service.ingest_payment("easypaisa", sign("ep-secret", payload_full), payload_full)
        final_invoice = self.service.get_invoice("inv-1")
        self.assertEqual(final_invoice.amount_outstanding, 0)
        self.assertEqual(final_invoice.state, "paid")

        report = self.service.review_lifecycle_alignment()
        self.assertEqual(report.alignment_percent, 100)
        self.assertEqual(report.score, "10/10")

    def test_overdue_and_missing_ref_flow(self) -> None:
        self.service.create_invoice(
            Invoice(
                invoice_id="inv-2",
                invoice_number="INV-200",
                customer_id="cust-2",
                issue_date="2026-02-01",
                due_date="2026-02-10",
                currency="PKR",
                total_amount=500,
            )
        )
        overdue = self.service.run_overdue_rollup(as_of="2026-02-15")
        self.assertEqual(overdue[0].state, "overdue")

        payload_no_ref = {
            "txn_id": "JZ-2",
            "customer_id": "cust-999",
            "amount": 100,
            "status": "paid",
            "timestamp": "2026-02-16T00:00:00Z",
        }
        _, rec = self.service.ingest_payment("jazzcash", sign("jc-secret", payload_no_ref), payload_no_ref)
        assert rec is not None
        self.assertEqual(rec.match_status, "needs_review")


if __name__ == "__main__":
    unittest.main()
