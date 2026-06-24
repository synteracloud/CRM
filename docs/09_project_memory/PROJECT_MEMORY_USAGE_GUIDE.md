---
Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI
Phase: 3.5 — Project Memory Layer Establishment
---

# PROJECT MEMORY USAGE GUIDE

> Instructions for future AI sessions on how to use the docs/09_project_memory/ layer.
> Read this document after AI_OPERATING_CONTEXT.md and before doing any gap analysis, audit, redesign, or build work.

---

## 1. What This Memory Layer Is

docs/09_project_memory/ is the institutional memory layer for Pakistan CRM OS. It contains:
- Every open item, gap, and decision from all prior audit phases (U0 through Phase 3.5)
- Their final classifications (what was resolved, what is deferred, what needs owner input)
- Evidence trails for each resolution
- Sprint plans for deferred items

**Purpose:** Future AI sessions should not re-derive decisions already made. Read the memory layer first. If an item is already classified, trust the classification and build on it rather than redoing the analysis.

---

## 2. Load Order for New AI Sessions

Load documents in this exact order:

| Order | Document | Why |
|-------|----------|-----|
| 1 | docs/07_governance/AI_OPERATING_CONTEXT.md | Primary context: current phase, frozen decisions, constraints, authority docs |
| 2 | docs/09_project_memory/FINAL_CLASSIFIED_REGISTER.md | Master index of all classified items — establishes what is already decided |
| 3 | Specific register (see table below) | Load only the register relevant to the current task |

**Load specific registers only when needed:**

| Register | Load When |
|----------|-----------|
| AUTO_CLOSED_REGISTER.md | Investigating a previously raised gap — check if it was already closed |
| SAFE_DEFAULT_REGISTER.md | Implementing a feature that involves an item with a documented default |
| OWNER_DECISION_REGISTER.md | Before escalating any item — check if it already has a documented path |
| EXTERNAL_DEPENDENCY_REGISTER.md | Before touching payment, Urdu, social, or voice note features |
| OUT_OF_SCOPE_REGISTER.md | Before implementing any C7+ feature — check if it is intentionally deferred |

---

## 3. When to Check Memory Before Acting

Check the memory layer BEFORE:
- Raising a new gap or issue (it may already be classified)
- Escalating an item to the owner (it may already have a safe default or documented path)
- Implementing any auth, payment, RBAC, or AI feature (may have constraints documented here)
- Starting any gap analysis, security audit, or architecture review
- Building any of the 8 out-of-scope items (they are intentionally deferred)

**The 60-second check:** Search FINAL_CLASSIFIED_REGISTER.md for keywords related to your task. If the item appears, read the Register Link column to find the full detail. Do not re-investigate.

---

## 4. How to Add New Entries

When a new item is discovered during any audit, build, or review:

**Step 1: Classify the item**
Use the classification rules in PROJECT_MEMORY_GOVERNANCE.md §1.

**Step 2: Add full detail to the correct register file**
- AUTO_CLOSED → AUTO_CLOSED_REGISTER.md (add AC-NNN entry)
- SAFE_DEFAULT → SAFE_DEFAULT_REGISTER.md (add SD-NNN entry)
- OWNER_DECISION → OWNER_DECISION_REGISTER.md (add OD-NNN entry)
- EXTERNAL_DEPENDENCY → EXTERNAL_DEPENDENCY_REGISTER.md (add ED-NNN entry)
- OUT_OF_SCOPE → OUT_OF_SCOPE_REGISTER.md (add OOS-NNN entry)

**Step 3: Add one-line summary to FINAL_CLASSIFIED_REGISTER.md**
Add a row to the correct section table. Include: Item ID, Title, Classification, Status, Evidence Source, Resolution Source, Current State, Register Link.

**Step 4: Do NOT modify the authority docs** (AI_OPERATING_CONTEXT.md, FEATURE_SCOPE.md, etc.) to record the new item — the memory registers are the correct location.

---

## 5. How to Reopen an Item

Items may only be reopened if ONE of these conditions is true:
1. **Evidence changed:** New code evidence contradicts the original resolution (e.g., a scope is removed that was confirmed present)
2. **Implementation changed:** The system state has changed in a way that invalidates the default (e.g., multi-instance deployment was added, requiring OA-002 JTI blocklist fix)
3. **Owner reversal:** The owner explicitly reverses a prior decision
4. **External event:** A third-party event changes the risk profile (e.g., a CVE is published for a dependency marked safe)

To reopen: update the item's Status in its register to REOPENED, add a Reopen Reason field, and add a new one-line summary entry in FINAL_CLASSIFIED_REGISTER.md.

**Never reopen** an item merely because you disagree with the classification — provide evidence for the reopen.

---

## 6. How This Layer Relates to Authority Docs

| Layer | Role |
|-------|------|
| Authority Docs (docs/00_authority/, docs/07_governance/) | Current source of truth for what the system is and does |
| Memory Layer (docs/09_project_memory/) | Historical context for what was investigated, decided, and deferred |

**Rule:** Authority docs win in any conflict. The memory layer records history — it does not override current decisions.

**Example:** If FEATURE_SCOPE.md says a feature is "Built" but the memory layer has an AC item saying it was deferred, the FEATURE_SCOPE.md is the ground truth. Update the memory item to reflect the current state.

---

## 7. Pakistan CRM Specific Context

Every AI session working on this project must know:

**Currency:** PKR only. Lakh/Crore formatting. No multi-currency. Formatter: crm-components.js pkr()

**Primary channel:** WhatsApp (not an integration — a primary layer). Inbound messages auto-create Contacts and Leads. See ADR-003.

**Payment system:** JazzCash + Easypaisa. Both in stub mode (P-016). Do not touch render.yaml payment stub flags without OA-003 activation credentials.

**Localization:** English (active) + Urdu (pending P-017 native speaker review). RTL CSS infrastructure is built. Do not remove UR_TODO markers — they are review flags, not error markers.

**DUMMY_MODE:** false. crm-api.js DUMMY_MODE is false. Pages use live API with graceful crm-dummy.js fallback for unconfirmed endpoints. Do not set DUMMY_MODE=true.

**7 Canonical Roles** (in rbac-scopes.js — do not add or remove without TIER 2 approval):
1. super_admin — platform operator, all scopes
2. tenant_owner — company owner, full company access
3. tenant_admin — company admin, all management scopes
4. sales_manager — manages sales team, pipeline oversight
5. sales_rep — individual contributor, own leads/deals
6. support_agent — handles cases and inbox
7. marketing — campaigns and segments

**91 scopes** defined in backend/gateway/config/rbac-scopes.js. When OA-001 is applied: 92 scopes (adds CONTACTS_DELETE).

**Current commercialisation phase:** C6 — Commercial Launch (in progress as of 2026-06-23)

---

## 8. Quick Reference: Key File Paths

| Item | Path |
|------|------|
| RBAC scopes (frozen) | backend/gateway/config/rbac-scopes.js |
| Payment adapters (stub) | backend/adapters/pakistan/payments/ |
| AI services (rule-based) | backend/src/ai_copilot/services.py, backend/src/ai_insights/services.py |
| Event bus | backend/src/event_bus/core.py |
| Auth routes (PROTECTED) | backend/gateway/routes/v1-auth.routes.js |
| Tenant isolation middleware | backend/gateway/middleware/auth-rbac.js |
| Render deployment config | render.yaml |
| Feature scope | docs/00_authority/FEATURE_SCOPE.md |
| Design spec (75 pages) | DESIGN-SPEC.md |
| Framework spec | FRAMEWORK.md |
| AI operating context | docs/07_governance/AI_OPERATING_CONTEXT.md |
| Governance escalation matrix | docs/07_governance/REVISED_DECISION_ESCALATION_MATRIX.md |
| Frontend permission matrix | docs/03_frontend_authority/FRONTEND_PERMISSION_MATRIX.md (if exists) |
| App pages | frontend/src/app/*.html |
| Backend services | backend/src/ (34 FastAPI modules) |
| Gateway routes | backend/gateway/routes/ (44 route groups) |
| DB schemas | backend/db/*/schema.sql (18 schemas) |

---

## 9. What the Memory Layer Does NOT Replace

Do not use the memory layer as a substitute for:
- Reading actual code when implementing a feature (memory records history; code is ground truth)
- Running tests before committing changes
- Following CLAUDE.md build checklist for any app/*.html page
- Checking DESIGN-SPEC.md scope gate before touching any file
- Following REVISED_DECISION_ESCALATION_MATRIX.md before making code changes

The memory layer answers "has this been investigated?" — not "how do I build this?"

---

*End PROJECT_MEMORY_USAGE_GUIDE.md — Phase 3.5 (2026-06-23)*
