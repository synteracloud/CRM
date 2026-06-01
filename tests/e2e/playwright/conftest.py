"""Playwright E2E conftest — browser fixture, BASE_URL, screenshot on failure."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright, Browser, Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Detect production mode (use longer timeouts)
_IS_PROD = "onrender.com" in BASE_URL
PAGE_LOAD_TIMEOUT = 60000 if _IS_PROD else 20000  # ms


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


@pytest.fixture
def page(browser: Browser, request):
    ctx = None
    pg = None
    try:
        ctx = browser.new_context(
            ignore_https_errors=True,
            java_script_enabled=True,
        )
        pg = ctx.new_page()
        pg.set_default_timeout(PAGE_LOAD_TIMEOUT)
        pg.set_default_navigation_timeout(PAGE_LOAD_TIMEOUT)
        yield pg
    except Exception as e:
        # If browser crashed, try to yield a stub that will cause test to error gracefully
        if pg is None:
            pytest.skip(f"Browser context unavailable: {e}")
        else:
            yield pg
    finally:
        # Screenshot on failure
        if pg and hasattr(request.node, "rep_call") and request.node.rep_call.failed:
            try:
                name = request.node.nodeid.replace("/", "_").replace("::", "__")
                pg.screenshot(path=str(SCREENSHOTS_DIR / f"{name}.png"), timeout=5000)
            except Exception:
                pass
        try:
            if pg:
                pg.close()
        except Exception:
            pass
        try:
            if ctx:
                ctx.close()
        except Exception:
            pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
