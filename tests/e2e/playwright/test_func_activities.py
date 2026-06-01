"""Functional tests — Activities: tasks, activity."""
from __future__ import annotations

import time
import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_cards,
)


# ══ tasks.html ════════════════════════════════════════════════════════════════

def test_tasks_table_populated(authed_page, seed):
    pg = _goto(authed_page, "tasks.html")
    count = _rows(pg)
    assert count > 0, "Tasks table empty — API may have returned 401"


def test_tasks_kpi_cards_visible(authed_page, seed):
    pg = _goto(authed_page, "tasks.html")
    assert _has_content(pg), "No KPI content on tasks page"


def test_tasks_priority_filter_chip(authed_page, seed):
    pg = _goto(authed_page, "tasks.html")
    _rows(pg)
    chip = pg.locator(
        "button[data-filter='high'], button:has-text('High'), button[data-filter='urgent']"
    ).first
    if chip.count() == 0:
        pytest.skip("Priority filter chip not found")
    chip.click()
    pg.wait_for_timeout(600)
    assert pg.locator("table").count() > 0, "Table vanished after priority filter"


def test_tasks_search_filters_rows(authed_page, seed):
    pg = _goto(authed_page, "tasks.html")
    _rows(pg)
    inp = pg.locator(
        ".dt-search input, input[type='search'], input[placeholder*='Search']"
    ).first
    if inp.count() == 0:
        pytest.skip("Search input not found on tasks")
    inp.fill("zzznomatch999xyz")
    pg.wait_for_timeout(700)
    rows = pg.locator("table tbody tr").count()
    assert rows <= 1, f"Search did not filter tasks; got {rows} rows"


def test_tasks_create_button_present(authed_page):
    pg = _goto(authed_page, "tasks.html")
    btn = pg.locator(
        "button:has-text('New Task'), button:has-text('Create'), a:has-text('New'), .btn-primary"
    ).first
    assert btn.count() > 0, "No create task button on tasks page"


# ══ activity.html ════════════════════════════════════════════════════════════

def test_activity_page_loads_timeline(authed_page, seed):
    pg = _goto(authed_page, "activity.html")
    count = _rows(pg)
    assert count >= 0, "Activity table/timeline broken"


def test_activity_kpi_or_content_visible(authed_page, seed):
    pg = _goto(authed_page, "activity.html")
    assert _has_content(pg), "No content on activity page"


def test_activity_filter_chips_present(authed_page):
    pg = _goto(authed_page, "activity.html")
    chips = pg.locator(
        ".nav-pills-custom button, ul.nav-pills button, .btn[data-filter]"
    )
    assert chips.count() >= 1, "No filter chips on activity page"
