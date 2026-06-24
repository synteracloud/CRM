Status: Active
Authority Level: Medium
Generated: 2026-06-22
Owner: AI (Claude Sonnet 4.6 — Documentation Normalization session)

---

# CONFLICT ANALYSIS REPORT — Pakistan CRM OS

## Purpose

Identifies every case where two documents make contradictory claims about the same fact. After the U0–U10 series and Governance Phase 1 remediation, most pre-governance conflicts were resolved. This report covers the current state of the full corpus as of 2026-06-22.

**Supersedes:** `docs/reports/u-series/DOC_CONFLICT_REGISTER.md` (U3 — covered pre-governance conflicts; most now resolved)

**Pre-existing resolved conflicts (from U3 DOC_CONFLICT_REGISTER.md):**
- C-001: SYSTEM-SNAPSHOT.md vs COMMERCIALISATION-PLAN.md phase status — PARTIALLY RESOLVED (COMMERCIALISATION-PLAN.md is correct; SYSTEM-SNAPSHOT.md still stale — see CF-001 below)
- C-002: COMMERCIALISATION-PLAN.md internal inconsistency (RESUME POINT table) — RESOLVED by U10 (table now says C5/C6 with check marks)
- C-003: Frontend API wiring doc claims vs code — RESOLVED by U10 (AI_OPERATING_CONTEXT.md now correctly states 5 pages wired)
- C-004 through C-007: Various stale reference conflicts — RESOLVED by U10 remediation

---

## How to Read This Report

| Column | Meaning |
|---|---|
| ID | Conflict identifier (CF-xxx) |
| Doc A | First document and its claim |
| Doc B | Second document and its contradicting claim |
| Severity | Critical / High / Medium / Low |
| Authority | Which document is correct |
| Resolution | Resolved / Flagged / Accepted |

---

## Active Conflicts (Unresolved)

### CF-001 — SYSTEM-SNAPSHOT.md: C3 vs C6 current phase

| Field | Value |
|---|---|
| **Doc A** | `docs/reports/session/SYSTEM-SNAPSHOT.md` line 5: "C2 Automated Test Suite COMPLETE. C3 Code Hardening is next." |
| **Claim in A** | Current phase is C3 |
| **Doc B** | `docs/07_governance/AI_OPERATING_CONTEXT.md` CURRENT_PHASE: "Phase: C6 — Commercial Launch — Status: Active" |
| **Claim in B** | Current phase is C6 |
| **Severity** | High — SYSTEM-SNAPSHOT.md is designated as the "first file to read at session start" in its own header. An AI reading it first will orient to C3 work that is 3 phases complete. |
| **Authority** | AI_OPERATING_CONTEXT.md (Critical authority) and COMMERCIALISATION-PLAN.md (operational authority) both say C6. SYSTEM-SNAPSHOT.md is dated 2026-06-01; AI_OPERATING_CONTEXT.md was last reviewed 2026-06-21. C6 is correct. |
| **Resolution** | **OPEN — flagged for update.** SYSTEM-SNAPSHOT.md must be updated to reflect C6 or replaced with a redirect to AI_OPERATING_CONTEXT.md. Until resolved: AI agents must read AI_OPERATING_CONTEXT.md before SYSTEM-SNAPSHOT.md and treat AI_OPERATING_CONTEXT.md as authoritative on phase. |
| **Action** | Update SYSTEM-SNAPSHOT.md body to current state, or add banner: "STALE — see docs/07_governance/AI_OPERATING_CONTEXT.md for current phase." |

---

### CF-002 — CURRENT_PROJECT_STATUS.md: 43 gateway route groups vs 44

| Field | Value |
|---|---|
| **Doc A** | `docs/reports/u-series/CURRENT_PROJECT_STATUS.md` line 9: "43 gateway route groups" |
| **Claim in A** | 43 gateway route groups |
| **Doc B** | `docs/07_governance/AI_OPERATING_CONTEXT.md`, `docs/00_authority/PROJECT_CHARTER.md` §5, `docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md` line 22, `docs/reports/u-series/API_INVENTORY.md` header | 
| **Claim in B** | 44 gateway route groups (corrected by U10 remediation 2026-06-21) |
| **Severity** | Medium — this is a stale number that was corrected everywhere except CURRENT_PROJECT_STATUS.md. Documented as SR-009 in DOC_STALE_REFERENCE_REPORT.md. |
| **Authority** | 44 is correct. AUTHORITY_RECONSTRUCTION_REPORT.md has "[corrected from 43 by U10 remediation 2026-06-21]" in header. API_INVENTORY.md header was updated to "(44 files)". |
| **Resolution** | **OPEN — stale reference.** CURRENT_PROJECT_STATUS.md line 9 needs updating from "43" to "44". SR-009 from U10 was documented as "acceptable — cosmetic." However it is a factual error. |
| **Action** | Update CURRENT_PROJECT_STATUS.md line 9 "43 gateway route groups" to "44 gateway route groups" |

---

### CF-003 — SESSION-HANDOFF.md: session startup sequence conflicts with AI_OPERATING_CONTEXT.md

| Field | Value |
|---|---|
| **Doc A** | `docs/reports/session/SESSION-HANDOFF.md` — directs sessions to start with SYSTEM-SNAPSHOT.md |
| **Claim in A** | Session startup: "Read SYSTEM-SNAPSHOT.md first" |
| **Doc B** | `docs/07_governance/AI_OPERATING_CONTEXT.md` — is the designated primary context document |
| **Claim in B** | "Read this document FIRST before reading any source code" |
| **Severity** | Medium — SESSION-HANDOFF.md is stale (pre-governance); AI_OPERATING_CONTEXT.md was created in Governance Phase 1 to supersede the SYSTEM-SNAPSHOT.md startup pattern. |
| **Authority** | AI_OPERATING_CONTEXT.md governs. Its header says "Read this document FIRST." |
| **Resolution** | **OPEN — stale reference.** SESSION-HANDOFF.md needs updating to reference AI_OPERATING_CONTEXT.md as the session opener. |
| **Action** | Update SESSION-HANDOFF.md to reference AI_OPERATING_CONTEXT.md → COMMERCIALISATION-PLAN.md → PENDING.md as the session startup sequence |

---

### CF-004 — DOMAIN_MODEL.md §Territory: criteria_type values diverge across documents

| Field | Value |
|---|---|
| **Doc A** | `docs/00_authority/DOMAIN_MODEL.md` §Territory: "criteria_type: geographic/postal/account_segment/rep_assigned/hybrid — from runtime API" |
| **Claim in A** | Runtime criteria_type values: geographic, postal, account_segment, rep_assigned, hybrid |
| **Doc B** | `backend/docs/domain/territory-management.md` — may describe older conceptual values (geography/industry/account_size/custom) |
| **Severity** | Low — DOMAIN_MODEL.md itself notes the discrepancy: "Runtime-enforced values (from gateway v1-territories.routes.js) are: geographic, postal, account_segment, rep_assigned, hybrid. These supersede the conceptual values in earlier documentation." The conflict is self-documented. |
| **Authority** | `gateway/routes/v1-territories.routes.js` (code); DOMAIN_MODEL.md correctly defers to code evidence. |
| **Resolution** | **CONTAINED — documented in DOMAIN_MODEL.md.** Verify territory-management.md uses the runtime values. If it still has old values, update it to match. |
| **Action** | Verify `backend/docs/domain/territory-management.md` criteria_type values; update if stale. DOMAIN_MODEL.md is already correct. |

---

## Resolved Conflicts (For Reference)

These were previously open conflicts that have been resolved.

| ID | Description | Resolution | Evidence |
|---|---|---|---|
| C-001 (U3) | COMMERCIALISATION-PLAN.md RESUME POINT table showed C5/C6 as pending despite header saying C6 complete | RESOLVED — RESUME POINT table updated with check marks by U10 remediation | COMMERCIALISATION-PLAN.md — table now shows ✓ COMPLETE for C0–C5 |
| C-002 (U3) | SYSTEM-SNAPSHOT.md showed C3 as current; COMMERCIALISATION-PLAN.md showed C6 | PARTIALLY RESOLVED — COMMERCIALISATION-PLAN.md is correct; SYSTEM-SNAPSHOT.md still stale (CF-001 above) | AI_OPERATING_CONTEXT.md CURRENT_PHASE section |
| C-003 (U3) | Frontend API wiring: doc claimed DUMMY_MODE: false everywhere; code had DUMMY_MODE: true on most pages | RESOLVED — AI_OPERATING_CONTEXT.md correctly states 5 pages wired, 70 use dummy fallback | AI_OPERATING_CONTEXT.md DUMMY_MODE STATUS section |
| H-001 (Gov Phase 1) | Gateway count: "42 vs 43 vs 44" in multiple documents | RESOLVED — API_INVENTORY.md footer updated to 44; all governance docs say 44 | REMEDIATION_REPORT.md H-001 |
| H-003 (Gov Phase 1) | PRODUCT_WORKFLOWS.md §WF-B: "POST /invoices" does not exist as standalone route | RESOLVED — updated in PRODUCT_WORKFLOWS.md to reference POST /invoice-summaries | REMEDIATION_REPORT.md H-003 |
| M-001 to M-010 (Gov Phase 1) | 10 medium consistency issues in governance documents | ALL RESOLVED — see REMEDIATION_REPORT.md | REMEDIATION_REPORT.md |

---

## Accepted Conflicts (Not to Fix)

These are apparent conflicts that are intentional or where both claims are correct in different contexts.

| ID | Description | Why Accepted |
|---|---|---|
| ACF-001 | Module count: FEATURE_SCOPE.md says "22 user-facing modules"; TEST_SUITE_PLAN.md says "29 modules" | Different counting scope: 22 = user-facing product modules; 29 = all Python src/ modules including infrastructure. Both are correct for their scope. FEATURE_SCOPE.md §Overview explains this. |
| ACF-002 | README.md and backend/README.md both describe Pakistan CRM purpose | Intentional — different audiences (project vs backend developer). Both should exist. DUP-007 covers this. |
| ACF-003 | DOMAIN_MODEL.md says "37+ entities"; ENTITY_INVENTORY.md lists 30 "confirmed" entities | Different confidence levels: 37+ includes inferred entities; 30 are directly confirmed from schema.sql. DOMAIN_MODEL.md §Overview explains this. |
| ACF-004 | L-001 (Gov Phase 1): FULLSTACK_STITCHING_CONTRACT.md §8 auth section marked TBD | Intentional TBD — password hashing algorithm not verified during U0–U10. Left as TBD until code verification pass. Not a conflict. |

---

## Conflict Count Summary

| Category | Count |
|---|---|
| Active (open) conflicts | 4 (CF-001 through CF-004) |
| Resolved conflicts | 17 (U3: 7, Gov Phase 1: 10) |
| Accepted (intentional) | 4 (ACF-001 through ACF-004) |
| Critical active conflicts | 0 |
| High active conflicts | 1 (CF-001 — SYSTEM-SNAPSHOT.md phase status) |
| Medium active conflicts | 2 (CF-002, CF-003) |
| Low active conflicts | 1 (CF-004 — territory criteria type) |

---

## Verification Notes

This report is based on content read during this session. Documents read and verified:
- docs/00_authority/PROJECT_CHARTER.md (full)
- docs/00_authority/DOMAIN_MODEL.md (full)
- docs/00_authority/FEATURE_SCOPE.md (full)
- docs/07_governance/AI_OPERATING_CONTEXT.md (full)
- docs/07_governance/DECISION_ESCALATION_MATRIX.md (full)
- docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md (full)
- docs/08_reports/GOVERNANCE_CONSISTENCY_AUDIT.md (partial — exec summary + findings)
- docs/08_reports/REMEDIATION_REPORT.md (partial — findings resolution)
- docs/reports/u-series/AUTHORITY_RECONSTRUCTION_REPORT.md (partial)
- docs/reports/u-series/DOC_CONFLICT_REGISTER.md (partial)
- docs/reports/u-series/CURRENT_PROJECT_STATUS.md (partial)
- docs/reports/session/SYSTEM-SNAPSHOT.md (partial)
- COMMERCIALISATION-PLAN.md (partial)
- backend/docs/architecture/architecture-overview.md (partial)

Documents not fully read (too large or not opened): FRAMEWORK.md (3401 lines; header only read), DESIGN-SPEC.md, PRODUCT-SPEC.md, backend/docs/domain/territory-management.md. CF-004 should be verified by reading territory-management.md fully.

---

*End CONFLICT_ANALYSIS_REPORT.md*
