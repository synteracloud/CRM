"""Production smoke test — every CRM page, every critical structural check.

Runs against BASE_URL (default localhost:3001; set to production URL for post-deploy verification).

Per-page checks:
  1. Page loads without navigation error
  2. CRM shell renders: header (.app-header) + sidebar (.app-menubar-tabs)
  3. Sidebar is on-screen (bounding box x >= 0)
  4. Footer appears exactly once (no double footer)
  5. No CORS/loopback console errors
  6. Main content area is not empty
"""
from __future__ import annotations

import os
import pytest
from playwright.sync_api import Browser, Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")
PAGE_LOAD_TIMEOUT = 60000 if "onrender.com" in BASE_URL else 15000

# Exact 75 custom CRM pages from DESIGN-SPEC.md archetypes A–M.
# Does NOT include NexLink library pages (calendar, chat, deals, etc.)
# that happen to use crm-shell.js but are outside the custom design phase.
CRM_PAGES = [
    # A — Dashboards (13)
    "dashboard.html",
    "leads-dashboard.html",
    "contacts-health.html",
    "sales-dashboard.html",
    "quotes-dashboard.html",
    "subscriptions-dashboard.html",
    "support-dashboard.html",
    "engagement-dashboard.html",
    "knowledge-dashboard.html",
    "workflows-dashboard.html",
    "tenants-dashboard.html",
    "identity-dashboard.html",
    "audit-dashboard.html",
    # B — Queues / Lists (11)
    "followups.html",
    "leads.html",
    "contacts.html",
    "accounts.html",
    "cases.html",
    "activity.html",
    "tasks.html",
    "collections.html",
    "invoices.html",
    "users.html",
    "partners.html",
    # C — Detail views (12)
    "leads-detail.html",
    "contacts-detail.html",
    "accounts-detail.html",
    "opportunities-detail.html",
    "cases-detail.html",
    "quotes-detail.html",
    "orders-detail.html",
    "invoices-detail.html",
    "subscriptions-detail.html",
    "workflow-run-detail.html",
    "partners-detail.html",
    "knowledge-article.html",
    # D — Cockpit (1)
    "sales-cockpit.html",
    # E — Support Console (1)
    "support-console.html",
    # F — Marketing Workspace (1)
    "marketing-workspace.html",
    # G — Settings (9)
    "org-settings.html",
    "user-management-crm.html",
    "roles.html",
    "billing-settings.html",
    "integrations.html",
    "notifications.html",
    "feature-flags.html",
    "compliance.html",
    "territories.html",
    # H — Analytics (7)
    "sales-analytics.html",
    "marketing-analytics.html",
    "support-analytics.html",
    "finance-analytics.html",
    "workflow-analytics.html",
    "audit-report.html",
    "report-builder.html",
    # I — Forms (6)
    "lead-new.html",
    "contact-new.html",
    "opportunity-new.html",
    "case-new.html",
    "quote-builder.html",
    "campaign-new.html",
    # J — Audit / Compliance (5)
    "audit-log.html",
    "compliance-report.html",
    "data-governance.html",
    "rbac-audit.html",
    "privacy.html",
    # K — Builders (4)
    "workflow-builder.html",
    "object-builder.html",
    "rule-builder.html",
    "approval-lanes.html",
    # L — Inbox (3)
    "inbox.html",
    "inbox-thread.html",
    "routing-config.html",
    # M — AI (2)
    "ai-copilot.html",
    "ai-insights.html",
]


@pytest.fixture(scope="module")
def smoke_browser():
    """Dedicated browser instance for the smoke suite — 1440x900 viewport."""
    import os
    from pathlib import Path
    from playwright.sync_api import sync_playwright

    browsers_path = os.getenv(
        "PLAYWRIGHT_BROWSERS_PATH",
        str(Path.home() / ".playwright-browsers"),
    )

    def _find_exe(base: str) -> str:
        base_path = Path(base)
        for child in sorted(base_path.iterdir()):
            if child.name.startswith("chromium"):
                for sub in ("chrome-win64", "chrome-win", "chrome-linux"):
                    exe_name = "chrome.exe" if "win" in sub else "chrome"
                    exe = child / sub / exe_name
                    if exe.exists():
                        return str(exe)
        raise FileNotFoundError(f"Chromium not found under {base}")

    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=True,
        executable_path=_find_exe(browsers_path),
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-first-run",
            "--disable-extensions",
        ],
    )
    yield browser
    try:
        browser.close()
    except Exception:
        pass
    try:
        pw.stop()
    except Exception:
        pass


@pytest.fixture(scope="module")
def smoke_token(smoke_browser):
    """Acquire a token once for the whole smoke module."""
    import httpx, uuid, base64, json, re

    gw = (
        "https://crm-gateway-l3rm.onrender.com"
        if "onrender.com" in BASE_URL
        else "http://localhost:3000"
    )
    is_prod = "onrender.com" in BASE_URL

    try:
        if is_prod:
            uid = uuid.uuid4().hex[:8]
            r = httpx.post(
                f"{gw}/api/v1/auth/register",
                json={
                    "name": f"Smoke-{uid}",
                    "email": f"smoke-{uid}@playwright.test",
                    "password": "Smoke2026!",
                },
                timeout=90,
            )
            d = r.json().get("data", {})
            return d.get("access_token", ""), d.get("tenant_id", "")
        else:
            r = httpx.get(f"{gw}/dev-token", timeout=15)
            d = r.json().get("data", {})
            return d.get("token", ""), d.get("tenant_id", "00000000-0000-0000-0000-000000000001")
    except Exception:
        return "", ""


def _make_authed_ctx(browser, token: str, tenant_id: str):
    return browser.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
        java_script_enabled=True,
        storage_state={
            "origins": [{
                "origin": BASE_URL,
                "localStorage": [
                    {"name": "crm_token",     "value": token},
                    {"name": "crm_tenant_id", "value": tenant_id},
                ],
            }],
            "cookies": [],
        },
    )


@pytest.mark.parametrize("page_name", CRM_PAGES)
def test_smoke_page(page_name, smoke_browser, smoke_token):
    """Every CRM page must: load, show shell, show on-screen sidebar,
    have single footer, no CORS errors, non-empty content."""
    token, tenant_id = smoke_token
    url = f"{BASE_URL}/app/{page_name}"

    console_errors: list[str] = []

    ctx = smoke_browser.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
        java_script_enabled=True,
        storage_state={
            "origins": [{
                "origin": BASE_URL,
                "localStorage": [
                    {"name": "crm_token",     "value": token or "dummy"},
                    {"name": "crm_tenant_id", "value": tenant_id or "00000000-0000-0000-0000-000000000001"},
                ],
            }],
            "cookies": [],
        },
    )
    pg = ctx.new_page()
    pg.set_default_timeout(PAGE_LOAD_TIMEOUT)
    pg.set_default_navigation_timeout(PAGE_LOAD_TIMEOUT)

    # Capture console errors
    pg.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    failures: list[str] = []

    try:
        # ── 1. Page loads ──────────────────────────────────────────────────────
        try:
            pg.goto(url, wait_until="domcontentloaded")
            pg.wait_for_timeout(2000)  # let shell JS inject elements
        except Exception as e:
            failures.append(f"LOAD: page navigation failed — {e}")
            pytest.fail("\n".join(failures))

        # ── 2. CRM shell — header ──────────────────────────────────────────────
        header = pg.locator("header.app-header")
        if header.count() == 0:
            failures.append("SHELL: header.app-header not found")

        # ── 3. CRM shell — sidebar ─────────────────────────────────────────────
        sidebar = pg.locator(".app-menubar-tabs")
        if sidebar.count() == 0:
            failures.append("SHELL: .app-menubar-tabs not found")
        else:
            # Sidebar must be on-screen (x >= 0)
            box = sidebar.first.bounding_box()
            if box is None:
                failures.append("SIDEBAR: not visible (no bounding box)")
            elif box["x"] < 0:
                failures.append(
                    f"SIDEBAR: off-screen — x={box['x']:.0f}px (sidebar links not clickable)"
                )

        # ── 4. No double footer ────────────────────────────────────────────────
        footer_count = pg.locator("footer").count()
        if footer_count > 1:
            failures.append(f"FOOTER: {footer_count} footer elements found (double footer)")
        elif footer_count == 0:
            failures.append("FOOTER: no footer found (shell may not have injected)")

        # ── 5. No CORS / loopback errors ───────────────────────────────────────
        cors_errors = [
            e for e in console_errors
            if any(kw in e for kw in ("CORS policy", "loopback", "ERR_BLOCKED_BY_RESPONSE", "localhost:3000"))
        ]
        if cors_errors:
            failures.append(f"CORS: {len(cors_errors)} console error(s) — {cors_errors[0][:120]}")

        # ── 6. Content not empty ───────────────────────────────────────────────
        # Main content selector varies; check for any substantial content block
        content_selectors = [
            ".app-content-inner",
            ".app-content",
            "main",
            ".container-fluid",
        ]
        has_content = False
        for sel in content_selectors:
            loc = pg.locator(sel)
            if loc.count() > 0:
                inner = loc.first.inner_text()
                if len(inner.strip()) > 50:
                    has_content = True
                    break
        if not has_content:
            failures.append("CONTENT: main content area appears empty or too short")

        # ── 7. Sidebar links are clickable (spot-check first visible link) ─────
        sidebar_links = pg.locator(".app-menubar-tabs a[href]")
        if sidebar_links.count() > 0:
            link_box = sidebar_links.first.bounding_box()
            if link_box is None or link_box["x"] < 0 or link_box["width"] < 1:
                failures.append("SIDEBAR LINKS: first nav link is not clickable (off-screen or zero-size)")

    finally:
        if failures:
            # Screenshot for debugging
            try:
                from pathlib import Path
                ss_dir = Path(__file__).parent / "screenshots"
                ss_dir.mkdir(exist_ok=True)
                pg.screenshot(path=str(ss_dir / f"smoke_FAIL_{page_name}.png"))
            except Exception:
                pass
        try:
            pg.close()
        except Exception:
            pass
        try:
            ctx.close()
        except Exception:
            pass

    if failures:
        pytest.fail(f"{page_name}:\n" + "\n".join(f"  ✗ {f}" for f in failures))
