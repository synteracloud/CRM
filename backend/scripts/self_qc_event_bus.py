"""Self-QC checks for event bus/event tracking implementation.

Checks:
1) All code-defined events match docs/event-catalog.md.
2) Handlers are present for every catalog event.
3) Idempotency guard prevents duplicate processing.
4) Event store payload validation enforces required fields for every event.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.event_bus import (
    EVENT_NAMES,
    DEFAULT_EVENT_HANDLERS,
    Event,
    EventStore,
    EventValidationError,
    InMemoryEventBus,
    load_event_payload_requirements,
)

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
        payload={
            "lead_id": "lead-1",
            "owner_user_id": "user-1",
            "source": "web",
            "status": "new",
            "score": 10,
            "email": "a@example.com",
            "phone": "555",
            "company_name": "Acme",
            "created_at": "2026-03-26T00:00:00Z",
        },
    )

    bus.publish(event)
    bus.publish(event)  # duplicate delivery

    if seen != ["evt-123"]:
        raise AssertionError(f"Expected one delivery, got: {seen}")


def assert_payload_requirements() -> None:
    reqs = load_event_payload_requirements()
    if set(reqs) != set(EVENT_NAMES):
        raise AssertionError("Catalog payload requirements did not load for all events.")

    store = EventStore()
    for idx, event_name in enumerate(EVENT_NAMES, start=1):
        required_fields = reqs[event_name]
        payload = {field: f"value-{field}" for field in required_fields}
        event = Event(
            event_name=event_name,
            event_id=f"evt-ok-{idx}",
            occurred_at="2026-03-26T00:00:00Z",
            tenant_id="tenant-1",
            payload=payload,
        )
        store.append(event)

        if required_fields:
            missing_payload = {field: f"value-{field}" for field in required_fields[1:]}
            bad_event = Event(
                event_name=event_name,
                event_id=f"evt-bad-{idx}",
                occurred_at="2026-03-26T00:00:00Z",
                tenant_id="tenant-1",
                payload=missing_payload,
            )
            try:
                store.append(bad_event)
            except EventValidationError:
                continue
            raise AssertionError(f"Expected EventValidationError for event={event_name}")


def main() -> None:
    assert_catalog_alignment()
    assert_handlers_coverage()
    assert_idempotency()
    assert_payload_requirements()
    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
