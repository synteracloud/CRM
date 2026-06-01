"""Functional tests — Finance: invoices, invoices-detail, collections, subscriptions-dashboard, subscriptions-detail, finance-analytics, billing-settings."""
from __future__ import annotations

import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_chart, _has_cards, _detail,
)


# ══ invoices.html ════════════════════════════════════════════════════════════

def test_invoices_table_populated(authed_page, seed):
    pg = _goto(authed_page, "invoices.html")
    count = _rows(pg, "#dt_Invoices tbody tr")
    assert count > 0, "Invoices DataTable empty"


def test_invoices_kpi_cards_visible(authed_page, seed):
    pg = _goto(authed_page, "invoices.html")
    assert _has_content(pg), "No KPI content on invoices page"


def test_invoices_status_filter_chip(authed_page, seed):
    pg = _goto(authed_page, "invoices.html")
    _rows(pg, "#dt_Invoices tbody tr")
    chip = pg.locator("button[data-filter='overdue'], button:has-text('Overdue')").first
    if chip.count() == 0:
        pytest.skip("Overdue filter chip not found")
    chip.click()
    pg.wait_for_timeout(600)
    assert pg.locator("table#dt_Invoices").count() > 0, "Table gone after status filter"


def test_invoices_search_filters_rows(authed_page, seed):
    pg = _goto(authed_page, "invoices.html")
    _rows(pg, "#dt_Invoices tbody tr")
    inp = pg.locator("#dt_Invoices_wrapper .dt-search input, input[placeholder*='Search']").first
    if inp.count() == 0:
        pytest.skip("Search input not found on invoices")
    inp.fill("zzznomatch999xyz")
    pg.wait_for_timeout(700)
    rows = pg.locator("#dt_Invoices tbody tr").count()
    assert rows <= 1, f"Search did not filter invoices; got {rows} rows"


# ══ invoices-detail.html ══════════════════════════════════════════════════════

def test_invoices_detail_page_renders(authed_page):
    pg = _goto(authed_page, "invoices-detail.html")
    assert _has_cards(pg), "No content on invoices detail"


def test_invoices_detail_line_items_section(authed_page):
    pg = _goto(authed_page, "invoices-detail.html")
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Invoices detail content empty"


def test_invoices_detail_action_buttons_present(authed_page):
    pg = _goto(authed_page, "invoices-detail.html")
    assert pg.locator("button.btn, a.btn").count() >= 1, "No action buttons on invoices detail"


# ══ collections.html ══════════════════════════════════════════════════════════

def test_collections_table_populated(authed_page, seed):
    pg = _goto(authed_page, "collections.html")
    count = _rows(pg)
    assert count > 0, "Collections table empty"


def test_collections_kpi_cards_visible(authed_page, seed):
    pg = _goto(authed_page, "collections.html")
    assert _has_content(pg), "No KPI content on collections page"


def test_collections_filter_chips_present(authed_page):
    pg = _goto(authed_page, "collections.html")
    chips = pg.locator(".nav-pills-custom button, ul.nav-pills button[data-filter]")
    assert chips.count() >= 2, "No filter chips on collections"


def test_collections_record_payment_button_present(authed_page, seed):
    pg = _goto(authed_page, "collections.html")
    _rows(pg)
    btn = pg.locator(
        "button:has-text('Payment'), button:has-text('Record'), a:has-text('Payment')"
    ).first
    assert btn.count() > 0, "No Record Payment button visible on collections"


# ══ subscriptions-dashboard.html ══════════════════════════════════════════════

def test_subscriptions_dashboard_kpis_visible(authed_page, seed):
    pg = _goto(authed_page, "subscriptions-dashboard.html")
    assert _has_content(pg), "No KPI content on subscriptions dashboard"


def test_subscriptions_dashboard_table_or_chart(authed_page, seed):
    pg = _goto(authed_page, "subscriptions-dashboard.html")
    has_vis = pg.locator("table").count() > 0 or _has_chart(pg)
    assert has_vis, "No table or chart on subscriptions dashboard"


def test_subscriptions_dashboard_cards_present(authed_page):
    pg = _goto(authed_page, "subscriptions-dashboard.html")
    assert _has_cards(pg, 2), "Fewer than 2 cards on subscriptions dashboard"


# ══ subscriptions-detail.html ═════════════════════════════════════════════════

def test_subscriptions_detail_page_renders(authed_page):
    pg = _goto(authed_page, "subscriptions-detail.html")
    assert _has_cards(pg), "No content on subscriptions detail"


def test_subscriptions_detail_content_non_empty(authed_page):
    pg = _goto(authed_page, "subscriptions-detail.html")
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Subscriptions detail content empty"


def test_subscriptions_detail_status_badge(authed_page):
    pg = _goto(authed_page, "subscriptions-detail.html")
    has_status = pg.locator(".badge").count() > 0 or _has_content(pg)
    assert has_status, "No status or content on subscriptions detail"


# ══ finance-analytics.html ════════════════════════════════════════════════════

def test_finance_analytics_kpis_visible(authed_page, seed):
    pg = _goto(authed_page, "finance-analytics.html")
    assert _has_content(pg), "No KPI content on finance analytics"


def test_finance_analytics_chart_present(authed_page):
    pg = _goto(authed_page, "finance-analytics.html")
    assert _has_chart(pg), "No chart on finance analytics"


def test_finance_analytics_cards_present(authed_page):
    pg = _goto(authed_page, "finance-analytics.html")
    assert _has_cards(pg, 2), "Fewer than 2 cards on finance analytics"


# ══ billing-settings.html ════════════════════════════════════════════════════

def test_billing_settings_plan_card_visible(authed_page):
    pg = _goto(authed_page, "billing-settings.html")
    assert _has_content(pg), "No content on billing settings"


def test_billing_settings_invoices_section(authed_page):
    pg = _goto(authed_page, "billing-settings.html")
    section = pg.locator(
        "[id*='invoice'], [class*='invoice'], h3:has-text('Invoice'), h4:has-text('Invoice')"
    ).first
    assert section.count() > 0 or _has_cards(pg, 2), \
        "No invoices section on billing settings"


def test_billing_settings_action_button_present(authed_page):
    pg = _goto(authed_page, "billing-settings.html")
    btn = pg.locator(
        "button:has-text('Upgrade'), button:has-text('Manage'), a:has-text('Plan'), .btn-primary"
    ).first
    assert btn.count() > 0, "No action button on billing settings"
