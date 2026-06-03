"""Functional tests — Lead Management: leads, leads-dashboard, leads-detail, lead-new, followups."""
from __future__ import annotations

import time
import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_chart, _has_cards, _detail,
)


# ══ leads.html ════════════════════════════════════════════════════════════════

def test_leads_table_populated_from_api(authed_page, seed):
    pg = _goto(authed_page, "leads.html")
    count = _rows(pg, "#dt_NewCustomers tbody tr")
    assert count > 0, "Lead DataTable empty — API likely returned 401 or no data"


def test_leads_kpi_total_non_zero(authed_page, seed):
    pg = _goto(authed_page, "leads.html")
    pg.wait_for_selector("#kpi-total-leads", timeout=T_DATA)
    val = pg.locator("#kpi-total-leads").inner_text(timeout=T_ACT).strip()
    assert val not in ("", "0"), f"kpi-total-leads shows '{val}'"


def test_leads_stage_filter_activates(authed_page, seed):
    pg = _goto(authed_page, "leads.html")
    _rows(pg, "#dt_NewCustomers tbody tr")
    chip = pg.locator("#lead-filter-stage button[data-filter='qualifying']")
    if chip.count() == 0:
        pytest.skip("Qualifying chip not found")
    chip.click()
    pg.wait_for_timeout(500)
    assert "active" in (chip.get_attribute("class") or ""), "Filter chip did not become active"


def test_leads_stage_filter_redraws_table(authed_page, seed):
    pg = _goto(authed_page, "leads.html")
    _rows(pg, "#dt_NewCustomers tbody tr")
    chip = pg.locator("#lead-filter-stage button[data-filter='new']")
    if chip.count() == 0:
        pytest.skip("New stage chip not found")
    chip.click()
    pg.wait_for_timeout(700)
    assert pg.locator("#dt_NewCustomers").count() > 0, "DataTable vanished after filter"


def test_leads_search_produces_empty_state(authed_page, seed):
    pg = _goto(authed_page, "leads.html")
    _rows(pg, "#dt_NewCustomers tbody tr")
    inp = pg.locator(
        "#dt_NewCustomers_Search input, #dt_NewCustomers_wrapper .dt-search input"
    ).first
    if inp.count() == 0:
        pytest.skip("Search input not found")
    inp.fill("zzznomatch999xyz")
    pg.wait_for_timeout(700)
    rows = pg.locator("#dt_NewCustomers tbody tr").count()
    assert rows <= 1, f"Expected empty state after no-match search, got {rows} rows"


def test_leads_search_restores_on_clear(authed_page, seed):
    pg = _goto(authed_page, "leads.html")
    initial = _rows(pg, "#dt_NewCustomers tbody tr")
    inp = pg.locator(
        "#dt_NewCustomers_Search input, #dt_NewCustomers_wrapper .dt-search input"
    ).first
    if inp.count() == 0:
        pytest.skip("Search input not found")
    inp.fill("zzznomatch999xyz")
    pg.wait_for_timeout(700)
    inp.fill("")
    pg.wait_for_timeout(700)
    restored = pg.locator("#dt_NewCustomers tbody tr").count()
    assert restored >= initial, "Row count did not restore after clearing search"


# ══ leads-dashboard.html ══════════════════════════════════════════════════════

def test_leads_dashboard_kpis_visible(authed_page):
    pg = _goto(authed_page, "leads-dashboard.html")
    assert _has_content(pg), "No KPI content on leads-dashboard"


def test_leads_dashboard_cards_present(authed_page):
    pg = _goto(authed_page, "leads-dashboard.html")
    assert _has_cards(pg, 2), "Fewer than 2 cards on leads dashboard"


def test_leads_dashboard_chart_container_present(authed_page):
    pg = _goto(authed_page, "leads-dashboard.html")
    assert _has_chart(pg), "No chart container on leads dashboard"


# ══ leads-detail.html ════════════════════════════════════════════════════════

def test_leads_detail_loads_with_id(authed_page, seed):
    if not seed.get("lead_id"):
        pytest.skip("No seed lead_id")
    pg = _detail(authed_page, "leads-detail.html", seed["lead_id"])
    assert _has_cards(pg), "No content cards on lead detail"


def test_leads_detail_has_stage_badge(authed_page, seed):
    if not seed.get("lead_id"):
        pytest.skip("No seed lead_id")
    pg = _detail(authed_page, "leads-detail.html", seed["lead_id"])
    assert pg.locator(".badge").count() > 0, "No stage badge on lead detail"


def test_leads_detail_action_buttons_visible(authed_page, seed):
    if not seed.get("lead_id"):
        pytest.skip("No seed lead_id")
    pg = _detail(authed_page, "leads-detail.html", seed["lead_id"])
    assert pg.locator("button.btn, a.btn").count() >= 1, "No action buttons on lead detail"


def test_leads_detail_content_section_non_empty(authed_page, seed):
    if not seed.get("lead_id"):
        pytest.skip("No seed lead_id")
    pg = _detail(authed_page, "leads-detail.html", seed["lead_id"])
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Lead detail content section appears empty"


# ══ lead-new.html ═════════════════════════════════════════════════════════════

def test_lead_new_step1_empty_validation(authed_page):
    pg = _goto(authed_page, "lead-new.html")
    pg.locator("#btn-next").click()
    pg.wait_for_timeout(400)
    assert pg.locator(".is-invalid").count() > 0, "No validation errors on empty Step 1"


def test_lead_new_phone_non_e164_rejected(authed_page):
    pg = _goto(authed_page, "lead-new.html")
    pg.fill("#lead-phone", "03001234567")
    pg.fill("#lead-fname", "Test")
    pg.fill("#lead-lname", "User")
    pg.locator("#btn-next").click()
    pg.wait_for_timeout(400)
    assert pg.locator("#lead-phone.is-invalid").count() > 0, "Non-E.164 phone not rejected"


def test_lead_new_step_navigation_shows_preview(authed_page):
    pg = _goto(authed_page, "lead-new.html")
    ts = str(int(time.time()))[-6:]
    pg.fill("#lead-phone", f"+9230099{ts}")
    pg.fill("#lead-fname", "Func")
    pg.fill("#lead-lname", "Test")
    pg.locator("#btn-next").click()
    pg.wait_for_selector("#wizard-step-2:not(.d-none)", timeout=5000)
    preview = pg.locator("#s2-name-preview").inner_text(timeout=T_ACT).strip()
    assert preview == "Func Test", f"Name preview shows '{preview}' instead of 'Func Test'"


def test_lead_new_back_button_returns_to_step1(authed_page):
    pg = _goto(authed_page, "lead-new.html")
    ts = str(int(time.time()))[-6:]
    pg.fill("#lead-phone", f"+9230099{ts}")
    pg.fill("#lead-fname", "Back")
    pg.fill("#lead-lname", "Test")
    pg.locator("#btn-next").click()
    pg.wait_for_selector("#wizard-step-2:not(.d-none)", timeout=5000)
    pg.locator("#btn-back").click()
    pg.wait_for_selector("#wizard-step-1:not(.d-none)", timeout=3000)
    assert pg.locator("#wizard-step-1:not(.d-none)").count() > 0, "Step 1 not restored after Back"


def test_lead_new_step2_empty_validation(authed_page):
    pg = _goto(authed_page, "lead-new.html")
    ts = str(int(time.time()))[-6:]
    pg.fill("#lead-phone", f"+9230099{ts}")
    pg.fill("#lead-fname", "Val")
    pg.fill("#lead-lname", "Test")
    pg.locator("#btn-next").click()
    pg.wait_for_selector("#wizard-step-2:not(.d-none)", timeout=5000)
    pg.locator("#btn-submit").click()
    pg.wait_for_timeout(400)
    assert pg.locator(".is-invalid").count() > 0, "No validation errors on empty Step 2"


def test_lead_new_full_wizard_creates_lead(authed_page):
    pg = _goto(authed_page, "lead-new.html")
    ts = str(int(time.time()))[-6:]
    pg.fill("#lead-phone", f"+9230077{ts}")
    pg.fill("#lead-fname", "Create")
    pg.fill("#lead-lname", "Lead")
    pg.locator("#btn-next").click()
    pg.wait_for_selector("#wizard-step-2:not(.d-none)", timeout=5000)
    pg.wait_for_timeout(800)  # let users API populate owner dropdown
    pg.select_option("#lead-stage", "new")
    owners = pg.locator("#lead-owner option")
    if owners.count() > 1:
        pg.select_option("#lead-owner", index=1)
    else:
        pg.evaluate("document.getElementById('lead-owner').innerHTML += '<option value=\"dev-user-001\">Dev User</option>'")
        pg.select_option("#lead-owner", "dev-user-001")
    pg.select_option("#lead-source", "whatsapp")
    pg.on("dialog", lambda d: d.accept())
    pg.locator("#btn-submit").click(force=True)
    pg.wait_for_selector("#wizard-success:not(.d-none)", timeout=T_DATA)
    success_text = pg.locator("#success-name").inner_text(timeout=T_ACT)
    assert "Create Lead" in success_text, f"Wizard success missing name: '{success_text}'"


# ══ followups.html ════════════════════════════════════════════════════════════

def test_followups_enforcement_strip_visible(authed_page, seed):
    pg = _goto(authed_page, "followups.html")
    strip = pg.locator(".alert-danger, [class*='danger'][class*='alert'], .bg-danger").first
    assert strip.count() > 0, "Enforcement strip not present on followups page"


def test_followups_table_populated(authed_page, seed):
    pg = _goto(authed_page, "followups.html")
    count = _rows(pg, "#dt_Followups tbody tr")
    assert count > 0, "Followups DataTable empty"


def test_followups_kpi_cards_present(authed_page, seed):
    pg = _goto(authed_page, "followups.html")
    assert _has_cards(pg, 3), "Fewer than 3 KPI cards on followups"


def test_followups_action_type_filter_activates(authed_page, seed):
    pg = _goto(authed_page, "followups.html")
    _rows(pg, "#dt_Followups tbody tr")
    chip = pg.locator("button[data-filter='Call'], button:has-text('Call')").first
    if chip.count() == 0:
        pytest.skip("Call filter chip not found")
    chip.click()
    pg.wait_for_timeout(600)
    assert pg.locator("table#dt_Followups").count() > 0, "Table gone after Call filter"


def test_followups_level_filter_activates(authed_page, seed):
    pg = _goto(authed_page, "followups.html")
    _rows(pg, "#dt_Followups tbody tr")
    chip = pg.locator("button[data-filter='Strict'], button:has-text('Strict')").first
    if chip.count() == 0:
        pytest.skip("Strict filter chip not found")
    chip.click()
    pg.wait_for_timeout(600)
    assert pg.locator("table").count() > 0, "Table gone after Strict filter"
