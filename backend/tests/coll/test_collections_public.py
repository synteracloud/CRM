"""Integration tests for public /api/v1/invoices and /api/v1/payments/callback endpoints.

Spec: backend/docs/collections-engine-model.md
API standards: backend/docs/api-standards.md
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import services.collections.http.public as collections_module
from services.app import app
from services.auth.jwt_deps import TokenClaims, get_current_user
from services.collections.service import CollectionsService
from services.db import get_db
from services.db.base import Base
import services.db.models  # noqa: F401

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


def _override_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()

# ── Fixtures ──────────────────────────────────────────────────────────────────

TEST_TENANT = "tenant-coll-001"
_CALLBACK_KEY = "dev-callback-key"


def _override_auth():
    return TokenClaims(
        sub="user-coll-001",
        tenant_id=TEST_TENANT,
        role="sales_rep",
        jti=str(uuid.uuid4()),
    )


@pytest.fixture(autouse=True)
def fresh_service():
    """Inject a fresh CollectionsService before every test."""
    svc = CollectionsService()
    collections_module.set_service(svc)
    yield svc
    collections_module.set_service(CollectionsService())


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _invoice_payload(invoice_number: str = "INV-001") -> dict:
    return {
        "invoice_number": invoice_number,
        "customer_id": "cust-001",
        "issue_date": "2026-05-01",
        "due_date": "2026-05-31",
        "currency": "PKR",
        "total_amount": 50000.00,
    }


# ── POST /api/v1/invoices ─────────────────────────────────────────────────────


class TestCreateInvoice:
    def test_create_returns_201_with_envelope(self, client: TestClient) -> None:
        r = client.post("/api/v1/invoices", json=_invoice_payload())
        assert r.status_code == 201
        body = r.json()
        assert "data" in body
        assert "meta" in body

    def test_create_stores_invoice_fields(self, client: TestClient) -> None:
        r = client.post("/api/v1/invoices", json=_invoice_payload("INV-XYZ"))
        data = r.json()["data"]
        assert data["invoice_number"] == "INV-XYZ"
        assert data["total_amount"] == 50000.00
        assert data["currency"] == "PKR"
        assert data["state"] == "unpaid"

    def test_create_duplicate_invoice_number_returns_409(self, client: TestClient) -> None:
        client.post("/api/v1/invoices", json=_invoice_payload("INV-DUP"))
        r = client.post("/api/v1/invoices", json=_invoice_payload("INV-DUP"))
        assert r.status_code == 409

    def test_create_sets_outstanding_equal_to_total(self, client: TestClient) -> None:
        r = client.post("/api/v1/invoices", json=_invoice_payload())
        data = r.json()["data"]
        assert data["amount_outstanding"] == data["total_amount"]
        assert data["amount_paid"] == 0.0


# ── GET /api/v1/invoices ──────────────────────────────────────────────────────


class TestListInvoices:
    def test_empty_list_returns_200(self, client: TestClient) -> None:
        r = client.get("/api/v1/invoices")
        assert r.status_code == 200
        assert r.json()["data"] == []

    def test_list_returns_created_invoices(self, client: TestClient) -> None:
        client.post("/api/v1/invoices", json=_invoice_payload("INV-A"))
        client.post("/api/v1/invoices", json=_invoice_payload("INV-B"))
        r = client.get("/api/v1/invoices")
        assert r.status_code == 200
        assert len(r.json()["data"]) == 2

    def test_meta_contains_total(self, client: TestClient) -> None:
        client.post("/api/v1/invoices", json=_invoice_payload())
        r = client.get("/api/v1/invoices")
        assert "total" in r.json()["meta"]


# ── GET /api/v1/invoices/{id} ─────────────────────────────────────────────────


class TestGetInvoice:
    def test_get_returns_invoice(self, client: TestClient) -> None:
        invoice_id = client.post("/api/v1/invoices", json=_invoice_payload()).json()["data"]["invoice_id"]
        r = client.get(f"/api/v1/invoices/{invoice_id}")
        assert r.status_code == 200
        assert r.json()["data"]["invoice_id"] == invoice_id

    def test_get_unknown_returns_404(self, client: TestClient) -> None:
        r = client.get("/api/v1/invoices/inv-does-not-exist")
        assert r.status_code == 404


# ── POST /api/v1/payments/callback/{provider} ────────────────────────────────


class _MockAdapter:
    """Test-only JazzCash adapter — always validates, passes payload through."""
    provider_name = "jazzcash"

    def verify_callback(self, signature: str, payload: dict) -> bool:
        return True

    def normalize_transaction(self, payload: dict) -> dict:
        return payload


class TestSendInvoice:
    def test_send_returns_200_with_action_sent(self, client: TestClient) -> None:
        invoice_id = client.post("/api/v1/invoices", json=_invoice_payload()).json()["data"]["invoice_id"]
        r = client.post(f"/api/v1/invoices/{invoice_id}/send")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["invoice_id"] == invoice_id
        assert data["action"] == "sent"

    def test_send_returns_scheduled_reminders(self, client: TestClient) -> None:
        invoice_id = client.post("/api/v1/invoices", json=_invoice_payload("INV-SEND")).json()["data"]["invoice_id"]
        r = client.post(f"/api/v1/invoices/{invoice_id}/send")
        assert r.status_code == 200
        reminders = r.json()["data"]["reminders_scheduled"]
        assert isinstance(reminders, list)
        assert len(reminders) > 0

    def test_send_unknown_invoice_returns_404(self, client: TestClient) -> None:
        r = client.post("/api/v1/invoices/inv-does-not-exist/send")
        assert r.status_code == 404


class TestTenantIsolation:
    def test_list_excludes_other_tenant_invoices(
        self, client: TestClient, fresh_service: CollectionsService
    ) -> None:
        from services.collections.entities import Invoice
        other = Invoice(
            invoice_id="inv-other-001",
            invoice_number="INV-OTHER",
            customer_id="cust-other",
            issue_date="2026-05-01",
            due_date="2026-05-31",
            currency="PKR",
            total_amount=9999.0,
            tenant_id="other-tenant-xyz",
        )
        fresh_service._invoices[other.invoice_id] = other
        fresh_service._invoice_by_number[other.invoice_number] = other.invoice_id
        r = client.get("/api/v1/invoices")
        assert r.status_code == 200
        assert r.json()["data"] == []

    def test_create_stamps_tenant_id(self, client: TestClient) -> None:
        r = client.post("/api/v1/invoices", json=_invoice_payload("INV-TENANT"))
        assert r.status_code == 201
        assert r.json()["data"]["tenant_id"] == TEST_TENANT


class TestPaymentCallback:
    def test_unknown_provider_returns_422(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/payments/callback/unknown_provider",
            json={"signature": "sig", "payload": {}},
            headers={"X-Api-Key": _CALLBACK_KEY},
        )
        assert r.status_code == 422

    def test_missing_callback_key_returns_401(self, client: TestClient, fresh_service: CollectionsService) -> None:
        r = client.post(
            "/api/v1/payments/callback/jazzcash",
            json={"payload": {}},
        )
        assert r.status_code == 401

    def test_registered_provider_processes_payment(
        self, client: TestClient, fresh_service: CollectionsService
    ) -> None:
        fresh_service._adapters["jazzcash"] = _MockAdapter()
        normalized_payload = {
            "provider_txn_id": "txn-001",
            "customer_ref": "cust-001",
            "amount": 25000.0,
            "currency": "PKR",
            "status": "succeeded",
            "received_at": "2026-05-18T10:00:00Z",
        }
        r = client.post(
            "/api/v1/payments/callback/jazzcash",
            json={"signature": "valid", "payload": normalized_payload},
            headers={"X-Api-Key": _CALLBACK_KEY},
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["provider"] == "jazzcash"
        assert data["amount"] == 25000.0
