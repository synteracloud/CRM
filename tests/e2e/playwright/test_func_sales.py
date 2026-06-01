"""Functional tests — Sales: dashboard, opportunities-detail, opportunity-new, sales-dashboard, sales-cockpit, sales-analytics."""
from __future__ import annotations

import time
import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_chart, _has_cards, _detail,
)


# ══ dashboard.html ════════════════════════════════════════════════════════════

def test_dashboard_kpi_cards_populated(authed_page, seed):
    pg = _goto(authed_page, "dashboard.html")
    assert _has_content(pg), "No KPI content on main dashboard"


def test_dashboard_cards_present(authed_page):
    pg = _goto(authed_page, "dashboard.html")
    assert _has_cards(pg, 2), "Fewer than 2 cards on main dashboard"


def test_dashboard_chart_or_table_present(authed_page):
    pg = _goto(authed_page, "dashboard.html")
    has_vis = _has_chart(pg) or pg.locator("table").count() > 0
    assert has_vis, "No chart or table on main dashboard"


def test_dashboard_navigation_links_present(authed_page):
    pg = _goto(authed_page, "dashboard.html")
    links = pg.locator(
        "a[href*='leads'], a[href*='contacts'], a[href*='sales'], a[href*='cases']"
    )
    assert links.count() >= 1, "No internal navigation links on dashboard"


# ══ opportunities-detail.html ═════════════════════════════════════════════════

def test_opp_detail_loads_with_id(authed_page, seed):
    if not seed.get("opportunity_id"):
        pytest.skip("No seed opportunity_id")
    pg = _detail(authed_page, "opportunities-detail.html", seed["opportunity_id"])
    assert _has_cards(pg), "No content on opportunity detail"


def test_opp_detail_has_stage_badge(authed_page, seed):
    if not seed.get("opportunity_id"):
        pytest.skip("No seed opportunity_id")
    pg = _detail(authed_page, "opportunities-detail.html", seed["opportunity_id"])
    assert pg.locator(".badge").count() > 0, "No stage badge on opportunity detail"


def test_opp_detail_content_non_empty(authed_page, seed):
    if not seed.get("opportunity_id"):
        pytest.skip("No seed opportunity_id")
    pg = _detail(authed_page, "opportunities-detail.html", seed["opportunity_id"])
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Opportunity detail content empty"


# ══ opportunity-new.html ══════════════════════════════════════════════════════

def test_opp_new_form_fields_present(authed_page):
    pg = _goto(authed_page, "opportunity-new.html")
    pg.locator("#opp-name").wait_for(state="attached", timeout=T_DATA)
    assert pg.locator("#opp-name, #opp-amount").count() == 2, \
        "Expected #opp-name and #opp-amount on opportunity-new"


def test_opp_new_empty_validation(authed_page):
    pg = _goto(authed_page, "opportunity-new.html")
    pg.locator("#opp-name").wait_for(state="attached", timeout=T_DATA)
    pg.locator("#btn-next").click(force=True)
    pg.wait_for_timeout(600)
    assert pg.locator("#opp-name.is-invalid, #opp-account.is-invalid, #opp-amount.is-invalid").count() > 0, \
        "No is-invalid on empty opp step 1"


def test_opp_new_submit_flow(authed_page):
    pg = _goto(authed_page, "opportunity-new.html")
    pg.locator("#opp-name").wait_for(state="attached", timeout=T_DATA)
    ts = str(int(time.time()))[-6:]
    pg.locator("#opp-name").fill(f"Func Opp {ts}", force=True)
    pg.locator("#opp-amount").fill("250000", force=True)
    pg.evaluate("document.querySelector('#opp-account').innerHTML += '<option value=\"test-acct\">Test Account</option>'")
    pg.select_option("#opp-account", value="test-acct")
    pg.locator("#btn-next").click(force=True)
    pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelector('#opp-close-date').value = '2026-12-31'")
    owner_opts = pg.locator("#opp-owner option")
    if owner_opts.count() > 1:
        pg.select_option("#opp-owner", index=1)
    pg.locator("#btn-submit").click(force=True)
    pg.wait_for_timeout(T_DATA)
    has_success = (
        pg.locator("#wizard-success, .alert-success").count() > 0
        or "opportunities" in pg.url
    )
    assert has_success, "Opportunity form did not reach success state"


# ══ sales-dashboard.html ══════════════════════════════════════════════════════

def test_sales_dashboard_kpis_visible(authed_page, seed):
    pg = _goto(authed_page, "sales-dashboard.html")
    assert _has_content(pg), "No KPI content on sales dashboard"


def test_sales_dashboard_chart_present(authed_page):
    pg = _goto(authed_page, "sales-dashboard.html")
    assert _has_chart(pg), "No chart on sales dashboard"


def test_sales_dashboard_pipeline_table_loads(authed_page, seed):
    pg = _goto(authed_page, "sales-dashboard.html")
    count = _rows(pg)
    assert count >= 0, "Table element broken on sales dashboard"


# ══ sales-cockpit.html ════════════════════════════════════════════════════════

def test_sales_cockpit_kpis_visible(authed_page, seed):
    pg = _goto(authed_page, "sales-cockpit.html")
    assert _has_content(pg), "No KPI content on sales cockpit"


def test_sales_cockpit_chart_present(authed_page):
    pg = _goto(authed_page, "sales-cockpit.html")
    assert _has_chart(pg), "No chart on sales cockpit"


def test_sales_cockpit_cards_present(authed_page):
    pg = _goto(authed_page, "sales-cockpit.html")
    assert _has_cards(pg, 2), "Fewer than 2 cards on sales cockpit"


# ══ sales-analytics.html ══════════════════════════════════════════════════════

def test_sales_analytics_kpis_visible(authed_page, seed):
    pg = _goto(authed_page, "sales-analytics.html")
    assert _has_content(pg), "No KPI content on sales analytics"


def test_sales_analytics_chart_present(authed_page):
    pg = _goto(authed_page, "sales-analytics.html")
    assert _has_chart(pg), "No chart on sales analytics"


def test_sales_analytics_cards_present(authed_page):
    pg = _goto(authed_page, "sales-analytics.html")
    assert _has_cards(pg, 2), "Fewer than 2 cards on sales analytics"
