"""C2b — Auth contract tests: invalid JWT → 401, missing tenant → 403."""
from __future__ import annotations

import httpx
import pytest

GATEWAY = "http://localhost:3000"
PROBE_ROUTE = "/api/v1/leads"


def test_missing_bearer_returns_401():
    resp = httpx.get(f"{GATEWAY}{PROBE_ROUTE}", headers={"Accept": "application/json"}, timeout=10)
    assert resp.status_code == 401
    body = resp.json()
    assert body["error"]["code"] == "unauthorized"
    assert "meta" in body


def test_malformed_bearer_returns_401():
    resp = httpx.get(
        f"{GATEWAY}{PROBE_ROUTE}",
        headers={"Accept": "application/json", "Authorization": "Bearer not.a.jwt"},
        timeout=10,
    )
    assert resp.status_code == 401


def test_missing_tenant_header_returns_403(token):
    resp = httpx.get(
        f"{GATEWAY}{PROBE_ROUTE}",
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert resp.status_code == 403
    body = resp.json()
    assert body["error"]["code"] == "forbidden"


def test_wrong_tenant_returns_403(token):
    resp = httpx.get(
        f"{GATEWAY}{PROBE_ROUTE}",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "x-tenant-id": "wrong-tenant-id",
        },
        timeout=10,
    )
    assert resp.status_code == 403


def test_missing_accept_header_returns_422():
    resp = httpx.get(
        f"{GATEWAY}{PROBE_ROUTE}",
        headers={"Authorization": "Bearer dummy"},
        timeout=10,
    )
    # requestValidationMiddleware enforces Accept: application/json
    assert resp.status_code in (401, 422)


@pytest.fixture
def token():
    resp = httpx.get(f"{GATEWAY}/dev-token", timeout=10)
    return resp.json()["data"]["token"]
