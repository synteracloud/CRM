"""Collections automation engine: reminder cycle, response tracking, and escalation."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta

from services.collections.entities import Invoice

from .entities import (
    AutomationCycleReport,
    CustomerResponse,
    EscalationDecision,
    ReminderPlan,
    ReminderTouchpoint,
)
from .templates import MessageTemplateCatalog


class CollectionsAutomationEngine:
    def __init__(self, templates: MessageTemplateCatalog | None = None) -> None:
        self._templates = templates or MessageTemplateCatalog()
        self._responses_by_invoice: dict[str, list[CustomerResponse]] = {}
        self._sent_sequences_by_invoice: dict[str, list[int]] = {}

    def build_plan(self, invoice: Invoice) -> ReminderPlan:
        touchpoints = (
            ReminderTouchpoint(stage="pre_due", offset_days=-3, sequence=1),
            ReminderTouchpoint(stage="due", offset_days=0, sequence=2),
            ReminderTouchpoint(stage="overdue", offset_days=1, sequence=3),
            ReminderTouchpoint(stage="overdue", offset_days=4, sequence=4),
        )
        return ReminderPlan(invoice_id=invoice.invoice_id, due_date=invoice.due_date, touchpoints=touchpoints)

    def next_message(self, invoice: Invoice, sequence: int) -> tuple[str, str, str]:
        plan = self.build_plan(invoice)
        touchpoint = plan.touchpoints[sequence - 1]
        template = self._templates.get(touchpoint.stage, invoice.escalation_level)
        scheduled_at = (date.fromisoformat(invoice.due_date) + timedelta(days=touchpoint.offset_days)).isoformat()
        return template.template_id, template.body, scheduled_at

    def mark_sent(self, invoice_id: str, sequence: int) -> None:
        sent = self._sent_sequences_by_invoice.setdefault(invoice_id, [])
        if sequence not in sent:
            sent.append(sequence)

    def track_response(self, response: CustomerResponse) -> EscalationDecision | None:
        history = self._responses_by_invoice.setdefault(response.invoice_id, [])
        history.append(response)
        ignored_count = sum(1 for item in history if item.state == "ignored")
        if ignored_count >= 2:
            return EscalationDecision(
                invoice_id=response.invoice_id,
                escalation_level=min(3, ignored_count),
                reason="repeated_reminders_ignored",
                next_tone="firm",
            )
        return None

    def apply_escalation(self, invoice: Invoice, decision: EscalationDecision | None) -> Invoice:
        if decision is None:
            return invoice
        return replace(invoice, escalation_level=max(invoice.escalation_level, decision.escalation_level))

    def evaluate_cycle(self, invoice: Invoice, payment_received: bool) -> AutomationCycleReport:
        expected = len(self.build_plan(invoice).touchpoints)
        sent = len(self._sent_sequences_by_invoice.get(invoice.invoice_id, []))
        responses = self._responses_by_invoice.get(invoice.invoice_id, [])
        ignored = sum(1 for item in responses if item.state == "ignored")
        replied = sum(1 for item in responses if item.state == "replied")

        checks = {
            "full_reminder_cycle": sent >= expected,
            "missed_payment_detected": (not payment_received and sent >= 2),
            "response_tracking": ignored + replied == len(responses),
            "escalation_applied": invoice.escalation_level >= 2 if ignored >= 2 else True,
        }
        alignment = int((sum(1 for ok in checks.values() if ok) / len(checks)) * 100)
        diagnostics = [name for name, ok in checks.items() if not ok]
        return AutomationCycleReport(
            invoice_id=invoice.invoice_id,
            expected_reminders=expected,
            sent_reminders=sent,
            missed_payment_detected=checks["missed_payment_detected"],
            ignored_count=ignored,
            replied_count=replied,
            alignment_percent=alignment,
            score="10/10" if alignment == 100 else "needs-fix",
            diagnostics=diagnostics,
        )
