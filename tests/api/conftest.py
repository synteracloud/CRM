"""Shared fixtures for gateway API contract tests.

Supports both local dev (uses /dev-token) and production (uses /auth/register).
Set GATEWAY_URL env var to point at production: https://crm-gateway-l3rm.onrender.com
"""
from __future__ import annotations

import os
import uuid
import pytest
import httpx

GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:3000")
_IS_PROD = "onrender.com" in GATEWAY or os.getenv("CI_PROD_TEST", "") == "1"

# For tenant isolation tests — a second tenant that does NOT match the token
ALT_TENANT = "00000000-0000-0000-0000-000000000099"


def _wake_gateway() -> None:
    """Ping /health until the gateway responds (free tier may sleep)."""
    for attempt in range(8):
        try:
            r = httpx.get(f"{GATEWAY}/health", timeout=45)
            if r.status_code == 200:
                return
        except Exception:
            pass
        import time; time.sleep(5)
    raise RuntimeError(f"Gateway at {GATEWAY} did not respond after warm-up")


def _get_auth() -> tuple[str, str]:
    """Return (token, tenant_id) — works for both local dev and production."""
    _wake_gateway()
    if _IS_PROD:
        # Production: register a fresh tenant each session (unique name AND email to avoid slug conflicts)
        uid = uuid.uuid4().hex[:10]
        email = f"c5-{uid}@smoke.test"
        name  = f"C5-{uid}"   # unique slug per test run
        for attempt in range(3):
            try:
                resp = httpx.post(
                    f"{GATEWAY}/api/v1/auth/register",
                    json={"name": name, "email": email, "password": "C5SmokeTest2026!"},
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    timeout=60,
                )
                data = resp.json().get("data", {})
                if "access_token" in data:
                    return data["access_token"], data["tenant_id"]
            except Exception:
                pass
            import time; time.sleep(10)
        raise RuntimeError("Failed to register test user in production after 3 attempts")
    else:
        # Local dev: use /dev-token
        resp = httpx.get(f"{GATEWAY}/dev-token", timeout=10)
        data = resp.json()["data"]
        return data["token"], data["tenant_id"]


@pytest.fixture(scope="session")
def auth():
    return _get_auth()


@pytest.fixture(scope="session")
def token(auth):
    return auth[0]


@pytest.fixture(scope="session")
def tenant_id(auth):
    return auth[1]


@pytest.fixture(scope="session")
def headers(token, tenant_id):
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "x-tenant-id": tenant_id,
    }


@pytest.fixture(scope="session")
def client(headers):
    with httpx.Client(base_url=GATEWAY, headers=headers, timeout=30) as c:
        yield c
