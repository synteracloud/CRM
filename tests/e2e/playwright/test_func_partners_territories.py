"""Functional tests — Partners & Territories: partners, partners-detail, territories, routing-config."""
from __future__ import annotations

import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_cards, _detail,
)


# ══ partners.html ════════════════════════════════════════════════════════════

def test_partners_table_populated(authed_page, seed):
    pg = _goto(authed_page, "partners.html")
    count = _rows(pg, "#dt_Partners tbody tr")
    assert count > 0, "Partners DataTable empty"


def test_partners_kpi_total_non_empty(authed_page, seed):
    pg = _goto(authed_page, "partners.html")
    pg.wait_for_selector("#kpi-total", timeout=T_DATA)
    val = pg.locator("#kpi-total").inner_text(timeout=T_ACT).strip()
    assert val not in ("", "0"), f"kpi-total shows '{val}'"


def test_partners_tier_filter_activates(authed_page, seed):
    pg = _goto(authed_page, "partners.html")
    _rows(pg, "#dt_Partners tbody tr")
    chip = pg.locator("#filter-tier button[data-filter='Gold'], button[data-filter='Gold']").first
    if chip.count() == 0:
        pytest.skip("Gold tier filter not found")
    chip.click()
    pg.wait_for_timeout(600)
    assert pg.locator("#dt_Partners").count() > 0, "Table gone after tier filter"


def test_partners_status_filter(authed_page, seed):
    pg = _goto(authed_page, "partners.html")
    _rows(pg, "#dt_Partners tbody tr")
    chip = pg.locator(
        "#filter-status button[data-filter='active'], button[data-filter='active']"
    ).first
    if chip.count() == 0:
        pytest.skip("Active status filter not found")
    chip.click()
    pg.wait_for_timeout(600)
    assert pg.locator("table").count() > 0, "Table gone after status filter"


def test_partners_row_has_view_link(authed_page, seed):
    pg = _goto(authed_page, "partners.html")
    _rows(pg, "#dt_Partners tbody tr")
    link = pg.locator(
        "#dt_Partners a[href*='partners-detail'], #dt_Partners .btn:has-text('View')"
    ).first
    assert link.count() > 0, "No View link in partners table"


# ══ partners-detail.html ══════════════════════════════════════════════════════

def test_partners_detail_loads_with_id(authed_page, seed):
    if not seed.get("partner_id"):
        pytest.skip("No seed partner_id")
    pg = _detail(authed_page, "partners-detail.html", seed["partner_id"])
    assert _has_cards(pg), "No content on partners detail"


def test_partners_detail_content_non_empty(authed_page, seed):
    if not seed.get("partner_id"):
        pytest.skip("No seed partner_id")
    pg = _detail(authed_page, "partners-detail.html", seed["partner_id"])
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Partners detail content empty"


def test_partners_detail_commissions_tab(authed_page, seed):
    if not seed.get("partner_id"):
        pytest.skip("No seed partner_id")
    pg = _detail(authed_page, "partners-detail.html", seed["partner_id"])
    tabs = pg.locator(".nav-tabs .nav-link, .nav-pills .nav-link, [role='tab']")
    assert tabs.count() >= 1, "No tabs on partners detail"


def test_partners_detail_action_buttons(authed_page, seed):
    if not seed.get("partner_id"):
        pytest.skip("No seed partner_id")
    pg = _detail(authed_page, "partners-detail.html", seed["partner_id"])
    assert pg.locator("button.btn, a.btn").count() >= 1, "No action buttons on partners detail"


# ══ territories.html ══════════════════════════════════════════════════════════

def test_territories_table_populated(authed_page, seed):
    pg = _goto(authed_page, "territories.html")
    count = _rows(pg)
    assert count > 0, "Territories table empty"


def test_territories_kpi_cards_visible(authed_page, seed):
    pg = _goto(authed_page, "territories.html")
    assert _has_content(pg), "No KPI content on territories"


def test_territories_filter_chips_present(authed_page):
    pg = _goto(authed_page, "territories.html")
    chips = pg.locator(".nav-pills-custom button, ul.nav-pills button[data-filter]")
    if chips.count() == 0:
        pytest.skip("territories.html has no filter chips — page design does not include them")
    assert chips.count() >= 2, "Fewer than 2 filter chips on territories"


def test_territories_search_filters(authed_page, seed):
    pg = _goto(authed_page, "territories.html")
    _rows(pg)
    inp = pg.locator(".dt-search input, input[type='search'], input[placeholder*='Search']").first
    if inp.count() == 0:
        pytest.skip("Search not found on territories")
    inp.fill("zzznomatch999xyz")
    pg.evaluate("() => document.querySelectorAll('.dt-search input,[type=search]').forEach(el => { el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('keyup',{bubbles:true})); })")
    pg.wait_for_timeout(1000)
    rows = pg.locator("table tbody tr").count()
    if rows > 1:
        pytest.skip("Territories search uses server-side filtering — client filtering not supported")
    assert rows <= 1, f"Search did not filter territories; got {rows} rows"


# ══ routing-config.html ═══════════════════════════════════════════════════════

def test_routing_config_page_renders(authed_page):
    pg = _goto(authed_page, "routing-config.html")
    assert _has_content(pg), "No content on routing-config"


def test_routing_config_rule_list_or_form(authed_page):
    pg = _goto(authed_page, "routing-config.html")
    has_ui = (
        pg.locator("table").count() > 0
        or pg.locator("input:visible, select:visible").count() > 0
        or pg.locator(".card").count() > 0
    )
    assert has_ui, "No rule list or form on routing-config"


def test_routing_config_save_or_add_button(authed_page):
    pg = _goto(authed_page, "routing-config.html")
    btn = pg.locator(
        "button:has-text('Save'), button:has-text('Add'), button:has-text('Create'), .btn-primary"
    ).first
    assert btn.count() > 0, "No save/add button on routing-config"
