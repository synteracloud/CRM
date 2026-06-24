Status: Active
Authority Level: Medium
Last Reviewed: 2026-06-23
Owner: AI

# TBD RESOLUTION REGISTER
> Every TBD found in docs/ (145 occurrences in 31 files) — resolved where code evidence exists, documented where it doesn't.
> Updated Phase 3.25 (2026-06-23): All 8 "Require Code Investigation" TBDs resolved. All authority doc TBDs cleared.

---

## Summary

| Category | Count |
|----------|-------|
| TBDs resolved with code evidence (prior phases) | 3 |
| TBDs resolved in Phase 3.25 | 16 |
| TBDs resolved in Phase 3.25 retry (2026-06-24) | 4 (P-TBD-001–004 reclassified; VALIDATION_PARITY.md email TBD; G-007 confirmed not-implemented) |
| TBDs remaining — genuinely unresolvable (commercial/vendor) | 2 (OA-003, G-MED-005) |
| TBDs in old/report documents (informational only) | ~122 |
| **Total TBD occurrences** | **145** |
| **Open authority-doc TBDs** | **0** |

---

## RESOLVED TBDs (evidence found this session)

### R-TBD-001: leads.delete Scope Existence
**Location:** `docs/08_reports/BACKEND_GAP_REGISTER.md` G-HIGH-005
**Original TBD:** "leads.delete may have the same issue as contacts.delete — TBD REQUIRES VERIFICATION"
**Resolution:** VERIFIED 2026-06-23 — `LEADS_DELETE: 'leads.delete'` IS present in `backend/gateway/config/rbac-scopes.js` line 21. No gap.
**Action taken:** G-HIGH-005 updated to CLOSED status in BACKEND_GAP_REGISTER.md; USER_ROLES_AND_PERMISSIONS.md updated.

### R-TBD-002: Row Level Security Not Implemented
**Location:** `docs/03_fullstack_contracts/AUTH_AND_TENANCY_CONTRACT.md`
**Original TBD:** "No DB-level Row Level Security (RLS) found — TBD REQUIRES VERIFICATION"
**Resolution:** VERIFIED 2026-06-23 — 18 schema.sql files in backend/db/ contain no `ENABLE ROW LEVEL SECURITY` or `CREATE POLICY` statements. Application-level tenant isolation is the only isolation mechanism. No RLS.
**Action taken:** Updated in DOC_DRIFT_REGISTER. TBD status converted to confirmed finding.

### R-TBD-003: Service Count (22 vs 23)
**Location:** Implicit in SERVICE_CATALOG.md and prior session docs
**Original TBD:** Undocumented — prior sessions claimed 22, actual is 23
**Resolution:** VERIFIED 2026-06-23 — backend/services/ has 23 subdirectories (excluding __pycache__). The `summary/` service was not counted.
**Action taken:** Documented in DOC_DRIFT_REGISTER DD-010 and DOC_TO_CODE_DELTA_MATRIX.

---

## RESOLVED TBDs — Phase 3.25 Code Investigation (all closed)

### O-TBD-001: Email Validation — EmailStr vs Plain str — RESOLVED Phase 3.25
**Resolution:** Plain `str` type confirmed. `grep -r "EmailStr" backend/src/` = no matches. No email format validation in Python layer. VALIDATION_RULES.md updated.

### O-TBD-002: Phone Number Validation Regex — RESOLVED Phase 3.25
**Resolution:** No phone regex validator in codebase. Dedup is string equality. E.164 is convention + DB uniqueness only. VALIDATION_RULES.md updated.

### O-TBD-003: CNIC/NTN/STRN Database Fields — RESOLVED Phase 3.25
**Resolution:** Not in any DB schema (18 schemas searched). CNIC is optional JazzCash payment metadata only. VALIDATION_RULES.md updated.

### O-TBD-004: UUID Type in FastAPI Models — RESOLVED Phase 3.25
**Resolution:** `uuid.UUID` type in Pydantic BaseModel (e.g., Optional[uuid.UUID] in CreateCaseRequest). Generated with uuid4(). VALIDATION_RULES.md updated.

### O-TBD-005: Event Version Metadata (6 events) — RESOLVED Phase 3.25
**Resolution:** Full payload schemas in `backend/docs/infrastructure/event-catalog.md`. All 6 events documented with complete field lists. CONTRACT_VERSION_REGISTRY.md updated.

### O-TBD-006: Route Deprecation Strategy — RESOLVED Phase 3.25
**Resolution:** Not implemented. Single v1 prefix in use. No deprecation headers. Strategy deferred to C7 when v2 planned. CONTRACT_VERSION_REGISTRY.md updated.

### O-TBD-007: Dev Token Endpoint in Production — CONFIRMED RESOLVED (prior phase)
**Resolution:** G-MED-003 CLOSED — JWT_SECRET in render.yaml means dev endpoint always inactive in production.

### O-TBD-008: SLA Breach Background Scanner — CONFIRMED RESOLVED (prior phase)
**Resolution:** G-MED-002 CLOSED — SLA breach events confirmed emitted from services/cases/service.py.

---

## SAFE-DEFAULT Items (not "open" — deterministic defaults documented)

### P-TBD-001: JTI Blocklist In-Memory → Redis — SAFE-DEFAULT (Phase 3.25)
**Location:** `docs/03_fullstack_contracts/AUTH_AND_TENANCY_CONTRACT.md`, `docs/08_reports/BACKEND_GAP_REGISTER.md` G-CRIT-001
**Resolution:** SAFE-DEFAULT applied (OA-002). C6 is single-instance. Accept in-memory JTI blocklist for C6. Redis migration in Post-C6 Auth Sprint. Not an open TBD — it is a documented deferred item.
**Status:** SAFE-DEFAULT — no owner decision needed before C6 launch

### P-TBD-002: Refresh Token Revocation on Logout — SAFE-DEFAULT (Phase 3.25)
**Location:** `docs/03_fullstack_contracts/AUTH_AND_TENANCY_CONTRACT.md`, `docs/08_reports/BACKEND_GAP_REGISTER.md` G-HIGH-002
**Resolution:** SAFE-DEFAULT applied (OA-009). Accept 7-day refresh token window for C6. Bundle fix with OA-002 in Post-C6 Auth Sprint.
**Status:** SAFE-DEFAULT — no owner decision needed before C6 launch

### P-TBD-003: Frontend Scope-Based UI Gating — CONFIRMED NOT IMPLEMENTED (Phase 3.25 retry)
**Location:** `docs/03_frontend_authority/FRONTEND_GAP_REGISTER.md` G-007
**Resolution:** VERIFIED 2026-06-24 — no `hasScope` utility exists in crm-api.js or crm-shell.js. JWT scopes are never read by frontend JS. Now documented as implementation gap G-007 with "CONFIRMED — NOT IMPLEMENTED" status. FRONTEND_GAP_REGISTER.md updated. This is now a tracked implementation task, not a TBD.
**Status:** RESOLVED (gap confirmed, documented, tracked)

### P-TBD-004: contacts.delete Scope in RBAC — SAFE-DEFAULT (prior phase)
**Location:** `docs/08_reports/BACKEND_GAP_REGISTER.md` G-CRIT-002, `docs/03_fullstack_contracts/USER_ROLES_AND_PERMISSIONS.md`
**Resolution:** SAFE-DEFAULT applied (OA-001, SD-001). Grant contacts.delete to tenant_admin + super_admin. Deterministic from 6 existing delete scope examples. Pre-launch hotfix (2 lines in rbac-scopes.js).
**Status:** SAFE-DEFAULT — pattern confirmed from code evidence

### P-TBD-005–P-TBD-012
The remaining ~8 TBDs are distributed across old report documents (REMEDIATION_REPORT.md 18, GOVERNANCE_CONSISTENCY_AUDIT.md 36, GOVERNANCE_IMPLEMENTATION_REPORT.md 6). These are reports, not authority documents — their TBDs reflect open items at time of report generation and do not need to be resolved in place. They are informational.

---

## Files with Most TBDs (for reference)

| File | TBD Count | Note |
|------|-----------|------|
| docs/08_reports/GOVERNANCE_CONSISTENCY_AUDIT.md | 36 | Report — informational |
| docs/08_reports/REMEDIATION_REPORT.md | 18 | Old report — informational |
| docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md | 13 | Authority doc — needs resolution |
| docs/08_reports/GOVERNANCE_IMPLEMENTATION_REPORT.md | 6 | Report — informational |
| docs/01_backend/EVENT_AND_QUEUE_ARCHITECTURE.md | 6 | Authority doc — needs resolution |
| docs/01_backend/VALIDATION_RULES.md | 7 | Authority doc — investigate with grep |
| docs/03_fullstack_contracts/CONTRACT_VERSION_REGISTRY.md | 7 | Authority doc — investigate with grep |

---

*End TBD_RESOLUTION_REGISTER.md*
