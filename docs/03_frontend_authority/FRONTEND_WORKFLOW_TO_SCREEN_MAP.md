---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Derived From: PRODUCT_WORKFLOWS.md (5 primary + 5 system workflows), DESIGN-SPEC.md (page IDs), API_CONTRACT.md
---

# FRONTEND WORKFLOW-TO-SCREEN MAP — Pakistan CRM OS

For each of the 10 workflows (5 primary + 5 system): entry screen, step sequence, decision points, exit screen, roles, and API calls per step.

---

## PRIMARY WORKFLOW 1 — WF-A: Lead-to-Deal

**Description:** End-to-end journey from lead capture to closed opportunity and invoice.
**Trigger:** Inbound WhatsApp message OR manual lead entry
**Duration:** Variable (days to weeks)

### Screen Flow

```
[lead-new.html] → [leads-detail.html] → [followups.html] → [leads-detail.html]
    → [opportunity-new.html] → [opportunities-detail.html] → [quote-builder.html]
    → [quotes-detail.html] → [quotes-dashboard.html] → [orders-detail.html]
    → [invoices-detail.html]
```

### Step-by-Step

| Step | Screen | Action | API Call | Roles |
|---|---|---|---|---|
| 1. Lead capture | lead-new.html (I-01) | Fill 2-step form, submit | POST /leads | agent+ |
| 2. Territory assignment (auto) | No UI — WF-004 fires automatically | System assigns owner | WF-004 event handling | System |
| 3. Follow-up scheduling | leads-detail.html (C-01) | "New Follow-up" button | POST /followups | agent+ |
| 4. Lead qualification | leads-detail.html (C-01) | Update stage chip | PATCH /leads/:id | agent+ |
| 5. Follow-up enforcement (auto) | followups.html (B-01) | WF-001 creates tasks; agent completes | POST /followups/:id/complete | agent+ |
| 6. Opportunity creation | opportunity-new.html (I-03) | "Convert to Opportunity" | POST /opportunities | agent+ |
| 7. CPQ Quote | quote-builder.html (I-05) | Build quote, add line items | POST /quotes | manager+ |
| 8a. Quote approval (if discount >10%) | quotes-dashboard.html (A-05) | Manager approves/rejects | PATCH /quotes/:id | manager+ |
| 8b. Quote acceptance | quotes-detail.html (C-06) | "Accept" button | POST /quotes/:id/accept | manager+ |
| 9. Opportunity close | opportunities-detail.html (C-04) | "Close Won" / "Close Lost" | PATCH /opportunities/:id (stage) | manager+ |
| 10. Invoice generation | invoices.html (B-09) / invoices-detail.html (C-08) | View or create invoice | POST /invoice-summaries | manager+ |

### Decision Points
- **Discount > 10% on quote?** → routes to approval queue (quotes-dashboard.html A-05)
- **Quote approved?** → continue to acceptance → order creation
- **Quote rejected?** → return to quote-builder.html for revision
- **Opportunity closed_won?** → generate invoice
- **Opportunity closed_lost?** → lead archived; no invoice

### Entry Screen: lead-new.html (I-01) or leads.html (B-02)
### Exit Screen: invoices-detail.html (C-08)

**Roles That Can Execute:** agent (steps 1–6), manager (steps 1–7), manager+ (all steps)

**Pakistan-Market Notes:**
- Step 1: WhatsApp inbound message auto-creates lead (WF-D triggers simultaneously)
- Step 7: All amounts in PKR; discount > 10% → approval mandatory
- Step 10: Invoice in PKR; payment via JazzCash/Easypaisa (P-016 STUB)

---

## PRIMARY WORKFLOW 2 — WF-B: Deal-to-Invoice

**Description:** Converting a closed deal to a paid invoice via Pakistan payment rails.
**Trigger:** opportunity.closed_won OR manual invoice creation

### Screen Flow

```
[orders-detail.html] → [invoices-detail.html] → [collections.html] → [invoices-detail.html]
```

### Step-by-Step

| Step | Screen | Action | API Call | Roles |
|---|---|---|---|---|
| 1. Order from quote | orders-detail.html (C-07) | View created order (auto from quote accept) | GET /orders/:id | manager+ |
| 2. Invoice issuance | invoices-detail.html (C-08) | View or create invoice | POST /invoice-summaries | manager+ |
| 3. Payment initiation | invoices-detail.html (C-08) | "Record Payment" button (STUB) | POST /payments | agent+ |
| 4. Payment webhook (auto) | No UI | JazzCash/Easypaisa webhook updates paid_amount | POST /payment-webhooks/jazzcash (STUB) | System |
| 5. WF-002 auto-reminder (auto) | No UI — WhatsApp | If overdue, system sends WhatsApp | WF-002 event | System |
| 6. Agent follow-up | collections.html (B-08) | View overdue, update status (contacted/promised) | PATCH collection | agent+ |
| 7. Reconciliation | invoices-detail.html (C-08) | "Reconcile" button | POST /collections/:id/reconcile | manager+ |

### Decision Points
- **Invoice paid on time?** → no collections action needed
- **Invoice overdue?** → WF-002 fires WhatsApp reminder; Collection record created
- **Payment received?** → reconcile; Invoice.status → paid

### Entry Screen: orders-detail.html (C-07)
### Exit Screen: invoices-detail.html (C-08) with status=paid

**Roles:** manager+ (invoice), agent (collections queue), system (webhooks)

**Constraint (SD-002):** JazzCash and Easypaisa payment flows show STUB state (P-016). Real payments blocked.

---

## PRIMARY WORKFLOW 3 — WF-C: Case Lifecycle

**Description:** Support request from creation through SLA-tracked resolution.
**Trigger:** Customer WhatsApp message, web form, or manual agent creation

### Screen Flow

```
[case-new.html] → [support-console.html / cases.html] → [cases-detail.html]
    → [cases-detail.html] (resolve) → [cases-detail.html] (close)
```

### Step-by-Step

| Step | Screen | Action | API Call | Roles |
|---|---|---|---|---|
| 1. Case creation | case-new.html (I-04) | 2-step form: contact + subject + priority | POST /cases | agent+ |
| 2. Queue routing (auto) | support-console.html (E-01) | Case appears in SLA queue | GET /support/queues | System |
| 3. Agent assignment | support-console.html (E-01) | "Claim" button | POST /cases/:id/assign | agent+ (cases.assign) |
| 4. First response | cases-detail.html (C-05) | Reply in Conversation tab | POST /cases/:id/comments (customer_reply) | agent+ |
| 5. SLA monitoring (auto) | No UI (system) | SLA monitor checks sla_first_response_due_at | Internal | System |
| 6. SLA breach handling | cases-detail.html (C-05) | Escalation auto-triggered; supervisor notified | WF-003 via event | System |
| 7. Customer communication | cases-detail.html (C-05) | Internal notes + customer replies | POST /cases/:id/comments | agent+ |
| 8. Knowledge linking | cases-detail.html (C-05) | "Link Article" from Resolution tab | POST /cases/:id/link-article | agent+ |
| 9. Resolution | cases-detail.html (C-05) | "Resolve" button | POST /cases/:id/resolve | manager+ |
| 10. Closure | cases-detail.html (C-05) | "Close" button | POST /cases/:id/close | manager+ (cases.close) |
| 11. Reopen (if needed) | cases-detail.html (C-05) | "Reopen" button (14-day window) | POST /cases/:id/reopen | agent+ (within 14d) |

### Decision Points
- **SLA breached?** → WF-003 fires: escalate case; notify supervisor
- **Customer replies within 14 days of close?** → reopen allowed (POST /cases/:id/reopen)
- **Customer replies after 14 days?** → 422 REOPEN_WINDOW_EXPIRED; must create new case
- **Knowledge article linked?** → improves deflection rate on A-09

**State Machine (enforced by API):**
- OPEN → ASSIGNED | CLOSED
- ASSIGNED → IN_PROGRESS | OPEN | ESCALATED
- IN_PROGRESS → WAITING_ON_CUSTOMER | RESOLVED | ESCALATED
- RESOLVED → CLOSED | IN_PROGRESS
- CLOSED → OPEN (14-day window only)

### Entry Screen: case-new.html (I-04)
### Exit Screen: cases-detail.html (C-05) with status=CLOSED

**Roles:** agent (create, comment), manager (resolve), manager+ (close, escalate, force-close)

**SLA Tiers:**
- tier_1_critical: 1h first response / 8h resolution
- tier_2_high: 4h / 24h
- tier_3_standard: 8h / 72h
- tier_4_low: 24h / 168h

---

## PRIMARY WORKFLOW 4 — WF-D: WhatsApp Conversation

**Description:** Inbound WhatsApp message handling through intent classification to CRM action.
**Trigger:** POST /whatsapp-webhooks/{provider} — inbound WhatsApp message

### Screen Flow

```
[inbox.html] → [inbox-thread.html] → (intent → CRM action link)
    → leads-detail.html | invoices-detail.html | cases-detail.html
```

### Step-by-Step

| Step | Screen | Action | API Call | Roles |
|---|---|---|---|---|
| 1. Webhook ingestion (auto) | No UI | Meta/Gupshup/360dialog/Twilio webhook received | POST /whatsapp-webhooks/:provider | System |
| 2. Contact lookup (auto) | No UI | Phone matched to existing Contact (E.164) | Internal | System |
| 3. Conversation creation (auto) | inbox.html (L-01) | Conversation appears in inbox | GET /inbox/conversations | System |
| 4. Intent detection (auto) | inbox-thread.html (L-02) | Intent badge shown: payment_query / lead_inquiry / support_request / follow_up_response | Internal | System |
| 5. Auto-routing (auto) | inbox.html (L-01) | Assigned to InboxQueue by routing_strategy | Internal | System |
| 6. Agent claim | inbox-thread.html (L-02) | "Claim" button | POST /inbox/conversations/:id/claim | agent+ |
| 7. Capacity check | inbox-thread.html (L-02) | If open_conversations >= 10 → claim rejected | Internal | System |
| 8. Agent response | inbox-thread.html (L-02) | Type and send message | POST /inbox/conversations/:id/messages | agent+ |
| 9. Handoff (if needed) | inbox-thread.html (L-02) | "Handoff" button | POST /inbox/conversations/:id/handoff | manager+ (inbox.handoff) |
| 10. CRM action from intent | intent CTA in thread | Click suggested CTA (e.g. "View Invoice") | Navigate to relevant detail page | agent+ |
| 11. Resolution | inbox-thread.html (L-02) | Close conversation | PATCH /inbox/conversations/:id (state=resolved) | agent+ |

### Decision Points
- **Intent = payment_query?** → suggested CTA links to invoices-detail.html
- **Intent = lead_inquiry?** → suggested CTA links to leads-detail.html
- **Intent = support_request?** → suggested CTA links to case-new.html
- **Agent at capacity (10 concurrent)?** → claim fails; routed to next available agent
- **Handoff needed?** → Handoff record created; conversation transferred

### Entry Screen: inbox.html (L-01) (conversation list)
### Exit Screen: inbox-thread.html (L-02) with state=resolved

**4 WhatsApp Providers:** Meta, Gupshup, Dialog360, Twilio (all wired; provider selection at org-level via integrations.html G-05)

**Roles:** agent (claim, respond), manager+ (handoff), manager/supervisor (presence board, routing config)

**Pakistan-Market:** WhatsApp is primary channel. RTL mandatory for Urdu message content. PTA compliance hooks built.

---

## PRIMARY WORKFLOW 5 — WF-E: Payment Collection

**Description:** Automated payment reminder and collection management for overdue invoices.
**Trigger:** invoice.overdue.v1 event (emitted by billing scheduler)

### Screen Flow

```
[invoices.html] → [collections.html] → [invoices-detail.html] (reconcile)
```

### Step-by-Step

| Step | Screen | Action | API Call | Roles |
|---|---|---|---|---|
| 1. Overdue detection (auto) | invoices.html (B-09) | Invoice flagged red | GET /invoice-summaries | System |
| 2. WF-002 WhatsApp reminder (auto) | No UI | System sends WhatsApp to Contact | WF-002 event + MessagingAdapter | System |
| 3. Collection record creation (auto) | collections.html (B-08) | Collection appears in queue | GET /collections | System |
| 4. Agent follow-up | collections.html (B-08) | Update status (pending → contacted → promised) | PATCH /collections/:id | agent+ |
| 5. Payment receipt | invoices-detail.html (C-08) | Record payment (STUB) | POST /payments | agent+ |
| 6. Reconciliation | invoices-detail.html (C-08) | "Reconcile" button | POST /collections/:id/reconcile | manager+ |

### Decision Points
- **WF-002 fails (WhatsApp rate-limit)?** → Retry max_retries=3, backoff=60s
- **Payment received?** → Reconcile; Invoice.status → paid; Collection.status → paid
- **Payment not received after escalation?** → Collection.status → escalated or written_off

### Entry Screen: invoices.html (B-09) (overdue row)
### Exit Screen: invoices-detail.html (C-08) with status=paid

**Roles:** agent (queue management), manager+ (reconcile)

**Constraint (SD-002):** JazzCash/Easypaisa payment processing STUB (P-016).

---

## SYSTEM WORKFLOW 1 — WF-001: Lead Follow-up Enforcement

**workflow_key:** lead_followup_enforcement
**Trigger:** lead.idle.v1 (emitted by follow-up service scheduler when lead has no activity for threshold days)
**is_system:** true (not editable by tenants)

### Frontend Visibility
- followups.html (B-01) — shows WF-001-created tasks in the queue
- leads-detail.html (C-01) — canonical follow-up task visible in follow-up panel
- workflows-dashboard.html (A-10) — WF-001 execution count in dashboard
- workflow-run-detail.html (C-10) — execution trace for WF-001 runs

### UI Steps Visible to User
1. Agent sees new task in followups.html (B-01) — created by WF-001
2. WhatsApp alert received (external — not in UI)
3. Agent marks task complete: POST /followups/:id/complete
4. Lead status returns to working; idle timer resets

**Roles:** agent (execute task), system (create task)

---

## SYSTEM WORKFLOW 2 — WF-002: Collections Auto-Reminder

**workflow_key:** collections_reminder
**Trigger:** invoice.overdue.v1
**is_system:** true
**max_retries:** 3, **retry_backoff_seconds:** 60

### Frontend Visibility
- collections.html (B-08) — collection record appears after WF-002 fires
- invoices.html (B-09) — overdue flag updated
- workflows-dashboard.html (A-10) — WF-002 execution health
- workflow-run-detail.html (C-10) — retry trace visible when WhatsApp rate-limited

**Roles:** agent (collections queue), system (reminder trigger)

---

## SYSTEM WORKFLOW 3 — WF-003: SLA Breach Notification

**workflow_key:** sla_breach_notify
**Trigger:** case.sla.breached.v1 AND case.sla.first_response_breached.v1
**is_system:** true
**max_retries:** 3

### Frontend Visibility
- cases-detail.html (C-05) — case status changes to ESCALATED; escalation badge visible
- support-console.html (E-01) — breached case moves to top of SLA queue
- support-dashboard.html (A-07) — breach count KPI increments
- workflows-dashboard.html (A-10) — WF-003 execution trace

### UI Steps Visible
1. SLA countdown timer in cases-detail.html header reaches zero
2. Case status badge changes to ESCALATED (auto, no user action)
3. Supervisor receives WhatsApp notification (external)
4. AuditLog entry created (visible in audit-log.html J-01)
5. Case appears in breach queue in support-dashboard.html (A-07)

**Roles:** agent (view escalated case), manager/supervisor (view notification), system (execute)

---

## SYSTEM WORKFLOW 4 — WF-004: Lead Territory Assignment

**workflow_key:** lead_assignment
**Trigger:** lead.created.v1 (fired immediately after POST /leads)
**is_system:** true
**max_retries:** 3, **retry_backoff_seconds:** 30

### Frontend Visibility
- leads-detail.html (C-01) — owner_id populated after WF-004 fires (may be near-instant)
- territories.html (G-09) — territory rules that WF-004 evaluates are configured here

### UI Steps Visible
1. Agent creates lead via lead-new.html (I-01)
2. POST /leads fires; lead.created.v1 emitted
3. WF-004 evaluates TerritoryRules for lead attributes (industry, geography, account_size)
4. owner_id updated on lead record; LeadAssignment record created
5. Agent opening leads-detail.html sees assigned owner (may be different from submitter)

**Configuration Screen:** territories.html (G-09) — configure TerritoryRule criteria_type (geography/industry/account_size) and assignment strategy

**Roles:** System (execute), manager+ (configure territories)

---

## SYSTEM WORKFLOW 5 — WF-005: Opportunity Stage Change Notification

**workflow_key:** opportunity_stage_notify
**Trigger:** opportunity.stage.changed.v1 (fired on PATCH /opportunities/:id)
**is_system:** true

### Frontend Visibility
- opportunities-detail.html (C-04) — stage change fires the event; no additional UI
- sales-dashboard.html (A-04) — forecast refreshes after WF-005 executes
- workflows-dashboard.html (A-10) — WF-005 execution count

### UI Steps Visible
1. Agent/manager updates opportunity stage in opportunities-detail.html (C-04)
2. PATCH /opportunities/:id fires; opportunity.stage.changed.v1 emitted
3. WF-005 runs: (a) checks if stage is in notification-enabled list; (b) sends stage alert to team; (c) calls POST /forecasts/aggregate to refresh forecast
4. sales-dashboard.html (A-04) forecast KPIs update on next load

**Notification-enabled stages:** qualification, negotiation, closed_won, closed_lost (configured in workflow DSL)

**Roles:** agent+ (trigger via stage update), system (notify + forecast refresh)

---

*End FRONTEND_WORKFLOW_TO_SCREEN_MAP.md*
*10 workflows documented (5 primary + 5 system)*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
