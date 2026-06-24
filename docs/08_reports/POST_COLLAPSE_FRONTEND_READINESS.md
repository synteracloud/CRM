---
Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: AI
Phase: 2.95
---

# POST-COLLAPSE FRONTEND READINESS

> Final readiness statement after Phase 2.95 Residual Decision Collapse.
> Supersedes PRE_FRONTEND_GO_NO_GO_REPORT.md for all decisions made in Phase 2.95.

---

# VERDICT: GO

**Frontend Authority Capture may begin immediately and without restriction.**

All 9 residual decisions have been collapsed to a single recommended path. No remaining decision can alter navigation, menus, screens, workflows, permissions, or user journeys in the C6 scope. The one TRUE_OWNER_DECISION (OA-003, payment credentials) is isolated to a payment form stub state that is already the documented production behavior.

---

## Why This Is a Full GO (Not Conditional)

Phase 2.9 issued a CONDITIONAL GO because 9 residual decisions remained open. Phase 2.95 has collapsed all 9:

| Decision | Phase 2.9 Status | Phase 2.95 Status |
|----------|-----------------|------------------|
| OA-001 contacts.delete | Open | OWNER_CONFIRMATION_ONLY — proceed with Option A |
| OA-002 JTI blocklist | Open | OWNER_CONFIRMATION_ONLY — accept for C6 |
| OA-003 payments | Open | TRUE_OWNER_DECISION — isolated, non-blocking |
| OA-004 AI model | Open | OWNER_CONFIRMATION_ONLY — rule-based for C6 |
| OA-005 contracts gateway | Open | RESOLVED — defer to C7 (no C6 page) |
| OA-006 security artifacts | Open | OWNER_CONFIRMATION_ONLY — move to docs/reports/security/ |
| OA-007 load test reports | Open | OWNER_CONFIRMATION_ONLY — move c5-prod to docs/reports/load/ |
| OA-008 password hashing | Open | OWNER_CONFIRMATION_ONLY — accept SHA-256 for C6 |
| OA-009 refresh revocation | Open | OWNER_CONFIRMATION_ONLY — bundle with OA-002 post-C6 |

The Phase 2.9 CONDITIONAL GO conditions have been resolved:
- OA-001: Recommendation is clear; frontend documents constraint and builds accordingly
- OA-009 + OA-002: Deferred with clear sprint plan; zero frontend impact
- OA-003: Stub state is the documented production state; frontend is already built for it

---

## What Frontend Authority Capture CAN Assume (Stable Facts)

All of the following are confirmed from repository evidence and will not change before C6 launch:

### Authentication
- JWT HS256, 15-minute access tokens, 7-day HttpOnly cookie refresh tokens
- All protected routes require `Authorization: Bearer {accessToken}`
- Login: POST /auth/login → returns access token + sets refresh cookie
- Logout: DELETE /auth/sessions/current → clear local state (note: refresh token remains valid 7 days — OA-009)
- Token refresh: POST /auth/refresh → new access token

### RBAC
- 7 roles: super_admin, tenant_owner, tenant_admin, sales_manager, field_agent, support_agent, viewer
- 91 permission scopes in JWT `scopes` array
- Frontend must show/hide controls based on scopes claim
- Exception: `contacts.delete` scope currently missing from all tokens (OA-001 pending)

### API
- 228 endpoints across 44 gateway route groups
- All endpoints documented in docs/01_backend/API_CONTRACT.md
- Gateway base URL: proxied to FastAPI backend
- Request lifecycle: JWT validation → tenant extraction → RBAC check → FastAPI proxy

### Tenancy
- x-tenant-id header on every authenticated request
- Extracted from JWT by gateway middleware automatically
- Frontend never sets this header manually

### DUMMY_MODE
- false on all 75 pages (crm-api.js line 14)
- Live API calls with graceful fallback to crm-dummy.js when API unavailable
- Frontend must maintain this pattern on any new pages

### Data Shapes
- 8 core entity shapes in docs/03_fullstack_contracts/DATA_SHAPE_REGISTRY.md
- PKR currency throughout; lakh/crore formatting
- E.164 phone format: /^\+92[0-9]{10}$/

### Idempotency
- Frontend MUST generate Idempotency-Key header on all POST/PUT/PATCH requests
- This is a confirmed frontend build requirement from gateway validation

---

## What Frontend Authority Capture Must Document as Constraints

These are known production states, not future changes — document them accurately:

| Constraint | Documentation Requirement |
|------------|--------------------------|
| contacts.delete returns 403 | Hide delete controls for all roles except tenant_admin/super_admin. Document: "OA-001 pending — delete scope grant required." |
| Logout does not revoke refresh token | Frontend session management: note that refresh token remains valid post-logout. No UX impact; security note for auth contract. |
| Payment flows return stub responses | G-04 billing-settings.html: document stub state (P-016). Wire payment form. Display stub confirmation. Live activation pending OA-003. |
| AI features are rule-based | M-01, M-02: document "rule-based advisory — AI inference model deferred to C7." |
| No contracts gateway route | No contracts page in C6 scope. If added in C7, gateway route will be created then. |

---

## What Is Explicitly Deferred to Post-Launch

| Item | Deferred To | Notes |
|------|-------------|-------|
| JTI blocklist Redis migration | Post-C6 Auth Sprint | Bundle with OA-009 |
| Refresh token revocation on logout | Post-C6 Auth Sprint | Bundle with OA-002 |
| JazzCash/Easypaisa live payments | OA-003 (owner decision) | Credential acquisition |
| LLM inference model | C7 | Additive feature |
| Contracts gateway route + page | C7 | No C6 frontend page |
| bcrypt password migration | C7 Security Sprint | Transparent re-hash on login |

---

## Final Decision Status Table

| ID | Description | Final Status | Frontend Assumption |
|----|-------------|--------------|---------------------|
| OA-001 | contacts.delete RBAC | OWNER_CONFIRMATION_ONLY → Option A | Hide delete; build permission-aware controls |
| OA-002 | JTI blocklist | OWNER_CONFIRMATION_ONLY → accept for C6 | No frontend impact |
| OA-003 | Payment stub | TRUE_OWNER_DECISION → isolated | Document stub state in G-04 |
| OA-004 | AI model | OWNER_CONFIRMATION_ONLY → rule-based | Document rule-based in M-01, M-02 |
| OA-005 | Contracts gateway | RESOLVED → defer to C7 | No C6 action |
| OA-006 | Security artifacts | OWNER_CONFIRMATION_ONLY → move to docs | No frontend action |
| OA-007 | Load test reports | OWNER_CONFIRMATION_ONLY → move c5-prod | No frontend action |
| OA-008 | Password hashing | OWNER_CONFIRMATION_ONLY → accept SHA-256 | No frontend action |
| OA-009 | Refresh revocation | OWNER_CONFIRMATION_ONLY → post-C6 sprint | No frontend action |

---

## Frontend Authority Capture Starting State

Frontend Authority Capture (Step 11 in prompt sequence) begins with:

- **75 custom pages** — all built, all confirmed in DESIGN-SPEC.md
- **169 total pages** in frontend/src/app/
- **228 API endpoints** documented and stable
- **7 roles, 91 scopes** — permission model stable
- **Auth contract stable** — JWT structure, token flow, tenant isolation all documented
- **Data shapes stable** — 8 entities in DATA_SHAPE_REGISTRY.md
- **DUMMY_MODE: false** — live API pattern established
- **0 frontend blockers** — no decision can alter the frontend authority capture work

Frontend Authority Capture may begin now.

---

*End POST_COLLAPSE_FRONTEND_READINESS.md*
