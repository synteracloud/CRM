"""Catalog schema extraction from docs/event-catalog.md."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parents[2] / "docs" / "event-catalog.md"
_ENVELOPE_FIELDS = {"event_id", "occurred_at", "tenant_id"}


def _normalize_field(field: str) -> str:
    return field.strip().removesuffix("[]")


@lru_cache(maxsize=1)
def load_event_payload_requirements() -> dict[str, tuple[str, ...]]:
    """Return required payload fields keyed by event name.

    Event envelope fields (`event_id`, `occurred_at`, `tenant_id`) are excluded
    because they are modeled as top-level Event attributes.
    """

    content = CATALOG_PATH.read_text(encoding="utf-8")
    requirements: dict[str, tuple[str, ...]] = {}

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or ".v1`" not in stripped:
            continue

        columns = [col.strip() for col in stripped.split("|")[1:-1]]
        if len(columns) < 4:
            continue

        event_cell, payload_cell = columns[1], columns[3]
        if not event_cell.startswith("`") or not payload_cell.startswith("`{"):
            continue

        event_name = event_cell.strip("`")
        payload_body = payload_cell.strip("`").strip()
        payload_body = payload_body.removeprefix("{").removesuffix("}").strip()

        fields: list[str] = []
        for raw_field in payload_body.split(","):
            field = _normalize_field(raw_field)
            if not field or field in _ENVELOPE_FIELDS:
                continue
            fields.append(field)

        requirements[event_name] = tuple(fields)

    return requirements
