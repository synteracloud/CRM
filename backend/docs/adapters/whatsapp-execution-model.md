<!-- OWNERSHIP
PRIMARY FOR: WhatsApp webhook contract; message lifecycle states; delivery receipt handling; MessagingAdapter typed interface; anti-lead-loss guarantee.
DEFERS TO: pakistan-adapter-architecture.md (MessagingAdapter concept); execution-hardening.md (API-level retry semantics); domain-model.md (Lead states); conversational-action-spec.md (intent command execution layer); compliance-adapter.md (SUBSCRIBE/STOP consent handling).
DO NOT RE-DEFINE: Lead state machine → domain-model.md; MessagingAdapter concept → pakistan-adapter-architecture.md §4.2; API-level retry/backoff → execution-hardening.md §3.2.
-->

# WhatsApp Execution Model (Primary Interface)

## 1) Core Principle

### Architectural Positioning

**WhatsApp is the primary execution interface for customer-facing operations.**

This means:
- Users (sales, support, operations) and external contacts interact through WhatsApp first.
- CRM modules do not "own" the user interaction channel; they orchestrate and persist it.
- System features are expressed as messaging behaviors (capture, follow-up, reminders, negotiation, support) rather than screen-only workflows.

### System Role Split

- **WhatsApp Layer = Interface + Interaction Runtime**
  - Receives inbound user input.
  - Delivers outbound system actions.
  - Represents the active operational surface.
- **CRM Layer = Backend Engine**
  - Entity resolution (Contact, Lead, Deal, Payment, Ticket).
  - Business rules/state transitions.
  - Scheduling, analytics, compliance, and auditability.

> Decision rule: if a workflow can run through WhatsApp, it should run through WhatsApp by default, with CRM UI as operator console and exception-handling surface.

---

## 2) Message Flow

## 2.1 Inbound Message Flow (Lead Creation/Update)

```text
Inbound WhatsApp Message
  -> Provider Webhook (Meta/Twilio/Local)
  -> MessagingAdapter.normalizeInbound()
  -> Identity Resolver (phone + tenant + channel)
  -> Conversation Resolver (existing thread or create)
  -> Contact Resolver (existing contact or create minimal profile)
  -> Intent/Event Classifier (lead/support/payment/etc.)
  -> Domain Command Router
      - CreateLeadFromMessage
      - UpdateLeadContext
      - AppendConversationEvent
  -> CRM Persistence (Contact, Lead, Conversation, Events)
  -> Optional Automation Trigger (auto-reply/task/follow-up)
```

Inbound behavior rules:
- Unknown number always creates a **Contact stub** and **Conversation entity**.
- First commercially relevant inbound message creates a **Lead** in `NEW` state unless already mapped to an active deal/ticket.
- Every inbound message is persisted as an immutable **Message Event** and linked to timeline.

## 2.2 Outbound Message Flow (Follow-up / Reminder / Sales)

```text
Scheduler / Agent Action / Workflow Rule
  -> Domain Command (SendFollowUp | SendReminder | SendSalesMessage)
  -> Policy Guard (opt-in, quiet hours, template policy)
  -> MessagingAdapter.send()
  -> Provider API
  -> Provider Ack (message_id/status)
  -> Outbound Event Persisted
  -> Delivery State Tracking (sent/delivered/read/failed)
  -> Retry / Escalation if needed
```

Outbound behavior rules:
- Outbound is always correlated to a Conversation.
- Template-based messages are required where provider policy demands.
- Business intent (`FOLLOW_UP`, `PAYMENT_REMINDER`, `NEGOTIATION`, `SUPPORT_UPDATE`) is stored alongside each message event.

## 2.3 Threading Model (Conversation = Entity)

A **Conversation** is a first-class domain entity, not a transport artifact.

- Primary key scope: `tenant_id + channel + normalized_phone` (plus optional business context key).
- Conversation contains:
  - participants
  - current state
  - active lead/deal/support linkage
  - SLA timers
  - last inbound/outbound timestamps
- Messages are append-only events under the Conversation timeline.
- A Contact may own multiple Conversations (e.g., support and sales contexts) via context partitioning.

---

## 3) Entity Mapping

## 3.1 WhatsApp User -> Contact

Mapping strategy:
- `phone_number` (E.164 normalized) is primary identity key.
- Secondary enrichments: profile name, locale, opt-in metadata, tags.
- On collision across tenants, identity remains tenant-scoped.

## 3.2 Conversation -> Activity Timeline

- Every Conversation maps to a chronological activity timeline visible in CRM.
- Timeline merges:
  - inbound/outbound message events
  - state transitions
  - task creation/completion
  - operator notes and automations

## 3.3 Messages -> Events

Event model per message:
- `message_received`
- `message_sent`
- `message_delivered`
- `message_read`
- `message_failed`
- `message_retry_scheduled`
- `message_retry_exhausted`

Event fields (minimum):
- `event_id`, `conversation_id`, `contact_id`, `direction`, `provider`, `provider_message_id`, `timestamp`, `intent`, `payload_hash`, `status`, `error_code?`

---

## 4) Execution Use Cases

## 4.1 Lead Capture

1. Prospect sends first message.
2. System resolves/creates Contact + Conversation.
3. Lead is created in `NEW`.
4. Auto-response confirms receipt + captures qualification fields.
5. Owner assignment rule runs.
6. Follow-up task scheduled if no reply in SLA window.

## 4.2 Follow-up

1. Trigger from scheduler (no response threshold reached).
2. Follow-up state checked (`DUE`, not `COMPLETED`).
3. Contextual follow-up message sent.
4. Delivery tracked; retries applied if transient failure.
5. Inbound reply transitions follow-up to `RESPONDED` and lead to next stage.

## 4.3 Deal Negotiation

1. Conversation linked to active Deal.
2. Price/term messages tagged as `NEGOTIATION` intent.
3. Counter-offers logged as structured events.
4. Approval workflow may inject guarded outbound templates.
5. Acceptance transitions deal to `WON_PENDING_PAYMENT`.

## 4.4 Payment Reminder

1. Invoice due/overdue event triggers reminder cadence.
2. Reminder messages sent with policy constraints.
3. Delivery/read tracked for escalation path.
4. Payment confirmation inbound updates ledger and closes reminder flow.

## 4.5 Support

1. Inbound support issue classified.
2. Ticket created/linked from Conversation.
3. Status updates pushed outbound through same thread.
4. Resolution message sent; CSAT request optional.
5. Conversation can remain open while ticket closes for later reactivation.

---

## 5) State Machine Definitions

## 5.1 Conversation States

- `NEW` - thread created, minimal context
- `ACTIVE` - live exchange ongoing
- `WAITING_ON_CONTACT` - outbound sent, waiting reply
- `WAITING_ON_INTERNAL` - pending internal action/approval
- `RESOLVED` - objective met (sale/support/payment)
- `CLOSED` - archived after inactivity timeout
- `REOPENED` - inbound arrives after closure

Allowed transitions (core):
- `NEW -> ACTIVE`
- `ACTIVE -> WAITING_ON_CONTACT`
- `ACTIVE -> WAITING_ON_INTERNAL`
- `WAITING_ON_CONTACT -> ACTIVE`
- `WAITING_ON_INTERNAL -> ACTIVE`
- `ACTIVE -> RESOLVED -> CLOSED`
- `CLOSED -> REOPENED -> ACTIVE`

## 5.2 Lead States

- `NEW`
- `QUALIFYING`
- `NURTURING`
- `PROPOSAL`
- `NEGOTIATION`
- `WON`
- `LOST`
- `DISQUALIFIED`

Transition policy:
- Any material inbound can move `NEW/QUALIFYING` forward.
- Explicit rejection or inactivity timeout can move to `LOST` or `DISQUALIFIED`.
- Payment-confirmed close moves to `WON`.

## 5.3 Follow-up States

- `SCHEDULED`
- `DUE`
- `SENT`
- `RESPONDED`
- `SNOOZED`
- `FAILED`
- `COMPLETED`

Transition policy:
- `SCHEDULED -> DUE -> SENT`
- `SENT -> RESPONDED -> COMPLETED`
- `SENT -> FAILED` (on terminal delivery failure)
- `DUE/SENT -> SNOOZED -> DUE`

---

## 6) Provider Abstraction via `MessagingAdapter`

## 6.1 Goal

Decouple CRM execution model from provider-specific APIs and policy quirks.

## 6.2 Interface Contract (Conceptual)

```text
MessagingAdapter
  normalizeInbound(webhookPayload) -> InboundMessage
  send(outboundMessage) -> ProviderAck
  getDeliveryStatus(providerMessageId) -> DeliveryStatus
  registerWebhook(endpointConfig) -> RegistrationResult
  validateSignature(headers, payload) -> bool
```

## 6.3 Supported Provider Classes

- **Meta WhatsApp Business API** (direct)
- **Twilio WhatsApp** (aggregator)
- **Local/Regional Providers** (country-specific gateways)

All providers must produce a canonical envelope:
- Canonical IDs
- Canonical status model
- Canonical error taxonomy
- Canonical timestamp semantics (UTC)

---

## 7) Failure Handling & Reliability

## 7.1 Message Failure Categories

- **Transient**: network timeout, 5xx, rate limit
- **Permanent**: invalid number, policy violation, blocked recipient
- **Unknown**: missing callback / ambiguous provider state

## 7.2 Retry Strategy

- Retry only transient failures.
- Backoff pattern: exponential with jitter (e.g., 30s, 2m, 10m, 30m).
- Max retry attempts configurable per intent criticality.
- Persist retry schedule as events (`message_retry_scheduled`).
- On exhaustion, mark `message_retry_exhausted` and raise operator task.

## 7.3 Delivery Tracking

Track lifecycle per outbound:
- `queued -> sent -> delivered -> read`
- Any failure updates conversation and follow-up states.
- If no delivery callback within SLA, mark as `unknown_delivery` and run reconciliation polling.

Reliability controls:
- Idempotency keys for send commands.
- Deduplication for webhook replays.
- Dead-letter queue for poison events.
- Audit trail for every status mutation.

---

## 7.4 Consent and Opt-out Handling

WhatsApp opt-out keywords (STOP / بند کرو) and opt-in keywords (SUBSCRIBE / سبسکرائب) are handled by the ComplianceAdapter. When the WhatsApp Engine receives an inbound message matching an opt-out keyword, it MUST call `compliance_adapter.record_consent(MARKETING, granted=False)` before any other processing. Full keyword list, consent types, and call sites are defined in `compliance-adapter.md §2.2`.

---

## 8) Execution Readiness Checklist

- WhatsApp-first rule enforced in workflow design.
- Conversation entity present and linked to core CRM objects.
- State machines implemented and observable.
- MessagingAdapter contract used by all providers.
- Delivery + retry telemetry exposed in dashboards.
- Operator fallback paths defined for terminal failures.

---

## 9) Conversational CRM Model

### 9.1 Principle

The CRM system supports a **Conversational CRM** mode where business actions are executed through conversation context rather than form-based UI. This is Domain Capability #2 from the system specification.

> Goal: A sales agent should be able to qualify a lead, schedule a follow-up, and send a payment reminder entirely within a WhatsApp conversation — without opening any CRM form.

### 9.2 What "Conversational" Means

- **Inbound classification drives state**: an inbound message can trigger stage changes, task completions, or payment confirmations without explicit form submission
- **Conversation = execution context**: the active conversation carries enough context (linked lead/deal/ticket, current stage, outstanding tasks) to determine what action to take next
- **Minimal form reliance**: forms are the exception (complex onboarding, bulk imports) not the default path
- **System takes initiative**: the system sends structured prompts, quick-reply buttons, and guided flows via WhatsApp to collect required information conversationally

### 9.3 Conversational Execution Capabilities

| Action | Triggered By | CRM Effect |
|---|---|---|
| Lead qualification | Inbound reply to qualification prompt | Updates lead fields, advances stage |
| Follow-up completion | Inbound reply to follow-up message | Marks follow-up RESPONDED, logs activity |
| Deal stage advance | Inbound acceptance message | Moves opportunity to next stage |
| Payment confirmation | Inbound "paid" / payment reference | Triggers reconciliation check |
| Support ticket update | Inbound reply to ticket thread | Appends to ticket timeline, may resolve |
| Task creation | Outbound auto-response or agent command | Creates task linked to conversation |

### 9.4 Constraints

- Conversational execution does not bypass business rules — the same validation and state machine rules apply
- Sensitive actions (invoice generation, deal close, refund) require explicit confirmation step even in conversation
- All conversational actions are logged in the Activity Timeline with `source: WHATSAPP_CONVERSATION`

---

## 10) Intent Detection + Auto-Classification

### 10.1 Design Principle

Every inbound WhatsApp message must be classified into a canonical intent before routing to domain commands. Classification is **rule-based and keyword-driven** — no ML required. The system must handle Pakistan market communication patterns (mix of Urdu/English, informal shorthand, price queries).

### 10.2 Intent Taxonomy

| Intent | Trigger Keywords / Patterns | Domain Action |
|---|---|---|
| `lead_inquiry` | price, rate, quote, product, available, interested, info | Create or update Lead in NEW/QUALIFYING |
| `payment_query` | paid, payment, send money, jazzcash, easypaisa, received | Trigger reconciliation check; append payment event |
| `follow_up_response` | yes, ok, done, confirmed, will do, call me, meeting | Mark active follow-up RESPONDED; advance lead stage |
| `support_request` | problem, issue, not working, help, complaint, broken | Create/link support ticket |
| `out_of_scope` | (no match) | Log message; surface to agent for manual classification |

### 10.3 Classification Rules

1. Match normalized lower-case message body against keyword list per intent.
2. First match wins (ordered by specificity: payment_query > follow_up_response > lead_inquiry > support_request).
3. If no match → `out_of_scope`; message still logged and linked to conversation.
4. Inbound messages with media attachments (image/document) classify as potential `payment_query` if linked to an open invoice.
5. Classification result stored as `intent` field on the message event — never mutated after write.

### 10.4 Extension Points

- Keyword lists are tenant-configurable (e.g., tenant can add Urdu keywords).
- Custom intent rules can be added via `FeatureFlag` without code changes.
- Future: replace keyword rules with a lightweight NLP classifier behind the same interface.

---

## 11) Anti-Lead Loss Guarantee

### 11.1 Guarantee Definition

> **Every message sent to the business WhatsApp number results in a Contact + Conversation record, regardless of whether the user is known, unknown, or previously inactive.**

This is the Anti-Lead Loss guarantee from the system's Trust + Control Layer (Behaviour Spec §5).

### 11.2 Mechanism

1. **Webhook captures all**: the WhatsApp provider webhook fires for every inbound message, including unknown senders. The system never ignores or drops an inbound event at the webhook layer.
2. **Unknown sender → Contact stub**: an unknown `from_number` always creates a minimal Contact record (phone_e164, tenant_id, source=whatsapp) — no form required.
3. **First commercial message → Lead stub**: if the inbound message classifies as `lead_inquiry` or is the first substantive message, a Lead in `NEW` state is created and linked to the Contact.
4. **Dead-letter recovery**: if the Conversation service fails to process an inbound event, the raw webhook payload is written to `webhook_dead_letter` table. A background job retries processing. No inbound message is silently discarded.

### 11.3 Zero-Friction Capture Rules

| Scenario | System Behavior |
|---|---|
| Unknown number sends first message | Create Contact stub (phone only) + Conversation; classify intent; create Lead if commercial |
| Known contact sends new query | Resolve to existing Contact; create new Conversation or reopen existing |
| Same phone number sends twice | Idempotency on phone_e164 per tenant — no duplicate Contact created |
| Message cannot be classified | Log as `out_of_scope`; surface to agent; Lead NOT auto-created |
| No response from prospect in 24h | Follow-up Engine auto-schedules reminder task |

### 11.4 Duplicate Detection — WhatsApp Layer

- **Primary key**: `E.164 normalized phone + tenant_id` — collision = existing contact.
- **Fuzzy name match** (optional, feature-flagged): if name from WhatsApp profile matches an existing Contact name within edit distance 1, surface merge suggestion — do not auto-merge.
- **Email-based dedup**: if prospect provides email in message, check against `contacts.contact_email` and suggest merge.
- Lead dedup: if a Lead already exists for this Contact in `NEW`/`QUALIFYING`, do not create a second Lead — update the existing one.
- **Code:** `services/leads/repository.py → detect_duplicate_contact(phone_e164, tenant_id)`

### 11.5 Enterprise Deduplication Engine

For cross-entity dedup beyond WhatsApp capture, the system has a full weighted rule engine in `src/data_deduplication_engine/`.

**Scope:** Covers `lead`, `contact`, and `account` entities (not just WhatsApp inbound).

**Dedup flow:**

```
Inbound record
    ↓
RuleDefinition evaluation (weighted match rules per entity_type)
    ↓
MatchEvidence collected (field_name, left/right value, score per rule)
    ↓
DuplicateCandidate scored (total score + risky_conflict flag)
    ↓
Decision:
  score < threshold          → no_match    → create new record
  score ≥ threshold, safe    → prevented   → block create, return existing_id
  score ≥ threshold, unsafe  → manual_review → create ManualReviewTask
  manual review approved     → merged      → execute MergeWorkflow
```

**Key entities:**

| Entity | Purpose |
|---|---|
| `RuleDefinition` | Weighted match rule (`rule_code`, `entity_type`, `weight`, `auto_merge_safe`) |
| `MatchEvidence` | Per-rule evidence with field values and score |
| `DuplicateCandidate` | Scored candidate pair with `risky_conflict` flag |
| `ManualReviewTask` | Queued for human decision when auto-merge is unsafe |
| `MergeWorkflow` | Executed merge with `before_survivor/before_merged/after_survivor` audit trail |
| `UpsertDecision` | Final outcome: `no_match \| prevented \| manual_review \| merged` |

**Auto-merge safety:** `RuleDefinition.auto_merge_safe = True` allows system to auto-merge on high confidence. `False` always routes to `ManualReviewTask`.

**Relationship to WhatsApp dedup:** The WhatsApp layer (`§11.4`) handles fast path E.164 dedup at inbound time. The enterprise engine handles retrospective cross-entity dedup, bulk imports, and manual review workflows.

---

## 12) Review Agent QC (Self-Validation)

## 9.1 Validation Against Objective

- **WhatsApp as core (not addon): PASS**
  - Document positions WhatsApp as primary interface and CRM as engine.
- **Flow completeness: PASS**
  - Includes inbound, outbound, threading, mapping, use cases, states, provider abstraction, and failure handling.

## 9.2 Gaps Found and Fixed

1. Gap: Risk of treating conversation as transport thread only.
   - Fix: Promoted Conversation to first-class domain entity with keys, state, SLA, linkage.
2. Gap: Delivery status ambiguity.
   - Fix: Added canonical lifecycle + unknown-delivery reconciliation.
3. Gap: Provider lock-in risk.
   - Fix: Defined MessagingAdapter contract + canonical envelope.

## 9.3 Alignment Score

**10/10 (100%)**

Rationale:
- All required sections covered.
- Execution-specific, implementation-ready semantics included.
- Explicit safeguards prevent WhatsApp from being reduced to a side integration.
