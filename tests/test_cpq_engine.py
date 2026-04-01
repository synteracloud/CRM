from __future__ import annotations

from decimal import Decimal
import unittest

from src.rule_engine import CPQLineItemInput, CPQQuoteInput, CPQRulesEngine
from src.rule_engine.cpq_rules import (
    ApprovalPolicy,
    BundleRule,
    CPQRuleSet,
    ProductRulePolicy,
)


class CPQRulesEngineTests(unittest.TestCase):
    def test_pricing_and_bundles_apply_deterministically(self) -> None:
        engine = CPQRulesEngine()
        quote = CPQQuoteInput(
            quote_id="q-100",
            tenant_id="tenant-1",
            currency="USD",
            line_items=(
                CPQLineItemInput(
                    line_id="l-1",
                    product_id="core-crm",
                    quantity=2,
                    list_price=Decimal("100.00"),
                    requested_discount_percent=Decimal("5"),
                ),
                CPQLineItemInput(
                    line_id="l-2",
                    product_id="analytics-pro",
                    quantity=1,
                    list_price=Decimal("80.00"),
                    requested_discount_percent=Decimal("0"),
                ),
            ),
        )

        result = engine.evaluate_quote(quote)

        self.assertEqual(result.status, "approved")
        self.assertEqual(result.validation_errors, ())
        self.assertEqual(result.line_results[0].discount_percent, Decimal("15.00"))
        self.assertEqual(result.line_results[1].discount_percent, Decimal("10.00"))
        self.assertEqual(result.subtotal, Decimal("280.00"))
        self.assertEqual(result.discount_total, Decimal("38.00"))

    def test_quote_discount_triggers_approval_policy(self) -> None:
        engine = CPQRulesEngine()
        quote = CPQQuoteInput(
            quote_id="q-200",
            tenant_id="tenant-1",
            currency="USD",
            line_items=(
                CPQLineItemInput(
                    line_id="l-1",
                    product_id="core-crm",
                    quantity=1,
                    list_price=Decimal("1000.00"),
                    requested_discount_percent=Decimal("10"),
                ),
                CPQLineItemInput(
                    line_id="l-2",
                    product_id="analytics-pro",
                    quantity=1,
                    list_price=Decimal("100.00"),
                    requested_discount_percent=Decimal("0"),
                ),
            ),
            requested_quote_discount_percent=Decimal("10"),
        )

        result = engine.evaluate_quote(quote)

        self.assertEqual(result.status, "approval_required")
        self.assertTrue(result.approval.required)
        self.assertEqual(result.approval.policy_code, "discount-band-20")

    def test_invalid_pricing_is_blocked_and_never_negative(self) -> None:
        ruleset = CPQRuleSet(
            tax_rate_percent=Decimal("0"),
            quote_max_discount_percent=Decimal("100"),
            product_policies={"p1": ProductRulePolicy(max_discount_percent=Decimal("95"))},
            bundle_rules=(BundleRule(bundle_id="b1", required_products=("p1",), discount_percent=Decimal("10")),),
            approval_policies=(ApprovalPolicy(policy_code="noop"),),
        )
        engine = CPQRulesEngine(ruleset)
        quote = CPQQuoteInput(
            quote_id="q-300",
            tenant_id="tenant-1",
            currency="USD",
            line_items=(
                CPQLineItemInput(
                    line_id="l-1",
                    product_id="p1",
                    quantity=1,
                    list_price=Decimal("100.00"),
                    requested_discount_percent=Decimal("95"),
                ),
            ),
        )

        result = engine.evaluate_quote(quote)

        self.assertEqual(result.status, "draft")
        self.assertIn("invalid pricing discount", " | ".join(result.validation_errors))
        self.assertEqual(result.line_results[0].net_unit_price, Decimal("0.00"))
        self.assertEqual(result.line_results[0].extended_price, Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
