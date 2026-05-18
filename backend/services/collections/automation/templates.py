"""Message templates for reminder tone progression from polite to firm."""

from __future__ import annotations

from dataclasses import dataclass

from .entities import ReminderStage, ToneLevel


@dataclass(frozen=True)
class MessageTemplate:
    template_id: str
    tone: ToneLevel
    body: str


class MessageTemplateCatalog:
    """Select tone-aware templates based on reminder stage and escalation level."""

    _TEMPLATES: dict[tuple[ReminderStage, ToneLevel], MessageTemplate] = {
        ("pre_due", "polite"): MessageTemplate(
            template_id="collections.pre_due.polite",
            tone="polite",
            body="Friendly reminder: your invoice is due soon. Please pay by due date to avoid interruption.",
        ),
        ("due", "polite"): MessageTemplate(
            template_id="collections.due.polite",
            tone="polite",
            body="Your invoice is due today. Please complete payment at your earliest convenience.",
        ),
        ("overdue", "polite"): MessageTemplate(
            template_id="collections.overdue.polite",
            tone="polite",
            body="Payment appears overdue. Please share payment confirmation or expected payment date.",
        ),
        ("overdue", "firm"): MessageTemplate(
            template_id="collections.overdue.firm",
            tone="firm",
            body="Urgent: payment is still overdue despite reminders. Immediate action is required.",
        ),
        ("due", "firm"): MessageTemplate(
            template_id="collections.due.firm",
            tone="firm",
            body="Action required today: settle this due invoice to prevent escalation.",
        ),
        ("pre_due", "firm"): MessageTemplate(
            template_id="collections.pre_due.firm",
            tone="firm",
            body="Please schedule payment now to avoid becoming overdue and entering escalation.",
        ),
    }

    def get(self, stage: ReminderStage, escalation_level: int) -> MessageTemplate:
        tone: ToneLevel = "firm" if escalation_level >= 2 and stage in {"due", "overdue"} else "polite"
        return self._TEMPLATES[(stage, tone)]
