"""Self-QC checks for B2-P01 Lead Management implementation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.lead_management import API_ENDPOINTS, LEAD_FIELDS, LEAD_LIFECYCLE_WORKFLOW

EXPECTED_LEAD_FIELDS = (
    "lead_id",
    "tenant_id",
    "owner_user_id",
    "source",
    "status",
    "score",
    "email",
    "phone",
    "company_name",
    "created_at",
    "converted_at",
)

EXPECTED_STEPS = ("create", "qualify", "convert")


def assert_matches_domain_model_exactly() -> None:
    if LEAD_FIELDS != EXPECTED_LEAD_FIELDS:
        raise AssertionError(f"Lead fields mismatch. expected={EXPECTED_LEAD_FIELDS}, actual={LEAD_FIELDS}")


def assert_no_duplicate_entities() -> None:
    if len(set(LEAD_FIELDS)) != len(LEAD_FIELDS):
        raise AssertionError("Duplicate fields detected in Lead entity definition.")


def assert_workflow_fully_covered() -> None:
    steps = tuple(item["step"] for item in LEAD_LIFECYCLE_WORKFLOW)
    if steps != EXPECTED_STEPS:
        raise AssertionError(f"Workflow steps mismatch. expected={EXPECTED_STEPS}, actual={steps}")

    required_apis = {
        "list_leads",
        "create_lead",
        "get_lead",
        "update_lead",
        "delete_lead",
        "qualify_lead",
        "convert_lead",
    }
    missing = required_apis - set(API_ENDPOINTS.keys())
    if missing:
        raise AssertionError(f"Missing required lead APIs: {sorted(missing)}")


def main() -> None:
    assert_matches_domain_model_exactly()
    assert_no_duplicate_entities()
    assert_workflow_fully_covered()
    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
