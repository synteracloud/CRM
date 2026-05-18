from __future__ import annotations

import unittest

from src.data_deduplication_engine import DataDeduplicationEngine, DuplicatePreventedError


class DataDeduplicationEngineTests(unittest.TestCase):
    def test_prevents_duplicate_lead_on_create_and_creates_manual_review(self) -> None:
        captured_reviews: list[str] = []

        def on_review(task) -> None:  # type: ignore[no-untyped-def]
            captured_reviews.append(task.review_id)

        engine = DataDeduplicationEngine(review_hook=on_review)
        engine.upsert_record(
            entity_type="lead",
            tenant_id="tenant-1",
            record={
                "lead_id": "lead-1",
                "email": "ava@example.com",
                "phone": "+1 (206) 555-0100",
                "company_name": "Acme Inc",
                "created_at": "2026-03-01T00:00:00Z",
            },
        )

        with self.assertRaises(DuplicatePreventedError):
            engine.upsert_record(
                entity_type="lead",
                tenant_id="tenant-1",
                record={
                    "lead_id": "lead-2",
                    "email": "ava@example.com",
                    "phone": "+1 (206) 555-9999",
                    "company_name": "Acme Inc",
                    "created_at": "2026-03-02T00:00:00Z",
                },
            )

        reviews = engine.list_manual_reviews()
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0].incoming_id, "lead-2")
        self.assertEqual(reviews[0].existing_id, "lead-1")
        self.assertEqual(len(captured_reviews), 1)

    def test_auto_merges_contact_when_strong_match_and_logs_trace(self) -> None:
        engine = DataDeduplicationEngine()
        engine.upsert_record(
            entity_type="contact",
            tenant_id="tenant-1",
            record={
                "contact_id": "con-1",
                "email": "mia@example.com",
                "phone": "+1 (425) 555-0199",
                "first_name": "Mia",
                "last_name": "Lopez",
                "account_id": "acc-1",
                "created_at": "2026-03-01T00:00:00Z",
            },
        )

        decision = engine.upsert_record(
            entity_type="contact",
            tenant_id="tenant-1",
            record={
                "contact_id": "con-2",
                "email": "mia@example.com",
                "phone": "4255550199",
                "first_name": "Mia",
                "last_name": "Lopez",
                "account_id": "acc-1",
                "created_at": "2026-03-02T00:00:00Z",
            },
        )

        self.assertEqual(decision.decision, "merged")
        merges = engine.list_merge_workflows()
        self.assertEqual(len(merges), 1)
        self.assertEqual(merges[0].entity_type, "contact")
        self.assertEqual(merges[0].decision_reason, "safe_auto_merge")
        self.assertGreaterEqual(len(merges[0].evidence), 2)

    def test_manual_review_approval_merges_and_is_traceable(self) -> None:
        engine = DataDeduplicationEngine()
        engine.upsert_record(
            entity_type="account",
            tenant_id="tenant-1",
            record={
                "account_id": "acc-1",
                "name": "Northwind LLC",
                "website": "https://northwind.com",
                "billing_address": "100 Main St Seattle",
                "created_at": "2026-03-01T00:00:00Z",
            },
        )

        with self.assertRaises(DuplicatePreventedError):
            engine.upsert_record(
                entity_type="account",
                tenant_id="tenant-1",
                record={
                    "account_id": "acc-2",
                    "name": "Northwind LLC",
                    "website": "northwind.com",
                    "billing_address": "100 Main St Seattle",
                    "created_at": "2026-03-02T00:00:00Z",
                },
            )

        review = engine.list_manual_reviews()[0]
        decision = engine.decide_manual_review(review.review_id, approve_merge=True, decided_by="user-1")

        self.assertEqual(decision.decision, "merged")
        merges = engine.list_merge_workflows()
        self.assertEqual(len(merges), 1)
        self.assertEqual(merges[0].executed_by, "user-1")
        self.assertEqual(merges[0].decision_reason, "manual_review_approved_merge")


if __name__ == "__main__":
    unittest.main()
