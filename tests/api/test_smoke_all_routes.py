"""C2b — Smoke test: all gateway routes return HTTP 200 with valid envelope.

Gate: 0 failures. All routes respond with {data: ..., meta: {request_id: ...}}.
"""
from __future__ import annotations

import pytest
import httpx

GATEWAY_ROUTES = [
    "/api/v1/leads",
    "/api/v1/contacts",
    "/api/v1/accounts",
    "/api/v1/opportunities",
    "/api/v1/followups",
    "/api/v1/tasks",
    "/api/v1/activities",
    "/api/v1/payments",
    "/api/v1/subscriptions",
    "/api/v1/invoice-summaries",
    "/api/v1/collections/invoices",
    "/api/v1/collections/subscriptions",
    "/api/v1/collections/overdue",
    "/api/v1/users",
    "/api/v1/roles",
    "/api/v1/feature-flags",
    "/api/v1/tenants/current",
    "/api/v1/audits/events",
    "/api/v1/org/settings",
    "/api/v1/reports/definitions",
    "/api/v1/billing/plans",
    "/api/v1/billing/subscription",
    "/api/v1/integrations",
    "/api/v1/governance/classification",
    "/api/v1/communications/engagement",
    "/api/v1/compliance/settings",
    "/api/v1/privacy/consent",
    "/api/v1/price-books",
    "/api/v1/quotes",
    "/api/v1/orders",
    "/api/v1/emails",
    "/api/v1/forecasts",
    "/api/v1/sync/status",
    "/api/v1/notification-preferences",
    "/api/v1/territories",
    "/api/v1/campaigns",
    "/api/v1/partners",
    "/api/v1/workflows",
    "/api/v1/segments",
    "/api/v1/templates",
    "/api/v1/cases",
    "/api/v1/knowledge/articles",
    "/api/v1/inbox/conversations",
    "/api/v1/ai/scores/leads",
]


@pytest.mark.parametrize("route", GATEWAY_ROUTES)
def test_route_returns_200_with_envelope(client, route):
    resp = client.get(route)
    assert resp.status_code == 200, f"{route} → {resp.status_code}: {resp.text[:200]}"
    body = resp.json()
    assert "data" in body, f"{route}: missing 'data' key in response"
    assert "meta" in body, f"{route}: missing 'meta' key in response"
    assert "request_id" in body["meta"], f"{route}: missing meta.request_id"


def test_route_count():
    """Verify we cover the minimum required route count."""
    assert len(GATEWAY_ROUTES) >= 42
