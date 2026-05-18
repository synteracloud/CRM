"""Workflow mapping for campaign lifecycle and segmentation execution."""

from __future__ import annotations

from src.event_bus.catalog_events import EVENT_NAME_SET

WORKFLOW_NAME = "Campaign segmentation lifecycle"

CAMPAIGN_SEGMENTATION_WORKFLOW: tuple[dict[str, str], ...] = (
    {
        "step": "draft",
        "status": "draft",
        "service": "Campaign Service",
        "event": "campaign_drafted",
        "catalog_event": "campaign.created.v1",
    },
    {
        "step": "activate",
        "status": "active",
        "service": "Campaign Service",
        "event": "campaign_activated",
        "catalog_event": "campaign.activated.v1",
    },
    {
        "step": "complete",
        "status": "completed",
        "service": "Campaign Service",
        "event": "campaign_completed",
        "catalog_event": "campaign.completed.v1",
    },
)


def assert_campaign_workflow_events_are_catalog_backed() -> None:
    missing = sorted(
        {
            row["catalog_event"]
            for row in CAMPAIGN_SEGMENTATION_WORKFLOW
            if row["catalog_event"] not in EVENT_NAME_SET
        }
    )
    if missing:
        raise ValueError(f"Campaign workflow references unknown catalog events: {missing}")
