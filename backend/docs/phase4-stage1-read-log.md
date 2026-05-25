# Phase 4 Stage 1 — Doc Normalisation Read Log

**Purpose:** Tracks every §F + §H spec file read status during Stage 1 doc normalisation. Survives session compression and memory loss.
**Key:** ⬜ = not read | ✓ = fully read line-by-line (main session direct read only)
**Reader:** M = main session direct Read tool call only. Agent reads do NOT count.
**Last updated:** 2026-05-23 — ALL 51 FILES READ. Stage 1 read-through COMPLETE.

---

## Status Summary

| Status | Count |
|---|---|
| ✓ Fully read (M — verified) | 51 |
| ⬜ Not yet read | 0 |
| **Total** | **51** |

**Total lines to read:** 13,732 (across 50 unread files) + 647 (domain-model.md, done) = **14,379 lines**

---

## Reading Rules

1. Only main session direct Read tool calls count. Agent reads = ⬜, not ✓.
2. Every file read from line 1 to its exact total line count. No gaps.
3. Files ≤ 2000 lines: one Read call. Files > 2000 lines: sequential Read calls with offset until all lines covered.
4. After reading each file: update this log (status → ✓, lines_read range, findings) before moving to next file.
5. On session resume: find first ⬜ file in this log and start there.

---

## §F — Domain & Architecture Specs

### Core Architecture

| File | Total lines | Status | Lines read | Duplication findings | Other findings |
|---|---|---|---|---|---|
| domain-model.md | 647 | ✓ M | 1–647 | Master reference — others repeat from this | — |
| architecture-overview.md | 156 | ✓ M | 1–156 | L1/L2/L3 layer model repeated in pakistan-adapter-architecture.md; CQRS-lite one-liner repeats from data-architecture.md | — |
| service-map.md | 90 | ✓ M | 1–90 | None | — |
| capability-matrix.md | 39 | ✓ M | 1–39 | None | — |
| data-architecture.md | 278 | ✓ M | 1–278 | CQRS-lite §2.1 (primary — architecture-overview.md repeats); transactional outbox §3.1 (primary — execution-hardening.md + concurrency-control.md repeat); tenant isolation invariant §1.3 (also in security-model.md, org-multi-tenancy.md, data-governance-layer.md, domain-model.md) | — |
| read-models.md | 176 | ✓ M | 1–176 | None | ActivityTaskOperationalRM stray row line 43 outside main catalog table; 4 dashboard shapes in §Dashboard Widget System not in main catalog table |
| api-standards.md | 312 | ✓ M | 1–312 | §6.2 line 244 deny-by-default duplicated from security-model.md; §9.1 line 287 idempotency 4-tuple duplicated from global-idempotency.md; §10.3 line 311 event dedup rule duplicated from event-catalog.md | — |
| event-catalog.md | 150 | ✓ M | 1–150 | Dedup rule `(tenant_id, event_name, event_id)` stated 3× internally (line 11, line 79, line 150); also repeated in api-standards.md §10.3 | — |

### Identity, Security, Tenancy

| File | Total lines | Status | Lines read | Duplication findings | Other findings |
|---|---|---|---|---|---|
| identity-auth-rbac.md | 479 | ✓ M | 1–479 | Deny-by-default policy also in api-standards.md §6.2; Role-Based UI Config section (lines 416–480) may duplicate ui-foundations.md / ui-system.md | Permission cache TTL 60s stated twice internally: §3.1 line 144 + §5.4 line 375 |
| org-multi-tenancy.md | 252 | ✓ M | 1–252 | Tenant isolation invariants (§3.1) repeat from data-architecture.md + security-model.md + domain-model.md; deny-by-default also in api-standards.md + identity-auth-rbac.md; Auth flow §3.3 mirrors identity-auth-rbac.md §5.2 | Admin Control Center section lines 194–252 (overlay) — may duplicate identity-auth-rbac.md Role-Based UI Config |
| security-model.md | 173 | ✓ M | 1–173 | JWT claims list (line 21) repeats identity-auth-rbac.md §3.2; token TTL table (lines 30–34) repeats identity-auth-rbac.md §2.6 + §3.1; deny-by-default also in api-standards.md + identity-auth-rbac.md + org-multi-tenancy.md; tenant isolation table (lines 75–86) repeats data-architecture.md §1.3 + domain-model.md; session revocation flow repeats identity-auth-rbac.md §3.3 | — |

### Pakistan-Specific

| File | Total lines | Status | Lines read | Duplication findings | Other findings |
|---|---|---|---|---|---|
| pakistan-adapter-architecture.md | 345 | ✓ M | 1–345 | L1/L2/L3 layer model (primary here) — architecture-overview.md repeats it; ComplianceAdapter interface (§4.3) may duplicate compliance-adapter.md (§H); tone tiers polite/firm/urgent (§3F) may overlap collections-engine-model.md / whatsapp-execution-model.md | — |
| whatsapp-execution-model.md | 460 | ✓ M | 1–460 | Lead states §5.2 repeat domain-model.md; MessagingAdapter conceptual §6.2 repeats pakistan-adapter-architecture.md §4.2 (typed); retry/backoff §7.2 repeats execution-hardening.md; intent taxonomy §10.2 may overlap conversational-action-spec.md | §12 QC sub-headings mislabelled "9.1/9.2/9.3" instead of "12.1/12.2/12.3" |
| adoption-ux.md | 155 | ✓ M | 1–155 | "Aha moment < 10 minutes" (line 107) also appears in architecture-overview.md §3 + activation-model.md (to confirm) | Clean — uses cross-refs rather than repeating other docs |
| activation-model.md | 310 | ✓ M | 1–310 | Primary source of aha-moment < 10 min definition — adoption-ux.md line 107 + architecture-overview.md §3 repeat it; default 5 stages may overlap opportunities-pipeline.md | — |

### Core Domain Specs

| File | Total lines | Status | Lines read | Duplication findings | Other findings |
|---|---|---|---|---|---|
| followup-enforcement-model.md | 351 | ✓ M | 1–351 | Escalation timing T+0/+2h/+24h/+48h (lines 68-81) is primary here — adoption-ux.md + architecture-overview.md reference it; enforcement phases Soft/Medium/Strict (§1.2) referenced in adoption-ux.md §5 | Follow-up task states (Pending/Overdue/Completed) differ from whatsapp-execution-model.md §5.3 states — two distinct state sets for same entity |
| activity-control-model.md | 332 | ✓ M | 1–332 | Employee performance KPIs (§5.2) may overlap employee-performance.md (§H); hash chain + Merkle checkpoint (§4.3) may overlap observability-audit.md | §8.1 Shadow Tracking is primary here — adoption-ux.md cross-refs correctly |
| activities-tasks.md | 190 | ✓ M | 1–190 | Ticket/Case overlay (lines 118–191) duplicates cases-domain.md (§H) — full Ticket entity, SLA states, escalation rules all likely repeated there | Activity entity here vs activity-control-model.md §1.2 schema: same entity, different levels of detail |
| opportunities-pipeline.md | 333 | ✓ M | 1–333 | Event payloads for opportunity.stage.changed.v1 + opportunity.closed.v1 (lines 164–198) duplicate event-catalog.md; Forecast overlay entities (lines 202–266) may overlap kpi-data-pipelines.md; Follow-up Queue API appended section (lines 296–334) duplicates followup-enforcement-model.md + domain-model.md — wrong file | Opp stages use code-style names vs activation-model.md human labels — same stages, different naming convention |
| cpq-quotes-orders.md | 74 | ✓ M | 1–74 | Quote + Order entity field lists repeat domain-model.md — thin spec adding API + workflow context only | — |
| payments-revenue.md | 225 | ✓ M | 1–225 | Payment entity fields repeat domain-model.md; payment status enum differs from pakistan-adapter-architecture.md §4.1 (this file has canceled/chargeback, that file omits them); Subscription overlay may overlap collections-engine-model.md + pricing-plans.md; Usage Billing overlay lists event names duplicating event-catalog.md | 3 overlay sections append to core spec — file has grown beyond single purpose |
| collections-engine-model.md | 630 | ✓ M | 1–630 | Tone tiers polite/firm/urgent (line 229) repeated from pakistan-adapter-architecture.md §3.F; Payment entity fields repeat domain-model.md + payments-revenue.md; Payment status enum differs from payments-revenue.md (this: initiated/succeeded/failed/reversed/chargeback vs that: initiated/authorized/captured/settled/failed/canceled/partially_refunded/refunded/chargeback); §4.2 cash/manual fields partly duplicate §N PaymentProof | Event names §10 use unversioned names (invoice.created vs event-catalog.md invoice.summary.updated.v1) — naming inconsistency |
| owner-dashboard.md | 131 | ✓ M | 1–131 | None significant — uses cross-refs correctly | Collections aging buckets (0-30/31-60/60+) differ from collections-engine-model.md buckets (1-7/8-30/31-60/61+) — inconsistent |
| data-governance-ownership.md | 92 | ✓ M | 1–92 | Tenant boundary gate (§1.2) repeats cross-cutting isolation rule from data-architecture.md + security-model.md + multiple others | §2 + §3 defer to data-governance-layer.md — clean cross-referencing |
| contract-lifecycle-management.md | 80 | ✓ M | 1–80 | Contract entity fields repeat domain-model.md — thin spec adding lifecycle + API context only | — |
| data-governance-layer.md | 273 | ✓ M | 1–273 | Break-glass TTL/approvers (§2.5 line 157) repeats security-model.md §Break-Glass section; Governance roles (§1.2) overlap security-model.md RBAC roles; audit envelope (§2.6) differs structurally from activity-control-model.md §1.2 schema — two audit schemas | §2.3 Retention is primary here — data-governance-ownership.md §2 correctly defers |
| partner-channel-management.md | 212 | ✓ M | 1–212 | Partner/PartnerRelationship/PartnerAttribution/PartnerCommission entities repeat domain-model.md; partner event names also in event-catalog.md (§Partner channel management) | DealRegistration overlay entity (lines 196–213) — primary source here |
| custom-object-framework.md | 299 | ✓ M | 1–299 | `FieldDefinition` (lines 212–231) and `CustomFieldDefinition` (lines 258–271) are near-identical structures from two different overlays within the same file — internal duplication | Primary source for custom object framework |

### Infrastructure & Reliability

| File | Total lines | Status | Lines read | Duplication findings | Other findings |
|---|---|---|---|---|---|
| execution-hardening.md | 327 | ✓ M | 1–327 | Idempotency 4-tuple §2.1 also in api-standards.md §9.1 and global-idempotency.md (to confirm primary); retry backoff 1s/2x/±20%/60s-max §3.2 also in whatsapp-execution-model.md §7.2; transactional outbox §5.1 repeats data-architecture.md §3.1; OCC via version_no §4.1 may overlap concurrency-control.md | VersionedRecord + LockLease overlay entities (lines 289–328) — primary source here |
| global-idempotency.md | 230 | ✓ M | 1–230 | PRIMARY SOURCE for idempotency 4-tuple (§1.1) — api-standards.md §9.1 + execution-hardening.md §2.1 both repeat it; PRIMARY SOURCE for event dedupe (§3.1) — event-catalog.md ×3 + api-standards.md §10.3 repeat it; outbox §2.1 step 5 repeats data-architecture.md §3.1 | — |
| concurrency-control.md | 306 | ✓ M | 1–306 | OCC via version_no repeats execution-hardening.md §4.1; transactional outbox §5 repeats data-architecture.md §3.1 + execution-hardening.md §5.1 + global-idempotency.md §2.1; pessimistic locking criteria repeats execution-hardening.md §4.2; deadlock prevention (line 70) repeats execution-hardening.md §4.4 | Entity-level application map (lines 265–280) — primary here |
| distributed-lock-strategy.md | 133 | ✓ M | 1–133 | Distributed lock principles repeat execution-hardening.md §4.3 + concurrency-control.md §1-4 — three files cover same topic at different depths; deadlock via sorted keys (§2.4 line 74) repeats execution-hardening.md §4.4 + concurrency-control.md line 70; 15-min max lease (§2.2 line 62) repeats execution-hardening.md §4.3 lines 161-163 | Primary for Redis implementation detail (SET NX, fencing tokens) — other files are more conceptual |
| offline-sync.md | 280 | ✓ M | 1–280 | Uses version_no for conflict detection (line 133) — concept from concurrency-control.md; §8 idempotency cross-refs global-idempotency.md (correct, not a dupe) | Clean and focused — §13 low-bandwidth budgets are primary here |
| scheduler-jobs.md | 233 | ✓ M | 1–233 | Event names §6 correctly defer to event-catalog.md; retry backoff values differ from execution-hardening.md (scheduler: 10s base/1800s max vs API: 1s base/60s max) — different contexts, both valid | Clean and focused |
| feature-flags-config.md | 167 | ✓ M | 1–167 | None significant | Clean and focused — primary source for feature flag + config system |
| integration-contracts.md | 254 | ✓ M | 1–254 | CommunicationThread/CommunicationMessage overlay fields may overlap domain-model.md; Forecasts API overlay (lines 128–152) stage probabilities — primary here | ProviderName values in overlay (line 216) list `stripe | sendgrid | twilio` only — WhatsApp providers supported but not listed; Plugin Framework overlay (lines 155–201) — primary here |
| observability-audit.md | 302 | ✓ M | 1–302 | §4.1 audit event schema (`integrity.hash/prev_hash/chain_seq`) matches activity-control-model.md §1.2 exactly — consistent; data-governance-layer.md §2.6 uses different `before_hash/after_hash` schema — that file is the outlier; §1.2 retention policy (30d/180d/365d/7yr) overlaps data-governance-layer.md §2.3 (primary there) | `GET /api/v1/audits/integrity/verify` and `GET /api/v1/activities/chain-integrity` serve same purpose — two integrity endpoints for same concept |
| kpi-data-pipelines.md | 290 | ✓ M | 1–290 | None significant — explicitly constrains sources to domain-model.md + event-catalog.md; uses cross-refs correctly | PRIMARY for KPI formulas, gold_kpi_timeseries schema, aggregation pipeline topology; Forecast Overlay in opportunities-pipeline.md (lines 202–266) is separate from this — no exact duplication |
| runtime-deployment.md | 419 | ✓ M | 1–419 | `/health/live`, `/health/ready`, `/health/startup` endpoints defined in both §3.2 here and observability-audit.md §3.2 — repeated definition; §7.1 Golden Signals overlap conceptually with observability-audit.md §3.1 metrics hooks (different levels of detail, not exact duplication) | PRIMARY for env matrix, K8s resource sizing, rollback thresholds, deployment workflow, IaC requirements; L0–L4 infra layer model distinct from pakistan-adapter-architecture.md L1/L2/L3 (different taxonomy) |
| workflow-catalog.md | 502 | ✓ M | 1–502 | Workflow definitions overlap domain specs in scope (leads, opps, cases, payments, partner channel) but at orchestration level not entity level — different abstraction, not strict duplication | Several events used in workflows not confirmed in event-catalog.md: `lead.conversion.failed`, `quote.submitted_for_approval.v1`, `case.sla.breached.v1`, `contact.merged.v1`, `knowledge.article.published.v1` — may be undocumented; PRIMARY for workflow step sequences and saga patterns (lead conversion atomicity contract §3) |
| workflow-dsl.md | 207 | ✓ M | 1–207 | None — explicitly aligned to workflow-catalog.md and event-catalog.md; no entity or rule repetition | PRIMARY for DSL grammar, JSON encoding, and workflow validation rules |

### UI Specs

| File | Total lines | Status | Lines read | Duplication findings | Other findings |
|---|---|---|---|---|---|
| ui-foundations.md | 397 | ✓ M | 1–397 | §7 label used twice (lines 340 + 350) — structural numbering error in file; default-deny UI rule (§1 line 19, §7 line 343) is UI application of the same principle in security-model.md/api-standards.md/identity-auth-rbac.md — different medium, not strict duplication; identity-auth-rbac.md Role-Based UI Config overlay (lines 416–480) overlaps §1 Coverage + §7 Security-Aligned Design Rules here | PRIMARY for typography scale, spacing tokens, color roles, component system, 2-step interaction rule; ≤2-step rule here distinct from ≤10-min aha-moment in activation-model.md |
| ui-system.md | 400 | ✓ M | 1–400 | §2.1 token hierarchy + §2.4 responsive/density behavior repeat ui-foundations.md §2 + §3.2 + §3.3 — same breakpoints (640/1024), same density modes, overlapping token descriptions; §2.3 interaction states here extend ui-foundations.md §4 states — two files cover same component state contract; §4.1 permission evaluation sequence (5 steps) overlaps identity-auth-rbac.md §3.1 RBAC resolution; §3.3 role-gated dashboard defaults overlaps identity-auth-rbac.md Role-Based UI Config overlay (lines 416–480) | PRIMARY for workspace models §5 (surface-by-surface), navigation map §6, design system entity model overlay (lines 357–400); §3.2 dashboard catalog may overlap read-models.md §Dashboard Widget System |

---

## §H — Sprint 0 Design Docs

| File | Total lines | Status | Lines read | Duplication findings | Other findings |
|---|---|---|---|---|---|
| cases-domain.md | 436 | ✓ M | 1–436 | Ticket/Case overlay in activities-tasks.md (lines 118–191) repeats entity, SLA states, and escalation rules here — activities-tasks.md is the duplicate; event names here use unversioned names (`case.sla.first_response_breached`, `case.sla.resolution_breached`) while event-catalog.md + workflow-catalog.md use `.v1` suffix and different granularity (`case.sla.breached.v1`) — naming inconsistency | PRIMARY for Case entity, CaseComment, CaseEscalation, SupportQueue, SLAPolicy, escalation ladder, routing strategies, scanner jobs; Urdu escalation keyword "مینیجر سے بات کریں" primary here |
| shared-inbox.md | 293 | ✓ M | 1–293 | `InboxQueue.routing_strategy` enum values (`round_robin | least_loaded | claim_first | skill_based`) overlap with `SupportQueue.routing_strategy` in cases-domain.md (`round_robin | least_loaded | skill_based | manual`) — same concept, slightly different names (`claim_first` vs `manual`); event names here unversioned vs event-catalog.md `.v1` convention; `CommunicationThread/CommunicationMessage` overlay in integration-contracts.md may overlap with Conversation entity and thread model here | PRIMARY for multi-agent inbox model (InboxQueue, AgentPresence, ConversationHandoff), claim/handoff pipeline, presence management; §2.1 explicitly extends whatsapp-execution-model.md Conversation — correct, not duplication |
| compliance-adapter.md | 327 | ✓ M | 1–327 | §2.5 Retention Rules table repeats data-governance-layer.md §2.3 (primary there) at entity-level detail; pakistan-adapter-architecture.md §4.3 covers same ComplianceAdapter interface at higher level — different depths, overlapping scope | PRIMARY for full ComplianceAdapter ABC interface, anonymize_entity SHA-256 pseudonymization rule, PII field table, call sites matrix; RTbF Urdu keyword "میرا ڈیٹا مٹا دو" primary here; WhatsApp SUBSCRIBE/STOP keywords should align with whatsapp-execution-model.md §7 |
| conversational-action-spec.md | 253 | ✓ M | 1–253 | Intent taxonomy (`payment_query`, `follow_up_response`, `lead_inquiry`, `support_request`) repeats whatsapp-execution-model.md §10.2 — this file IS the execution layer of those intents; `pending_command`/`pending_command_ctx`/`pending_since` fields added to Conversation (§4.1) — Conversation entity now extended across 3 files: whatsapp-execution-model.md (base), shared-inbox.md (§2.1), and here; Urdu escalation keyword inconsistency: here "مینیجر سے بات" vs cases-domain.md §6.2 "مینیجر سے بات کریں" — minor text difference | PRIMARY for command dictionary, context resolution pipeline, confirmation state machine, YES/NO detection, error response matrix; Lead.stage = DISQUALIFIED must align with followup-enforcement-model.md state names |
| localization.md | 398 | ✓ M | 1–398 | WhatsApp template bodies in §6.2 (8 templates) may overlap with templates referenced in collections-engine-model.md and whatsapp-execution-model.md — this file is PRIMARY for EN+UR template string content | PRIMARY for RTL CSS rules, registry.js spec, locale toggle mechanism, formatPKR/formatDate/formatPKPhone helpers, i18n namespace catalog, P-017 gate enforcement; no entity or business rule duplication |
| employee-performance.md | 182 | ✓ M | 1–182 | activity-control-model.md §5.2 employee performance KPIs likely partially overlaps with this file's KPI catalog — this file is PRIMARY; KPI event sources use unversioned names (`lead.created`, `opportunity.won`, `followup.completed`) vs event-catalog.md `.v1` convention — naming inconsistency | PRIMARY for EmployeePerformanceRM schema, KPI formulas (P-01 to P-08), aggregation rules, refresh schedule, RBAC visibility; `EmployeePerformanceRM` may be missing from read-models.md catalog (to verify) |
| territory-management.md | 374 | ✓ M | 1–374 | Routing strategy concepts (`round_robin`, `least_loaded`) overlap with cases-domain.md SupportQueue and shared-inbox.md InboxQueue — same strategy types defined independently for 3 different routing contexts; territory events unversioned vs event-catalog.md `.v1` convention | PRIMARY for Territory entity, TerritoryRule criteria types, TerritoryAssignment schema, conflict resolution algorithm; `territory_ids` JWT claim added at login (§6.2) — likely NOT in security-model.md or identity-auth-rbac.md JWT claims list (gap); `TerritoryPerformanceRM` may be missing from read-models.md catalog |
| pricing-plans.md | 250 | ✓ M | 1–250 | `payments-revenue.md` Subscription overlay overlaps in concept but different angle (revenue recognition vs entitlement plan) — not strict duplication; feature flag mappings table (§2.2) connects this doc to feature-flags-config.md (primary there for toggle system, primary here for plan→flag mapping) | PRIMARY for plan tier definitions (PKR prices), feature entitlement matrix, EntitlementGuard, trial model, upgrade/downgrade rules; `TenantUsageMetric` entity mentioned in §6 — not confirmed in domain-model.md (potential gap); `TenantEntitlement` extensions may need alignment with domain-model.md base entity |
| integration-flow-traces.md | 175 | ✓ M | 1–175 | None — uses cross-references to workflow-catalog.md, execution-hardening.md, offline-sync.md; Cross-Flow Invariants (§lines 166–175) restate cross-cutting rules (idempotency, OCC, tenant isolation) as trace-level assertions — not duplication, different purpose | PRIMARY for 4 end-to-end integration flow traces, failure paths per step, end-state assertions |

---

## Resume Point

**Next action:** Stage 1 COMPLETE. Present findings to user for review before Stage 2 (Code Overlay).
