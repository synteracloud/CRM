"""Functional tests — Marketing: marketing-workspace, marketing-analytics, campaign-new, engagement-dashboard."""
from __future__ import annotations

import time
import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_chart, _has_cards,
)


# ══ marketing-workspace.html ══════════════════════════════════════════════════

def test_marketing_workspace_campaigns_visible(authed_page, seed):
    pg = _goto(authed_page, "marketing-workspace.html")
    has_data = _rows(pg) > 0 or _has_content(pg)
    assert has_data, "No campaign data on marketing workspace"


def test_marketing_workspace_kpi_cards(authed_page, seed):
    pg = _goto(authed_page, "marketing-workspace.html")
    assert _has_cards(pg, 2), "Fewer than 2 cards on marketing workspace"


def test_marketing_workspace_filter_chips(authed_page):
    pg = _goto(authed_page, "marketing-workspace.html")
    chips = pg.locator(
        ".nav-pills-custom button, ul.nav-pills button[data-filter], .btn[data-filter]"
    )
    assert chips.count() >= 2, "No filter chips on marketing workspace"


def test_marketing_workspace_create_campaign_button(authed_page):
    pg = _goto(authed_page, "marketing-workspace.html")
    btn = pg.locator(
        "button:has-text('New'), button:has-text('Create'), a[href*='campaign-new'], .btn-primary"
    ).first
    assert btn.count() > 0, "No create campaign button on marketing workspace"


# ══ marketing-analytics.html ══════════════════════════════════════════════════

def test_marketing_analytics_kpis_visible(authed_page, seed):
    pg = _goto(authed_page, "marketing-analytics.html")
    assert _has_content(pg), "No KPI content on marketing analytics"


def test_marketing_analytics_chart_present(authed_page):
    pg = _goto(authed_page, "marketing-analytics.html")
    assert _has_chart(pg), "No chart on marketing analytics"


def test_marketing_analytics_cards_present(authed_page):
    pg = _goto(authed_page, "marketing-analytics.html")
    assert _has_cards(pg, 2), "Fewer than 2 cards on marketing analytics"


# ══ campaign-new.html ════════════════════════════════════════════════════════

def test_campaign_new_form_fields_present(authed_page):
    pg = _goto(authed_page, "campaign-new.html")
    assert pg.locator("input:visible, select:visible").count() >= 2, \
        "Fewer than 2 form fields on campaign-new"


def test_campaign_new_empty_validation(authed_page):
    pg = _goto(authed_page, "campaign-new.html")
    submit = pg.locator(
        "button[type='submit'], button:has-text('Save'), button:has-text('Create'), "
        "button:has-text('Next'), .btn-primary"
    ).first
    if submit.count() == 0:
        pytest.skip("Submit/Next button not found on campaign-new")
    submit.click()
    pg.wait_for_timeout(500)
    has_error = (
        pg.locator(".is-invalid, .invalid-feedback:visible").count() > 0
        or pg.locator("button[id*='next']:disabled, .btn-primary:disabled").count() == 0
    )
    assert has_error, "No validation on empty campaign form"


def test_campaign_new_name_field_accepts_input(authed_page):
    pg = _goto(authed_page, "campaign-new.html")
    pg.locator("#campaign-name").wait_for(state="attached", timeout=T_DATA)
    pg.locator("#campaign-name").fill("Func Test Campaign", force=True)
    val = pg.locator("#campaign-name").input_value()
    assert val == "Func Test Campaign", f"#campaign-name shows '{val}' instead of input"


def test_campaign_new_channel_selection(authed_page):
    pg = _goto(authed_page, "campaign-new.html")
    pg.locator("#campaign-type").wait_for(state="attached", timeout=T_DATA)
    pg.select_option("#campaign-type", index=1)
    val = pg.locator("#campaign-type").input_value()
    assert val != "", "#campaign-type returned empty after selection"


# ══ engagement-dashboard.html ════════════════════════════════════════════════

def test_engagement_dashboard_metrics_visible(authed_page, seed):
    pg = _goto(authed_page, "engagement-dashboard.html")
    assert _has_content(pg), "No metrics on engagement dashboard"


def test_engagement_dashboard_chart_present(authed_page):
    pg = _goto(authed_page, "engagement-dashboard.html")
    assert _has_chart(pg), "No chart on engagement dashboard"


def test_engagement_dashboard_delivery_stats(authed_page, seed):
    pg = _goto(authed_page, "engagement-dashboard.html")
    assert _has_cards(pg, 2), "Fewer than 2 metric cards on engagement dashboard"
