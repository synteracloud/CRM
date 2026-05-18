"""Default event handlers mapped for every catalog event."""

from __future__ import annotations

from typing import Final

from .catalog_events import EVENT_NAMES
from .interfaces import Event


def _noop_handler(_: Event) -> None:
    """Default placeholder handler for downstream service implementation."""


def build_default_handlers() -> dict[str, list]:
    return {event_name: [_noop_handler] for event_name in EVENT_NAMES}


DEFAULT_EVENT_HANDLERS: Final[dict[str, list]] = build_default_handlers()
