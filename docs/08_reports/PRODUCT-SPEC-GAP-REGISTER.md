# Product Spec Gap Register

**Source:** `D:\CRM\PRODUCT-SPEC.md` overlay against all 81 active .md files in the repository.
**Analysis date:** 2026-05-18
**Anchor:** PRODUCT-SPEC.md Â§1 (System Architecture), Â§2 (Pakistan Behavioral Layer), Â§3 (Market Intelligence)
**Method:** Each product capability, feature, and domain area in PRODUCT-SPEC.md was mapped to its corresponding doc(s). Gaps are items with no doc, partial doc, or doc coverage claimed but spec content missing.

---

## Coverage Map â€” Well-Covered Areas

These PRODUCT-SPEC.md sections have full, production-grade documentation. No new gaps.

| PRODUCT-SPEC.md Section | Covered by |
|---|---|
| Â§1 Core Engines (all 6) | whatsapp-execution-model.md Â· followup-enforcement-model.md Â· collections-engine-model.md Â· activity-control-model.md Â· activation-model.md Â· execution-hardening.md |
| Â§1 Architecture (L1/L2/L3) | architecture-overview.md Â· pakistan-adapter-architecture.md Â· ADR-001 Â· ADR-002 Â· ADR-003 |
| Â§1 Domain Capabilities â€” WhatsApp Lead Capture | whatsapp-execution-model.md |
| Â§1 Domain Capabilities â€” Follow-up Assistant | followup-enforcement-model.md |
| Â§1 Domain Capabilities â€” Collections Automation | collections-engine-model.md |
| Â§1 Domain Capabilities â€” Owner Dashboard | owner-dashboard.md Â· b9-p01-dashboard-kpi.md |
| Â§1 Domain Capabilities â€” Deal / Revenue Tracking | opportunities-pipeline.md Â· payments-revenue.md |
| Â§1 Domain Capabilities â€” Workflow Engine | workflow-catalog.md Â· workflow-dsl.md Â· b9-p07-workflow-visual-ui.md |
| Â§1 Domain Capabilities â€” Offline Sync | offline-sync.md |
| Â§1 Execution Model (ownership, idle thresholds, logging) | followup-enforcement-model.md Â· activity-control-model.md Â· domain-model.md |
| Â§1 Hardening (idempotency, retry, rate limiting) | execution-hardening.md Â· global-idempotency.md Â· concurrency-control.md Â· security-model.md |
| Â§1 Data Integrity | data-architecture.md Â· data-governance-ownership.md Â· data-governance-layer.md |
| Â§1 Extensibility (adapter pattern) | pakistan-adapter-architecture.md Â· integration-contracts.md |
| Â§2 Behavioral Design Principles | adoption-ux.md |
| Â§2 WhatsApp-native operation | whatsapp-execution-model.md Â· adoption-ux.md |
| Â§2 Trust + Control Layer | identity-auth-rbac.md Â· security-model.md Â· activity-control-model.md |
| Â§2 Follow-up Enforcement Phases (soft â†’ strict) | followup-enforcement-model.md Â· adoption-ux.md |
| Â§2 Cash Flow Reality (confidence scoring, opt-out) | collections-engine-model.md |
| Â§2 Time-to-Value / Activation | activation-model.md |
| Â§2 Mobile-first constraint | b9-p08-mobile-responsiveness-system.md |
| Â§2 Simplicity (â‰¤2 steps per action) | adoption-ux.md Â· ui-foundations.md |
| JWT / RBAC / Security | identity-auth-rbac.md Â· security-model.md Â· org-multi-tenancy.md |
| API standards / envelope / errors | api-standards.md |
| KPI pipelines and read models | kpi-data-pipelines.md Â· read-models.md |
| Scheduling / background jobs | scheduler-jobs.md |
| Feature flags | feature-flags-config.md |
| Observability / audit trail | observability-audit.md |

---

## Already-Logged Gaps â€” market-research-gap-register.md (7 items)

These gaps from PRODUCT-SPEC.md Â§3 (Market Intelligence) are already captured. Status as of 2026-05-18:

| ID | Feature | PRODUCT-SPEC.md ref | Status |
|---|---|---|---|
| MR-001 | Facebook / Instagram lead capture | Â§3/Â§9.3 Â· Â§3/Â§8 | OPEN â€” blocked by Meta API access |
| MR-002 | One-click invoice + WhatsApp payment link | Â§3/Â§9.5 Â· Â§3/Â§8 | PARTIAL â€” `/send` endpoint built (P3-C); payment link blocked by P-016 |
| MR-003 | Voice note transcription (UR/EN/Roman Urdu) | Â§3/Â§9.8 | OPEN â€” needs transcription provider + adapter |
| MR-004 | Automated daily WhatsApp summary to managers | Â§3/Â§9.11 | OPEN â€” not blocked; buildable in Phase 5 |
| MR-005 | Excel import / export for contacts and leads | Â§3/Â§9.12 | OPEN â€” not blocked; buildable in Phase 5 |
| MR-006 | Geo-tagging / field check-in for field reps | Â§3/Â§9.13 | OPEN â€” low priority; needs mobile GPS |
| MR-007 | Kuickpay payment adapter | Â§3/Â§9.6 | OPEN â€” blocked by Kuickpay API credentials |

---

## New Gaps â€” Not Yet Logged Anywhere (10 items)

These were not captured by the original P-033 audit or the MR register.

---

### PS-001 â€” Support / Cases Domain Spec

**PRODUCT-SPEC.md ref:** Â§3/Â§3.C (Support Lifecycle Workflow)
**Severity:** ðŸ”´ Build blocker â€” Phase 4 Build Phase 4 includes 6 support pages (B-05, C-05, E-01, A-07, I-04, C-12)

**What exists:**
- `b9-p04-support-console.md` â€” UI archetype only
- `b9-p02-list-queue.md` â€” generic list/queue archetype

**What is missing:**
- Backend domain spec for the Cases / Support Ticket domain: entity model (`Case`, `CaseComment`, `CaseEscalation`), state machine (open â†’ assigned â†’ in_progress â†’ resolved â†’ closed), SLA timers (first response time, resolution time), routing rules (skill-based, queue-based, round-robin), escalation rules (separate from Follow-up escalation), knowledge base article linking.
- No `cases-domain.md` or `support-ticket.md` equivalent to how `followup-enforcement-model.md` covers the Follow-up domain.

**What to create:**
- `backend/docs/cases-domain.md` â€” entity model, state machine, SLA tiers, routing rules, escalation

---

### PS-002 â€” Shared WhatsApp Inbox Spec

**PRODUCT-SPEC.md ref:** Â§3/Â§9.2 ("Shared WhatsApp Inbox")
**Severity:** ðŸŸ  Architecture gap â€” affects Phase 4 inbox pages (L-01, L-02)

**What exists:**
- `whatsapp-execution-model.md` â€” single-webhook inbound routing; conversation keyed by `tenant_id + phone`
- `b9-p13-inbox-communication.md` â€” UI archetype for inbox thread view

**What is missing:**
- Multi-agent inbox spec: multiple team members handling queries from one official business number. Requires: agent assignment model (conversation â†’ assigned_agent_id), queue management (unassigned pool), conversation handoff (re-assign between agents), agent-scoped inbox view vs supervisor view, presence/availability status, concurrent assignment conflict rules.
- Current architecture assigns conversations per tenant (not per agent) â€” shared inbox is a different model.

**What to create:**
- `backend/docs/shared-inbox.md` â€” agent routing, assignment model, conversation handoff spec

---

### PS-003 â€” ComplianceAdapter Interface Spec

**PRODUCT-SPEC.md ref:** Â§1/Â§3 (L2 Interfaces: MessagingAdapter, PaymentAdapter, **ComplianceAdapter**)
**Severity:** ðŸŸ  Architecture gap â€” third L2 interface is unspecified

**What exists:**
- `pakistan-adapter-architecture.md` â€” covers MessagingAdapter + PaymentAdapter fully
- `data-governance-layer.md` â€” GDPR/PDPA compliance rules
- `data-governance-ownership.md` â€” ownership enforcement rules

**What is missing:**
- ComplianceAdapter interface contract: method signatures (e.g., `verify_consent()`, `anonymize_entity()`, `check_retention_policy()`, `audit_access()`), expected behavior per Pakistan market (PDPA vs GDPR), Pakistan-specific implementation at `adapters/pakistan/compliance/`, which services are required to call it and when.
- No `adapters/interfaces/compliance_adapter.py` protocol file (only `messaging_adapter.py` and `payment_adapter.py` exist).

**What to create:**
- `backend/docs/compliance-adapter.md` â€” interface contract, Pakistan implementation spec, call sites

---

### PS-004 â€” Conversational CRM Action Mapping Spec

**PRODUCT-SPEC.md ref:** Â§1/Â§5.2 ("actions executed via conversation context; minimal reliance on forms") + Â§2/Â§3 ("trigger actions via conversational inputs")
**Severity:** ðŸŸ  Architecture gap â€” conversational actions are a primary differentiator

**What exists:**
- `whatsapp-execution-model.md` â€” intent classification (keyword rules â†’ payment_query, follow_up_response, lead_inquiry, support_request) + lead auto-creation advisory flag
- Intent classification produces a label but does NOT execute CRM mutations.

**What is missing:**
- Command execution layer: how classified intents map to CRM actions. Example: `payment_query` â†’ query open invoices and respond with balance. `follow_up_response` + "DONE" keyword â†’ close follow-up task. No spec for the command dictionary, required entity context (which lead/invoice/task is the action targeting?), confirmation flow for destructive actions (close, reassign), error response when context is ambiguous.

**What to create:**
- `backend/docs/conversational-action-spec.md` â€” command dictionary, intent-to-action mapping, context resolution, error flows

---

### PS-005 â€” Localization / i18n Spec

**PRODUCT-SPEC.md ref:** Â§2/Â§13 (Localization: PKR, local dates, bilingual EN/UR, culturally appropriate tone)
**Severity:** ðŸ”´ Build blocker â€” Phase 4 pages must satisfy RTL constraint (CONSTRAINTS.md C-001)

**What exists:**
- `adoption-ux.md` Â§4 mentions bilingual support
- `CONSTRAINTS.md` C-001 â€” RTL verified on all pages
- `activation-model.md` â€” sample data uses Pakistan names / PKR amounts
- WhatsApp template messages reference `i18n registry` (market-research-gap-register.md MR-002 mentions it) but no registry exists

**What is missing:**
- Localization spec document: i18n framework choice (browser-native `Intl`, custom JSON key-value, or library), i18n key registry format (namespace + key â†’ EN/UR strings), RTL rendering rules (which CSS classes, direction toggle mechanism, right-to-left text flow in forms, tables, charts), Urdu font selection and loading strategy, locale-aware date format rules (DD/MM/YYYY, Islamic calendar option), currency format (Rs. vs PKR vs â‚¨, decimal separator in Pakistan), localized WhatsApp template message keys (EN + UR variants), the locale toggle UI and persistence (per-user setting vs browser detection).

**What to create:**
- `backend/docs/localization.md` â€” i18n framework, RTL rules, EN/UR key registry, WhatsApp template locale rules

---

### PS-006 â€” Employee Performance Indicators Spec

**PRODUCT-SPEC.md ref:** Â§1/Â§5.7 ("Employee Activity Monitoring â€” tracking of user actions; performance indicators")
**Severity:** ðŸŸ¡ Feature spec gap â€” owner dashboard depends on per-employee KPIs

**What exists:**
- `activity-control-model.md` â€” immutable activity logging (event type, owner_id, timestamp, entity_ref)
- `activities-tasks.md` â€” raw event storage model
- `owner-dashboard.md` â€” owner-level view (aggregate metrics)
- `read-models.md` â€” denormalized projections for dashboards

**What is missing:**
- Per-employee performance KPI aggregation spec: which metrics constitute "performance indicators" (leads captured per rep, follow-up completion rate, average response time, conversion rate leadâ†’deal, daily activity count), how read-models aggregate these from raw activity events, refresh frequency, the EmployeePerformanceRM projection schema, which roles can see whose data (manager sees all reps; rep sees own only), drill-down from owner dashboard to per-employee view.

**What to create:**
- `backend/docs/employee-performance.md` â€” KPI definitions, aggregation model, read-model schema, RBAC visibility rules

---

### PS-007 â€” Payment Proof Handling Spec

**PRODUCT-SPEC.md ref:** Â§2/Â§7.2 ("Payment Proof Handling â€” attach screenshot/note; mark as pending verification")
**Severity:** ðŸŸ¡ Feature spec gap â€” required for hybrid payment model (cash + bank transfer)

**What exists:**
- `collections-engine-model.md` â€” automated reconciliation with confidence scoring (â‰¥85% auto-match, 40â€“84% manual review), customer opt-out mechanism
- `payments-revenue.md` â€” payment entity states

**What is missing:**
- Manual payment proof workflow: PaymentProof entity model (`proof_id`, `invoice_id`, `attachment_url`, `note`, `submitted_by`, `submitted_at`, `verification_status: pending|verified|rejected`), file/image upload endpoint (`POST /api/v1/invoices/{id}/proof`), state transition rules (who can submit, who can verify, what moves invoice to paid), reconciliation confidence score for manual proofs (100% by definition once verified), audit trail entry on proof submission and verification.
- This is distinct from the automated callback reconciliation that exists today.

**What to create:**
- Section in `collections-engine-model.md` Â§N: Manual Payment Proof workflow (entity, states, endpoints, RBAC)

---

### PS-008 â€” Territory Management Spec

**PRODUCT-SPEC.md ref:** Â§1/Â§5.7 (field monitoring context) + Â§3/Â§9.13 (geo-tagging: FMCG, Real Estate, Pharma)
**Severity:** ðŸ”´ Build blocker â€” Phase 4 Build Phase 6 includes G-09 territories.html

**What exists:**
- `domain-model.md` â€” mentions `TerritoryRule` criteria schema (entry in table, no full definition)
- `b9-p09-settings-admin.md` â€” territories referenced as a settings page
- `service-map.md` â€” territories may be referenced as a capability

**What is missing:**
- Dedicated territory domain spec: Territory entity model (territory_id, name, criteria_type: geographic|postal|account_segment, criteria_value, assigned_reps[], created_by, active), TerritoryRule criteria schema in full (the domain-model.md entry is a pointer, not a definition), lead/account auto-routing by territory, territory-scoped dashboard views (manager sees only their territory's data), territory assignment conflict resolution (what if a lead matches multiple territories), territory performance reporting.

**What to create:**
- `backend/docs/territory-management.md` â€” entity model, criteria schema, routing rules, RBAC scoping

---

### PS-009 â€” Pricing Tier / PKR Plan Configuration Spec

**PRODUCT-SPEC.md ref:** Â§2/Â§12 ("early value before monetization; visible ROI; revenue features first") + Â§3/Â§5 (PKR pricing benchmarks)
**Severity:** ðŸŸ  Architecture gap â€” feature flags + entitlements need plan tiers to be meaningful

**What exists:**
- `feature-flags-config.md` â€” feature flag service; flags can be enabled/disabled per tenant
- `payments-revenue.md` â€” billing and subscription entity model
- `adoption-ux.md` Â§2 â€” feature visibility tiers (Tier 1â€“4 by usage maturity)

**What is missing:**
- Pricing plan spec: plan tier definitions (Starter / Growth / Business or equivalent), PKR price per tier (aligned to Â§3/Â§5 benchmarks: 1,500â€“4,500 / 5,000â€“12,000 / 15,000+), feature entitlements per plan (which feature flags are unlocked per tier), upgrade/downgrade flow (prorate billing, immediate vs next-cycle), plan-gated feature enforcement in API (which endpoints check plan entitlement before executing), trial period model (how long, what happens on expiry), the metering model (per-user vs flat vs usage-based). Note: adoption-ux.md tiers are UX progressive disclosure, not billing plan tiers â€” these are different concepts.

**What to create:**
- `backend/docs/pricing-plans.md` â€” plan tiers, PKR prices, feature entitlements, upgrade flow, enforcement model

---

### PS-010 â€” End-to-End Integration Flow Traces

**PRODUCT-SPEC.md ref:** Â§1/Â§12 (4 mandatory integration flows that "must function without failure")
**Severity:** ðŸŸ¡ Documentation gap â€” no single trace document for cross-service flows

**What exists:**
- `workflow-catalog.md` â€” lead conversion atomicity (Accountâ†’Contactâ†’Opportunity saga with compensation)
- Individual domain specs cover per-service behavior
- `execution-hardening.md` â€” retry and DLQ behavior
- `offline-sync.md` â€” covers flow #4 partially

**What is missing:**
- Four dedicated end-to-end flow trace documents (or a single unified doc) covering:
  1. **WhatsApp â†’ Lead â†’ Follow-up â†’ Close**: inbound message triggers conversation; intent = lead_inquiry; lead auto-created; follow-up T+0 scheduled; follow-up completed; deal closed; what events are emitted at each step, which service handles each step, what happens if any step fails
  2. **Lead â†’ Invoice â†’ Payment â†’ Reconciliation**: deal close event â†’ invoice created; invoice sent via WhatsApp; customer pays via JazzCash/Easypaisa callback; confidence scoring â†’ auto-reconciled or manual review; invoice marked paid; audit event logged
  3. **Follow-up â†’ Escalation â†’ Reassignment**: T+48h threshold crossed; overdue scanner marks task overdue; escalation event created; manager notified via WhatsApp; manager reassigns; new owner receives WhatsApp notification; activity log updated
  4. **Offline Action â†’ Sync â†’ Consistent State**: user takes action offline; CommandRecord queued locally; connectivity restored; command ingested; conflict detection; resolution applied; device state reconciled

**What to create:**
- `backend/docs/integration-flow-traces.md` â€” all 4 flows with step-by-step cross-service trace, failure paths, end-state assertions

---

## Gap Summary Table

| ID | Gap | Severity | Phase impact | Action |
|---|---|---|---|---|
| MR-001 | Facebook/Instagram lead capture | ðŸŸ  High | Phase 5 | Blocked â€” needs Meta API |
| MR-002 | One-click invoice + WhatsApp payment link | ðŸŸ  High | Phase 5 | Partial â€” P-016 blocker |
| MR-003 | Voice note transcription | ðŸŸ¡ Medium | Phase 5 | Needs provider choice |
| MR-004 | Daily WhatsApp summary to managers | ðŸŸ¡ Medium | Phase 5 | Buildable now |
| MR-005 | Excel import/export | ðŸŸ¡ Medium | Phase 5 | Buildable now |
| MR-006 | Geo-tagging / field check-in | ðŸŸ¢ Low | Phase 5 | Low priority |
| MR-007 | Kuickpay adapter | ðŸŸ¢ Low | Phase 5 | Blocked â€” needs credentials |
| **PS-001** | Support / Cases domain spec | ðŸ”´ Build blocker | **Phase 4** | Create cases-domain.md |
| **PS-002** | Shared WhatsApp inbox spec | ðŸŸ  Arch gap | Phase 4 | Create shared-inbox.md |
| **PS-003** | ComplianceAdapter interface spec | ðŸŸ  Arch gap | Phase 5 | Create compliance-adapter.md |
| **PS-004** | Conversational CRM action mapping | ðŸŸ  Arch gap | Phase 5 | Create conversational-action-spec.md |
| **PS-005** | Localization / i18n spec | ðŸ”´ Build blocker | **Phase 4** | Create localization.md |
| **PS-006** | Employee performance indicators | ðŸŸ¡ Feature gap | Phase 4â€“5 | Create employee-performance.md |
| **PS-007** | Payment proof handling | ðŸŸ¡ Feature gap | Phase 5 | Extend collections-engine-model.md |
| **PS-008** | Territory management spec | ðŸ”´ Build blocker | **Phase 4** | Create territory-management.md |
| **PS-009** | Pricing tier / PKR plan config | ðŸŸ  Arch gap | Phase 5 | Create pricing-plans.md |
| **PS-010** | End-to-end integration flow traces | ðŸŸ¡ Doc gap | Phase 5 | Create integration-flow-traces.md |

**Totals:** 17 open gaps â€” 3 build blockers for Phase 4 (PS-001, PS-005, PS-008), 4 architecture gaps (PS-002, PS-003, PS-004, PS-009), 3 feature spec gaps (PS-006, PS-007, PS-010), 7 already-logged MR items.

---

## What is NOT a gap

The following were checked and are fully covered â€” no action needed:

- All 6 core engine specs âœ“
- WhatsApp-first architecture âœ“
- JWT auth + RBAC + role gates âœ“
- Pakistan payment adapters (JazzCash/Easypaisa) âœ“
- Multi-tenancy + tenant isolation âœ“
- Offline sync architecture âœ“
- Execution hardening (idempotency, retry, DLQ, concurrency) âœ“
- Data governance (GDPR/PDPA) âœ“
- Workflow engine (DSL + catalog) âœ“
- Observability + audit trail âœ“
- Feature flags âœ“
- KPI data pipelines + read models âœ“
- API standards / envelope / error format âœ“
- Domain model (entities, states, FK rules) âœ“
- Adoption UX + behavioral principles âœ“
- Activation model + <10-min onboarding âœ“

