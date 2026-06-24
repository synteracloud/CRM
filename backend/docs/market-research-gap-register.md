# Market Research Gap Register

**Source:** `pakistan_crm_market_report_manus.md` — P-034 overlay (2026-04-09)
**Purpose:** Gaps identified from Manus AI market research that are not covered in `CRM Build.md`, `Behaviour.md`, or any existing system docs. These represent real Pakistan market signals that the current build does not yet address.

---

## Gap Summary

| ID | Feature | Priority | Build complexity |
|---|---|---|---|
| MR-001 | Facebook / Instagram lead capture automation | High | Medium |
| MR-002 | One-click invoice + WhatsApp payment link send | High | Medium |
| MR-003 | Voice note transcription (Urdu / Roman Urdu / English) | Medium | High |
| MR-004 | Automated daily WhatsApp activity summary to managers | Medium | Low |
| MR-005 | Excel import / export for contacts and leads | Medium | Low |
| MR-006 | Geo-tagging / field check-in for field reps | Low | Medium |
| MR-007 | Kuickpay payment gateway adapter | Low | Low (after P-016) |

---

## Detailed Gap Entries

### MR-001 — Facebook / Instagram Lead Capture Automation

**Source:** Manus report §7 (Execution Gaps), §8 (Opportunity Zones), §9 feature #3
**Market signal:** Leads generated from Facebook/Instagram ads are manually transferred to Excel — the most common point of data leakage for Pakistan SMEs.
**Current state:** System supports WhatsApp inbound lead capture. No Facebook Lead Ads webhook or Instagram DM integration exists.
**What to build:**
- Facebook Lead Ads webhook integration — when a form is submitted on a Facebook/Instagram ad, auto-create a `Lead` in the system
- Map FB Lead Ads fields → `Lead.contact_name`, `Lead.normalized_phone`, `Lead.source = "facebook_lead_ads"`
- Extend `adapters/interfaces/messaging_adapter.py` for Facebook Lead Ads source
- Document in `docs/integration-contracts.md`
**Blocked by:** Facebook Lead Ads API access (requires Meta Business Manager setup by user)

---

### MR-002 — One-Click Invoice + WhatsApp Payment Link

**Source:** Manus report §8 (Opportunity Zones — "One-Click Invoicing via WhatsApp"), §9 feature #5
**Market signal:** Most critical cash flow acceleration feature. Businesses send PDF invoices — customers don't act. An embedded payment link sent via WhatsApp converts faster.
**Current state:** Invoice generation exists (`services/collections/service.py`). WhatsApp messaging exists. There is no flow that: generates invoice → creates payment link → sends via WhatsApp in one action.
**What to build:**
- `POST /api/v1/invoices/:id/send-whatsapp` — generates invoice, creates JazzCash/Easypaisa payment link, sends via WhatsApp template message
- Payment link creation requires P-016 (JazzCash/Easypaisa credentials) to be unblocked
- WhatsApp template: `invoice.send_whatsapp` (add to i18n registry in EN + UR)
- Document in `docs/collections-engine-model.md` as payment request flow
**Blocked by:** P-016 (payment credentials) and WhatsApp template approval (Meta)

---

### MR-003 — Voice Note Transcription (Urdu / Roman Urdu / English)

**Source:** Manus report §9 feature #8
**Market signal:** Voice notes are heavily used in Pakistan business WhatsApp. Not transcribed = not searchable, not actionable in CRM.
**Current state:** Zero coverage — not in spec, not in code, not in docs.
**What to build:**
- Inbound WhatsApp voice note → transcription service call → text stored as `Message.body` alongside audio attachment
- Transcription languages: `ur`, `en`, Roman Urdu (treat as `ur` with Latin script fallback)
- Transcription provider: external API (e.g., Google Speech-to-Text, AssemblyAI, OpenAI Whisper) — new adapter needed
- Extend `adapters/interfaces/messaging_adapter.py` with `transcribe_voice_note()` protocol method
- Transcribed text feeds into `services/conversation/intent.py` classify pipeline
**Blocked by:** Transcription API provider selection + credentials; significant build effort; no ML/AI infra currently in system

---

### MR-004 — Automated Daily WhatsApp Activity Summary to Managers

**Source:** Manus report §9 feature #11; `CRM_EXECUTION_OS_SPEC_v1_ADDENDUM §5` (Activity Transparency + Alerts)
**Market signal:** Managers want daily summaries delivered via WhatsApp — not via dashboard login. Fits existing behavior.
**Current state:** Activity monitoring exists (`services/activity/monitor/`). Notification system exists (`db/notification_db/`). No scheduled WhatsApp summary job exists.
**What to build:**
- Scheduled job (cron or `services/core/execution/scheduler`) — runs daily at configurable time per tenant
- Aggregates: leads captured today, follow-ups completed, follow-ups missed, payments recorded, escalations active
- Formats as WhatsApp template message and sends via messaging adapter to tenant owner's number
- Add i18n key: `notification.daily_summary` (EN + UR)
- Add to `docs/scheduler-jobs.md` as scheduled job entry
**Not blocked** — buildable without P-016 (uses WhatsApp, not payment)

---

### MR-005 — Excel Import / Export for Contacts and Leads

**Source:** Manus report §9 feature #12; §6 (Onboarding Issues — data migration from Excel)
**Market signal:** Every SME onboarding has existing data in Excel. Without import, adoption is blocked. Export is required for "data portability" trust.
**Current state:** No import or export functionality exists anywhere in the system.
**What to build:**
- `POST /api/v1/contacts/import` — accept `.xlsx` / `.csv`, map columns to `Contact` entity, validate, batch-create
- `GET /api/v1/contacts/export` — export all tenant contacts as `.csv`
- `POST /api/v1/leads/import` — same for leads
- `GET /api/v1/leads/export` — same for leads
- Column mapping UI in onboarding wizard (b9-p11 §2.6 Tenant Activation Onboarding)
- Dedup check during import (phone-exact + fuzzy name match if flag enabled)
**Not blocked** — buildable independently

---

### MR-006 — Geo-Tagging / Field Check-In for Field Reps

**Source:** Manus report §9 feature #13
**Market signal:** FMCG, Real Estate, Pharma field teams. Managers want to verify reps are actually visiting clients.
**Current state:** Zero coverage. Not in spec or system.
**What to build:**
- `POST /api/v1/activity/check-in` — accepts GPS coordinates + optional account_id/contact_id
- Stores as `ActivityEvent` with `event_type = "field_check_in"`, lat/lng in metadata
- Map view on manager dashboard: pins for today's check-ins per rep
- Mobile-first: single tap from Lead detail → check-in with auto-location
**Priority:** Low — relevant for FMCG/Real Estate verticals specifically; not core to initial launch
**Not blocked** — requires mobile GPS permission (browser/app)

---

### MR-007 — Kuickpay Payment Gateway Adapter

**Source:** Manus report §9 feature #6 (mentions "Kuickpay" alongside Easypaisa, JazzCash)
**Market signal:** Kuickpay is a Pakistani payment gateway used for utility bill payments and B2B collections in certain sectors.
**Current state:** JazzCash + Easypaisa adapters exist (`adapters/pakistan/payments/`). Kuickpay not present.
**What to build:**
- `adapters/pakistan/payments/kuickpay.py` — implements `PaymentAdapter` interface
- Same pattern as `jazzcash.py` and `easypaisa.py` — HMAC auth, normalize transaction
- Add to `adapters/pakistan/bootstrap/registry.py` conditional on `KUICKPAY_ENABLED` env var
**Blocked by:** Kuickpay API documentation + sandbox credentials (similar to P-016)
**Priority:** Low — after P-016 is unblocked and JazzCash/Easypaisa are live

---

## What P-033 Found (CRM_EXECUTION_OS_SPEC_v1 + ADDENDUM)

**Result: No new gaps.** The CRM Execution OS Spec v1 and its Pakistan Wedge Addendum are the original design briefs that became `CRM Build.md` and `Behaviour.md` respectively. All 15 spec sections and all 14 addendum sections are fully implemented in the current system:

| Spec section | System coverage |
|---|---|
| Core Engines (6) | All 6 built — WhatsApp, Followup, Collections, Activity, Activation, Control Plane |
| Domain Capabilities (10) | All 10 built |
| Execution Model | Built — enforcement ramp-up, idle thresholds, mandatory ownership |
| WhatsApp-first | Built — primary interaction layer |
| Collections lifecycle | Built — invoice → payment → reminder → reconciliation |
| Hardening | Built — idempotency, retry, transactions, rate limiting, logging |
| Integration flows | Built — all 4 end-to-end flows |
| Data integrity | Built — dedup, orphan prevention, offline consistency |
| Extensibility | Built — adapter pattern for countries and providers |
| Pakistan Wedge addendum | Built — behavioral principles, trust layer, hybrid payments, time-to-value |

The spec documents are the system — no delta exists.
