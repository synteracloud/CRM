from __future__ import annotations

import unittest

from adapters.interfaces.messaging_adapter import InboundMessage, MessageDeliveryStatus, MessageSendResult, RawWebhookInput
from adapters.interfaces.types import AdapterContext
from services.leads import LeadsRepository, OwnerAssigner, WhatsAppLeadCaptureService
from services.messaging import MessagingRepository, WhatsAppCoreEngine


class _FakeAdapter:
    def parse_inbound(self, input: RawWebhookInput, ctx: AdapterContext) -> list[InboundMessage]:
        payload = input.body
        return [
            InboundMessage(
                event_id=payload["event_id"],
                provider_message_id=payload["provider_message_id"],
                from_number=payload["from"],
                to_number=payload.get("to", "+10000000000"),
                text=payload["text"],
                occurred_at=payload["occurred_at"],
                profile_name=payload.get("profile_name"),
                raw=payload,
            )
        ]

    def parse_webhook(self, input: RawWebhookInput, ctx: AdapterContext):
        return []

    def send_message(self, input, ctx):
        return MessageSendResult(
            message_id=input.message_id,
            provider_message_id=f"provider:{input.message_id}",
            status=MessageDeliveryStatus.SENT,
            accepted_at="2026-04-01T00:00:00Z",
        )

    def send_template(self, input, ctx):
        raise NotImplementedError

    def get_message_status(self, input, ctx):
        raise NotImplementedError


class WhatsAppLeadCaptureTests(unittest.TestCase):
    def test_inbound_creates_lead_assigns_owner_and_attaches_timeline(self) -> None:
        leads_repo = LeadsRepository()
        assigner = OwnerAssigner(default_owner_id="owner-default")
        assigner.configure("t1", ("owner-a", "owner-b"))
        lead_service = WhatsAppLeadCaptureService(repository=leads_repo, assigner=assigner)

        engine = WhatsAppCoreEngine(MessagingRepository(), _FakeAdapter(), "meta", lead_capture_service=lead_service)
        ctx = AdapterContext(tenant_id="t1", trace_id="tr-1", country_code="US")

        first = RawWebhookInput(headers={}, body={
            "event_id": "evt-1",
            "provider_message_id": "pm-1",
            "from": "+1 (206) 555-0100",
            "text": "Need pricing for 50 users",
            "occurred_at": "2026-04-01T10:00:00Z",
        })
        second = RawWebhookInput(headers={}, body={
            "event_id": "evt-2",
            "provider_message_id": "pm-2",
            "from": "+12065550100",
            "text": "confirmed, invoice paid",
            "occurred_at": "2026-04-01T10:05:00Z",
        })

        engine.handle_inbound_webhook(first, ctx)
        engine.handle_inbound_webhook(second, ctx)

        lead = next(iter(leads_repo.leads.values()))
        self.assertEqual(lead.owner_user_id, "owner-a")
        self.assertEqual(lead.stage.value, "Won")
        self.assertEqual(len(leads_repo.timeline(lead.lead_id)), 2)

    def test_phone_dedup_prevents_duplicate_leads(self) -> None:
        leads_repo = LeadsRepository()
        lead_service = WhatsAppLeadCaptureService(repository=leads_repo)
        engine = WhatsAppCoreEngine(MessagingRepository(), _FakeAdapter(), "meta", lead_capture_service=lead_service)
        ctx = AdapterContext(tenant_id="t1", trace_id="tr-1", country_code="US")

        for idx, phone in enumerate(["+12065550100", "+1 206 555 0100", "12065550100"], start=1):
            engine.handle_inbound_webhook(
                RawWebhookInput(
                    headers={},
                    body={
                        "event_id": f"evt-{idx}",
                        "provider_message_id": f"pm-{idx}",
                        "from": phone,
                        "text": "hello",
                        "occurred_at": f"2026-04-01T10:0{idx}:00Z",
                    },
                ),
                ctx,
            )

        self.assertEqual(len(leads_repo.leads), 1)


if __name__ == "__main__":
    unittest.main()
