<!-- OWNERSHIP
PRIMARY FOR: Campaign entity schema and state machine; segment definition and validation; message template contract; broadcast dispatch logic; delivery/open/reply rate tracking; WhatsApp opt-in/opt-out management.
DEFERS TO: whatsapp-execution-model.md (WhatsApp send execution, webhook inbound, opt-out keyword handling); pakistan-adapter-architecture.md (tone tiers, Urdu message requirements); event-catalog.md (canonical event names); activities-tasks.md (ActivityEvent logging); followup-enforcement-model.md (follow-up tasks spawned from campaign conversions).
DO NOT RE-DEFINE: WhatsApp send/receive mechanics → whatsapp-execution-model.md; tone tier definitions → pakistan-adapter-architecture.md §3.F; follow-up task lifecycle → followup-enforcement-model.md.
-->

# Marketing Campaigns Domain Spec

## Purpose

This document is the canonical backend spec for the **Marketing Campaigns Service** — the domain that handles campaign lifecycle (draft → active → completed), audience segmentation, message dispatch, delivery tracking, and conversion attribution. It is the spec counterpart to `followup-enforcement-model.md` for the marketing domain.

**Build gates:** This doc must exist before any of the following pages can be implemented: F-01 `marketing-workspace.html`, I-06 `campaign-new.html`, A-08 `engagement-dashboard.html`, H-02 `marketing-analytics.html`.

**P-017 constraint:** All Urdu message templates require native-speaker sign-off before any customer send. See `backend/PENDING.md`. Never set a campaign containing Urdu content to `active` without sign-off confirmation in `Campaign.urdu_approved_by`.

---

## 1) Core Principles

### 1.1 Campaign Contract
- A **Campaign** is a single outbound engagement unit: one audience segment, one message template, one channel, one schedule.
- Campaigns are broadcast-only in v1 — no conversational branching (that is Journey scope, Phase 6+).
- Every send is opt-in checked: contacts without `whatsapp_opted_in = true` are silently skipped for WhatsApp campaigns.
- Delivery, open, and reply rates are the primary KPIs. Conversion is attributed when a campaign contact creates or advances an Opportunity within the campaign's attribution window (default: 30 days).

### 1.2 Non-negotiable Invariants
1. A campaign cannot be activated without a `segment_id` that resolves to at least 1 eligible contact.
2. A campaign cannot be activated without a validated `template_id`.
3. WhatsApp campaigns: only contacts with `whatsapp_opted_in = true` receive messages.
4. Urdu campaigns: `Campaign.urdu_approved_by` must be set before activation.
5. All sends are idempotent — duplicate send attempts for the same `(campaign_id, contact_id)` are deduplicated via the global idempotency ledger.
6. Tenant isolation: agents can only view/action campaigns belonging to their own tenant.

---

## 2) Entity Model

### 2.1 Campaign

```
Campaign
├── campaign_id          : UUID (PK)
├── tenant_id            : str (FK → Tenant, required)
├── name                 : str (max 255)
├── description          : str (max 2,000, optional)
├── status               : CampaignStatus enum (see §3)
├── type                 : CampaignType enum (whatsapp_broadcast | email | sms)
├── segment_id           : UUID (FK → CampaignSegment, required before activation)
├── template_id          : UUID (FK → MessageTemplate, required before activation)
├── scheduled_at         : datetime (nullable — null = send immediately on activation)
├── activated_at         : datetime (nullable)
├── completed_at         : datetime (nullable)
├── paused_at            : datetime (nullable)
├── cancelled_at         : datetime (nullable)
├── attribution_window_days : int (default 30)
├── urdu_approved_by     : UUID (FK → User, nullable — required if template contains Urdu)
├── total_recipients     : int (computed on segment validation, updated on activation)
├── sent_count           : int (running total, updated per send)
├── delivered_count      : int (updated via delivery receipts)
├── opened_count         : int (updated via read receipts — WhatsApp read status)
├── replied_count        : int (updated when contact replies to campaign message)
├── opted_out_count      : int (contacts who opted out during or after this campaign)
├── leads_generated      : int (contacts who became new leads within attribution window)
├── conversions          : int (leads who closed an opportunity within attribution window)
├── created_by           : UUID (FK → User)
├── created_at           : datetime
└── updated_at           : datetime
```

### 2.2 CampaignSegment

```
CampaignSegment
├── segment_id           : UUID (PK)
├── tenant_id            : str (required)
├── name                 : str (max 255)
├── description          : str (optional)
├── entity_type          : SegmentEntityType enum (lead | contact)
├── rules                : SegmentRule[] (see §4)
├── estimated_size       : int (last computed match count)
├── last_validated_at    : datetime (nullable)
├── is_dynamic           : bool (true = re-evaluated at send time; false = frozen at creation)
├── created_by           : UUID (FK → User)
├── created_at           : datetime
└── updated_at           : datetime
```

### 2.3 MessageTemplate

```
MessageTemplate
├── template_id          : UUID (PK)
├── tenant_id            : str (required)
├── name                 : str (max 255)
├── channel              : CampaignType enum (whatsapp_broadcast | email | sms)
├── language             : str ("en" | "ur")
├── subject              : str (nullable — email only, max 255)
├── body                 : str (max 4,096 chars; supports {{contact.name}}, {{contact.company}} merge tags)
├── footer               : str (nullable — max 255; WhatsApp footer text)
├── cta_label            : str (nullable — call-to-action button label, max 20)
├── cta_url              : str (nullable — call-to-action URL)
├── meta_template_name   : str (nullable — WhatsApp Business approved template name from Meta)
├── meta_template_status : MetaTemplateStatus enum (nullable — pending | approved | rejected | paused)
├── is_urdu              : bool (derived: true if language = "ur")
├── created_by           : UUID (FK → User)
├── created_at           : datetime
└── updated_at           : datetime
```

### 2.4 CampaignSend

```
CampaignSend
├── send_id              : UUID (PK)
├── campaign_id          : UUID (FK → Campaign, required)
├── tenant_id            : str (required)
├── contact_id           : UUID (FK → Contact or Lead depending on segment entity_type)
├── contact_phone        : str (WhatsApp/SMS) or contact_email: str (Email)
├── channel              : CampaignType enum
├── status               : SendStatus enum (queued | sent | delivered | read | replied | failed | skipped)
├── skip_reason          : SkipReason enum (nullable — not_opted_in | no_channel | duplicate | opted_out)
├── sent_at              : datetime (nullable)
├── delivered_at         : datetime (nullable)
├── read_at              : datetime (nullable)
├── replied_at           : datetime (nullable)
├── failed_at            : datetime (nullable)
├── failure_reason       : str (nullable)
├── idempotency_key      : str (unique — `campaign_{campaign_id}_contact_{contact_id}`)
└── created_at           : datetime
```

### 2.5 CampaignConversion

```
CampaignConversion
├── conversion_id        : UUID (PK)
├── campaign_id          : UUID (FK → Campaign)
├── tenant_id            : str (required)
├── contact_id           : UUID
├── conversion_type      : ConversionType enum (lead_created | opportunity_created | opportunity_won)
├── entity_id            : UUID (the Lead or Opportunity created/won)
├── attributed_at        : datetime
└── created_at           : datetime
```

---

## 3) State Machine

### 3.1 CampaignStatus Enum

```
DRAFT → SCHEDULED (if scheduled_at set) → ACTIVE → COMPLETED
      → ACTIVE (if no schedule)
ACTIVE → PAUSED → ACTIVE
ACTIVE → CANCELLED
DRAFT  → CANCELLED
SCHEDULED → CANCELLED
```

| State | Meaning | Allowed transitions |
|---|---|---|
| `draft` | Being built; not yet validated or activated. | → `scheduled` (set scheduled_at + validate), → `active` (immediate send + validate), → `cancelled` |
| `scheduled` | Validated; waiting for `scheduled_at` to arrive. Scheduler job activates it. | → `active` (scheduler triggers), → `draft` (edit/reschedule), → `cancelled` |
| `active` | Sends are in progress or queued. | → `paused` (manual or rate-limit), → `completed` (all sends done) |
| `paused` | Sends halted. Queued sends not dispatched. | → `active` (resume), → `cancelled` |
| `completed` | All eligible sends dispatched. Attribution window still open. | Terminal — no transitions. Read-only. |
| `cancelled` | Campaign aborted. Queued sends discarded. | Terminal — no transitions. |

### 3.2 Transition Guards

| Transition | Guard |
|---|---|
| `draft` → `active` / `scheduled` | `segment_id` resolves to ≥1 eligible contact; `template_id` is set and `meta_template_status = approved` for WhatsApp; if Urdu template, `urdu_approved_by` is set. |
| Any → `completed` | `sent_count + skipped_count = total_recipients`. System-triggered only. |
| `active` → `paused` | Any manager/admin. Reason recorded in campaign log. |
| `paused` → `active` | Any manager/admin. Re-queues remaining sends. |

---

## 4) Segment Rules

### 4.1 SegmentRule

A segment is a boolean AND/OR tree of field conditions.

```
SegmentRule
├── rule_id     : str (unique within segment)
├── field       : str (dotted path, e.g. "lead.stage", "contact.city", "contact.tags")
├── operator    : RuleOperator enum (eq | ne | in | not_in | gt | gte | lt | lte | contains | starts_with | is_set | is_not_set)
├── value       : Any (string, number, list — depends on operator)
└── logic       : RuleLogic enum (and | or) — how this rule combines with the next
```

### 4.2 Built-in Segment Presets (Pakistan context)

| Preset name | Rule definition |
|---|---|
| `active_leads_karachi` | lead.stage IN [qualifying, negotiation] AND lead.city = "Karachi" |
| `overdue_invoices_sme` | contact.has_overdue_invoice = true AND contact.account_tier IN [SMB, Mid-Market] |
| `whatsapp_opted_in_all` | contact.whatsapp_opted_in = true |
| `high_value_pipeline` | opportunity.amount >= 100000 AND opportunity.stage NOT IN [won, lost] |
| `inactive_30_days` | lead.last_activity_at < now() - 30 days |

### 4.3 Segment Validation
- POST `/api/v1/segments/{id}/validate` — runs rules against DB, returns `estimated_size` and a sample of 5 matching contacts.
- Validation must pass before campaign activation. Result is cached as `last_validated_at`.
- If `is_dynamic = true`, segment re-validates at send time (catches opt-outs added since validation).

---

## 5) Dispatch Logic

### 5.1 Send Pipeline

On campaign activation:
```
1. Validate segment → resolve eligible contact list
2. For each contact:
   a. Check opt-in status (skip if not opted in for channel)
   b. Check idempotency ledger (skip if already sent)
   c. Resolve merge tags in template body
   d. Enqueue CampaignSend record (status = queued)
3. Set Campaign.total_recipients = eligible_count
4. Scheduler/worker processes queued sends (rate-limited: 80 msg/min for WhatsApp per Meta policy)
```

### 5.2 Rate Limiting
- WhatsApp broadcasts: max 80 messages/minute per tenant (Meta Business API tier 1 limit).
- SMS: max 200 messages/minute.
- Email: max 500 messages/minute.
- Rate limit enforced by dispatcher worker using token bucket per tenant per channel.

### 5.3 Delivery Receipt Processing
- WhatsApp delivery/read statuses arrive via inbound webhook (`POST /api/v1/webhooks/whatsapp`).
- Webhook handler matches `wamid` (WhatsApp message ID) to `CampaignSend.idempotency_key`.
- Updates `CampaignSend.status`, `delivered_at`, `read_at` accordingly.
- Increments parent `Campaign.delivered_count` / `opened_count` atomically.

### 5.4 Reply Attribution
- When an inbound WhatsApp message arrives from a contact phone number that has an `active` `CampaignSend`:
  - Set `CampaignSend.status = replied`, `replied_at = now()`.
  - Increment `Campaign.replied_count`.
  - Spawn a follow-up task (via `followup-enforcement-model.md`) for the owning agent.

### 5.5 WhatsApp Opt-Out Handling
- Customer sends "STOP" / "بند کریں" (Urdu: stop) → set `Contact.whatsapp_opted_in = false`.
- Increment `Campaign.opted_out_count` if opt-out occurred during an active campaign send.
- All future campaign sends to this contact are skipped (SkipReason = `opted_out`).
- Canonical keyword list: `whatsapp-execution-model.md §opt-out`.

---

## 6) Conversion Attribution

### 6.1 Attribution Window
- Default: 30 days from `CampaignSend.sent_at`.
- Configurable per campaign via `Campaign.attribution_window_days`.

### 6.2 Attribution Logic
A conversion is attributed when:
1. A contact who received a campaign send (`status != skipped`) creates a new Lead → `ConversionType = lead_created`.
2. A contact who received a campaign send creates a new Opportunity → `ConversionType = opportunity_created`.
3. An Opportunity linked to such a contact moves to `won` within the attribution window → `ConversionType = opportunity_won`.

Attribution is **last-touch**: if the same contact was in multiple campaigns, the most recent non-skipped send is credited.

---

## 7) API Endpoints

### Campaigns Resource

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/campaigns` | JWT | `manager`, `admin` | Create draft campaign. |
| `GET` | `/api/v1/campaigns` | JWT | Any | List campaigns (tenant-scoped). |
| `GET` | `/api/v1/campaigns/{id}` | JWT | Any | Campaign detail with send stats. |
| `PATCH` | `/api/v1/campaigns/{id}` | JWT | `manager`, `admin` | Update draft campaign fields. |
| `POST` | `/api/v1/campaigns/{id}/activate` | JWT | `manager`, `admin` | Activate (validate → enqueue sends). |
| `POST` | `/api/v1/campaigns/{id}/pause` | JWT | `manager`, `admin` | Pause active campaign. |
| `POST` | `/api/v1/campaigns/{id}/resume` | JWT | `manager`, `admin` | Resume paused campaign. |
| `POST` | `/api/v1/campaigns/{id}/cancel` | JWT | `manager`, `admin` | Cancel campaign. |
| `GET` | `/api/v1/campaigns/{id}/sends` | JWT | `manager`, `admin` | List individual sends with status. |
| `GET` | `/api/v1/campaigns/{id}/conversions` | JWT | `manager`, `admin` | List attributed conversions. |

### Segments Resource

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/segments` | JWT | `manager`, `admin` | Create segment with rules. |
| `GET` | `/api/v1/segments` | JWT | Any | List segments. |
| `GET` | `/api/v1/segments/{id}` | JWT | Any | Segment detail. |
| `PATCH` | `/api/v1/segments/{id}` | JWT | `manager`, `admin` | Update segment rules. |
| `POST` | `/api/v1/segments/{id}/validate` | JWT | `manager`, `admin` | Validate rules; return estimated_size + sample. |

### Message Templates Resource

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/templates` | JWT | `manager`, `admin` | Create message template. |
| `GET` | `/api/v1/templates` | JWT | Any | List templates. |
| `GET` | `/api/v1/templates/{id}` | JWT | Any | Template detail. |
| `PATCH` | `/api/v1/templates/{id}` | JWT | `manager`, `admin` | Update template. |

---

## 8) RBAC Role Gates

| Operation | `sales_rep` | `agent` | `manager` | `admin` |
|---|---|---|---|---|
| View campaigns | ✓ | ✓ | ✓ | ✓ |
| Create / edit campaign | — | — | ✓ | ✓ |
| Activate / pause / cancel | — | — | ✓ | ✓ |
| View sends + conversions | — | — | ✓ | ✓ |
| Create / edit segments | — | — | ✓ | ✓ |
| Create / edit templates | — | — | ✓ | ✓ |

---

## 9) Events Emitted

| Event | Trigger |
|---|---|
| `campaign.created` | Campaign created. |
| `campaign.activated` | Status → active. |
| `campaign.paused` | Status → paused. |
| `campaign.completed` | All sends dispatched. |
| `campaign.cancelled` | Status → cancelled. |
| `campaign.send.queued` | CampaignSend enqueued (per contact). |
| `campaign.send.delivered` | Delivery receipt received. |
| `campaign.send.read` | Read receipt received. |
| `campaign.send.replied` | Inbound reply matched to campaign send. |
| `campaign.send.failed` | Send failed after retries. |
| `campaign.conversion.attributed` | Conversion attributed to campaign. |
| `contact.opted_out` | Contact opts out via STOP keyword during campaign. |

---

## 10) Scanner Jobs

### 10.1 Campaign Scheduler Job
- **Schedule:** Every 1 minute.
- **Action:** Query `Campaign WHERE status = scheduled AND scheduled_at <= now()`. Activate each: run segment validation, enqueue sends, set `status = active`, `activated_at = now()`.

### 10.2 Conversion Attribution Job
- **Schedule:** Every 15 minutes.
- **Action:** For all `active` and `completed` campaigns within attribution window: check for new Leads/Opportunities linked to campaign recipients. Create `CampaignConversion` records; update `Campaign.leads_generated` and `Campaign.conversions`.

### 10.3 Campaign Completion Job
- **Schedule:** Every 5 minutes.
- **Action:** Query `Campaign WHERE status = active`. For each: if `sent_count + skipped_count + failed_count = total_recipients` → set `status = completed`, `completed_at = now()`. Emit `campaign.completed`.

---

## 11) Implementation Acceptance Checklist

- [ ] `Campaign`, `CampaignSegment`, `MessageTemplate`, `CampaignSend`, `CampaignConversion` entities created.
- [ ] State machine transitions enforced — invalid transitions return `422`.
- [ ] Segment validation resolves rules against DB and returns correct `estimated_size`.
- [ ] WhatsApp opt-in gate: contacts with `whatsapp_opted_in = false` are skipped with `SkipReason = not_opted_in`.
- [ ] Urdu template guard: activation blocked if template `is_urdu = true` and `urdu_approved_by` is null.
- [ ] Idempotency: duplicate sends for same `(campaign_id, contact_id)` deduplicated.
- [ ] Dispatch rate limiting: 80 msg/min WhatsApp enforced per tenant.
- [ ] Delivery/read/reply receipts update `CampaignSend` status and parent `Campaign` counters atomically.
- [ ] Opt-out via "STOP" / "بند کریں" sets `Contact.whatsapp_opted_in = false`.
- [ ] Attribution: last-touch, 30-day default window, all three conversion types tracked.
- [ ] All API endpoints respect RBAC role gates (table in §8).
- [ ] All events in §9 emitted via activity log.
- [ ] Scanner jobs (scheduler, attribution, completion) scheduled and testable.
- [ ] Tenant isolation enforced on all list endpoints.
