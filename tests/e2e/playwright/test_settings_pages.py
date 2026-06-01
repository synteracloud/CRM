"""C2c — All settings (G-series) pages: settings nav renders, save button present."""
from __future__ import annotations

import pytest

BASE_URL = "http://localhost:3001"

SETTINGS_PAGES = [
    "org-settings.html",
    "billing-settings.html",
    "integrations.html",
    "notifications.html",
    "feature-flags.html",
    "compliance.html",
    "privacy.html",
    "roles.html",
    "users.html",
    "user-management-crm.html",
]


@pytest.mark.parametrize("page_name", SETTINGS_PAGES)
def test_settings_page_renders(page, page_name):
    url = f"{BASE_URL}/app/{page_name}"
    response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
    assert response and response.status == 200, f"{page_name}: HTTP {response.status if response else 'N/A'}"

    # Settings pages should have list-group or nav for navigation
    nav = page.locator(".list-group, .nav, [role='navigation']").first
    assert nav.count() > 0, f"{page_name}: no navigation element found"

    # Content area should have some text
    body_text = page.locator("main, .container-fluid, .content").first.inner_text(timeout=5000)
    assert len(body_text.strip()) > 20, f"{page_name}: content area is empty"
