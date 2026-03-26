"""Deterministic predictive models for opportunity win probability and churn risk."""

from __future__ import annotations

from datetime import date

from .entities import (
    ChurnPrediction,
    OpportunityHistory,
    PredictionValidationError,
    SubscriptionHistory,
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
    """Simple scoring models built only from documented historical entity fields."""

    def __init__(self) -> None:
        self._opportunity_history: list[OpportunityHistory] = []
        self._subscription_history: list[SubscriptionHistory] = []

    def ingest_opportunity_history(self, rows: list[OpportunityHistory]) -> int:
        for row in rows:
            self._validate_opportunity_row(row)
        self._opportunity_history.extend(rows)
        return len(rows)

    def ingest_subscription_history(self, rows: list[SubscriptionHistory]) -> int:
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
        mrr: float,
        started_at: str,
        current_period_end: str,
        last_payment_at: str,
        late_payment_count: int,
        support_case_count_90d: int,
    ) -> ChurnPrediction:
        if status not in _ALLOWED_SUBSCRIPTION_STATUSES:
            raise PredictionValidationError(f"Unknown subscription status: {status}")
        if mrr < 0:
            raise PredictionValidationError("MRR cannot be negative.")
        if late_payment_count < 0 or support_case_count_90d < 0:
            raise PredictionValidationError("Historical count fields cannot be negative.")

        started = _parse_iso_date(started_at, "started_at")
        period_end = _parse_iso_date(current_period_end, "current_period_end")
        last_payment = _parse_iso_date(last_payment_at, "last_payment_at")
        if period_end < started:
            raise PredictionValidationError("current_period_end cannot be earlier than started_at.")
        if last_payment < started:
            raise PredictionValidationError("last_payment_at cannot be earlier than started_at.")

        tenant_rows = [r for r in self._subscription_history if r.tenant_id == tenant_id]
        churned = [r for r in tenant_rows if r.status == "canceled"]
        base_rate = (len(churned) / len(tenant_rows)) if tenant_rows else 0.2

        score = base_rate
        drivers: list[str] = [f"tenant_historical_churn_rate={base_rate:.2f}"]

        status_lift = {"trialing": 0.12, "active": -0.06, "past_due": 0.22, "canceled": 0.60}[status]
        score += status_lift
        drivers.append(f"status_adjustment={status_lift:+.2f}")

        if late_payment_count >= 3:
            score += 0.18
            drivers.append("late_payment_adjustment=+0.18(repeat_late_payment)")
        elif late_payment_count == 0:
            score -= 0.05
            drivers.append("late_payment_adjustment=-0.05(no_late_payment)")

        if support_case_count_90d >= 5:
            score += 0.10
            drivers.append("support_case_adjustment=+0.10(high_volume)")

        tenure_days = (period_end - started).days
        if tenure_days >= 365:
            score -= 0.08
            drivers.append("tenure_adjustment=-0.08(long_tenure)")

        if (period_end - last_payment).days > 35:
            score += 0.14
            drivers.append("payment_recency_adjustment=+0.14(stale_payment)")

        churn_probability = _clamp(score)
        return ChurnPrediction(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            churn_probability=churn_probability,
            risk_level=_risk_label(churn_probability),
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

    def _validate_subscription_row(self, row: SubscriptionHistory) -> None:
        if row.status not in _ALLOWED_SUBSCRIPTION_STATUSES:
            raise PredictionValidationError(f"Unknown historical subscription status: {row.status}")
        if row.mrr < 0:
            raise PredictionValidationError("Historical MRR cannot be negative.")
        if row.late_payment_count < 0 or row.support_case_count_90d < 0:
            raise PredictionValidationError("Historical count fields cannot be negative.")
        started = _parse_iso_date(row.started_at, "started_at")
        period_end = _parse_iso_date(row.current_period_end, "current_period_end")
        if period_end < started:
            raise PredictionValidationError("Historical current_period_end cannot be earlier than started_at.")


def _parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise PredictionValidationError(f"Invalid ISO date for {field_name}: {value}") from exc


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
