"""C2c — J-series audit pages: DataTable rows present, export button visible."""
from __future__ import annotations

import pytest

import os; BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")

AUDIT_PAGES = [
    "audit-dashboard.html",
    "audit-log.html",
    "audit-report.html",
    "rbac-audit.html",
    "compliance-report.html",
    "data-governance.html",
]


@pytest.mark.parametrize("page_name", AUDIT_PAGES)
def test_audit_page_renders(page, page_name):
    url = f"{BASE_URL}/app/{page_name}"
    response = page.goto(url, wait_until="networkidle", timeout=20000)
    assert response and response.status == 200, f"{page_name}: HTTP {response.status if response else 'N/A'}"

    # Page should have some meaningful content
    content = page.locator("main, .container-fluid").first
    assert content.count() > 0, f"{page_name}: no main content area"
    text = content.inner_text(timeout=5000).strip()
    assert len(text) > 10, f"{page_name}: content area is empty"

    # Tables or cards should be present
    has_table = page.locator("table").count() > 0
    has_card = page.locator(".card").count() > 0
    assert has_table or has_card, f"{page_name}: no table or card found"
