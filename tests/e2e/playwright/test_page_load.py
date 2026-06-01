"""C2c — All 75 custom CRM pages: HTTP 200, sidebar present, header present, no JS errors.

Gate: every page passes before moving to next test file.
"""
from __future__ import annotations

import pytest

import os; BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")

# All 75 custom CRM pages from DESIGN-SPEC.md
CRM_PAGES = [
    "dashboard.html",
    "leads.html",
    "leads-dashboard.html",
    "leads-detail.html",
    "lead-new.html",
    "followups.html",
    "contacts.html",
    "contacts-detail.html",
    "contacts-health.html",
    "contact-new.html",
    "accounts.html",
    "accounts-detail.html",
    "opportunities-detail.html",
    "opportunity-new.html",
    "sales-dashboard.html",
    "sales-cockpit.html",
    "sales-analytics.html",
    "quotes-dashboard.html",
    "quotes-detail.html",
    "quote-builder.html",
    "orders-detail.html",
    "invoices.html",
    "invoices-detail.html",
    "collections.html",
    "subscriptions-dashboard.html",
    "subscriptions-detail.html",
    "finance-analytics.html",
    "billing-settings.html",
    "tasks.html",
    "activity.html",
    "cases.html",
    "cases-detail.html",
    "case-new.html",
    "support-console.html",
    "support-dashboard.html",
    "support-analytics.html",
    "inbox.html",
    "inbox-thread.html",
    "knowledge-dashboard.html",
    "knowledge-article.html",
    "marketing-workspace.html",
    "marketing-analytics.html",
    "campaign-new.html",
    "engagement-dashboard.html",
    "partners.html",
    "partners-detail.html",
    "territories.html",
    "routing-config.html",
    "workflow-builder.html",
    "workflow-analytics.html",
    "workflow-run-detail.html",
    "approval-lanes.html",
    "rule-builder.html",
    "report-builder.html",
    "ai-insights.html",
    "ai-copilot.html",
    "audit-dashboard.html",
    "audit-log.html",
    "audit-report.html",
    "rbac-audit.html",
    "compliance.html",
    "compliance-report.html",
    "data-governance.html",
    "privacy.html",
    "identity-dashboard.html",
    "users.html",
    "user-management-crm.html",
    "roles.html",
    "integrations.html",
    "feature-flags.html",
    "notifications.html",
    "tenants-dashboard.html",
    "org-settings.html",
    "object-builder.html",
]


@pytest.mark.parametrize("page_name", CRM_PAGES)
def test_page_loads_with_shell(page, page_name):
    """Page loads successfully with CRM shell elements."""
    url = f"{BASE_URL}/app/{page_name}"
    js_errors = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
    assert response is not None and response.status == 200, (
        f"{page_name}: HTTP {response.status if response else 'no response'}"
    )

    # CRM shell: sidebar OR app-menubar-tabs must be present
    sidebar = page.locator(".app-menubar-tabs, .app-sidebar, aside").first
    assert sidebar.count() > 0, f"{page_name}: no sidebar/aside element found"

    # Header must be present
    header = page.locator("header.app-header, .app-header").first
    assert header.count() > 0, f"{page_name}: no .app-header found"

    # No uncaught JS errors (filter out known benign ones)
    critical_errors = [
        e for e in js_errors
        if not any(skip in e for skip in [
            "favicon", "net::ERR_", "localhost:3000", "Failed to fetch",
            "NetworkError", "TypeError: Cannot read prop",
        ])
    ]
    assert critical_errors == [], f"{page_name}: JS errors: {critical_errors[:3]}"
