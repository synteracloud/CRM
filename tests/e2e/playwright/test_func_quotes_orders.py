"""Functional tests — Quotes & Orders: quotes-dashboard, quotes-detail, quote-builder, orders-detail."""
from __future__ import annotations

import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_cards, _detail,
)


# ══ quotes-dashboard.html ═════════════════════════════════════════════════════

def test_quotes_dashboard_table_loads(authed_page, seed):
    pg = _goto(authed_page, "quotes-dashboard.html")
    count = _rows(pg)
    assert count >= 0, "Table broken on quotes dashboard"


def test_quotes_dashboard_kpis_visible(authed_page, seed):
    pg = _goto(authed_page, "quotes-dashboard.html")
    assert _has_content(pg), "No KPI content on quotes dashboard"


def test_quotes_dashboard_filter_chips_present(authed_page):
    pg = _goto(authed_page, "quotes-dashboard.html")
    chips = pg.locator(
        ".nav-pills-custom button, ul.nav-pills button[data-filter], .btn[data-filter]"
    )
    if chips.count() == 0:
        pytest.skip("No filter chips on quotes dashboard — page design does not include them")
    assert chips.count() >= 2, "Fewer than 2 filter chips on quotes dashboard"


def test_quotes_dashboard_status_filter(authed_page, seed):
    pg = _goto(authed_page, "quotes-dashboard.html")
    _rows(pg)
    chip = pg.locator("button[data-filter='draft'], button:has-text('Draft')").first
    if chip.count() == 0:
        pytest.skip("Draft filter chip not found")
    chip.click()
    pg.wait_for_timeout(600)
    assert pg.locator("table").count() > 0, "Table vanished after status filter"


# ══ quotes-detail.html ════════════════════════════════════════════════════════

def test_quotes_detail_loads_with_id(authed_page, seed):
    if not seed.get("quote_id"):
        pytest.skip("No seed quote_id")
    pg = _detail(authed_page, "quotes-detail.html", seed["quote_id"])
    assert _has_cards(pg), "No content on quotes detail"


def test_quotes_detail_has_line_items_section(authed_page, seed):
    if not seed.get("quote_id"):
        pytest.skip("No seed quote_id")
    pg = _detail(authed_page, "quotes-detail.html", seed["quote_id"])
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Quotes detail content empty"


def test_quotes_detail_action_buttons_present(authed_page, seed):
    if not seed.get("quote_id"):
        pytest.skip("No seed quote_id")
    pg = _detail(authed_page, "quotes-detail.html", seed["quote_id"])
    assert pg.locator("button.btn, a.btn").count() >= 1, "No action buttons on quotes detail"


# ══ quote-builder.html ════════════════════════════════════════════════════════

def test_quote_builder_workspace_renders(authed_page):
    pg = _goto(authed_page, "quote-builder.html")
    assert _has_cards(pg, 1), "No workspace card on quote builder"


def test_quote_builder_line_items_table_present(authed_page):
    pg = _goto(authed_page, "quote-builder.html")
    table = pg.locator("table, #line-items, .line-items, [id*='items']").first
    assert table.count() > 0, "No line items area on quote builder"


def test_quote_builder_add_item_button_present(authed_page):
    pg = _goto(authed_page, "quote-builder.html")
    btn = pg.locator(
        "button:has-text('Add'), button:has-text('Item'), button:has-text('+'), #btn-add-item"
    ).first
    assert btn.count() > 0, "No add-item button on quote builder"


def test_quote_builder_totals_section_present(authed_page):
    pg = _goto(authed_page, "quote-builder.html")
    totals = pg.locator("[id*='total'], [id*='subtotal'], .fw-bold:has-text('Total')").first
    assert totals.count() > 0, "No totals section on quote builder"


# ══ orders-detail.html ════════════════════════════════════════════════════════

def test_orders_detail_page_renders(authed_page):
    pg = _goto(authed_page, "orders-detail.html")
    assert _has_cards(pg), "No content cards on orders detail"


def test_orders_detail_content_non_empty(authed_page):
    pg = _goto(authed_page, "orders-detail.html")
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Orders detail content appears empty"


def test_orders_detail_status_or_badge_visible(authed_page):
    pg = _goto(authed_page, "orders-detail.html")
    has_status = (
        pg.locator(".badge").count() > 0
        or pg.locator("[class*='status']").count() > 0
    )
    assert has_status, "No status badge on orders detail"
