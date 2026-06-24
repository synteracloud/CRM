---
Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI
Version: 1.0
Phase: 3.5 — Project Memory Layer Establishment
---

# PROJECT MEMORY GOVERNANCE

> Rules for maintaining the docs/09_project_memory/ layer.
> These rules govern how items are classified, added, reopened, and retired.
> Every AI session and human contributor must follow these rules when modifying the memory layer.

---

## 1. Classification Rules

Every item must be assigned exactly one classification. Use the decision tree below.

```
Is the item resolved by repository evidence alone (code, config, docs)?
  YES → AUTO_CLOSED
  NO  → Continue

Is a deterministic safe default fully documented and accepted?
  YES → SAFE_DEFAULT
  NO  → Continue

Does resolution require a human commercial, legal, or product-scope judgment?
  YES → OWNER_DECISION
  NO  → Continue

Does resolution require external provisioning (vendor credentials, government registration, third-party approval)?
  YES → EXTERNAL_DEPENDENCY
  NO  → Continue

Is the item intentionally deferred to a future phase (C7+)?
  YES → OUT_OF_SCOPE
  NO  → Item is not classifiable — escalate to owner for guidance
```

**Classification Criteria Detail:**

| Classification | Applies When |
|---------------|-------------|
| AUTO_CLOSED | Code grep confirms, docs confirm, or the absence of an issue is confirmed. Collapse rules A–F from DECISION_COLLAPSE_REGISTER.md Phase 3.25. No human judgment needed. |
| SAFE_DEFAULT | The correct action is deterministic from existing patterns, architecture decisions, or risk tolerance at C6 scale. Owner may object but action proceeds if no objection is received. |
| OWNER_DECISION | The WHAT cannot be derived from code. Requires product roadmap knowledge, commercial judgment, legal expertise, or TIER 2 code-change approval for a PROTECTED file. |
| EXTERNAL_DEPENDENCY | Resolution requires a third-party entity (vendor, government, human expert) outside the development team. No code change can supply the resolution. |
| OUT_OF_SCOPE | The feature/fix is correct to defer — it was never in the current phase's scope, or it was explicitly approved for deferral with a documented future phase target. |

---

## 2. No Duplicate Entries Rule

**Every item appears in exactly ONE register file.**

If an item has both a SAFE_DEFAULT component and an OWNER_DECISION component (like OA-001 — what to do is a safe default, but touching rbac-scopes.js requires TIER 2 approval):
- The item appears in SAFE_DEFAULT_REGISTER.md for the "what to do" default
- The item ALSO appears in OWNER_DECISION_REGISTER.md for the "TIER 2 approval" requirement
- FINAL_CLASSIFIED_REGISTER.md has ONE summary row (primary classification = SAFE_DEFAULT; note the OWNER_DECISION link in the Current State field)

**Disambiguation rule:** If an item spans two categories, the primary classification is the more restrictive one (OWNER_DECISION > SAFE_DEFAULT > AUTO_CLOSED). Note the secondary register link in both registers.

**Never copy full detail entries between registers.** Cross-reference by Related Register Entries field only.

---

## 3. Reopen Governance

Items may be reopened ONLY when ONE of these four conditions is met:

| Condition | Example | Evidence Required |
|-----------|---------|-------------------|
| Evidence changed | A scope confirmed present is discovered absent | grep output + file read showing absence |
| Implementation changed | Multi-instance deployment added (changes OA-002 risk profile) | render.yaml or deployment config change |
| Owner reversal | Owner explicitly reverses a prior safe default | Written owner decision |
| External event | CVE published for a dependency marked safe | CVE ID + affected version confirmation |

**Reopen procedure:**
1. Update the item's Status field in its register to: `REOPENED — [date] — [condition met]`
2. Add a `Reopen Reason:` field with specific evidence
3. Re-classify using the decision tree in §1
4. Update FINAL_CLASSIFIED_REGISTER.md summary row with new status

**Reopen is NOT permitted for:**
- Disagreement with the original classification (without new evidence)
- General concern or uncertainty (uncertainty is not evidence)
- A new AI session not finding the evidence independently (trust prior classifications)

---

## 4. Project Completion Rule

**External dependencies do not block development.**

Items in EXTERNAL_DEPENDENCY_REGISTER.md (vendor credentials, linguistic reviews, third-party approvals) are NOT gates on the development roadmap. The system is designed to launch in stub/restricted mode and progressively activate as external items are resolved.

**Rule:** The development team does not wait for external dependencies. Build on stub state. Activate when credentials arrive.

**Implementation rule:** Any feature with an EXTERNAL_DEPENDENCY item MUST have a stub implementation that allows full system operation without the external item. If a stub does not exist, building the stub is the development priority — not waiting for the external dependency.

---

## 5. Future Workflow

Standard workflow for any AI session or developer encountering a potential gap, question, or decision:

```
1. SEARCH: Search FINAL_CLASSIFIED_REGISTER.md for keywords
   → If found: read the Register Link, follow the documented path. Do not re-investigate.
   → If not found: proceed to step 2

2. INVESTIGATE: Use code evidence, documentation, and patterns
   (Collapse rules A–F from DECISION_COLLAPSE_REGISTER.md Phase 3.25)

3. CLASSIFY: Apply classification decision tree from §1

4. DOCUMENT:
   a. Add full-detail entry to correct register file
   b. Add one-line summary to FINAL_CLASSIFIED_REGISTER.md
   c. Do NOT modify authority docs (FEATURE_SCOPE.md, AI_OPERATING_CONTEXT.md, etc.)
      unless the item requires a genuine authority doc update

5. ACT: Follow the classification:
   AUTO_CLOSED → No action needed
   SAFE_DEFAULT → Implement the documented default
   OWNER_DECISION → Escalate to owner with evidence and options
   EXTERNAL_DEPENDENCY → Document; proceed with stub implementation
   OUT_OF_SCOPE → Do not implement; document future phase target
```

---

## 6. Maintenance Responsibility

| Role | Responsibility |
|------|---------------|
| AI sessions | Read FINAL_CLASSIFIED_REGISTER.md before raising new items. Add entries for genuinely new discoveries. Never re-investigate closed items. |
| Human owner | Respond to OWNER_DECISION items. Trigger EXTERNAL_DEPENDENCY items (vendor applications, expert engagement). Approve TIER 2 code changes. |
| Development team | Apply SAFE_DEFAULT code changes once owner approves TIER 2 items. Execute SAFE_REPOSITORY_HYGIENE tasks (SD-003, SD-004, SD-009). |

**Ownership transfer:** This memory layer is owned by the AI session set that created it. Future AI sessions inherit this layer and contribute to it. Humans are notified when OWNER_DECISION or EXTERNAL_DEPENDENCY items require action.

---

## 7. Register File Index

| File | Classification | Item Count (v1.0) |
|------|---------------|-------------------|
| FINAL_CLASSIFIED_REGISTER.md | Master index (all) | 50 total |
| AUTO_CLOSED_REGISTER.md | AUTO_CLOSED | 24 |
| SAFE_DEFAULT_REGISTER.md | SAFE_DEFAULT | 12 |
| OWNER_DECISION_REGISTER.md | OWNER_DECISION | 1 |
| EXTERNAL_DEPENDENCY_REGISTER.md | EXTERNAL_DEPENDENCY | 5 |
| OUT_OF_SCOPE_REGISTER.md | OUT_OF_SCOPE | 8 |
| PROJECT_MEMORY_USAGE_GUIDE.md | Usage instructions | N/A |
| PROJECT_MEMORY_GOVERNANCE.md | Governance rules | N/A |

**Total classified items in v1.0:** 50
**Total register files:** 8

---

## 8. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-23 | Initial creation — Phase 3.5 Project Memory Layer Establishment. Consolidated from 10 input registers spanning U0 through Phase 3.25. 50 items classified across 5 categories. |

---

## 9. Relationship to Prior Phase Reports

The following reports in docs/08_reports/ are the SOURCE documents for this memory layer. They contain the detailed investigation history that supports each classification. Do not delete these reports — they are the audit trail.

| Source Report | Phase | What It Contributed |
|--------------|-------|---------------------|
| FINAL_CLASSIFIED_REGISTER.md | 2.97 | Master item list with AUTO-CLOSED, SAFE-DEFAULT, OWNER-REQUIRED classifications |
| DECISION_COLLAPSE_REGISTER.md | 3.25 | 28 items collapsed in Phase 3.25 Autonomous Gap Elimination |
| OWNER_REQUIRED_COMPRESSION_REPORT.md | 2.97 | 18 owner-required items → 12 safe defaults, 3 auto-closed, 3 remaining |
| UNRESOLVABLE_ITEMS_REGISTER.md | 3.25 | 2 confirmed unresolvable items (OA-003, G-MED-005) + D-002 closure |
| APPROVAL_ELIMINATION_REPORT.md | 2.9 | 14 items eliminated from approval queue in Phase 2.9 |
| RESIDUAL_OWNER_DECISION_REGISTER.md | 2.9 | 9 owner decisions documented with evidence and options |
| OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md | Pre-3 | Original 9 owner items before compression passes |
| AI_OPERATING_CONTEXT.md | Active | 13 frozen decisions, known constraints, current phase |
| FEATURE_SCOPE.md | Active | 131 features, C0-C6 phase gates, blocked features |

**The memory registers in docs/09_project_memory/ are the DISTILLATION of these reports.** For audit trail purposes (why was item X classified as Y?), read the source report referenced in each register entry's Resolution Source field.

---

*End PROJECT_MEMORY_GOVERNANCE.md — Version 1.0 — Phase 3.5 (2026-06-23)*
