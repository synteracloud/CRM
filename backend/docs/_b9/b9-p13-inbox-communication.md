# B9-P13::INBOX_COMMUNICATION_THREAD

## Scope

Defines the **Inbox / Communication Thread** archetype — 3 named communication surfaces.
Anchored to `docs/adapters/whatsapp-execution-model.md`, `docs/adapters/pakistan-adapter-architecture.md`, `docs/domain/shared-inbox.md`, `adapters/pakistan/messaging/`.

**Key entities** (from `shared-inbox.md`):
- `InboxQueue` — tenant-scoped queue (`routing_strategy`: `round_robin` / `least_loaded` / `claim_first` / `skill_based`; `auto_assign` flag; `team_id` scope)
- `AgentPresence` — per-agent availability (`status`: `online` / `away` / `busy` / `offline`; `max_concurrent` open conversations)
- `ConversationHandoff` — immutable handoff audit record (from_agent, to_agent, reason, note, triggered_at)
- `Conversation` extended fields: `assigned_agent_id`, `queue_id`, `assignment_reason`, `handoff_count`

**Assignment invariant** (from `shared-inbox.md §1.2`): Every conversation has exactly one active assigned agent. Reassignment is atomic — old agent loses write access the moment new agent is assigned. Unassigned conversations are visible to all agents in pool and claimable by any.

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
- Inbound messages classified by `ConversationalCRMService` → `InboxQueue` routing strategy determines assignment
- Queue routing strategies: `round_robin` / `least_loaded` / `claim_first` (agent-initiated claim) / `skill_based`
- If `auto_assign = false`: conversation enters pool as unassigned; agents claim via `[Claim]` button
- If `auto_assign = true`: system assigns to eligible agent per routing strategy
- Agent eligibility: `AgentPresence.status IN (online, away)` AND `open_conversation_count < max_concurrent`
- Manual reassignment via `[Reassign]` on thread header — creates `ConversationHandoff` record
- Unrouted threads show in "Unassigned" bucket; visible to all pool agents and supervisor

---

### 2.2 — Conversation Thread (L-02)

**Route:** `/app/inbox/:thread_id`
**Channel-specific rendering:** thread view adapts to `MessageThread.channel` — email threads render email-style; WhatsApp threads render bubble-style. Single route, channel-aware component.

#### Email threads (`channel = email`)

**Route pattern:** `/app/inbox/:thread_id` (where `MessageThread.channel = email`)
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

#### WhatsApp / Messaging threads (`channel = whatsapp`)

**Route pattern:** `/app/inbox/:thread_id` (where `MessageThread.channel = whatsapp`)
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

### 2.3 — Routing Configuration (L-03)

**Route:** `/app/admin/routing`
**Role gate:** `tenant_admin`, `sales_manager`
**Source entities:** `InboxQueue`, `AgentPresence`, `Team`
**Entity contract:** `docs/domain/shared-inbox.md`

**Purpose:** Configure inbox queues, routing strategies, and agent availability defaults.

**Sections:**
1. **Queue management** — create/edit `InboxQueue` records. Set `routing_strategy`, `auto_assign` flag, `team_id` scope, `skill_tags` for skill-based routing.
2. **Agent capacity** — per-agent `max_concurrent` open conversations. Default: 10. Override per agent.
3. **Routing rules** — conditions that route an inbound conversation to a specific queue (e.g., keyword match → billing queue; contact.account_tier = enterprise → VIP queue).
4. **Fallback config** — what happens when no rule matches: default queue name, default assignment, overflow behaviour.

**Design rule:** Changes to routing config take effect immediately for new conversations; active conversations are not rerouted.

---

## 3) Interaction Patterns

1. **Unified compose:** Same compose bar pattern across all channels — only template picker and attachment options differ.
2. **No page churn on thread switch:** Selecting a thread in the left pane updates the right pane — no full navigation.
3. **Intent-driven actions:** Intent badge click offers contextual next action (not just classification label).
4. **Quick context from thread:** Clicking the customer context strip opens the entity detail view in a slide-over — no navigation away.
5. **Offline compose queue:** Messages composed offline are queued in `OfflineAction` and sent when reconnected. `buildOfflineIndicator()` shows pending count.
6. **RTL support:** When `locale=ur`, compose bar input switches to RTL, thread bubbles align correctly, template text renders in Urdu.

---

## 4) API Routes

All endpoints below exist in `backend/gateway/routes/v1-inbox.routes.js`. No backend work needed before building L-01 or L-02.

### L-01 — Omnichannel Inbox (page load)

| Endpoint | Method | Scope | CRM_API call | Notes |
|---|---|---|---|---|
| `/inbox/conversations` | GET | `inbox.read` | `CRM_API.inbox.conversations.list({ limit:50 })` | Returns `MessageThread[]` sorted by last_message_at DESC |
| `/inbox/presence` | GET | `inbox.read` | `CRM_API.inbox.presence.list()` | Returns agent presence status array |
| `/inbox/queues` | GET | `inbox.read` | `CRM_API.inbox.queues.list()` | Returns queue names for filter chips |

### L-01 — Omnichannel Inbox (user actions)

| Endpoint | Method | Scope | CRM_API call | Trigger |
|---|---|---|---|---|
| `/inbox/conversations/:id/claim` | POST | `inbox.write` | `CRM_API.inbox.conversations.claim(id)` | `[Claim]` button on unassigned thread |
| `/inbox/conversations/:id/handoff` | POST | `inbox.write` | `CRM_API.inbox.conversations.handoff(id, { to_agent_id, reason })` | `[Reassign]` on thread header |
| `/inbox/conversations/:id/messages` | POST | `inbox.write` | `CRM_API.inbox.conversations.sendMessage(id, text)` | Compose bar `[Send]` |
| `/inbox/presence` | PATCH | `inbox.write` | `CRM_API.inbox.presence.update(status)` | Presence status toggle |

### L-02 — Conversation Thread (page load)

| Endpoint | Method | Scope | CRM_API call | Notes |
|---|---|---|---|---|
| `/inbox/conversations/:id` | GET | `inbox.read` | `CRM_API.inbox.conversations.get(id)` | Thread ID from URL param `?id=` |

### L-02 — Conversation Thread (user actions)

| Endpoint | Method | CRM_API call | Trigger |
|---|---|---|---|
| `/inbox/conversations/:id/messages` | POST | `CRM_API.inbox.conversations.sendMessage(id, text)` | Compose bar `[Send]` |
| `/inbox/conversations/:id/handoff` | POST | `CRM_API.inbox.conversations.handoff(id, body)` | `[Reassign]` / `[Close]` |

### MessageThread entity shape (from `v1-inbox.routes.js`)

| Field | Type | Notes |
|---|---|---|
| `conversation_id` | string | PK |
| `contact_name` | string | Display name |
| `contact_phone` | string | E.164 |
| `channel` | enum | `whatsapp` / `email` / `sms` |
| `status` | enum | `open` / `assigned` / `closed` |
| `assigned_agent_id` | string? | Null = unassigned |
| `queue_id` | string? | Routing queue |
| `last_message_preview` | string | 80-char truncation |
| `last_message_at` | ISO-8601 | Sort key |
| `unread_count` | number | Badge |
| `intent` | string | Classifier output |

---

## SELF-QC

- **All DESIGN-SPEC.md L-series pages documented:** ✅ — L-01/L-02/L-03 all defined (2026-05-28 update added L-03; L-02 route unified to `/app/inbox/:thread_id`)
- **shared-inbox.md entities integrated:** ✅ — InboxQueue, AgentPresence, ConversationHandoff, assignment invariants
- **L-02 route conflict resolved:** ✅ — single `/app/inbox/:thread_id` route with channel-aware rendering (was split into email/:id and whatsapp/:id)
- **Anti-lead-loss integration documented:** ✅ — banner + one-tap lead creation
- **Intent classification integration documented:** ✅ — badge + contextual actions
- **RTL layout documented:** ✅ — `isRtl()` applied
- **Delivery status icons defined for all channels:** ✅
- **Offline compose queue cross-referenced:** ✅
- **API routes section added (§4) for L-01 and L-02:** ✅ — all inbox endpoints documented, all exist in `v1-inbox.routes.js`, no backend work needed (2026-05-30)
- **MessageThread entity shape documented in §4:** ✅

Score: **10/10**
