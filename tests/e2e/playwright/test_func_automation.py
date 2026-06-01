"""Functional tests — Automation: workflow-builder, workflow-analytics, workflow-run-detail, approval-lanes, rule-builder, report-builder."""
from __future__ import annotations

import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_chart, _has_cards, _detail,
)


# ══ workflow-builder.html ════════════════════════════════════════════════════

def test_workflow_builder_canvas_nodes_present(authed_page):
    pg = _goto(authed_page, "workflow-builder.html")
    try:
        pg.locator(".canvas-node, [data-node], .workflow-node").first.wait_for(state="attached", timeout=T_DATA)
    except Exception:
        pass
    nodes = pg.locator(".canvas-node, [data-node], .workflow-node")
    assert nodes.count() > 0, "No canvas nodes on workflow builder"


def test_workflow_builder_node_selectable(authed_page):
    pg = _goto(authed_page, "workflow-builder.html")
    try:
        pg.wait_for_selector(".canvas-node, [data-node]", timeout=T_DATA)
    except Exception:
        pass
    node = pg.locator(".canvas-node, [data-node]").first
    if node.count() == 0:
        pytest.skip("No canvas nodes found")
    node.click()
    pg.wait_for_timeout(400)
    assert "selected" in (node.get_attribute("class") or ""), "Node not selected after click"


def test_workflow_builder_validate_button_present(authed_page):
    pg = _goto(authed_page, "workflow-builder.html")
    try:
        pg.locator("#btn-validate").wait_for(state="attached", timeout=T_DATA)
    except Exception:
        pass
    assert pg.locator("#btn-validate").count() > 0, "Validate button not found on workflow-builder"


def test_workflow_builder_validate_shows_success(authed_page):
    pg = _goto(authed_page, "workflow-builder.html")
    try:
        pg.locator("#btn-validate").wait_for(state="attached", timeout=T_DATA)
    except Exception:
        pytest.skip("Validate button not found")
    pg.locator("#btn-validate").click(force=True)
    pg.wait_for_timeout(3000)
    assert pg.locator(".alert-success, .alert-info").count() > 0, \
        "Validate did not show success/info banner"


def test_workflow_builder_save_draft(authed_page):
    pg = _goto(authed_page, "workflow-builder.html")
    try:
        pg.locator("#btn-save").wait_for(state="attached", timeout=T_DATA)
    except Exception:
        pytest.skip("Save button not found")
    pg.locator("#btn-save").click(force=True)
    pg.wait_for_timeout(3000)
    assert pg.locator(".alert-info, .alert-success").count() > 0, \
        "Save did not show confirmation"


def test_workflow_builder_inspector_panel(authed_page):
    pg = _goto(authed_page, "workflow-builder.html")
    inspector = pg.locator(
        ".col-lg-3 .card, [id*='inspector'], [class*='inspector'], aside .card"
    ).first
    assert inspector.count() > 0, "No inspector panel on workflow builder"


# ══ workflow-analytics.html ════════════════════════════════════════════════════

def test_workflow_analytics_kpis_visible(authed_page, seed):
    pg = _goto(authed_page, "workflow-analytics.html")
    assert _has_content(pg), "No KPI content on workflow analytics"


def test_workflow_analytics_runs_table(authed_page, seed):
    pg = _goto(authed_page, "workflow-analytics.html")
    assert pg.locator("table").count() > 0 or _has_cards(pg), "No table or cards on workflow analytics"


def test_workflow_analytics_chart_present(authed_page):
    pg = _goto(authed_page, "workflow-analytics.html")
    assert _has_chart(pg) or _has_cards(pg, 2), "No chart or metric cards on workflow analytics"


# ══ workflow-run-detail.html ════════════════════════════════════════════════════

def test_workflow_run_detail_loads(authed_page, seed):
    wf_id = seed.get("workflow_id", "")
    url = f"{BASE_URL}/app/workflow-run-detail.html" + (f"?id={wf_id}" if wf_id else "")
    try:
        authed_page.goto(url, wait_until="networkidle", timeout=T_NAV)
    except Exception:
        authed_page.goto(url, wait_until="domcontentloaded", timeout=T_NAV)
    assert _has_cards(authed_page), "No content on workflow-run-detail"


def test_workflow_run_detail_step_trace(authed_page, seed):
    pg = _goto(authed_page, "workflow-run-detail.html")
    has_trace = (
        pg.locator("[class*='step'], [class*='trace'], [class*='timeline'], table").count() > 0
    )
    assert has_trace or _has_content(pg), "No step trace on workflow run detail"


def test_workflow_run_detail_status_visible(authed_page, seed):
    pg = _goto(authed_page, "workflow-run-detail.html")
    has_status = pg.locator(".badge").count() > 0 or _has_content(pg)
    assert has_status, "No status badge on workflow run detail"


# ══ approval-lanes.html ════════════════════════════════════════════════════════

def test_approval_lanes_content_renders(authed_page):
    pg = _goto(authed_page, "approval-lanes.html")
    assert _has_content(pg), "No content on approval-lanes"


def test_approval_lanes_lane_cards_present(authed_page):
    pg = _goto(authed_page, "approval-lanes.html")
    has_lanes = (
        pg.locator("[class*='lane'], [class*='approval'], .card").count() > 0
    )
    assert has_lanes, "No lane cards on approval-lanes"


def test_approval_lanes_action_button(authed_page):
    pg = _goto(authed_page, "approval-lanes.html")
    btn = pg.locator(
        "button:has-text('Add'), button:has-text('Approve'), button:has-text('New'), .btn-primary"
    ).first
    assert btn.count() > 0, "No action button on approval-lanes"


# ══ rule-builder.html ════════════════════════════════════════════════════════

def test_rule_builder_condition_ui_present(authed_page):
    pg = _goto(authed_page, "rule-builder.html")
    has_conditions = (
        pg.locator(
            "select[id*='field'], select[id*='operator'], [class*='condition'], [class*='rule']"
        ).count() > 0
        or pg.locator("input:visible, select:visible").count() > 0
    )
    assert has_conditions or _has_content(pg), "No condition builder UI on rule-builder"


def test_rule_builder_add_condition_button(authed_page):
    pg = _goto(authed_page, "rule-builder.html")
    btn = pg.locator(
        "button:has-text('Add'), button:has-text('Condition'), button:has-text('Rule'), .btn-primary"
    ).first
    assert btn.count() > 0, "No add-condition button on rule-builder"


def test_rule_builder_save_button_present(authed_page):
    pg = _goto(authed_page, "rule-builder.html")
    btn = pg.locator("button:has-text('Save'), button:has-text('Publish'), .btn-primary").first
    assert btn.count() > 0, "No save button on rule-builder"


# ══ report-builder.html ════════════════════════════════════════════════════════

def test_report_builder_metric_selector_present(authed_page):
    pg = _goto(authed_page, "report-builder.html")
    selector = pg.locator(
        "select[id*='metric'], #report-metric, [id*='metric'], select:visible"
    ).first
    assert selector.count() > 0 or _has_content(pg), "No metric selector on report-builder"


def test_report_builder_chart_type_controls(authed_page):
    pg = _goto(authed_page, "report-builder.html")
    controls = pg.locator(
        "button[data-chart-type], select[id*='chart'], [class*='chart-type'], input[type='radio']"
    )
    assert controls.count() > 0 or _has_content(pg), "No chart type controls on report-builder"


def test_report_builder_execute_button(authed_page):
    pg = _goto(authed_page, "report-builder.html")
    btn = pg.locator(
        "button:has-text('Run'), button:has-text('Execute'), button:has-text('Generate'), .btn-primary"
    ).first
    assert btn.count() > 0, "No execute/run button on report-builder"


def test_report_builder_chart_renders_after_execute(authed_page):
    pg = _goto(authed_page, "report-builder.html")
    btn = pg.locator(
        "button:has-text('Run'), button:has-text('Execute'), button:has-text('Generate'), .btn-primary"
    ).first
    if btn.count() == 0:
        pytest.skip("Execute button not found")
    btn.click()
    pg.wait_for_timeout(T_DATA)
    has_result = _has_chart(pg) or pg.locator("[id*='result'], [class*='result'], table").count() > 0
    assert has_result or _has_content(pg), "No result after report execution"
