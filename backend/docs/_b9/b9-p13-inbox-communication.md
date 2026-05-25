# B9-P13::INBOX_COMMUNICATION_THREAD

## Scope

Defines the **Inbox / Communication Thread** archetype — 3 named communication surfaces.
Anchored to `docs/adapters/whatsapp-execution-model.md`, `docs/adapters/pakistan-adapter-architecture.md`, `adapters/pakistan/messaging/`.

---

## 1) Archetype Structure

Communication surfaces use a **thread list + thread view** shell:

```
┌─ Channel selector (WhatsApp / Email / SMS / All) ─────────┐
├──────────────┬────────────────────────────────────────────┤
│ Thread list  │  Active thread view                        │
│ (left pane)  │  - Message chronology (oldest at top)      │
│ - Name       │  - Compose bar (bottom)                    │
│ - Preview    │  - Delivery status per message             │
│ - Timestamp  │  - Customer context strip (top)            │
│ - Status     │                                            │
└──────────────┴────────────────────────────────────────────┘
```

**Design rules:**
- Thread list sorted by last message timestamp DESC.
- Unread threads pinned to top; bold name + unread count badge.
- Compose bar always visible at thread bottom — no scroll required to reply.
- Delivery status icons: `sent` / `delivered` / `read` / `failed` (with retry button on failed).
- RTL layout applies automatically when locale = `ur` (per `gateway/services/i18n.js` `isRtl()`).

---

## 2) The 3 Inbox / Communication Pages

### 2.1 — Omnichannel Inbox

**Route:** `/app/inbox`
**Source entities:** `MessageThread`, `Message`, `RoutingDecision`
**Source doc:** `docs/adapters/whatsapp-execution-model.md`

**Purpose:** Unified view across all inbound channels (WhatsApp, Email, SMS). Single agent surface — no channel switching required.

**Thread list columns:**
- Contact name / phone
- Channel icon (WhatsApp / Email / SMS)
- Last message preview (truncated 80 chars)
- Timestamp (relative)
- Unread badge
- Assignment status (unassigned / assigned to [agent])

**Thread view:**
- Customer context strip: contact name, phone, account, lead stage, open case count
- Chronological message history with channel icons per message
- Compose bar: text input + `[Send]` + template picker + attachment (WhatsApp only)
- Intent badge (from `services/conversation/intent.py`): `lead_inquiry` / `payment_query` / `follow_up_response` / `support_request` / `out_of_scope`

**Routing integration:**
- Inbound messages classified by `ConversationalCRMService` → `RoutingDecision` drives assignment
- Unrouted threads show in "Unassigned" bucket
- Manual reassignment via `[Assign]` on thread header

---

### 2.2 — Email Engagement Thread

**Route:** `/app/inbox/email/:thread_id`
**Source entities:** `MessageThread`, `Message` (channel = `email`)

**Purpose:** Email-specific thread view with engagement tracking (open / click / reply).

**Thread view sections:**
- Email chain (threaded conversation; collapsible quoted text)
- Engagement bar: open count, click count, last engaged timestamp
- Contact + account context (same as Omnichannel)
- Compose: full-text email composer with template insertion, CC/BCC

**Engagement indicators:**
- `opened` — eye icon + timestamp
- `clicked` — cursor icon + link clicked
- `replied` — reply icon

**Design rule:** Engagement data from `CommunicationEngagementRM.delivery_open_click_reply_rate`. Never expose raw tracking pixels or click data to end user — show only aggregated indicators.

---

### 2.3 — WhatsApp / Messaging Thread

**Route:** `/app/inbox/whatsapp/:thread_id`
**Source entities:** `MessageThread`, `Message` (channel = `whatsapp`)
**Source doc:** `docs/adapters/whatsapp-execution-model.md` §10 (intent detection) + §11 (anti-lead-loss)
**Adapters:** `adapters/pakistan/messaging/` (dialog360, gupshup, meta, twilio)

**Purpose:** WhatsApp-specific thread with full business API feature set.

**Thread view:**
- Message bubbles with WhatsApp-style delivery ticks (sent ✓ / delivered ✓✓ / read ✓✓ blue)
- Template message picker: select approved templates from adapter template library
- Media messages: image preview inline; document/audio with download
- Compose bar: text + emoji + template + attachment

**Anti-lead-loss integration:**
- When an inbound message arrives from an unknown number, a "Create lead?" banner appears with one-tap confirmation
- If contact exists: thread automatically links to existing lead/contact record
- Duplicate suggestion shown if fuzzy match finds similar contact (feature-flagged)

**Intent display:**
- Intent badge shown per inbound message (from classifier)
- `lead_inquiry` → suggest creating/updating lead
- `payment_query` → link to invoice or Collections Queue
- `support_request` → suggest opening a case

---

## 3) Interaction Patterns

1. **Unified compose:** Same compose bar pattern across all channels — only template picker and attachment options differ.
2. **No page churn on thread switch:** Selecting a thread in the left pane updates the right pane — no full navigation.
3. **Intent-driven actions:** Intent badge click offers contextual next action (not just classification label).
4. **Quick context from thread:** Clicking the customer context strip opens the entity detail view in a slide-over — no navigation away.
5. **Offline compose queue:** Messages composed offline are queued in `OfflineAction` and sent when reconnected. `buildOfflineIndicator()` shows pending count.
6. **RTL support:** When `locale=ur`, compose bar input switches to RTL, thread bubbles align correctly, template text renders in Urdu.

---

## SELF-QC

- **All 3 Archetype.md inbox pages documented:** ✅ — 2.1–2.3 match exactly.
- **Anti-lead-loss integration documented:** ✅ — banner + one-tap lead creation.
- **Intent classification integration documented:** ✅ — badge + contextual actions.
- **RTL layout documented:** ✅ — `isRtl()` applied.
- **Delivery status icons defined for all channels:** ✅
- **Offline compose queue cross-referenced:** ✅

Score: **10/10**
