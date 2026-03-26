"""Rules-based scoring entities for Lead and Opportunity scoring."""

from __future__ import annotations

from dataclasses import dataclass


SCORING_MODEL_FIELDS: tuple[str, ...] = (
    "model_id",
    "tenant_id",
    "entity_type",
    "version",
    "status",
    "created_at",
)


@dataclass(frozen=True)
class ScoringFactor:
    """Weighted scoring factor used in a rules-based model."""

    factor_key: str
    weight: float
    value: float
    evidence: dict[str, object]


@dataclass(frozen=True)
class LeadScoringInput:
    """Lead attributes mapped from the domain model for score computation."""

    lead_id: str
    tenant_id: str
    source: str
    status: str
    email: str
    phone: str
    company_name: str
    activity_event_count_30d: int


@dataclass(frozen=True)
class OpportunityScoringInput:
    """Opportunity attributes mapped from the domain model for score computation."""

    opportunity_id: str
    tenant_id: str
    stage: str
    amount: float
    close_days_out: int
    quote_count: int
    activity_event_count_30d: int
    has_primary_contact: bool


@dataclass(frozen=True)
class ScoringResult:
    """Final score + raw factors used to compute it."""

    entity_id: str
    tenant_id: str
    entity_type: str
    score: int
    factors: tuple[ScoringFactor, ...]


class ScoringValidationError(ValueError):
    """Raised when scoring inputs are invalid or incomplete."""
