---
Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: Human
Phase: 3.5 — Project Memory Layer Establishment
---

# OWNER_DECISION REGISTER

> Genuine product/business decisions that require owner input.
> Items here cannot be resolved from repository evidence or safe defaults alone.
> Owner Required: YES for all entries.

---

## How to Use This Register

For each item:
1. Read the Evidence Reviewed section to understand what was already investigated
2. Read Evidence Exhausted to understand why code cannot resolve it
3. Understand the current safe default (if any) — this is what the system does RIGHT NOW
4. Make your decision and inform the development team
5. Once decided, update this entry: change Status to DECIDED, record the Decision Made, and move any resolved code items to the appropriate downstream register

---

## OD-001: OA-001 — contacts.delete RBAC Code Change Approval

**Item ID:** OA-001
**Title:** contacts.delete scope — TIER 2 code change approval for rbac-scopes.js
**Classification:** OWNER_DECISION
**Current Status:** Awaiting TIER 2 approval for code change
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md
**Evidence Source:** backend/gateway/config/rbac-scopes.js (CONTACTS_DELETE absent); backend/gateway/routes/v1-contacts.routes.js (requireScopes(['contacts.delete']) present); 6 existing delete scope examples as pattern
**Resolution Source:** RESIDUAL_OWNER_DECISION_REGISTER.md Phase 2.9; SAFE_DEFAULT_REGISTER.md SD-001
**Resolution Date:** 2026-06-23 (safe default documented; code change pending)
**Resolved By:** Safe default documented by Phase 2.97; code change approval pending owner

**Decision Summary:** The WHAT is already determined (see SD-001 in SAFE_DEFAULT_REGISTER.md): add CONTACTS_DELETE scope to tenant_admin and super_admin in rbac-scopes.js. What requires owner approval: authorization to touch rbac-scopes.js, which is a PROTECTED file (TIER 2 per REVISED_DECISION_ESCALATION_MATRIX.md).

**Detailed Explanation:** contacts.delete scope is missing from rbac-scopes.js SCOPES constant. Effect: DELETE /contacts/:id returns 403 for ALL authenticated users — contacts cannot be deleted from the live system.

The safe default is fully deterministic: grant `CONTACTS_DELETE: 'contacts.delete'` to `tenant_admin` and `super_admin`. This matches the pattern of all 6 other delete scopes in rbac-scopes.js. The fix is 3 lines of code. No judgment is required about WHAT to do — only TIER 2 approval is needed to actually touch rbac-scopes.js.

**Evidence Reviewed:**
- `backend/gateway/config/rbac-scopes.js` — CONTACTS_DELETE absent (grep confirms)
- `backend/gateway/routes/v1-contacts.routes.js` — requireScopes(['contacts.delete']) present on DELETE route
- 6 existing delete scopes confirm pattern: LEADS_DELETE, DEALS_DELETE, CASES_DELETE, QUOTES_DELETE, ORDERS_DELETE, INVOICES_DELETE

**Evidence Exhausted:** The code fix is technically determinable from patterns. However, rbac-scopes.js is explicitly listed in REVISED_DECISION_ESCALATION_MATRIX.md as TIER 2 (PROTECTED_AREA): "Does the action touch rbac-scopes.js?" → YES → TIER 2 REQUIRES_APPROVAL.

**Options:**
1. [RECOMMENDED] Approve the 3-line change: add CONTACTS_DELETE to SCOPES + grant to tenant_admin + super_admin. Contacts can then be deleted by admins. GDPR deletion requests become serviceable.
2. Decline — accept that contacts cannot be deleted (Option 3 from prior register). Frontend must permanently hide delete controls for all roles.

**Risk if not actioned:**
- CRITICAL: contacts cannot be deleted from live system
- GDPR/data deletion requests are unserviceable via the API
- Contacts accumulate permanently with no cleanup mechanism

**Current Behavior (SD-001 safe default in effect):** Frontend hides the contacts delete button for all non-admin roles. DELETE /contacts/:id returns 403 for ALL roles (including tenant_admin and super_admin) until the code change is applied.

**Affected Components:** backend/gateway/config/rbac-scopes.js (3 lines), frontend delete button visibility
**Affected Routes:** DELETE /contacts/:id
**Affected APIs:** Customer 360 CDP / Contacts API
**Affected Workflows:** Contact data management, GDPR deletion
**Affected Roles:** tenant_admin, super_admin (will gain delete capability); all others unchanged

**Owner Required:** YES — TIER 2 code change approval for PROTECTED file rbac-scopes.js
**External Dependency:** NO

**Future Impact:** Once approved and applied: GDPR deletions serviceable. Contact cleanup possible. Frontend delete button visible to tenant_admin and super_admin.

**Reopen Criteria:** Permanently closed once decision is made (either approve change or formally document that contacts are non-deletable by design).

**Related Documents:** REVISED_DECISION_ESCALATION_MATRIX.md (TIER 2 criteria), backend/gateway/config/rbac-scopes.js, SAFE_DEFAULT_REGISTER.md SD-001, RESIDUAL_OWNER_DECISION_REGISTER.md OA-001
**Related Register Entries:** SD-001 (SAFE_DEFAULT_REGISTER.md)

---

## Summary

| Item | Status | Launch Impact | Priority |
|------|--------|---------------|----------|
| OD-001 (OA-001) | Awaiting TIER 2 code-change approval | Contacts cannot be deleted (GDPR risk) | P1 — pre-launch |

**Note:** All other items previously listed as OWNER-REQUIRED have been resolved:
- D-002 (custom objects scope): CLOSED Phase 3.25 — K-02 is advisory shell per FEATURE_SCOPE.md
- OA-003 (payment credentials): reclassified as EXTERNAL_DEPENDENCY — not a product decision, a vendor relationship
- G-MED-005 (Urdu templates): reclassified as EXTERNAL_DEPENDENCY — not a product decision, a linguistic review
- OA-004 (AI model): AUTO_CLOSED — rule-based IS the C6 design
- OA-005 (contracts gateway): AUTO_CLOSED — C7 scope per DESIGN-SPEC.md
- All SD-002 through SD-011 items: accepted as SAFE_DEFAULT — no owner decision needed

**Net result: 1 genuine owner decision remains (OA-001 TIER 2 code change approval).**

---

*End OWNER_DECISION_REGISTER.md — 1 item (OD-001) — Phase 3.5 (2026-06-23)*
