"""Data deduplication engine exports."""

from .entities import (
    DeduplicationError,
    DuplicateCandidate,
    DuplicatePreventedError,
    ManualReviewTask,
    MatchEvidence,
    MergeWorkflow,
    ReviewDecisionError,
    RuleDefinition,
    UpsertDecision,
)
from .services import DataDeduplicationEngine

__all__ = [
    "DataDeduplicationEngine",
    "DeduplicationError",
    "DuplicateCandidate",
    "DuplicatePreventedError",
    "ManualReviewTask",
    "MatchEvidence",
    "MergeWorkflow",
    "ReviewDecisionError",
    "RuleDefinition",
    "UpsertDecision",
]
