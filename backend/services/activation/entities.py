"""Activation Engine domain entities and state enums."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum


class ActivationState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    BASELINE_READY = "BASELINE_READY"
    WHATSAPP_READY = "WHATSAPP_READY"
    SAMPLE_DATA_READY = "SAMPLE_DATA_READY"
    FIRST_ACTION_DONE = "FIRST_ACTION_DONE"
    AHA_REACHED = "AHA_REACHED"
    RETENTION_HOOK_TRIGGERED = "RETENTION_HOOK_TRIGGERED"


@dataclass(frozen=True)
class Pipeline:
    pipeline_id: str
    tenant_id: str
    name: str
    stages: tuple[str, ...]


@dataclass(frozen=True)
class Contact:
    contact_id: str
    tenant_id: str
    full_name: str
    segment: str
    is_sample: bool = True


@dataclass(frozen=True)
class Deal:
    deal_id: str
    tenant_id: str
    contact_id: str
    title: str
    stage: str
    is_sample: bool = True


@dataclass(frozen=True)
class OnboardingPrompt:
    key: str
    label: str
    optional: bool = True


@dataclass(frozen=True)
class OnboardingChecklistStep:
    key: str
    label: str
    auto_complete: bool
    completed: bool = False

    def patch(self, **changes: object) -> "OnboardingChecklistStep":
        return replace(self, **changes)


@dataclass(frozen=True)
class ActivationSession:
    tenant_id: str
    session_id: str
    started_at: datetime
    state: ActivationState = ActivationState.NOT_STARTED
    pipeline_ready_at: datetime | None = None
    whatsapp_ready_at: datetime | None = None
    first_inbound_at: datetime | None = None
    first_stage_move_at: datetime | None = None
    aha_at: datetime | None = None
    inbox_channel: str | None = None
    checklist: tuple[OnboardingChecklistStep, ...] = field(default_factory=tuple)

    def patch(self, **changes: object) -> "ActivationSession":
        return replace(self, **changes)


@dataclass(frozen=True)
class ActivationMetrics:
    time_to_pipeline_ready_seconds: float | None
    time_to_whatsapp_ready_seconds: float | None
    time_to_first_inbound_seconds: float | None
    time_to_first_stage_move_seconds: float | None
    time_to_aha_seconds: float | None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
