"""Reminder scheduling and WhatsApp dispatch utilities."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from typing import Protocol

from .entities import ReminderEvent, utc_now


class WhatsAppAdapter(Protocol):
    def send_template(self, *, to: str, template_id: str, params: dict[str, str]) -> str:
        """Send WhatsApp template and return delivery status."""


REMINDER_OFFSETS: tuple[int, ...] = (-3, -1, 1, 7, 15)


class ReminderScheduler:
    def schedule(self, invoice_id: str, due_date: str, template_id: str = "invoice_due") -> list[ReminderEvent]:
        due = date.fromisoformat(due_date)
        reminders: list[ReminderEvent] = []
        for idx, offset in enumerate(REMINDER_OFFSETS, start=1):
            reminders.append(
                ReminderEvent(
                    reminder_event_id=f"rm-{invoice_id}-{idx}",
                    invoice_id=invoice_id,
                    scheduled_at=(due + timedelta(days=offset)).isoformat(),
                    sent_at=None,
                    channel="whatsapp",
                    template_id=template_id,
                    attempt_no=1,
                    delivery_status="queued",
                )
            )
        return reminders


class ReminderDispatcher:
    def __init__(self, adapter: WhatsAppAdapter) -> None:
        self._adapter = adapter

    def dispatch(self, reminder: ReminderEvent, recipient: str, params: dict[str, str]) -> ReminderEvent:
        status = self._adapter.send_template(to=recipient, template_id=reminder.template_id, params=params)
        mapped_status = status if status in {"sent", "delivered", "failed", "read"} else "sent"
        return replace(reminder, sent_at=utc_now(), delivery_status=mapped_status)
