"""Models for smart follow-up assistant outputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FollowupSuggestion:
    lead_id: str
    next_followup_at: datetime
    template_key: str
    template_message: str
    confidence_percent: float
    reason: str


@dataclass(frozen=True)
class SuggestionQuality:
    evaluated: int
    accurate: int
    accuracy_percent: float


@dataclass(frozen=True)
class AssistantAlignmentReport:
    no_idle_leads_percent: float
    suggestion_accuracy_percent: float
    overall_alignment_percent: float
