"""Lead lifecycle event primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


LEAD_EVENT_TO_CATALOG: dict[str, str] = {
    "lead_created": "lead.created.v1",
    "lead_qualified": "lead.qualified.v1",
    "lead_converted": "lead.converted.v1",
}


@dataclass(frozen=True)
class LeadEvent:
    name: str
    tenant_id: str
    lead_id: str
    payload: dict[str, Any]
