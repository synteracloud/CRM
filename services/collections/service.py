"""Collections engine service implementing invoice->payment->reconciliation lifecycle."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from typing import Protocol

from .automation import CollectionsAutomationEngine
from .automation.entities import AutomationCycleReport, CustomerResponse
from .entities import Invoice, Payment, ReconciliationCase, ReviewReport
from .reminders import ReminderScheduler


class PaymentAdapter(Protocol):
    provider_name: str

    def normalize_transaction(self, payload: dict[str, object]) -> dict[str, object]:
        ...

    def verify_callback(self, signature: str, payload: dict[str, object]) -> bool:
        ...


class CollectionsService:
    def __init__(self, adapters: dict[str, PaymentAdapter] | None = None) -> None:
        self._adapters = adapters or {}
        self._invoices: dict[str, Invoice] = {}
        self._invoice_by_number: dict[str, str] = {}
        self._payments: dict[str, Payment] = {}
        self._payments_by_provider_txn: set[tuple[str, str]] = set()
        self._reconciliation_cases: dict[str, ReconciliationCase] = {}
        self._invoice_to_payments: dict[str, list[str]] = {}
        self._scheduler = ReminderScheduler()
        self._automation = CollectionsAutomationEngine()

    def create_invoice(self, invoice: Invoice) -> Invoice:
        if invoice.invoice_id in self._invoices or invoice.invoice_number in self._invoice_by_number:
            raise ValueError("Invoice already exists")
        normalized = replace(invoice, amount_outstanding=invoice.total_amount, state="unpaid", overdue_days=0)
        self._invoices[invoice.invoice_id] = normalized
        self._invoice_by_number[invoice.invoice_number] = invoice.invoice_id
        return normalized

    def get_invoice(self, invoice_id: str) -> Invoice:
        return self._invoices[invoice_id]

    def list_invoice_reminders(self, invoice_id: str) -> list[str]:
        invoice = self.get_invoice(invoice_id)
        return [event.scheduled_at for event in self._scheduler.schedule(invoice_id, invoice.due_date)]

    def ingest_payment(self, provider: str, signature: str, payload: dict[str, object]) -> tuple[Payment, ReconciliationCase | None]:
        adapter = self._adapters[provider]
        if not adapter.verify_callback(signature, payload):
            raise ValueError("Invalid callback signature")
        normalized = adapter.normalize_transaction(payload)

        provider_txn_id = str(normalized["provider_txn_id"])
        idempotency_key = (provider, provider_txn_id)
        if idempotency_key in self._payments_by_provider_txn:
            raise ValueError("Duplicate provider transaction")

        payment = Payment(
            payment_id=f"pay-{len(self._payments)+1}",
            provider=provider,  # type: ignore[arg-type]
            provider_txn_id=provider_txn_id,
            invoice_ref=str(normalized.get("invoice_ref")) if normalized.get("invoice_ref") else None,
            customer_ref=str(normalized["customer_ref"]),
            amount=float(normalized["amount"]),
            currency=str(normalized["currency"]),
            status=str(normalized["status"]),  # type: ignore[arg-type]
            received_at=str(normalized["received_at"]),
            settled_at=str(normalized.get("settled_at")) if normalized.get("settled_at") else None,
            raw_payload=payload,
        )
        self._payments[payment.payment_id] = payment
        self._payments_by_provider_txn.add(idempotency_key)

        case = self._reconcile(payment)
        return payment, case

    def _reconcile(self, payment: Payment) -> ReconciliationCase | None:
        if payment.status != "succeeded":
            return None

        target_invoice: Invoice | None = None
        mismatch_reason = "unknown"

        if payment.invoice_ref and payment.invoice_ref in self._invoice_by_number:
            target_invoice = self._invoices[self._invoice_by_number[payment.invoice_ref]]
            mismatch_reason = "amount_diff" if payment.amount != target_invoice.amount_outstanding else "unknown"
        else:
            for invoice in self._invoices.values():
                if invoice.customer_id == payment.customer_ref and invoice.currency == payment.currency and invoice.amount_outstanding > 0:
                    target_invoice = invoice
                    mismatch_reason = "missing_ref"
                    break

        if target_invoice is None:
            case = ReconciliationCase(
                case_id=f"rec-{len(self._reconciliation_cases)+1}",
                payment_id=payment.payment_id,
                invoice_id=None,
                match_status="needs_review",
                mismatch_reason="missing_ref",
                resolver_user_id=None,
                resolution_action=None,
                resolved_at=None,
            )
            self._reconciliation_cases[case.case_id] = case
            return case

        applied = min(target_invoice.amount_outstanding, payment.amount)
        new_paid = round(target_invoice.amount_paid + applied, 2)
        outstanding = round(target_invoice.total_amount - new_paid, 2)
        state = self._derive_state(target_invoice, outstanding, payment.received_at[:10])

        updated_invoice = replace(
            target_invoice,
            amount_paid=new_paid,
            amount_outstanding=outstanding,
            state=state,
            overdue_days=self._overdue_days(target_invoice.due_date, outstanding, payment.received_at[:10]),
        )
        self._invoices[target_invoice.invoice_id] = updated_invoice
        self._invoice_to_payments.setdefault(target_invoice.invoice_id, []).append(payment.payment_id)

        case = ReconciliationCase(
            case_id=f"rec-{len(self._reconciliation_cases)+1}",
            payment_id=payment.payment_id,
            invoice_id=target_invoice.invoice_id,
            match_status="auto_matched",
            mismatch_reason=mismatch_reason,  # type: ignore[arg-type]
            resolver_user_id=None,
            resolution_action="applied_to_invoice",
            resolved_at=payment.received_at,
        )
        self._reconciliation_cases[case.case_id] = case
        return case


    def run_automation_cycle(self, invoice_id: str, payment_received: bool = False) -> AutomationCycleReport:
        invoice = self.get_invoice(invoice_id)
        plan = self._automation.build_plan(invoice)
        for touchpoint in plan.touchpoints:
            self._automation.mark_sent(invoice_id, touchpoint.sequence)
        return self._automation.evaluate_cycle(invoice, payment_received=payment_received)

    def track_customer_response(self, invoice_id: str, reminder_sequence: int, replied: bool, note: str | None = None) -> Invoice:
        response = CustomerResponse(
            invoice_id=invoice_id,
            reminder_sequence=reminder_sequence,
            state="replied" if replied else "ignored",
            response_note=note,
        )
        decision = self._automation.track_response(response)
        current = self.get_invoice(invoice_id)
        updated = self._automation.apply_escalation(current, decision)
        self._invoices[invoice_id] = updated
        return updated

    def run_overdue_rollup(self, as_of: str) -> list[Invoice]:
        out: list[Invoice] = []
        today = date.fromisoformat(as_of)
        for invoice_id, invoice in list(self._invoices.items()):
            if invoice.amount_outstanding <= 0:
                continue
            due = date.fromisoformat(invoice.due_date)
            if today > due:
                overdue_days = (today - due).days
                state = "overdue" if invoice.state in {"unpaid", "partial", "overdue"} else invoice.state
                updated = replace(invoice, state=state, overdue_days=overdue_days)
                self._invoices[invoice_id] = updated
                out.append(updated)
        return out

    def review_lifecycle_alignment(self) -> ReviewReport:
        checks = {
            "invoicing": bool(self._invoices),
            "payments": bool(self._payments),
            "reminders": any(self.list_invoice_reminders(iid) for iid in self._invoices),
            "reconciliation": bool(self._reconciliation_cases),
            "states": all(i.state in {"unpaid", "partial", "paid", "overdue"} for i in self._invoices.values()),
        }
        missing = [name for name, ok in checks.items() if not ok]
        percent = int((sum(1 for ok in checks.values() if ok) / len(checks)) * 100)
        return ReviewReport(
            lifecycle_steps=checks,
            missing_flows=missing,
            alignment_percent=percent,
            score="10/10" if percent == 100 and not missing else "needs-fix",
        )

    @staticmethod
    def _derive_state(invoice: Invoice, outstanding: float, as_of: str) -> str:
        if outstanding <= 0:
            return "paid"
        if 0 < outstanding < invoice.total_amount:
            if date.fromisoformat(as_of) > date.fromisoformat(invoice.due_date):
                return "overdue"
            return "partial"
        if date.fromisoformat(as_of) > date.fromisoformat(invoice.due_date):
            return "overdue"
        return "unpaid"

    @staticmethod
    def _overdue_days(due_date: str, outstanding: float, as_of: str) -> int:
        if outstanding <= 0:
            return 0
        delta = (date.fromisoformat(as_of) - date.fromisoformat(due_date)).days
        return max(0, delta)
