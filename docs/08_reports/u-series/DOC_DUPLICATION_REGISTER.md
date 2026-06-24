> **HISTORICAL** — Covers pre-governance duplications as of 2026-06-20 (U3). See [DUPLICATION_ANALYSIS_REPORT.md](../../08_reports/DUPLICATION_ANALYSIS_REPORT.md) for current duplication state.
> Content preserved for historical reference. Do not update this document.
> Retired: 2026-06-21 (Documentation Normalization Phase — DUP-010 resolution)

# DOC_DUPLICATION_REGISTER.md — Pakistan CRM OS

**Generated:** 2026-06-20 (U3 — Documentation Normalization)
**Scope:** Duplicated or near-duplicated content across the 130 project-owned .md files.

---

## How to read this register

| Column | Meaning |
|---|---|
| ID | Duplication identifier |
| Doc A / Doc B | The two (or more) documents with overlapping content |
| Overlap Description | What content is duplicated or near-duplicated |
| Recommended Action | Merge / Delete one / Keep both / Extract to shared reference / Archive |

---

## §1 — Duplications (same or nearly same content)

### D-001 — Document catalogue: DOC-CATALOGUE.md vs DOC_CATALOGUE.md

| Field | Value |
|---|---|
| **Doc A** | `DOC-CATALOGUE.md` (root, 2026-05-31) |
| **Doc B** | `DOC_CATALOGUE.md` (root, 2026-06-20 U2 output) |
| **Overlap** | Both serve as the master document index for the project. DOC-CATALOGUE.md is the manually-maintained predecessor (109 entries, §A–§I structure). DOC_CATALOGUE.md is the U2-generated replacement (130 entries, §A–§P structure). Their §A–§I content overlaps substantially; DOC_CATALOGUE.md adds 21 entries from U0/U1/U2 outputs that DOC-CATALOGUE.md does not have. |
| **Status of fix** | U3 normalization applied SUPERSEDED banner to DOC-CATALOGUE.md pointing to DOC_CATALOGUE.md |
| **Recommended Action** | **Delete DOC-CATALOGUE.md** after confirming all cross-references to it have been updated to point to DOC_CATALOGUE.md (see DOC_STALE_REFERENCE_REPORT.md SR-01 through SR-05). DOC-CATALOGUE.md should not be kept indefinitely; it will diverge further with each session. If retained for historical audit, move to `_archive/`. |

---

### D-002 — README.md and backend/README.md: system identity narrative

| Field | Value |
|---|---|
| **Doc A** | `README.md` (root) |
| **Doc B** | `backend/README.md` |
| **Overlap** | Both describe what the Pakistan CRM is — its architecture, design principles, and market positioning. README.md describes the full 3-tier architecture (frontend/gateway/backend). backend/README.md describes the backend system identity (6 platform engines, L1/L2/L3 layer model, module map). Some identity narrative (Pakistan SME focus, WhatsApp-first, PKR) appears in both. |
| **Recommended Action** | **Keep both** — different audiences (GitHub landing page vs backend developer onboarding). Duplication is intentional and appropriate for the audience separation. No action needed. |

---

## §2 — Near-Duplications (same purpose, different scope or detail)

### D-003 — REBUILD-PLAN.md RESUME POINT vs COMMERCIALISATION-PLAN.md RESUME POINT

| Field | Value |
|---|---|
| **Doc A** | `REBUILD-PLAN.md` — contains a RESUME POINT table (now CLOSED) |
| **Doc B** | `COMMERCIALISATION-PLAN.md` — contains the active RESUME POINT table |
| **Overlap** | Both have "RESUME POINT — Read Before Every Session" sections with phase status tables. REBUILD-PLAN.md's RESUME POINT is historical; COMMERCIALISATION-PLAN.md's is the active one. The REBUILD-PLAN.md RESUME POINT now redirects to COMMERCIALISATION-PLAN.md. |
| **Recommended Action** | **Keep both** — REBUILD-PLAN.md is a closed historical record. The U3 SUPERSEDED banner has been added. The RESUME POINT in REBUILD-PLAN.md explicitly says "Active anchor: COMMERCIALISATION-PLAN.md". No further structural change needed. |

---

### D-004 — Permanently blocked items table (multiple docs)

| Field | Value |
|---|---|
| **Doc A** | `SYSTEM-SNAPSHOT.md` — Permanently Blocked Items table (P-016, P-017, MR-001, MR-003, MR-007) |
| **Doc B** | `COMMERCIALISATION-PLAN.md` — same Permanently Blocked Items table |
| **Overlap** | Both contain an identical 5-row table listing P-016, P-017, MR-001, MR-003, MR-007 with the same blocked-by reasons and runtime behaviours. Also partially duplicated in `DOC-CATALOGUE.md` §I (Non-Negotiables) and `backend/PENDING.md`. |
| **Recommended Action** | **Keep both** — this duplication is intentional. The table is a safety reminder that appears in every high-frequency session document. The risk of omitting it from one doc (developer forgets a blocker) outweighs the maintenance cost of keeping it in sync. |

---

### D-005 — Non-negotiable rules table (multiple docs)

| Field | Value |
|---|---|
| **Doc A** | `SYSTEM-SNAPSHOT.md` — Non-Negotiables table (RTL, DUMMY_MODE, JAZZCASH_STUB_MODE, etc.) |
| **Doc B** | `COMMERCIALISATION-PLAN.md` — same Non-Negotiable Rules table |
| **Overlap** | Both contain an identical or near-identical non-negotiable rules table with 8–9 rows covering RTL, API calls via crm-api.js, JAZZCASH_STUB_MODE, core/* isolation, library pages HTTP 200, doc cataloguing, push to GitHub. |
| **Recommended Action** | **Keep both** — same rationale as D-004. Intentional redundancy for safety. |

---

## §3 — Orphaned Documents (no active inbound references)

The following documents were identified as having no clear inbound references from any Authority or high-frequency Reference document. They are not duplicates, but their isolation means they may be stale, abandoned, or candidates for archiving.

### D-006 — backend/docs/domain/enterprise-depth.md

| Field | Value |
|---|---|
| **Document** | `backend/docs/domain/enterprise-depth.md` |
| **Class/Status** | Reference / Active (per DOC_CATALOGUE.md) |
| **Issue** | Not referenced from DESIGN-SPEC.md, PAGE-BUILD-PROTOCOL.md, FRAMEWORK.md, or any b9-p spec. DOC_CATALOGUE.md §K includes it. BACKEND-QC.md may reference it generically. |
| **Recommended Action** | Human review — confirm it is actively consulted for multi-tenant/multi-territory features. If so, add an explicit cross-reference from `backend/docs/architecture/architecture-overview.md` or `DESIGN-SPEC.md`. If not actively used, move to `_archive/`. |

---

### D-007 — backend/docs/domain/data-governance-ownership.md

| Field | Value |
|---|---|
| **Document** | `backend/docs/domain/data-governance-ownership.md` |
| **Class/Status** | Reference / Active (per DOC_CATALOGUE.md) |
| **Issue** | Exists alongside `backend/docs/domain/data-governance-layer.md` without a clear cross-reference between them. Their relationship (companion doc vs overlapping coverage vs different audience) is not documented. |
| **Recommended Action** | Human review — read both docs together and determine whether to: (a) merge data-governance-ownership.md into data-governance-layer.md; (b) add a companion-doc header to each pointing to the other; or (c) confirm they serve different audiences (governance policy vs ownership accountability) and add explicit cross-references. |

---

### D-008 — backend/docs/_b9/b9-p08-mobile-responsiveness-system.md

| Field | Value |
|---|---|
| **Document** | `backend/docs/_b9/b9-p08-mobile-responsiveness-system.md` |
| **Class/Status** | Reference / Active (per DOC_CATALOGUE.md) |
| **Issue** | The filename uses the b9-p08 prefix (Builder/Extensions archetype) but covers mobile responsiveness as a system-wide concern, not a single archetype page. It is not referenced from FRAMEWORK.md §31, the pre-build reading sequence in CLAUDE.md, or any individual b9-p archetype spec. |
| **Recommended Action** | Human review — add a cross-reference from FRAMEWORK.md (or CLAUDE.md pre-build reading sequence) if this doc is meant to be read before building mobile-facing pages. If it was written speculatively and is no longer consulted, move to `_archive/`. |

---

### D-009 — CATALOGUE-MERGE-PLAN.md

| Field | Value |
|---|---|
| **Document** | `CATALOGUE-MERGE-PLAN.md` (root) |
| **Class/Status** | Report / Complete (per DOC_CATALOGUE.md) |
| **Issue** | Status is COMPLETE (2026-05-22). All 7 steps done. The sub-catalogues it merged (DOC-CATALOGUE-OPS.md and DOC-CATALOGUE-TECH.md) were deleted. The document is no longer referenced from SYSTEM-SNAPSHOT.md, PENDING.md, or any active session doc. |
| **Recommended Action** | **Move to `_archive/`** — the merge work is complete and the plan is not needed for any current activity. It is a useful historical audit record. |

---

### D-010 — backend/product-spec-gap-register.md

| Field | Value |
|---|---|
| **Document** | `backend/product-spec-gap-register.md` |
| **Class/Status** | Report / Active (per DOC_CATALOGUE.md) |
| **Issue** | This file is a PRODUCT-SPEC.md overlay against 81 active docs, dated 2026-05-18. It is not referenced from SYSTEM-SNAPSHOT.md, PENDING.md, or COMMERCIALISATION-PLAN.md. Phase 4 gap register (`backend/docs/phase4-gap-register.md`) is explicitly Complete with 28 gaps fixed and 2 Open (A-006/A-007 — resolved in C3). It is unclear whether the product-spec-gap-register gaps are all resolved or still tracked elsewhere. |
| **Recommended Action** | Human review — check whether all gaps in this register were resolved during Phase 4. If yes, mark as Complete and move to `_archive/`. If some remain open, add them to `PENDING.md`. |
