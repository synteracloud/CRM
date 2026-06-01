"""C2b — Integrations contract tests."""
from __future__ import annotations


def test_integrations_list_shape(client):
    resp = client.get("/api/v1/integrations")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0
    item = body["data"][0]
    for field in ("provider",):
        assert field in item, f"integrations: missing field '{field}'"


def test_integrations_test_endpoint(client):
    resp = client.post(
        "/api/v1/integrations/whatsapp/test",
        json={},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code in (200, 201, 422, 503)
    body = resp.json()
    assert "data" in body or "error" in body
