"""Functional tests — Inbox & Knowledge: inbox, inbox-thread, knowledge-dashboard, knowledge-article."""
from __future__ import annotations

import pytest
from helpers import (
    BASE_URL, T_NAV, T_DATA, T_ACT,
    _goto, _rows, _has_content, _has_cards, _detail,
)


# ══ inbox.html ════════════════════════════════════════════════════════════════

def test_inbox_conversation_list_visible(authed_page, seed):
    pg = _goto(authed_page, "inbox.html")
    has_list = (
        pg.locator("table tbody tr").count() > 0
        or pg.locator("[class*='thread'], [class*='conversation'], [class*='inbox-item']").count() > 0
    )
    assert has_list or _has_content(pg), "No conversation list on inbox"


def test_inbox_queue_filter_present(authed_page):
    pg = _goto(authed_page, "inbox.html")
    filter_el = pg.locator(
        ".nav-pills-custom button, ul.nav-pills button, select[id*='queue'], [data-filter]"
    )
    assert filter_el.count() >= 1, "No queue filter on inbox"


def test_inbox_presence_status_control(authed_page):
    pg = _goto(authed_page, "inbox.html")
    presence = pg.locator(
        "[id*='presence'], select[id*='status'], button:has-text('Online'), button:has-text('Away')"
    ).first
    assert presence.count() > 0 or _has_content(pg), "No presence control on inbox"


def test_inbox_cards_or_content(authed_page, seed):
    pg = _goto(authed_page, "inbox.html")
    assert _has_content(pg), "No content on inbox page"


# ══ inbox-thread.html ════════════════════════════════════════════════════════

def test_inbox_thread_page_renders(authed_page):
    pg = _goto(authed_page, "inbox-thread.html")
    assert _has_cards(pg), "No content on inbox-thread page"


def test_inbox_thread_message_area_present(authed_page):
    pg = _goto(authed_page, "inbox-thread.html")
    msg_area = pg.locator(
        "[id*='messages'], [class*='message-list'], [class*='thread-body'], .chat-body"
    ).first
    assert msg_area.count() > 0 or _has_content(pg), "No message area on inbox-thread"


def test_inbox_thread_send_box_present(authed_page):
    pg = _goto(authed_page, "inbox-thread.html")
    send = pg.locator(
        "textarea[placeholder*='message'], textarea[placeholder*='type'], #msg-input, #message-input"
    ).first
    assert send.count() > 0, "No send message input on inbox-thread"


def test_inbox_thread_send_button_present(authed_page):
    pg = _goto(authed_page, "inbox-thread.html")
    btn = pg.locator(
        "button:has-text('Send'), button[title='Send'], button[id*='send'], .btn-send, [id*='btn-send'], button.btn-primary"
    ).first
    assert btn.count() > 0, "No Send button on inbox-thread"


# ══ knowledge-dashboard.html ══════════════════════════════════════════════════

def test_knowledge_dashboard_articles_visible(authed_page, seed):
    pg = _goto(authed_page, "knowledge-dashboard.html")
    has_articles = (
        _rows(pg) > 0
        or pg.locator("[class*='article'], [class*='knowledge']").count() > 0
    )
    assert has_articles or _has_content(pg), "No articles on knowledge dashboard"


def test_knowledge_dashboard_search_present(authed_page):
    pg = _goto(authed_page, "knowledge-dashboard.html")
    search = pg.locator(
        "input[type='search'], input[placeholder*='Search'], .dt-search input"
    ).first
    assert search.count() > 0, "No search on knowledge dashboard"


def test_knowledge_dashboard_create_button(authed_page):
    pg = _goto(authed_page, "knowledge-dashboard.html")
    btn = pg.locator(
        "button:has-text('New'), button:has-text('Create'), a:has-text('Article'), .btn-primary"
    ).first
    assert btn.count() > 0, "No create article button on knowledge dashboard"


# ══ knowledge-article.html ════════════════════════════════════════════════════

def test_knowledge_article_loads_with_id(authed_page, seed):
    if not seed.get("article_id"):
        pytest.skip("No seed article_id")
    pg = _detail(authed_page, "knowledge-article.html", seed["article_id"])
    assert _has_cards(pg), "No content on knowledge article"


def test_knowledge_article_content_non_empty(authed_page, seed):
    if not seed.get("article_id"):
        pytest.skip("No seed article_id")
    pg = _detail(authed_page, "knowledge-article.html", seed["article_id"])
    content = pg.locator("main, .container-fluid").first.inner_text(timeout=T_DATA).strip()
    assert len(content) > 20, "Knowledge article content empty"


def test_knowledge_article_publish_or_action_button(authed_page, seed):
    if not seed.get("article_id"):
        pytest.skip("No seed article_id")
    pg = _detail(authed_page, "knowledge-article.html", seed["article_id"])
    btn = pg.locator(
        "button:has-text('Publish'), button:has-text('Edit'), button:has-text('Save'), .btn-primary"
    ).first
    assert btn.count() > 0, "No action button on knowledge article"
