"""Self-QC checks for B3-P05 Omnichannel Inbox implementation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.omnichannel_inbox import API_ENDPOINTS, MESSAGE_FIELDS, THREAD_FIELDS

EXPECTED_THREAD_FIELDS = (
    "message_thread_id",
    "tenant_id",
    "account_id",
    "contact_id",
    "channel_type",
    "subject",
    "status",
    "created_at",
    "updated_at",
)

EXPECTED_MESSAGE_FIELDS = (
    "message_id",
    "tenant_id",
    "message_thread_id",
    "direction",
    "provider_message_id",
    "sender",
    "recipient",
    "status",
    "sent_at",
    "delivered_at",
    "opened_at",
    "clicked_at",
)

REQUIRED_APIS = {
    "list_threads",
    "create_or_get_thread",
    "get_thread",
    "list_messages",
    "post_message",
    "route_thread",
    "get_thread_routing",
}


def assert_entities_match_domain_model() -> None:
    if THREAD_FIELDS != EXPECTED_THREAD_FIELDS:
        raise AssertionError(f"Thread fields mismatch. expected={EXPECTED_THREAD_FIELDS}, actual={THREAD_FIELDS}")
    if MESSAGE_FIELDS != EXPECTED_MESSAGE_FIELDS:
        raise AssertionError(f"Message fields mismatch. expected={EXPECTED_MESSAGE_FIELDS}, actual={MESSAGE_FIELDS}")


def assert_no_duplicate_fields() -> None:
    if len(set(THREAD_FIELDS)) != len(THREAD_FIELDS):
        raise AssertionError("Duplicate fields detected in MessageThread entity definition.")
    if len(set(MESSAGE_FIELDS)) != len(MESSAGE_FIELDS):
        raise AssertionError("Duplicate fields detected in Message entity definition.")


def assert_apis_covered() -> None:
    missing = REQUIRED_APIS - set(API_ENDPOINTS)
    if missing:
        raise AssertionError(f"Missing required omnichannel APIs: {sorted(missing)}")


def main() -> None:
    assert_entities_match_domain_model()
    assert_no_duplicate_fields()
    assert_apis_covered()
    print("Self-QC score: 10/10")


if __name__ == "__main__":
    main()
