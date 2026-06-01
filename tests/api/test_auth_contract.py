"""C2b/C5 — Auth contract tests: invalid JWT → 401, missing tenant → 403."""
from __future__ import annotations

import os
import uuid
import httpx
import pytest

GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:3000")
_IS_PROD = "onrender.com" in GATEWAY
PROBE_ROUTE = "/api/v1/leads"


def _get_valid_token() -> str:
    if _IS_PROD:
        email = f"auth-test-{uuid.uuid4().hex[:8]}@test.crm"
        resp = httpx.post(
            f"{GATEWAY}/api/v1/auth/register",
            json={"name": f"Auth-{uuid.uuid4().hex[:8]}", "email": email, "password": "AuthTest2026!"},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=30,
        )
        return resp.json()["data"]["access_token"]
    resp = httpx.get(f"{GATEWAY}/dev-token", timeout=10)
    return resp.json()["data"]["token"]


@pytest.fixture(scope="module")
def token():
    return _get_valid_token()


def test_missing_bearer_returns_401():
    resp = httpx.get(f"{GATEWAY}{PROBE_ROUTE}", headers={"Accept": "application/json"}, timeout=15)
    assert resp.status_code == 401
    body = resp.json()
    assert body["error"]["code"] == "unauthorized"
    assert "meta" in body


def test_malformed_bearer_returns_401():
    resp = httpx.get(
        f"{GATEWAY}{PROBE_ROUTE}",
        headers={"Accept": "application/json", "Authorization": "Bearer not.a.jwt"},
        timeout=15,
    )
    assert resp.status_code == 401


def test_missing_tenant_header_returns_403(token):
    resp = httpx.get(
        f"{GATEWAY}{PROBE_ROUTE}",
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
        timeout=15,
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
        timeout=15,
    )
    assert resp.status_code == 403


def test_missing_accept_header_returns_422_or_401():
    resp = httpx.get(
        f"{GATEWAY}{PROBE_ROUTE}",
        headers={"Authorization": "Bearer dummy"},
        timeout=15,
    )
    assert resp.status_code in (401, 422)
