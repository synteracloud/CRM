"""Basic chat command parsing for conversational CRM."""

from __future__ import annotations

import re
from datetime import date, timedelta

from .entities import CommandIntent, CommandParseResult


class BasicCommandParser:
    """Rule-based parser for high-signal CRM actions in chat."""

    STAGE_ALIASES = {
        "new": "new",
        "open": "open",
        "qualified": "qualified",
        "proposal": "proposal",
        "negotiation": "negotiation",
        "won": "won",
        "lost": "lost",
        "converted": "converted",
    }

    def parse(self, text: str, *, today: date | None = None) -> CommandParseResult:
        normalized = " ".join(text.lower().strip().split())
        intents: list[CommandIntent] = []

        if "send invoice" in normalized or "invoice" in normalized:
            intents.append(CommandIntent(name="send_invoice", confidence=0.95))

        if "follow up tomorrow" in normalized:
            due = (today or date.today()) + timedelta(days=1)
            intents.append(
                CommandIntent(
                    name="schedule_follow_up",
                    confidence=0.98,
                    entities={"due_date": due.isoformat(), "natural": "tomorrow"},
                )
            )

        stage_match = re.search(r"(?:move|set)\s+(?:stage\s+)?(?:to\s+)?([a-z_ ]+)$", normalized)
        if stage_match:
            raw = stage_match.group(1).strip()
            stage = self.STAGE_ALIASES.get(raw)
            if stage:
                intents.append(CommandIntent(name="move_stage", confidence=0.93, entities={"stage": stage}))

        if "qualified" in normalized and "lead" in normalized:
            intents.append(CommandIntent(name="move_stage", confidence=0.88, entities={"stage": "qualified"}))
        if "converted" in normalized and "lead" in normalized:
            intents.append(CommandIntent(name="move_stage", confidence=0.88, entities={"stage": "converted"}))

        email_match = re.search(r"email\s+(?:to\s+)?([a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})", normalized)
        if email_match:
            intents.append(
                CommandIntent(
                    name="update_lead",
                    confidence=0.9,
                    entities={"field": "email", "value": email_match.group(1)},
                )
            )

        phone_match = re.search(r"phone\s+(?:to\s+)?([+0-9\-() ]{7,})", normalized)
        if phone_match:
            intents.append(
                CommandIntent(
                    name="update_lead",
                    confidence=0.86,
                    entities={"field": "phone", "value": phone_match.group(1).strip()},
                )
            )

        score_match = re.search(r"score\s+(?:to\s+)?(\d{1,3})", normalized)
        if score_match:
            intents.append(
                CommandIntent(
                    name="update_lead",
                    confidence=0.89,
                    entities={"field": "score", "value": int(score_match.group(1))},
                )
            )

        return CommandParseResult(intents=tuple(intents), unmatched_text="" if intents else normalized)
