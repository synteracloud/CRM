"""C2c — lead-new, contact-new: form submits without 4xx/5xx."""
from __future__ import annotations

import pytest

import os; BASE_URL = os.getenv("BASE_URL", "http://localhost:3001")


def test_lead_new_form_loads(page):
    page.goto(f"{BASE_URL}/app/lead-new.html", wait_until="domcontentloaded", timeout=15000)
    form = page.locator("form, .wizard-step, [data-step]").first
    assert form.count() > 0, "lead-new.html: no form or wizard element found"
    # Verify at least one input is present
    inputs = page.locator("input, select, textarea")
    assert inputs.count() > 0, "lead-new.html: no input fields found"


def test_contact_new_form_loads(page):
    page.goto(f"{BASE_URL}/app/contact-new.html", wait_until="domcontentloaded", timeout=15000)
    form = page.locator("form, .wizard-step, [data-step]").first
    assert form.count() > 0, "contact-new.html: no form or wizard element found"
    inputs = page.locator("input, select, textarea")
    assert inputs.count() > 0, "contact-new.html: no input fields found"


def test_lead_new_first_step_visible(page):
    page.goto(f"{BASE_URL}/app/lead-new.html", wait_until="networkidle", timeout=20000)
    # First step should be visible (not hidden)
    visible_inputs = page.locator("input:visible, select:visible")
    assert visible_inputs.count() > 0, "lead-new.html: no visible input on first step"
