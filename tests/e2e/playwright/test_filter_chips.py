"""C2c — Filter pill click changes visible row count or active state."""
from __future__ import annotations

import pytest

BASE_URL = "http://localhost:3001"

FILTER_PAGES = [
    ("followups.html", ".nav-pills-custom button, .nav-pills button"),
    ("leads.html", ".nav-pills-custom button, .nav-pills button"),
    ("cases.html", ".nav-pills-custom button, .nav-pills button"),
]


@pytest.mark.parametrize("page_name,pill_selector", FILTER_PAGES)
def test_filter_chip_clickable(page, page_name, pill_selector):
    url = f"{BASE_URL}/app/{page_name}"
    page.goto(url, wait_until="networkidle", timeout=20000)

    pills = page.locator(pill_selector)
    if pills.count() < 2:
        pytest.skip(f"{page_name}: fewer than 2 filter pills found")

    # Click the second pill (first non-"All")
    second_pill = pills.nth(1)
    second_pill.click()
    page.wait_for_timeout(500)

    # After click, the pill should have 'active' class or aria-selected
    active = second_pill.get_attribute("class") or ""
    assert "active" in active or second_pill.get_attribute("aria-selected") == "true", (
        f"{page_name}: pill did not become active after click"
    )
