"""C2b — Billing contract tests."""
from __future__ import annotations


def test_billing_plans_shape(client):
    resp = client.get("/api/v1/billing/plans")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0
    plan = body["data"][0]
    for field in ("plan_code", "label"):
        assert field in plan, f"billing/plans: missing field '{field}'"


def test_billing_subscription_shape(client):
    resp = client.get("/api/v1/billing/subscription")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], dict)
    for field in ("plan_code",):
        assert field in body["data"], f"billing/subscription: missing '{field}'"
