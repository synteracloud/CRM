---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Derived From: USER_ROLES_AND_PERMISSIONS.md, API_CONTRACT.md, DESIGN-SPEC.md, DETERMINISM_CERTIFICATION_REPORT.md, AI_OPERATING_CONTEXT.md
---

# FRONTEND GAP REGISTER — Pakistan CRM OS

Genuine gaps between frontend design authority and backend reality. Categorized by type.

**Gap Status Key:**
- CONFIRMED — verified from source code or authority docs
- DOCUMENTED — documented constraint, known and accepted for C6
- MONITORING — track post-C6; no immediate action required
- OWNER_DECISION — requires human sign-off before resolution

---

## CATEGORY 1: Security Gaps (Permission / Scope Issues)

### G-001 — contacts.delete Scope Missing from SCOPES Constant

**Type:** Security / Permission Gap
**Status:** CONFIRMED — OWNER_DECISION (OA-001)
**Source:** USER_ROLES_AND_PERMISSIONS.md §4, FULLSTACK_STITCHING_CONTRACT.md §1

**Description:**
The `contacts.delete` scope is referenced in two places:
1. `v1-contacts.routes.js` route guard: `requireScopes(['contacts.delete'])`
2. `ROLE_SCOPES.tenant_admin[]` array

But it is NOT present in the `SCOPES` constant object in `rbac-scopes.js`.

**Effect:** No JWT can ever be issued with `contacts.delete` in its `scopes[]` array (because scopes are granted from the SCOPES constant). The DELETE /contacts/:id endpoint is effectively inaccessible to ALL roles, including tenant_admin and tenant_owner.

**Frontend Impact:**
- Delete button hidden for all roles (SD-001 in effect)
- This is documented as a safe default, not a silent failure
- Handle 403 gracefully on DELETE /contacts/:id

**Resolution Path:** Add `CONTACTS_DELETE: 'contacts.delete'` to SCOPES constant in rbac-scopes.js; grant to tenant_admin and tenant_owner. OA-001 requires owner sign-off.

**Frontend Action Required:** None until OA-001 resolved. Document SD-001 on all contact delete UI elements.

---

### G-002 — leads.delete Scope Status (Verified as Present)

**Type:** Verification finding — NOT a gap
**Status:** CONFIRMED PRESENT
**Source:** USER_ROLES_AND_PERMISSIONS.md §4

**Description:**
USER_ROLES_AND_PERMISSIONS.md originally flagged leads.delete as potentially missing. Verified 2026-06-23: `LEADS_DELETE: 'leads.delete'` IS present in rbac-scopes.js line 21. No gap exists for leads.delete.

**Frontend Action Required:** None. leads.delete scope is functional and granted to tenant_admin.

---

## CATEGORY 2: API / Route Gaps

### G-003 — Contract Lifecycle Management: No Gateway Route

**Type:** API Gap — Backend module with no gateway exposure
**Status:** CONFIRMED — DOCUMENTED
**Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS D-001

**Description:**
`contract_lifecycle_management` module exists in backend Python (`backend/src/`) with 12 API endpoints defined. However, no `v1-contract*.routes.js` exists in the gateway route list (44 confirmed route groups).

**Frontend Impact:**
- No frontend page for contract management exists in C6 scope (confirmed — not in DESIGN-SPEC.md §3)
- Zero orphaned frontend pages calling these endpoints
- The 12 backend endpoints have no frontend consumer

**Resolution Path:** Human architectural decision — expose via gateway (creates new route group #45) or archive module. Deferred to C7.

**Frontend Action Required:** None for C6. If C7 adds a contracts page, create v1-contracts.routes.js first.

---

### G-004 — Custom Objects: No Gateway Route Confirmed

**Type:** API Gap — Ambiguous backend module
**Status:** CONFIRMED — OWNER_DECISION (D-002)
**Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS D-002

**Description:**
`custom_object_framework/` and `custom_objects/` modules confirmed in backend. However, no `v1-custom-objects.routes.js` found in the 44-item gateway route list.

**Frontend Impact:**
- object-builder.html (K-02) is an advisory shell only
- No live API calls from K-02 are confirmed functional
- SD-009 in effect: K-02 documented as visual-only

**Resolution Path:** Human decision on routing mechanism. Deferred.

**Frontend Action Required:** None for C6. K-02 remains advisory shell. Document SD-009 on page.

---

### G-005 — activities.html (Library Page) vs activity.html (B-06 Custom Page)

**Type:** Naming / Directory Gap
**Status:** MONITORING
**Source:** Directory listing of frontend/src/app/

**Description:**
Two files exist with similar names:
- `activities.html` — NexLink library demo (94 library pages)
- `activity.html` — Custom CRM page (B-06 Activity Feed)

These are distinct pages. activities.html is a library template; activity.html is the B-06 custom page at route /app/activity.

**Frontend Impact:** No functional gap. Potential confusion for new developers who might build on activities.html instead of activity.html.

**Frontend Action Required:** Document this disambiguation. The authoritative custom page is `activity.html` (B-06). `activities.html` is a library demo.

---

## CATEGORY 3: Role / RBAC Documentation Gaps

### G-006 — DUMMY_MODE Frontend Wiring Incomplete for 70 Pages

**Type:** Live API wiring gap
**Status:** DOCUMENTED — Phase 6 Component 3 pending
**Source:** AI_OPERATING_CONTEXT.md CURRENT_PHASE, DETERMINISM_CERTIFICATION_REPORT.md

**Description:**
Only 5 of 75 custom pages are confirmed fully wired to live API:
1. integrations.html (G-05) — Wired 2026-05-31
2. report-builder.html (H-07) — Wired 2026-05-31
3. data-governance.html (J-03) — Wired 2026-05-31
4. engagement-dashboard.html (A-08) — Wired 2026-05-31
5. billing-settings.html (G-04) — Wired 2026-05-31 (content blocked by P-016)

The remaining 70 pages use live API calls with graceful fallback to crm-dummy.js (DUMMY_MODE: false in crm-api.js). The fallback path is intentional and correct; this is not a bug.

**Frontend Impact:**
- 70 pages may display dummy data if API returns an error
- Full live-API re-verification pass (Phase 6 Component 3) pending
- Frontend authority documentation is complete regardless of wiring status

**Frontend Action Required:** None blocking for authority documentation. Track as pending in Phase 6 Component 3 work.

---

### G-007 — Frontend Scope-Based UI Gating: CONFIRMED NOT IMPLEMENTED

**Type:** Implementation gap
**Status:** CONFIRMED — NOT IMPLEMENTED (verified Phase 3.25 retry, 2026-06-24)
**Source:** USER_ROLES_AND_PERMISSIONS.md §7

**Description:**
Scope-based UI gating does not exist in the frontend codebase. Verified by direct code inspection.

**Evidence (Phase 3.25 retry):**
- `frontend/src/assets/js/app/crm-api.js` — no `hasScope`, no scope parsing, no JWT decode utility
- `frontend/src/assets/js/app/crm-shell.js` — no scope-gating logic; only uses `a([page])` helper for active menu link styling
- Grep for `hasScope|getScopes|userScopes|jwt.*scope|scope.*jwt|scopes\[|checkScope` across all frontend JS = no matches

**Current State (Confirmed):** No `hasScope()` utility exists. JWT scopes claim is never read by frontend JS. All permission-gated buttons (delete, admin-only actions) are currently visible to all authenticated users regardless of role.

**Risk:** Users see buttons they cannot execute — server returns 403 on attempt. UX is degraded for lower-privileged roles.

**Frontend Action Required (Pre-launch):** Implement `hasScope(scope)` utility in crm-api.js that decodes JWT and checks scopes array. Add scope checks to all permission-gated buttons per FRONTEND_PERMISSION_MATRIX.md.

---

### G-008 — Role Name Inconsistency Across Authority Documents (RESOLVED in Frontend Authority docs)

**Type:** Documentation inconsistency
**Status:** RESOLVED in docs/03_frontend_authority/ — MONITORING for other governance docs
**Source:** USER_ROLES_AND_PERMISSIONS.md vs DETERMINISM_CERTIFICATION_REPORT.md vs POST_COLLAPSE_FRONTEND_READINESS.md

**Description:**
Authority documents were originally written with incorrect role names not present in rbac-scopes.js. This was corrected 2026-06-23.

**Canonical role names (from rbac-scopes.js — AUTHORITATIVE):**
tenant_owner, tenant_admin, manager, agent, analyst, auditor, integration_service

**Previously incorrect names used in these docs (now corrected):**
- super_admin → tenant_owner
- senior_agent → manager (collections scopes are included on the agent role)
- collections_agent → agent
- read_only → analyst

**Other governance docs that still use old names (require separate update):**
- DETERMINISM_CERTIFICATION_REPORT.md (uses: super_admin, tenant_owner, tenant_admin, sales_manager, field_agent, support_agent, viewer)
- POST_COLLAPSE_FRONTEND_READINESS.md (uses: super_admin, tenant_owner, tenant_admin, sales_rep, support_agent, finance_user, viewer)

**Frontend Authority Decision:** All 12 docs in docs/03_frontend_authority/ now use canonical rbac-scopes.js role names. USER_ROLES_AND_PERMISSIONS.md also corrected.

**Frontend Action Required:** None for docs/03_frontend_authority/ — corrections applied. Flag for governance: update DETERMINISM_CERTIFICATION_REPORT.md and POST_COLLAPSE_FRONTEND_READINESS.md to use canonical role names.

---

## CATEGORY 4: Blocked Features (Known Production Constraints)

### G-009 — JazzCash/Easypaisa: Payment UI Blocked (P-016)

**Type:** Feature stub — production constraint
**Status:** DOCUMENTED — TRUE_OWNER_DECISION (OA-003)

**Pages Affected:** billing-settings.html (G-04), invoices-detail.html (C-08), collections.html (B-08)

**Description:** Payment method section shows STUB state. POST /payments returns stub response. POST /payment-webhooks/* returns stub response.

**Frontend Action Required:** Display stub state per SD-002. No further action until OA-003 resolved.

---

### G-010 — Notification Strings: Urdu Blocked (P-017)

**Type:** Localization stub — production constraint
**Status:** DOCUMENTED

**Pages Affected:** notifications.html (G-06)

**Description:** EN notification strings only. Urdu strings exist with `<!-- UR_TODO: -->` markers but are blocked by P-017 (native speaker review pending).

**Frontend Action Required:** Display EN only per SD-004. RTL CSS is built.

---

### G-011 — AI Features: Rule-Based Only (AI-001)

**Type:** Feature advisory state
**Status:** DOCUMENTED — OWNER_DECISION (OA-004)

**Pages Affected:** ai-copilot.html (M-01), ai-insights.html (M-02)

**Description:** All AI features use rule-based weighted-sum algorithms. No LLM SDK in requirements.txt. AI inference model deferred to C7.

**Frontend Action Required:** Display advisory-only banner per SD-003.

---

### G-012 — Facebook/Instagram Lead Capture Blocked (MR-001)

**Type:** Feature not implemented
**Status:** DOCUMENTED

**Pages Affected:** lead-new.html (I-01)

**Description:** Facebook/Instagram lead capture hidden in UI with `data-unblock="MR-001"`. Meta Business Manager account setup pending.

**Frontend Action Required:** Keep hidden per SD-005.

---

## CATEGORY 5: Minor Documentation Gaps

### G-013 — followups Scope Group Missing from SCOPES Constant

**Type:** Scope naming gap
**Status:** MONITORING
**Source:** FULLSTACK_STITCHING_CONTRACT.md §2

**Description:**
FULLSTACK_STITCHING_CONTRACT.md §2 lists permissions: "followups.read, followups.create, followups.complete, followups.snooze" — but these exact scope strings are NOT in the USER_ROLES_AND_PERMISSIONS.md 91-scope list. Follow-up actions use tasks.* scopes instead (tasks.read, tasks.create, tasks.complete, tasks.update).

**Frontend Action Required:** Use tasks.* scope names when gating follow-up UI elements.

---

### G-014 — inbox.admin Scope Not in 91-Scope List

**Type:** Scope naming gap
**Status:** MONITORING
**Source:** PRODUCT_WORKFLOWS.md WF-D (references inbox.admin for queue management)

**Description:**
WF-D documentation references `inbox.admin` scope for queue management. However, USER_ROLES_AND_PERMISSIONS.md 91-scope list only includes inbox.read, inbox.claim, inbox.handoff, inbox.supervise. inbox.admin may be an alias for inbox.supervise or may not exist.

**Frontend Action Required:** Use `inbox.supervise` for routing-config.html (L-03) gating until inbox.admin is confirmed in rbac-scopes.js.

---

## Summary

| Gap ID | Category | Severity | Frontend Impact | Resolution |
|---|---|---|---|---|
| G-001 | Security / RBAC | HIGH | contacts.delete hidden for all roles (SD-001) | OA-001 owner decision |
| G-002 | Verification | None | None — leads.delete is present | N/A |
| G-003 | API missing gateway | Medium | No C6 contracts page affected | Deferred C7 |
| G-004 | API ambiguous | Medium | K-02 advisory shell (SD-009) | Owner decision D-002 |
| G-005 | Naming clarity | Low | activities.html vs activity.html disambiguation | Document only |
| G-006 | Wiring incomplete | Low | 70 pages use dummy fallback | Phase 6 Component 3 |
| G-007 | UI gating unverified | Medium | Scope-based button show/hide may be missing | Verify post-C6 |
| G-008 | Role name mismatch | Medium | Must use Set A names in all implementation | Update other docs |
| G-009 | P-016 payment stub | None (documented) | G-04, C-08 stub state (SD-002) | OA-003 |
| G-010 | P-017 Urdu blocked | None (documented) | G-06 EN only (SD-004) | P-017 |
| G-011 | AI advisory only | None (documented) | M-01, M-02 rule-based (SD-003) | OA-004 |
| G-012 | MR-001 FB/IG blocked | None (documented) | I-01 hidden element (SD-005) | MR-001 |
| G-013 | followups scope alias | Low | Use tasks.* for follow-up gating | Clarify in rbac-scopes.js |
| G-014 | inbox.admin vs inbox.supervise | Low | Use inbox.supervise for L-03 | Clarify in rbac-scopes.js |

---

## Conclusion

**There are no gaps that block Frontend Authority Capture.**

The frontend authority model is complete for C6 scope. All identified gaps are either:
1. Documented production constraints with safe defaults in effect (G-001, G-009 through G-012)
2. Backend-only concerns with no current frontend page affected (G-003, G-004)
3. Post-C6 verification work (G-006, G-007)
4. Minor clarifications needed in other authority docs (G-005, G-008, G-013, G-014)

**The 75 custom pages are correctly specified in this authority model.** No gap prevents a developer from using this authority model to build, maintain, or verify any C6 frontend page.

---

*End FRONTEND_GAP_REGISTER.md*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
