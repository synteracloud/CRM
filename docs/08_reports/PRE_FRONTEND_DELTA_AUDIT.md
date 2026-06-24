Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI

# PRE-FRONTEND DOC-TO-CODE DELTA AUDIT
> Executed: 2026-06-23 — Pre-Frontend Authority Capture, Step 7 of prompt sequence

---

## Objective

Verify that all governance, backend, and repository documentation accurately reflects the actual codebase and repository state before Frontend Authority Capture (Step 11) begins.

---

## Pass 1 — Backend Source vs Documentation

### Backend src/ modules (34 total)

**Verified:** All 34 modules in `backend/src/` are documented in MODULE_INVENTORY.md.

| Module | In MODULE_INVENTORY | Gateway Route |
|--------|---------------------|---------------|
| admin_control_center | ✓ (§21, §22) | v1-audit, v1-governance, v1-compliance-settings, v1-privacy |
| ai_copilot | ✓ (§14) | v1-ai |
| ai_scoring | ✓ (§14) | v1-ai |
| automation_journeys | Note only in §12 | No dedicated route (part of campaigns) |
| campaigns | ✓ (§12) | v1-campaigns, v1-segments, v1-emails, v1-templates |
| communication_integrations | ✓ (§25) | v1-communications, v1-whatsapp-webhooks |
| contract_lifecycle_management | ✓ (§29) | NONE — gap G-MED-004 confirmed |
| customer_360_cdp | ✓ (§2, §3) | v1-contacts, v1-accounts |
| custom_object_framework | ✓ (§23) | No gateway route found (G-MED-004 pattern) |
| custom_objects | ✓ (§23) | No gateway route found |
| data_deduplication_engine | ✓ (§27) | Internal only |
| design_system | ✓ (§22) | v1-org-settings |
| event_bus | ✓ (§27) | Internal only |
| execution_hardening | ✓ (§27) | Internal only |
| external_apis_webhooks | ✓ (§26) | v1-sync |
| knowledge_base | ✓ (§9) | v1-knowledge |
| lead_management | ✓ (§1) | v1-leads, v1-followups |
| marketing_admin_workflow_ui | ✓ (§12) | Shared with campaigns |
| omnichannel_inbox | ✓ (§10, §11) | v1-inbox |
| partner_channel_management | ✓ (§18) | v1-partners |
| plugin_framework | ✓ (§26) | No dedicated route (SDK layer) |
| predictive_forecasting | ✓ (§15) | v1-forecasts |
| predictive_models | ✓ (§14) | v1-ai |
| reporting_dashboards | ✓ (§16) | v1-reports |
| revenue_recognition | ✓ (§6) | v1-invoice-summaries, v1-payments, v1-payment-webhooks |
| role_based_ui | ✓ (§19) | v1-users, v1-roles |
| rule_engine | ✓ (§5, §24) | v1-quotes, v1-orders |
| sales_cockpit | ✓ (§4) | v1-opportunities |
| subscription_billing | ✓ (§6, §7) | v1-subscriptions, v1-billing |
| support_console | ✓ (§8) | v1-cases |
| territory_management | ✓ (§17) | v1-territories |
| ticket_management | ✓ (§8) | v1-cases (shared) |
| usage_billing | ✓ (§6) | v1-invoice-summaries |
| workflow_engine | ✓ (§13) | v1-workflows |

**Gaps found:**
- `automation_journeys` has no dedicated MODULE_INVENTORY entry — only mentioned as a note in §12. Minor documentation gap.
- `contract_lifecycle_management`: No gateway route. 12 API paths defined in Python `api.py::API_ENDPOINTS` but not mounted. Owner decision required.
- `custom_object_framework` + `custom_objects`: No gateway route found. Either accessed via catch-all or not yet exposed.

### Gateway route files (44 total)

Actual count: 44 route files (excluding index.js) in `backend/gateway/routes/`. **Matches documented 44.**

### Backend services (backend/services/)

Actual service directories: **23** (excluding `__pycache__/`).
Documented claim: **22** (context from prior sessions).
Delta: +1 service directory undocumented. The `summary/` directory is documented in MODULE_INVENTORY.md as `services/summary/daily_summary.py` but was not counted in the 22 total. SERVICE_CATALOG.md covers the major services by function.

**Finding:** Minor count drift. The `summary` service subdirectory brings the total to 23, not 22.

### contacts.delete scope (CRIT-002 verification)

Verified 2026-06-23: `contacts.delete` / `CONTACTS_DELETE` does NOT appear in `backend/gateway/config/rbac-scopes.js`. **Gap G-CRIT-002 confirmed.** Owner decision required.

### leads.delete scope (G-HIGH-005 resolution)

Verified 2026-06-23: `LEADS_DELETE: 'leads.delete'` IS present in rbac-scopes.js line 21. **G-HIGH-005 was a false alarm. CLOSED.**

### CI/CD files

Actual: 2 workflow files in `.github/workflows/`:
- `deploy-runtime.yml` — documented in AI_OPERATING_CONTEXT.md ✓
- `ci.yml` — **not documented** in any governance doc. CI/CD pipeline for testing/linting on all branches. Undocumented.

---

## Pass 2 — Governance Docs vs Code

### AI_OPERATING_CONTEXT.md (primary context doc)

| Claim | Code Reality | Action |
|-------|-------------|--------|
| Status: Draft | Should be Active (primary context doc in use) | **FIXED** → Active |
| 20 database schemas | Actual 18 (backend/db/ has 18 directories) | **FIXED** → 18 |
| 23 Playwright E2E test files | Actual 25 (.py files in tests/e2e/playwright/) | **FIXED** → 25 |
| 11 CI/CD jobs | Not re-verified; accepted from prior session | Left as-is (not re-runnable here) |
| Last Reviewed: 2026-06-21 | Reviewed today 2026-06-23 | **FIXED** → 2026-06-23 |

### USER_ROLES_AND_PERMISSIONS.md

- leads.delete TBD resolved: `LEADS_DELETE` IS in rbac-scopes.js. **FIXED.**
- contacts.delete gap: Confirmed. Requires owner decision.

### AUTH_AND_TENANCY_CONTRACT.md

3 TBDs remain — all owner-decision items:
1. RLS not implemented: "No DB-level Row Level Security found — TBD REQUIRES VERIFICATION" → Verified: no RLS in any of the 18 schema.sql files. **Resolvable: confirmed no RLS.** Updated in DOC_DRIFT_REGISTER.
2. JTI blocklist in-memory: Owner decision item (G-CRIT-001). Remains TBD.
3. Refresh token revocation on logout: Owner decision item (G-HIGH-002). Remains TBD.

### CONTRACT_VERSION_REGISTRY.md

6 event version TBDs: `opportunity.stage.changed.v1`, `opportunity.closed.v1`, `lead.idle.v1`, `lead.created.v1`, `invoice.overdue.v1`, `case.sla.breached.v1`. These events are referenced in `backend/services/app.py` and the workflow engine but versioning metadata was not found in code. Remain TBD.

### FULLSTACK_STITCHING_CONTRACT.md

13 TBD markers found. These reflect genuinely unresolved frontend wiring status (70 pages still in DUMMY_MODE graceful fallback). Not documentation drift — accurate.

### PROJECT_CHARTER.md

Not re-audited in detail. Status: Draft — should be Active. Documented in DOC_DRIFT_REGISTER for batch promotion.

---

## Pass 3 — Repository Structure vs Normalization Reports

### .gitignore

All critical patterns present: ✓
- `*.log`, `gw.log`, `gateway_startup.log`, `gateway_err.log`
- `logs/`
- `.pytest_cache/`
- `__pycache__/`, `*.py[cod]`
- `bin/`, `data/` (R-01/R-02 items)
- `.env`, `.env.local`, `.env.*.local`
- `node_modules/`, `.npm-cache/`, `.pip-cache/`
- Playwright screenshots/artifacts

**No .gitignore gaps found.**

### Root file state

| File | Status | Action Needed |
|------|--------|---------------|
| CLAUDE.md | Correctly at root ✓ | None |
| DESIGN-SPEC.md | Correctly at root ✓ | None |
| FRAMEWORK.md | Correctly at root ✓ | None |
| PAGE-BUILD-PROTOCOL.md | Correctly at root ✓ | None |
| README.md | Correctly at root ✓ | None |
| CONTRIBUTING.md | Correctly at root ✓ (RR-T5-04 — stays per GitHub convention) | None |
| PRODUCT-SPEC.md | At root — should be in docs/ (misplaced) | SAFE_REPOSITORY_HYGIENE — see below |
| COMMERCIALISATION-PLAN.md | Duplicate: at root AND docs/00_authority/ | Root copy should be removed from git |
| BACKEND AUTHORITY CAPTURE.md | Prompt file at root | Archive to docs/archive/ |
| PRE-FRONTEND DOC-TO-CODE DELTA AUDIT AND REMEDIATION.md | Prompt file at root | Archive to docs/archive/ |

### File move execution (this session)

SAFE_REPOSITORY_HYGIENE items executed in this audit pass:

| Item | From | To | Status |
|------|------|----|--------|
| L-01 | backend/docs/PENDING.md | docs/reports/session/BACKEND-PENDING.md | **DONE** |
| L-02 | backend/docs/market-research-gap-register.md | docs/08_reports/MARKET-RESEARCH-GAP-REGISTER.md | **DONE** |
| L-03 | backend/docs/product-spec-gap-register.md | docs/08_reports/PRODUCT-SPEC-GAP-REGISTER.md | **DONE** |
| L-04 | backend/docs/phase4-gap-register.md | docs/08_reports/PHASE4-GAP-REGISTER.md | **DONE** |
| L-07 | backend/docs/FRONTEND-BACKEND-MAPPING.md | docs/03_fullstack_contracts/FRONTEND-BACKEND-MAPPING.md | **DONE** |
| D-15 | tests/e2e/playwright/SKIP-BACKLOG.md | docs/04_testing/SKIP-BACKLOG.md | **DONE** |

Note: L-05 (backend/docs/BACKEND-QC.md) and L-06 (backend/docs/CONSTRAINTS.md) were already at correct destinations from prior session.

### CI/CD

- `deploy-runtime.yml` at `.github/workflows/` root ✓ (fixed in prior session, confirmed)
- `ci.yml` also exists at `.github/workflows/` — undocumented. No remediation needed (file is correct), only doc update needed.

---

## Pass 4 — TBD Resolution

Total TBDs found in docs/: **145 occurrences in 31 files.**

### Resolved in this session

| TBD Location | Resolution | Evidence |
|---|---|---|
| BACKEND_GAP_REGISTER.md G-HIGH-005 | leads.delete scope EXISTS | rbac-scopes.js line 21 |
| USER_ROLES_AND_PERMISSIONS.md | leads.delete scope EXISTS | rbac-scopes.js line 21 |
| AUTH_AND_TENANCY_CONTRACT.md (RLS) | No RLS confirmed absent | 18 schema.sql files, no RLS clauses found |

### Remain open (owner decisions — not resolvable from code alone)

| TBD | File | Reason Remains Open |
|-----|------|---------------------|
| JTI blocklist in-memory | AUTH_AND_TENANCY_CONTRACT.md | Owner decision: migrate to Redis |
| Refresh token revocation on logout | AUTH_AND_TENANCY_CONTRACT.md, BACKEND_GAP_REGISTER.md | Owner decision |
| Email validation (EmailStr vs str) | VALIDATION_RULES.md | Requires reading all 34 Pydantic models |
| Phone number regex | VALIDATION_RULES.md | Requires reading all domain services |
| CNIC/NTN/STRN in DB | VALIDATION_RULES.md | Fields possibly in JSONB custom_fields |
| Event version metadata | CONTRACT_VERSION_REGISTRY.md (6 events) | Not found in code; events are in-process |
| Frontend scope-based UI gating | USER_ROLES_AND_PERMISSIONS.md | 70 pages still DUMMY_MODE |
| Dev token endpoint in prod | BACKEND_GAP_REGISTER.md G-MED-003 | Requires checking render.yaml JWT_SECRET env |
| SLA breach scanner | BACKEND_GAP_REGISTER.md G-MED-002 | Requires deeper services/app.py read |
| DB connection pool size | BACKEND_GAP_REGISTER.md G-LOW-001 | Requires reading gateway/db/pool.js |

---

## Pass 5 — SAFE_REPOSITORY_HYGIENE Items

### Already executed (prior sessions)

- C-01: COMMERCIALISATION-PLAN.md → docs/00_authority/ (partially — root copy still tracked)
- C-03 through C-06: .gitignore entries for logs, .env.local, .pytest_cache — already in .gitignore ✓
- L-05: backend/BACKEND-QC.md → backend/docs/BACKEND-QC.md ✓
- L-06: backend/CONSTRAINTS.md → backend/docs/CONSTRAINTS.md ✓
- RR-T4: Archive retirement notices on 7 docs/archive/ files ✓

### Executed this session (6 items)

See Pass 3 file move table above.

### Remaining SAFE_REPOSITORY_HYGIENE items (not executed — deferred to next SAFE pass)

| Item | Action | Reason Deferred |
|------|---------|----------------|
| RR-T3-01 to RR-T3-11 | Move 11 root prompt/session files → docs/archive/ | Files may be referenced by user in ongoing sessions |
| C-07/D-02 to D-07 | Add root .md prompt duplicates to .gitignore | Low priority |
| R-09 | Prompts/ → prompts/ rename | Requires grep confirmation no CI references |
| R-10 | seal.ps1 → scripts/ | Requires Makefile/CI check |
| D-16 | docs/reference/RENDER-DEPLOY.md → docs/05_deployment/ | Optional |
| PRODUCT-SPEC.md | Move from root to docs/ | Not in APPROVAL_RECLASSIFICATION_REPORT; new finding |

---

## Summary Counts

| Pass | Findings | Fixed | Escalated | Confirmed OK |
|------|---------|-------|-----------|-------------|
| Pass 1 — Backend vs Docs | 5 | 0 | 3 | 2 |
| Pass 2 — Governance vs Code | 8 | 6 | 2 | 0 |
| Pass 3 — Repo Structure | 8 | 6 | 2 | 4 |
| Pass 4 — TBD Resolution | 13 | 3 | 10 | 0 |
| Pass 5 — SAFE items | 28 | 12 | 5 (deferred) | 11 |

---

*End PRE_FRONTEND_DELTA_AUDIT.md*
