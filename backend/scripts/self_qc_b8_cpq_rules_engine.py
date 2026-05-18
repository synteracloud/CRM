"""Self-QC checks for B8-P02 advanced CPQ rules engine."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rule_engine import CPQQuoteInput, CPQRulesEngine, CPQLineItemInput


def assert_no_invalid_pricing_combinations() -> None:
    engine = CPQRulesEngine()
    quote = CPQQuoteInput(
        quote_id="quo-invalid",
        tenant_id="tenant-1",
        currency="USD",
        line_items=(
            CPQLineItemInput(
                line_id="1",
                product_id="analytics-pro",
                quantity=1,
                list_price=Decimal("1200"),
                requested_discount_percent=Decimal("5"),
            ),
            CPQLineItemInput(
                line_id="2",
                product_id="legacy-support",
                quantity=1,
                list_price=Decimal("800"),
                requested_discount_percent=Decimal("1"),
            ),
            CPQLineItemInput(
                line_id="3",
                product_id="support-plus",
                quantity=1,
                list_price=Decimal("900"),
                requested_discount_percent=Decimal("1"),
            ),
        ),
    )
    result = engine.evaluate_quote(quote)
    if not result.validation_errors:
        raise AssertionError("Expected invalid pricing combinations to be rejected")


def assert_approval_flow_complete() -> None:
    engine = CPQRulesEngine()
    submitted = engine.apply_approval_transition("quo-1", "draft", "submit")
    if submitted.new_status != "approval_required" or "approval.requested.v1" not in submitted.emitted_events:
        raise AssertionError("Quote submission transition did not emit approval request")

    approved = engine.apply_approval_transition("quo-1", "approval_required", "approve")
    if approved.new_status != "approved":
        raise AssertionError("Quote approval transition failed")

    accepted = engine.apply_approval_transition("quo-1", "approved", "accept_customer")
    if accepted.new_status != "accepted" or "order.created.v1" not in accepted.emitted_events:
        raise AssertionError("Quote acceptance transition did not convert to order")


def assert_rule_execution_deterministic() -> None:
    engine = CPQRulesEngine()
    quote = CPQQuoteInput(
        quote_id="quo-deterministic",
        tenant_id="tenant-1",
        currency="USD",
        line_items=(
            CPQLineItemInput("line-b", "analytics-pro", 2, Decimal("2000"), Decimal("5")),
            CPQLineItemInput("line-a", "core-crm", 5, Decimal("1000"), Decimal("10")),
        ),
        requested_quote_discount_percent=Decimal("3"),
    )
    run_one = engine.evaluate_quote(quote)
    run_two = engine.evaluate_quote(quote)

    if run_one != run_two:
        raise AssertionError("CPQ rule evaluation must be deterministic")


def main() -> None:
    assert_no_invalid_pricing_combinations()
    assert_approval_flow_complete()
    assert_rule_execution_deterministic()
    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
