"""Self-QC checks for B3-P01 Campaigns Segmentation implementation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.campaigns import (
    API_ENDPOINTS,
    CAMPAIGN_FIELDS,
    CAMPAIGN_SEGMENTATION_WORKFLOW,
    CONTACT_SEGMENT_FIELDS,
    LEAD_SEGMENT_FIELDS,
    SEGMENT_FIELDS,
    VALID_SEGMENT_ENTITIES,
)

EXPECTED_CAMPAIGN_FIELDS = (
    "campaign_id",
    "tenant_id",
    "owner_user_id",
    "name",
    "description",
    "status",
    "segment_id",
    "starts_at",
    "ends_at",
    "created_at",
    "updated_at",
    "activated_at",
    "completed_at",
)

EXPECTED_SEGMENT_FIELDS = (
    "segment_id",
    "tenant_id",
    "name",
    "description",
    "entity_type",
    "rules",
    "created_at",
    "updated_at",
)

EXPECTED_WORKFLOW_STEPS = ("draft", "activate", "complete")


REQUIRED_APIS = {
    "list_campaigns",
    "create_campaign",
    "get_campaign",
    "update_campaign",
    "delete_campaign",
    "activate_campaign",
    "list_segments",
    "create_segment",
    "get_segment",
    "update_segment",
    "delete_segment",
    "link_campaign_lead",
    "link_campaign_contact",
}


def assert_entities_valid() -> None:
    if CAMPAIGN_FIELDS != EXPECTED_CAMPAIGN_FIELDS:
        raise AssertionError(f"Campaign fields mismatch. expected={EXPECTED_CAMPAIGN_FIELDS}, actual={CAMPAIGN_FIELDS}")
    if SEGMENT_FIELDS != EXPECTED_SEGMENT_FIELDS:
        raise AssertionError(f"Segment fields mismatch. expected={EXPECTED_SEGMENT_FIELDS}, actual={SEGMENT_FIELDS}")


def assert_segments_use_valid_entities_only() -> None:
    if VALID_SEGMENT_ENTITIES != ("lead", "contact"):
        raise AssertionError(f"Invalid segment entities: {VALID_SEGMENT_ENTITIES}")
    if "company_name" in CONTACT_SEGMENT_FIELDS:
        raise AssertionError("Contact segment fields duplicate lead-only field company_name.")
    if "first_name" in LEAD_SEGMENT_FIELDS:
        raise AssertionError("Lead segment fields duplicate contact-only field first_name.")


def assert_workflow_complete() -> None:
    steps = tuple(item["step"] for item in CAMPAIGN_SEGMENTATION_WORKFLOW)
    if steps != EXPECTED_WORKFLOW_STEPS:
        raise AssertionError(f"Workflow steps mismatch. expected={EXPECTED_WORKFLOW_STEPS}, actual={steps}")

    missing_apis = REQUIRED_APIS - set(API_ENDPOINTS.keys())
    if missing_apis:
        raise AssertionError(f"Missing required campaign APIs: {sorted(missing_apis)}")


def main() -> None:
    assert_entities_valid()
    assert_segments_use_valid_entities_only()
    assert_workflow_complete()
    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
