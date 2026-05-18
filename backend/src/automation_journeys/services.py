"""Journey engine: definitions, trigger handling, step execution, and delays."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any

from src.event_bus import Event
from src.event_bus.catalog_events import EVENT_NAME_SET

from .entities import (
    JourneyDefinition,
    JourneyInstance,
    JourneyNotFoundError,
    JourneyStep,
    JourneyValidationError,
)

ALLOWED_ACTIONS: frozenset[str] = frozenset({"email", "update", "assign", "delay"})


class JourneyService:
    def __init__(self) -> None:
        self._definitions: dict[str, JourneyDefinition] = {}
        self._instances: dict[str, JourneyInstance] = {}
        self._event_bindings: dict[str, set[str]] = {}
        self._instance_counter = 0

    def create_journey(self, definition: JourneyDefinition) -> JourneyDefinition:
        self._validate_definition(definition)
        self._definitions[definition.journey_id] = definition
        self._event_bindings.setdefault(definition.trigger_event, set()).add(definition.journey_id)
        return definition

    def stop_journey(self, journey_id: str) -> JourneyDefinition:
        definition = self.get_journey(journey_id)
        updated = replace(definition, is_active=False)
        self._definitions[journey_id] = updated

        for instance in self._instances.values():
            if instance.journey_id == journey_id and instance.status in {"running", "waiting"}:
                instance.status = "stopped"
                instance.completed_at = _now_iso()
                instance.execution_log.append({"action": "stop", "at": instance.completed_at})
        return updated

    def start_journey(self, journey_id: str, event: Event) -> JourneyInstance:
        definition = self.get_journey(journey_id)
        if definition.trigger_event != event.event_name:
            raise JourneyValidationError(
                f"Journey {journey_id} expects trigger {definition.trigger_event}, got {event.event_name}"
            )
        if definition.tenant_id != event.tenant_id:
            raise JourneyValidationError(
                f"Journey {journey_id} tenant mismatch: {definition.tenant_id} != {event.tenant_id}"
            )
        if not definition.is_active:
            raise JourneyValidationError(f"Journey is not active: {journey_id}")

        instance = JourneyInstance(
            instance_id=self._next_instance_id(journey_id),
            tenant_id=definition.tenant_id,
            journey_id=journey_id,
            trigger_event=event.event_name,
            trigger_event_id=event.event_id,
            status="running",
            current_step_index=0,
            started_at=event.occurred_at,
        )
        self._instances[instance.instance_id] = instance
        self._run_until_wait_or_complete(instance)
        return instance

    def handle_event(self, event: Event) -> list[JourneyInstance]:
        started: list[JourneyInstance] = []
        for journey_id in sorted(self._event_bindings.get(event.event_name, set())):
            definition = self._definitions[journey_id]
            if definition.is_active and definition.tenant_id == event.tenant_id:
                started.append(self.start_journey(journey_id, event))
        return started

    def resume_due_delays(self, now_iso: str | None = None) -> list[JourneyInstance]:
        now = _parse_time(now_iso) if now_iso else datetime.now(timezone.utc)
        resumed: list[JourneyInstance] = []
        for instance in self._instances.values():
            if instance.status != "waiting" or not instance.waiting_until:
                continue
            if _parse_time(instance.waiting_until) <= now:
                instance.status = "running"
                instance.waiting_until = None
                instance.execution_log.append({"action": "delay.resumed", "at": _to_iso(now)})
                self._run_until_wait_or_complete(instance)
                resumed.append(instance)
        return resumed

    def event_bindings(self) -> dict[str, tuple[str, ...]]:
        return {event_name: tuple(sorted(journey_ids)) for event_name, journey_ids in self._event_bindings.items()}

    def list_instances(self, journey_id: str | None = None) -> list[JourneyInstance]:
        if journey_id is None:
            return list(self._instances.values())
        return [instance for instance in self._instances.values() if instance.journey_id == journey_id]

    def get_journey(self, journey_id: str) -> JourneyDefinition:
        definition = self._definitions.get(journey_id)
        if not definition:
            raise JourneyNotFoundError(f"Journey not found: {journey_id}")
        return definition

    def _run_until_wait_or_complete(self, instance: JourneyInstance) -> None:
        definition = self.get_journey(instance.journey_id)
        steps = definition.steps
        while instance.current_step_index < len(steps):
            step = steps[instance.current_step_index]
            if step.action == "delay":
                self._apply_delay(instance, step)
                return
            self._execute_step(instance, step)
            instance.current_step_index += 1

        instance.status = "completed"
        instance.completed_at = _now_iso()

    def _execute_step(self, instance: JourneyInstance, step: JourneyStep) -> None:
        executor = {
            "email": self._exec_email,
            "update": self._exec_update,
            "assign": self._exec_assign,
        }.get(step.action)
        if not executor:
            instance.status = "failed"
            instance.completed_at = _now_iso()
            instance.error_message = f"Undefined action executor: {step.action}"
            raise JourneyValidationError(instance.error_message)

        output = executor(step.config)
        instance.execution_log.append(
            {
                "step_id": step.step_id,
                "action": step.action,
                "output": output,
                "at": _now_iso(),
            }
        )

    def _apply_delay(self, instance: JourneyInstance, step: JourneyStep) -> None:
        if step.delay_seconds <= 0:
            instance.status = "failed"
            instance.error_message = f"Delay step requires positive delay_seconds. step={step.step_id}"
            instance.completed_at = _now_iso()
            raise JourneyValidationError(instance.error_message)

        wait_until = datetime.now(timezone.utc) + timedelta(seconds=step.delay_seconds)
        instance.execution_log.append(
            {
                "step_id": step.step_id,
                "action": "delay.started",
                "delay_seconds": step.delay_seconds,
                "at": _now_iso(),
            }
        )
        instance.status = "waiting"
        instance.waiting_until = _to_iso(wait_until)
        instance.current_step_index += 1

    @staticmethod
    def _exec_email(config: dict[str, Any]) -> dict[str, Any]:
        return {
            "channel": "email",
            "to": config.get("to", "owner"),
            "template": config.get("template", "default-template"),
            "subject": config.get("subject", "Automated CRM update"),
        }

    @staticmethod
    def _exec_update(config: dict[str, Any]) -> dict[str, Any]:
        return {
            "operation": "update",
            "entity": config.get("entity", "record"),
            "fields": config.get("fields", {}),
        }

    @staticmethod
    def _exec_assign(config: dict[str, Any]) -> dict[str, Any]:
        return {
            "operation": "assign",
            "assignee": config.get("assignee", "queue:default"),
            "reason": config.get("reason", "journey-assignment"),
        }

    @staticmethod
    def _validate_definition(definition: JourneyDefinition) -> None:
        if definition.trigger_event not in EVENT_NAME_SET:
            raise JourneyValidationError(f"Unknown trigger event: {definition.trigger_event}")
        if not definition.steps:
            raise JourneyValidationError("Journey must contain at least one step")

        seen_step_ids: set[str] = set()
        for idx, step in enumerate(definition.steps):
            if step.action not in ALLOWED_ACTIONS:
                raise JourneyValidationError(f"Unsupported step action: {step.action}")
            if step.step_id in seen_step_ids:
                raise JourneyValidationError(f"Duplicate step_id: {step.step_id}")
            seen_step_ids.add(step.step_id)
            if step.action == "delay" and step.delay_seconds <= 0:
                raise JourneyValidationError(f"Delay step must define delay_seconds > 0. step={step.step_id}")
            if step.action != "delay" and step.delay_seconds:
                raise JourneyValidationError(
                    f"Non-delay step should not define delay_seconds. step={step.step_id}, index={idx}"
                )

    def _next_instance_id(self, journey_id: str) -> str:
        self._instance_counter += 1
        return f"jrninst::{journey_id}::{self._instance_counter}"


def _now_iso() -> str:
    return _to_iso(datetime.now(timezone.utc))


def _to_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
