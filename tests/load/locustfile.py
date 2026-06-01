"""C2d — Locust load tests for Pakistan CRM gateway.

6 scenarios with p95 targets per COMMERCIALISATION-PLAN.md §C2d.

Run:
  locust --headless -f tests/load/locustfile.py \
    --host=http://localhost:3000 --users=50 --spawn-rate=10 --run-time=60s \
    --html=tests/load/reports/report.html

All scenarios require gateway at http://localhost:3000 with valid dev JWT.
"""
from __future__ import annotations

import os
import json
import time
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner

_token_cache: dict = {}

import requests as _req
import uuid as _uuid

def _get_token_once(host: str = "http://localhost:3000") -> str:
    if "token" not in _token_cache:
        # Try /dev-token first (local dev); fall back to /auth/register (production)
        try:
            resp = _req.get(f"{host}/dev-token", timeout=10)
            data = resp.json().get("data", {})
            if data.get("token"):
                _token_cache["token"] = data["token"]
                _token_cache["tenant"] = data.get("tenant_id", "00000000-0000-0000-0000-000000000001")
                return _token_cache["token"]
        except Exception:
            pass
        # Production: register a test user
        try:
            uid = _uuid.uuid4().hex[:8]
            resp = _req.post(
                f"{host}/api/v1/auth/register",
                json={"name": f"Locust-{uid}", "email": f"locust-{uid}@load.test", "password": "LocustLoad2026!"},
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=60,
            )
            data = resp.json().get("data", {})
            _token_cache["token"] = data.get("access_token", "")
            _token_cache["tenant"] = data.get("tenant_id", "")
        except Exception as e:
            print(f"[WARN] Could not get token: {e}")
            _token_cache["token"] = ""
            _token_cache["tenant"] = ""
    return _token_cache["token"]


def _get_tenant(host: str = "http://localhost:3000") -> str:
    if "tenant" not in _token_cache:
        _get_token_once(host)
    return _token_cache.get("tenant", "00000000-0000-0000-0000-000000000001")


def _get_token(client=None) -> str:
    host = os.getenv("LOCUST_HOST", "http://localhost:3000")
    return _get_token_once(host)


def _auth_headers(token: str, tenant: str = None) -> dict:
    _host = os.getenv("LOCUST_HOST", "http://localhost:3000")
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "x-tenant-id": tenant or _get_tenant(_host),
    }


class FollowupQueueUser(HttpUser):
    """Scenario 1: Follow-up queue browse — GET /followups. p95 target < 500ms."""
    wait_time = between(0.5, 2)
    weight = 3

    def on_start(self):
        self.token = _get_token(self.client)
        self.headers = _auth_headers(self.token)

    @task(3)
    def browse_followups(self):
        self.client.get("/api/v1/followups", headers=self.headers, name="GET /followups")

    @task(1)
    def browse_followups_filtered(self):
        self.client.get(
            "/api/v1/followups?state=pending",
            headers=self.headers,
            name="GET /followups?state=pending",
        )


class LeadCreationUser(HttpUser):
    """Scenario 2: Lead creation burst — POST /leads. p95 target < 800ms."""
    wait_time = between(0.2, 1)
    weight = 4

    def on_start(self):
        self.token = _get_token(self.client)
        self.headers = {**_auth_headers(self.token), "Content-Type": "application/json"}
        self._counter = 0

    @task(2)
    def list_leads(self):
        self.client.get("/api/v1/leads", headers=self.headers, name="GET /leads")

    @task(1)
    def create_lead(self):
        self._counter += 1
        payload = {
            "owner_id": "00000000-0000-0000-0000-000000000002",
            "title": f"Load test lead {self._counter}",
            "stage": "new",
            "status": "open",
            "priority": "medium",
            "source": "manual",
            "contact_name": f"Load User {self._counter}",
            "contact_phone_e164": f"+923001{self._counter:06d}",
        }
        with self.client.post(
            "/api/v1/leads",
            json=payload,
            headers=self.headers,
            name="POST /leads",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 201):
                resp.failure(f"Unexpected status: {resp.status_code}")


class CollectionsQueueUser(HttpUser):
    """Scenario 3: Collections queue — GET /collections + /invoice-summaries. p95 < 500ms."""
    wait_time = between(0.5, 2)
    weight = 2

    def on_start(self):
        self.token = _get_token(self.client)
        self.headers = _auth_headers(self.token)

    @task(2)
    def get_invoices(self):
        self.client.get("/api/v1/collections/invoices", headers=self.headers, name="GET /collections/invoices")

    @task(2)
    def get_invoice_summaries(self):
        self.client.get("/api/v1/invoice-summaries", headers=self.headers, name="GET /invoice-summaries")

    @task(1)
    def get_overdue(self):
        self.client.get("/api/v1/collections/overdue", headers=self.headers, name="GET /collections/overdue")


class CasesCRUDUser(HttpUser):
    """Scenario 4: Cases CRUD — GET /cases + POST /cases. p95 < 600ms."""
    wait_time = between(0.5, 2)
    weight = 2

    def on_start(self):
        self.token = _get_token(self.client)
        self.headers = _auth_headers(self.token)
        self.post_headers = {**self.headers, "Content-Type": "application/json"}
        self._counter = 0

    @task(3)
    def list_cases(self):
        self.client.get("/api/v1/cases", headers=self.headers, name="GET /cases")

    @task(1)
    def create_case(self):
        self._counter += 1
        self.client.post(
            "/api/v1/cases",
            json={"subject": f"Load test case {self._counter}"},
            headers=self.post_headers,
            name="POST /cases",
        )


class InboxUser(HttpUser):
    """Scenario 5: Inbox claim + send — GET /inbox/conversations. p95 < 700ms."""
    wait_time = between(1, 3)
    weight = 1

    def on_start(self):
        self.token = _get_token(self.client)
        self.headers = _auth_headers(self.token)

    @task
    def list_conversations(self):
        self.client.get(
            "/api/v1/inbox/conversations",
            headers=self.headers,
            name="GET /inbox/conversations",
        )


class OnboardingFlowUser(HttpUser):
    """Scenario 6: Full onboarding flow — leads → followups. p95 < 2000ms."""
    wait_time = between(1, 4)
    weight = 1

    def on_start(self):
        self.token = _get_token(self.client)
        self.headers = _auth_headers(self.token)

    @task
    def onboarding_flow(self):
        start = time.time()
        self.client.get("/api/v1/leads", headers=self.headers, name="onboarding:GET /leads")
        self.client.get("/api/v1/followups", headers=self.headers, name="onboarding:GET /followups")
        elapsed_ms = (time.time() - start) * 1000
        # If total flow > 2000ms this is a finding, logged to console
        if elapsed_ms > 2000:
            print(f"[WARN] onboarding flow took {elapsed_ms:.0f}ms (target <2000ms)")
