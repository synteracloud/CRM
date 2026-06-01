"""Shared fixtures for gateway API contract tests."""
from __future__ import annotations

import os
import pytest
import httpx

GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:3000")
DEV_TENANT = "00000000-0000-0000-0000-000000000001"
ALT_TENANT = "00000000-0000-0000-0000-000000000099"


def _get_token(tenant_id: str = DEV_TENANT) -> str:
    resp = httpx.get(f"{GATEWAY}/dev-token", timeout=10)
    return resp.json()["data"]["token"]


@pytest.fixture(scope="session")
def token():
    return _get_token()


@pytest.fixture(scope="session")
def headers(token):
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "x-tenant-id": DEV_TENANT,
    }


@pytest.fixture(scope="session")
def client(headers):
    with httpx.Client(base_url=GATEWAY, headers=headers, timeout=15) as c:
        yield c
