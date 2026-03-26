"""Workflow mapping for campaign lifecycle and segmentation execution."""

from __future__ import annotations

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
