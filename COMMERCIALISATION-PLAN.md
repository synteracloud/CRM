# Pakistan CRM OS — Commercialisation Plan

**Created:** 2026-05-31
**Authority:** This file is the active anchor document for all work from 2026-05-31 onwards. `REBUILD-PLAN.md` is closed — do not resume work from it.
**Status:** C5 ← CURRENT (C4 complete 2026-06-02 — 42/42 routes pass production smoke test)
**Task tracker:** `PENDING.md` (root) — add commercialisation tasks here as `[ ]` items under a new `## Commercialisation` section
**Session log:** `PROGRESS.md` — one-line summary added every session
**Predecessor:** `REBUILD-PLAN.md` — build phases 1–6 complete, all 75 pages built + wired + browser-approved

---

## RESUME POINT — Read Before Every Session

**Current phase:** C5 — Post-Deploy Smoke + Production Sign-Off
**First file to open every session:** `SYSTEM-SNAPSHOT.md` → this file → `PENDING.md` Commercialisation section
**Rule in force:** C0 seal must be verified before running any tool. PAGE-BUILD-PROTOCOL.md governs every page fix found during testing. No new page builds without explicit approval.

| Phase | Name | Status |
|---|---|---|
| C0 | Environment Seal | ✓ COMPLETE 2026-05-31 |
| C1 | DB Wiring (local) | ✓ COMPLETE 2026-05-31 |
| C2 | Automated Test Suite (local) | ✓ COMPLETE 2026-06-01 |
| C3 | Code Hardening (local) | ✓ COMPLETE 2026-06-01 |
| C4 | Infrastructure Deployment (Render.com) | ✓ COMPLETE 2026-06-01 — all 5 services LIVE on free tier; gateway + services + frontend + postgres + redis |
| C5 | Post-Deploy Smoke + Production Sign-Off | ⬜ pending |
| C6 | Commercial Launch | ⬜ pending |

**Phase gate rule:** Each phase must reach its stated gate criterion before the next phase starts. No exceptions. No parallel execution across gate boundaries.

---

## Session Resumption Protocol

Every session MUST follow this sequence before any work:

1. Read `SYSTEM-SNAPSHOT.md` — 60-second orientation: what is built, what is next
2. Read this file — confirm current phase from the RESUME POINT table above
3. Read `PENDING.md` Commercialisation section — find first unchecked `[ ]`
4. Verify C0 seal is active (run `.env.local` loader — see C0 §Step 4)
5. Execute the task

**Session close (mandatory before ending every session):**
1. Mark completed tasks `[x]` in `PENDING.md`
2. Update RESUME POINT table above — correct current phase
3. Update **Status** line at the top of this file
4. Add one-line summary to `PROGRESS.md`
5. Commit with semantic message (see `CONTRIBUTING.md`)
6. Push to GitHub — run `git status` first, confirm clean

---

## Non-Negotiable Rules (all phases, always)

| Rule | Source |
|---|---|
| C0 seal must be verified before running any tool that could write to C: | This file §C0 |
| Every page defect found during testing must be fixed via `PAGE-BUILD-PROTOCOL.md` T1–T4 | This file §C2c |
| `JAZZCASH_STUB_MODE=true` until P-016 credentials + full sandbox E2E verified | `CONSTRAINTS.md C-009` |
| All `_STRINGS['ur']` need native Urdu speaker sign-off before any customer send | `CONSTRAINTS.md C-010` |
| All 96 library pages must return HTTP 200 after every push | `REBUILD-PLAN.md` — carried forward |
| Every new `.md` file catalogued in `DOC-CATALOGUE.md` same day it is written | `DOC-CATALOGUE.md` rule |
| `core/*` must never import `adapters/pakistan/*` | ADR-001, ADR-002 — ruff CI enforced |
| Report back after each sub-phase gate; wait for confirmation before proceeding | Phase 4 protocol — carried forward |
| No new page builds without explicit scope approval | `CLAUDE.md` scope gate |

---

## Permanently Blocked Items (carried forward, do not attempt)

| ID | Item | Blocked by | Runtime behaviour |
|---|---|---|---|
| P-016 | JazzCash/Easypaisa production callbacks | Real credentials + sandbox E2E | `JAZZCASH_STUB_MODE=true` — static stub badge |
| P-017 | Urdu customer-facing strings | Native speaker sign-off | English + `<!-- UR_TODO: -->` comment |
| MR-001 | Facebook/Instagram lead capture | Meta Business Manager setup | Hidden div `data-unblock="MR-001"` |
| MR-003 | Voice note transcription | Transcription provider + credentials | Microphone icon `disabled` |
| MR-007 | Kuickpay adapter | Kuickpay API credentials | Not rendered |

---

## Build Phase Carry-Forward State

The following is the inherited state from `REBUILD-PLAN.md` at closure. Do not re-derive — read it as ground truth.

| Item | State at closure |
|---|---|
| Custom pages | 75/75 built · T1–T4 ✓ · wired to live API · browser-approved |
| Library pages | 96/96 HTTP 200 (last verified 2026-05-30) |
| Gateway routes | 42 inline routes under `/api/v1/` |
| Backend services | 38 ORM models · Alembic migrations 0001→0010 · ~527+ tests |
| In-memory stores | All 42 gateway routes use in-memory `_store` — replaced by PostgreSQL in C1 |
| Coverage gate | 70% (`--cov-fail-under=70` in `.github/workflows/ci.yml`) — raised to 80% in C2 |
| DUMMY_MODE | `false` in `crm-api.js` — all pages call live API with graceful dummy fallback |
| Deferred items | A-006 (Redis rate-limit), A-007 (FeatureFlag Redis cache) — addressed in C3 |

---

## C0 — Environment Seal

**Purpose:** Guarantee zero silent writes to C: before any commercialisation tool runs. This phase runs once and its results are documented. It is a hard gate — C1 cannot start until all tool cache locations are confirmed on D:.

**Why this is the first phase:** Tools like Docker, npm, pip, Playwright, and OWASP ZAP silently write browser binaries, package caches, image layers, and driver files to `C:\Users\Admin\AppData\...` by default. These writes have no error, no warning, and no indication they happened. One forgotten env var and gigabytes land on C:. The seal is established once, verified, and then loaded at the start of every subsequent session.

### Step 1 — Create `D:\CRM\.env.local`

This file is gitignored. It must exist before any tool in C1–C6 is run.

```
PLAYWRIGHT_BROWSERS_PATH=D:\CRM\.playwright-browsers
SE_CACHE_PATH=D:\CRM\.selenium-cache
PIP_CACHE_DIR=D:\pip-cache
NPM_CONFIG_CACHE=D:\npm-cache
DOCKER_DATA_ROOT=D:\DockerData
ZAP_HOME=D:\ZAP
LOCUST_LOG_DIR=D:\CRM\tests\load\logs
```

### Step 2 — Verify each tool's write location before first use

| Tool | Verify command | Expected result | Fix if on C: |
|---|---|---|---|
| npm cache | `npm config get cache` | `D:\npm-cache` | `npm config set cache D:\npm-cache` |
| pip cache | `D:\CRM\backend\.venv\Scripts\pip cache dir` | `D:\pip-cache` | Env var above |
| Python Playwright | `echo $env:PLAYWRIGHT_BROWSERS_PATH` | `D:\CRM\.playwright-browsers` | Set env var, then `playwright install chromium` |
| Docker Desktop | Docker Desktop → Settings → Resources → Disk image location | `D:\DockerData` | Change in UI, restart Docker |
| OWASP ZAP | Use portable zip only — extract to `D:\ZAP` | No `C:\Program Files` entry | Never use the Windows installer |
| Locust | `D:\CRM\backend\.venv\Scripts\locust --version` | Version printed, no C: write | No action (pure Python) |
| pytest / httpx | Runs inside D: venv | No C: write | No action |
| semgrep | `pip install semgrep` into D: venv | `D:\CRM\backend\.venv\...` | No action |
| pip-audit | `pip install pip-audit` into D: venv | `D:\CRM\backend\.venv\...` | No action |
| Node in gateway | Already at `D:\CRM\frontend\node_modules` | No global installs needed | Confirm `npm config get prefix` |

### Step 3 — Playwright one-time browser install (Chromium to D:)

```powershell
# Load seal first
Get-Content D:\CRM\.env.local | ForEach-Object { $k,$v = $_ -split '=',2; [System.Environment]::SetEnvironmentVariable($k,$v,'Process') }
# Install Chromium to D:\CRM\.playwright-browsers
D:\CRM\backend\.venv\Scripts\playwright install chromium
# Verify — should show D: path
D:\CRM\backend\.venv\Scripts\playwright install --dry-run chromium
```

Expected: `~130MB` downloaded to `D:\CRM\.playwright-browsers\chromium-*`. Verify with `Get-ChildItem D:\CRM\.playwright-browsers`.

### Step 4 — C: baseline + per-tool delta check

```powershell
# Record C: free space before any tool run
(Get-PSDrive C).Free | Out-File D:\CRM\c-seal\baseline.txt
# After running each new tool for the first time:
(Get-PSDrive C).Free | Out-File D:\CRM\c-seal\after-<toolname>.txt
# Compare — if delta > 2MB, investigate before proceeding
```

Create `D:\CRM\c-seal\` directory. Keep all baseline and delta files. Any unexpected growth stops the phase.

### Step 5 — Session startup loader (run at start of every C1–C6 session)

```powershell
Get-Content D:\CRM\.env.local | ForEach-Object { $k,$v = $_ -split '=',2; [System.Environment]::SetEnvironmentVariable($k,$v,'Process') }
```

Add this as a one-liner to session notes or a `D:\CRM\seal.ps1` script. Running any tool without this loader active is a protocol violation.

### C0 Gate

All items in the Step 2 table show D: locations. C: delta after first run of each tool is < 2MB. `D:\CRM\c-seal\baseline.txt` exists with a recorded value. Only then: proceed to C1.

---

## C1 — DB Wiring (local)

**Purpose:** Replace all 42 gateway in-memory `_store` objects with real PostgreSQL queries. After C1, the system runs end-to-end on a real database locally — no data is lost on gateway restart.

**Prerequisite:** C0 gate passed. Docker Desktop data root set to `D:\DockerData`.

### Step 1 — Start local PostgreSQL via docker-compose

```powershell
# From D:\CRM\backend
docker-compose up -d postgres redis
# Verify
docker-compose ps
```

PostgreSQL available at `localhost:5432`, Redis at `localhost:6379`.

### Step 2 — Run Alembic migration chain

```powershell
# From D:\CRM\backend, with D: venv active
D:\CRM\backend\.venv\Scripts\alembic upgrade head
# Verify chain 0001→0010 applied
D:\CRM\backend\.venv\Scripts\alembic current
```

Expected: `0010_ai_scores_schema (head)`.

### Step 3 — Replace in-memory stores (42 route files)

For each gateway route file in `D:\CRM\backend\gateway\routes\`:
1. Replace `let _store = [...]` / `const _store = {}` with `const { Pool } = require('pg')` + pool instance
2. Replace in-memory CRUD with SQL queries (`SELECT`, `INSERT`, `UPDATE`)
3. Keep the same response shape — no frontend changes required
4. Preserve inline Pakistan-locale seed data as a `seed()` function called once on startup

**Priority order:**
1. Core domain routes (leads, followups, contacts, accounts, opportunities) — these serve the most pages
2. Collections and invoice routes — financial data, needs persistence
3. Phase 6 inline stubs (billing, integrations, governance, reports, communications) — lowest priority; seed data is small

### Step 4 — Seed staging data

```powershell
node D:\CRM\backend\gateway\scripts\seed_staging.js
```

Create this script to insert Pakistan-locale seed rows into all tables. Mirrors the in-memory data that was in the `_store` arrays.

### Step 5 — Smoke verify all 42 routes

```powershell
# Start gateway
node D:\CRM\backend\gateway\app.js
# Run route smoke check
D:\CRM\backend\.venv\Scripts\pytest tests\api\test_smoke_all_routes.py -v
```

### C1 Gate

All 42 routes return `{ data: [...] }` with non-empty arrays from PostgreSQL. Gateway restart does not lose data. `alembic current` shows `0010 (head)`.

---

## C2 — Automated Test Suite (local, C0 seal in force)

**Purpose:** Full automated verification of every layer — backend, API contracts, all 75 frontend pages, load, and security — with zero human browser interaction. Every failure produces a finding; every page finding is fixed via PAGE-BUILD-PROTOCOL.md before the phase closes.

**Prerequisite:** C1 gate passed. C0 seal loader run at session start.

**Sub-phase order is strict.** Each gate must pass before the next sub-phase starts.

---

### C2a — Backend Coverage (pytest)

**Tool:** pytest + pytest-cov — already in `D:\CRM\backend\.venv`
**Target:** 80% coverage (`--cov-fail-under=80`)
**Current baseline:** ~527 tests passing at 70% coverage

```powershell
D:\CRM\backend\.venv\Scripts\pytest --cov=. --cov-report=term-missing --cov-fail-under=80
```

Identify uncovered modules. Add targeted tests until gate passes. Focus on the 5 new Phase 6 route files (billing, integrations, governance, reports, communications) which have no tests yet.

**C2a Gate:** `pytest --cov-fail-under=80` exits 0.

---

### C2b — API Contract Tests (pytest + httpx)

**Tool:** httpx — `pip install httpx` into D: venv
**Gateway must be running** at `localhost:3000` during this sub-phase.

**Test files to create:**
```
D:\CRM\tests\api\
  test_smoke_all_routes.py      — all 42 routes return HTTP 200 with valid envelope
  test_billing_contract.py      — /billing/subscription shape, /billing/invoices shape
  test_integrations_contract.py — /integrations list shape, POST /test returns {ok, latency_ms}
  test_governance_contract.py   — /governance/sar POST creates 30-day due_date
  test_reports_contract.py      — POST /reports/execute returns series[6], valid metric_key
  test_communications_contract.py — /communications/engagement returns all 8 fields
  test_auth_contract.py         — invalid JWT → 401, missing tenant → 403
  test_tenant_isolation.py      — tenant A cannot read tenant B data
```

**What each contract test checks:**
- HTTP status code (200, 201, 400, 401, 403, 404, 422 as appropriate)
- Response envelope: `{ data: ..., meta: { request_id: ... } }`
- Required fields present in `data` (field names, not values)
- Error envelope on bad input: `{ error: { code, message }, meta: ... }`
- Tenant isolation: same resource with different `x-tenant-id` returns empty/404

```powershell
D:\CRM\backend\.venv\Scripts\pytest D:\CRM\tests\api\ -v
```

**C2b Gate:** 0 contract failures. All 42 routes respond with correct envelope shape.

---

### C2c — Frontend E2E (Python Playwright)

**Tool:** Playwright for Python — `pip install playwright` into D: venv; browsers at `D:\CRM\.playwright-browsers`
**PAGE-BUILD-PROTOCOL.md is the mandatory anchor for every page defect found here.**

**CRITICAL RULE:** Any page that fails a Playwright test is not simply marked as a test failure and moved on. It enters a fix loop:
1. Read the failing page's current HTML and JS driver fully
2. Diagnose against T1 (structure) / T2 (data) / T3 (alignment) / T4 (behaviour)
3. Apply the fix per `PAGE-BUILD-PROTOCOL.md` rules — no ad-hoc edits
4. Re-run the test for that page only
5. Only when the test passes: proceed to the next page

**Test files:**
```
D:\CRM\tests\e2e\playwright\
  conftest.py                   — browser fixture, BASE_URL, screenshot on failure
  test_page_load.py             — all 75 pages: HTTP 200, sidebar present, header present, no JS errors
  test_kpi_render.py            — all dashboard pages: KPI tile text is non-empty
  test_datatable.py             — all list/queue pages: tbody has ≥1 row after load
  test_filter_chips.py          — filter pill click changes visible row count
  test_form_submit.py           — lead-new, contact-new: form submits without 4xx/5xx
  test_workflow_onboarding.py   — full onboarding: register → first lead → first followup → mark complete
  test_workflow_invoice.py      — create invoice → send → simulate payment callback → status = paid
  test_workflow_report.py       — report builder: select 2 metrics → Preview → chart canvas renders
  test_settings_pages.py        — all G-series pages: settings nav renders, save button present
  test_audit_pages.py           — J-series pages: DataTable rows present, export button visible
```

**Run:**
```powershell
# Load C0 seal first
Get-Content D:\CRM\.env.local | ForEach-Object { $k,$v = $_ -split '=',2; [System.Environment]::SetEnvironmentVariable($k,$v,'Process') }
# Run all E2E tests (headless)
D:\CRM\backend\.venv\Scripts\pytest D:\CRM\tests\e2e\playwright\ -v --tb=short
```

Screenshots saved to `D:\CRM\tests\e2e\playwright\screenshots\` on failure. Videos saved on retry.

**C2c Gate:** All 75 pages pass `test_page_load.py`. All workflow scenario tests pass. Zero pages with unfixed defects. Every fix applied followed PAGE-BUILD-PROTOCOL.md T1–T4.

---

### C2d — Load Tests (Locust)

**Tool:** Locust — `pip install locust` into D: venv. Pure Python, zero C: writes.
**Gateway and PostgreSQL must be running.**

**File:** `D:\CRM\tests\load\locustfile.py`

**Scenarios and targets:**

| Scenario | Endpoint(s) | Users | Ramp | p95 target |
|---|---|---|---|---|
| Follow-up queue browse | GET /followups | 50 | 10/s | < 500ms |
| Lead creation burst | POST /leads | 100 | 20/s | < 800ms |
| Collections queue | GET /collections + GET /invoice-summaries | 50 | 10/s | < 500ms |
| Cases CRUD | GET /cases + POST /cases | 50 | 10/s | < 600ms |
| Inbox claim + send | GET /inbox/conversations + POST /inbox/:id/claim | 30 | 5/s | < 700ms |
| Full onboarding flow | POST /activation/start → GET /leads → POST /followups | 20 | 2/s | < 2000ms |

**Run:**
```powershell
D:\CRM\backend\.venv\Scripts\locust --headless -f D:\CRM\tests\load\locustfile.py `
  --host=http://localhost:3000 --users=50 --spawn-rate=10 --run-time=60s `
  --html=D:\CRM\tests\load\reports\report-$(Get-Date -Format yyyyMMdd-HHmm).html
```

**C2d Gate:** All scenarios meet p95 targets at stated concurrency levels. No 5xx responses during load run.

---

### C2e — Security Scanning

**All tools run locally. All write to D:. C0 seal must be active.**

#### pip-audit (Python CVE scan)
```powershell
D:\CRM\backend\.venv\Scripts\pip-audit
```
**Gate:** 0 Critical CVEs.

#### npm audit (Node CVE scan)
```powershell
npm audit --prefix D:\CRM\frontend
```
**Gate:** 0 Critical CVEs.

#### semgrep (SAST)
```powershell
D:\CRM\backend\.venv\Scripts\semgrep --config=auto D:\CRM\backend\ `
  --include="*.py" --include="*.js" `
  --output=D:\CRM\tests\security\semgrep-report.json --json
```
Focus rules: `python.lang.security.injection`, `javascript.lang.security.injection`, `generic.secrets`, tenant isolation (every SQL query must bind `tenant_id`).

**Gate:** 0 High/Critical findings. Any finding blocks C3.

#### OWASP ZAP (active API scan)

**Install:** Download portable zip from `https://www.zaproxy.org/download/` — extract to `D:\ZAP`. Never use the Windows installer.

**Gateway must be running** at `localhost:3000`.

```powershell
# Start ZAP daemon
& D:\ZAP\zap.sh -daemon -host 127.0.0.1 -port 8090 -config api.disablekey=true
# Run baseline scan against gateway
& D:\ZAP\zap.sh -cmd -quickurl http://localhost:3000/api/v1 `
  -quickout D:\CRM\tests\security\zap-report.html -quickprogress
```

**Gate:** 0 High/Critical findings in the ZAP report.

#### C2e Gate

All four scanners produce reports stored in `D:\CRM\tests\security\`. All gates pass. Reports committed to repo under `tests/security/`.

---

### C2 Overall Gate

All five sub-phases (C2a through C2e) pass their individual gates. No outstanding page defects from C2c. Security scan reports clean. Only then: proceed to C3.

---

## C3 — Code Hardening (local)

**Purpose:** Close the remaining deferred technical debt items and add production-grade reliability before deployment. All changes are local code changes — no infrastructure required.

**Prerequisite:** C2 gate passed.

### Deferred items from build phases (must resolve in C3)

| Item | File(s) | What to do |
|---|---|---|
| A-006 — Redis rate-limit | `backend/gateway/middleware/rate-limit-hook.js` | Swap in-memory token buckets for Redis (`ioredis`). Use `D:\DockerData` Redis from docker-compose. |
| A-007 — FeatureFlag Redis cache | `backend/gateway/routes/v1-feature-flags-mgmt.routes.js` | Cache flag evaluations in Redis with 60s TTL. |

### New hardening items

| Item | File(s) | What to do |
|---|---|---|
| JWT refresh token flow | `backend/gateway/routes/v1-auth.routes.js` + `crm-api.js` | `POST /auth/refresh` — short-lived access token (15min) + long-lived refresh token (7d). Store refresh token in `httpOnly` cookie. |
| Security headers | `backend/gateway/app.js` | Add `helmet()` middleware. Sets CSP, X-Frame-Options, HSTS, X-Content-Type-Options. |
| CORS allowlist | `backend/gateway/app.js` | Replace `origin: '*'` with explicit allowlist: `['http://localhost:3001', 'https://yourcrm.pk']`. |
| Password reset OTP flow | `backend/gateway/routes/v1-auth.routes.js` | `POST /auth/forgot-password` → generate 6-digit OTP, store in Redis (15min TTL) → `POST /auth/reset-password` → validate OTP, update hash. |
| Multi-tenant signup | `backend/gateway/routes/v1-auth.routes.js` | `POST /auth/register` → create tenant record → seed default pipeline via Activation Engine → return JWT. |
| Tenant isolation Semgrep rule | `.semgrep/tenant-isolation.yaml` | Custom rule: any `SELECT/INSERT/UPDATE/DELETE` in gateway JS must include `tenant_id` bind param. CI blocks on violation. |
| Email transactional (stub) | `backend/gateway/routes/v1-auth.routes.js` | `sendEmail(to, subject, body)` — log to console in dev, call SendGrid in prod (env var `SENDGRID_API_KEY`). Used by OTP + invite flows. |

### C3 Gate

All deferred items implemented. `helmet()` active on all routes. CORS restricted. JWT refresh flow working. `POST /auth/register` creates a tenant and returns a valid JWT. Redis rate-limit confirmed writing to `D:\DockerData` Redis. 0 new semgrep findings introduced.

---

## C4 — Infrastructure Deployment (Render.com + GitHub Actions)

**Purpose:** Deploy the fully tested, hardened local system to production infrastructure on Render.com with automated CI/CD via GitHub Actions.

**Prerequisite:** C3 gate passed. All local tests green.

### Step 1 — Render.com service setup

Create the following services in Render dashboard:

| Service | Type | Config |
|---|---|---|
| `crm-postgres` | PostgreSQL (managed) | Plan: Starter → scale as needed. Region: nearest to Pakistan. |
| `crm-redis` | Redis (managed) | Plan: Starter. |
| `crm-gateway` | Web Service (Node.js) | Root: `backend/gateway`. Build: `npm install`. Start: `node app.js`. |
| `crm-services` | Web Service (Python) | Root: `backend`. Build: `pip install -r requirements.txt`. Start: `uvicorn services.app:app`. |
| `crm-frontend` | Static Site | Root: `frontend/src`. Publish directory: `.`. |

### Step 2 — Environment variables (Render Environment Groups)

Create a `crm-production` Environment Group with all secrets from `D:\CRM\.env.local` plus:

```
DATABASE_URL         — Render PostgreSQL internal URL
REDIS_URL            — Render Redis internal URL
JWT_SECRET           — strong random 256-bit hex
JWT_REFRESH_SECRET   — different strong random 256-bit hex
SKIP_JWT_VERIFICATION=false
NODE_ENV=production
WHATSAPP_TOKEN       — Meta token (when P-016 unblocked)
SENDGRID_API_KEY     — email OTP
ALLOWED_ORIGINS      — https://yourcrm.pk,https://www.yourcrm.pk
```

Never commit these values. They live in Render only.

### Step 3 — GitHub Actions CI/CD pipeline

File: `.github/workflows/ci.yml` (already exists — extend it)

```yaml
jobs:
  test-backend:     # pytest --cov-fail-under=80
  test-api:         # pytest tests/api/
  security-scan:    # pip-audit + npm audit + semgrep
  build-gateway:    # docker build backend/gateway
  build-services:   # docker build backend/services
  deploy-staging:   # Render deploy hook (staging env) — on PR merge to main
  smoke-staging:    # pytest tests/api/ against staging URL
  deploy-prod:      # Render deploy hook (prod env) — on git tag v*.*.*
```

**Deploy flow:**
- PR merge to `main` → deploy to staging → run smoke tests → pass = staging green
- `git tag v1.0.0 && git push --tags` → deploy to prod → run smoke tests

### Step 4 — Alembic migrations on Render PostgreSQL

```powershell
# One-time: run migration against production DB via Render shell
DATABASE_URL=<render-postgres-url> alembic upgrade head
```

### C4 Gate

`curl https://api.yourcrm.pk/api/v1/health` returns `{"status":"ok","version":"1.0.0"}` with zero manual steps. All GitHub Actions jobs pass on `main`. Staging environment matches local test results.

---

## C5 — Post-Deploy Smoke + Production Sign-Off

**Purpose:** Run the same automated test suite from C2 against the live Render.com production URL. Any failure is treated identically to a C2c failure — PAGE-BUILD-PROTOCOL.md governs every page fix.

**Prerequisite:** C4 gate passed.

### Step 1 — Point test suite at production

```powershell
$env:BASE_URL = "https://app.yourcrm.pk"
$env:API_BASE_URL = "https://api.yourcrm.pk/api/v1"
```

### Step 2 — Run smoke suite

```powershell
# API contracts against production
D:\CRM\backend\.venv\Scripts\pytest D:\CRM\tests\api\ -v --base-url=$env:API_BASE_URL

# Playwright E2E against production
D:\CRM\backend\.venv\Scripts\pytest D:\CRM\tests\e2e\playwright\ -v --base-url=$env:BASE_URL

# Load test at 50 concurrent against staging (not prod — protect real users)
D:\CRM\backend\.venv\Scripts\locust --headless -f D:\CRM\tests\load\locustfile.py `
  --host=https://staging-api.yourcrm.pk --users=50 --spawn-rate=10 --run-time=60s
```

### Step 3 — OWASP ZAP against production API

```powershell
& D:\ZAP\zap.sh -cmd -quickurl https://api.yourcrm.pk/api/v1 `
  -quickout D:\CRM\tests\security\zap-prod-report.html -quickprogress
```

**Gate:** 0 High/Critical findings on prod URL.

### Step 4 — 96 library pages HTTP 200 verification

```powershell
# Playwright test_page_load.py already covers all 75 custom pages
# Add library page check separately
D:\CRM\backend\.venv\Scripts\pytest D:\CRM\tests\e2e\playwright\test_library_pages.py -v
```

### C5 Gate

All C2 test suite results replicate on production. 96 library pages HTTP 200. 75 custom pages pass Playwright suite. OWASP ZAP prod scan clean. Zero unfixed page defects. Load test p95 targets met on staging.

---

## C6 — Commercial Launch

**Purpose:** Final audit, version tagging, and GitHub push. This phase is documentation and process — no new code.

**Prerequisite:** C5 gate passed.

### Step 1 — Final grade audit

Re-run the Current State vs Target assessment from `REBUILD-PLAN.md` against the live production system. All 8 areas should now be 10/10:

| Area | Expected score after C3 |
|---|---|
| Documentation | 10/10 — no change needed |
| Architecture design | 9/10 — event bus still not wired; ML still rule-based |
| Project structure | 10/10 — containers in CI (C4), staging deploy (C4) |
| Code implementation | 10/10 — Redis rate-limit (C3), JWT refresh (C3) |
| Testing | 10/10 — 80% coverage (C2a), load tests (C2d), E2E (C2c) |
| DevOps / CI-CD | 10/10 — Docker + staging deploy (C4) |
| Security | 9.5/10 — OWASP clean, semgrep clean; no pen test yet |
| Frontend | 10/10 — no change needed |

### Step 2 — CHANGELOG v1.0.0 entry

Add `## [1.0.0] — YYYY-MM-DD — Commercial launch` to `CHANGELOG.md` with summary of C0–C6 work.

### Step 3 — Tag and push

```powershell
git add -A
git commit -m "chore(launch): v1.0.0 commercial launch — C0-C6 complete"
git tag v1.0.0
git push origin main --tags
```

### Step 4 — Update anchor docs

- `SYSTEM-SNAPSHOT.md` — final score update, date, C6 complete
- `PENDING.md` — all commercialisation tasks marked `[x]`
- `PROGRESS.md` — final session summary line
- This file — all phases marked ✓ in RESUME POINT table

### C6 Gate

`git tag v1.0.0` pushed. All CI/CD jobs green on the tagged commit. `SYSTEM-SNAPSHOT.md` reflects final scores. `PENDING.md` 100% complete.

---

## Phase Dependency Map

```
C0 (Environment Seal)
  └─► C1 (DB Wiring)
        └─► C2a (Backend Coverage)  ─┐
            C2b (API Contracts)      ├─► C2 Gate ─► C3 (Code Hardening)
            C2c (Playwright E2E)     │                └─► C4 (Render Deploy)
            C2d (Load Tests)         │                      └─► C5 (Prod Smoke)
            C2e (Security Scan) ─────┘                            └─► C6 (Launch)
```

C2 sub-phases (a through e) run in strict order — each gate before the next starts.
C2e (security scanning) can start once C1 is complete — it does not depend on C2a–C2d.

---

## Tool Inventory (all on D:, C0 sealed)

| Tool | Location | Used in |
|---|---|---|
| Python 3.12.10 | `D:\Python\python.exe` | All Python tools |
| Python venv | `D:\CRM\backend\.venv` | pytest, playwright, locust, semgrep, pip-audit, httpx |
| Playwright Chromium | `D:\CRM\.playwright-browsers` | C2c |
| Node.js + npm | `D:\CRM\frontend\node_modules` | Gateway, npm audit |
| npm cache | `D:\npm-cache` | npm operations |
| pip cache | `D:\pip-cache` | pip install operations |
| Docker data | `D:\DockerData` | PostgreSQL + Redis containers |
| OWASP ZAP portable | `D:\ZAP` | C2e, C5 |
| C: seal baseline | `D:\CRM\c-seal\` | C0 verification records |
| Load test reports | `D:\CRM\tests\load\reports\` | C2d |
| Security reports | `D:\CRM\tests\security\` | C2e, C5 |
| E2E screenshots | `D:\CRM\tests\e2e\playwright\screenshots\` | C2c failure captures |

---

## Reference Documents

| Document | Purpose |
|---|---|
| `REBUILD-PLAN.md` | **CLOSED** — build phases 1–6 historical record |
| `SYSTEM-SNAPSHOT.md` | Current project state — read first every session |
| `PENDING.md` | Task checklist — Commercialisation section |
| `PROGRESS.md` | Session-by-session log |
| `SCREEN-ARTEFACTS.md` | QC records for all 75 custom pages |
| `DESIGN-SPEC.md` | 75 custom pages, archetypes A–M |
| `PAGE-BUILD-PROTOCOL.md` | **Mandatory anchor for every page fix in C2c and C5** |
| `FRAMEWORK.md` | Build rules, QC tiers T1–T4 |
| `backend/CONSTRAINTS.md` | 17 build constraints — never violate |
| `backend/FRONTEND-BACKEND-MAPPING.md` | Frontend↔API wiring reference |
| `DOC-CATALOGUE.md` | Master index of all .md files |
| `backend/gateway/README.md` | 42 gateway routes reference |
