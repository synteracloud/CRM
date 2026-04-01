from services.deals import Deal, DealsRevenueService, InvoiceLink, LeadContext, PaymentLink


def test_pipeline_value_and_revenue_chain_alignment_10_on_consistent_links() -> None:
    service = DealsRevenueService(stage_probabilities={"proposal": 0.5, "negotiation": 0.8})
    service.upsert_lead(LeadContext(lead_id="lead-1", account_id="acct-1", owner_id="u-1"))
    service.upsert_lead(LeadContext(lead_id="lead-2", account_id="acct-2", owner_id="u-2"))

    open_deal = service.create_deal(
        Deal(
            deal_id="deal-open",
            lead_id="lead-1",
            title="Expansion",
            stage="proposal",
            state="open",
            expected_value=1000.0,
            weighted_value=0,
        )
    )
    assert open_deal.weighted_value == 500.0

    won_deal = service.create_deal(
        Deal(
            deal_id="deal-won",
            lead_id="lead-2",
            title="Renewal",
            stage="negotiation",
            state="open",
            expected_value=2000.0,
            weighted_value=0,
        )
    )
    service.update_deal_state(won_deal.deal_id, "won")
    service.link_invoice(InvoiceLink(invoice_id="inv-1", deal_id=won_deal.deal_id, amount=2000.0, currency="USD"))
    service.link_payment(
        PaymentLink(payment_id="pay-1", invoice_id="inv-1", amount=2000.0, currency="USD", status="succeeded")
    )

    assert service.pipeline_value_by_stage() == {"proposal": 500.0}

    report = service.qc_alignment_report()
    assert report.alignment_percent == 100
    assert report.score == "10/10"
    assert report.inconsistencies == []


def test_detects_revenue_linkage_inconsistencies() -> None:
    service = DealsRevenueService(stage_probabilities={"closing": 0.9})
    service.upsert_lead(LeadContext(lead_id="lead-3", account_id="acct-3", owner_id="u-3"))

    service.create_deal(
        Deal(
            deal_id="deal-bad",
            lead_id="lead-3",
            title="Bad Link",
            stage="closing",
            state="won",
            expected_value=1500.0,
            weighted_value=0,
        )
    )

    issues = service.validate_revenue_linkage()
    assert any(issue.code == "won_missing_invoice" for issue in issues)

    report = service.qc_alignment_report()
    assert report.alignment_percent < 100
    assert report.score == "needs-fix"
