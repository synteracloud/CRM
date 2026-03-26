from __future__ import annotations

import unittest

from src.event_bus import EVENT_NAMES, API_ENDPOINTS, Event, EventStore, EventTrackingApi, EventValidationError
from src.event_bus.catalog_schema import load_event_payload_requirements


class EventTrackingTests(unittest.TestCase):
    def test_catalog_requirements_cover_all_catalog_events(self) -> None:
        requirements = load_event_payload_requirements()
        self.assertEqual(set(requirements.keys()), set(EVENT_NAMES))
        self.assertIn("lead_id", requirements["lead.created.v1"])

    def test_store_rejects_missing_required_payload_field(self) -> None:
        store = EventStore()
        with self.assertRaises(EventValidationError):
            store.append(
                Event(
                    event_name="lead.created.v1",
                    event_id="evt-1",
                    occurred_at="2026-03-26T00:00:00Z",
                    tenant_id="tenant-1",
                    payload={
                        "owner_user_id": "user-1",
                        "source": "web",
                        "status": "new",
                        "score": 0,
                        "email": "x@example.com",
                        "phone": "123",
                        "company_name": "Acme",
                        "created_at": "2026-03-26T00:00:00Z",
                    },
                )
            )

    def test_query_api_filters_by_tenant_event_and_date(self) -> None:
        store = EventStore()
        api = EventTrackingApi(store)

        endpoint = API_ENDPOINTS["query_events"]
        self.assertEqual(endpoint["method"], "GET")

        lead_fields = load_event_payload_requirements()["lead.created.v1"]
        campaign_fields = load_event_payload_requirements()["campaign.created.v1"]

        api.record_event(
            Event(
                event_name="lead.created.v1",
                event_id="evt-a",
                occurred_at="2026-03-20T00:00:00Z",
                tenant_id="tenant-1",
                payload={field: f"v-{field}" for field in lead_fields},
            ),
            request_id="req-1",
        )
        api.record_event(
            Event(
                event_name="campaign.created.v1",
                event_id="evt-b",
                occurred_at="2026-03-21T00:00:00Z",
                tenant_id="tenant-1",
                payload={field: f"v-{field}" for field in campaign_fields},
            ),
            request_id="req-2",
        )
        api.record_event(
            Event(
                event_name="lead.created.v1",
                event_id="evt-c",
                occurred_at="2026-03-22T00:00:00Z",
                tenant_id="tenant-2",
                payload={field: f"v-{field}" for field in lead_fields},
            ),
            request_id="req-3",
        )

        response = api.query_events(
            request_id="req-4",
            tenant_id="tenant-1",
            event_name="lead.created.v1",
            occurred_from="2026-03-19T00:00:00Z",
            occurred_to="2026-03-21T00:00:00Z",
        )
        self.assertEqual([item["event_id"] for item in response["data"]], ["evt-a"])


if __name__ == "__main__":
    unittest.main()
