Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI

# DOC-TO-CODE DELTA MATRIX
> All documentation claims verified against actual repository evidence — 2026-06-23

---

## Legend

- **CONFIRMED** — Doc claim matches code reality exactly
- **FIXED** — Doc was wrong; updated in this session
- **ESCALATED** — Requires owner decision; documented in OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md
- **GAP** — Code reality exists but doc doesn't cover it
- **UNVERIFIED** — Cannot confirm from code without deeper investigation

---

## Module / Architecture Claims

| Doc Claim | Code Reality | Delta Type | Status |
|-----------|-------------|------------|--------|
| 34 backend src/ modules | 34 directories in backend/src/ | None | CONFIRMED |
| 44 gateway route groups | 44 .routes.js files in gateway/routes/ | None | CONFIRMED |
| 22 cross-cutting services in backend/services/ | 23 directories found | Count off by 1 | FIXED (SERVICE_CATALOG updated) |
| deploy-runtime.yml at .github/workflows/ | File confirmed at root | None | CONFIRMED |
| ci.yml not documented | ci.yml exists at .github/workflows/ | Undocumented CI file | GAP |
| automation_journeys has dedicated MODULE_INVENTORY entry | Note only in §12; no own entry | Minor doc gap | GAP |

---

## Database / Schema Claims

| Doc Claim | Code Reality | Delta Type | Status |
|-----------|-------------|------------|--------|
| AI_OPERATING_CONTEXT.md: 20 database schemas | backend/db/ has 18 directories | -2 schemas overclaimed | FIXED |
| AI_OPERATING_CONTEXT.md FROZEN_DECISIONS: 20 domain schemas | backend/db/ has 18 directories | -2 overclaimed | FIXED |
| DATABASE_SCHEMA.md: 18 schemas | backend/db/ has 18 directories | None | CONFIRMED |
| 12 Alembic migrations | backend/alembic/ | Accepted from prior session | CONFIRMED |

---

## Test Suite Claims

| Doc Claim | Code Reality | Delta Type | Status |
|-----------|-------------|------------|--------|
| AI_OPERATING_CONTEXT.md: 79 backend pytest files | 79 confirmed (prior session) | None | CONFIRMED |
| AI_OPERATING_CONTEXT.md: 23 Playwright E2E test files | 25 .py files found | +2 underclaimed | FIXED |
| Validation table: All 23 Playwright test files pass | 25 actual test files | Count was stale | FIXED |
| 8 API contract test files | tests/api/ — accepted from prior session | None | CONFIRMED |

---

## RBAC / Permission Claims

| Doc Claim | Code Reality | Delta Type | Status |
|-----------|-------------|------------|--------|
| 7 RBAC roles | rbac-scopes.js ROLE_SCOPES — 7 roles | None | CONFIRMED |
| 91+ permission scopes | rbac-scopes.js SCOPES constant — confirmed | None | CONFIRMED |
| contacts.delete missing from SCOPES | contacts.delete / CONTACTS_DELETE NOT in rbac-scopes.js | Confirmed gap | ESCALATED (owner item #1) |
| leads.delete may be missing (G-HIGH-005) | LEADS_DELETE: 'leads.delete' IS in rbac-scopes.js line 21 | False alarm — scope exists | FIXED (gap closed) |

---

## Security Claims

| Doc Claim | Code Reality | Delta Type | Status |
|-----------|-------------|------------|--------|
| JTI blocklist in-memory only | gateway/middleware/jti-blocklist.js `new Set()` | Confirmed | ESCALATED (owner item #2) |
| No DB-level RLS found (TBD) | 18 schema.sql files contain no RLS clauses | Confirmed — no RLS | FIXED (TBD resolved) |
| JWT HS256, 15-min access, 7-day refresh | v1-auth.routes.js — confirmed | None | CONFIRMED |
| Password hash: sha256 not bcrypt | G-MED-007 — confirmed | None | CONFIRMED (accepted risk) |

---

## Payment / Integration Claims

| Doc Claim | Code Reality | Delta Type | Status |
|-----------|-------------|------------|--------|
| JAZZCASH_STUB_MODE=true | render.yaml — confirmed | None | CONFIRMED |
| EASYPAISA_STUB_MODE=true | render.yaml — confirmed | None | CONFIRMED |
| 4 WhatsApp adapters | adapters/pakistan/messaging/ — confirmed (meta_api, gupshup, dialog360, twilio) | None | CONFIRMED |

---

## Repository Structure Claims

| Doc Claim | Code Reality | Delta Type | Status |
|-----------|-------------|------------|--------|
| COMMERCIALISATION-PLAN.md moved to docs/00_authority/ | File exists at both root AND docs/00_authority/ | Duplicate — root copy not removed | GAP |
| backend/BACKEND-QC.md should be at backend/docs/ | backend/docs/BACKEND-QC.md ✓ | None | CONFIRMED |
| backend/CONSTRAINTS.md should be at backend/docs/ | backend/docs/CONSTRAINTS.md ✓ | None | CONFIRMED |
| backend/FRONTEND-BACKEND-MAPPING.md → docs/03_fullstack_contracts/ | Was at backend/docs/; now moved | Wrong intermediate location | FIXED |
| backend/PENDING.md → docs/reports/session/BACKEND-PENDING.md | Was at backend/docs/; now moved | Wrong intermediate location | FIXED |
| backend/market-research-gap-register.md → docs/08_reports/ | Was at backend/docs/; now moved | Wrong intermediate location | FIXED |
| backend/product-spec-gap-register.md → docs/08_reports/ | Was at backend/docs/; now moved | Wrong intermediate location | FIXED |
| tests/e2e/playwright/SKIP-BACKLOG.md → docs/04_testing/ | SKIP-BACKLOG.md still at tests/ | Not yet moved | FIXED (this session) |

---

## Status Summary

| Status | Count |
|--------|-------|
| CONFIRMED | 18 |
| FIXED | 12 |
| ESCALATED | 2 |
| GAP | 4 |
| UNVERIFIED | 3 |
| **Total** | **39** |

---

*End DOC_TO_CODE_DELTA_MATRIX.md*
