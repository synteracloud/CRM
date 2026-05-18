"""Integration tests for public WhatsApp webhook and conversation endpoints.

Spec: backend/docs/whatsapp-execution-model.md
API standards: backend/docs/api-standards.md
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

import services.conversation.http.public as conv_module
from services.app import app
from services.auth.jwt_deps import TokenClaims, get_current_user

# ── Shared fixtures ───────────────────────────────────────────────────────────

TEST_TENANT = "tenant-conv-001"
TEST_TENANT_B = "tenant-conv-002"
_API_KEY = "dev-webhook-key"


def _override_auth_a():
    return TokenClaims(sub="user-001", tenant_id=TEST_TENANT, role="sales_rep", jti=str(uuid.uuid4()))


def _override_auth_b():
    return TokenClaims(sub="user-002", tenant_id=TEST_TENANT_B, role="sales_rep", jti=str(uuid.uuid4()))


@pytest.fixture(autouse=True)
def clear_state():
    conv_module._conversations.clear()
    conv_module._messages.clear()
    yield
    conv_module._conversations.clear()
    conv_module._messages.clear()


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = _override_auth_a
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _webhook_payload(
    from_number: str = "+923001111111",
    text: str = "price quote please",
    tenant_id: str = TEST_TENANT,
) -> dict:
    return {
        "from_number": from_number,
        "to_number": "+929990000001",
        "provider_message_id": str(uuid.uuid4()),
        "text": text,
        "occurred_at": "2026-05-18T10:00:00Z",
        "tenant_id": tenant_id,
    }


# ── POST /api/v1/webhooks/whatsapp ────────────────────────────────────────────


class TestWebhookIngestion:
    def test_valid_key_returns_200_with_envelope(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(),
            headers={"X-Api-Key": _API_KEY},
        )
        assert r.status_code == 200
        body = r.json()
        assert "data" in body
        assert "meta" in body

    def test_classifies_lead_inquiry(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(text="price quote please"),
            headers={"X-Api-Key": _API_KEY},
        )
        assert r.json()["data"]["intent"] == "lead_inquiry"

    def test_classifies_payment_query(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(text="jazzcash payment sent"),
            headers={"X-Api-Key": _API_KEY},
        )
        assert r.json()["data"]["intent"] == "payment_query"

    def test_anti_lead_loss_always_creates_conversation(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(text="random text no keyword"),
            headers={"X-Api-Key": _API_KEY},
        )
        assert r.status_code == 200
        assert r.json()["data"]["conversation_id"] is not None

    def test_should_create_lead_on_first_lead_inquiry(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(text="interested in your product"),
            headers={"X-Api-Key": _API_KEY},
        )
        assert r.json()["data"]["should_create_lead"] is True

    def test_should_not_create_lead_on_second_message(self, client: TestClient) -> None:
        payload = _webhook_payload(text="interested in your product")
        client.post("/api/v1/webhooks/whatsapp", json=payload, headers={"X-Api-Key": _API_KEY})
        r = client.post("/api/v1/webhooks/whatsapp", json=payload, headers={"X-Api-Key": _API_KEY})
        assert r.json()["data"]["should_create_lead"] is False

    def test_invalid_api_key_returns_401(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(),
            headers={"X-Api-Key": "wrong-key"},
        )
        assert r.status_code == 401

    def test_missing_api_key_returns_401(self, client: TestClient) -> None:
        r = client.post("/api/v1/webhooks/whatsapp", json=_webhook_payload())
        assert r.status_code == 401

    def test_media_on_invoice_classified_as_payment(self, client: TestClient) -> None:
        payload = _webhook_payload(text="")
        payload["has_media_attachment"] = True
        payload["linked_invoice_id"] = "inv-001"
        r = client.post(
            "/api/v1/webhooks/whatsapp",
            json=payload,
            headers={"X-Api-Key": _API_KEY},
        )
        assert r.json()["data"]["intent"] == "payment_query"

    def test_response_includes_message_id(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(),
            headers={"X-Api-Key": _API_KEY},
        )
        assert "message_id" in r.json()["data"]


# ── GET /api/v1/conversations ─────────────────────────────────────────────────


class TestListConversations:
    def test_empty_list_before_any_webhook(self, client: TestClient) -> None:
        r = client.get("/api/v1/conversations")
        assert r.status_code == 200
        assert r.json()["data"] == []

    def test_list_returns_conversation_after_webhook(self, client: TestClient) -> None:
        client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(),
            headers={"X-Api-Key": _API_KEY},
        )
        r = client.get("/api/v1/conversations")
        assert r.status_code == 200
        assert len(r.json()["data"]) == 1

    def test_tenant_isolation(self) -> None:
        # Tenant A creates a conversation
        app.dependency_overrides[get_current_user] = _override_auth_a
        with TestClient(app) as ca:
            ca.post(
                "/api/v1/webhooks/whatsapp",
                json=_webhook_payload(tenant_id=TEST_TENANT),
                headers={"X-Api-Key": _API_KEY},
            )

        # Tenant B should see no conversations
        app.dependency_overrides[get_current_user] = _override_auth_b
        with TestClient(app) as cb:
            r = cb.get("/api/v1/conversations")
        app.dependency_overrides.clear()

        assert r.status_code == 200
        assert r.json()["data"] == []


# ── GET /api/v1/conversations/{conversation_id} ───────────────────────────────


class TestGetConversation:
    def test_get_returns_conversation_with_messages(self, client: TestClient) -> None:
        client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(),
            headers={"X-Api-Key": _API_KEY},
        )
        conv_id = client.get("/api/v1/conversations").json()["data"][0]["conversation_id"]
        r = client.get(f"/api/v1/conversations/{conv_id}")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["conversation_id"] == conv_id
        assert "messages" in data

    def test_get_includes_message_content(self, client: TestClient) -> None:
        client.post(
            "/api/v1/webhooks/whatsapp",
            json=_webhook_payload(),
            headers={"X-Api-Key": _API_KEY},
        )
        conv_id = client.get("/api/v1/conversations").json()["data"][0]["conversation_id"]
        data = client.get(f"/api/v1/conversations/{conv_id}").json()["data"]
        assert len(data["messages"]) == 1
        assert data["messages"][0]["direction"] == "inbound"

    def test_get_unknown_returns_404(self, client: TestClient) -> None:
        r = client.get("/api/v1/conversations/nonexistent-conv-id")
        assert r.status_code == 404

    def test_get_tenant_isolation(self, client: TestClient) -> None:
        import uuid as _uuid
        conv_id = str(_uuid.uuid4())
        conv_module._conversations[f"other-tenant:{conv_id}"] = {
            "conversation_id": conv_id,
            "tenant_id": "other-tenant",
            "from_number": "+920000000000",
            "state": "ACTIVE",
            "created_at": "2026-05-18T00:00:00Z",
            "updated_at": "2026-05-18T00:00:00Z",
            "intent_history": [],
        }
        r = client.get(f"/api/v1/conversations/{conv_id}")
        assert r.status_code == 404
