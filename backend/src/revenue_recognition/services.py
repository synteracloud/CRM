"""Revenue recognition engine with deterministic schedules and billing-traceable earned/deferred logic."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from .entities import (
    ALLOWED_BILLING_EVENT_TYPES,
    ALLOWED_REVENUE_TYPES,
    BillingEvent,
    RecognitionReportInput,
    RecognitionRule,
    RevenuePosition,
    RevenueRecognitionValidationError,
    RevenueSchedule,
    RevenueScheduleLine,
)

CENT = Decimal("0.01")


class RevenueRecognitionService:
    def build_schedules(
        self,
        *,
        tenant_id: str,
        rules: list[RecognitionRule],
        billing_events: list[BillingEvent],
    ) -> tuple[RevenueSchedule, ...]:
        scoped_rules = [rule for rule in rules if rule.tenant_id == tenant_id]
        scoped_events = [event for event in billing_events if event.tenant_id == tenant_id]

        for rule in scoped_rules:
            self._validate_rule(rule)
        for event in scoped_events:
            self._validate_event(event)

        events_by_contract = defaultdict(list)
        for event in scoped_events:
            events_by_contract[event.contract_id].append(event)

        schedules: list[RevenueSchedule] = []
        for contract_id in sorted({r.contract_id for r in scoped_rules}):
            contract_rules = sorted(
                [rule for rule in scoped_rules if rule.contract_id == contract_id],
                key=lambda r: (r.service_period_start, r.rule_id),
            )
            if not contract_rules:
                continue
            currency = contract_rules[0].currency
            if any(rule.currency != currency for rule in contract_rules):
                raise RevenueRecognitionValidationError("All recognition rules per contract must share one currency")

            trace_ids = tuple(sorted({event.event_id for event in events_by_contract.get(contract_id, [])}))
            lines: list[RevenueScheduleLine] = []
            line_index = 0
            for rule in contract_rules:
                for recognition_date, amount in self._expand_rule(rule):
                    line_index += 1
                    lines.append(
                        RevenueScheduleLine(
                            line_id=f"{rule.rule_id}-L{line_index:04d}",
                            tenant_id=tenant_id,
                            contract_id=contract_id,
                            rule_id=rule.rule_id,
                            recognition_date=recognition_date,
                            amount=float(amount),
                            currency=rule.currency,
                            revenue_type=rule.revenue_type,
                            trace_event_ids=trace_ids,
                        )
                    )

            lines_sorted = tuple(sorted(lines, key=lambda l: (l.recognition_date, l.rule_id, l.line_id)))
            total = self._sum_decimal([Decimal(str(line.amount)) for line in lines_sorted])
            schedules.append(
                RevenueSchedule(
                    tenant_id=tenant_id,
                    contract_id=contract_id,
                    currency=currency,
                    lines=lines_sorted,
                    total_scheduled_amount=float(total),
                )
            )

        return tuple(schedules)

    def build_positions(
        self,
        *,
        tenant_id: str,
        as_of: str,
        schedules: list[RevenueSchedule],
        billing_events: list[BillingEvent],
    ) -> tuple[RevenuePosition, ...]:
        as_of_date = _parse_iso_date(as_of, "as_of")
        scoped_events = [event for event in billing_events if event.tenant_id == tenant_id]
        for event in scoped_events:
            self._validate_event(event)

        event_by_contract = defaultdict(list)
        for event in scoped_events:
            event_by_contract[event.contract_id].append(event)

        positions: list[RevenuePosition] = []
        for schedule in sorted(schedules, key=lambda s: s.contract_id):
            if schedule.tenant_id != tenant_id:
                continue

            contract_events = event_by_contract.get(schedule.contract_id, [])
            billed = self._sum_decimal(
                [Decimal(str(e.amount)) for e in contract_events if e.event_type == "invoice_posted" and _parse_iso_date(e.occurred_at, "occurred_at") <= as_of_date]
            )
            collected = self._sum_decimal(
                [
                    Decimal(str(e.amount))
                    if e.event_type == "payment_settled"
                    else -Decimal(str(e.amount))
                    for e in contract_events
                    if e.event_type in {"payment_settled", "payment_refunded", "chargeback"}
                    and _parse_iso_date(e.occurred_at, "occurred_at") <= as_of_date
                ]
            )
            scheduled_through = self._sum_decimal(
                [
                    Decimal(str(line.amount))
                    for line in schedule.lines
                    if _parse_iso_date(line.recognition_date, "recognition_date") <= as_of_date
                ]
            )

            earned = min(scheduled_through, max(collected, Decimal("0.00")))
            deferred = max(collected - earned, Decimal("0.00"))

            if earned > billed + Decimal("0.01"):
                raise RevenueRecognitionValidationError(
                    f"Earned revenue exceeds billed revenue for contract {schedule.contract_id} as_of={as_of}"
                )

            positions.append(
                RevenuePosition(
                    tenant_id=tenant_id,
                    contract_id=schedule.contract_id,
                    currency=schedule.currency,
                    as_of=as_of,
                    billed_amount=float(billed),
                    collected_amount=float(collected),
                    earned_amount=float(earned),
                    deferred_amount=float(deferred),
                    scheduled_through_as_of=float(scheduled_through),
                )
            )

        return tuple(positions)

    def build_reporting_inputs(
        self,
        *,
        tenant_id: str,
        as_of: str,
        schedules: list[RevenueSchedule],
        billing_events: list[BillingEvent],
    ) -> tuple[RecognitionReportInput, ...]:
        positions = self.build_positions(
            tenant_id=tenant_id,
            as_of=as_of,
            schedules=schedules,
            billing_events=billing_events,
        )
        as_of_date = _parse_iso_date(as_of, "as_of")

        event_by_contract = defaultdict(list)
        for event in billing_events:
            if event.tenant_id == tenant_id:
                event_by_contract[event.contract_id].append(event)

        reports: list[RecognitionReportInput] = []
        for schedule in sorted(schedules, key=lambda s: s.contract_id):
            if schedule.tenant_id != tenant_id:
                continue
            position = next(p for p in positions if p.contract_id == schedule.contract_id)

            earned_daily_map: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
            for line in schedule.lines:
                recognition_day = _parse_iso_date(line.recognition_date, "recognition_date")
                if recognition_day <= as_of_date:
                    earned_daily_map[line.recognition_date] += Decimal(str(line.amount))

            billed_daily_map: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
            collected_daily_map: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
            for event in event_by_contract.get(schedule.contract_id, []):
                if _parse_iso_date(event.occurred_at, "occurred_at") > as_of_date:
                    continue
                if event.event_type == "invoice_posted":
                    billed_daily_map[event.occurred_at] += Decimal(str(event.amount))
                elif event.event_type == "payment_settled":
                    collected_daily_map[event.occurred_at] += Decimal(str(event.amount))
                elif event.event_type in {"payment_refunded", "chargeback"}:
                    collected_daily_map[event.occurred_at] -= Decimal(str(event.amount))

            reports.append(
                RecognitionReportInput(
                    tenant_id=tenant_id,
                    contract_id=schedule.contract_id,
                    currency=schedule.currency,
                    as_of=as_of,
                    daily_earned=tuple((d, float(v)) for d, v in sorted(earned_daily_map.items())),
                    daily_billed=tuple((d, float(v)) for d, v in sorted(billed_daily_map.items())),
                    daily_collected=tuple((d, float(v)) for d, v in sorted(collected_daily_map.items())),
                    cumulative_earned=position.earned_amount,
                    deferred_ending_balance=position.deferred_amount,
                )
            )
        return tuple(reports)

    def _expand_rule(self, rule: RecognitionRule) -> list[tuple[str, Decimal]]:
        amount = _to_money(rule.amount)
        if rule.revenue_type == "one_time":
            recognition_date = rule.recognized_at or rule.service_period_start
            _parse_iso_date(recognition_date, "recognized_at")
            return [(recognition_date, amount)]

        start = _parse_iso_date(rule.service_period_start, "service_period_start")
        end = _parse_iso_date(rule.service_period_end, "service_period_end")
        if end < start:
            raise RevenueRecognitionValidationError("service_period_end must be >= service_period_start")

        days = (end - start).days + 1
        allocations = _allocate_evenly(amount, days)
        return [((start + timedelta(days=i)).isoformat(), allocations[i]) for i in range(days)]

    def _validate_rule(self, rule: RecognitionRule) -> None:
        if not rule.rule_id.strip() or not rule.tenant_id.strip() or not rule.contract_id.strip():
            raise RevenueRecognitionValidationError("rule_id, tenant_id, and contract_id must be non-empty")
        if rule.revenue_type not in ALLOWED_REVENUE_TYPES:
            raise RevenueRecognitionValidationError(f"Unsupported revenue_type: {rule.revenue_type}")
        if rule.amount < 0:
            raise RevenueRecognitionValidationError("Rule amount must be non-negative")
        if not rule.currency.isalpha() or len(rule.currency) != 3:
            raise RevenueRecognitionValidationError("currency must be 3-letter ISO code")
        _parse_iso_date(rule.service_period_start, "service_period_start")
        _parse_iso_date(rule.service_period_end, "service_period_end")

    def _validate_event(self, event: BillingEvent) -> None:
        if not event.event_id.strip() or not event.tenant_id.strip() or not event.contract_id.strip():
            raise RevenueRecognitionValidationError("event_id, tenant_id, and contract_id must be non-empty")
        if event.event_type not in ALLOWED_BILLING_EVENT_TYPES:
            raise RevenueRecognitionValidationError(f"Unsupported billing event type: {event.event_type}")
        if event.amount < 0:
            raise RevenueRecognitionValidationError("Billing event amount must be non-negative")
        if not event.currency.isalpha() or len(event.currency) != 3:
            raise RevenueRecognitionValidationError("currency must be 3-letter ISO code")
        _parse_iso_date(event.occurred_at, "occurred_at")

    def _sum_decimal(self, values: list[Decimal]) -> Decimal:
        total = Decimal("0.00")
        for value in values:
            total += value
        return total.quantize(CENT, rounding=ROUND_HALF_UP)


def _allocate_evenly(total: Decimal, buckets: int) -> list[Decimal]:
    if buckets <= 0:
        raise RevenueRecognitionValidationError("buckets must be > 0")
    total_cents = int((total / CENT).to_integral_value(rounding=ROUND_HALF_UP))
    base_cents, remainder = divmod(total_cents, buckets)
    allocations = [Decimal(base_cents) * CENT for _ in range(buckets)]
    for idx in range(remainder):
        allocations[idx] += CENT
    return allocations


def _to_money(value: float) -> Decimal:
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def _parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RevenueRecognitionValidationError(f"Invalid ISO date for {field_name}: {value}") from exc
