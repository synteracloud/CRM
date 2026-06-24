> **RETIRED** — Merge plan is complete (all 7 steps done 2026-05-22). See [DOC_CATALOGUE.md](../reports/u-series/DOC_CATALOGUE.md) for the merged master catalogue.
> Content preserved for historical reference. Do not update this document.
> Retired: 2026-06-21 (Documentation Normalization Phase)

# Catalogue Merge Plan

**Purpose:** Step-by-step protocol for merging DOC-CATALOGUE-OPS.md and DOC-CATALOGUE-TECH.md into DOC-CATALOGUE.md (the master), then removing the sub-catalogues.  
**Created:** 2026-05-22  
**Status:** COMPLETE — All 7 steps done 2026-05-22  
**Rule:** Do NOT delete any sub-catalogue until Step 5 (verification) passes completely.

---

## Files in scope

| File | Role | Action |
|---|---|---|
| `D:\CRM\DOC-CATALOGUE.md` | Master — merge target | Keep; receives all content |
| `D:\CRM\DOC-CATALOGUE-OPS.md` | Ops subset (§A + §B) | Read → merge → delete ONLY after Step 5 |
| `D:\CRM\backend\docs\DOC-CATALOGUE-TECH.md` | Tech subset (§B2–§H) | Read → merge → delete ONLY after Step 5 |

---

## Steps

### Step 1 — Inventory all three files
- [x] Read DOC-CATALOGUE.md fully
- [x] Read DOC-CATALOGUE-OPS.md fully
- [x] Read DOC-CATALOGUE-TECH.md fully
- [x] Build section-by-section entry count table (master vs OPS vs TECH)
- [x] Flag any count mismatch as a gap before touching anything
- **Output:** Inventory table appended to §Appendix A of this file ✓

### Step 2 — Identify the delta
- [x] For each section present in both a sub-catalogue and the master: compare descriptions side-by-side
- [x] Flag any entry where the sub-catalogue has more detail or different wording than the master
- [x] Flag any entry unique to a sub-catalogue (not in master at all)
- **Output:** Delta list appended to §Appendix B of this file ✓

### Step 3 — Merge section by section (checklist)
Work through each section one at a time. Tick each off only after verifying the merged result.

- [x] §A — removed DOC-CATALOGUE-OPS.md self-ref; header 14→15 active; FRAMEWORK.md G-01–G-10; REBUILD-PLAN.md "Sprint-level detail"
- [x] §B — BACKEND-QC.md purpose added; market-research wording improved; product-spec "resolved" + "9 docs" + better purpose; FRONTEND-BACKEND-MAPPING.md Phase 3 note
- [x] §B2 — fixed "(11 files)"→"(6 modules)"; added send-invoice + conversation-detail
- [x] §C — identical, no changes needed
- [x] §D — identical, no changes needed
- [x] §E — identical, no changes needed
- [x] §F0 — entire section removed from master
- [x] §F — identical, no changes needed
- [x] §G — identical, no changes needed
- [x] §H — identical, no changes needed
- [x] Update master header — updated to 2026-05-22 with merge note
- [x] "How to use" rebuilt: 12 rows → 28 rows (all three catalogues merged, deduplicated)
- [x] §I added — Non-Negotiables + Permanently Blocked Items (carried from OPS)

### Step 4 — Post-merge grep verification
Run the following grep checks against both sub-catalogues to confirm every entry is present in the merged master:

- [x] Grep DOC-CATALOGUE-OPS.md for 10 unique key strings → all 10 found in master ✓
- [x] Grep DOC-CATALOGUE-TECH.md for 10 unique key strings → all 10 found in master ✓
- [x] Grep master for strings that should NOT appear → all 5 stale strings absent ✓
- **Output:** Grep results appended to §Appendix C of this file ✓

### Step 5 — Count verification
- [x] Count total entries in merged master
- [x] Count unique entries across all three originals
- [x] Confirm: merged master count ≥ unique entry count across originals ✓
- **Output:** Count table appended to §Appendix C of this file ✓

### Step 6 — Delete sub-catalogues and update cross-references ✓ COMPLETE 2026-05-22
**Only execute after Step 5 passes.**

Files to update before deleting:
- [x] `D:\CRM\README.md` — verified clean, no references to sub-catalogues
- [x] `D:\CRM\backend\README.md` — verified clean, no references to sub-catalogues
- [x] `D:\CRM\DOC-CATALOGUE.md` — §F0 removed (Step 3); §A OPS entry removed (Step 3); §I note updated to "originally from DOC-CATALOGUE-OPS.md (merged and deleted 2026-05-22)"
- [x] `D:\CRM\DOC-READ-LOG.md` — removed OPS + TECH entries; added deployment-pipelines.md ✓, DOC-READ-LOG.md W, CATALOGUE-MERGE-PLAN.md W; summary updated to 101 ✓ / 2 W / 103 total
- [x] `C:\Users\Admin\.claude\projects\D--CRM\memory\MEMORY.md` — verified clean, no sub-catalogue references

Files to delete:
- [x] `D:\CRM\DOC-CATALOGUE-OPS.md` — deleted 2026-05-22
- [x] `D:\CRM\backend\docs\DOC-CATALOGUE-TECH.md` — deleted 2026-05-22

### Step 7 — Final audit ✓ COMPLETE 2026-05-22
- [x] Read merged DOC-CATALOGUE.md fully one pass — no garbled sections; 3 residual issues found and fixed (Scope line count, CATALOGUE-MERGE-PLAN.md status, DOC-READ-LOG.md description)
- [x] DOC-READ-LOG.md already updated in Step 6 (OPS + TECH entries removed; 3 new entries added; summary 103 total)
- [x] DOC-CATALOGUE.md Last updated header updated to "COMPLETE"
- [x] CATALOGUE-MERGE-PLAN.md status updated to COMPLETE
- [x] This file status updated to COMPLETE

---

## Appendix A — Inventory Table
*(populated during Step 1 — 2026-05-22)*

### Section-by-section entry counts

| Section | Master (DOC-CATALOGUE.md) | OPS | TECH | Match? |
|---|---|---|---|---|
| §A root | 15 active + 1 archived = **16** (incl. CATALOGUE-MERGE-PLAN.md added today) | 14 active + 1 archived = **15** (OPS header says 13+1 — header off by 1; CATALOGUE-MERGE-PLAN.md not yet in OPS) | — | ⚠ OPS missing 1 new entry; OPS header count wrong |
| §B backend root | 7 active + 1 archived = **8** | 7 active + 1 archived = **8** | — | ✓ |
| §B2 Phase 3 API | **6** | — | **6** | ✓ |
| §C database | **5** | — | **5** | ✓ |
| §D gateway | **2** | — | **2** | ✓ |
| §E page specs | **15** | — | **15** | ✓ |
| §F0 catalogue index | **1** (DOC-CATALOGUE-TECH.md self-ref) | — | — | — (removed after merge) |
| §F domain/arch | **46** (8 core arch + 3 identity + 4 Pakistan + 13 domain + 13 infra + 2 UI + 3 QC) | — | **46** | ✓ |
| §G ADRs | **3** | — | **3** | ✓ |
| §H Sprint 0 | **9** | — | **9** | ✓ |
| **Total file entries** | **111** | **23** | **95** | all subsets of master |

### Unique content blocks in sub-catalogues (NOT in master)

| Block | In OPS? | In TECH? | Action |
|---|---|---|---|
| "Permanently Blocked Items" cross-reference table (P-016/P-017/MR-001/003/007) | ✓ YES | — | **Must carry into master** |
| "Non-Negotiables Quick Reference" table (9 rules with Source + Consequence) | ✓ YES | — | **Must carry into master** |
| "How to use" navigation table | ✓ YES (ops-focused rows) | ✓ YES (tech-focused rows) | Merge both into master §Quick Navigation |
| §F0 self-reference entry for DOC-CATALOGUE-TECH.md | — | — | Remove from master after merge |

### Description wording differences (OPS vs Master) — Step 2 detail

| File | OPS wording | Master wording | Use |
|---|---|---|---|
| FRAMEWORK.md | "seed-to-page table (88 entries)" | "(§17 — 96 entries)" | Master (more recent) |
| FRAMEWORK.md | "15 past mistakes" | "14 past mistakes" | **Flag for Step 2** |
| DESIGN-SPEC.md | Shorter description | Longer with §2–§7 detail | Master (more complete) |
| PRODUCT-SPEC.md | Shorter description | Longer with §1–§3 detail | Master (more complete) |
| CONTRIBUTING.md | Shorter description | Longer with full rule list | Master (more complete) |
| PROGRESS.md | "96/96 library pages complete" | "97 built pages (96 unique — slot #3 unused)" | Master (more accurate) |
| REBUILD-PLAN.md | Adds "Sprint-level detail" phrase | Does not have this phrase | Master (add phrase) |
| BACKEND-QC.md | Adds "required reading before Phase 4 work" | Does not have this phrase | Master (add phrase) |
| FRONTEND-BACKEND-MAPPING.md | Has note: "**Note: dated 2026-05-05 — Phase 3 API additions (2026-05-18) not yet reflected; update in Phase 4 Sprint 3.**" | No note | **Must carry into master** |
| market-research-gap-register.md | "MR-004 (daily WhatsApp summary) and MR-005 (Excel import/export) buildable now" | "MR-004 and MR-005 buildable" | OPS (more specific) |
| product-spec-gap-register.md | "All PS items resolved as Sprint-0 tasks" | "All PS items tracked as Sprint-0 tasks" | OPS (more accurate — all are resolved) |

### Step 1 verdict

- **No file entries exist in sub-catalogues that are missing from master.** All sub-catalogue entries are subsets of master entries.
- **4 content items unique to OPS must be carried into master:** Permanently Blocked Items table, Non-Negotiables Quick Reference table, FRONTEND-BACKEND-MAPPING.md note, and the more specific market-research + product-spec descriptions.
- **Master §A header count** needs updating: should now read "15 active + 1 archived" (was 14+1; CATALOGUE-MERGE-PLAN.md added today).
- **OPS header count** is wrong independently: says "13 active + 1 archived" but has 14 active entries.
- **§F0 entry** (DOC-CATALOGUE-TECH.md self-ref) will be removed from master after merge.

---

## Appendix B — Delta List
*(populated during Step 2 — 2026-05-22)*

**Legend:** ✓ = identical, keep master | ← OPS = OPS wording is better, update master | ← TECH = TECH wording is better, update master | MERGE = take specific phrase from sub-catalogue into master | CARRY = unique content block, must be added to master | DROP = remove from master after merge

---

### §A — OPS vs Master

| File | Status | Delta detail | Action |
|---|---|---|---|
| `CLAUDE.md` | ✓ Identical | — | Keep master |
| `FRAMEWORK.md` | ⚠ Different | OPS: "seed-to-page table (88 entries)" vs master "(§17 — 96 entries)"; OPS: "15 past mistakes" vs master "14 past mistakes"; OPS Purpose adds "G-01–G-10" after page-lock gate reference | Keep master description (96 entries correct, 14 mistakes correct per actual file); MERGE OPS Purpose addition "G-01–G-10" into master |
| `DESIGN-SPEC.md` | ⚠ Different | OPS description is shorter (missing §2–§7 breakdown) | Keep master (more complete) |
| `PRODUCT-SPEC.md` | ⚠ Different | OPS: "consolidated from 5 source files"; master: "3 source files". OPS description shorter (missing §1/§2/§3 breakdown). Verified in Batch 1 read: actual file has 3 source files. | Keep master (OPS count wrong; master description more complete) |
| `SCREEN-ARTEFACTS.md` | ✓ Identical | — | Keep master |
| `DOC-CATALOGUE.md` | ⚠ Different | OPS: "99 active + 3 archived" (stale — count was correct at OPS creation date, now higher) | Keep master (no count in master description — avoids stale count problem) |
| `DOC-CATALOGUE-OPS.md` | — | This entry is a self-reference to a file being deleted | DROP from master §A after merge |
| `CATALOGUE-MERGE-PLAN.md` | — | Not in OPS (added today) | Already in master only — keep |
| `SYSTEM-SNAPSHOT.md` | ✓ Near-identical | OPS Purpose: "update at the start of each phase" vs master "should be updated at the start of each phase" | Keep master (identical meaning) |
| `PROGRESS.md` | ⚠ Different | OPS: shorter, says "96/96 library pages complete" — stale; master: "97 built pages (96 unique — slot #3 unused)" + full history detail | Keep master (more accurate and detailed) |
| `REBUILD-PLAN.md` | ⚠ Different | OPS Description adds "with Sprint-level detail" after "Phase 4/5/6 scope definitions" | MERGE: add "with Sprint-level detail" into master description |
| `PENDING.md` (root) | ✓ Identical | — | Keep master |
| `README.md` | ✓ Identical | — | Keep master |
| `CHANGELOG.md` | ✓ Identical | — | Keep master |
| `CONTRIBUTING.md` | ⚠ Different | OPS description is shorter; missing "7 types" count, missing full rule list detail | Keep master (more complete) |
| `FRAMEWORK-GAPS.md` | ✓ Identical | — | Keep master |

---

### §B — OPS vs Master

| File | Status | Delta detail | Action |
|---|---|---|---|
| `README.md` | ✓ Identical | — | Keep master |
| `BACKEND-QC.md` | ⚠ Different | OPS Purpose adds: "required reading before Phase 4 work to understand what was already validated" — master omits this | MERGE: add this phrase to master Purpose |
| `CONSTRAINTS.md` | ✓ Identical | — | Keep master |
| `PENDING.md` (backend) | ✓ Identical | — | Keep master |
| `gap-register.md` | ✓ Identical | — | Keep master |
| `market-research-gap-register.md` | ⚠ Different | OPS: "MR-004 (daily WhatsApp summary) and MR-005 (Excel import/export) buildable now; rest blocked. All Phase 6 scope." Master: "MR-004 and MR-005 buildable; rest blocked. Phase 6 scope." | ← OPS: more specific, use OPS wording |
| `product-spec-gap-register.md` | ⚠ Different | OPS Description: "All PS items **resolved** as Sprint-0 tasks" + "All 9 new docs written 2026-05-19"; master says "tracked" and omits doc-writing confirmation. OPS Purpose: "Historical record... all PS gaps now resolved; retained as audit trail... documents rationale behind Sprint 0 doc choices." vs master Purpose shorter/different | ← OPS: both description and purpose are more accurate and complete |
| `FRONTEND-BACKEND-MAPPING.md` | ⚠ Different | OPS has bold note not in master: **"Note: dated 2026-05-05 — Phase 3 API additions (2026-05-18) not yet reflected; update in Phase 4 Sprint 3."** | CARRY: add note to master description |

---

### §B2 — TECH vs Master (section header only — all 6 row entries identical)

| Element | Master | TECH | Action |
|---|---|---|---|
| Section title | "§B2 — Phase 3 Public API layer + Audit Fixes **(11 files)**" | "§B2 — backend/ — Phase 3 Public API Layer **(6 modules)**" | ← TECH: "(11 files)" is wrong — only 6 entries exist; fix to "(6 modules)" |
| Section description | "New service public-facing HTTP modules..." audit additions: "new endpoints, RBAC gates, tenant isolation, overdue scanner" | "Service public-facing HTTP modules and background workers..." additions: "RBAC gates, tenant isolation, overdue scanner, **send-invoice endpoint, conversation detail**" | MERGE: add "send-invoice endpoint, conversation detail" into master section description |
| 6 table rows | — | — | ✓ All 6 rows identical |

---

### §C through §H — TECH vs Master (all table rows)

All §C (5), §D (2), §E (15), §F (46), §G (3), §H (9) entries: **✓ Identical** — corrections were applied to both catalogues simultaneously throughout the audit; no divergence found.

---

### Unique content blocks to CARRY from OPS into master

| Block | Location in OPS | Content | Action |
|---|---|---|---|
| "Permanently Blocked Items" table | After §B table | 5 rows: P-016/P-017/MR-001/MR-003/MR-007 with Blocked-by and Blocked-in columns | CARRY into master as new §I section |
| "Non-Negotiables Quick Reference" table | After Blocked Items | 9 rows: Rule / Source / Consequence columns | CARRY into master as new §I section |

---

### Navigation to merge

| Element | Master "How to use" | OPS "How to use" | TECH "How to use" |
|---|---|---|---|
| Rows | 12 rows (mixed ops + tech) | 17 rows (ops-focused) | 15 rows (tech-focused) |
| Action | Replace with a merged set covering all use-cases from all three, deduplicated |

---

### Items to REMOVE from master after merge

| Item | Reason |
|---|---|
| §F0 section + DOC-CATALOGUE-TECH.md entry | TECH catalogue being deleted |
| `DOC-CATALOGUE-OPS.md` entry in §A | OPS catalogue being deleted |
| `DOC-CATALOGUE-TECH.md` entry in §A (if present) | Same reason |

---

### Step 2 summary — changes needed to master

| # | Type | Target | Change |
|---|---|---|---|
| 1 | MERGE | FRAMEWORK.md Purpose | Add "G-01–G-10" after "page-lock gate" |
| 2 | MERGE | REBUILD-PLAN.md Description | Add "with Sprint-level detail" after "Phase 4/5/6 scope definitions" |
| 3 | MERGE | BACKEND-QC.md Purpose | Add "required reading before Phase 4 work to understand what was already validated" |
| 4 | UPDATE | market-research-gap-register.md Description | Use OPS wording (MR-004/MR-005 named explicitly) |
| 5 | UPDATE | product-spec-gap-register.md Description + Purpose | Use OPS version ("resolved" + "All 9 new docs written 2026-05-19" + fuller purpose) |
| 6 | CARRY | FRONTEND-BACKEND-MAPPING.md Description | Add OPS bold note about Phase 3 gap |
| 7 | FIX | §B2 section header | "(11 files)" → "(6 modules)"; add "send-invoice endpoint, conversation detail" to description |
| 8 | CARRY | New §I section | Add "Permanently Blocked Items" table from OPS |
| 9 | CARRY | New §I section | Add "Non-Negotiables Quick Reference" table from OPS |
| 10 | MERGE | "How to use" table | Rebuild with all rows from all three catalogues, deduplicated |
| 11 | FIX | §A section header | "14 active" → "15 active" (CATALOGUE-MERGE-PLAN.md added today) |
| 12 | DROP | §F0 section | Remove after merge |
| 13 | DROP | DOC-CATALOGUE-OPS.md entry in §A | Remove after merge |

---

## Appendix C — Verification Results
*(populated during Steps 4 and 5 — 2026-05-22)*

### Step 4 — Grep results

#### OPS positive checks (10/10 PASS)

| # | Search string | Found on line | Result |
|---|---|---|---|
| 1 | "Permanently Blocked Items" | 3, 42, 273, 277 | ✓ PASS |
| 2 | "JAZZCASH_STUB_MODE" (backtick-wrapped in §I) | 66, 295 | ✓ PASS |
| 3 | "Non-Negotiables Quick Reference" | 289 | ✓ PASS |
| 4 | "MR-004 (daily WhatsApp summary)" | 82 | ✓ PASS |
| 5 | "All 9 new docs written 2026-05-19" | 83 | ✓ PASS |
| 6 | "Phase 3 API additions (2026-05-18) not yet reflected" | 84 | ✓ PASS |
| 7 | "required reading before Phase 4 work to understand what was already validated" | 78 | ✓ PASS |
| 8 | "with Sprint-level detail" | 62 | ✓ PASS |
| 9 | "G-01–G-10" | 53 | ✓ PASS |
| 10 | "all PS gaps now resolved" | 83 | ✓ PASS |

#### TECH positive checks (10/10 PASS)

| # | Search string | Found on line | Result |
|---|---|---|---|
| 1 | "send-invoice endpoint, conversation detail" | 90 | ✓ PASS |
| 2 | "identity-auth-rbac.md + security-model.md" | 37 | ✓ PASS |
| 3 | "execution-hardening.md + concurrency-control.md" | 39 | ✓ PASS |
| 4 | "§F Pakistan-specific → pakistan-adapter-architecture.md" | 38 | ✓ PASS |
| 5 | "§F Core architecture → service-map.md" | 34 | ✓ PASS |
| 6 | "§F Core architecture → api-standards.md" | 35 | ✓ PASS |
| 7 | "§C database docs" | 31 | ✓ PASS |
| 8 | "6 modules" (§B2 header fix) | 88 | ✓ PASS |
| 9 | "§H — cases, shared-inbox" | 41 | ✓ PASS |
| 10 | "§F Core architecture → event-catalog.md" | 36 | ✓ PASS |

---

### Step 5 — Count verification

**Grep pattern used:** `^\| \`` (rows where column 1 starts with a backtick — file entry rows)

**Note:** Pattern also catches 2 non-file rows in the Non-Negotiables table where column 1 contains backtick-wrapped values (`` `JAZZCASH_STUB_MODE=true` `` and `` `core/*` ``). These appear in both master and OPS, not in TECH. Adjusted counts subtract these 2 rows.

| File | Raw grep count | Non-file backtick rows | Actual file entries |
|---|---|---|---|
| DOC-CATALOGUE.md (merged master) | 111 | −2 | **109** |
| DOC-CATALOGUE-OPS.md | 25 | −2 | **23** |
| DOC-CATALOGUE-TECH.md | 86 | 0 | **86** |

**Section-by-section breakdown of merged master (109 file entries):**

| Section | File entries | Covers |
|---|---|---|
| §A | 15 | 14 active + 1 archived |
| §B | 8 | 7 active + 1 archived |
| §B2 | 6 | 6 service modules |
| §C | 5 | db schema docs |
| §D | 2 | gateway docs |
| §E | 15 | b9-p page specs |
| §F | 46 | domain + arch specs |
| §G | 3 | ADRs |
| §H | 9 | Sprint 0 design docs |
| **Total** | **109** | |

**Unique entry coverage check:**

| Sub-catalogue | Entries | Covered by master sections | Result |
|---|---|---|---|
| OPS (23 file entries) | §A(15) + §B(8) | Master §A(15) + §B(8) = 23 | ✓ All present |
| TECH (86 file entries) | §B2+§C+§D+§E+§F+§G+§H = 86 | Master §B2+§C+§D+§E+§F+§G+§H = 86 | ✓ All present |

**Intentional removals (2 entries):** DOC-CATALOGUE-OPS.md from §A (self-ref to file being deleted); DOC-CATALOGUE-TECH.md from §F0 (self-ref to file being deleted). Both correct by design — these are the files being merged away.

**Step 5 verdict: PASS** — merged master (109) accounts for all unique entries across all originals. No file entries dropped.

#### Stale string checks (5/5 PASS — none present as live content)

| # | Search string | Result | Notes |
|---|---|---|---|
| 1 | "§F0" | Line 3 only | ✓ PASS — header note only ("removed §F0"), not a live section |
| 2 | "(11 files)" | Not found | ✓ PASS |
| 3 | "Find planned but not-yet-written docs" | Not found | ✓ PASS |
| 4 | "6 planned docs remaining" | Not found | ✓ PASS |
| 5 | "Operational subset of the master catalogue.*Lives at D" | Not found | ✓ PASS — OPS table row fully removed |
