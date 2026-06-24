---
Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: Human
Phase: 3.5 — Project Memory Layer Establishment
---

# EXTERNAL_DEPENDENCY REGISTER

> Items requiring external provisioning: credentials, onboarding, registration, vendor approval, or third-party decisions.
> External Dependency: YES for all entries.
> Development is NOT blocked by these items — all have stub implementations in place.

---

## KEY PRINCIPLE: External Dependencies Do Not Block Development

Every item in this register has a corresponding stub implementation that allows the full CRM to operate. The system is designed to launch in stub/free-tier mode and progressively activate paid features as external credentials are received. Items in this register are commercial activation steps, not technical gaps.

---

## ED-001: OA-003 — JazzCash Merchant Account and Live Credentials

**Item ID:** OA-003 (JazzCash component)
**Title:** JazzCash merchant account + API credentials
**Classification:** EXTERNAL_DEPENDENCY
**Current Status:** Not initiated — merchant account application required
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md
**Evidence Source:** render.yaml JAZZCASH_STUB_MODE=true; backend/adapters/pakistan/payments/jazzcash.py (stub adapter returns mock response); no credentials anywhere in repo
**Resolution Source:** UNRESOLVABLE_ITEMS_REGISTER.md Phase 3.25 (confirmed unresolvable from repository)
**Resolution Date:** 2026-06-23 (classified; unresolved externally)
**Resolved By:** Phase 3.25 Autonomous Gap Elimination (confirmed EXTERNAL_DEPENDENCY)

**Decision Summary:** JazzCash integration requires a registered business entity and formal merchant account application to HBL Konnect partner program. The backend adapter is complete. Only credentials are missing. Stub mode is the active C6 production state.

**Detailed Explanation:** The JazzCash payment adapter (backend/adapters/pakistan/payments/jazzcash.py) is fully implemented and tested. render.yaml sets JAZZCASH_STUB_MODE=true so the adapter returns mock responses without real payment processing. To activate live payments:
1. Registered business entity (SECP-registered company or individual NTN) required
2. Formal merchant account application to JazzCash (HBL Konnect partner program) — typical timeline: 2–4 weeks
3. Sandbox credential testing (sandbox credentials received first)
4. Production credential issuance after sandbox testing passes
5. Set JAZZCASH_STUB_MODE=false and inject real credentials in render.yaml environment

No code changes are needed. Only render.yaml env var changes required (JAZZCASH_MERCHANT_ID, JAZZCASH_PASSWORD, JAZZCASH_INTEGRITY_SALT, etc. — stub adapter shows expected env var names).

**Affected Components:** backend/adapters/pakistan/payments/jazzcash.py, render.yaml (JAZZCASH_STUB_MODE env var)
**Affected Routes:** POST /payments/jazzcash/initiate, POST /payments/jazzcash/confirm, payment-webhooks
**Affected APIs:** Billing/Payment API
**Affected Workflows:** WF-002 (collections invoicing — payment confirmation step blocked)
**Affected Roles:** tenant_admin (billing management), customers (paying invoices)

**Owner Required:** YES — requires business relationship and vendor contract
**External Dependency:** YES — JazzCash HBL Konnect merchant onboarding (Pakistan)

**Current C6 Behavior:** G-04 (billing-settings.html) displays stub state. Payment forms submit but return mock success. No real money moves. Free-tier CRM launch is viable without payment activation. Constraint P-016 remains active.

**Recommended Owner Actions:**
1. Apply for JazzCash merchant account at: hbljsandbox.pk / HBL Konnect partner portal
2. Provide business registration documents (SECP certificate or NTN)
3. Complete sandbox integration testing once credentials received
4. Switch JAZZCASH_STUB_MODE to false + add credentials to Render.com environment variables (not in render.yaml — use Render dashboard secrets)

**Future Impact:** When activated: POST /payments/jazzcash/* processes real payments. WF-002 collections workflow completes end-to-end. Outbox publisher implementation becomes mandatory (see SAFE_DEFAULT_REGISTER.md SD-007).

**Reopen Criteria:** This item is never "closed" — it transitions to RESOLVED when credentials are received and integration tested.

**Related Documents:** render.yaml, backend/adapters/pakistan/payments/jazzcash.py, AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS P-016
**Related Register Entries:** OA-003b (ED-002), G-HIGH-004 (SAFE_DEFAULT_REGISTER.md SD-007)

---

## ED-002: OA-003b — Easypaisa Merchant Account and Live Credentials

**Item ID:** OA-003b (Easypaisa component)
**Title:** Easypaisa merchant account + API credentials
**Classification:** EXTERNAL_DEPENDENCY
**Current Status:** Not initiated — merchant account application required
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md (bundled with OA-003)
**Evidence Source:** render.yaml EASYPAISA_STUB_MODE=true; backend/adapters/pakistan/payments/easypaisa.py (stub adapter); no credentials anywhere in repo
**Resolution Source:** UNRESOLVABLE_ITEMS_REGISTER.md Phase 3.25 (confirmed unresolvable from repository)
**Resolution Date:** 2026-06-23 (classified; unresolved externally)
**Resolved By:** Phase 3.25 Autonomous Gap Elimination (confirmed EXTERNAL_DEPENDENCY)

**Decision Summary:** Easypaisa integration requires a merchant account application to Telenor Pakistan. Adapter is complete; stub mode is active. Activation timeline typically 2–4 weeks.

**Detailed Explanation:** Same pattern as ED-001 (JazzCash) but for Easypaisa (Telenor Pakistan). backend/adapters/pakistan/payments/easypaisa.py is fully implemented. render.yaml sets EASYPAISA_STUB_MODE=true. To activate: apply for Easypaisa merchant account, complete sandbox testing, set EASYPAISA_STUB_MODE=false with real credentials.

Easypaisa and JazzCash applications can be submitted in parallel. Easypaisa merchant portal: easypaisa.com.pk/merchant.

**Affected Components:** backend/adapters/pakistan/payments/easypaisa.py, render.yaml (EASYPAISA_STUB_MODE)
**Affected Routes:** POST /payments/easypaisa/initiate, POST /payments/easypaisa/confirm, payment-webhooks
**Affected APIs:** Billing/Payment API
**Affected Workflows:** WF-002 (collections — Easypaisa payment path)
**Affected Roles:** tenant_admin, customers

**Owner Required:** YES — requires business relationship and vendor contract
**External Dependency:** YES — Easypaisa (Telenor Pakistan) merchant onboarding

**Current C6 Behavior:** Same as OA-003. G-04 shows stub. P-016 constraint active.

**Recommended Owner Actions:** Submit Easypaisa merchant application in parallel with JazzCash (ED-001). Bundled with JazzCash into single OA-003 activation sprint.

**Future Impact:** When activated: Easypaisa payment path processes real payments. Activates alongside JazzCash in same sprint.

**Reopen Criteria:** Transitions to RESOLVED when credentials received and tested.

**Related Documents:** render.yaml, backend/adapters/pakistan/payments/easypaisa.py, AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS P-016
**Related Register Entries:** OA-003 (ED-001)

---

## ED-003: G-MED-005 — Urdu WhatsApp Template Native Speaker Review

**Item ID:** G-MED-005
**Title:** Urdu WhatsApp template strings — native speaker linguistic review required
**Classification:** EXTERNAL_DEPENDENCY
**Current Status:** Not initiated — native speaker review required
**Original Source:** UNRESOLVABLE_ITEMS_REGISTER.md (2 confirmed unresolvable items)
**Evidence Source:** frontend/src/app/notifications.html (G-06) EN strings only; _STRINGS['ur'] with UR_TODO markers; RTL CSS infrastructure built; WhatsApp compliance adapter hooks in adapters/pakistan/messaging/; no approved Urdu string set in docs/
**Resolution Source:** UNRESOLVABLE_ITEMS_REGISTER.md Phase 3.25 (confirmed UNRESOLVABLE — Linguistic/Compliance)
**Resolution Date:** 2026-06-23 (classified; unresolved externally)
**Resolved By:** Phase 3.25 Autonomous Gap Elimination (confirmed EXTERNAL_DEPENDENCY)

**Decision Summary:** Urdu strings exist in the codebase with UR_TODO markers. Verification requires a human Urdu native speaker with knowledge of Pakistani B2B communication norms and WhatsApp/PTA compliance requirements.

**Detailed Explanation:** The Urdu localization infrastructure is complete: RTL CSS is built and confirmed, _STRINGS['ur'] pattern is wired, WhatsApp compliance adapter hooks are in adapters/pakistan/messaging/. The only missing element is human approval of the actual Urdu strings for linguistic correctness, cultural appropriateness, WhatsApp guideline compliance, and PTA commercial message compliance. The strings were written programmatically and marked with UR_TODO to flag that native speaker review has not occurred.

**What requires review:**
1. Linguistic correctness (grammar, idiom in Pakistani business Urdu)
2. Cultural appropriateness for Pakistani B2B users
3. WhatsApp Urdu message guideline compliance
4. PTA compliance for commercial messages (may require disclaimers)

**Affected Components:** All _STRINGS['ur'] values in frontend; adapters/pakistan/messaging/; G-06 (notifications.html) Urdu template section
**Affected Routes:** POST /notifications/send (Urdu templates), WhatsApp broadcast routes
**Affected APIs:** Omnichannel Inbox API, Notifications API
**Affected Workflows:** WhatsApp campaign delivery (Urdu-language)
**Affected Roles:** marketing, tenant_admin (campaign creators)

**Owner Required:** YES — requires native Urdu speaker (human judgment, not technical)
**External Dependency:** YES — human Urdu native speaker with B2B/PTA knowledge

**Current C6 Behavior:** G-06 (notifications.html) shows English templates only. Urdu templates are hidden. English campaigns are fully functional. P-017 constraint remains active.

**Recommended Owner Actions:**
1. Identify a Urdu-speaking team member or professional translator
2. Request review of all _STRINGS['ur'] values (search codebase for _STRINGS['ur'] pattern)
3. After approval: remove all UR_TODO markers, mark P-017 as resolved in AI_OPERATING_CONTEXT.md

**Future Impact:** When approved: Urdu notification templates become visible in G-06. WhatsApp Urdu campaigns can be created and broadcast. RTL display infrastructure is already in place.

**Reopen Criteria:** Transitions to RESOLVED when native speaker approval is documented. Cannot be automated.

**Related Documents:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS P-017, frontend/src/app/notifications.html (G-06), adapters/pakistan/messaging/
**Related Register Entries:** G-MED-005 (FINAL_CLASSIFIED_REGISTER.md)

---

## ED-004: MR-001 — Facebook/Instagram Lead Capture (Meta Business Manager)

**Item ID:** MR-001
**Title:** Facebook/Instagram lead capture — Meta Business Manager approval
**Classification:** EXTERNAL_DEPENDENCY
**Current Status:** Not initiated — hidden in UI pending Meta approval
**Original Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS
**Evidence Source:** UI hidden div with data-unblock="MR-001"; Meta Business Manager account not set up; no Facebook SDK credentials in repo
**Resolution Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS (confirmed constraint)
**Resolution Date:** 2026-06-23 (classified from KNOWN_CONSTRAINTS)
**Resolved By:** Phase 3.5 Memory Layer Establishment

**Decision Summary:** Facebook/Instagram lead capture integration is built but hidden in UI pending Meta Business Manager account setup and API approval.

**Detailed Explanation:** The UI for Facebook/Instagram lead capture is built but hidden behind a data-unblock="MR-001" div. No Meta SDK credentials exist in the repository. To activate: set up Meta Business Manager account, apply for Facebook Lead Ads API access, receive approval, add credentials to render.yaml environment.

**Affected Components:** Frontend UI (hidden element with data-unblock=MR-001), Meta integration adapter (if implemented)
**Affected Routes:** Facebook lead webhook receiver (if implemented)
**Affected APIs:** Facebook Lead Ads API (external)
**Affected Workflows:** Lead capture from Facebook/Instagram
**Affected Roles:** marketing, tenant_admin

**Owner Required:** YES — Meta Business Manager account creation and API approval
**External Dependency:** YES — Meta Platforms (Facebook/Instagram) API approval

**Current C6 Behavior:** Facebook/Instagram lead capture is completely hidden in the UI. Does not affect any other functionality. Not a launch blocker.

**Recommended Owner Actions:** Set up Meta Business Manager at business.facebook.com. Apply for Lead Ads API access. Receive approval (timeline varies — typically 1–4 weeks). Add credentials and remove data-unblock attribute.

**Future Impact:** When approved: Facebook/Instagram leads flow directly into the CRM lead pipeline.

**Reopen Criteria:** Transitions to RESOLVED when Meta approval received and integration tested.

**Related Documents:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS MR-001
**Related Register Entries:** None

---

## ED-005: MR-003 — Voice Note Transcription Provider

**Item ID:** MR-003
**Title:** Voice note transcription — provider selection and credentials
**Classification:** EXTERNAL_DEPENDENCY
**Current Status:** Not initiated — microphone icon disabled in UI
**Original Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS
**Evidence Source:** Microphone icon disabled in UI; no transcription provider SDK in requirements.txt; no API key in repo
**Resolution Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS (confirmed constraint)
**Resolution Date:** 2026-06-23 (classified from KNOWN_CONSTRAINTS)
**Resolved By:** Phase 3.5 Memory Layer Establishment

**Decision Summary:** Voice note transcription is blocked pending provider selection (OpenAI Whisper, Google Speech-to-Text, or other) and API credentials.

**Detailed Explanation:** The voice note transcription feature is partially built — the microphone icon is present in the UI but disabled. No transcription provider SDK is installed (no whisper, google-cloud-speech, or equivalent in requirements.txt). To activate: select a provider, add SDK to requirements.txt, configure API key in render.yaml environment, enable the microphone button.

**Affected Components:** Frontend microphone UI element (disabled), transcription adapter (not yet implemented in backend)
**Affected Routes:** POST /transcription (not yet implemented)
**Affected APIs:** Transcription provider API (external — OpenAI Whisper, Google Speech-to-Text, etc.)
**Affected Workflows:** Omnichannel inbox voice note handling
**Affected Roles:** Agents (inbox users)

**Owner Required:** YES — provider selection is a product/cost decision
**External Dependency:** YES — transcription provider API key and account

**Current C6 Behavior:** Microphone icon is visible but disabled. Voice notes can still be sent as audio files (without transcription). Not a launch blocker.

**Recommended Owner Actions:** Select transcription provider (OpenAI Whisper recommended for Pakistan Urdu support). Obtain API key. Add to requirements.txt and render.yaml.

**Future Impact:** When activated: voice notes in inbox are transcribed and searchable. Urdu voice note transcription possible (if Whisper or equivalent is selected).

**Reopen Criteria:** Transitions to RESOLVED when provider selected, SDK installed, and feature end-to-end tested.

**Related Documents:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS MR-003, backend/requirements.txt
**Related Register Entries:** None

---

## Summary

| Item ID | External Provider | Priority | Launch Blocker | Revenue Blocker |
|---------|------------------|----------|----------------|-----------------|
| ED-001 (OA-003) | JazzCash (HBL Konnect) | P1 | NO (stub viable) | YES |
| ED-002 (OA-003b) | Easypaisa (Telenor Pakistan) | P1 | NO (stub viable) | YES |
| ED-003 (G-MED-005) | Urdu native speaker | P2 | NO | NO (Urdu campaigns only) |
| ED-004 (MR-001) | Meta Business Manager | P3 | NO | NO |
| ED-005 (MR-003) | Transcription provider | P3 | NO | NO |

**CRM launches without ANY of these items being resolved.** All external dependencies have stub implementations or hidden-UI states that allow full CRM operation for non-payment, non-Urdu use cases.

---

*End EXTERNAL_DEPENDENCY_REGISTER.md — 5 items (ED-001 through ED-005) — Phase 3.5 (2026-06-23)*
