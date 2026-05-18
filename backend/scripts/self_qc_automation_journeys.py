"""Self-QC checks for B3-P02 automation journeys."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.automation_journeys import ALLOWED_ACTIONS, TRIGGER_EVENT_BINDINGS, WORKFLOW_AUTOMATION_TRIGGER_EVENTS
from src.automation_journeys.events import assert_triggers_in_catalog
from src.automation_journeys.workflow_mapping import build_default_journeys


def assert_trigger_mapping() -> None:
    assert_triggers_in_catalog()


def assert_no_undefined_actions() -> None:
    default_journeys = build_default_journeys("tenant-self-qc")
    for definition in default_journeys:
        for step in definition.steps:
            if step.action not in ALLOWED_ACTIONS:
                raise AssertionError(
                    f"Undefined action detected. journey={definition.journey_id}, action={step.action}"
                )


def assert_step_sequences_valid() -> None:
    default_journeys = build_default_journeys("tenant-self-qc")
    for definition in default_journeys:
        if not definition.steps:
            raise AssertionError(f"Journey has no steps: {definition.journey_id}")

        seen = set()
        for index, step in enumerate(definition.steps):
            if step.step_id in seen:
                raise AssertionError(f"Duplicate step id in {definition.journey_id}: {step.step_id}")
            seen.add(step.step_id)
            if step.action == "delay" and step.delay_seconds <= 0:
                raise AssertionError(f"Invalid delay step at index={index} in {definition.journey_id}")


def assert_binding_not_empty() -> None:
    binding_events = {event for events in TRIGGER_EVENT_BINDINGS.values() for event in events}
    missing = set(WORKFLOW_AUTOMATION_TRIGGER_EVENTS) - binding_events
    if missing:
        raise AssertionError(f"Unbound workflow automation triggers: {sorted(missing)}")


def main() -> None:
    assert_trigger_mapping()
    assert_no_undefined_actions()
    assert_step_sequences_valid()
    assert_binding_not_empty()
    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
