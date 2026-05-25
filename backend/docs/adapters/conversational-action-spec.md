<!-- OWNERSHIP
PRIMARY FOR: ConversationalCommand schema and execution contract; command dictionary (intent→CRM action mapping); context resolution algorithm (target entity disambiguation); confirmation flow spec for destructive actions; error reply templates; ConversationCommandProcessor service contract.
DEFERS TO: whatsapp-execution-model.md (intent classification — primary there; this doc consumes classified intents, does not define them); identity-auth-rbac.md (RBAC applies equally to conversational actions — actor is assigned_agent_id); cases-domain.md (support_request command targets Case entity); activities-tasks.md (mutations logged as ActivityEvent with source=conversational_whatsapp).
DO NOT RE-DEFINE: Intent classification rules → whatsapp-execution-model.md; WhatsApp message delivery mechanics → whatsapp-execution-model.md; Case entity schema → cases-domain.md.
-->

# Conversational CRM Action Mapping Spec

## Purpose

This document defines how intent-classified WhatsApp messages map to concrete CRM mutations. The `whatsapp-execution-model.md` classifies intents (payment_query, follow_up_response, lead_inquiry, support_request) but stops at the label — it does not execute CRM actions. This spec defines the **command execution layer**: the command dictionary, context resolution, confirmation flow, and error responses.

**Architecture context:** PRODUCT-SPEC.md §1/§5.2 states "actions executed via conversation context; minimal reliance on forms." This spec operationalizes that design principle.

---

## 1) Core Model

### 1.1 Conversational Command Execution

A **ConversationalCommand** is an action triggered by a classified inbound WhatsApp message. It is executed by the `ConversationCommandProcessor` service, which:
1. Takes a classified `Message` (with `intent` label and full `body`).
2. Resolves the **target entity** (which lead/invoice/task is this message about?).
3. Applies the **action** (mutation against the CRM).
4. Sends a **WhatsApp reply** confirming the outcome.

### 1.2 Non-negotiable Invariants
1. A conversational action may never execute without a resolved target entity. Ambiguous context → error reply, no mutation.
2. Destructive actions (close, mark paid, reassign) require a **confirmation step** before execution.
3. All mutations are logged in `ActivityEvent` with `source = conversational_whatsapp`.
4. If the execution fails for any reason, the system sends a human-readable error reply to the customer and logs the failure.
5. ConversationalCommand execution is subject to the same RBAC rules as REST API calls — the acting principal is the `Conversation.assigned_agent_id` (or the tenant's default bot user if no agent is assigned).

---

## 2) Command Dictionary

### 2.1 Intent → Command Mapping Table

| Intent | Trigger keywords | Command | Required context |
|---|---|---|---|
| `payment_query` | "balance", "invoice", "kitna baqi", "کتنا باقی", "due amount" | `QueryOpenInvoices` | `contact_id` or `phone_number` |
| `payment_query` | "paid", "payment done", "ادائیگی ہو گئی", "sent", "transferred" | `ReportPayment` | `invoice_id` + `amount` |
| `follow_up_response` | "done", "complete", "کام ہو گیا", "finished", "meeting done" | `CloseFollowUp` | `followup_task_id` |
| `follow_up_response` | "delay", "postpone", "کل کریں", "reschedule", "tomorrow" | `SnoozeFollowUp` | `followup_task_id` + `snooze_duration` |
| `follow_up_response` | "not interested", "cancel", "نہیں چاہیے", "stop following up" | `DisqualifyLead` | `lead_id` |
| `lead_inquiry` | "interested", "want to buy", "کوٹیشن بھیجیں", "quote please", "need info" | `CreateLead` | `phone_number` (from message metadata) |
| `lead_inquiry` | "refer", "friend interested", "آپ کا نمبر دیں", "send to friend" | `CreateReferral` | `phone_number` |
| `support_request` | "complaint", "issue", "problem", "شکایت", "نہیں چل رہا", "broken" | `CreateCase` | `contact_id` (from conversation) |
| `support_request` | "escalate", "manager", "مینیجر سے بات کریں", "ESCALATE" | `EscalateCase` | `case_id` (latest open case for contact) |
| `support_request` | "resolved", "fixed", "ٹھیک ہو گیا", "problem solved" | `ConfirmCaseResolution` | `case_id` |

### 2.2 Command Specifications

---

#### `QueryOpenInvoices`
**Trigger:** `payment_query` + balance/invoice keywords  
**Context:** `contact_id` or `phone_number`  
**Action:** Read-only. Queries all open invoices for the contact.  
**Reply format:**
```
"Hi [name], your open invoices:
1. Invoice #INV-001 — Rs 25,000 — due 20 May
2. Invoice #INV-002 — Rs 12,500 — overdue

Total outstanding: Rs 37,500
Reply "PAID [invoice number]" to mark as paid, or send your payment."
```
**No confirmation required** (read-only operation).

---

#### `ReportPayment`
**Trigger:** `payment_query` + payment confirmation keywords  
**Context required:** Most recent open invoice for the contact (if `invoice_id` not explicit in message).  
**Extraction:** Try to extract payment amount from message body (regex: `Rs?\s*[\d,]+` or `PKR\s*[\d,]+` or `(\d{1,3}(?:,\d{3})*)\s*(?:rs|rupees|PKR)`).  
**Confirmation flow:**
```
System reply: "Got it! Rs [amount] received? Let me confirm:
Invoice #INV-001 — Rs 25,000 — PAID
Reply YES to confirm or NO to cancel."
```
**On YES:** Creates a `PaymentEvent` via the Collections Engine; updates invoice status.  
**On NO:** No mutation; reply "Ok, no changes made."  
**Failure case:** If amount doesn't match any open invoice amount (within ±5% tolerance): "I found an invoice for Rs X but you mentioned Rs Y. Please reply the exact invoice number or speak to your sales rep."

---

#### `CloseFollowUp`
**Trigger:** `follow_up_response` + completion keywords  
**Context:** Resolve the most recent open `FollowupTask` where `lead.phone_number = message.from_number`.  
**Confirmation:** No confirmation required for close (non-destructive — task was completed).  
**Action:** Marks `FollowupTask.status = COMPLETED`; logs ActivityEvent.  
**Reply:** "Great! Follow-up marked complete. Your next follow-up is scheduled for [next_due_at]. Reply DONE when complete or POSTPONE to reschedule."

---

#### `SnoozeFollowUp`
**Trigger:** `follow_up_response` + delay/reschedule keywords  
**Context:** Most recent open `FollowupTask` for the contact.  
**Snooze duration extraction:** "tomorrow" → +24h; "next week" / "اگلے ہفتے" → +7 days; "Monday" → next Monday; explicit date (e.g. "25 May") → parsed date; fallback: +24h.  
**Confirmation:** No confirmation required.  
**Action:** Updates `FollowupTask.due_at`; logs ActivityEvent.  
**Reply:** "Ok, follow-up snoozed to [new_due_at]. I'll remind you then."

---

#### `DisqualifyLead`
**Trigger:** `follow_up_response` + opt-out keywords  
**Context:** Most recent open `Lead` for the contact.  
**Confirmation required:**
```
"You said 'not interested'. Should I close this lead?
Reply YES to close or NO to keep it open."
```
**On YES:** Sets `Lead.stage = DISQUALIFIED`; logs reason as "customer_declined_via_whatsapp".  
**On NO:** No mutation.  
**Reply on confirm:** "Lead closed. If you change your mind, just message us again."

---

#### `CreateLead`
**Trigger:** `lead_inquiry` + interest keywords (or any inbound with `lead_inquiry` intent and no existing open lead for this phone)  
**Context:** `phone_number` from inbound message metadata (always available).  
**Action:** Creates `Lead` with `source = whatsapp_inbound`, `stage = OPEN`, `phone_number = from_number`. Triggers follow-up T+0 creation.  
**No confirmation required** (lead creation is non-destructive).  
**Reply:** "Hi! Thanks for reaching out. I've noted your interest. [Agent name] will follow up with you shortly."

---

#### `CreateReferral`
**Trigger:** `lead_inquiry` + referral keywords  
**Context:** `phone_number` from message.  
**Action:** Creates a `Lead` with `source = whatsapp_referral`, `referred_by = current_contact_id`.  
**Reply:** "Thanks for the referral! We'll reach out to your friend. Is there anything else we can help you with?"

---

#### `CreateCase`
**Trigger:** `support_request` + complaint/issue keywords  
**Context:** `contact_id` resolved from `conversation.contact_id` (or auto-created from phone if no contact exists).  
**Action:** Creates `Case` with `source = whatsapp`, `subject` = first 100 chars of message body, `status = OPEN`.  
**Reply:** "I've opened a support case for you (#[case_number]). Our team will respond within [sla_hours] hours. Reply 'STATUS' to check your case."

---

#### `EscalateCase`
**Trigger:** `support_request` + escalate/manager keywords  
**Context:** Most recent open `Case` for the contact (status != CLOSED).  
**Confirmation:** No confirmation (customer escalation is always honored immediately).  
**Action:** Creates `CaseEscalation` with `reason = customer_request`; notifies supervisor.  
**Reply:** "Your case has been escalated to a senior team member. They'll contact you within [sla_hours] hours."

---

#### `ConfirmCaseResolution`
**Trigger:** `support_request` + resolution confirmation keywords  
**Context:** Most recent `Case` in `RESOLVED` status for the contact.  
**Action:** Sets `Case.resolution_confirmed_at = now()`; triggers `RESOLVED → CLOSED` transition.  
**Reply:** "Glad we could help! Your case #[case_number] is now closed. Feel free to message us anytime."

---

## 3) Context Resolution

### 3.1 Resolution Pipeline

```
1. PHONE LOOKUP
   contact = Contact.find_by(tenant_id, phone_number=from_number)
   lead    = Lead.find_by(tenant_id, phone_number=from_number, stage NOT IN [CLOSED, DISQUALIFIED])
   case    = Case.find_by(tenant_id, contact_id=contact.id, status NOT IN [CLOSED]) ORDER BY created_at DESC LIMIT 1
   invoice = Invoice.find_by(tenant_id, contact_id=contact.id, status IN [open, overdue]) ORDER BY due_date ASC LIMIT 1
   followup= FollowupTask.find_by(tenant_id, lead_id=lead.id, status=PENDING) ORDER BY due_at ASC LIMIT 1

2. ENTITY AVAILABILITY CHECK
   — For each command's required context: check if resolved entity exists
   — If not found: apply fallback rules (see §3.2)

3. COMMAND EXECUTION
   — Execute mutation against resolved entities
   — Log ActivityEvent with source=conversational_whatsapp
```

### 3.2 Context Fallback Rules

| Scenario | Fallback behavior |
|---|---|
| Contact not found for phone | Auto-create a `Lead` from the phone number; no `Contact` record yet |
| No open lead for contact | Create new lead (for `lead_inquiry`) or return soft error (for `follow_up_response`) |
| Multiple open leads for phone | Select the most recently updated lead; log ambiguity warning |
| No open invoice | Reply: "You have no outstanding invoices. 🎉" |
| No open follow-up task | Reply: "I don't see any pending follow-ups for you. Are you following up on something specific?" |
| No open case | Reply: "I don't see any open support cases. Reply COMPLAINT to open a new one." |

### 3.3 Explicit Entity Reference Extraction

If the message body contains an explicit entity reference, it overrides the fallback:
- Invoice: `#INV-\d+` pattern → use that specific invoice.
- Case: `#CAS-\d+` pattern → use that specific case.
- Task: "task [task_number]" → use that specific task (Phase 5 feature; not in v1).

---

## 4) Confirmation Flow

### 4.1 Pending Confirmation State

Commands that require confirmation (DisqualifyLead, ReportPayment) use a **pending confirmation slot** stored in the `Conversation` entity:

```
Conversation additions:
├── pending_command      : str (nullable — the command awaiting confirmation)
├── pending_command_ctx  : JSONB (nullable — serialized context for the pending command)
├── pending_since        : datetime (nullable)
```

**Expiry:** Pending confirmation expires after 5 minutes. If the next message arrives after 5 minutes, the pending command is cleared and the message is processed fresh.

### 4.2 YES/NO Detection

| Message body (case-insensitive, trimmed) | Action |
|---|---|
| "yes", "yeah", "ok", "ہاں", "جی", "confirm", "confirmed", "Y" | Execute pending command |
| "no", "nope", "cancel", "نہیں", "منسوخ", "N" | Clear pending command; send cancellation reply |
| Anything else | Clear pending command; re-process as new intent (prevents stuck state) |

---

## 5) Error Responses

| Error condition | Reply sent to customer | Internal action |
|---|---|---|
| Intent classified but no matching command | "I didn't quite get that. Can you clarify?" | Log `unknown_command` event |
| Context resolution failed (no entity) | Context-specific message (see §3.2) | Log `context_resolution_failed` event |
| Ambiguous context (multiple matches) | "I see multiple [entities]. Can you give me the reference number?" | Log `ambiguous_context` event |
| Command execution failed (service error) | "Something went wrong on our side. Your team has been notified." | Log `command_execution_failed` event; create internal alert |
| RBAC denied (bot user doesn't have required role) | "This action requires a team member. We'll follow up shortly." | Log `rbac_denied` event |
| Confirmation expired | Clear pending; reprocess | Log `confirmation_expired` event |

**Rule:** The customer ALWAYS receives a reply, even on error. Silent failures are not permitted.

---

## 6) Implementation Acceptance Checklist

- [ ] `ConversationCommandProcessor` service created with all 9 commands.
- [ ] Intent-to-command mapping table implemented.
- [ ] Context resolution pipeline: phone → contact → lead → invoice → case → followup.
- [ ] Explicit entity reference extraction (`#INV-`, `#CAS-` patterns).
- [ ] `pending_command` + `pending_command_ctx` + `pending_since` fields on `Conversation`.
- [ ] YES/NO detection with 5-minute expiry.
- [ ] All 9 commands produce a WhatsApp reply (success and error paths).
- [ ] All mutations logged to `ActivityEvent` with `source = conversational_whatsapp`.
- [ ] Error replies sent for all failure modes listed in §5.
- [ ] RBAC: bot user's role checked before mutation; `rbac_denied` path implemented.
- [ ] `ReportPayment` amount tolerance (±5%) implemented.
- [ ] `SnoozeFollowUp` date parsing: tomorrow/next week/Monday/explicit date/fallback.
