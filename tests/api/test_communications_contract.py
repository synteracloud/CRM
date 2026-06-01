"""C2b — Communications contract tests."""
from __future__ import annotations

REQUIRED_ENGAGEMENT_FIELDS = {
    "delivery_rate", "open_rate", "reply_rate", "failed_delivery_count",
}


def test_communications_engagement_shape(client):
    resp = client.get("/api/v1/communications/engagement")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], dict)
    for field in REQUIRED_ENGAGEMENT_FIELDS:
        assert field in body["data"], f"communications/engagement: missing field '{field}'"
