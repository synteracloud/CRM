Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: AI

# FRONTEND BLOCKERS REGISTER — Phase 2.9
> Items that would prevent Frontend Authority Capture from proceeding.
> Strict definition: only items where frontend documentation literally cannot proceed without resolution.

---

## Verdict

# NO FRONTEND BLOCKERS

**Frontend Authority Capture can begin immediately.**

All 9 residual owner decision items are backend/infra decisions. None prevent frontend documentation from proceeding.

---

## Why Each Owner Decision Does NOT Block Frontend

| Item | Why Not a Frontend Blocker |
|------|---------------------------|
| OA-001: contacts.delete scope | Frontend can document: "DELETE contact requires contacts.delete scope (currently broken — OA-001 pending)." Frontend UI knows to show/hide delete controls based on whether scope is granted. |
| OA-002: JTI blocklist in-memory | Invisible to frontend. JWT auth flow is unchanged. Frontend calls DELETE /auth/sessions/current and trusts the response. |
| OA-003: JazzCash/Easypaisa stub | Frontend can document stub behavior: payment flows exist but return stub responses. Frontend pages (billing-settings.html G-04) are already built with this known state. |
| OA-004: AI inference model | Frontend AI pages (M-01, M-02) are built and display rule-based results. Frontend does not need to know which provider is behind the API. |
| OA-005: contract_lifecycle_management | No frontend contracts page exists in DESIGN-SPEC.md scope. If a contracts page is added, gateway route must be created first — but this is a future decision, not a current blocker. |
| OA-006: Security test artifacts | File disposition has no frontend impact. |
| OA-007: Load test reports | Performance evidence has no frontend impact. |
| OA-008: Password hashing | Frontend auth flow is unchanged. Login/register pages call the same gateway endpoints regardless of backend hashing algorithm. |
| OA-009: Refresh token not revoked | Invisible to frontend. Frontend sends DELETE /auth/sessions/current and clears its local token state. The backend-side security gap does not change frontend behavior. |

---

## What Frontend Planning CAN Assume (Safe Assumptions)

Based on confirmed repository evidence:

1. **Auth flow:** JWT access token (15 min) + HttpOnly cookie refresh token (7 days). All protected routes require `Authorization: Bearer {token}`. Frontend auth wiring pattern is documented in AUTH_AND_TENANCY_CONTRACT.md.

2. **RBAC:** 7 roles, 91 scopes. Frontend should show/hide controls based on role from JWT `scopes` claim. All 91 scopes are documented in USER_ROLES_AND_PERMISSIONS.md. Exception: contacts.delete returns 403 (OA-001) — hide delete button until fixed.

3. **API endpoints:** 228 endpoints across 44 gateway route groups. All documented in API_CONTRACT.md. Request/response shapes documented in DATA_SHAPE_REGISTRY.md.

4. **DUMMY_MODE:** false. All 75 pages use live API calls with graceful fallback from crm-dummy.js when API unavailable. Frontend wiring must follow this pattern.

5. **Payment pages:** billing-settings.html (G-04) payment section shows stub responses. This is the current production state. Frontend can document this as P-016 constraint (known).

6. **AI pages:** M-01, M-02 display rule-based scores. No inference model behind them. Frontend can document this accurately.

7. **Idempotency:** Frontend must generate `Idempotency-Key` headers for all POST/PUT/PATCH requests (V-002 from VALIDATION_PARITY.md). This is a frontend build requirement confirmed from gateway validation code.

---

## Items That Would Create Frontend Blockers (Hypothetical — Not Current)

The following would block frontend planning — none are current:

- If API contract was unknown or contradictory → would block API wiring decisions
- If RBAC model was undefined → would block permission-based UI decisions  
- If auth flow was undocumented → would block login/token handling decisions
- If data shapes were unknown → would block form field definitions

None of these apply. All are fully documented.

---

*End FRONTEND_BLOCKERS_REGISTER.md*
