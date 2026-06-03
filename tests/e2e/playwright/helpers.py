"""Shared helpers for functional Playwright tests."""
from __future__ import annotations

import os
import pytest
from playwright.sync_api import Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")
_PROD = "onrender.com" in BASE_URL

T_NAV  = 60000 if _PROD else 12000
T_DATA = 20000 if _PROD else 5000
T_ACT  = 5000


def _goto(pg: Page, page_name: str) -> Page:
    url = f"{BASE_URL}/app/{page_name}"
    try:
        pg.goto(url, wait_until="domcontentloaded", timeout=T_NAV)
    except Exception:
        try:
            pg.goto(url, wait_until="domcontentloaded", timeout=T_NAV)
        except Exception:
            pass
    return pg


def _rows(pg: Page, sel: str = "table tbody tr") -> int:
    try:
        pg.wait_for_selector(sel, timeout=T_DATA)
    except Exception:
        pass
    return pg.locator(sel).count()


def _has_content(pg: Page) -> bool:
    for sel in [
        "[data-kpi]", ".kpi-value", ".fs-2.fw-bold",
        ".display-4", ".stat-value", ".metric-value",
    ]:
        els = pg.locator(sel)
        if els.count() > 0:
            try:
                txt = els.first.inner_text(timeout=2000).strip()
                if txt:
                    return True
            except Exception:
                pass
    cards = pg.locator(".card-body")
    for i in range(min(cards.count(), 4)):
        try:
            if cards.nth(i).inner_text(timeout=2000).strip():
                return True
        except Exception:
            pass
    return False


def _click_filter(pg: Page, extra_sel: str = "") -> bool:
    base = (
        ".nav-pills-custom button[data-filter]:not(.active),"
        "ul.nav-pills button[data-filter]:not(.active)"
    )
    sel = f"{base},{extra_sel}" if extra_sel else base
    chips = pg.locator(sel)
    if chips.count() == 0:
        return False
    chips.first.click()
    pg.wait_for_timeout(600)
    return True


def _search(pg: Page, term: str = "zzznomatch999xyz") -> int:
    inp = pg.locator(
        ".dt-search input,"
        "input[type='search'],"
        "input[placeholder*='Search'],"
        "input[placeholder*='search']"
    ).first
    if inp.count() == 0:
        return -1
    inp.fill(term)
    pg.wait_for_timeout(700)
    return pg.locator("table tbody tr").count()


def _detail(pg: Page, page_name: str, record_id: str) -> Page:
    url = f"{BASE_URL}/app/{page_name}?id={record_id}"
    try:
        pg.goto(url, wait_until="domcontentloaded", timeout=T_NAV)
    except Exception:
        try:
            pg.goto(url, wait_until="domcontentloaded", timeout=T_NAV)
        except Exception:
            pass
    return pg


def _has_heading(pg: Page) -> bool:
    for sel in ["h1", "h2", "h3", ".card-title", ".fs-3", ".fs-4.fw-bold"]:
        els = pg.locator(sel)
        if els.count() > 0:
            try:
                if els.first.inner_text(timeout=2000).strip():
                    return True
            except Exception:
                pass
    return False


def _has_cards(pg: Page, minimum: int = 1) -> bool:
    return pg.locator(".card").count() >= minimum


def _has_table(pg: Page) -> bool:
    return pg.locator("table").count() > 0


def _has_chart(pg: Page) -> bool:
    return (
        pg.locator(
            "canvas, .apexcharts-canvas, [id*='Chart'], [id*='chart'], svg.recharts-surface"
        ).count()
        > 0
    )
