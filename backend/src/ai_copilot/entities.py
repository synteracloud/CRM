"""Entities for deterministic CRM AI copilot suggestions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


COPILOT_CONTEXT_FIELDS: tuple[str, ...] = (
    "tenant_id",
    "user_id",
    "workflow_name",
    "primary_entity_type",
    "primary_entity_id",
)


@dataclass(frozen=True)
class CopilotContext:
    """Request context scoped to tenant/user and a primary workflow entity."""

    tenant_id: str
    user_id: str
    workflow_name: str
    primary_entity_type: str
    primary_entity_id: str
    observed_data: dict[str, Any]


@dataclass(frozen=True)
class CopilotSuggestion:
    """Actionable suggestion constrained to explicit evidence from observed data."""

    suggestion_id: str
    tenant_id: str
    action_type: str
    title: str
    rationale: str
    evidence: dict[str, Any]
    confidence: float


@dataclass(frozen=True)
class CopilotSuggestionResult:
    """Deterministic response payload for the copilot API."""

    tenant_id: str
    user_id: str
    workflow_name: str
    primary_entity_type: str
    primary_entity_id: str
    suggestions: tuple[CopilotSuggestion, ...]


class CopilotValidationError(ValueError):
    """Raised when copilot context or inputs are invalid."""
