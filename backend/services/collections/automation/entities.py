"""Entities for collections automation reminder cycle and escalation orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

ReminderStage = Literal["pre_due", "due", "overdue"]
ToneLevel = Literal["polite", "firm"]
ResponseState = Literal["replied", "ignored"]


@dataclass(frozen=True)
class ReminderTouchpoint:
    stage: ReminderStage
    offset_days: int
    sequence: int

    def scheduled_for(self, due_date: str) -> str:
        return (date.fromisoformat(due_date) + timedelta(days=self.offset_days)).isoformat()


@dataclass(frozen=True)
class ReminderPlan:
    invoice_id: str
    due_date: str
    touchpoints: tuple[ReminderTouchpoint, ...]


@dataclass(frozen=True)
class CustomerResponse:
    invoice_id: str
    reminder_sequence: int
    state: ResponseState
    response_note: str | None = None


@dataclass(frozen=True)
class EscalationDecision:
    invoice_id: str
    escalation_level: int
    reason: str
    next_tone: ToneLevel


@dataclass(frozen=True)
class AutomationCycleReport:
    invoice_id: str
    expected_reminders: int
    sent_reminders: int
    missed_payment_detected: bool
    ignored_count: int
    replied_count: int
    alignment_percent: int
    score: str
    diagnostics: list[str] = field(default_factory=list)
