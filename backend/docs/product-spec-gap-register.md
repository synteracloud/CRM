# Product Spec Gap Register

**Source:** `D:\CRM\PRODUCT-SPEC.md` overlay against all 81 active .md files in the repository.
**Analysis date:** 2026-05-18
**Anchor:** PRODUCT-SPEC.md §1 (System Architecture), §2 (Pakistan Behavioral Layer), §3 (Market Intelligence)
**Method:** Each product capability, feature, and domain area in PRODUCT-SPEC.md was mapped to its corresponding doc(s). Gaps are items with no doc, partial doc, or doc coverage claimed but spec content missing.

---

## Coverage Map — Well-Covered Areas

These PRODUCT-SPEC.md sections have full, production-grade documentation. No new gaps.

| PRODUCT-SPEC.md Section | Covered by |
|---|---|
| §1 Core Engines (all 6) | whatsapp-execution-model.md · followup-enforcement-model.md · collections-engine-model.md · activity-control-model.md · activation-model.md · execution-hardening.md |
| §1 Architecture (L1/L2/L3) | architecture-overview.md · pakistan-adapter-architecture.md · ADR-001 · ADR-002 · ADR-003 |
| §1 Domain Capabilities — WhatsApp Lead Capture | whatsapp-execution-model.md |
| §1 Domain Capabilities — Follow-up Assistant | followup-enforcement-model.md |
| §1 Domain Capabilities — Collections Automation | collections-engine-model.md |
| §1 Domain Capabilities — Owner Dashboard | owner-dashboard.md · b9-p01-dashboard-kpi.md |
| §1 Domain Capabilities — Deal / Revenue Tracking | opportunities-pipeline.md · payments-revenue.md |
| §1 Domain Capabilities — Workflow Engine | workflow-catalog.md · workflow-dsl.md · b9-p07-workflow-visual-ui.md |
| §1 Domain Capabilities — Offline Sync | offline-sync.md |
| §1 Execution Model (ownership, idle thresholds, logging) | followup-enforcement-model.md · activity-control-model.md · domain-model.md |
| §1 Hardening (idempotency, retry, rate limiting) | execution-hardening.md · global-idempotency.md · concurrency-control.md · security-model.md |
| §1 Data Integrity | data-architecture.md · data-governance-ownership.md · data-governance-layer.md |
| §1 Extensibility (adapter pattern) | pakistan-adapter-architecture.md · integration-contracts.md |
| §2 Behavioral Design Principles | adoption-ux.md |
| §2 WhatsApp-native operation | whatsapp-execution-model.md · adoption-ux.md |
| §2 Trust + Control Layer | identity-auth-rbac.md · security-model.md · activity-control-model.md |
| §2 Follow-up Enforcement Phases (soft → strict) | followup-enforcement-model.md · adoption-ux.md |
| §2 Cash Flow Reality (confidence scoring, opt-out) | collections-engine-model.md |
| §2 Time-to-Value / Activation | activation-model.md |
| §2 Mobile-first constraint | b9-p08-mobile-responsiveness-system.md |
| §2 Simplicity (≤2 steps per action) | adoption-ux.md · ui-foundations.md |
| JWT / RBAC / Security | identity-auth-rbac.md · security-model.md · org-multi-tenancy.md |
| API standards / envelope / errors | api-standards.md |
| KPI pipelines and read models | kpi-data-pipelines.md · read-models.md |
| Scheduling / background jobs | scheduler-jobs.md |
| Feature flags | feature-flags-config.md |
| Observability / audit trail | observability-audit.md |

---

## Already-Logged Gaps — market-research-gap-register.md (7 items)

These gaps from PRODUCT-SPEC.md §3 (Market Intelligence) are already captured. Status as of 2026-05-18:

| ID | Feature | PRODUCT-SPEC.md ref | Status |
|---|---|---|---|
| MR-001 | Facebook / Instagram lead capture | §3/§9.3 · §3/§8 | OPEN — blocked by Meta API access |
| MR-002 | One-click invoice + WhatsApp payment link | §3/§9.5 · §3/§8 | PARTIAL — `/send` endpoint built (P3-C); payment link blocked by P-016 |
| MR-003 | Voice note transcription (UR/EN/Roman Urdu) | §3/§9.8 | OPEN — needs transcription provider + adapter |
| MR-004 | Automated daily WhatsApp summary to managers | §3/§9.11 | OPEN — not blocked; buildable in Phase 5 |
| MR-005 | Excel import / export for contacts and leads | §3/§9.12 | OPEN — not blocked; buildable in Phase 5 |
| MR-006 | Geo-tagging / field check-in for field reps | §3/§9.13 | OPEN — low priority; needs mobile GPS |
| MR-007 | Kuickpay payment adapter | §3/§9.6 | OPEN — blocked by Kuickpay API credentials |

---

## New Gaps — Not Yet Logged Anywhere (10 items)

These were not captured by the original P-033 audit or the MR register.

---

### PS-001 — Support / Cases Domain Spec

**PRODUCT-SPEC.md ref:** §3/§3.C (Support Lifecycle Workflow)
**Severity:** 🔴 Build blocker — Phase 4 Build Phase 4 includes 6 support pages (B-05, C-05, E-01, A-07, I-04, C-12)

**What exists:**
- `b9-p04-support-console.md` — UI archetype only
- `b9-p02-list-queue.md` — generic list/queue archetype

**What is missing:**
- Backend domain spec for the Cases / Support Ticket domain: entity model (`Case`, `CaseComment`, `CaseEscalation`), state machine (open → assigned → in_progress → resolved → closed), SLA timers (first response time, resolution time), routing rules (skill-based, queue-based, round-robin), escalation rules (separate from Follow-up escalation), knowledge base article linking.
- No `cases-domain.md` or `support-ticket.md` equivalent to how `followup-enforcement-model.md` covers the Follow-up domain.

**What to create:**
- `backend/docs/cases-domain.md` — entity model, state machine, SLA tiers, routing rules, escalation

---

### PS-002 — Shared WhatsApp Inbox Spec

**PRODUCT-SPEC.md ref:** §3/§9.2 ("Shared WhatsApp Inbox")
**Severity:** 🟠 Architecture gap — affects Phase 4 inbox pages (L-01, L-02)

**What exists:**
- `whatsapp-execution-model.md` — single-webhook inbound routing; conversation keyed by `tenant_id + phone`
- `b9-p13-inbox-communication.md` — UI archetype for inbox thread view

**What is missing:**
- Multi-agent inbox spec: multiple team members handling queries from one official business number. Requires: agent assignment model (conversation → assigned_agent_id), queue management (unassigned pool), conversation handoff (re-assign between agents), agent-scoped inbox view vs supervisor view, presence/availability status, concurrent assignment conflict rules.
- Current architecture assigns conversations per tenant (not per agent) — shared inbox is a different model.

**What to create:**
- `backend/docs/shared-inbox.md` — agent routing, assignment model, conversation handoff spec

---

### PS-003 — ComplianceAdapter Interface Spec

**PRODUCT-SPEC.md ref:** §1/§3 (L2 Interfaces: MessagingAdapter, PaymentAdapter, **ComplianceAdapter**)
**Severity:** 🟠 Architecture gap — third L2 interface is unspecified

**What exists:**
- `pakistan-adapter-architecture.md` — covers MessagingAdapter + PaymentAdapter fully
- `data-governance-layer.md` — GDPR/PDPA compliance rules
- `data-governance-ownership.md` — ownership enforcement rules

**What is missing:**
- ComplianceAdapter interface contract: method signatures (e.g., `verify_consent()`, `anonymize_entity()`, `check_retention_policy()`, `audit_access()`), expected behavior per Pakistan market (PDPA vs GDPR), Pakistan-specific implementation at `adapters/pakistan/compliance/`, which services are required to call it and when.
- No `adapters/interfaces/compliance_adapter.py` protocol file (only `messaging_adapter.py` and `payment_adapter.py` exist).

**What to create:**
- `backend/docs/compliance-adapter.md` — interface contract, Pakistan implementation spec, call sites

---

### PS-004 — Conversational CRM Action Mapping Spec

**PRODUCT-SPEC.md ref:** §1/§5.2 ("actions executed via conversation context; minimal reliance on forms") + §2/§3 ("trigger actions via conversational inputs")
**Severity:** 🟠 Architecture gap — conversational actions are a primary differentiator

**What exists:**
- `whatsapp-execution-model.md` — intent classification (keyword rules → payment_query, follow_up_response, lead_inquiry, support_request) + lead auto-creation advisory flag
- Intent classification produces a label but does NOT execute CRM mutations.

**What is missing:**
- Command execution layer: how classified intents map to CRM actions. Example: `payment_query` → query open invoices and respond with balance. `follow_up_response` + "DONE" keyword → close follow-up task. No spec for the command dictionary, required entity context (which lead/invoice/task is the action targeting?), confirmation flow for destructive actions (close, reassign), error response when context is ambiguous.

**What to create:**
- `backend/docs/conversational-action-spec.md` — command dictionary, intent-to-action mapping, context resolution, error flows

---

### PS-005 — Localization / i18n Spec

**PRODUCT-SPEC.md ref:** §2/§13 (Localization: PKR, local dates, bilingual EN/UR, culturally appropriate tone)
**Severity:** 🔴 Build blocker — Phase 4 pages must satisfy RTL constraint (CONSTRAINTS.md C-001)

**What exists:**
- `adoption-ux.md` §4 mentions bilingual support
- `CONSTRAINTS.md` C-001 — RTL verified on all pages
- `activation-model.md` — sample data uses Pakistan names / PKR amounts
- WhatsApp template messages reference `i18n registry` (market-research-gap-register.md MR-002 mentions it) but no registry exists

**What is missing:**
- Localization spec document: i18n framework choice (browser-native `Intl`, custom JSON key-value, or library), i18n key registry format (namespace + key → EN/UR strings), RTL rendering rules (which CSS classes, direction toggle mechanism, right-to-left text flow in forms, tables, charts), Urdu font selection and loading strategy, locale-aware date format rules (DD/MM/YYYY, Islamic calendar option), currency format (Rs. vs PKR vs ₨, decimal separator in Pakistan), localized WhatsApp template message keys (EN + UR variants), the locale toggle UI and persistence (per-user setting vs browser detection).

**What to create:**
- `backend/docs/localization.md` — i18n framework, RTL rules, EN/UR key registry, WhatsApp template locale rules

---

### PS-006 — Employee Performance Indicators Spec

**PRODUCT-SPEC.md ref:** §1/§5.7 ("Employee Activity Monitoring — tracking of user actions; performance indicators")
**Severity:** 🟡 Feature spec gap — owner dashboard depends on per-employee KPIs

**What exists:**
- `activity-control-model.md` — immutable activity logging (event type, owner_id, timestamp, entity_ref)
- `activities-tasks.md` — raw event storage model
- `owner-dashboard.md` — owner-level view (aggregate metrics)
- `read-models.md` — denormalized projections for dashboards

**What is missing:**
- Per-employee performance KPI aggregation spec: which metrics constitute "performance indicators" (leads captured per rep, follow-up completion rate, average response time, conversion rate lead→deal, daily activity count), how read-models aggregate these from raw activity events, refresh frequency, the EmployeePerformanceRM projection schema, which roles can see whose data (manager sees all reps; rep sees own only), drill-down from owner dashboard to per-employee view.

**What to create:**
- `backend/docs/employee-performance.md` — KPI definitions, aggregation model, read-model schema, RBAC visibility rules

---

### PS-007 — Payment Proof Handling Spec

**PRODUCT-SPEC.md ref:** §2/§7.2 ("Payment Proof Handling — attach screenshot/note; mark as pending verification")
**Severity:** 🟡 Feature spec gap — required for hybrid payment model (cash + bank transfer)

**What exists:**
- `collections-engine-model.md` — automated reconciliation with confidence scoring (≥85% auto-match, 40–84% manual review), customer opt-out mechanism
- `payments-revenue.md` — payment entity states

**What is missing:**
- Manual payment proof workflow: PaymentProof entity model (`proof_id`, `invoice_id`, `attachment_url`, `note`, `submitted_by`, `submitted_at`, `verification_status: pending|verified|rejected`), file/image upload endpoint (`POST /api/v1/invoices/{id}/proof`), state transition rules (who can submit, who can verify, what moves invoice to paid), reconciliation confidence score for manual proofs (100% by definition once verified), audit trail entry on proof submission and verification.
- This is distinct from the automated callback reconciliation that exists today.

**What to create:**
- Section in `collections-engine-model.md` §N: Manual Payment Proof workflow (entity, states, endpoints, RBAC)

---

### PS-008 — Territory Management Spec

**PRODUCT-SPEC.md ref:** §1/§5.7 (field monitoring context) + §3/§9.13 (geo-tagging: FMCG, Real Estate, Pharma)
**Severity:** 🔴 Build blocker — Phase 4 Build Phase 6 includes G-09 territories.html

**What exists:**
- `domain-model.md` — mentions `TerritoryRule` criteria schema (entry in table, no full definition)
- `b9-p09-settings-admin.md` — territories referenced as a settings page
- `service-map.md` — territories may be referenced as a capability

**What is missing:**
- Dedicated territory domain spec: Territory entity model (territory_id, name, criteria_type: geographic|postal|account_segment, criteria_value, assigned_reps[], created_by, active), TerritoryRule criteria schema in full (the domain-model.md entry is a pointer, not a definition), lead/account auto-routing by territory, territory-scoped dashboard views (manager sees only their territory's data), territory assignment conflict resolution (what if a lead matches multiple territories), territory performance reporting.

**What to create:**
- `backend/docs/territory-management.md` — entity model, criteria schema, routing rules, RBAC scoping

---

### PS-009 — Pricing Tier / PKR Plan Configuration Spec

**PRODUCT-SPEC.md ref:** §2/§12 ("early value before monetization; visible ROI; revenue features first") + §3/§5 (PKR pricing benchmarks)
**Severity:** 🟠 Architecture gap — feature flags + entitlements need plan tiers to be meaningful

**What exists:**
- `feature-flags-config.md` — feature flag service; flags can be enabled/disabled per tenant
- `payments-revenue.md` — billing and subscription entity model
- `adoption-ux.md` §2 — feature visibility tiers (Tier 1–4 by usage maturity)

**What is missing:**
- Pricing plan spec: plan tier definitions (Starter / Growth / Business or equivalent), PKR price per tier (aligned to §3/§5 benchmarks: 1,500–4,500 / 5,000–12,000 / 15,000+), feature entitlements per plan (which feature flags are unlocked per tier), upgrade/downgrade flow (prorate billing, immediate vs next-cycle), plan-gated feature enforcement in API (which endpoints check plan entitlement before executing), trial period model (how long, what happens on expiry), the metering model (per-user vs flat vs usage-based). Note: adoption-ux.md tiers are UX progressive disclosure, not billing plan tiers — these are different concepts.

**What to create:**
- `backend/docs/pricing-plans.md` — plan tiers, PKR prices, feature entitlements, upgrade flow, enforcement model

---

### PS-010 — End-to-End Integration Flow Traces

**PRODUCT-SPEC.md ref:** §1/§12 (4 mandatory integration flows that "must function without failure")
**Severity:** 🟡 Documentation gap — no single trace document for cross-service flows

**What exists:**
- `workflow-catalog.md` — lead conversion atomicity (Account→Contact→Opportunity saga with compensation)
- Individual domain specs cover per-service behavior
- `execution-hardening.md` — retry and DLQ behavior
- `offline-sync.md` — covers flow #4 partially

**What is missing:**
- Four dedicated end-to-end flow trace documents (or a single unified doc) covering:
  1. **WhatsApp → Lead → Follow-up → Close**: inbound message triggers conversation; intent = lead_inquiry; lead auto-created; follow-up T+0 scheduled; follow-up completed; deal closed; what events are emitted at each step, which service handles each step, what happens if any step fails
  2. **Lead → Invoice → Payment → Reconciliation**: deal close event → invoice created; invoice sent via WhatsApp; customer pays via JazzCash/Easypaisa callback; confidence scoring → auto-reconciled or manual review; invoice marked paid; audit event logged
  3. **Follow-up → Escalation → Reassignment**: T+48h threshold crossed; overdue scanner marks task overdue; escalation event created; manager notified via WhatsApp; manager reassigns; new owner receives WhatsApp notification; activity log updated
  4. **Offline Action → Sync → Consistent State**: user takes action offline; CommandRecord queued locally; connectivity restored; command ingested; conflict detection; resolution applied; device state reconciled

**What to create:**
- `backend/docs/integration-flow-traces.md` — all 4 flows with step-by-step cross-service trace, failure paths, end-state assertions

---

## Gap Summary Table

| ID | Gap | Severity | Phase impact | Action |
|---|---|---|---|---|
| MR-001 | Facebook/Instagram lead capture | 🟠 High | Phase 5 | Blocked — needs Meta API |
| MR-002 | One-click invoice + WhatsApp payment link | 🟠 High | Phase 5 | Partial — P-016 blocker |
| MR-003 | Voice note transcription | 🟡 Medium | Phase 5 | Needs provider choice |
| MR-004 | Daily WhatsApp summary to managers | 🟡 Medium | Phase 5 | Buildable now |
| MR-005 | Excel import/export | 🟡 Medium | Phase 5 | Buildable now |
| MR-006 | Geo-tagging / field check-in | 🟢 Low | Phase 5 | Low priority |
| MR-007 | Kuickpay adapter | 🟢 Low | Phase 5 | Blocked — needs credentials |
| **PS-001** | Support / Cases domain spec | 🔴 Build blocker | **Phase 4** | Create cases-domain.md |
| **PS-002** | Shared WhatsApp inbox spec | 🟠 Arch gap | Phase 4 | Create shared-inbox.md |
| **PS-003** | ComplianceAdapter interface spec | 🟠 Arch gap | Phase 5 | Create compliance-adapter.md |
| **PS-004** | Conversational CRM action mapping | 🟠 Arch gap | Phase 5 | Create conversational-action-spec.md |
| **PS-005** | Localization / i18n spec | 🔴 Build blocker | **Phase 4** | Create localization.md |
| **PS-006** | Employee performance indicators | 🟡 Feature gap | Phase 4–5 | Create employee-performance.md |
| **PS-007** | Payment proof handling | 🟡 Feature gap | Phase 5 | Extend collections-engine-model.md |
| **PS-008** | Territory management spec | 🔴 Build blocker | **Phase 4** | Create territory-management.md |
| **PS-009** | Pricing tier / PKR plan config | 🟠 Arch gap | Phase 5 | Create pricing-plans.md |
| **PS-010** | End-to-end integration flow traces | 🟡 Doc gap | Phase 5 | Create integration-flow-traces.md |

**Totals:** 17 open gaps — 3 build blockers for Phase 4 (PS-001, PS-005, PS-008), 4 architecture gaps (PS-002, PS-003, PS-004, PS-009), 3 feature spec gaps (PS-006, PS-007, PS-010), 7 already-logged MR items.

---

## What is NOT a gap

The following were checked and are fully covered — no action needed:

- All 6 core engine specs ✓
- WhatsApp-first architecture ✓
- JWT auth + RBAC + role gates ✓
- Pakistan payment adapters (JazzCash/Easypaisa) ✓
- Multi-tenancy + tenant isolation ✓
- Offline sync architecture ✓
- Execution hardening (idempotency, retry, DLQ, concurrency) ✓
- Data governance (GDPR/PDPA) ✓
- Workflow engine (DSL + catalog) ✓
- Observability + audit trail ✓
- Feature flags ✓
- KPI data pipelines + read models ✓
- API standards / envelope / error format ✓
- Domain model (entities, states, FK rules) ✓
- Adoption UX + behavioral principles ✓
- Activation model + <10-min onboarding ✓
