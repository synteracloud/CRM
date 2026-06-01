"""C2b — Reports contract tests."""
from __future__ import annotations


def test_reports_definitions_shape(client):
    resp = client.get("/api/v1/reports/definitions")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0


def test_reports_execute_shape(client):
    resp = client.post(
        "/api/v1/reports/execute",
        json={"report_id": "revenue_by_period", "params": {}},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code in (200, 201, 404, 422)
    body = resp.json()
    assert "data" in body or "error" in body
    if resp.status_code in (200, 201):
        data = body["data"]
        assert "series" in data or "rows" in data or "result" in data
