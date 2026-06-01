"""C2c/C5 — Filter pill click changes visible row count or active state."""
from __future__ import annotations

import pytest

import os; BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")

FILTER_PAGES = [
    ("followups.html", ".nav-pills-custom button, .nav-pills button"),
    ("leads.html", ".nav-pills-custom button, .nav-pills button"),
    ("cases.html", ".nav-pills-custom button, .nav-pills button"),
]


@pytest.mark.parametrize("page_name,pill_selector", FILTER_PAGES)
def test_filter_chip_clickable(page, page_name, pill_selector):
    url = f"{BASE_URL}/app/{page_name}"
    page.goto(url, wait_until="networkidle", timeout=30000)

    pills = page.locator(pill_selector)
    if pills.count() < 2:
        pytest.skip(f"{page_name}: fewer than 2 filter pills found")

    # Click the second pill (first non-"All")
    second_pill = pills.nth(1)
    second_pill.click()
    # Longer wait on production (CDN latency + JS initialization)
    page.wait_for_timeout(2000)

    # After click, the pill should have 'active' class or aria-selected
    active = second_pill.get_attribute("class") or ""
    aria = second_pill.get_attribute("aria-selected") or ""
    # Also accept if the URL hash changed (some implementations use that)
    if "active" not in active and aria != "true":
        # One more try with explicit wait for class change
        try:
            page.locator(f"{pill_selector}.active").first.wait_for(timeout=3000)
            active = second_pill.get_attribute("class") or ""
        except Exception:
            pass
    assert "active" in active or aria == "true", (
        f"{page_name}: pill did not become active after click (class='{active}')"
    )
