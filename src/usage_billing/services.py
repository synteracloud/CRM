"""Usage billing services: collection, dedupe, aggregation, rating, invoice inputs."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime

from .entities import (
    BillableEventRule,
    InvoiceInput,
    MeterRateCard,
    RatedUsageLine,
    TierPrice,
    TRACKED_BILLABLE_EVENT_NAMES,
    TrackedEvent,
    UsageAggregate,
    UsageRecord,
)


class UsageBillingError(ValueError):
    """Raised for invalid metering/rating setup or payloads."""


class UsageBillingService:
    """Collect tracked events into billable usage, then aggregate and rate."""

    def __init__(self) -> None:
        self._processed_event_keys: set[tuple[str, str, str]] = set()

    def collect_billable_events(
        self,
        events: list[TrackedEvent],
        rules: list[BillableEventRule],
    ) -> list[UsageRecord]:
        """Derive usage from tracked events and skip duplicate charges by event identity."""
        rule_by_event_name = {rule.event_name: rule for rule in rules}
        usage_records: list[UsageRecord] = []

        for event in events:
            if event.event_name not in TRACKED_BILLABLE_EVENT_NAMES:
                continue

            rule = rule_by_event_name.get(event.event_name)
            if rule is None:
                continue

            event_identity = (event.tenant_id, event.event_name, event.event_id)
            if event_identity in self._processed_event_keys:
                continue

            quantity = self._extract_quantity(event, rule)
            if quantity <= 0:
                continue

            subscription_id = self._require_payload_str(event.payload, "subscription_id")
            account_id = self._require_payload_str(event.payload, "account_id")
            dedupe_key = f"{event.tenant_id}:{event.event_name}:{event.event_id}"
            usage_records.append(
                UsageRecord(
                    usage_record_id=f"ur_{event.event_id}",
                    tenant_id=event.tenant_id,
                    subscription_id=subscription_id,
                    account_id=account_id,
                    meter_code=rule.meter_code,
                    quantity=quantity,
                    unit="event",
                    occurred_at=event.occurred_at,
                    source_event_id=event.event_id,
                    source_event_name=event.event_name,
                    dedupe_key=dedupe_key,
                )
            )
            self._processed_event_keys.add(event_identity)

        return usage_records

    def aggregate_usage(
        self,
        usage_records: list[UsageRecord],
        period_start: str,
        period_end: str,
    ) -> list[UsageAggregate]:
        """Aggregate usage by explicit keys for invoicing."""
        aggregates: dict[tuple[str, str, str, str, str, str, str], dict[str, object]] = {}

        for record in usage_records:
            key = (
                record.tenant_id,
                record.subscription_id,
                record.account_id,
                record.meter_code,
                record.unit,
                period_start,
                period_end,
            )
            row = aggregates.setdefault(
                key,
                {
                    "tenant_id": record.tenant_id,
                    "subscription_id": record.subscription_id,
                    "account_id": record.account_id,
                    "meter_code": record.meter_code,
                    "unit": record.unit,
                    "period_start": period_start,
                    "period_end": period_end,
                    "total_quantity": 0,
                    "source_usage_record_ids": [],
                },
            )
            row["total_quantity"] = int(row["total_quantity"]) + record.quantity
            row["source_usage_record_ids"].append(record.usage_record_id)

        return [
            UsageAggregate(
                tenant_id=str(row["tenant_id"]),
                subscription_id=str(row["subscription_id"]),
                account_id=str(row["account_id"]),
                meter_code=str(row["meter_code"]),
                unit=str(row["unit"]),
                period_start=str(row["period_start"]),
                period_end=str(row["period_end"]),
                total_quantity=int(row["total_quantity"]),
                source_usage_record_ids=tuple(sorted(set(row["source_usage_record_ids"]))),
            )
            for row in aggregates.values()
        ]

    def rate_usage(
        self,
        aggregates: list[UsageAggregate],
        rate_cards: list[MeterRateCard],
    ) -> list[RatedUsageLine]:
        """Apply flat or tiered rating logic to usage aggregates."""
        card_by_meter = {card.meter_code: card for card in rate_cards}
        rated_lines: list[RatedUsageLine] = []

        for aggregate in aggregates:
            card = card_by_meter.get(aggregate.meter_code)
            if card is None:
                raise UsageBillingError(f"Missing rate card for meter_code={aggregate.meter_code}")

            if card.billing_model == "flat":
                if card.unit_price is None:
                    raise UsageBillingError("flat billing model requires unit_price")
                subtotal = round(card.unit_price * aggregate.total_quantity, 4)
                breakdown = (
                    {
                        "billing_model": "flat",
                        "quantity": aggregate.total_quantity,
                        "unit_price": card.unit_price,
                        "subtotal": subtotal,
                    },
                )
            elif card.billing_model == "tiered":
                subtotal, breakdown = self._rate_tiered(aggregate.total_quantity, card.tiers)
            else:
                raise UsageBillingError(f"Unsupported billing model: {card.billing_model}")

            rated_lines.append(
                RatedUsageLine(
                    tenant_id=aggregate.tenant_id,
                    subscription_id=aggregate.subscription_id,
                    account_id=aggregate.account_id,
                    meter_code=aggregate.meter_code,
                    quantity=aggregate.total_quantity,
                    unit=aggregate.unit,
                    currency=card.currency,
                    subtotal=subtotal,
                    period_start=aggregate.period_start,
                    period_end=aggregate.period_end,
                    rate_breakdown=breakdown,
                )
            )

        return rated_lines

    def generate_invoice_inputs(self, rated_lines: list[RatedUsageLine]) -> list[InvoiceInput]:
        """Generate invoice usage input grouped by tenant/subscription/period/currency."""
        grouped: dict[tuple[str, str, str, str, str, str], list[RatedUsageLine]] = defaultdict(list)

        for line in rated_lines:
            key = (
                line.tenant_id,
                line.subscription_id,
                line.account_id,
                line.currency,
                line.period_start,
                line.period_end,
            )
            grouped[key].append(line)

        invoice_inputs: list[InvoiceInput] = []
        for key, lines in grouped.items():
            subtotal = round(sum(line.subtotal for line in lines), 4)
            tenant_id, subscription_id, account_id, currency, period_start, period_end = key
            invoice_inputs.append(
                InvoiceInput(
                    tenant_id=tenant_id,
                    subscription_id=subscription_id,
                    account_id=account_id,
                    currency=currency,
                    billing_period_start=period_start,
                    billing_period_end=period_end,
                    usage_subtotal=subtotal,
                    line_items=tuple(sorted(lines, key=lambda line: line.meter_code)),
                )
            )

        return invoice_inputs

    @staticmethod
    def processing_rules() -> dict[str, object]:
        """Deterministic processing rules for usage metering and rating."""
        return {
            "usage_source": "tracked_event_stream",
            "dedupe_identity": ["tenant_id", "event_name", "event_id"],
            "aggregation_dimensions": [
                "tenant_id",
                "subscription_id",
                "account_id",
                "meter_code",
                "unit",
                "period_start",
                "period_end",
            ],
            "required_event_payload_fields": ["subscription_id", "account_id"],
            "supported_billing_models": ["flat", "tiered"],
            "invoice_grouping": [
                "tenant_id",
                "subscription_id",
                "account_id",
                "currency",
                "billing_period_start",
                "billing_period_end",
            ],
        }

    @staticmethod
    def _rate_tiered(quantity: int, tiers: tuple[TierPrice, ...]) -> tuple[float, tuple[dict[str, object], ...]]:
        if not tiers:
            raise UsageBillingError("tiered billing model requires at least one tier")

        remaining = quantity
        previous_threshold = 0
        subtotal = 0.0
        breakdown: list[dict[str, object]] = []

        for tier in tiers:
            if remaining <= 0:
                break

            tier_limit = tier.up_to if tier.up_to is not None else quantity
            tier_capacity = tier_limit - previous_threshold if tier.up_to is not None else remaining
            billable_qty = min(remaining, tier_capacity)
            tier_subtotal = round(billable_qty * tier.unit_price, 4)
            subtotal += tier_subtotal
            breakdown.append(
                {
                    "up_to": tier.up_to,
                    "quantity": billable_qty,
                    "unit_price": tier.unit_price,
                    "subtotal": tier_subtotal,
                }
            )
            remaining -= billable_qty
            if tier.up_to is not None:
                previous_threshold = tier.up_to

        if remaining > 0:
            raise UsageBillingError("tier configuration did not cover full quantity")

        return round(subtotal, 4), tuple(breakdown)

    @staticmethod
    def _extract_quantity(event: TrackedEvent, rule: BillableEventRule) -> int:
        if rule.quantity_field is None:
            return rule.default_quantity
        raw_value = event.payload.get(rule.quantity_field)
        if raw_value is None:
            return rule.default_quantity
        if not isinstance(raw_value, int):
            raise UsageBillingError(
                f"Event {event.event_id} field {rule.quantity_field} must be int for quantity extraction"
            )
        return raw_value

    @staticmethod
    def _require_payload_str(payload: dict[str, object], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value:
            raise UsageBillingError(f"Missing required payload field: {key}")
        return value


def to_dicts(invoice_inputs: list[InvoiceInput]) -> list[dict[str, object]]:
    """Serialize invoice inputs to plain dictionaries."""
    return [asdict(item) for item in invoice_inputs]


def period_bounds_from_month(month: str) -> tuple[str, str]:
    """Return RFC3339 timestamps for start/end of a UTC month, month=YYYY-MM."""
    dt = datetime.strptime(month, "%Y-%m")
    year, month_num = dt.year, dt.month
    if month_num == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month_num + 1
    start = f"{year:04d}-{month_num:02d}-01T00:00:00Z"
    end = f"{next_year:04d}-{next_month:02d}-01T00:00:00Z"
    return start, end
