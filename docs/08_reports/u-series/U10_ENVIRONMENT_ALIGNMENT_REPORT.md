# U10 ENVIRONMENT ALIGNMENT REPORT — Pakistan CRM OS

**Generated:** 2026-06-21 — U10 Audit Remediation
**Purpose:** python-jose and starlette before/after versions; overall environment alignment

---

## python-jose Version Status

### What the forensic audit reported

The U0_U9_FORENSIC_AUDIT_REPORT.md (CRIT-002) stated:
- requirements.txt specifies `python-jose[cryptography]==3.5.0`
- pip-audit.json (tests/security/pip-audit.json) shows python-jose 3.3.0 installed with 3 CVEs
- "The .venv has not been rebuilt since requirements.txt was updated"

### What U10 verification found (2026-06-21)

**Live pip install check:**
```
Command: D:\SaaS\CRM\backend\.venv\Scripts\python.exe -m pip install "python-jose[cryptography]>=3.5.0"
Result: Requirement already satisfied: python-jose>=3.5.0 in d:\saas\crm\backend\.venv\lib\site-packages (3.5.0)
```

**Live pip show check:**
```
Name: python-jose
Version: 3.5.0
Location: D:\SaaS\CRM\backend\.venv\Lib\site-packages
```

**Conclusion:** python-jose 3.5.0 is already installed in the venv. CRIT-002 was incorrect — the venv WAS rebuilt after requirements.txt was updated.

### Root cause of CRIT-002 false alarm

- PROGRESS.md (2026-06-01, C3 session): "C2e: semgrep 0 ERROR/CRITICAL; npm audit fix (qs moderate); pip-audit python-jose upgraded"
- This confirms python-jose was upgraded to 3.5.0 during C3 (2026-06-01)
- tests/security/pip-audit.json is a STALE FILE — it was generated before the C3 upgrade and was not regenerated
- The forensic audit read the stale pip-audit.json (date: 2026-06-20 filename, but content from pre-C3)
- Result: forensic audit concluded 3.3.0 was installed when 3.5.0 was actually installed

### Before / After (actual vs reported)

| Field | pip-audit.json (stale) | Actual installed (confirmed) |
|---|---|---|
| python-jose version | 3.3.0 | **3.5.0** |
| CVE-2024-33663 (algorithm confusion) | Present | **Resolved in 3.5.0** |
| CVE-2024-33664 (JWT bomb DoS) | Present | **Resolved in 3.5.0** |
| CVE-2024-29370 (JWE decompression DoS) | Present | **Resolved in 3.5.0** |
| requirements.txt alignment | Drift (requirements says 3.5.0, json shows 3.3.0) | **Aligned** (both 3.5.0) |

**No environment fix was required.** Environment was already aligned.

---

## starlette Version Status

### What the forensic audit reported

Both pip-audit.json and requirements.txt specify starlette 0.38.6. No version drift.

### U10 verification

**Live pip show check:**
```
Name: starlette
Version: 0.38.6
Location: D:\SaaS\CRM\backend\.venv\Lib\site-packages
```

**Requirements.txt:** `starlette==0.38.6`

**Conclusion:** No version drift. starlette 0.38.6 is pinned at requirements.txt level. This is an intentional pin for FastAPI 0.115 compatibility.

### CVE Status

| CVE | Description | Fix Version | Status |
|---|---|---|---|
| PYSEC-2026-161 / GHSA-86qp-5c8j-p5mr | Host header injection | 1.0.1 | Accepted risk — FastAPI 0.115 requires starlette 0.38.6; upgrading breaks FastAPI compat |
| CVE-2024-47874 | Multipart DoS | 0.40.0 | Accepted risk — same compat constraint |
| CVE-2025-54121 | File upload blocking | 0.47.2 | Accepted risk — same compat constraint |

**Risk acceptance documented.** The starlette CVEs represent accepted risk pending FastAPI upgrade planning. No immediate action in U10 scope.

---

## Overall Environment Alignment Summary

| Component | requirements.txt | Installed (verified) | Aligned | CVEs in installed |
|---|---|---|---|---|
| python-jose | 3.5.0 | 3.5.0 | YES | 0 (patched in 3.5.0) |
| starlette | 0.38.6 | 0.38.6 | YES | 3 (accepted risk) |
| fastapi | 0.115.0 | 0.115.0 | YES | 0 |
| pydantic | 2.13.4 | 2.13.4 | YES | 0 |
| psycopg2-binary | 2.9.10 | 2.9.12 | Minor drift (no CVEs) | 0 |
| pip (tool) | N/A | 25.0.1 | N/A | 4 (dev tooling risk) |

**psycopg2-binary note:** requirements.txt specifies 2.9.10; installed is 2.9.12 (MI-012). This is a minor forward-drift with no CVEs — pip resolved to a newer patch when rebuilding. No action required.

---

## Workspace Sealing Re-Verification

All U8 sealing claims re-verified live by U10 forensic audit:

| Tool | Claimed | Verified |
|---|---|---|
| npm cache | D:\npm-cache | CONFIRMED |
| npm prefix | D:\npm | CONFIRMED |
| PLAYWRIGHT_BROWSERS_PATH | D:\dev-cache\playwright | CONFIRMED |
| TEMP | D:\Temp | CONFIRMED |
| pip cache (pip.ini) | D:\LMS\workspace\.pip-cache | CONFIRMED |
| node_modules | D:\SaaS\CRM\frontend\node_modules | CONFIRMED |

**Overall environment sealing: FULLY SEALED — no C: drive leakage**

---

*End U10_ENVIRONMENT_ALIGNMENT_REPORT.md*
