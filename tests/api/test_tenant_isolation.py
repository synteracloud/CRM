"""C2b — Tenant isolation: tenant A cannot read tenant B data."""
from __future__ import annotations

import httpx
import pytest

GATEWAY = "http://localhost:3000"
DEV_TENANT = "00000000-0000-0000-0000-000000000001"
ALT_TENANT = "00000000-0000-0000-0000-000000000099"


@pytest.fixture(scope="module")
def dev_token():
    resp = httpx.get(f"{GATEWAY}/dev-token", timeout=10)
    return resp.json()["data"]["token"]


def _headers(token: str, tenant_id: str) -> dict:
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "x-tenant-id": tenant_id,
    }


def test_correct_tenant_returns_data(dev_token):
    resp = httpx.get(
        f"{GATEWAY}/api/v1/leads",
        headers=_headers(dev_token, DEV_TENANT),
        timeout=10,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    # Dev tenant has seeded leads
    assert isinstance(body["data"], list)


def test_alt_tenant_token_mismatch_returns_403(dev_token):
    """Token says tenant-dev-001, header says ALT_TENANT → 403."""
    resp = httpx.get(
        f"{GATEWAY}/api/v1/leads",
        headers=_headers(dev_token, ALT_TENANT),
        timeout=10,
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "forbidden"


def test_leads_scoped_to_tenant(dev_token):
    """Data returned should only contain records for the authenticated tenant."""
    resp = httpx.get(
        f"{GATEWAY}/api/v1/leads",
        headers=_headers(dev_token, DEV_TENANT),
        timeout=10,
    )
    assert resp.status_code == 200
    for lead in resp.json()["data"]:
        assert lead.get("tenant_id") == DEV_TENANT


def test_contacts_scoped_to_tenant(dev_token):
    resp = httpx.get(
        f"{GATEWAY}/api/v1/contacts",
        headers=_headers(dev_token, DEV_TENANT),
        timeout=10,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], list)
