---
Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: Human
Phase: 3.25
---

# UNRESOLVABLE ITEMS REGISTER

> Only items that are genuinely unresolvable from repository evidence.
> Each entry proves why code, config, docs, and patterns cannot supply the answer.
> Updated Phase 3.25 (2026-06-23): D-002 CLOSED from repository evidence. 2 items remain.

---

## CLOSED IN PHASE 3.25

### D-002: Custom Objects Module Product Scope in C6 — CLOSED

**Status:** CLOSED 2026-06-23 — resolved from repository evidence during Phase 3.25

**Evidence used to close:**
- `docs/00_authority/FEATURE_SCOPE.md` §22 (Module 22: Builder Tools): Feature 129 "Custom object builder (schema definition, layout)" has Status = **Built**
- `DESIGN-SPEC.md` line 204: K-02 (object-builder.html) — "Cat 2. Built 2026-05-29. Browser-approved."
- `docs/08_reports/OWNER_REQUIRED_COMPRESSION_REPORT.md` D-002 entry: "Whether custom objects is in C6 product scope" — confirmed yes by FEATURE_SCOPE.md

**Resolution:** K-02 is a C6 built page. The correct C6 implementation is advisory shell (no live backend API dependency), which is exactly what FG-005 in FRONTEND_GAP_REGISTER.md documents. No gateway route is needed for the advisory shell posture. D-002 is fully resolved: build K-02 as advisory shell with crm-dummy.js data.

**Frontend impact:** Zero — FG-005 already documents K-02 as advisory shell regardless.

---

## REMAINING UNRESOLVABLE ITEMS (2)

---

## OA-003: JazzCash / Easypaisa Live Payment Credentials

**Category:** Commercial / Vendor Relationship
**Blocks:** Live payment collection at C6 launch

**Why unresolvable from repository:**
The backend adapters are fully implemented. `render.yaml` has JAZZCASH_STUB_MODE=true and EASYPAISA_STUB_MODE=true. The STUB flags exist precisely because the merchant credentials do not exist in the repository. Obtaining credentials requires:
1. Registered business entity (SECP-registered company or individual NTN)
2. Merchant account application to JazzCash (HBL Konnect partner program) — typically 2–4 weeks
3. Merchant account application to Easypaisa (Telenor Pakistan) — typically 2–4 weeks
4. Sandbox credential testing + approval
5. Production credential issuance

No code analysis can produce these. This is a business relationship / commercial action.

**Evidence reviewed and exhausted:**
- `render.yaml` lines 40–43: JAZZCASH_STUB_MODE=true, EASYPAISA_STUB_MODE=true confirmed
- `backend/adapters/pakistan/payments/jazzcash.py`: stub adapter returns mock response
- `backend/adapters/pakistan/payments/easypaisa.py`: stub adapter returns mock response
- `backend/src/billing/`: billing module complete, all downstream calls are stubs
- No credentials file, no `.env.payments`, no sandbox key anywhere in repo
- Phase 3.25 scan: grep for credentials, keys, merchant IDs — all return null

**Why repository cannot determine:** Vendor credential acquisition is a business relationship/commercial action, not a code decision.

**What happens at C6 launch without resolution:**
- G-04 (billing-settings.html) operates in stub mode — payment forms submit but return mock success
- P-016 constraint remains active — payment confirmation is stub
- Revenue collection is blocked
- Free-tier CRM launch is viable (contacts, leads, deals, communications all functional)

**Frontend impact:** None — G-04 is already built for stub state per FG-003.

**Recommended owner action:**
Apply for JazzCash and Easypaisa merchant accounts immediately. Sandbox testing can begin as soon as sandbox credentials are received. Switch STUB flags to false + set real credentials in render.yaml environment once sandbox testing passes.

**Priority:** P1 — commercial launch blocker for paid subscriptions

---

## G-MED-005: Urdu WhatsApp Template Approval (P-017)

**Category:** Content / Human Linguistic Review
**Blocks:** Urdu-language WhatsApp campaign launch

**Why unresolvable from repository:**
The Urdu strings exist in the codebase with `<!-- UR_TODO: -->` markers. The strings were written programmatically. Verifying that they are:
1. Linguistically correct (grammar, idiom)
2. Culturally appropriate for Pakistani B2B users
3. Compliant with WhatsApp's Urdu message guidelines
4. PTA-compliant for commercial messages

...requires a human Urdu native speaker with knowledge of Pakistani B2B communication norms. No code analysis can substitute for this review.

**Evidence reviewed and exhausted:**
- `frontend/src/app/notifications.html` (G-06): confirmed English strings only
- RTL CSS infrastructure: built and confirmed
- Urdu string placeholders: exist in code with `_STRINGS['ur']` pattern + `<!-- UR_TODO: -->` markers
- WhatsApp compliance adapter: hooks built in `adapters/pakistan/messaging/`
- No native speaker review has occurred; no approved Urdu string set exists in docs/
- Phase 3.25 scan: no automated Urdu language validation tool found in codebase

**Why repository cannot determine:** Human Urdu native speaker required. This is a linguistic/compliance decision, not a technical question.

**What happens without resolution:**
- WhatsApp campaigns targeting Urdu speakers remain blocked
- English campaigns are fully functional
- P-017 constraint remains active in AI_OPERATING_CONTEXT.md
- G-06 (notifications.html) shows only English templates

**Frontend impact:** Partial — Urdu notification templates hidden in G-06 until approved.

**Recommended owner action:**
Engage a Urdu-speaking member of the team or a professional translator to review all `_STRINGS['ur']` values. After approval, mark P-017 as resolved and remove the `<!-- UR_TODO: -->` markers.

**Priority:** P2 — blocks Urdu campaign activation only; not a general launch blocker

---

## Summary

| ID | Category | Status | C6 Launch Impact | Action Required |
|----|----------|--------|-----------------|-----------------|
| D-002 | Product scope | CLOSED (Phase 3.25) | K-02 advisory shell confirmed | None |
| OA-003 | Vendor credentials | UNRESOLVABLE | Blocks payment revenue | Apply for merchant accounts |
| G-MED-005 | Linguistic review | UNRESOLVABLE | Blocks Urdu campaigns | Native Urdu speaker review |

**Frontend Authority Capture is NOT blocked by any remaining unresolvable item.**

---

*End UNRESOLVABLE_ITEMS_REGISTER.md — Updated Phase 3.25 (2026-06-23)*
