"""Functional tests — Account Management: accounts, accounts-detail."""
from __future__ import annotations

import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_cards, _detail,
)


# ══ accounts.html ═════════════════════════════════════════════════════════════

def test_accounts_table_populated_from_api(authed_page, seed):
    pg = _goto(authed_page, "accounts.html")
    count = _rows(pg)
    assert count > 0, "Accounts table empty — API may have returned 401"


def test_accounts_kpi_cards_have_content(authed_page, seed):
    pg = _goto(authed_page, "accounts.html")
    assert _has_content(pg), "No KPI content on accounts page"


def test_accounts_search_filters_rows(authed_page, seed):
    pg = _goto(authed_page, "accounts.html")
    _rows(pg)
    inp = pg.locator(
        ".dt-search input, input[type='search'], input[placeholder*='Search']"
    ).first
    if inp.count() == 0:
        pytest.skip("Search input not found on accounts")
    inp.fill("zzznomatch999xyz")
    pg.wait_for_timeout(700)
    rows = pg.locator("table tbody tr").count()
    assert rows <= 1, f"Search did not filter accounts; got {rows} rows"


def test_accounts_filter_chips_present(authed_page, seed):
    pg = _goto(authed_page, "accounts.html")
    chips = pg.locator(
        ".nav-pills-custom button, ul.nav-pills button[data-filter], .btn-group button[data-filter]"
    )
    assert chips.count() >= 2, "No filter chips on accounts page"


def test_accounts_row_has_action_or_link(authed_page, seed):
    pg = _goto(authed_page, "accounts.html")
    _rows(pg)
    action = pg.locator(
        "table tbody a[href*='accounts-detail'], table tbody .btn"
    ).first
    assert action.count() > 0, "No action link/button in accounts table rows"


# ══ accounts-detail.html ══════════════════════════════════════════════════════

def test_accounts_detail_loads_with_id(authed_page, seed):
    acct_id = seed.get("account_id")
    if not acct_id:
        pytest.skip("No seed account_id (no accounts in DB)")
    pg = _detail(authed_page, "accounts-detail.html", acct_id)
    assert _has_cards(pg), "No content cards on account detail"


def test_accounts_detail_has_content(authed_page, seed):
    acct_id = seed.get("account_id")
    if not acct_id:
        pytest.skip("No seed account_id")
    pg = _detail(authed_page, "accounts-detail.html", acct_id)
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Account detail content area appears empty"


def test_accounts_detail_tabs_or_sections_present(authed_page, seed):
    acct_id = seed.get("account_id")
    if not acct_id:
        pytest.skip("No seed account_id")
    pg = _detail(authed_page, "accounts-detail.html", acct_id)
    tabs = pg.locator(".nav-tabs .nav-link, .nav-pills .nav-link, [role='tab']")
    assert tabs.count() >= 1, "No tabs or nav sections on account detail"
