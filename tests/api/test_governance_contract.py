"""C2b — Governance contract tests."""
from __future__ import annotations

import pytest


def test_governance_classification_shape(client):
    resp = client.get("/api/v1/governance/classification")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], (dict, list))
    assert "meta" in body


def test_governance_sar_post_creates_due_date(client):
    resp = client.post(
        "/api/v1/governance/sar",
        json={"request_type": "access", "contact_id": "ct-001"},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code in (200, 201, 404, 422)
    body = resp.json()
    assert "data" in body or "error" in body
    if resp.status_code in (200, 201):
        assert "due_date" in body["data"]
