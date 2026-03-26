"""Self-QC checks for event bus implementation.

Checks:
1) All code-defined events match docs/event-catalog.md.
2) Handlers are present for every catalog event.
3) Idempotency guard prevents duplicate processing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.event_bus import EVENT_NAMES, DEFAULT_EVENT_HANDLERS, Event, InMemoryEventBus

CATALOG_PATH = Path("docs/event-catalog.md")


def extract_catalog_events() -> set[str]:
    content = CATALOG_PATH.read_text(encoding="utf-8")
    pattern = r"`([a-z0-9_]+(?:\.[a-z0-9_]+)+\.v1)`"
    return set(re.findall(pattern, content))


def assert_catalog_alignment() -> None:
    doc_events = extract_catalog_events()
    code_events = set(EVENT_NAMES)
    if doc_events != code_events:
        missing_in_code = sorted(doc_events - code_events)
        missing_in_docs = sorted(code_events - doc_events)
        raise AssertionError(
            "Event catalog mismatch. "
            f"Missing in code={missing_in_code}; Missing in docs={missing_in_docs}"
        )


def assert_handlers_coverage() -> None:
    code_events = set(EVENT_NAMES)
    handler_events = set(DEFAULT_EVENT_HANDLERS.keys())
    if code_events != handler_events:
        raise AssertionError("Default handlers are missing one or more catalog events.")


def assert_idempotency() -> None:
    bus = InMemoryEventBus()
    seen: list[str] = []

    def handler(event: Event) -> None:
        seen.append(event.event_id)

    bus.subscribe("lead.created.v1", handler)

    event = Event(
        event_name="lead.created.v1",
        event_id="evt-123",
        occurred_at="2026-03-26T00:00:00Z",
        tenant_id="tenant-1",
        payload={"lead_id": "lead-1"},
    )

    bus.publish(event)
    bus.publish(event)  # duplicate delivery

    if seen != ["evt-123"]:
        raise AssertionError(f"Expected one delivery, got: {seen}")


def main() -> None:
    assert_catalog_alignment()
    assert_handlers_coverage()
    assert_idempotency()
    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
