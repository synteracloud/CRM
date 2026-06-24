Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI

# PRE-FRONTEND READINESS SCORECARD — Phase 2.9
> Scored assessment across 11 dimensions. Evidence cited for each score.

---

## Scoring Key

| Score | Meaning |
|-------|---------|
| 9–10 | Excellent — complete, verified, no gaps |
| 7–8 | Good — minor gaps, non-blocking |
| 5–6 | Acceptable — some gaps, documented and manageable |
| 3–4 | Weak — significant gaps, plan required |
| 1–2 | Poor — critical gaps, blocks planning |

---

## Dimension Scores

### 1. Backend Authority Completeness — 9/10

**Evidence:**
- All 34 domain modules inventoried in MODULE_INVENTORY.md (verified vs backend/src/)
- 23 cross-cutting services documented in SERVICE_CATALOG.md (verified vs backend/services/)
- 44 gateway route groups, 228 endpoints in API_CONTRACT.md (verified vs backend/gateway/routes/)
- 18 DB schemas in DATABASE_SCHEMA.md (verified vs backend/db/)
- 12 Alembic migrations documented
- SERVICE_CATALOG.md promoted to Active

**Why not 10:** automation_journeys lacks dedicated MODULE_INVENTORY entry (UDC-002, low priority). backend/docs/ spec library not linked from docs/01_backend/ README (UDC-004).

---

### 2. Repository Authority Completeness — 9/10

**Evidence:**
- Repository structure fully inventoried (REPOSITORY_TREE_INVENTORY.md)
- docs/ framework complete and normalized
- .gitignore comprehensive (logs, pycache, pytest_cache, screenshots all covered)
- deploy-runtime.yml at correct root .github/ location (fixed in prior session)
- ci.yml confirmed and documented in AI_OPERATING_CONTEXT.md (UDC-001 resolved)
- Root COMMERCIALISATION-PLAN.md duplicate removed (DD-008 resolved)

**Why not 10:** 2 deferred SAFE_REPOSITORY_HYGIENE items (UDC-002, UDC-004) — low priority.

---

### 3. Repository Normalization Completeness — 8/10

**Evidence:**
- All 6 high-priority file moves executed (Steps 7+2.9)
- 10 authority docs promoted from Draft → Active
- Service count corrected to 23 across 5 report docs
- ROOT_LEVEL_CLEANUP_PLAN.md items C-03 through C-06 confirmed done (.gitignore verified)
- Root prompt files: 3 remain at root (originals — no Prompts/Main/ copies)

**Why not 10:** 9 REQUIRES_APPROVAL items remain unexecuted (bin/, data/, CI/CD decisions, compliance decisions) — these are genuine owner decisions not hygiene. Conditional items (R-09, R-10) still need grep verification.

---

### 4. Documentation Accuracy — 9/10

**Evidence:**
- AI_OPERATING_CONTEXT.md: 4 count errors fixed (Steps 7+2.9)
- BACKEND_GAP_REGISTER.md: 4 false alarms closed (G-MED-002, G-MED-003, G-LOW-001, G-HIGH-005)
- VALIDATION_RULES.md: EmailStr claim corrected (was wrong)
- USER_ROLES_AND_PERMISSIONS.md: leads.delete TBD resolved
- G-HIGH-002: confirmed as real gap with evidence
- 6 UNVERIFIED_CLAIMS resolved

**Why not 10:** UC-002 (phone regex) remains open. CONTRACT_VERSION_REGISTRY.md still shows SERVICE_CATALOG as "10 services" (not updated this session).

---

### 5. Security Readiness — 6/10

**Evidence:**
- JWT HS256 auth model documented and confirmed
- Multi-tenant isolation with semgrep CI enforcement confirmed
- Default-deny RBAC with 91 scopes documented
- OA-001 (contacts.delete broken — all users get 403) confirmed and documented
- OA-002 (JTI in-memory blocklist) documented
- OA-008 (sha256 not bcrypt) documented
- OA-009 (refresh token not revoked on logout) NEWLY DISCOVERED and documented
- Dev token endpoint confirmed disabled in production (G-MED-003 closed)

**Why 6 not higher:** 4 security gaps remain as owner decisions: OA-001 (auth bypass for contacts delete), OA-002 (stateless JTI), OA-008 (weak hashing), OA-009 (incomplete logout). These are known, documented, and bounded — but they exist.

---

### 6. Permission Model Readiness — 8/10

**Evidence:**
- 7 roles confirmed: super_admin, tenant_owner, tenant_admin, sales_manager, sales_rep, support_agent, billing_manager
- 91 scopes confirmed in rbac-scopes.js
- ROLE_SCOPES mapping documented in USER_ROLES_AND_PERMISSIONS.md
- G-HIGH-005 (leads.delete) confirmed not a gap

**Why not 10:** OA-001 (contacts.delete missing) is a known permission model defect. Frontend must account for it.

---

### 7. API Readiness — 9/10

**Evidence:**
- 228 endpoints, 44 route groups confirmed
- Request/response patterns documented in API_CONTRACT.md (now Active)
- Error contract (9 error codes) documented in ERROR_CONTRACT.md (now Active)
- Auth requirements on all routes confirmed (requireScopes([]) enforced everywhere)
- Idempotency-Key requirement documented (V-002 in VALIDATION_PARITY.md)

**Why not 10:** OA-005 (contracts module has no gateway route) and UDC-003 (custom_objects no gateway route) mean 2 backend modules are built but inaccessible via API.

---

### 8. Workflow Readiness — 9/10

**Evidence:**
- 5 primary workflows documented in PRODUCT_WORKFLOWS.md
- Workflow engine catalog documented (`backend/src/workflow_engine/catalog.py`)
- SLA breach workflow confirmed operational (UC-005 resolved — events emitted)
- WhatsApp inbound → contact/lead creation workflow documented
- Follow-up enforcement engine documented in SERVICE_CATALOG.md

**Why not 10:** G-HIGH-003 (no message broker — in-process events only) means events can be lost on restart. G-HIGH-004 (outbox publisher not implemented) means payment events are never dispatched.

---

### 9. Validation Readiness — 7/10

**Evidence:**
- Gateway validation patterns documented in VALIDATION_RULES.md (now Active)
- FastAPI Pydantic validation documented
- 5 validation parity gaps documented in VALIDATION_PARITY.md (V-001 through V-005)
- EmailStr confirmed not used (UC-001 resolved) — gateway-only email validation
- Phone E.164 format documented
- PKR amount validation documented

**Why 7:** UC-002 (phone regex) unresolved. 5 parity gaps require frontend implementation (Idempotency-Key, phone format, etc.). 7 TBDs remain in VALIDATION_RULES.md event version section.

---

### 10. Repository Hygiene Status — 8/10

**Evidence:**
- .gitignore comprehensive (20+ entries)
- All tracked build artifacts addressed
- docs/ framework organized and normalized
- 6 misplaced files moved to correct locations
- Root duplicate removed (COMMERCIALISATION-PLAN.md)
- 10 draft docs promoted to Active

**Why not 10:** 9 REQUIRES_APPROVAL items remain (bin/, data/, CI/CD, compliance). 2 conditional items (R-09, R-10) not yet executed. 2 deferred SAFE_REPOSITORY_HYGIENE items.

---

### 11. Operational Readiness — 8/10

**Evidence:**
- 11 CI jobs confirmed passing on main (ci.yml verified)
- Render.com deployment confirmed (3 services + 2 managed)
- DUMMY_MODE false confirmed
- Redis live (crm-redis managed service)
- PostgreSQL live (crm-postgres managed service)
- 79 backend tests, 25 Playwright E2E tests

**Why not 10:** OA-002 (JTI in-memory — single instance risk). OA-003 (no real payments). G-HIGH-003 (no message broker). Payment integration stub.

---

## Overall Score

| Dimension | Score |
|-----------|-------|
| Backend Authority Completeness | 9/10 |
| Repository Authority Completeness | 9/10 |
| Repository Normalization Completeness | 8/10 |
| Documentation Accuracy | 9/10 |
| Security Readiness | 6/10 |
| Permission Model Readiness | 8/10 |
| API Readiness | 9/10 |
| Workflow Readiness | 9/10 |
| Validation Readiness | 7/10 |
| Repository Hygiene Status | 8/10 |
| Operational Readiness | 8/10 |
| **Overall** | **82/110 (75%)** |

---

## Verdict

**CONDITIONAL GO** — 75% overall readiness.

Security dimension (6/10) is the only weak area and is bounded to 4 known, documented, owner-decision items. All documentation dimensions are 8–9/10. Frontend Authority Capture can proceed on a solid documentation foundation.

**Target for commercial launch:** resolve OA-001, OA-002/OA-009 (bundled auth sprint), OA-003 — pushes Security from 6→9, overall from 75%→88%+.

---

*End PRE_FRONTEND_READINESS_SCORECARD.md*
