"""C2b/C5 — Tenant isolation: tenant A cannot read tenant B data."""
from __future__ import annotations

import os
import uuid
import httpx
import pytest

GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:3000")
_IS_PROD = "onrender.com" in GATEWAY


def _get_token_and_tenant() -> tuple[str, str]:
    if _IS_PROD:
        email = f"isolation-{uuid.uuid4().hex[:8]}@test.crm"
        resp = httpx.post(
            f"{GATEWAY}/api/v1/auth/register",
            json={"name": f"Iso-{uuid.uuid4().hex[:8]}", "email": email, "password": "IsoTest2026!"},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=30,
        )
        d = resp.json().get("data", {})
        return d["access_token"], d["tenant_id"]
    resp = httpx.get(f"{GATEWAY}/dev-token", timeout=10)
    d = resp.json()["data"]
    return d["token"], d["tenant_id"]


_module_auth: tuple[str, str] | None = None


@pytest.fixture(scope="module")
def _shared_auth():
    global _module_auth
    if _module_auth is None:
        _module_auth = _get_token_and_tenant()
    return _module_auth


@pytest.fixture(scope="module")
def dev_token(_shared_auth):
    return _shared_auth[0]


@pytest.fixture(scope="module")
def dev_tenant(_shared_auth):
    return _shared_auth[1]


def _headers(token: str, tenant_id: str) -> dict:
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "x-tenant-id": tenant_id,
    }


def test_correct_tenant_returns_data(dev_token, dev_tenant):
    resp = httpx.get(
        f"{GATEWAY}/api/v1/leads",
        headers=_headers(dev_token, dev_tenant),
        timeout=30,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert isinstance(body["data"], list)


def test_alt_tenant_token_mismatch_returns_403(dev_token):
    """Token says dev_tenant, header says a different tenant → 403."""
    ALT = "00000000-0000-0000-0000-000000000099"
    resp = httpx.get(
        f"{GATEWAY}/api/v1/leads",
        headers=_headers(dev_token, ALT),
        timeout=30,
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "forbidden"


def test_leads_scoped_to_tenant(dev_token, dev_tenant):
    resp = httpx.get(
        f"{GATEWAY}/api/v1/leads",
        headers=_headers(dev_token, dev_tenant),
        timeout=30,
    )
    assert resp.status_code == 200
    for lead in resp.json()["data"]:
        assert lead.get("tenant_id") == dev_tenant


def test_contacts_returns_data(dev_token, dev_tenant):
    resp = httpx.get(
        f"{GATEWAY}/api/v1/contacts",
        headers=_headers(dev_token, dev_tenant),
        timeout=30,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], list)
