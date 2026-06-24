# VALIDATION_COMMANDS.md — Pakistan CRM OS
**Generated:** 2026-06-21 — U9 Runnable Command Reference
**Platform:** Windows 10 Pro (primary shell: PowerShell 5.1); bash also available via Git Bash
**Workspace root:** D:\SaaS\CRM
**Python venv:** D:\SaaS\CRM\backend\.venv
**Node:** C:\Program Files\nodejs\node.exe (system PATH)
**npm cache:** D:\npm-cache (env override)
**Playwright browsers:** D:\dev-cache\playwright

---

## Environment Validation

### Verify Python is accessible (venv only — no system python)

```powershell
# Verify venv python exists and its version
D:\SaaS\CRM\backend\.venv\Scripts\python.exe --version
# Expected: Python 3.12.x

# Verify venv pip exists
D:\SaaS\CRM\backend\.venv\Scripts\pip.exe --version
# Expected: pip 25.0.1 from D:\SaaS\CRM\backend\.venv\...
```

```bash
# Bash equivalent:
D:/SaaS/CRM/backend/.venv/Scripts/python.exe --version
```

### Activate venv (PowerShell)

```powershell
D:\SaaS\CRM\backend\.venv\Scripts\Activate.ps1
# After activation: prompt shows (.venv)
# Verify: python --version should now work
```

### Verify Node.js

```powershell
node --version
# Expected: v20.x.x

npm --version
# Expected: 10.x.x

# Verify npm cache is on D:
npm config get cache
# Expected: D:\npm-cache (from env override)
```

### Verify all critical env vars set

```powershell
# Check workspace-sealing env vars
$env:npm_config_cache          # Expected: D:\npm-cache
$env:PLAYWRIGHT_BROWSERS_PATH  # Expected: D:\dev-cache\playwright
$env:TEMP                      # Expected: D:\Temp
$env:TMP                       # Expected: D:\Temp

# Check if gateway env vars are set (for local dev)
# These should be in a .env file that you source manually:
$env:JWT_SECRET                # Should be set for local gateway
$env:DATABASE_URL              # Should be set for local PostgreSQL
$env:REDIS_URL                 # Should be set for local Redis
$env:NODE_ENV                  # Should be: development (local) or production (Render)
```

### Verify Playwright browsers are present

```powershell
# Check D:\dev-cache\playwright contains a chromium directory:
Get-ChildItem D:\dev-cache\playwright | Select-Object Name
# Expected: chromium-XXXXX directory

# Or check via .npmrc setting:
Get-Content D:\SaaS\CRM\frontend\.npmrc
# Should show: playwright_browsers_path=D:\CRM\.playwright-browsers
```

---

## Backend Tests

### Run all pytest tests (from backend directory)

```powershell
Set-Location D:\SaaS\CRM\backend
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  --ignore=.venv `
  -q `
  --tb=short
```

```bash
# Bash equivalent:
cd /d/SaaS/CRM/backend
.venv/Scripts/python.exe -m pytest --ignore=.venv -q --tb=short
```

### Run all tests with coverage report (CI gate command)

```powershell
Set-Location D:\SaaS\CRM\backend
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  --cov=. `
  --cov-report=term-missing `
  --cov-report=xml:coverage.xml `
  --cov-fail-under=80 `
  -q `
  --tb=short `
  --ignore=.venv
# Pass: exits 0, shows "80 passed" or similar
# Fail: exits 1 if coverage < 80% OR any test fails
```

### Run only a specific module's tests

```powershell
# Example: run only lead management tests
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  D:\SaaS\CRM\backend\tests\test_lead_management.py `
  -v --tb=long

# Example: run only Pakistan payment adapter tests
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  D:\SaaS\CRM\backend\tests\test_pakistan_payment_adapters.py `
  -v --tb=long

# Example: run only security-related tests
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  D:\SaaS\CRM\backend\tests\test_system_hardening_qc.py `
  D:\SaaS\CRM\backend\tests\test_final_supervisor_qc.py `
  -v --tb=long
```

### Run only fast unit tests (exclude slow/integration tests)

```powershell
# Skip tests marked as slow or integration (if markers are used):
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  --ignore=.venv `
  -m "not slow and not integration" `
  -q --tb=short

# If no pytest marks used, exclude by file pattern:
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  --ignore=.venv `
  --ignore=D:\SaaS\CRM\backend\tests\test_integration_end_to_end_qc.py `
  --ignore=D:\SaaS\CRM\backend\tests\test_concurrency_lock_cluster.py `
  -q --tb=short
```

### Run backend linting (ruff + black)

```powershell
Set-Location D:\SaaS\CRM\backend
D:\SaaS\CRM\backend\.venv\Scripts\ruff.exe check . --exclude .venv
D:\SaaS\CRM\backend\.venv\Scripts\black.exe --check . --exclude ".venv"

# Architecture guard (ADR-002 — adapter boundary):
D:\SaaS\CRM\backend\.venv\Scripts\ruff.exe check services/core/ --select TID251
```

---

## Frontend / E2E Tests

### Prerequisites: frontend dev server must be running on port 3001

```powershell
# Start the frontend dev server (npm run serve from frontend directory):
Set-Location D:\SaaS\CRM\frontend
npm run serve
# Serves D:\SaaS\CRM\frontend\src at http://localhost:3001
# Run this in a separate terminal — it stays running
```

### Run all Playwright tests (headless, default)

```powershell
Set-Location D:\SaaS\CRM
$env:BASE_URL = "http://localhost:3001"
$env:PLAYWRIGHT_BROWSERS_PATH = "D:\dev-cache\playwright"
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  tests/e2e/playwright/ `
  -q --tb=short
```

```bash
# Bash equivalent:
cd /d/SaaS/CRM
BASE_URL=http://localhost:3001 PLAYWRIGHT_BROWSERS_PATH=D:/dev-cache/playwright \
  /d/SaaS/CRM/backend/.venv/Scripts/python.exe -m pytest \
  tests/e2e/playwright/ -q --tb=short
```

### Run headed (visible browser) for debugging a specific test

```powershell
# Override headless to False by setting env variable (requires conftest.py to read PWHEADLESS)
# Current conftest.py hardcodes headless=True — to run headed, temporarily edit conftest.py
# OR pass env var if supported:
$env:PWHEADLESS = "0"  # Only works if conftest.py reads this variable
$env:BASE_URL = "http://localhost:3001"
$env:PLAYWRIGHT_BROWSERS_PATH = "D:\dev-cache\playwright"
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  tests/e2e/playwright/test_page_load.py::test_page_loads_with_shell[dashboard.html] `
  -v --tb=long -s
```

### Run a specific Playwright test file

```powershell
# Run only page load tests (all 75 pages):
$env:BASE_URL = "http://localhost:3001"
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  tests/e2e/playwright/test_page_load.py `
  -v --tb=short

# Run only DataTable tests:
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  tests/e2e/playwright/test_datatable.py `
  -v --tb=short

# Run only functional lead tests:
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  tests/e2e/playwright/test_func_leads.py `
  -v --tb=short
```

### Run E2E tests against production (Render)

```powershell
$env:BASE_URL = "https://crm-frontend-0gde.onrender.com"
$env:PLAYWRIGHT_BROWSERS_PATH = "D:\dev-cache\playwright"
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  tests/e2e/playwright/test_prod_smoke.py `
  -v --tb=short
# Note: production tests use auth/register to create a test tenant; slow cold-start expected
```

---

## API Contract Tests

### Prerequisites: gateway must be running on port 3000

```powershell
# Start the gateway (in a separate terminal):
Set-Location D:\SaaS\CRM\backend\gateway
$env:NODE_ENV = "development"
$env:PORT = "3000"
$env:DATABASE_URL = "postgresql://crm:changeme@localhost:5432/crm_dev"
node server.js
# Leave running; confirm /dev-token responds:
Invoke-RestMethod -Uri http://localhost:3000/dev-token
```

### Run all API contract tests

```powershell
Set-Location D:\SaaS\CRM
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  tests/api/ `
  -q --tb=short
```

### Run only smoke test (44 routes)

```powershell
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe `
  tests/api/test_smoke_all_routes.py `
  -v --tb=short
```

---

## API Smoke Test (curl / httpx)

### Health check

```powershell
# Local gateway:
Invoke-RestMethod -Uri http://localhost:3000/health
# Expected: {"status":"ok"} or similar

# Production:
Invoke-RestMethod -Uri https://crm-gateway-l3rm.onrender.com/health
```

```bash
# Bash:
curl -sf http://localhost:3000/health | python -m json.tool
```

### Get a dev token (local only)

```powershell
$response = Invoke-RestMethod -Uri http://localhost:3000/dev-token
$token = $response.data.token
$tenantId = $response.data.tenant_id
Write-Host "Token: $token"
Write-Host "Tenant: $tenantId"
```

```bash
TOKEN=$(curl -sf http://localhost:3000/dev-token | python -c "import sys,json; d=json.load(sys.stdin); print(d['data']['token'])")
TENANT_ID=$(curl -sf http://localhost:3000/dev-token | python -c "import sys,json; d=json.load(sys.stdin); print(d['data']['tenant_id'])")
```

### Test auth login (POST /auth/login)

```powershell
$body = @{ email="owner@tenant.test"; password="Test1234!" } | ConvertTo-Json
Invoke-RestMethod -Method POST `
  -Uri http://localhost:3000/api/v1/auth/login `
  -ContentType "application/json" `
  -Body $body
# Expected: {data: {access_token, tenant_id}, meta: {request_id}}
```

```bash
curl -sf -X POST http://localhost:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@tenant.test","password":"Test1234!"}' | python -m json.tool
```

### Test authenticated GET (GET /api/v1/leads)

```powershell
# Assumes $token and $tenantId from dev-token above:
$headers = @{
    "Authorization" = "Bearer $token"
    "x-tenant-id" = $tenantId
    "Accept" = "application/json"
}
Invoke-RestMethod -Uri http://localhost:3000/api/v1/leads -Headers $headers
# Expected: {data: [...], meta: {request_id, total}}
```

```bash
curl -sf http://localhost:3000/api/v1/leads \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-tenant-id: $TENANT_ID" | python -m json.tool
```

### Test unauthenticated access (should return 401)

```powershell
try {
    Invoke-RestMethod -Uri http://localhost:3000/api/v1/leads
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
    # Expected: 401
}
```

```bash
curl -sf -o /dev/null -w "%{http_code}" http://localhost:3000/api/v1/leads
# Expected: 401
```

### Verify gateway routing (dev-token returns correct data shape)

```powershell
$dt = Invoke-RestMethod -Uri http://localhost:3000/dev-token
$dt.data | ConvertTo-Json
# Expected keys: token (JWT string), tenant_id (UUID), expires_in, dev_mode: true
```

---

## Security Tests

### Run c5 API security scan (local)

```powershell
Set-Location D:\SaaS\CRM
D:\SaaS\CRM\backend\.venv\Scripts\python.exe `
  tests/security/c5_api_security_scan.py `
  http://localhost:3000
# Expected: PASS on all 7 categories; exit 0
```

### Run c5 scan against production

```powershell
D:\SaaS\CRM\backend\.venv\Scripts\python.exe `
  tests/security/c5_api_security_scan.py `
  https://crm-gateway-l3rm.onrender.com
# Report saved to: tests/security/c5-api-security-report.json
```

### Run pip-audit (dependency CVE check)

```powershell
Set-Location D:\SaaS\CRM\backend
D:\SaaS\CRM\backend\.venv\Scripts\pip-audit.exe `
  --requirement requirements.txt `
  -o json `
  -f tests/security/pip-audit.json
# View summary:
D:\SaaS\CRM\backend\.venv\Scripts\pip-audit.exe --requirement requirements.txt
```

### Run semgrep (static analysis)

```powershell
Set-Location D:\SaaS\CRM
# Full auto scan:
D:\SaaS\CRM\backend\.venv\Scripts\semgrep.exe `
  --config=auto `
  D:\SaaS\CRM\backend\ `
  --include="*.py" --include="*.js" `
  --exclude=".venv" --exclude="node_modules" `
  --timeout=120 `
  --json -o tests/security/semgrep-report.json

# Custom tenant-isolation rule only:
D:\SaaS\CRM\backend\.venv\Scripts\semgrep.exe `
  --config=D:\SaaS\CRM\.semgrep\ `
  D:\SaaS\CRM\backend\gateway\routes\
```

---

## Load Tests

### Run standard locust load test (50 users, local)

```powershell
# Prerequisites: gateway running on port 3000
Set-Location D:\SaaS\CRM
$timestamp = Get-Date -Format 'yyyyMMdd-HHmm'
D:\SaaS\CRM\backend\.venv\Scripts\locust.exe `
  --headless `
  -f tests/load/locustfile.py `
  --host=http://localhost:3000 `
  --users=50 `
  --spawn-rate=10 `
  --run-time=60s `
  --html="tests/load/reports/report-$timestamp.html"
# Report saved to tests/load/reports/report-<timestamp>.html
```

```bash
# Bash equivalent:
cd /d/SaaS/CRM
/d/SaaS/CRM/backend/.venv/Scripts/locust --headless \
  -f tests/load/locustfile.py \
  --host=http://localhost:3000 \
  --users=50 --spawn-rate=10 --run-time=60s \
  --html="tests/load/reports/report-$(date +%Y%m%d-%H%M).html"
```

### Run locust against production (conservative — 20 users)

```powershell
$timestamp = Get-Date -Format 'yyyyMMdd-HHmm'
D:\SaaS\CRM\backend\.venv\Scripts\locust.exe `
  --headless `
  -f tests/load/locustfile.py `
  --host=https://crm-gateway-l3rm.onrender.com `
  --users=20 `
  --spawn-rate=5 `
  --run-time=60s `
  --html="tests/load/reports/prod-$timestamp.html"
```

---

## Build Validation

### Compile SASS (CSS build)

```powershell
Set-Location D:\SaaS\CRM\frontend
npm run build
# Compiles SCSS → CSS in src/assets/css/
# Expected: exits 0; no error messages
```

### Start frontend dev server

```powershell
Set-Location D:\SaaS\CRM\frontend
npm run serve
# Starts http-server at http://localhost:3001
# Leave running; press Ctrl+C to stop
```

### Verify frontend dev server is responding

```powershell
Invoke-RestMethod -Uri http://localhost:3001/app/dashboard.html -Method Head
# Expected: HTTP 200
```

```bash
curl -sf -o /dev/null -w "%{http_code}" http://localhost:3001/app/dashboard.html
# Expected: 200
```

### Check frontend for lint errors (ESLint if configured)

```powershell
# Gateway ESLint:
Set-Location D:\SaaS\CRM\backend\gateway
npm install
npx eslint . --ext .js --max-warnings 0
# Expected: no output (no warnings) or exit 0
```

### Start the Node.js gateway (dev mode)

```powershell
Set-Location D:\SaaS\CRM\backend\gateway
$env:NODE_ENV = "development"
$env:PORT = "3000"
$env:SKIP_JWT_VERIFICATION = "false"  # Set to "true" for dev token mode
node server.js
# Expected log: "CRM Gateway listening on port 3000"
```

### Verify gateway health after start

```powershell
Start-Sleep -Seconds 2
Invoke-RestMethod -Uri http://localhost:3000/health
# Expected: {"status":"ok",...}

# Also verify dev-token endpoint (development only):
Invoke-RestMethod -Uri http://localhost:3000/dev-token
# Expected: {data: {token, tenant_id, ...}, meta: {...}}
```

---

## Full Validation Sequence (Quick Pre-Release Checklist)

Run these in order to validate the workspace before a release:

```powershell
# Step 1: Backend lint
Set-Location D:\SaaS\CRM\backend
D:\SaaS\CRM\backend\.venv\Scripts\ruff.exe check . --exclude .venv
D:\SaaS\CRM\backend\.venv\Scripts\black.exe --check . --exclude ".venv"

# Step 2: Backend tests with coverage
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe --cov=. --cov-report=term-missing --cov-fail-under=80 -q --tb=short --ignore=.venv

# Step 3: Security scan (dependencies)
D:\SaaS\CRM\backend\.venv\Scripts\pip-audit.exe --requirement requirements.txt

# Step 4: Start gateway (in new terminal) + wait
# [Open new PowerShell]
# Set-Location D:\SaaS\CRM\backend\gateway; $env:NODE_ENV="development"; node server.js

# Step 5: API contract tests (requires gateway from Step 4)
Set-Location D:\SaaS\CRM
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe tests/api/ -q --tb=short

# Step 6: C5 API security scan (requires gateway)
D:\SaaS\CRM\backend\.venv\Scripts\python.exe tests/security/c5_api_security_scan.py http://localhost:3000

# Step 7: Start frontend dev server (in new terminal)
# [Open new PowerShell]
# Set-Location D:\SaaS\CRM\frontend; npm run serve

# Step 8: E2E Playwright tests (requires gateway + frontend from Steps 4 + 7)
Set-Location D:\SaaS\CRM
D:\SaaS\CRM\backend\.venv\Scripts\pytest.exe tests/e2e/playwright/ -q --tb=short

# Step 9: Load test (50 users, 60s) - optional, run before staging deploy
D:\SaaS\CRM\backend\.venv\Scripts\locust.exe --headless -f tests/load/locustfile.py --host=http://localhost:3000 --users=50 --spawn-rate=10 --run-time=60s --html="tests/load/reports/pre-release-$(Get-Date -Format 'yyyyMMdd-HHmm').html"
```

---

*End VALIDATION_COMMANDS.md*
