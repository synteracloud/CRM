Status: Draft
Authority Level: Medium
Last Reviewed: 2026-06-21
Owner: Shared

---

# ARCHITECTURAL GAP REGISTER — Pakistan CRM OS

## Purpose

This register documents every area with missing documentation, missing implementation, or known architectural gaps. Items are sourced from U10 unresolved items, U6 delta findings, U9 test gaps, and Governance Phase 1 audit.

**Severity classification:**
- CRITICAL: Blocks commercial use or creates security risk
- HIGH: Significant functionality gap or documentation mislead
- MEDIUM: Partial coverage; workaround exists
- LOW: Cosmetic or informational gap

---

## Register

### GAP-001 — JazzCash/Easypaisa Live Integration
**Area:** Payment Rails
**Gap Description:** JazzCash and Easypaisa payment adapters are implemented but configured with stub_mode=True in render.yaml. Real PKR payment processing cannot be tested or used.
**Severity:** CRITICAL (blocks revenue collection for customers)
**Source:** AUTHORITY_RECONSTRUCTION_REPORT.md §7; render.yaml; COMMERCIALISATION-PLAN.md P-016
**Recommended Action:** Receive P-016 credentials; run full sandbox E2E test via test_workflow_invoice.py; set JAZZCASH_STUB_MODE=false and EASYPAISA_STUB_MODE=false in Render environment only after sandbox tests pass
**Status:** Blocked externally (P-016)

---

### GAP-002 — AI Inference Model Not Selected
**Area:** AI / Copilot
**Gap Description:** No AI inference provider SDK (OpenAI/Anthropic/Google Generative AI) is in requirements.txt. All AI models (lead scoring, churn prediction, CLV estimation, copilot query) are rule-based computations. ai-copilot.html (M-01) is an advisory-only shell.
**Severity:** HIGH (documented AI features do not use AI inference)
**Source:** AUTHORITY_RECONSTRUCTION_REPORT.md §11; CURRENT_PROJECT_STATUS.md §Known Issues
**Recommended Action:** Decide AI provider (D-004 in KNOWN_CONSTRAINTS); add SDK to requirements.txt; implement inference calls in ai_copilot, ai_scoring, predictive_models; write ADR-003 (governance numbering)
**Status:** Open — human decision required

---

### GAP-003 — contract_lifecycle_management Has No Gateway Route
**Area:** Contract Lifecycle Management (Module 29)
**Gap Description:** backend/src/contract_lifecycle_management/ module is complete (Python api.py, entities.py, services.py, 12 API endpoints defined). No v1-contract*.routes.js exists in gateway/routes/. The module has no frontend pages.
**Severity:** HIGH (module is invisible to frontend; cannot be used)
**Source:** BACKEND_DOC_ALIGNMENT_STATUS.md D-001; MODULE_INVENTORY.md Module 29; U10_FINAL_STATUS.md D-001
**Recommended Action:** Human decides: (a) Create v1-contract-lifecycle.routes.js gateway route and expose the 12 endpoints, or (b) Archive the module as completed backend work with no frontend surface in v1
**Status:** Open — human decision required (D-001)

---

### GAP-004 — custom_objects Module Routing Mechanism Unknown
**Area:** Custom Objects (Module 22)
**Gap Description:** backend/src/custom_object_framework/ and backend/src/custom_objects/ confirmed in backend. object-builder.html (K-02) is built. No v1-custom-objects.routes.js found in gateway route list. Routing mechanism is unresolved.
**Severity:** HIGH (UI page exists; backend exists; API connection unknown)
**Source:** AUTHORITY_RECONSTRUCTION_REPORT.md §11; BACKEND_DOC_ALIGNMENT_STATUS.md D-002; U10_FINAL_STATUS.md D-002
**Recommended Action:** Verify if custom objects are proxied via an existing catch-all route or if v1-custom-objects.routes.js needs creating. If missing: create the gateway route file. Document the decision in ADR format.
**Status:** Open — human decision required (D-002)

---

### GAP-005 — Live-API Re-verification Pass Incomplete
**Area:** Frontend-API Integration
**Gap Description:** 70 of 75 custom HTML pages have DUMMY_MODE graceful fallback behavior. While crm-api.js has DUMMY_MODE: false set in C1, many pages may have local overrides or untested live-API paths. Only 5 pages are confirmed fully wired: G-05 (integrations), H-07 (report-builder), J-03 (data-governance), A-08 (engagement-dashboard), G-04 (billing — content blocked P-016).
**Severity:** HIGH (end-to-end integration not fully verified)
**Source:** CURRENT_PROJECT_STATUS.md §API Wiring State; COMMERCIALISATION-PLAN.md §C6
**Recommended Action:** Complete Phase 6 Component 3 — full live-API re-verification pass for all 75 pages; update CURRENT_PROJECT_STATUS.md for each wired page
**Status:** In progress — C6 current phase

---

### GAP-006 — T-Level Audit Backlog (5 Pages)
**Area:** Frontend Quality
**Gap Description:** 5 pages have documented T1–T4 defects from DESIGN-SPEC.md §3 notes: followups.html (B-01), leads.html (B-02), contacts.html (B-03), collections.html (B-08), lead-new.html (I-01).
**Severity:** MEDIUM (pages functional; cosmetic/alignment issues)
**Source:** CURRENT_PROJECT_STATUS.md §T-Level Audit Backlog
**Recommended Action:** Apply T1–T4 fixes per PAGE-BUILD-PROTOCOL.md and CLAUDE.md build checklist; focus on: crm-custom.css Place 3 CSS, filter chip vocabulary, hardcoded delta text
**Status:** Open

---

### GAP-007 — Urdu Customer-Facing Strings Pending Review
**Area:** Localization
**Gap Description:** Urdu notification strings and customer-facing text (G-06 notifications.html) are built with EN strings. Urdu strings exist in codebase with <!-- UR_TODO: --> markers. RTL CSS (styles-rtl.css) and locale infrastructure (crm-locale.js) are complete. Blocked pending native speaker review.
**Severity:** MEDIUM (product usable in English; Urdu capability documented but not usable)
**Source:** COMMERCIALISATION-PLAN.md P-017; AUTHORITY_RECONSTRUCTION_REPORT.md §11
**Recommended Action:** Arrange native Urdu speaker review of all _STRINGS['ur'] values in crm-locale.js and notification template strings; get sign-off; remove UR_TODO comments
**Status:** Blocked externally (P-017)

---

### GAP-008 — Application-Level Tenant Isolation (vs RLS)
**Area:** Security Architecture
**Gap Description:** Tenant isolation is enforced at application layer (x-tenant-id header + WHERE tenant_id = $1 in every query) rather than PostgreSQL Row-Level Security (RLS). A bug in gateway middleware or a query missing tenant_id could expose cross-tenant data.
**Severity:** MEDIUM (mitigated by semgrep CI rule; test_tenant_isolation.py)
**Source:** AUTHORITY_RECONSTRUCTION_REPORT.md §6; FULLSTACK_STITCHING_CONTRACT.md §9
**Recommended Action:** Write ADR-002 (governance numbering) formally documenting the application-level isolation decision and its mitigation controls; consider adding property-based tests for tenant isolation in high-risk routes
**Status:** Accepted risk — mitigation in place; ADR recommended

---

### GAP-009 — starlette CVEs (3 Known)
**Area:** Security — Dependency
**Gap Description:** 3 CVEs in starlette transitive dependency. Cannot upgrade due to FastAPI 0.115 compatibility constraint.
**Severity:** MEDIUM (accepted risk; no exploit known for this usage pattern)
**Source:** U10_FINAL_STATUS.md; SECURITY_TEST_PLAN.md; HARDENING_PLAN.md
**Recommended Action:** Monitor FastAPI upstream for fix; upgrade starlette when FastAPI compatibility permits; re-run pip-audit after each upgrade
**Status:** Accepted risk

---

### GAP-010 — 5 Entity DB Schema Attributions Unverified
**Area:** Documentation Accuracy
**Gap Description:** 5 entities have fields inferred from gateway code, not directly read from schema.sql: Activities (activity_task_db), Tasks (activity_task_db), Accounts (contact_account_db), Quotes (quote_order_db), Orders (quote_order_db). No incorrect claims are known — these are approximations.
**Severity:** LOW (informational; entities function correctly)
**Source:** BACKEND_DOC_ALIGNMENT_STATUS.md D-003
**Recommended Action:** Read db/activity_task_db/schema.sql, db/contact_account_db/schema.sql, db/quote_order_db/schema.sql directly and verify field accuracy; update ENTITY_INVENTORY.md and DOMAIN_MODEL.md
**Status:** Open — low priority

---

### GAP-011 — Password Hashing Algorithm Not Documented
**Area:** Security Documentation
**Gap Description:** v1-auth.routes.js handles password hashing but the algorithm (bcrypt/argon2/scrypt) is not documented in any governance document. This is confirmed to exist in code but not directly verified during U-series.
**Severity:** LOW (security works; documentation gap only)
**Source:** FULLSTACK_STITCHING_CONTRACT.md §8 (marked TBD – REQUIRES VERIFICATION)
**Recommended Action:** Read backend/gateway/routes/v1-auth.routes.js password hash section; document the algorithm in ADR-001_PROJECT_FOUNDATION.md §3.6
**Status:** Open — low priority

---

### GAP-012 — Automation Journeys Specification Incomplete
**Area:** Workflow Automation
**Gap Description:** src/automation_journeys/ module confirmed in backend (api.py, entities.py, services.py, workflow_mapping.py). The specification beyond "multi-step marketing/sales automation journeys" is not documented in governance documents.
**Severity:** LOW (module exists; system workflow documentation is complete; journeys are a superset)
**Source:** WORKFLOW_INVENTORY.md §Automation Journey Modules; MODULE_INVENTORY.md
**Recommended Action:** Read backend/src/automation_journeys/api.py and services.py; document supported journey types, trigger conditions, step types in PRODUCT_WORKFLOWS.md
**Status:** Open — low priority

---

### GAP-013 — Load Test Results Not in Repository
**Area:** Testing / Performance
**Gap Description:** Load tests (Locust) were defined in C2d. Reports expected at D:\CRM\tests\load\reports\. These reports are not in the repository (gitignored or not committed). p95 targets and actual results not verified from code.
**Severity:** MEDIUM (targets defined; actual results unknown)
**Source:** COMMERCIALISATION-PLAN.md §C2d; LOAD_TEST_PLAN.md
**Recommended Action:** Run load test suite; commit summary report to tests/load/reports/ (aggregate, not binary); update TEST_SUITE_PLAN.md with actual p95 results
**Status:** Open

---

### GAP-014 — OWASP ZAP Security Scan Reports Not in Repository
**Area:** Security Testing
**Gap Description:** OWASP ZAP scans were run in C2e and C5 against local and production. Reports expected at D:\CRM\tests\security\. Not confirmed in repository.
**Severity:** MEDIUM (scans ran; gate passed per C5 completion; reports not persisted)
**Source:** COMMERCIALISATION-PLAN.md §C2e; SECURITY_TEST_PLAN.md
**Recommended Action:** Confirm reports in tests/security/; if missing, re-run ZAP against production API; commit zap-report.html and zap-prod-report.html
**Status:** Open

---

### GAP-015 — Facebook/Instagram Lead Capture Not Implemented
**Area:** Lead Capture
**Gap Description:** MR-001 (Facebook/Instagram lead capture) is permanently blocked pending Meta Business Manager setup. A hidden div with data-unblock="MR-001" exists in UI but no functional code.
**Severity:** LOW (documented as out-of-scope for v1)
**Source:** COMMERCIALISATION-PLAN.md §Permanently Blocked Items; FEATURE_SCOPE.md
**Recommended Action:** No action until Meta Business Manager account is approved and MR-001 is explicitly unblocked by human decision
**Status:** Blocked externally (MR-001)

---

### GAP-016 — 4 Backend Docs Placement Unresolved
**Area:** Documentation Organization
**Gap Description:** backend/docs/phase4-gap-register.md and 3 other docs may be historical artifacts from build phases but remain in active backend/docs/ tree. Human decision on archive vs keep.
**Severity:** LOW (organizational; no functional impact)
**Source:** U10_FINAL_STATUS.md D-005
**Recommended Action:** Human reviews backend/docs/phase4-gap-register.md and 3 similar files; decides archive or keep as reference; moves to docs/archive/ if archiving
**Status:** Open — human decision required (D-005)

---

## Priority Summary

| Severity | Count | Items |
|---|---|---|
| CRITICAL | 1 | GAP-001 (payment integration) |
| HIGH | 4 | GAP-002 (AI inference), GAP-003 (contract lifecycle), GAP-004 (custom objects routing), GAP-005 (live-API re-verification) |
| MEDIUM | 5 | GAP-006 (T-level audit), GAP-007 (Urdu), GAP-008 (tenant isolation docs), GAP-009 (starlette CVEs), GAP-010 (entity schemas), GAP-013 (load tests), GAP-014 (ZAP reports) |
| LOW | 4 | GAP-011 (password hash docs), GAP-012 (automation journeys), GAP-015 (Facebook leads), GAP-016 (backend docs placement) |
| BLOCKED | 3 | GAP-001 (P-016), GAP-007 (P-017), GAP-015 (MR-001) |

---

*End ARCHITECTURAL_GAP_REGISTER.md*
