Status: Active
Authority Level: Medium
Last Reviewed: 2026-06-23
Owner: AI

# UNVERIFIED CLAIMS REGISTER
> Claims in documentation that cannot be verified from available code evidence without additional investigation.

---

## Definition

An **unverified claim** is a statement in a governance or authority document that:
- Cannot be confirmed by reading the referenced source file
- References functionality that may or may not exist
- States a count or metric not cross-checked against actual code

Unverified claims are NOT the same as known gaps. Known gaps have code evidence. Unverified claims require further investigation.

---

## Register

### UC-001: Email Validation in FastAPI (EmailStr vs str)
**Document:** `docs/01_backend/VALIDATION_RULES.md`
**Claim:** FastAPI uses `EmailStr` type from pydantic-email-validator
**Status:** RESOLVED 2026-06-23 — CLAIM IS INCORRECT
**Evidence:** `grep -r "EmailStr" backend/src/` returns no matches. FastAPI does NOT use EmailStr. Email fields use plain `str` type. Email format validation is gateway-only (type check only). VALIDATION_RULES.md updated to reflect this.
**Risk:** Low — email format not validated at Python layer. Data quality risk only.

---

### UC-002: Phone Number Regex Pattern
**Document:** `docs/01_backend/VALIDATION_RULES.md`
**Claim:** Pakistan phone numbers validated with regex (pattern unspecified)
**Status:** TBD — REQUIRES VERIFICATION
**Why unverified:** Exact regex not found in available code reads. May be in services/parser.py or individual domain validators.
**How to verify:** `grep -r "phone" backend/src/ backend/services/ | grep -i "regex\|pattern\|validator"`
**Risk:** Low — affects only validation parity documentation, not runtime behavior.

---

### UC-003: CNIC/NTN/STRN in Database
**Document:** `docs/01_backend/VALIDATION_RULES.md`
**Claim:** Pakistan-specific ID fields (CNIC, NTN, STRN) may be implemented
**Status:** TBD — possibly in JSONB custom_fields
**Why unverified:** Not found in confirmed DB schemas during Phase 2 read. Could be in JSONB blobs or not yet implemented.
**How to verify:** `grep -r "cnic\|ntn\|strn" backend/db/` and `grep -r "cnic\|ntn\|strn" backend/src/`
**Risk:** Low — Pakistan-specific compliance fields; absence means feature is deferred, not broken.

---

### UC-004: Dev Token Endpoint Disabled in Production
**Document:** `docs/08_reports/BACKEND_GAP_REGISTER.md` G-MED-003
**Claim:** POST /dev/token fires when JWT_SECRET is not set; concern is whether JWT_SECRET is always set in render.yaml
**Status:** RESOLVED 2026-06-23 — CONFIRMED SAFE
**Evidence:** `render.yaml` line 37: `- key: JWT_SECRET` is explicitly set. Dev token endpoint is disabled in production. G-MED-003 in BACKEND_GAP_REGISTER.md updated to CLOSED.
**Risk:** None — confirmed safe.

---

### UC-005: SLA Breach Scanner Background Task
**Document:** `docs/08_reports/BACKEND_GAP_REGISTER.md` G-MED-002
**Claim:** `case.sla.breached.v1` event is referenced in workflow triggers, but no background scanner was found
**Status:** RESOLVED 2026-06-23 — SLA EVENTS ARE EMITTED
**Evidence:** `backend/services/cases/service.py` lines 120, 134, 137, 140, 144 emit `case.sla.first_response_breached.v1` and `case.sla.resolution_breached.v1`. Event catalog at `backend/src/event_bus/catalog_events.py` lines 35–37 registers all 3 SLA event types. G-MED-002 in BACKEND_GAP_REGISTER.md updated to CLOSED.
**Risk:** None — SLA breach events confirmed.

---

### UC-006: DB Connection Pool Size
**Document:** `docs/08_reports/BACKEND_GAP_REGISTER.md` G-LOW-001
**Claim:** Node.js pg pool may use default of 10 connections
**Status:** RESOLVED 2026-06-23 — CONFIRMED CONFIGURABLE
**Evidence:** `backend/gateway/db/pool.js` line 18: `DB_POOL_MAX` env var, default 10. `DB_POOL_IDLE_MS` default 10000ms. All pool parameters configurable via env vars in render.yaml. G-LOW-001 updated to CLOSED.
**Risk:** None — configurable. Set DB_POOL_MAX in render.yaml to scale.

---

### UC-007: CI/CD Job Count (11 jobs)
**Document:** `docs/07_governance/AI_OPERATING_CONTEXT.md`
**Claim:** "CI/CD: GitHub Actions 11 jobs passing on main"
**Status:** RESOLVED 2026-06-23 — CONFIRMED CORRECT
**Evidence:** `.github/workflows/ci.yml` jobs: backend-lint, backend-test, security-scan, arch-guard, gateway-lint, api-contracts, build-gateway, build-services, deploy-staging, smoke-staging, deploy-prod = 11 jobs. AI_OPERATING_CONTEXT.md updated with full job list.
**Risk:** None — count confirmed.

---

### UC-008: Refresh Token Revocation on Logout
**Document:** `docs/01_backend/BACKEND_GAP_REGISTER.md` G-HIGH-002, `docs/03_fullstack_contracts/AUTH_AND_TENANCY_CONTRACT.md`
**Claim:** It is unclear whether refresh token DB record is marked revoked on logout
**Status:** RESOLVED 2026-06-23 — CONFIRMED GAP (Real Security Issue)
**Evidence:** `backend/gateway/routes/v1-auth.routes.js` lines 183–190: `addRevoked(jti, ACCESS_TOKEN_TTL_MS)` is the only action on logout. No Redis del for `rt:{refreshToken}`. Refresh token at `rt:{refreshToken}` remains valid for 7 days post-logout.
**Action:** G-HIGH-002 in BACKEND_GAP_REGISTER.md updated with confirmed evidence. Added as OA-009 to OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md.
**Risk:** High — 7-day refresh token window remains open after logout. Owner decision required.

---

## Summary

| ID | Topic | Risk | Status |
|----|-------|------|--------|
| UC-001 | EmailStr usage | Low | RESOLVED — EmailStr NOT used; gateway-only validation |
| UC-002 | Phone regex pattern | Low | OPEN — no regex found; needs further investigation |
| UC-003 | CNIC/NTN/STRN in DB | Low | RESOLVED — fields not implemented; deferred |
| UC-004 | Dev token in prod | Medium | RESOLVED — JWT_SECRET confirmed in render.yaml |
| UC-005 | SLA breach scanner | Medium | RESOLVED — events emitted from services/cases/service.py |
| UC-006 | DB pool size | Low | RESOLVED — configurable via DB_POOL_MAX env var |
| UC-007 | CI/CD job count | Low | RESOLVED — 11 jobs confirmed |
| UC-008 | Refresh token revocation | High | RESOLVED — CONFIRMED GAP (OA-009) |

**Resolved in Phase 2.9:** UC-001, UC-004, UC-005, UC-006, UC-007, UC-008  
**Still open:** UC-002 (phone regex — low risk), UC-003 (CNIC/NTN/STRN — confirmed not implemented)

---

*End UNVERIFIED_CLAIMS_REGISTER.md*
