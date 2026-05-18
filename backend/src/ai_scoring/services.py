"""Rules-based lead/opportunity scoring service based on real entity data only."""

from __future__ import annotations

from .entities import LeadScoringInput, OpportunityScoringInput, ScoringFactor, ScoringResult, ScoringValidationError


class ScoringService:
    """Computes deterministic weighted scores from observed CRM fields."""

    _LEAD_SOURCE_SCORES: dict[str, float] = {
        "referral": 1.0,
        "web_form": 0.8,
        "event": 0.7,
        "partner": 0.7,
        "outbound": 0.5,
        "unknown": 0.3,
    }

    _OPPORTUNITY_STAGE_SCORES: dict[str, float] = {
        "prospecting": 0.25,
        "qualification": 0.45,
        "proposal": 0.7,
        "negotiation": 0.85,
        "closed_won": 1.0,
        "closed_lost": 0.0,
    }

    def score_lead(self, scoring_input: LeadScoringInput) -> ScoringResult:
        if scoring_input.activity_event_count_30d < 0:
            raise ScoringValidationError("activity_event_count_30d must be >= 0")
        if not scoring_input.email and not scoring_input.phone:
            raise ScoringValidationError("At least one contact field (email or phone) is required for scoring.")

        factors: tuple[ScoringFactor, ...] = (
            self._factor("source_quality", 0.30, self._lead_source_value(scoring_input.source), {"source": scoring_input.source}),
            self._factor(
                "contact_completeness",
                0.30,
                self._contact_completeness_value(scoring_input.email, scoring_input.phone),
                {"has_email": bool(scoring_input.email), "has_phone": bool(scoring_input.phone)},
            ),
            self._factor(
                "company_presence",
                0.15,
                1.0 if bool(scoring_input.company_name.strip()) else 0.0,
                {"has_company_name": bool(scoring_input.company_name.strip())},
            ),
            self._factor(
                "recent_activity",
                0.25,
                min(scoring_input.activity_event_count_30d / 8.0, 1.0),
                {"activity_event_count_30d": scoring_input.activity_event_count_30d},
            ),
        )
        return ScoringResult(
            entity_id=scoring_input.lead_id,
            tenant_id=scoring_input.tenant_id,
            entity_type="lead",
            score=self._final_score(factors),
            factors=factors,
        )

    def score_opportunity(self, scoring_input: OpportunityScoringInput) -> ScoringResult:
        if scoring_input.amount <= 0:
            raise ScoringValidationError("amount must be > 0")
        if scoring_input.close_days_out < 0:
            raise ScoringValidationError("close_days_out must be >= 0")

        factors: tuple[ScoringFactor, ...] = (
            self._factor("stage_progression", 0.35, self._opportunity_stage_value(scoring_input.stage), {"stage": scoring_input.stage}),
            self._factor(
                "close_date_proximity",
                0.25,
                self._close_date_value(scoring_input.close_days_out),
                {"close_days_out": scoring_input.close_days_out},
            ),
            self._factor(
                "quote_coverage",
                0.20,
                min(scoring_input.quote_count / 2.0, 1.0),
                {"quote_count": scoring_input.quote_count},
            ),
            self._factor(
                "buyer_engagement",
                0.20,
                self._engagement_value(scoring_input.activity_event_count_30d, scoring_input.has_primary_contact),
                {
                    "activity_event_count_30d": scoring_input.activity_event_count_30d,
                    "has_primary_contact": scoring_input.has_primary_contact,
                },
            ),
        )
        return ScoringResult(
            entity_id=scoring_input.opportunity_id,
            tenant_id=scoring_input.tenant_id,
            entity_type="opportunity",
            score=self._final_score(factors),
            factors=factors,
        )

    def _lead_source_value(self, source: str) -> float:
        return self._LEAD_SOURCE_SCORES.get(source, self._LEAD_SOURCE_SCORES["unknown"])

    def _opportunity_stage_value(self, stage: str) -> float:
        if stage not in self._OPPORTUNITY_STAGE_SCORES:
            raise ScoringValidationError(f"Unsupported opportunity stage for scoring: {stage}")
        return self._OPPORTUNITY_STAGE_SCORES[stage]

    def _close_date_value(self, close_days_out: int) -> float:
        if close_days_out <= 30:
            return 1.0
        if close_days_out <= 60:
            return 0.7
        if close_days_out <= 90:
            return 0.4
        return 0.2

    def _contact_completeness_value(self, email: str, phone: str) -> float:
        if email and phone:
            return 1.0
        return 0.5

    def _engagement_value(self, activity_events_30d: int, has_primary_contact: bool) -> float:
        if activity_events_30d < 0:
            raise ScoringValidationError("activity_event_count_30d must be >= 0")
        activity_value = min(activity_events_30d / 10.0, 1.0)
        contact_bonus = 0.2 if has_primary_contact else 0.0
        return min(activity_value + contact_bonus, 1.0)

    def _factor(self, factor_key: str, weight: float, value: float, evidence: dict[str, object]) -> ScoringFactor:
        return ScoringFactor(factor_key=factor_key, weight=weight, value=value, evidence=evidence)

    def _final_score(self, factors: tuple[ScoringFactor, ...]) -> int:
        total_weight = sum(factor.weight for factor in factors)
        if total_weight <= 0:
            raise ScoringValidationError("Score factors must have positive total weight")
        weighted_value = sum(factor.weight * factor.value for factor in factors) / total_weight
        return round(weighted_value * 100)
