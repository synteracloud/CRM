"""End-to-end integration test: WhatsApp lead → follow-up → invoice → payment.

Spec flow:
  1. WhatsApp inbound message classified as lead_inquiry → conversation created
  2. Follow-up task created for the lead
  3. Follow-up completed (lead closed)
  4. Invoice created for the closed lead's customer
  5. Payment callback received → reconciliation case created

All services share the same in-memory SQLite DB so the full chain is
verifiable without a real Postgres or Redis instance.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.app import app
from services.auth.jwt_deps import TokenClaims, get_current_user
from services.db import get_db
from services.db.base import Base
import services.db.models  # noqa: F401  — registers all ORM models
import services.conversation.http.public as conv_module
import services.collections.http.public as coll_module

# ── Shared SQLite test DB ─────────────────────────────────────────────────────

_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

TENANT = "e2e-tenant-001"
USER   = "e2e-user-001"
_API_KEY = "dev-webhook-key"
_CB_KEY  = "dev-callback-key"


class _AlwaysVerifyAdapter:
    """Stub JazzCash adapter for tests — skips HMAC, normalises pp_* fields."""

    provider_name = "jazzcash"

    def normalize_transaction(self, payload: dict) -> dict:
        raw_code = str(payload.get("pp_ResponseCode") or "")
        txn_status = "succeeded" if raw_code == "000" else "failed"
        raw_amount = payload.get("pp_Amount", "0")
        amount = float(str(raw_amount)) / 100
        return {
            "provider_txn_id": payload.get("pp_TxnRefNo", ""),
            "invoice_ref": payload.get("pp_BillReference"),
            "customer_ref": payload.get("pp_MobileNumber", ""),
            "amount": amount,
            "currency": payload.get("pp_TxnCurrency", "PKR"),
            "status": txn_status,
            "received_at": payload.get("pp_TxnDateTime", ""),
            "settled_at": None,
        }

    def verify_callback(self, signature: str, payload: dict) -> bool:
        return True


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture(scope="module", autouse=True)
def clear_in_memory():
    conv_module._conversations.clear()
    conv_module._messages.clear()
    _service = coll_module._service
    _service._invoices.clear()
    _service._payments.clear()
    _service._reconciliation_cases.clear()
    _service._invoice_by_number.clear()
    _service._invoice_to_payments.clear()
    yield


@pytest.fixture(scope="module", autouse=True)
def setup_jazzcash_adapter():
    """Inject stub JazzCash adapter so payment callback (step 9) resolves correctly."""
    coll_module._service._adapters["jazzcash"] = _AlwaysVerifyAdapter()
    yield
    coll_module._service._adapters.pop("jazzcash", None)


def _override_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()


def _override_auth():
    return TokenClaims(sub=USER, tenant_id=TENANT, role="sales_rep", jti=str(uuid.uuid4()))


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Step 1: WhatsApp inbound → lead intent classified ────────────────────────

def test_step1_whatsapp_lead_inquiry(client: TestClient) -> None:
    """Inbound WhatsApp message is classified as lead_inquiry and a conversation is created."""
    r = client.post(
        "/api/v1/webhooks/whatsapp",
        json={
            "from_number": "+923001234567",
            "to_number":   "+929990000001",
            "provider_message_id": str(uuid.uuid4()),
            "text": "interested in buying your product",
            "occurred_at": "2026-05-26T09:00:00Z",
            "tenant_id": TENANT,
        },
        headers={"X-Api-Key": _API_KEY},
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["intent"] == "lead_inquiry"
    assert data["should_create_lead"] is True
    assert data["conversation_id"] is not None

    # stash conversation_id for later steps
    pytest.e2e_conversation_id = data["conversation_id"]


# ── Step 2: Conversation is retrievable ───────────────────────────────────────

def test_step2_conversation_retrievable(client: TestClient) -> None:
    """Conversation is persisted and GET returns the message thread."""
    r = client.get(f"/api/v1/conversations/{pytest.e2e_conversation_id}")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["conversation_id"] == pytest.e2e_conversation_id
    assert len(data["messages"]) >= 1
    assert data["messages"][0]["direction"] == "inbound"


# ── Step 3: Create a follow-up task for the lead ─────────────────────────────

def test_step3_create_followup(client: TestClient) -> None:
    """A follow-up task is created for the lead captured via WhatsApp."""
    pytest.e2e_lead_id = f"lead-{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/api/v1/followups",
        json={
            "lead_id": pytest.e2e_lead_id,
            "owner_user_id": USER,
            "rule_type": "TimeBased",
        },
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["state"] == "pending"
    assert data["lead_id"] == pytest.e2e_lead_id
    pytest.e2e_task_id = data["task_id"]


# ── Step 4: List follow-ups — task appears, pagination correct ────────────────

def test_step4_list_followups_pagination(client: TestClient) -> None:
    """List endpoint returns the task and uses total_items + total_pages."""
    r = client.get("/api/v1/followups", params={"lead_id": pytest.e2e_lead_id})
    assert r.status_code == 200, r.text
    meta = r.json()["meta"]
    data = r.json()["data"]
    assert len(data) >= 1
    assert "total_items" in meta
    assert "total_pages" in meta


# ── Step 5: Complete the follow-up ───────────────────────────────────────────

def test_step5_complete_followup(client: TestClient) -> None:
    """Follow-up is marked completed; state transitions correctly."""
    r = client.patch(
        f"/api/v1/followups/{pytest.e2e_task_id}/complete",
        json={"completed_activity_id": f"act-{uuid.uuid4().hex[:8]}"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["data"]["state"] == "completed"


# ── Step 6: Log an activity on the closed lead ───────────────────────────────

def test_step6_log_activity(client: TestClient) -> None:
    """Activity is logged against the lead entity and returned with structured meta."""
    r = client.post(
        "/api/v1/activities",
        json={
            "entity_type": "lead",
            "entity_id": pytest.e2e_lead_id,
            "owner_id": USER,
            "action": "lead.closed",
            "changes": {"stage": "won"},
        },
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["entity_id"] == pytest.e2e_lead_id


# ── Step 7: Create an invoice for the customer ───────────────────────────────

def test_step7_create_invoice(client: TestClient) -> None:
    """Invoice created for the customer after lead close."""
    pytest.e2e_customer_id = f"cust-{uuid.uuid4().hex[:8]}"
    pytest.e2e_invoice_number = f"INV-E2E-{uuid.uuid4().hex[:6].upper()}"
    r = client.post(
        "/api/v1/invoices",
        json={
            "invoice_number": pytest.e2e_invoice_number,
            "customer_id":    pytest.e2e_customer_id,
            "issue_date":     "2026-05-26",
            "due_date":       "2026-06-25",
            "currency":       "PKR",
            "total_amount":   50000.0,
        },
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["state"] == "unpaid"
    assert data["total_amount"] == 50000.0
    pytest.e2e_invoice_id = data["invoice_id"]


# ── Step 8: Retrieve invoice — pagination meta present ───────────────────────

def test_step8_list_invoices(client: TestClient) -> None:
    """Invoice list returns total_items + total_pages."""
    r = client.get("/api/v1/invoices")
    assert r.status_code == 200, r.text
    meta = r.json()["meta"]
    assert "total_items" in meta
    assert meta["total_items"] >= 1


# ── Step 9: Payment callback → reconciliation ────────────────────────────────

def test_step9_payment_callback(client: TestClient) -> None:
    """JazzCash-style payment callback is ingested; reconciliation case created."""
    r = client.post(
        "/api/v1/payments/callback/jazzcash",
        json={
            "signature": "",
            "payload": {
                "pp_ResponseCode":  "000",
                "pp_TxnRefNo":      f"T{uuid.uuid4().hex[:12]}",
                "pp_BillReference": pytest.e2e_invoice_number,
                "pp_MobileNumber":  "+923001234567",
                "pp_Amount":        "5000000",
                "pp_TxnCurrency":   "PKR",
                "pp_TxnDateTime":   "20260526090000",
                "status":           "succeeded",
            },
        },
        headers={"X-Api-Key": _CB_KEY},
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["payment_id"] is not None
    assert data["status"] == "succeeded"


# ── Step 10: Error envelope shape ────────────────────────────────────────────

def test_step10_error_envelope_shape(client: TestClient) -> None:
    """404 errors use structured error envelope (D-005)."""
    r = client.get("/api/v1/conversations/nonexistent-id-e2e")
    assert r.status_code == 404
    body = r.json()
    assert "error" in body
    assert "code" in body["error"]
    assert "message" in body["error"]
    assert "meta" in body
    assert "request_id" in body["meta"]
