"""CPQ rules engine for pricing, discounting, validation, and approval orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

Money = Decimal
QuoteStatus = Literal["draft", "approval_required", "approved", "rejected", "accepted"]


@dataclass(frozen=True)
class CPQLineItemInput:
    line_id: str
    product_id: str
    quantity: int
    list_price: Money
    requested_discount_percent: Decimal = Decimal("0")


@dataclass(frozen=True)
class CPQQuoteInput:
    quote_id: str
    tenant_id: str
    currency: str
    line_items: tuple[CPQLineItemInput, ...]
    requested_quote_discount_percent: Decimal = Decimal("0")


@dataclass(frozen=True)
class CPQLineResult:
    line_id: str
    product_id: str
    quantity: int
    list_price: Money
    discount_percent: Decimal
    net_unit_price: Money
    extended_price: Money


@dataclass(frozen=True)
class ApprovalDecision:
    required: bool
    policy_code: str | None
    reasons: tuple[str, ...]
    assigned_approver_role: str | None


@dataclass(frozen=True)
class CPQQuoteEvaluation:
    quote_id: str
    status: QuoteStatus
    line_results: tuple[CPQLineResult, ...]
    subtotal: Money
    discount_total: Money
    tax_total: Money
    grand_total: Money
    validation_errors: tuple[str, ...]
    approval: ApprovalDecision


@dataclass(frozen=True)
class QuoteApprovalTransitionResult:
    quote_id: str
    previous_status: QuoteStatus
    new_status: QuoteStatus
    emitted_events: tuple[str, ...]


@dataclass(frozen=True)
class ProductRulePolicy:
    max_discount_percent: Decimal
    must_bundle_with: tuple[str, ...] = ()
    disallow_with: tuple[str, ...] = ()


@dataclass(frozen=True)
class BundleRule:
    bundle_id: str
    required_products: tuple[str, ...]
    discount_percent: Decimal


@dataclass(frozen=True)
class ApprovalPolicy:
    policy_code: str
    min_discount_percent: Decimal = Decimal("0")
    min_grand_total: Money = Decimal("0")
    approver_role: str = "sales_manager"


@dataclass(frozen=True)
class CPQRuleSet:
    tax_rate_percent: Decimal
    quote_max_discount_percent: Decimal
    product_policies: dict[str, ProductRulePolicy]
    bundle_rules: tuple[BundleRule, ...]
    approval_policies: tuple[ApprovalPolicy, ...]


DEFAULT_CPQ_RULESET = CPQRuleSet(
    tax_rate_percent=Decimal("8.25"),
    quote_max_discount_percent=Decimal("20"),
    product_policies={
        "core-crm": ProductRulePolicy(max_discount_percent=Decimal("15")),
        "analytics-pro": ProductRulePolicy(max_discount_percent=Decimal("20"), must_bundle_with=("core-crm",)),
        "support-plus": ProductRulePolicy(max_discount_percent=Decimal("25"), disallow_with=("legacy-support",)),
        "legacy-support": ProductRulePolicy(max_discount_percent=Decimal("5"), disallow_with=("support-plus",)),
    },
    bundle_rules=(
        BundleRule(bundle_id="bundle-growth", required_products=("core-crm", "analytics-pro"), discount_percent=Decimal("10")),
    ),
    approval_policies=(
        ApprovalPolicy(policy_code="discount-band-15", min_discount_percent=Decimal("15"), approver_role="sales_manager"),
        ApprovalPolicy(policy_code="discount-band-20", min_discount_percent=Decimal("20"), approver_role="finance_controller"),
        ApprovalPolicy(policy_code="large-deal-100k", min_grand_total=Decimal("100000"), approver_role="finance_controller"),
    ),
)


class CPQRulesEngine:
    """Deterministic CPQ evaluator aligned to quote approval workflow."""

    def __init__(self, ruleset: CPQRuleSet = DEFAULT_CPQ_RULESET) -> None:
        self._ruleset = ruleset

    def evaluate_quote(self, quote: CPQQuoteInput) -> CPQQuoteEvaluation:
        validation_errors = self._validate_quote(quote)
        line_results = self._price_lines(quote)
        subtotal = _money(sum((line.list_price * line.quantity for line in line_results), start=Decimal("0")))
        discounted_total = _money(sum((line.extended_price for line in line_results), start=Decimal("0")))

        quote_level_discount = _money(discounted_total * (quote.requested_quote_discount_percent / Decimal("100")))
        quote_level_discount = min(quote_level_discount, discounted_total)
        net_before_tax = _money(discounted_total - quote_level_discount)
        tax_total = _money(net_before_tax * (self._ruleset.tax_rate_percent / Decimal("100")))
        grand_total = _money(net_before_tax + tax_total)
        discount_total = _money(subtotal - net_before_tax)

        approval = self._evaluate_approval(discount_total, subtotal, grand_total)
        status: QuoteStatus = "approved"
        if validation_errors:
            status = "draft"
        elif approval.required:
            status = "approval_required"

        return CPQQuoteEvaluation(
            quote_id=quote.quote_id,
            status=status,
            line_results=line_results,
            subtotal=subtotal,
            discount_total=discount_total,
            tax_total=tax_total,
            grand_total=grand_total,
            validation_errors=validation_errors,
            approval=approval,
        )

    def apply_approval_transition(
        self,
        quote_id: str,
        current_status: QuoteStatus,
        action: Literal["submit", "approve", "reject", "accept_customer"],
    ) -> QuoteApprovalTransitionResult:
        transitions: dict[tuple[QuoteStatus, str], tuple[QuoteStatus, tuple[str, ...]]] = {
            ("draft", "submit"): ("approval_required", ("quote.submitted_for_approval.v1", "approval.requested.v1")),
            ("approval_required", "approve"): ("approved", ("approval.decided.v1",)),
            ("approval_required", "reject"): ("rejected", ("approval.decided.v1",)),
            ("approved", "accept_customer"): ("accepted", ("quote.accepted.v1", "order.created.v1")),
        }
        key = (current_status, action)
        if key not in transitions:
            raise ValueError(f"Invalid approval transition from {current_status} using {action}")

        new_status, emitted = transitions[key]
        return QuoteApprovalTransitionResult(
            quote_id=quote_id,
            previous_status=current_status,
            new_status=new_status,
            emitted_events=emitted,
        )

    def _validate_quote(self, quote: CPQQuoteInput) -> tuple[str, ...]:
        errors: list[str] = []
        if not quote.line_items:
            errors.append("Quote must contain at least one line item")

        if quote.requested_quote_discount_percent > self._ruleset.quote_max_discount_percent:
            errors.append(
                f"Quote discount {quote.requested_quote_discount_percent}% exceeds maximum {self._ruleset.quote_max_discount_percent}%"
            )

        products = {item.product_id for item in quote.line_items}
        bundle_discounts = self._bundle_discounts(products)
        for item in quote.line_items:
            if item.quantity <= 0:
                errors.append(f"Line {item.line_id} has invalid quantity {item.quantity}")
            if item.list_price < Decimal("0"):
                errors.append(f"Line {item.line_id} has invalid list price {item.list_price}")
            policy = self._ruleset.product_policies.get(item.product_id)
            if policy is None:
                errors.append(f"Product {item.product_id} does not exist in pricing policy")
                continue
            if item.requested_discount_percent > policy.max_discount_percent:
                errors.append(
                    f"Line {item.line_id} discount {item.requested_discount_percent}% exceeds max {policy.max_discount_percent}%"
                )
            combined_discount = item.requested_discount_percent + bundle_discounts.get(item.product_id, Decimal("0"))
            if combined_discount > Decimal("100"):
                errors.append(
                    f"Line {item.line_id} has invalid pricing discount {combined_discount}% (must be <= 100%)"
                )
            for must_have in policy.must_bundle_with:
                if must_have not in products:
                    errors.append(f"Product {item.product_id} must be bundled with {must_have}")
            for excluded in policy.disallow_with:
                if excluded in products:
                    errors.append(f"Invalid product combination: {item.product_id} with {excluded}")

        for bundle in self._ruleset.bundle_rules:
            matched = [required in products for required in bundle.required_products]
            if any(matched) and not all(matched):
                missing = [required for required in bundle.required_products if required not in products]
                errors.append(f"Bundle {bundle.bundle_id} is incomplete; missing {', '.join(sorted(missing))}")

        return tuple(sorted(set(errors)))

    def _price_lines(self, quote: CPQQuoteInput) -> tuple[CPQLineResult, ...]:
        products = {item.product_id for item in quote.line_items}
        bundle_discounts = self._bundle_discounts(products)

        lines: list[CPQLineResult] = []
        for item in sorted(quote.line_items, key=lambda entry: entry.line_id):
            discount_percent = _quantize_percent(item.requested_discount_percent + bundle_discounts.get(item.product_id, Decimal("0")))
            discount_percent = min(discount_percent, Decimal("100"))
            discount_multiplier = Decimal("1") - (discount_percent / Decimal("100"))
            net_unit = _money(item.list_price * discount_multiplier)
            lines.append(
                CPQLineResult(
                    line_id=item.line_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    list_price=_money(item.list_price),
                    discount_percent=discount_percent,
                    net_unit_price=net_unit,
                    extended_price=_money(net_unit * item.quantity),
                )
            )
        return tuple(lines)

    def _bundle_discounts(self, products: set[str]) -> dict[str, Decimal]:
        result: dict[str, Decimal] = {}
        for bundle in self._ruleset.bundle_rules:
            if all(required in products for required in bundle.required_products):
                for product in bundle.required_products:
                    result[product] = _quantize_percent(result.get(product, Decimal("0")) + bundle.discount_percent)
        return result

    def _evaluate_approval(self, discount_total: Money, subtotal: Money, grand_total: Money) -> ApprovalDecision:
        if subtotal <= Decimal("0"):
            return ApprovalDecision(required=False, policy_code=None, reasons=(), assigned_approver_role=None)

        effective_discount_pct = _quantize_percent((discount_total / subtotal) * Decimal("100"))
        matched: list[ApprovalPolicy] = []
        reasons: list[str] = []

        for policy in sorted(self._ruleset.approval_policies, key=lambda p: p.policy_code):
            discount_hit = effective_discount_pct >= policy.min_discount_percent and policy.min_discount_percent > Decimal("0")
            value_hit = grand_total >= policy.min_grand_total and policy.min_grand_total > Decimal("0")
            if discount_hit or value_hit:
                matched.append(policy)
                reasons.append(
                    f"{policy.policy_code}: discount={effective_discount_pct}% grand_total={grand_total}"
                )

        if not matched:
            return ApprovalDecision(required=False, policy_code=None, reasons=(), assigned_approver_role=None)

        strictest = sorted(matched, key=lambda p: (p.min_discount_percent, p.min_grand_total, p.policy_code), reverse=True)[0]
        return ApprovalDecision(
            required=True,
            policy_code=strictest.policy_code,
            reasons=tuple(reasons),
            assigned_approver_role=strictest.approver_role,
        )


def _money(value: Decimal | int | float) -> Money:
    normalized = value if isinstance(value, Decimal) else Decimal(str(value))
    return normalized.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _quantize_percent(value: Decimal | int | float) -> Decimal:
    normalized = value if isinstance(value, Decimal) else Decimal(str(value))
    return normalized.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
