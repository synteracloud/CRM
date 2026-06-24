Status: Active
Authority Level: Medium
Owner: AI
Last Reviewed: 2026-06-22

---

# REPOSITORY HYGIENE EXECUTION GUIDELINES — Pakistan CRM OS

## Purpose

This document is the practical execution guide for SAFE_REPOSITORY_HYGIENE tasks. It translates the policy defined in SAFE_REPOSITORY_HYGIENE_POLICY.md into step-by-step procedures for AI agents performing hygiene runs. It covers the full lifecycle: pre-run setup, execution mechanics, post-run reporting, and mid-run escalation triggers.

**Read before executing any hygiene task.** The policy document defines what qualifies; this document explains how to do it correctly.

---

## Before Starting Any Hygiene Run

Complete all of the following steps before touching a single file.

### Step 1 — Read the governance documents

| Document | What to check |
|----------|---------------|
| AI_OPERATING_CONTEXT.md | PROTECTED_AREAS and DO_NOT_MODIFY_AREAS tables — memorize which files cannot be touched |
| SAFE_REPOSITORY_HYGIENE_POLICY.md | Qualifying criteria (MN-1 through MN-12, M-1 through M-5) and Disqualifying Criteria table |
| APPROVAL_RECLASSIFICATION_REPORT.md | The ready-to-execute list — only work on items listed as "Yes — Tier 1, ready" or the current session's approved items |

### Step 2 — Confirm no feature work is bundled

A hygiene run must be a standalone session or a clearly demarcated segment. Before starting:
- Confirm the session has no other open tasks (no page builds, no backend changes, no test fixes)
- If the session started with feature work, complete and close that work first, then begin the hygiene run as a separate block
- The hygiene execution report will state "no feature work bundled" — this must be accurate

### Step 3 — Build the move plan before touching anything

For every file to be moved in this run:
1. List every source file path
2. List every target file path
3. Identify every .md file in the repository that contains a link or reference to the source path

Use Grep to search for references:
```
Grep pattern: "filename_without_extension" across all .md files
```

Do not begin any file move until the full reference map is built. Moving a file and then discovering a broken reference mid-run is an error.

### Step 4 — Confirm the target directories exist

For every target path, verify the destination directory exists before writing:
```bash
ls "D:/SaaS/CRM/docs/03_fullstack_contracts/"
ls "D:/SaaS/CRM/docs/04_testing/"
ls "D:/SaaS/CRM/docs/08_reports/"
ls "D:/SaaS/CRM/docs/archive/"
ls "D:/SaaS/CRM/backend/docs/"
```

If a target directory does not exist, create it before writing the file. Do not write to a non-existent path.

### Step 5 — Note the current .gitignore state

Read the current .gitignore before making any additions, so the execution report can accurately list what was added vs what was already present.

---

## During Execution

### File Move Mechanics

**Always use Read → Write → Remove-Item, not Move-Item.**

The reason: `Move-Item` leaves no audit trail of what was written to the new location. Using Read + Write creates an explicit record in the session transcript of the exact content written. Using Remove-Item creates an explicit record of the deletion.

Sequence for each file move:

```
1. Read the source file completely
2. Write to the target path (same content)
3. Verify the Write completed successfully
4. Run Grep to confirm the content is now at the target path
5. Remove-Item on the source path (or use git rm if the file is tracked)
6. Update ALL cross-references immediately (before moving the next file)
```

**Critical rule: Never move more than one file at a time without completing the cross-reference update.**

Moving multiple files simultaneously and then updating cross-references in a batch leads to missed references and broken links. Move one file, update all its references, confirm the references are correct, then move the next file.

### Cross-Reference Update Mechanics

After each file move, update cross-references in this order:

**Priority 1 — AI_OPERATING_CONTEXT.md (ACTIVE_AUTHORITY_DOCS table)**
If the moved file appears in the ACTIVE_AUTHORITY_DOCS table, update the path immediately.

**Priority 2 — DOCUMENT_INVENTORY.md (docs/08_reports/)**
Update the file path entry and any location notes.

**Priority 3 — DOC_CATALOGUE.md (docs/reports/u-series/)**
Update the file path and subfolder columns.

**Priority 4 — Any document that directly links to the moved file**
Use Grep output from Step 3 to find these. Update each one.

**Priority 5 — The APPROVAL_RECLASSIFICATION_REPORT.md status entry**
Mark the item as executed with the date.

### .gitignore Update Mechanics

When adding entries to .gitignore:

1. Read the current .gitignore fully first
2. Identify which entries are already present (do not duplicate)
3. Group new entries by category with comments:
   ```
   # Python bytecode
   __pycache__/
   *.pyc

   # pytest caches
   .pytest_cache/

   # Runtime logs
   logs/
   gw.log
   gateway_startup.log
   gateway_err.log
   ```
4. Add entries using Edit (not Write — preserve existing content)
5. Use the Read → Edit flow, never overwrite the entire .gitignore

### git rm --cached Mechanics

When removing tracked artifacts from git tracking:

1. Confirm the file pattern matches only the intended artifacts:
   ```bash
   git ls-files --error-unmatch "pattern"
   ```
2. Confirm no CI step, Makefile target, or source code reads these files by path
3. Execute the removal:
   ```bash
   git rm --cached "path/to/file"
   ```
   or for patterns:
   ```bash
   git rm -r --cached "__pycache__/"
   ```
4. The files remain on disk (only removed from git tracking)
5. Add the corresponding .gitignore entry in the same operation

### Archive Move Mechanics

When moving a document to docs/archive/:

1. Read the source file
2. Add a retirement notice at the top of the file (if not already present):
   ```
   > **ARCHIVED** — This document was retired on 2026-06-22 as part of the repository hygiene run.
   > Content is preserved for historical reference. Do not update this file.
   > See [successor document path] for current content.
   ```
3. Write to docs/archive/[FILENAME.md]
4. Update cross-references as above
5. Remove source file

---

## After Execution

### Produce the Hygiene Execution Report

Every SAFE_REPOSITORY_HYGIENE run must close with a report file in docs/08_reports/. Name the file:

```
HYGIENE_EXECUTION_REPORT_YYYY-MM-DD.md
```

If multiple hygiene runs occur on the same date, suffix with a sequence number:
```
HYGIENE_EXECUTION_REPORT_2026-06-22_01.md
HYGIENE_EXECUTION_REPORT_2026-06-22_02.md
```

The report must contain these sections:

---

**Template:**

```markdown
# HYGIENE EXECUTION REPORT
Date: YYYY-MM-DD
Session: [brief description]
Tier: SAFE_REPOSITORY_HYGIENE (Tier 1)
Feature work bundled: NO

## Actions Taken

### Files Moved
| From | To | Cross-references updated? |
|------|-----|--------------------------|
| path/from | path/to | YES — [list of files updated] |

### .gitignore Additions
| Entry added | Already present? |
|-------------|----------------|
| __pycache__/ | NO — added |

### git rm --cached Actions
| File/Pattern | Reason |
|-------------|--------|
| tests/api/__pycache__/ | Generated artifact |

### Files Not Touched (deferred from plan)
| Item | Reason deferred |
|------|----------------|
| bin/ removal | Awaiting owner answer on Makefile references |

## Escalations
| Item | Escalation Reason |
|------|------------------|
| [none] | |

## Verification
- [ ] No source code files modified (.py, .js, .ts, .sql)
- [ ] No CI/CD files modified (.github/workflows/)
- [ ] No runtime config files modified (render.yaml, Dockerfiles)
- [ ] No auth, RBAC, or security files modified
- [ ] All cross-references updated
- [ ] All moved files retain retirement/archive notices where applicable
- [ ] .gitignore additions do not duplicate existing entries
- [ ] No files deleted (only moved or removed from git tracking)
```

---

### Update DOC_CATALOGUE.md

After every hygiene run that moves files, update docs/reports/u-series/DOC_CATALOGUE.md with:
- New paths for moved files
- New entries for any newly created files (the execution report itself)
- Removal of paths that no longer exist

### Verify No Broken References

After all moves and cross-reference updates, run a final Grep pass:

For each file that was moved, grep for the old path across all .md files:
```
Grep pattern: "old/path/to/file.md"
Expected result: 0 matches (all references updated)
```

If any matches remain, update them before closing the session.

### Do Not Commit

Leave the commit to the human owner. Stage all changes (git add for new files, git rm --cached for removed artifacts, git add for .gitignore updates) and produce the execution report. The commit message and the decision to push are the owner's responsibility.

---

## Escalation Triggers — What Stops a Hygiene Run Mid-Execution

If any of the following conditions are discovered during execution, stop the current move immediately, revert any partial changes, and escalate to REQUIRES_APPROVAL:

| Trigger | Why It Escalates |
|---------|-----------------|
| A source code file (.py, .js, .ts) imports from or requires the file being moved | The file participates in runtime; this is not a passive document |
| A CI/CD file (.github/workflows/*.yml) references the file path being changed | Moving it changes CI behavior |
| render.yaml or any Dockerfile references the file path | Moving it changes deployment behavior |
| A Makefile target calls the file or its directory by path | Moving it breaks the build target |
| The file path appears in a Python sys.path manipulation or module __init__.py | Import dependency |
| A README or installation guide instructs users to run the file from its current location | Moving it breaks the documented setup procedure |
| The file contains executable code that is run directly (not just called by documentation references) | It is not a passive document |
| Moving the file would require updating a PROTECTED_AREA document without an approved change | See AI_OPERATING_CONTEXT.md PROTECTED_AREAS |
| Any unexpected dependency is found that was not identified in the pre-run Step 3 reference scan | The move plan was incomplete; stop and reassess |

**Escalation procedure:**

1. Stop the current move immediately
2. If the file was already partially moved (Read done, Write done, but Remove-Item not yet done), leave the source file in place — do not remove it
3. If the source file was already removed, restore it from the Write output (you have the content)
4. Document the escalation in the hygiene execution report under "Escalations"
5. Report the item to the human owner with the specific dependency that was discovered
6. Mark the item in APPROVAL_RECLASSIFICATION_REPORT.md as "Escalated — dependency found"

---

## Quick-Reference Checklists

### Pre-Run Checklist
- [ ] Read AI_OPERATING_CONTEXT.md PROTECTED_AREAS table
- [ ] Read SAFE_REPOSITORY_HYGIENE_POLICY.md qualifying criteria
- [ ] Confirmed no feature work is bundled in this session
- [ ] Built the full move plan (source paths, target paths, reference map)
- [ ] Confirmed all target directories exist
- [ ] Read current .gitignore state

### Per-File Move Checklist
- [ ] Read source file completely
- [ ] Identified all cross-references to this file (Grep check done)
- [ ] Target directory exists
- [ ] Write to target path (same content + retirement notice if archiving)
- [ ] Remove source file
- [ ] Updated AI_OPERATING_CONTEXT.md if file was in ACTIVE_AUTHORITY_DOCS
- [ ] Updated DOCUMENT_INVENTORY.md
- [ ] Updated DOC_CATALOGUE.md
- [ ] Updated all other .md files that linked to the old path
- [ ] Grepped for old path — 0 matches remain

### Post-Run Checklist
- [ ] Hygiene execution report written to docs/08_reports/
- [ ] DOC_CATALOGUE.md updated with new paths and new report entry
- [ ] Final Grep pass for old paths — all 0 matches
- [ ] Verification checklist in execution report completed
- [ ] No commits made (left to owner)

---

## Common Mistakes to Avoid

**Moving multiple files before updating cross-references.** Move one file completely (including all reference updates) before starting the next move. Batch moves followed by batch reference updates inevitably miss some references.

**Using Move-Item instead of Read → Write → Remove-Item.** Move-Item leaves no content audit trail. The content written to the new location is never explicitly recorded in the session transcript.

**Adding .gitignore entries without reading the current file first.** Duplicate entries create confusion. Always read the current .gitignore before editing.

**Forgetting to add retirement notices when archiving.** Any file moved to docs/archive/ must have a retirement notice at the top. Without it, future readers do not know the document is retired or where to find the successor.

**Updating DOCUMENT_INVENTORY.md but not DOC_CATALOGUE.md (or vice versa).** Both tracking documents must be updated after any file move. They serve different audiences and both must be accurate.

**Grepping for the filename only, not the full relative path.** A filename like BACKEND-QC.md may appear as a text reference ("see BACKEND-QC.md") without a path, or as a full path reference. Search for both patterns.

**Treating a CI-referenced file as a passive document.** Any file referenced in .github/workflows/*.yml is infrastructure, not documentation, regardless of its extension.

---

## Reference

| Document | Location |
|----------|----------|
| SAFE_REPOSITORY_HYGIENE_POLICY.md | docs/07_governance/ |
| REVISED_DECISION_ESCALATION_MATRIX.md | docs/07_governance/ |
| APPROVAL_RECLASSIFICATION_REPORT.md | docs/07_governance/ |
| AI_OPERATING_CONTEXT.md | docs/07_governance/ |
| DOCUMENT_INVENTORY.md | docs/08_reports/ |
| DOC_CATALOGUE.md | docs/reports/u-series/ |
| REPOSITORY_RESTRUCTURING_PLAN.md | docs/08_reports/ |
| ROOT_LEVEL_CLEANUP_PLAN.md | docs/08_reports/ |
| LEGACY_AND_ARCHIVE_PLAN.md | docs/08_reports/ |

---

*End REPOSITORY_HYGIENE_EXECUTION_GUIDELINES.md*
