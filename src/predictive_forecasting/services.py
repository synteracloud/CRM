"""Forecasting engine for pipeline + revenue aggregation and deterministic prediction."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from .entities import (
    ALLOWED_FORECAST_CATEGORIES,
    ForecastBucket,
    ForecastResult,
    ForecastTotals,
    ForecastValidationError,
    OpportunityForecastRow,
    OpportunityPrediction,
)

_FORECAST_CATEGORY_WEIGHTS: dict[str, float] = {
    "pipeline": 0.25,
    "best_case": 0.50,
    "commit": 0.75,
    "closed": 1.0,
    "omitted": 0.0,
}


class ForecastEngineService:
    """Builds forecast outputs only from validated opportunity rows."""

    def build_forecast(self, *, tenant_id: str, as_of: str, opportunities: list[OpportunityForecastRow]) -> ForecastResult:
        _parse_iso_date(as_of, "as_of")
        rows = [row for row in opportunities if row.tenant_id == tenant_id]
        for row in rows:
            self._validate_row(row)

        open_rows = [row for row in rows if not row.is_closed]
        closed_rows = [row for row in rows if row.is_closed]
        won_rows = [row for row in closed_rows if row.is_won]

        global_win_rate = (len(won_rows) / len(closed_rows)) if closed_rows else None
        closed_by_stage: dict[str, list[OpportunityForecastRow]] = defaultdict(list)
        for row in closed_rows:
            closed_by_stage[row.stage].append(row)

        predictions = tuple(
            self._predict_one(row, closed_by_stage, global_win_rate)
            for row in sorted(open_rows, key=lambda r: r.opportunity_id)
        )

        total_pipeline = sum(row.amount for row in open_rows)
        weighted_pipeline = sum(row.amount * _FORECAST_CATEGORY_WEIGHTS[row.forecast_category] for row in open_rows)
        won_revenue = sum(row.amount for row in won_rows)
        predicted_revenue = sum(item.predicted_revenue for item in predictions)

        return ForecastResult(
            tenant_id=tenant_id,
            as_of=as_of,
            totals=ForecastTotals(
                opportunity_count=len(rows),
                open_count=len(open_rows),
                closed_count=len(closed_rows),
                won_count=len(won_rows),
                lost_count=len(closed_rows) - len(won_rows),
                total_pipeline_amount=round(total_pipeline, 2),
                weighted_pipeline_amount=round(weighted_pipeline, 2),
                won_revenue_amount=round(won_revenue, 2),
                predicted_revenue_amount=round(predicted_revenue, 2),
            ),
            by_stage=self._to_buckets(rows, lambda r: r.stage),
            by_forecast_category=self._to_buckets(rows, lambda r: r.forecast_category),
            by_close_month=self._to_buckets(rows, lambda r: r.close_date[:7]),
            predictions=predictions,
        )

    def _validate_row(self, row: OpportunityForecastRow) -> None:
        if not row.opportunity_id.strip():
            raise ForecastValidationError("opportunity_id must be a non-empty string")
        if not row.tenant_id.strip():
            raise ForecastValidationError("tenant_id must be a non-empty string")
        if not row.stage.strip():
            raise ForecastValidationError("stage must be a non-empty string")
        if row.forecast_category not in ALLOWED_FORECAST_CATEGORIES:
            raise ForecastValidationError(f"Unsupported forecast_category: {row.forecast_category}")
        if row.amount < 0:
            raise ForecastValidationError("amount must be a non-negative number")
        _parse_iso_date(row.close_date, "close_date")
        if row.is_won and not row.is_closed:
            raise ForecastValidationError("is_won=true requires is_closed=true")

    def _predict_one(
        self,
        row: OpportunityForecastRow,
        closed_by_stage: dict[str, list[OpportunityForecastRow]],
        global_win_rate: float | None,
    ) -> OpportunityPrediction:
        basis: list[str] = []
        candidate_probabilities: list[float] = []

        stage_history = closed_by_stage.get(row.stage, [])
        if stage_history:
            stage_wins = sum(1 for item in stage_history if item.is_won)
            stage_rate = stage_wins / len(stage_history)
            candidate_probabilities.append(stage_rate)
            basis.append(f"stage_win_rate={stage_rate:.4f}({len(stage_history)}_closed)")

        if global_win_rate is not None:
            candidate_probabilities.append(global_win_rate)
            basis.append(f"tenant_win_rate={global_win_rate:.4f}")

        category_weight = _FORECAST_CATEGORY_WEIGHTS.get(row.forecast_category)
        if category_weight is not None:
            candidate_probabilities.append(category_weight)
            basis.append(f"forecast_category_weight={category_weight:.4f}")

        if not candidate_probabilities:
            return OpportunityPrediction(
                opportunity_id=row.opportunity_id,
                tenant_id=row.tenant_id,
                probability=None,
                predicted_revenue=0.0,
                confidence="insufficient_data",
                basis=("no_valid_probability_inputs",),
            )

        probability = round(sum(candidate_probabilities) / len(candidate_probabilities), 4)
        predicted_revenue = round(row.amount * probability, 2)
        return OpportunityPrediction(
            opportunity_id=row.opportunity_id,
            tenant_id=row.tenant_id,
            probability=probability,
            predicted_revenue=predicted_revenue,
            confidence=_confidence_label(len(stage_history), global_win_rate is not None),
            basis=tuple(basis),
        )

    def _to_buckets(self, rows: list[OpportunityForecastRow], key_fn: callable) -> tuple[ForecastBucket, ...]:
        grouped: dict[str, dict[str, float]] = defaultdict(
            lambda: {
                "opportunity_count": 0,
                "total_amount": 0.0,
                "weighted_amount": 0.0,
                "won_amount": 0.0,
            }
        )

        for row in rows:
            key = str(key_fn(row))
            bucket = grouped[key]
            bucket["opportunity_count"] += 1
            bucket["total_amount"] += row.amount
            bucket["weighted_amount"] += row.amount * _FORECAST_CATEGORY_WEIGHTS[row.forecast_category]
            if row.is_closed and row.is_won:
                bucket["won_amount"] += row.amount

        return tuple(
            ForecastBucket(
                key=key,
                opportunity_count=int(value["opportunity_count"]),
                total_amount=round(value["total_amount"], 2),
                weighted_amount=round(value["weighted_amount"], 2),
                won_amount=round(value["won_amount"], 2),
            )
            for key, value in sorted(grouped.items())
        )


def _parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ForecastValidationError(f"Invalid ISO date for {field_name}: {value}") from exc


def _confidence_label(stage_sample_size: int, has_tenant_history: bool) -> str:
    if stage_sample_size >= 20:
        return "high"
    if stage_sample_size >= 5 or has_tenant_history:
        return "medium"
    return "low"
