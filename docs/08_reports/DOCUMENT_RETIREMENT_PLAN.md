Status: Active
Authority Level: Medium
Generated: 2026-06-22
Owner: AI (Claude Sonnet 4.6 — Documentation Normalization session)

---

# DOCUMENT RETIREMENT PLAN — Pakistan CRM OS

## Purpose

For every document recommended for retirement, replacement, or archiving, this plan specifies: what action is required, what risk exists if not done, and who must act.

**Constraint:** Do not delete any files. Do not modify application code. Add retirement notices only as planned here — this plan is read-only; execution is a separate step.

**Disposition codes:**
- **Retire** — Add SUPERSEDED/RETIRED banner; keep file in place
- **Archive** — Move to docs/archive/ and add retirement notice
- **Redirect** — Update header to point to the authoritative replacement
- **Update** — Refresh stale content in place
- **Human Decision** — Requires explicit human approval before any action

---

## Protected Documents (Must NOT Be Retired)

These documents must be preserved in their current form and location. Do not add retirement notices. Do not archive.

| Document | Why Protected |
|---|---|
| docs/00_authority/PROJECT_CHARTER.md | Primary authority for project purpose; Critical authority level |
| docs/00_authority/FEATURE_SCOPE.md | Primary authority for product scope; Critical authority level |
| docs/00_authority/DOMAIN_MODEL.md | Primary authority for domain model; Critical authority level |
| docs/00_authority/PRODUCT_WORKFLOWS.md | Primary authority for workflows; Critical authority level |
| docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md | Primary authority for fullstack traceability; Critical authority level |
| docs/06_decisions/ADR-001_PROJECT_FOUNDATION.md | Primary architectural decision record; High authority level |
| docs/07_governance/AI_OPERATING_CONTEXT.md | Primary AI session context; Critical authority level |
| docs/07_governance/DECISION_ESCALATION_MATRIX.md | Governance authority; High authority level |
| CLAUDE.md | Session enforcement; Critical authority level; auto-loaded every session |
| FRAMEWORK.md | Frontend build authority; Critical authority level |
| DESIGN-SPEC.md | Page scope authority; Critical authority level |
| COMMERCIALISATION-PLAN.md | Operational authority; Critical authority level |
| PAGE-BUILD-PROTOCOL.md | Build protocol authority; High authority level |
| backend/CONSTRAINTS.md | Build constraints; Critical authority level |
| backend/docs/security/identity-auth-rbac.md | RBAC design authority; Critical authority level |
| backend/docs/security/org-multi-tenancy.md | Tenancy authority; Critical authority level |
| backend/docs/infrastructure/api-standards.md | API design authority; High authority level |
| All backend/docs/_b9/b9-p*.md files (14 files) | Frontend archetype specs; active build authority |

---

## Retirement Plan Table

### Tier 1 — Retire (Add Retirement Notice — AI Autonomous, No Human Approval Needed)

These are clearly superseded. Action: add SUPERSEDED banner at top of file with pointer to replacement. Do not delete. Do not move.

| Document | Current Path | Disposition | Reason | Action Required | Risk |
|---|---|---|---|---|---|
| DOCUMENT_CLASSIFICATION_MATRIX.md (U2) | docs/reports/u-series/DOCUMENT_CLASSIFICATION_MATRIX.md | Retire | Superseded by docs/08_reports/DOCUMENT_CLASSIFICATION_MATRIX.md (this session — covers 195 docs vs 130; adds 9 classes vs 6) | Add banner: "SUPERSEDED — see docs/08_reports/DOCUMENT_CLASSIFICATION_MATRIX.md (2026-06-22)" | Low — U2 version is a generated snapshot; content preserved in new version |
| DOC_CONFLICT_REGISTER.md (U3) | docs/reports/u-series/DOC_CONFLICT_REGISTER.md | Retire | Superseded by docs/08_reports/CONFLICT_ANALYSIS_REPORT.md (this session); U3 conflicts are mostly resolved | Add banner: "HISTORICAL — covers pre-governance conflicts as of 2026-06-20 (U3). See docs/08_reports/CONFLICT_ANALYSIS_REPORT.md for current conflict state." | Low — conflicts documented here are mostly resolved |
| DOC_DUPLICATION_REGISTER.md (U3) | docs/reports/u-series/DOC_DUPLICATION_REGISTER.md | Retire | Superseded by docs/08_reports/DUPLICATION_ANALYSIS_REPORT.md (this session) | Add banner: "HISTORICAL — covers pre-governance duplications as of 2026-06-20 (U3). See docs/08_reports/DUPLICATION_ANALYSIS_REPORT.md for current duplication state." | Low — duplications documented here are re-covered in new report |
| DOC_NORMALIZATION_REPORT.md (U3) | docs/reports/u-series/DOC_NORMALIZATION_REPORT.md | Retire | Superseded by docs/08_reports/DOCUMENT_NORMALIZATION_REPORT.md (this session) | Add banner: "HISTORICAL — U3 normalization report as of 2026-06-20. See docs/08_reports/DOCUMENT_NORMALIZATION_REPORT.md for current normalization state." | Low — pre-governance state; not used for current decisions |

---

### Tier 2 — Redirect (Update Content to Point to Authority — AI Autonomous)

These documents are stale but retained for their content. Action: add redirect banner and update key stale claims.

| Document | Current Path | Disposition | Reason | Action Required | Risk |
|---|---|---|---|---|---|
| SYSTEM-SNAPSHOT.md | docs/reports/session/SYSTEM-SNAPSHOT.md | Redirect + Update | Body says "C3 ← CURRENT" (C2-era). AI agents instructed to read this first at session start will orient incorrectly. | (Option A) Add banner: "STALE (2026-06-01) — see docs/07_governance/AI_OPERATING_CONTEXT.md for current phase and session orientation." OR (Option B) Replace body with C6-accurate content. | **High** — this is a session orientation document; stale content can cause agents to work on wrong phase. Option A is faster; Option B is more complete. |
| SESSION-HANDOFF.md | docs/reports/session/SESSION-HANDOFF.md | Redirect | References SYSTEM-SNAPSHOT.md as session opener; AI_OPERATING_CONTEXT.md has superseded this role. | Update session startup sequence to: AI_OPERATING_CONTEXT.md → COMMERCIALISATION-PLAN.md → PENDING.md. Remove reference to SYSTEM-SNAPSHOT.md as primary orientation. | Medium — SESSION-HANDOFF.md is for mid-phase resumption; if stale, agent resumes from wrong context. |
| DOCUMENT_OWNERSHIP_MATRIX.md (U2) | docs/reports/u-series/DOCUMENT_OWNERSHIP_MATRIX.md | Redirect | Covers 130 pre-governance docs. DOCUMENT_INVENTORY.md (this session) covers all ~195 with more detail. | Add banner: "See also docs/08_reports/DOCUMENT_INVENTORY.md for owner classification across all 195 project documents (2026-06-22)." Keep file — ownership history is useful. | Low — informational only |

---

### Tier 3 — Archive (Move File to docs/archive/ — Requires Human Approval for file move)

These documents have no current utility but have historical value. They should be moved to docs/archive/ if not already there. Files in docs/archive/ already do not need to move.

**Note:** The files in docs/archive/ already exist there. The remaining candidates are root-level U-series prompt files.

| Document | Current Path | Disposition | Reason | Action Required | Risk |
|---|---|---|---|---|---|
| U0–U9 LEGACY MODERNIZATION AUDIT.md | U0–U9 LEGACY MODERNIZATION AUDIT.md (root) | Archive | Session prompt file; outputs are in docs/reports/u-series/. No utility at root. | Human decision: move to docs/archive/ or create docs/09_prompts/ | Low — prompt file; outputs preserved in u-series/ |
| U10 — U0–U9 AUDIT REMEDIATION.md | U10 — U0–U9 AUDIT REMEDIATION.md (root) | Archive | Session prompt file; outputs are in docs/reports/u-series/U10_*.md | Human decision: move to docs/archive/ | Low |
| U5 — WORKSPACE RESTRUCTURING EXECUTION.md | U5 — WORKSPACE RESTRUCTURING EXECUTION.md (root) | Archive | Session prompt file; execution complete | Human decision: move to docs/archive/ | Low |
| U6 — DOC TO CODE DELTA ANALYSIS.md | U6 — DOC TO CODE DELTA ANALYSIS.md (root) | Archive | Session prompt file; outputs in u-series/ | Human decision: move to docs/archive/ | Low |
| U7 — DELTA REMEDIATION.md | U7 — DELTA REMEDIATION.md (root) | Archive | Session prompt file; remediation complete | Human decision: move to docs/archive/ | Low |
| U8 — WORKSPACE SEALING.md | U8 — WORKSPACE SEALING.md (root) | Archive | Session prompt file; seal complete | Human decision: move to docs/archive/ | Low |
| U9 — TEST SUITE PLANNING.md | U9 — TEST SUITE PLANNING.md (root) | Archive | Session prompt file; outputs in u-series/ | Human decision: move to docs/archive/ | Low |
| GOVERNANCE IMPLEMENTATION PHASE 1.md | GOVERNANCE IMPLEMENTATION PHASE 1.md (root) | Archive | Phase 1 prompt; execution complete; outputs in docs/08_reports/ | Human decision: move to docs/archive/ | Low |
| PHASE 1 GOVERNANCE VALIDATION.md | PHASE 1 GOVERNANCE VALIDATION.md (root) | Archive | Validation prompt; validation complete | Human decision: move to docs/archive/ | Low |
| AUDIT REMEDIATION.md | AUDIT REMEDIATION.md (root) | Archive | Working prompt file for this and prior sessions | Human decision after this session is complete | Low |
| DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md | DOCUMENTATION NORMALIZATION AND AUTHORITY CONSOLIDATION.md (root) | Archive | This session's prompt file | Human decision after this session is complete | Low |

---

### Tier 4 — Already Retired (Files in docs/archive/ — No Action Needed)

These are already archived. Confirm retirement notice exists (may need adding if missing).

| Document | Current Path | Status | Replacement |
|---|---|---|---|
| DOC-CATALOGUE.md | docs/archive/DOC-CATALOGUE.md | Archived (U3 SUPERSEDED banner applied) | docs/reports/u-series/DOC_CATALOGUE.md |
| REBUILD-PLAN.md | docs/archive/REBUILD-PLAN.md | Archived (U3 SUPERSEDED banner applied) | COMMERCIALISATION-PLAN.md |
| deployment-pipelines.md | docs/archive/deployment-pipelines.md | Archived | docs/reference/RENDER-DEPLOY.md + backend/docs/infrastructure/runtime-deployment.md |
| gap-register.md | docs/archive/gap-register.md | Archived | docs/08_reports/ARCHITECTURAL_GAP_REGISTER.md |
| FRAMEWORK-GAPS.md | docs/archive/FRAMEWORK-GAPS.md | Archived | FRAMEWORK.md (gaps resolved) |
| CATALOGUE-MERGE-PLAN.md | docs/archive/CATALOGUE-MERGE-PLAN.md | Archived | docs/reports/u-series/DOC_CATALOGUE.md |
| MAPPING-TRACKER.md | docs/archive/MAPPING-TRACKER.md | Archived | docs/reports/u-series/DOCUMENT_OWNERSHIP_MATRIX.md |

**Action:** Verify each has an explicit retirement notice. If missing, add one (AI autonomous, Tier 1 action per DECISION_ESCALATION_MATRIX.md).

---

### Tier 5 — Human Decision Required

These require human judgment before any action can be taken.

| Document | Current Path | Decision Needed | Options | Risk |
|---|---|---|---|---|
| backend/docs/phase4-gap-register.md | backend/docs/phase4-gap-register.md | Is this still relevant? Phase 4 is complete. | (A) Move to docs/archive/ as historical. (B) Review gaps and close/merge into ARCHITECTURAL_GAP_REGISTER.md. | Low — if archived, any open Phase 4 gaps not captured in ARCHITECTURAL_GAP_REGISTER.md would be lost |
| backend/PENDING.md | backend/PENDING.md | Is this still tracking active work? | (A) Keep as operational artifact. (B) Merge outstanding items into docs/reports/session/PENDING.md. | Low — may contain backend-specific pending items not in main PENDING.md |
| PROMPT SEQUENCE.md | PROMPT SEQUENCE.md (root) | What does this document contain? Should it be archived? | (A) If it sequences future U-series runs, keep as reference. (B) If complete, archive. | Low |
| CONTRIBUTING.md | CONTRIBUTING.md (root) | Is this the project's developer contribution guide? If so, it should remain at root. | (A) Keep at root as developer reference. (B) Move to docs/ if project is internal only. | Low — standard GitHub convention to have CONTRIBUTING.md at root |

---

## Execution Sequence (Recommended Order)

When executing this retirement plan, follow this order to minimize confusion:

1. **Immediate (this session):** Add retirement notices to Tier 1 documents (4 files — AI autonomous)
2. **This session:** Add redirect banners to Tier 2 documents (3 files — AI autonomous)
3. **This session:** Verify docs/archive/ documents have retirement notices (7 files — AI autonomous)
4. **Next session:** Human decision on Tier 3 archive candidates (11 root prompt files)
5. **Next session:** Human decision on Tier 5 documents (4 files requiring judgment)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Agent reads SYSTEM-SNAPSHOT.md and orients to C3 | High (it's the designated first read per its own header) | High (wrong phase work) | Update SYSTEM-SNAPSHOT.md immediately per Tier 2 action |
| Retirement notice added to wrong file | Low | High | Review file path carefully before editing; this plan lists exact paths |
| Archive move breaks cross-references | Medium | Medium | Before any file move, search for all references to the file and update them |
| Prompt files at root confuse AI agents | Low | Low | Add archive note; low priority |

---

*End DOCUMENT_RETIREMENT_PLAN.md*
