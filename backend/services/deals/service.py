"""Deal pipeline and revenue linkage service (deal -> invoice -> payment)."""

from __future__ import annotations

from dataclasses import replace

from .entities import Deal, InvoiceLink, LeadContext, PaymentLink, RevenueAlignmentReport, RevenueIssue


class DealsRevenueService:
    def __init__(self, stage_probabilities: dict[str, float] | None = None) -> None:
        self._stage_probabilities = stage_probabilities or {
            "qualification": 0.2,
            "proposal": 0.5,
            "negotiation": 0.75,
            "closing": 0.9,
        }
        self._leads: dict[str, LeadContext] = {}
        self._deals: dict[str, Deal] = {}
        self._invoices: dict[str, InvoiceLink] = {}
        self._payments: dict[str, PaymentLink] = {}
        self._invoice_by_deal: dict[str, str] = {}
        self._payments_by_invoice: dict[str, list[str]] = {}

    def upsert_lead(self, lead: LeadContext) -> LeadContext:
        self._leads[lead.lead_id] = lead
        return lead

    def create_deal(self, deal: Deal) -> Deal:
        if deal.deal_id in self._deals:
            raise ValueError("Deal already exists")
        if deal.lead_id not in self._leads:
            raise ValueError("Deal must be tied to known lead")
        probability = self._stage_probabilities.get(deal.stage.lower(), 0.1)
        normalized = replace(deal, weighted_value=round(deal.expected_value * probability, 2))
        self._deals[deal.deal_id] = normalized
        return normalized

    def update_deal_state(self, deal_id: str, state: str) -> Deal:
        deal = self._deals[deal_id]
        if state not in {"open", "won", "lost"}:
            raise ValueError("Invalid deal state")
        updated = replace(deal, state=state)
        self._deals[deal_id] = updated
        return updated

    def link_invoice(self, invoice: InvoiceLink) -> InvoiceLink:
        if invoice.deal_id not in self._deals:
            raise ValueError("Invoice must map to existing deal")
        self._invoices[invoice.invoice_id] = invoice
        self._invoice_by_deal[invoice.deal_id] = invoice.invoice_id
        return invoice

    def link_payment(self, payment: PaymentLink) -> PaymentLink:
        if payment.invoice_id not in self._invoices:
            raise ValueError("Payment must map to existing invoice")
        self._payments[payment.payment_id] = payment
        self._payments_by_invoice.setdefault(payment.invoice_id, []).append(payment.payment_id)
        return payment

    def pipeline_value_by_stage(self) -> dict[str, float]:
        stage_totals: dict[str, float] = {}
        for deal in self._deals.values():
            if deal.state != "open":
                continue
            stage_totals[deal.stage] = round(stage_totals.get(deal.stage, 0.0) + deal.weighted_value, 2)
        return dict(sorted(stage_totals.items()))

    def validate_revenue_linkage(self) -> list[RevenueIssue]:
        issues: list[RevenueIssue] = []
        for deal in self._deals.values():
            invoice_id = self._invoice_by_deal.get(deal.deal_id)
            if deal.state == "won" and not invoice_id:
                issues.append(RevenueIssue("won_missing_invoice", deal.deal_id, "Won deal has no invoice link"))
                continue
            if deal.state == "lost" and invoice_id:
                issues.append(RevenueIssue("lost_has_invoice", deal.deal_id, "Lost deal should not carry invoice"))
            if not invoice_id:
                continue

            invoice = self._invoices[invoice_id]
            if invoice.currency != deal.currency:
                issues.append(RevenueIssue("currency_mismatch", deal.deal_id, "Deal and invoice currency mismatch"))

            payment_ids = self._payments_by_invoice.get(invoice_id, [])
            succeeded = [self._payments[pid] for pid in payment_ids if self._payments[pid].status == "succeeded"]

            if deal.state == "won" and not succeeded:
                issues.append(RevenueIssue("won_missing_payment", deal.deal_id, "Won deal invoice has no succeeded payment"))

            settled_amount = round(sum(payment.amount for payment in succeeded), 2)
            if settled_amount > invoice.amount:
                issues.append(RevenueIssue("over_collected", deal.deal_id, "Payments exceed invoice amount"))

        return issues

    def qc_alignment_report(self) -> RevenueAlignmentReport:
        issues = self.validate_revenue_linkage()
        checks = {
            "deals_have_valid_states": all(deal.state in {"open", "won", "lost"} for deal in self._deals.values()),
            "revenue_chain_present": all(
                deal.state != "won" or deal.deal_id in self._invoice_by_deal for deal in self._deals.values()
            ),
            "pipeline_value_tracking": bool(self.pipeline_value_by_stage()) or bool(self._deals),
            "no_link_inconsistencies": not issues,
        }
        passed = sum(1 for ok in checks.values() if ok)
        alignment = int((passed / len(checks)) * 100)
        return RevenueAlignmentReport(
            checks=checks,
            inconsistencies=issues,
            alignment_percent=alignment,
            score="10/10" if alignment == 100 and not issues else "needs-fix",
        )
