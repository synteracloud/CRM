"""Playwright E2E conftest — browser fixture, BASE_URL, screenshot on failure."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright, Browser, Page

BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")
# For production: BASE_URL=https://crm-frontend-0gde.onrender.com
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def browser():
    browsers_path = os.getenv(
        "PLAYWRIGHT_BROWSERS_PATH",
        str(Path.home() / ".playwright-browsers"),
    )
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
    with sync_playwright() as pw:
        b = pw.chromium.launch(
            headless=True,
            executable_path=_chromium_exe(browsers_path),
        )
        yield b
        b.close()


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


@pytest.fixture
def page(browser: Browser, request):
    ctx = browser.new_context()
    pg = ctx.new_page()
    yield pg
    # Screenshot on failure
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        name = request.node.nodeid.replace("/", "_").replace("::", "__")
        pg.screenshot(path=str(SCREENSHOTS_DIR / f"{name}.png"))
    pg.close()
    ctx.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
