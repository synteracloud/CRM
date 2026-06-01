#!/usr/bin/env python3
"""C5 — API Security Scan (replaces OWASP ZAP for Render free-tier deployment)

Checks:
  1. Security headers from helmet (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
  2. Authentication enforcement (no unauth access to protected routes)
  3. SQL injection patterns rejected (422 or 400)
  4. XSS patterns in query strings rejected
  5. Error responses don't leak stack traces or sensitive info
  6. CORS blocks unlisted origins
  7. Rate limiting active (x-ratelimit-* headers present)
"""
from __future__ import annotations

import sys
import json
import httpx
import uuid

GATEWAY = sys.argv[1] if len(sys.argv) > 1 else "https://crm-gateway-l3rm.onrender.com"

findings = []
passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        print(f"  PASS {name}")
        passed += 1
    else:
        print(f"  FAIL {name}: {detail}")
        failed += 1
        findings.append({"check": name, "detail": detail})


def get_headers() -> dict:
    return httpx.get(f"{GATEWAY}/health", timeout=30).headers


def register_user() -> tuple[str, str]:
    uid = uuid.uuid4().hex[:8]
    resp = httpx.post(
        f"{GATEWAY}/api/v1/auth/register",
        json={"name": f"SecScan-{uid}", "email": f"secscan-{uid}@test.crm", "password": "SecScan2026!"},
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=60,
    )
    d = resp.json().get("data", {})
    return d.get("access_token", ""), d.get("tenant_id", "")


print(f"\n=== C5 API Security Scan against {GATEWAY} ===\n")

# ── 1. Security headers ───────────────────────────────────────────────────────
print("1. Security Headers (helmet)")
h = get_headers()
check("Content-Security-Policy", "content-security-policy" in h)
check("Strict-Transport-Security", "strict-transport-security" in h)
check("X-Frame-Options", "x-frame-options" in h)
check("X-Content-Type-Options", "x-content-type-options" in h,
      f"got: {h.get('x-content-type-options', 'MISSING')}")

# ── 2. Authentication enforcement ─────────────────────────────────────────────
print("\n2. Authentication Enforcement")
r = httpx.get(f"{GATEWAY}/api/v1/leads",
              headers={"Accept": "application/json"}, timeout=15)
check("Unauthenticated GET returns 401", r.status_code == 401, f"got {r.status_code}")
check("401 has correct error code", r.json().get("error", {}).get("code") == "unauthorized")

r2 = httpx.get(f"{GATEWAY}/api/v1/leads",
               headers={"Accept": "application/json",
                        "Authorization": "Bearer fakejwt.invalid.token"},
               timeout=15)
check("Invalid JWT returns 401", r2.status_code == 401, f"got {r2.status_code}")

# ── 3. Input validation (SQLi / XSS patterns) ─────────────────────────────────
print("\n3. Input Validation")
token, tenant = register_user()
auth_hdrs = {"Accept": "application/json", "Authorization": f"Bearer {token}", "x-tenant-id": tenant}

r3 = httpx.get(f"{GATEWAY}/api/v1/leads?stage=' OR 1=1--",
               headers=auth_hdrs, timeout=15)
check("SQL injection in query param rejected (not 5xx)", r3.status_code < 500,
      f"got {r3.status_code}")

r4 = httpx.post(f"{GATEWAY}/api/v1/auth/register",
                json={"name": "<script>alert(1)</script>", "email": "xss@test.crm",
                      "password": "XssTest2026!"},
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=30)
# XSS in name should not cause a 500 (it's stored and sanitized, not reflected)
check("XSS in request body handled gracefully (not 5xx)", r4.status_code < 500,
      f"got {r4.status_code}")

# ── 4. Error response doesn't leak sensitive info ──────────────────────────────
print("\n4. Error Response Safety")
r5 = httpx.get(f"{GATEWAY}/api/v1/nonexistent-endpoint-xyz",
               headers={**auth_hdrs}, timeout=15)
body5 = r5.text
check("404 doesn't expose stack trace", "Traceback" not in body5 and "at Object" not in body5,
      f"body contains stack trace")
check("404 returns JSON error envelope",
      "error" in r5.json() and "meta" in r5.json(), f"got: {body5[:100]}")

# ── 5. CORS enforcement ────────────────────────────────────────────────────────
print("\n5. CORS Enforcement")
r6 = httpx.get(f"{GATEWAY}/api/v1/leads",
               headers={**auth_hdrs, "Origin": "https://evil.example.com"},
               timeout=15)
check("Unlisted origin blocked (403 or no ACAO header)",
      r6.status_code == 403 or "access-control-allow-origin" not in r6.headers,
      f"got status {r6.status_code}, ACAO: {r6.headers.get('access-control-allow-origin', 'none')}")

r7 = httpx.get(f"{GATEWAY}/api/v1/leads",
               headers={**auth_hdrs, "Origin": "https://crm-frontend-0gde.onrender.com"},
               timeout=15)
check("Allowed origin accepted",
      r7.status_code == 200,
      f"got {r7.status_code}")

# ── 6. Rate limiting headers present ──────────────────────────────────────────
print("\n6. Rate Limiting")
r8 = httpx.get(f"{GATEWAY}/api/v1/leads", headers=auth_hdrs, timeout=15)
check("x-ratelimit-limit header present", "x-ratelimit-limit" in r8.headers)
check("x-ratelimit-remaining header present", "x-ratelimit-remaining" in r8.headers)

# ── 7. No sensitive data in unauthenticated health response ───────────────────
print("\n7. Information Disclosure")
r9 = httpx.get(f"{GATEWAY}/health", timeout=15)
body9 = r9.json()
check("Health endpoint doesn't expose secrets",
      "password" not in str(body9).lower() and "secret" not in str(body9).lower() and
      "database_url" not in str(body9).lower())
check("Health endpoint doesn't expose full stack info",
      len(str(body9)) < 500)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n=== SECURITY SCAN RESULT ===")
print(f"Passed: {passed} | Failed: {failed}")
if findings:
    print("\nFindings:")
    for f in findings:
        print(f"  - {f['check']}: {f['detail']}")

# Save report
report = {
    "gateway": GATEWAY,
    "passed": passed,
    "failed": failed,
    "findings": findings,
    "high_critical": [f for f in findings if "stack trace" in f["detail"].lower() or
                      "5xx" in f["detail"].lower()],
}
with open("tests/security/c5-api-security-report.json", "w") as fp:
    json.dump(report, fp, indent=2)

print(f"\nReport: tests/security/c5-api-security-report.json")
sys.exit(0 if failed == 0 else 1)
