from __future__ import annotations

import unittest

from src.event_bus import API_ENDPOINTS, EVENT_NAMES, Event, EventStore, EventTrackingApi, EventValidationError, InMemoryEventBus
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

    def test_store_dedupes_by_tenant_event_and_event_id(self) -> None:
        store = EventStore()
        lead_fields = load_event_payload_requirements()["lead.created.v1"]

        event_a = Event(
            event_name="lead.created.v1",
            event_id="evt-shared",
            occurred_at="2026-03-20T00:00:00Z",
            tenant_id="tenant-1",
            payload={field: f"a-{field}" for field in lead_fields},
        )
        event_b = Event(
            event_name="lead.created.v1",
            event_id="evt-shared",
            occurred_at="2026-03-21T00:00:00Z",
            tenant_id="tenant-2",
            payload={field: f"b-{field}" for field in lead_fields},
        )

        store.append(event_a)
        store.append(event_b)
        self.assertEqual(len(store.query(limit=10)), 2)

    def test_event_bus_dedupes_by_tenant_event_and_event_id(self) -> None:
        bus = InMemoryEventBus()
        observed: list[tuple[str, str]] = []
        lead_fields = load_event_payload_requirements()["lead.created.v1"]

        bus.subscribe("lead.created.v1", lambda event: observed.append((event.tenant_id, event.event_id)))
        bus.publish(
            Event(
                event_name="lead.created.v1",
                event_id="evt-shared",
                occurred_at="2026-03-20T00:00:00Z",
                tenant_id="tenant-1",
                payload={field: f"a-{field}" for field in lead_fields},
            )
        )
        bus.publish(
            Event(
                event_name="lead.created.v1",
                event_id="evt-shared",
                occurred_at="2026-03-21T00:00:00Z",
                tenant_id="tenant-2",
                payload={field: f"b-{field}" for field in lead_fields},
            )
        )

        self.assertEqual(observed, [("tenant-1", "evt-shared"), ("tenant-2", "evt-shared")])


if __name__ == "__main__":
    unittest.main()
