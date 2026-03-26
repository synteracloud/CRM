"""Deterministic predictive models for opportunity win probability, churn risk, and CLV."""

from __future__ import annotations

from datetime import date

from .entities import (
    ChurnPrediction,
    CustomerLifetimeValuePrediction,
    OpportunityHistory,
    PredictionValidationError,
    SubscriptionValueHistory,
    WinProbabilityPrediction,
)

_ALLOWED_OPPORTUNITY_STAGES = {
    "prospecting",
    "qualification",
    "proposal",
    "negotiation",
    "closed_won",
    "closed_lost",
}

_ALLOWED_FORECAST_CATEGORIES = {"pipeline", "best_case", "commit", "closed"}
_ALLOWED_SUBSCRIPTION_STATUSES = {"trialing", "active", "past_due", "canceled"}


class PredictiveModelService:
    """Scoring models built only from documented domain entities and derived aggregates."""

    def __init__(self) -> None:
        self._opportunity_history: list[OpportunityHistory] = []
        self._subscription_history: list[SubscriptionValueHistory] = []

    def ingest_opportunity_history(self, rows: list[OpportunityHistory]) -> int:
        for row in rows:
            self._validate_opportunity_row(row)
        self._opportunity_history.extend(rows)
        return len(rows)

    def ingest_subscription_history(self, rows: list[SubscriptionValueHistory]) -> int:
        for row in rows:
            self._validate_subscription_row(row)
        self._subscription_history.extend(rows)
        return len(rows)

    def predict_win_probability(
        self,
        tenant_id: str,
        opportunity_id: str,
        stage: str,
        amount: float,
        forecast_category: str,
        created_at: str,
        close_date: str,
    ) -> WinProbabilityPrediction:
        if stage not in _ALLOWED_OPPORTUNITY_STAGES:
            raise PredictionValidationError(f"Unknown opportunity stage: {stage}")
        if forecast_category not in _ALLOWED_FORECAST_CATEGORIES:
            raise PredictionValidationError(f"Unknown forecast category: {forecast_category}")
        if amount <= 0:
            raise PredictionValidationError("Opportunity amount must be positive.")

        created = _parse_iso_date(created_at, "created_at")
        close = _parse_iso_date(close_date, "close_date")
        if close < created:
            raise PredictionValidationError("close_date cannot be earlier than created_at.")

        won = [r for r in self._opportunity_history if r.tenant_id == tenant_id and r.is_closed and r.is_won]
        closed = [r for r in self._opportunity_history if r.tenant_id == tenant_id and r.is_closed]
        base_rate = (len(won) / len(closed)) if closed else 0.5

        score = base_rate
        drivers: list[str] = [f"tenant_historical_win_rate={base_rate:.2f}"]

        stage_lift = {
            "prospecting": -0.20,
            "qualification": -0.10,
            "proposal": 0.05,
            "negotiation": 0.15,
            "closed_won": 0.45,
            "closed_lost": -0.45,
        }[stage]
        score += stage_lift
        drivers.append(f"stage_adjustment={stage_lift:+.2f}")

        forecast_lift = {"pipeline": -0.05, "best_case": 0.05, "commit": 0.15, "closed": 0.30}[forecast_category]
        score += forecast_lift
        drivers.append(f"forecast_adjustment={forecast_lift:+.2f}")

        if amount >= 100000:
            score -= 0.08
            drivers.append("amount_adjustment=-0.08(high_deal_size)")
        elif amount <= 10000:
            score += 0.04
            drivers.append("amount_adjustment=+0.04(low_deal_size)")

        sales_cycle_days = (close - created).days
        if sales_cycle_days > 180:
            score -= 0.06
            drivers.append("sales_cycle_adjustment=-0.06(long_cycle)")

        probability = _clamp(score)
        return WinProbabilityPrediction(
            opportunity_id=opportunity_id,
            tenant_id=tenant_id,
            probability=probability,
            confidence=_confidence_label(len(closed)),
            drivers=tuple(drivers),
        )

    def predict_churn(
        self,
        tenant_id: str,
        subscription_id: str,
        status: str,
        start_date: str,
        end_date: str | None,
        renewal_date: str | None,
        invoice_amount_due_12m: float,
        invoice_amount_paid_12m: float,
        invoice_overdue_count_12m: int,
        payment_failed_count_90d: int,
        payment_success_count_90d: int,
    ) -> ChurnPrediction:
        row = SubscriptionValueHistory(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            renewal_date=renewal_date,
            invoice_amount_due_12m=invoice_amount_due_12m,
            invoice_amount_paid_12m=invoice_amount_paid_12m,
            invoice_overdue_count_12m=invoice_overdue_count_12m,
            payment_failed_count_90d=payment_failed_count_90d,
            payment_success_count_90d=payment_success_count_90d,
        )
        self._validate_subscription_row(row)

        tenant_rows = [r for r in self._subscription_history if r.tenant_id == tenant_id]
        churned = [r for r in tenant_rows if r.status == "canceled"]
        base_rate = (len(churned) / len(tenant_rows)) if tenant_rows else 0.2

        score = base_rate
        drivers: list[str] = [f"tenant_historical_churn_rate={base_rate:.2f}"]

        status_lift = {"trialing": 0.12, "active": -0.06, "past_due": 0.22, "canceled": 0.60}[status]
        score += status_lift
        drivers.append(f"status_adjustment={status_lift:+.2f}")

        if invoice_amount_due_12m > 0:
            collection_ratio = invoice_amount_paid_12m / invoice_amount_due_12m
            if collection_ratio < 0.7:
                score += 0.16
                drivers.append("collection_ratio_adjustment=+0.16(low_collection_ratio)")
            elif collection_ratio >= 0.98:
                score -= 0.06
                drivers.append("collection_ratio_adjustment=-0.06(strong_collection_ratio)")

        if invoice_overdue_count_12m >= 3:
            score += 0.14
            drivers.append("overdue_invoice_adjustment=+0.14(repeat_overdue)")

        if payment_failed_count_90d >= 2:
            score += 0.18
            drivers.append("failed_payment_adjustment=+0.18(recent_failures)")
        elif payment_success_count_90d >= 3:
            score -= 0.05
            drivers.append("payment_success_adjustment=-0.05(recent_successes)")

        tenure_days = _tenure_days(start_date=start_date, end_date=end_date, renewal_date=renewal_date)
        if tenure_days >= 365:
            score -= 0.08
            drivers.append("tenure_adjustment=-0.08(long_tenure)")

        churn_probability = _clamp(score)
        return ChurnPrediction(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            churn_probability=churn_probability,
            risk_level=_risk_label(churn_probability),
            drivers=tuple(drivers),
        )

    def predict_customer_lifetime_value(
        self,
        tenant_id: str,
        subscription_id: str,
        status: str,
        start_date: str,
        end_date: str | None,
        renewal_date: str | None,
        invoice_amount_due_12m: float,
        invoice_amount_paid_12m: float,
        invoice_overdue_count_12m: int,
        payment_failed_count_90d: int,
        payment_success_count_90d: int,
    ) -> CustomerLifetimeValuePrediction:
        churn = self.predict_churn(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            renewal_date=renewal_date,
            invoice_amount_due_12m=invoice_amount_due_12m,
            invoice_amount_paid_12m=invoice_amount_paid_12m,
            invoice_overdue_count_12m=invoice_overdue_count_12m,
            payment_failed_count_90d=payment_failed_count_90d,
            payment_success_count_90d=payment_success_count_90d,
        )

        annualized_value = max(invoice_amount_paid_12m, 0.0)
        expected_retention_years = 1.0 + (1.0 - churn.churn_probability) * 2.0
        clv = round(annualized_value * expected_retention_years, 2)
        drivers = list(churn.drivers)
        drivers.append(f"annualized_paid_value_12m={annualized_value:.2f}")
        drivers.append(f"expected_retention_years={expected_retention_years:.2f}")

        tenant_rows = [r for r in self._subscription_history if r.tenant_id == tenant_id]
        return CustomerLifetimeValuePrediction(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            estimated_clv=clv,
            confidence=_confidence_label(len(tenant_rows)),
            drivers=tuple(drivers),
        )

    def _validate_opportunity_row(self, row: OpportunityHistory) -> None:
        if row.stage not in _ALLOWED_OPPORTUNITY_STAGES:
            raise PredictionValidationError(f"Unknown historical stage: {row.stage}")
        if row.forecast_category not in _ALLOWED_FORECAST_CATEGORIES:
            raise PredictionValidationError(f"Unknown historical forecast_category: {row.forecast_category}")
        if row.amount <= 0:
            raise PredictionValidationError("Historical opportunity amount must be positive.")
        created = _parse_iso_date(row.created_at, "created_at")
        close = _parse_iso_date(row.close_date, "close_date")
        if close < created:
            raise PredictionValidationError("Historical close_date cannot be earlier than created_at.")

    def _validate_subscription_row(self, row: SubscriptionValueHistory) -> None:
        if row.status not in _ALLOWED_SUBSCRIPTION_STATUSES:
            raise PredictionValidationError(f"Unknown historical subscription status: {row.status}")
        start = _parse_iso_date(row.start_date, "start_date")
        end = _parse_optional_iso_date(row.end_date, "end_date")
        renewal = _parse_optional_iso_date(row.renewal_date, "renewal_date")

        if end and end < start:
            raise PredictionValidationError("Historical end_date cannot be earlier than start_date.")
        if renewal and renewal < start:
            raise PredictionValidationError("Historical renewal_date cannot be earlier than start_date.")
        if row.invoice_amount_due_12m < 0 or row.invoice_amount_paid_12m < 0:
            raise PredictionValidationError("Invoice amount fields cannot be negative.")
        if row.invoice_amount_paid_12m > row.invoice_amount_due_12m:
            raise PredictionValidationError("invoice_amount_paid_12m cannot exceed invoice_amount_due_12m.")
        if row.invoice_overdue_count_12m < 0 or row.payment_failed_count_90d < 0 or row.payment_success_count_90d < 0:
            raise PredictionValidationError("Count fields cannot be negative.")


def _parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise PredictionValidationError(f"Invalid ISO date for {field_name}: {value}") from exc


def _parse_optional_iso_date(value: str | None, field_name: str) -> date | None:
    if value is None:
        return None
    return _parse_iso_date(value, field_name)


def _tenure_days(start_date: str, end_date: str | None, renewal_date: str | None) -> int:
    start = _parse_iso_date(start_date, "start_date")
    end = _parse_optional_iso_date(end_date, "end_date")
    renewal = _parse_optional_iso_date(renewal_date, "renewal_date")
    anchor = end or renewal or date.today()
    return max((anchor - start).days, 0)


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def _confidence_label(sample_size: int) -> str:
    if sample_size >= 200:
        return "high"
    if sample_size >= 50:
        return "medium"
    return "low"


def _risk_label(probability: float) -> str:
    if probability >= 0.7:
        return "high"
    if probability >= 0.4:
        return "medium"
    return "low"
