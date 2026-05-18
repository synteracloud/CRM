"""Workflow mapping for lead lifecycle create -> qualify -> convert."""

from __future__ import annotations

WORKFLOW_NAME = "Lead intake, assignment, conversion"

LEAD_LIFECYCLE_WORKFLOW: tuple[dict[str, str], ...] = (
    {
        "step": "create",
        "status": "new",
        "service": "Lead Management Service",
        "event": "lead_created",
        "catalog_event": "lead.created.v1",
    },
    {
        "step": "qualify",
        "status": "qualified",
        "service": "Lead Management Service",
        "event": "lead_qualified",
        "catalog_event": "lead.assignment.updated.v1",
    },
    {
        "step": "convert",
        "status": "converted",
        "service": "Lead Management Service",
        "event": "lead_converted",
        "catalog_event": "lead.converted.v1",
    },
)
