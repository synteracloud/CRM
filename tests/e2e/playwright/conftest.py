"""Playwright E2E conftest — browser, auth, seed, page fixtures."""
from __future__ import annotations

import base64
import json
import os
import time
import uuid
from pathlib import Path

import httpx
import pytest
from playwright.sync_api import sync_playwright, Browser, Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

_IS_PROD = "onrender.com" in BASE_URL
PAGE_LOAD_TIMEOUT = 60000 if _IS_PROD else 20000
DATA_TIMEOUT = 20000 if _IS_PROD else 8000

GATEWAY_URL = (
    "https://crm-gateway-l3rm.onrender.com"
    if _IS_PROD
    else "http://localhost:3000"
)


# ── Browser ────────────────────────────────────────────────────────────────────

def _chromium_exe(base: str) -> str:
    base_path = Path(base)
    for child in sorted(base_path.iterdir()):
        if child.name.startswith("chromium"):
            for sub in ("chrome-win64", "chrome-win", "chrome-linux"):
                exe_name = "chrome.exe" if "win" in sub else "chrome"
                exe = child / sub / exe_name
                if exe.exists():
                    return str(exe)
    raise FileNotFoundError(f"Chromium not found under {base}")


_pw_instance = None
_browser_instance = None


@pytest.fixture(scope="session")
def browser():
    global _pw_instance, _browser_instance
    browsers_path = os.getenv(
        "PLAYWRIGHT_BROWSERS_PATH",
        str(Path.home() / ".playwright-browsers"),
    )
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
    _pw_instance = sync_playwright().start()
    _browser_instance = _pw_instance.chromium.launch(
        headless=True,
        executable_path=_chromium_exe(browsers_path),
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    yield _browser_instance
    try:
        _browser_instance.close()
    except Exception:
        pass
    try:
        _pw_instance.stop()
    except Exception:
        pass


# ── Auth ───────────────────────────────────────────────────────────────────────

_AUTH_CACHE: dict = {}


def _decode_jwt_sub(token: str) -> str:
    """Extract sub (user_id) from a JWT without verifying signature."""
    try:
        payload_b64 = token.split(".")[1]
        padding = 4 - len(payload_b64) % 4
        payload_b64 += "=" * (padding % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload_b64))
        return decoded.get("sub", "")
    except Exception:
        return ""


def _acquire_token() -> tuple[str, str]:
    if _AUTH_CACHE:
        return _AUTH_CACHE["token"], _AUTH_CACHE["tenant_id"]

    gw = GATEWAY_URL
    if _IS_PROD:
        uid = uuid.uuid4().hex[:8]
        r = httpx.post(
            f"{gw}/api/v1/auth/register",
            json={
                "name": f"E2E-Full-{uid}",
                "email": f"e2e-full-{uid}@playwright.test",
                "password": "E2EFull2026!",
            },
            timeout=90,
        )
        d = r.json().get("data", {})
        _AUTH_CACHE["token"] = d.get("access_token", "")
        _AUTH_CACHE["tenant_id"] = d.get("tenant_id", "")
    else:
        r = httpx.get(f"{gw}/dev-token", timeout=15)
        d = r.json().get("data", {})
        _AUTH_CACHE["token"] = d.get("token", "")
        _AUTH_CACHE["tenant_id"] = d.get(
            "tenant_id", "00000000-0000-0000-0000-000000000001"
        )

    _AUTH_CACHE["user_id"] = _decode_jwt_sub(_AUTH_CACHE["token"])
    return _AUTH_CACHE["token"], _AUTH_CACHE["tenant_id"]


@pytest.fixture(scope="session")
def auth_credentials():
    return _acquire_token()


# ── Seed data (one record per resource, created once per session) ──────────────

_SEED: dict = {}


@pytest.fixture(scope="session")
def seed(auth_credentials):
    if _SEED:
        return _SEED

    token, tenant_id = auth_credentials
    gw = GATEWAY_URL
    hdrs = {
        "Authorization": f"Bearer {token}",
        "x-tenant-id": tenant_id,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    ts = str(int(time.time()))[-6:]
    user_id = _AUTH_CACHE.get("user_id") or tenant_id

    def _post(path: str, body: dict) -> dict:
        try:
            r = httpx.post(f"{gw}/api/v1{path}", json=body, headers=hdrs, timeout=30)
            return r.json().get("data", {}) if r.status_code < 300 else {}
        except Exception:
            return {}

    def _get_first(path: str) -> dict:
        try:
            r = httpx.get(f"{gw}/api/v1{path}", headers=hdrs, timeout=15)
            items = r.json().get("data", [])
            return items[0] if isinstance(items, list) and items else {}
        except Exception:
            return {}

    lead = _post("/leads", {
        "contact_name": f"E2E Lead {ts}",
        "contact_phone_e164": f"+9230088{ts}",
        "stage": "qualifying", "source": "manual",
        "owner_id": user_id, "estimated_value": 150000, "currency": "PKR",
    })
    _SEED["lead_id"] = lead.get("lead_id") or _get_first("/leads?limit=1").get("lead_id", "")

    contact = _post("/contacts", {
        "first_name": "E2E", "last_name": f"Contact{ts}",
        "email": f"e2e-{ts}@test.com", "phone_e164": f"+9230188{ts}",
    })
    _SEED["contact_id"] = contact.get("contact_id") or _get_first("/contacts?limit=1").get("contact_id", "")

    opp = _post("/opportunities", {
        "name": f"E2E Opp {ts}", "stage": "qualification",
        "amount": 500000, "currency": "PKR",
        "close_date": "2026-12-31", "owner_id": user_id,
    })
    _SEED["opportunity_id"] = opp.get("opportunity_id") or _get_first("/opportunities?limit=1").get("opportunity_id", "")

    case = _post("/cases", {
        "subject": f"E2E Case {ts}", "priority": "medium",
        "channel": "email", "description": "Seeded by E2E test suite.",
        "source": "crm", "queue": "General Support",
    })
    _SEED["case_id"] = case.get("case_id", "")
    _SEED["case_number"] = case.get("case_number", _SEED["case_id"])

    task = _post("/tasks", {
        "title": f"E2E Task {ts}", "due_date": "2026-12-31", "priority": "medium",
    })
    _SEED["task_id"] = task.get("task_id", "")

    partner = _post("/partners", {
        "name": f"E2E Partner {ts}", "partner_tier": "silver",
        "contact_email": f"partner-{ts}@test.com",
    })
    _SEED["partner_id"] = partner.get("partner_id") or _get_first("/partners?limit=1").get("partner_id", "")

    territory = _post("/territories", {
        "name": f"E2E Territory {ts}", "criteria_type": "geographic",
        "description": "E2E test territory",
    })
    _SEED["territory_id"] = territory.get("territory_id") or _get_first("/territories?limit=1").get("territory_id", "")

    workflow = _post("/workflows", {
        "name": f"E2E Workflow {ts}",
        "trigger_events": ["manual.trigger.v1"],
        "steps_dsl": [],
    })
    _SEED["workflow_id"] = workflow.get("workflow_id") or _get_first("/workflows?limit=1").get("workflow_id", "")

    campaign = _post("/campaigns", {
        "name": f"E2E Campaign {ts}", "type": "whatsapp_broadcast",
    })
    _SEED["campaign_id"] = campaign.get("campaign_id") or _get_first("/campaigns?limit=1").get("campaign_id", "")

    article = _post("/knowledge/articles", {
        "title": f"E2E Article {ts}",
        "content": "E2E functional test article.",
        "category": "general",
    })
    _SEED["article_id"] = article.get("article_id") or _get_first("/knowledge/articles?limit=1").get("article_id", "")

    account = _get_first("/accounts?limit=1")
    _SEED["account_id"] = account.get("account_id", "")

    invoice = _get_first("/invoice-summaries?limit=1")
    _SEED["invoice_id"] = invoice.get("invoice_id") or invoice.get("invoice_summary_id", "")

    quote = _post("/quotes", {
        "name": f"E2E Quote {ts}",
        "opportunity_id": _SEED.get("opportunity_id", ""),
        "valid_until": "2026-12-31",
    })
    _SEED["quote_id"] = quote.get("quote_id") or _get_first("/quotes?limit=1").get("quote_id", "")

    _SEED["token"] = token
    _SEED["tenant_id"] = tenant_id
    return _SEED


# ── Page fixtures ──────────────────────────────────────────────────────────────

def _screenshot_on_fail(pg: Page | None, request) -> None:
    if (
        pg
        and hasattr(request.node, "rep_call")
        and getattr(request.node.rep_call, "failed", False)
    ):
        try:
            name = request.node.nodeid.replace("/", "_").replace("::", "__")
            pg.screenshot(path=str(SCREENSHOTS_DIR / f"{name}.png"), timeout=5000)
        except Exception:
            pass


def _close(*items) -> None:
    for item in items:
        if item:
            try:
                item.close()
            except Exception:
                pass


@pytest.fixture
def page(browser: Browser, request):
    ctx = pg = None
    try:
        ctx = browser.new_context(ignore_https_errors=True, java_script_enabled=True)
        pg = ctx.new_page()
        pg.set_default_timeout(PAGE_LOAD_TIMEOUT)
        pg.set_default_navigation_timeout(PAGE_LOAD_TIMEOUT)
        yield pg
    except Exception as e:
        if pg is None:
            pytest.skip(f"Browser context unavailable: {e}")
        else:
            yield pg
    finally:
        _screenshot_on_fail(pg, request)
        _close(pg, ctx)


@pytest.fixture
def authed_page(browser: Browser, auth_credentials, request):
    token, tenant_id = auth_credentials
    if not token:
        pytest.skip("No auth token — check gateway connectivity")
    ctx = pg = None
    try:
        ctx = browser.new_context(ignore_https_errors=True, java_script_enabled=True)
        pg = ctx.new_page()
        pg.set_default_timeout(PAGE_LOAD_TIMEOUT)
        pg.set_default_navigation_timeout(PAGE_LOAD_TIMEOUT)
        try:
            pg.goto(
                f"{BASE_URL}/app/dashboard.html",
                wait_until="domcontentloaded",
                timeout=PAGE_LOAD_TIMEOUT,
            )
        except Exception:
            pass
        pg.evaluate(
            "([t, tid]) => { localStorage.setItem('crm_token', t); localStorage.setItem('crm_tenant_id', tid); }",
            [token, tenant_id],
        )
        yield pg
    except Exception as e:
        if pg is None:
            pytest.skip(f"Browser context unavailable: {e}")
        else:
            yield pg
    finally:
        _screenshot_on_fail(pg, request)
        _close(pg, ctx)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
