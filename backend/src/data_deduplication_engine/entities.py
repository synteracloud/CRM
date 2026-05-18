"""Entities for tenant-scoped lead/contact/account deduplication."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

EntityType = Literal["lead", "contact", "account"]
DecisionType = Literal["no_match", "prevented", "manual_review", "merged"]


@dataclass(frozen=True)
class RuleDefinition:
    rule_code: str
    entity_type: EntityType
    description: str
    weight: float
    auto_merge_safe: bool = False


@dataclass(frozen=True)
class MatchEvidence:
    rule_code: str
    field_name: str
    left_value: str
    right_value: str
    score: float


@dataclass(frozen=True)
class DuplicateCandidate:
    entity_type: EntityType
    tenant_id: str
    incoming_id: str
    existing_id: str
    score: float
    evidence: tuple[MatchEvidence, ...] = ()
    risky_conflict: bool = False


@dataclass(frozen=True)
class ManualReviewTask:
    review_id: str
    entity_type: EntityType
    tenant_id: str
    incoming_id: str
    existing_id: str
    score: float
    reason: str
    evidence: tuple[MatchEvidence, ...] = ()


@dataclass(frozen=True)
class MergeWorkflow:
    merge_id: str
    entity_type: EntityType
    tenant_id: str
    survivor_id: str
    merged_id: str
    executed_by: str
    decision_reason: str
    evidence: tuple[MatchEvidence, ...] = ()
    before_survivor: dict[str, Any] = field(default_factory=dict)
    before_merged: dict[str, Any] = field(default_factory=dict)
    after_survivor: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UpsertDecision:
    decision: DecisionType
    entity_type: EntityType
    tenant_id: str
    record_id: str
    duplicate_of: str | None = None
    merge_id: str | None = None
    review_id: str | None = None
    reason: str = ""


class DeduplicationError(ValueError):
    """Base deduplication exception."""


class DuplicatePreventedError(DeduplicationError):
    """Raised when create/update is blocked due to likely duplicate."""


class ReviewDecisionError(DeduplicationError):
    """Raised when manual review input is invalid or missing."""
