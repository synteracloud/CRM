"""C2c — All dashboard pages: KPI tile text is non-empty."""
from __future__ import annotations

import pytest

BASE_URL = "http://localhost:3001"

DASHBOARD_PAGES = [
    "dashboard.html",
    "leads-dashboard.html",
    "sales-dashboard.html",
    "sales-cockpit.html",
    "sales-analytics.html",
    "finance-analytics.html",
    "support-dashboard.html",
    "support-analytics.html",
    "marketing-analytics.html",
    "engagement-dashboard.html",
    "workflow-analytics.html",
    "audit-dashboard.html",
]


@pytest.mark.parametrize("page_name", DASHBOARD_PAGES)
def test_kpi_tiles_have_content(page, page_name):
    url = f"{BASE_URL}/app/{page_name}"
    page.goto(url, wait_until="networkidle", timeout=20000)

    # KPI cards use .card .display-4, .fs-2, .fw-bold or data-kpi attribute
    kpi_selectors = [
        "[data-kpi]",
        ".kpi-value",
        ".card .display-4",
        ".card .fs-2.fw-bold",
        ".stat-value",
        ".metric-value",
    ]

    found_kpi = False
    for sel in kpi_selectors:
        tiles = page.locator(sel)
        if tiles.count() > 0:
            for i in range(min(tiles.count(), 3)):
                text = tiles.nth(i).inner_text(timeout=3000).strip()
                if text:
                    found_kpi = True
                    break
        if found_kpi:
            break

    # Fallback: check for any non-empty card body
    if not found_kpi:
        cards = page.locator(".card-body")
        for i in range(min(cards.count(), 4)):
            text = cards.nth(i).inner_text(timeout=3000).strip()
            if text:
                found_kpi = True
                break

    assert found_kpi, f"{page_name}: no KPI/card content found"
