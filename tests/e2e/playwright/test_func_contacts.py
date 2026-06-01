"""Functional tests — Contacts: contacts, contacts-detail, contacts-health, contact-new."""
from __future__ import annotations

import time
import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_cards, _has_heading, _detail,
)


# ══ contacts.html ═════════════════════════════════════════════════════════════

def test_contacts_table_populated_from_api(authed_page, seed):
    pg = _goto(authed_page, "contacts.html")
    count = _rows(pg, "#dt_Contacts tbody tr")
    assert count > 0, "Contacts DataTable empty — API likely returned 401"


def test_contacts_kpi_total_non_empty(authed_page, seed):
    pg = _goto(authed_page, "contacts.html")
    pg.wait_for_selector("#kpi-total-contacts", timeout=T_DATA)
    val = pg.locator("#kpi-total-contacts").inner_text(timeout=T_ACT).strip()
    assert val not in ("", "0"), f"kpi-total-contacts shows '{val}'"


def test_contacts_search_produces_empty_state(authed_page, seed):
    pg = _goto(authed_page, "contacts.html")
    _rows(pg, "#dt_Contacts tbody tr")
    inp = pg.locator(
        "#dt_Contacts_wrapper .dt-search input, input[placeholder*='Search contacts']"
    ).first
    if inp.count() == 0:
        pytest.skip("Contacts search input not found")
    inp.fill("zzznomatch999xyz")
    pg.wait_for_timeout(700)
    rows = pg.locator("#dt_Contacts tbody tr").count()
    assert rows <= 1, f"Expected empty state, got {rows} rows"


def test_contacts_search_restores_on_clear(authed_page, seed):
    pg = _goto(authed_page, "contacts.html")
    initial = _rows(pg, "#dt_Contacts tbody tr")
    inp = pg.locator(
        "#dt_Contacts_wrapper .dt-search input, input[placeholder*='Search contacts']"
    ).first
    if inp.count() == 0:
        pytest.skip("Search input not found")
    inp.fill("zzznomatch999xyz")
    pg.wait_for_timeout(700)
    inp.fill("")
    pg.wait_for_timeout(700)
    restored = pg.locator("#dt_Contacts tbody tr").count()
    assert restored >= initial, "Row count did not restore after clearing search"


def test_contacts_row_has_open_detail_link(authed_page, seed):
    pg = _goto(authed_page, "contacts.html")
    _rows(pg, "#dt_Contacts tbody tr")
    detail_link = pg.locator(
        "#dt_Contacts a[href*='contacts-detail'], #dt_Contacts .btn:has-text('View')"
    ).first
    assert detail_link.count() > 0, "No detail link in contacts table rows"


# ══ contacts-detail.html ══════════════════════════════════════════════════════

def test_contacts_detail_loads_with_id(authed_page, seed):
    if not seed.get("contact_id"):
        pytest.skip("No seed contact_id")
    pg = _detail(authed_page, "contacts-detail.html", seed["contact_id"])
    assert _has_cards(pg), "No content on contacts detail page"


def test_contacts_detail_has_contact_fields(authed_page, seed):
    if not seed.get("contact_id"):
        pytest.skip("No seed contact_id")
    pg = _detail(authed_page, "contacts-detail.html", seed["contact_id"])
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Contacts detail content area empty"


def test_contacts_detail_action_buttons_visible(authed_page, seed):
    if not seed.get("contact_id"):
        pytest.skip("No seed contact_id")
    pg = _detail(authed_page, "contacts-detail.html", seed["contact_id"])
    assert pg.locator("button.btn, a.btn").count() >= 1, "No action buttons on contact detail"


def test_contacts_detail_tabs_present(authed_page, seed):
    if not seed.get("contact_id"):
        pytest.skip("No seed contact_id")
    pg = _detail(authed_page, "contacts-detail.html", seed["contact_id"])
    tabs = pg.locator(".nav-tabs .nav-link, .nav-pills .nav-link, [role='tab']")
    assert tabs.count() >= 2, "Expected at least 2 tabs on contact detail"


# ══ contacts-health.html ══════════════════════════════════════════════════════

def test_contacts_health_page_loads(authed_page):
    pg = _goto(authed_page, "contacts-health.html")
    assert _has_content(pg), "No content on contacts-health page"


def test_contacts_health_metric_cards_present(authed_page):
    pg = _goto(authed_page, "contacts-health.html")
    assert _has_cards(pg, 2), "Fewer than 2 metric cards on contacts health"


def test_contacts_health_has_table_or_chart(authed_page):
    from helpers import _has_chart, _has_table
    pg = _goto(authed_page, "contacts-health.html")
    assert _has_table(pg) or _has_chart(pg), "Neither table nor chart found on contacts health"


# ══ contact-new.html ══════════════════════════════════════════════════════════

def test_contact_new_required_field_validation(authed_page):
    pg = _goto(authed_page, "contact-new.html")
    pg.locator("#c-first-name").wait_for(state="attached", timeout=T_DATA)
    pg.locator("#btn-next").click(force=True)
    pg.wait_for_timeout(600)
    assert pg.locator(".is-invalid").count() > 0, \
        "No is-invalid on empty contact form step 1"


def test_contact_new_form_fields_present(authed_page):
    pg = _goto(authed_page, "contact-new.html")
    pg.locator("#c-first-name").wait_for(state="attached", timeout=T_DATA)
    assert pg.locator("#c-first-name, #c-last-name, #c-phone").count() == 3, \
        "Expected #c-first-name, #c-last-name, #c-phone on contact-new"


def test_contact_new_submit_creates_contact(authed_page):
    pg = _goto(authed_page, "contact-new.html")
    pg.locator("#c-first-name").wait_for(state="attached", timeout=T_DATA)
    ts = str(int(time.time()))[-6:]
    pg.locator("#c-first-name").fill("FuncNew", force=True)
    pg.locator("#c-last-name").fill(f"Contact{ts}", force=True)
    pg.locator("#c-phone").fill(f"+9230077{ts}", force=True)
    pg.locator("#btn-next").click(force=True)
    pg.wait_for_timeout(1000)
    pg.locator("#btn-submit").click(force=True)
    pg.wait_for_timeout(T_DATA)
    has_success = (
        pg.locator("#wizard-success").count() > 0
        or "contacts" in pg.url
    )
    assert has_success, "Contact form did not reach success state"
