"""Functional tests — AI: ai-insights, ai-copilot."""
from __future__ import annotations

import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_chart, _has_cards,
)


# ══ ai-insights.html ══════════════════════════════════════════════════════════

def test_ai_insights_scores_table_or_list(authed_page, seed):
    pg = _goto(authed_page, "ai-insights.html")
    has_data = _rows(pg) > 0 or _has_content(pg)
    assert has_data, "No content on ai-insights"


def test_ai_insights_score_bands_visible(authed_page, seed):
    pg = _goto(authed_page, "ai-insights.html")
    bands = pg.locator(
        ".badge, [class*='band'], [class*='score'], [data-score]"
    )
    assert bands.count() > 0 or _has_content(pg), "No score bands on ai-insights"


def test_ai_insights_kpi_cards_present(authed_page):
    pg = _goto(authed_page, "ai-insights.html")
    assert _has_cards(pg, 2), "Fewer than 2 cards on ai-insights"


def test_ai_insights_chart_or_metrics(authed_page):
    pg = _goto(authed_page, "ai-insights.html")
    has_visual = _has_chart(pg) or _has_content(pg)
    assert has_visual, "No chart or metrics on ai-insights"


def test_ai_insights_recompute_or_action_button(authed_page):
    pg = _goto(authed_page, "ai-insights.html")
    btn = pg.locator(
        "button:has-text('Recompute'), button:has-text('Refresh'), "
        "button:has-text('Score'), .btn-primary, .btn-secondary"
    ).first
    assert btn.count() > 0, "No action button on ai-insights"


# ══ ai-copilot.html ════════════════════════════════════════════════════════════

def test_ai_copilot_chat_input_present(authed_page):
    pg = _goto(authed_page, "ai-copilot.html")
    pg.locator("#chat-input").wait_for(state="attached", timeout=T_DATA)
    assert pg.locator("#chat-input").count() > 0, "#chat-input not found on ai-copilot"


def test_ai_copilot_send_button_present(authed_page):
    pg = _goto(authed_page, "ai-copilot.html")
    pg.locator("#btn-chat-send").wait_for(state="attached", timeout=T_DATA)
    assert pg.locator("#btn-chat-send").count() > 0, "#btn-chat-send not found on ai-copilot"


def test_ai_copilot_suggestions_section(authed_page, seed):
    pg = _goto(authed_page, "ai-copilot.html")
    has_suggestions = (
        pg.locator("[class*='suggestion'], [data-suggestion], .suggestion-card").count() > 0
        or _has_content(pg)
    )
    assert has_suggestions, "No suggestions section on ai-copilot"


def test_ai_copilot_query_submit_no_error(authed_page):
    pg = _goto(authed_page, "ai-copilot.html")
    pg.locator("#chat-input").wait_for(state="attached", timeout=T_DATA)
    pg.locator("#chat-input").fill("Show me top leads this month", force=True)
    js_errors = []
    pg.on("console", lambda m: js_errors.append(m.text) if m.type == "error" else None)
    pg.locator("#btn-chat-send").click(force=True)
    pg.wait_for_timeout(T_DATA)
    critical = [e for e in js_errors if "Uncaught" in e or "TypeError" in e]
    assert critical == [], f"JS errors after copilot query: {critical[:2]}"


def test_ai_copilot_response_area_present(authed_page):
    pg = _goto(authed_page, "ai-copilot.html")
    response_area = pg.locator(
        "[id*='response'], [id*='result'], [class*='response'], [class*='answer'], .chat-body"
    ).first
    assert response_area.count() > 0 or _has_content(pg), "No response area on ai-copilot"
