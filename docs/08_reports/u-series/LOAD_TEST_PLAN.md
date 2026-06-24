# LOAD_TEST_PLAN.md — Pakistan CRM OS
**Generated:** 2026-06-21 — U9 Load Test Planning
**Evidence base:** tests/load/locustfile.py, tests/load/reports/ (7 HTML reports), U8 WORKSPACE_SEALING_REPORT, render.yaml

---

## Infrastructure Baseline

**Deployment:** Render.com (Singapore region — closest data center to Pakistan)
- `crm-gateway` — Node.js Express, Render free/starter tier
- `crm-services` — Python FastAPI, Render free/starter tier
- `crm-postgres` — Render PostgreSQL (managed)
- `crm-redis` — Render Redis (managed, used for rate limiting + JTI blocklist)

**Render free tier constraints:**
- Cold start delay: 30–60s after inactivity (instances spin down on Render free tier)
- Concurrency: unknown (depends on plan; assume ~100 concurrent connections max for starter)
- No horizontal scaling on free/starter tier

**Pakistan network context:**
- Mobile-first users on 4G (Telenor, Jazz, Zong, Ufone) — typical RTT to Singapore: 80–150ms
- WhatsApp is the primary communication surface; webhook burst events are expected
- JazzCash/Easypaisa payment flows are currently stub_mode=true (P-016) — load test stubs only

---

## Tool — Locust

**Confirmed present:** locust 2.44.0 in backend/.venv (from pip-audit.json)
**Locustfile:** `D:\SaaS\CRM\tests\load\locustfile.py`
**Reports:** `D:\SaaS\CRM\tests\load\reports\` (7 HTML reports from prior runs)

**No alternative tools needed.** Locust covers all required scenarios. pytest-benchmark is available for micro-benchmarks of Python service functions if needed (pytest-benchmark not in requirements.txt — do not add without cause).

---

## Target Endpoints (Priority Order)

| Priority | Endpoint | Method | Locust Scenario | p95 Target |
|---|---|---|---|---|
| P0 | GET /api/v1/followups | GET | FollowupQueueUser (weight=3) | < 500ms |
| P0 | GET /api/v1/leads | GET | LeadCreationUser (weight=4) | < 500ms |
| P0 | POST /api/v1/leads | POST | LeadCreationUser (weight=4) | < 800ms |
| P0 | GET /api/v1/auth/login (indirectly via token setup) | POST | All users (on_start) | < 300ms |
| P1 | GET /api/v1/collections/invoices | GET | CollectionsQueueUser (weight=2) | < 500ms |
| P1 | GET /api/v1/collections/overdue | GET | CollectionsQueueUser (weight=2) | < 500ms |
| P1 | GET /api/v1/cases | GET | CasesCRUDUser (weight=2) | < 600ms |
| P1 | POST /api/v1/cases | POST | CasesCRUDUser (weight=2) | < 800ms |
| P1 | GET /api/v1/inbox/conversations | GET | InboxUser (weight=1) | < 700ms |
| P2 | GET /health | GET | (not in locustfile — add) | < 100ms |
| P2 | GET /api/v1/leads + GET /api/v1/followups (sequential) | GET+GET | OnboardingFlowUser (weight=1) | < 2000ms total |
| P2 | POST /api/v1/ai/copilot/query | POST | (not in locustfile — add as new scenario) | < 1500ms |
| P3 | GET /api/v1/territories | GET | (not in locustfile) | < 500ms |
| P3 | GET /api/v1/campaigns | GET | (not in locustfile) | < 500ms |

---

## Test Scenarios

### Scenario 1 — Baseline (single user, warm system)

**Purpose:** Establish p50/p95/p99 latency for each endpoint with zero concurrency stress.

**Command:**
```bash
locust --headless -f tests/load/locustfile.py \
  --host=http://localhost:3000 \
  --users=1 --spawn-rate=1 --run-time=120s \
  --html=tests/load/reports/baseline-$(date +%Y%m%d-%H%M).html
```

**Expected:** p95 < 200ms for GET endpoints (in-memory/stub mode), < 500ms for POST

**When to run:** After every significant backend change; before running ramp tests

---

### Scenario 2 — Ramp Test (10 → 50 → 100 users)

**Purpose:** Find the concurrency ceiling and observe where errors begin.

**Command (3 separate runs):**
```bash
# Ramp 10 users
locust --headless -f tests/load/locustfile.py \
  --host=http://localhost:3000 \
  --users=10 --spawn-rate=2 --run-time=120s \
  --html=tests/load/reports/ramp-10-$(date +%Y%m%d-%H%M).html

# Ramp 50 users
locust --headless -f tests/load/locustfile.py \
  --host=http://localhost:3000 \
  --users=50 --spawn-rate=10 --run-time=60s \
  --html=tests/load/reports/ramp-50-$(date +%Y%m%d-%H%M).html

# Ramp 100 users (Render free-tier stress point)
locust --headless -f tests/load/locustfile.py \
  --host=http://localhost:3000 \
  --users=100 --spawn-rate=20 --run-time=60s \
  --html=tests/load/reports/ramp-100-$(date +%Y%m%d-%H%M).html
```

**Observation points:**
- At 50 users: p95 should remain within targets
- At 100 users: identify first endpoints to degrade (expected: POST /leads, POST /cases)
- Record error rate at each tier

---

### Scenario 3 — Spike Test (sudden 10x load)

**Purpose:** Simulate WhatsApp broadcast campaign triggering sudden user activity burst; JazzCash payment webhook burst.

**Command:**
```bash
# Start at 5 users, spike to 100 users after 30 seconds
locust --headless -f tests/load/locustfile.py \
  --host=http://localhost:3000 \
  --users=100 --spawn-rate=50 --run-time=90s \
  --html=tests/load/reports/spike-$(date +%Y%m%d-%H%M).html
```

**Expected:** System recovers within 30 seconds; error rate returns to < 1% after spike subsides; no crash or restart

**Pakistan-specific note:** WhatsApp broadcast campaigns can generate thousands of inbound messages within minutes. The omnichannel inbox endpoints (GET /inbox/conversations, POST /inbox/conversations/:id/messages) are most at risk during a broadcast spike.

---

### Scenario 4 — Soak Test (sustained 30-minute load)

**Purpose:** Detect memory leaks, connection pool exhaustion, Redis TTL issues under sustained load.

**Command:**
```bash
locust --headless -f tests/load/locustfile.py \
  --host=http://localhost:3000 \
  --users=25 --spawn-rate=5 --run-time=1800s \
  --html=tests/load/reports/soak-$(date +%Y%m%d-%H%M).html
```

**Observation points:**
- Node.js gateway memory: watch for growth over time (heapUsed via /health or process metrics)
- PostgreSQL connection pool: watch for "too many connections" errors
- Redis: watch for JTI blocklist growth (should have TTL matching refresh token expiry = 7 days)
- Error rate must remain < 0.5% throughout 30 minutes

**When to run:** Before each production release; after any change to gateway middleware or database query patterns.

---

### Scenario 5 — WhatsApp Webhook Burst (Pakistan-specific)

**Purpose:** Simulate burst of inbound WhatsApp messages from a campaign broadcast (common pattern: 500 messages in 60 seconds).

**Add to locustfile.py (new HttpUser class):**
```python
class WhatsAppWebhookBurstUser(HttpUser):
    """Scenario 5: WhatsApp webhook burst — POST /whatsapp-webhooks/meta. p95 < 300ms."""
    wait_time = between(0.05, 0.2)  # fast burst: 5-20 events/second per user
    weight = 2

    @task
    def inbound_whatsapp(self):
        payload = {
            "object": "whatsapp_business_account",
            "entry": [{"changes": [{"value": {"messages": [
                {"from": "923001234567", "type": "text", "text": {"body": "Hello"}}
            ]}}]}]
        }
        # Note: real Meta webhooks require X-Hub-Signature-256; use test signature in dev
        self.client.post(
            "/api/v1/whatsapp-webhooks/meta",
            json=payload,
            name="POST /whatsapp-webhooks/meta",
        )
```

**Command:**
```bash
locust --headless -f tests/load/locustfile.py \
  --host=http://localhost:3000 \
  --users=20 --spawn-rate=20 --run-time=60s \
  --html=tests/load/reports/whatsapp-burst-$(date +%Y%m%d-%H%M).html
```

**p95 target:** < 300ms per webhook acknowledgment (WhatsApp requires response within 5s or retries)

---

### Scenario 6 — Dashboard KPI Load

**Purpose:** Multiple managers viewing KPI dashboards simultaneously (common morning peak).

**Add to locustfile.py (new HttpUser class):**
```python
class DashboardKPIUser(HttpUser):
    """Scenario 6: Dashboard KPI burst — parallel KPI endpoint calls. p95 < 1000ms."""
    wait_time = between(2, 5)
    weight = 2

    def on_start(self):
        self.token = _get_token(self.client)
        self.headers = _auth_headers(self.token)

    @task(2)
    def get_leads_dashboard(self):
        self.client.get("/api/v1/leads/dashboard", headers=self.headers, name="GET /leads/dashboard")

    @task(2)
    def get_forecasts(self):
        self.client.get("/api/v1/forecasts", headers=self.headers, name="GET /forecasts")

    @task(1)
    def get_ai_scores(self):
        self.client.get("/api/v1/ai/scores/leads", headers=self.headers, name="GET /ai/scores/leads")
```

**p95 target:** < 1000ms for dashboard/aggregate endpoints

---

## Success Criteria (All Scenarios)

| Endpoint Type | p50 Target | p95 Target | p99 Target | Error Rate |
|---|---|---|---|---|
| Health check | < 50ms | < 100ms | < 200ms | 0% |
| Auth (POST /auth/login) | < 100ms | < 300ms | < 500ms | 0% |
| GET list endpoints (leads, contacts, cases, followups) | < 200ms | < 500ms | < 1000ms | < 0.1% |
| POST create endpoints (leads, contacts, cases) | < 300ms | < 800ms | < 1500ms | < 0.5% |
| Dashboard/KPI aggregates | < 400ms | < 1000ms | < 2000ms | < 0.5% |
| Inbox conversations | < 300ms | < 700ms | < 1500ms | < 0.5% |
| WhatsApp webhook acknowledgment | < 100ms | < 300ms | < 500ms | 0% |
| Full onboarding flow (leads + followups) | < 800ms | < 2000ms | < 3000ms | < 1% |

---

## Failure Criteria (Block Release)

- Error rate > 1% under Scenario 2 (50 users ramp)
- p99 latency > 3s on any list endpoint under 50 concurrent users
- Any HTTP 5xx response during normal load (not spike)
- System fails to recover within 60s after Scenario 3 spike
- Memory or connection pool exhaustion during Scenario 4 soak
- WhatsApp webhook p95 > 500ms (risk of Meta retry storm)

---

## Failure Criteria (Log and Monitor, Not Block)

- p95 > 1s on AI endpoints under load (advisory-only, rule-based — not time-critical)
- Render cold-start delay > 30s after idle (Render free-tier limitation — document, not a code issue)

---

## Running Load Tests (Local)

```powershell
# Activate venv
D:\SaaS\CRM\backend\.venv\Scripts\Activate.ps1

# Ensure gateway is running on port 3000 first
# Ensure frontend dev server is running on port 3001 (for UI perf if needed)

# Run standard scenario (50 users, 60 seconds)
Set-Location D:\SaaS\CRM
D:\SaaS\CRM\backend\.venv\Scripts\locust --headless -f tests/load/locustfile.py `
  --host=http://localhost:3000 `
  --users=50 --spawn-rate=10 --run-time=60s `
  --html=tests/load/reports/report-$(Get-Date -Format 'yyyyMMdd-HHmm').html

# Run against production Render deployment
D:\SaaS\CRM\backend\.venv\Scripts\locust --headless -f tests/load/locustfile.py `
  --host=https://crm-gateway-l3rm.onrender.com `
  --users=20 --spawn-rate=5 --run-time=60s `
  --html=tests/load/reports/prod-$(Get-Date -Format 'yyyyMMdd-HHmm').html
```

---

## Evidence Requirements

- HTML report saved to `tests/load/reports/` with timestamp in filename (confirmed pattern from existing reports)
- Report must include: requests/s, p50/p95/p99 per endpoint, error count, error rate
- Soak test: include memory trend if possible (Render metrics dashboard)
- All failure criteria breaches must be documented in report with endpoint name and percentile

---

*End LOAD_TEST_PLAN.md*
