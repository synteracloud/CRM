Status: Draft
Authority Level: Low
Last Reviewed: 2026-06-21
Owner: Human

---

# RECOMMENDED ADR ROADMAP — Pakistan CRM OS

## Purpose

This document lists Architecture Decision Records (ADRs) that are recommended for authoring based on open questions, implicit decisions, and forward-looking choices identified during U0–U10 and Governance Phase 1. These are recommendations only — all require human approval before authoring.

**Existing ADRs (in backend/docs/adr/):**
- ADR-001 (original) — DDD + Microservices Architecture — Accepted 2026-05-18
- ADR-002 (original) — Adapter Pattern for Pakistan Market Isolation — Accepted 2026-05-18
- ADR-003 (original) — WhatsApp-First Interaction Model — Accepted 2026-05-18

**Consolidated governance ADR:**
- ADR-001_PROJECT_FOUNDATION.md (docs/06_decisions/) — Created 2026-06-21 — incorporates all 3 originals and expands

---

## Recommended ADR Roadmap

### ADR-002 (governance) — Multi-Tenancy Isolation Strategy: Application-Level vs PostgreSQL RLS

| Field | Value |
|---|---|
| ADR-ID | ADR-002 (governance numbering) |
| Topic | Multi-tenancy isolation: application-level enforcement vs PostgreSQL Row-Level Security |
| Trigger | Current implementation uses application-level isolation (x-tenant-id header + WHERE tenant_id = $1). This is an implicit decision that needs formal documentation. |
| Priority | HIGH |
| Status | Recommended — not authored |

**Context to cover:**
- Current implementation: x-tenant-id header validated in auth-rbac.js; every SQL binds tenant_id; semgrep CI rule enforces
- Alternative considered: PostgreSQL RLS — policies enforce tenant isolation at DB level regardless of application code
- Trade-offs: application-level (simpler, debuggable, ORM-friendly) vs RLS (stronger guarantee, single point of enforcement)
- Risk of current approach: application bug could expose cross-tenant data (mitigated by test_tenant_isolation.py and semgrep)
- Decision: Document that application-level isolation is the chosen approach; document the mitigation controls

---

### ADR-003 (governance) — AI Inference Model Selection

| Field | Value |
|---|---|
| ADR-ID | ADR-003 (governance numbering) |
| Topic | AI inference provider selection for ai-copilot.html (M-01), lead scoring, churn prediction, CLV estimation |
| Trigger | No AI inference SDK in requirements.txt. All models are rule_based. M-01 is advisory-only. Commercial launch requires deciding whether rule-based is acceptable or ML inference is needed. |
| Priority | HIGH |
| Status | Recommended — not authored — blocked on human product decision (D-004) |

**Context to cover:**
- Current state: 3 ScoringModels (lead_score_v1, churn_predict_v1, clv_estimate_v1) all algorithm=rule_based
- Options: (a) Keep rule-based permanently — simpler, no external API cost, no rate limits; (b) Add OpenAI API — ML inference for copilot query and score models; (c) Add Anthropic Claude API — stronger reasoning for copilot; (d) Self-host model — no external dependency, higher infrastructure cost
- Pakistan-specific considerations: API latency from Singapore to Pakistan via overseas AI providers; data sovereignty concerns if customer data sent to external AI
- Decision: Must cover which provider, which models, data governance for inference calls, cost implications

---

### ADR-004 (governance) — Payment Gateway Production Integration

| Field | Value |
|---|---|
| ADR-ID | ADR-004 (governance numbering) |
| Topic | Production rollout of JazzCash and Easypaisa live payment processing |
| Trigger | P-016 blocker will eventually be cleared. When credentials arrive, a formal decision record should cover the production go-live process, testing requirements, and rollback plan. |
| Priority | HIGH (when P-016 is cleared) |
| Status | Recommended — not authored — blocked on P-016 |

**Context to cover:**
- Current state: adapters/pakistan/payments/jazzcash.py and easypaisa.py are complete but stub_mode=True
- Sandbox testing requirements: full E2E test with sandbox credentials must pass test_workflow_invoice.py payment flow
- Production enablement: setting JAZZCASH_STUB_MODE=false and EASYPAISA_STUB_MODE=false in Render environment
- Rollback plan: how to re-enable stub mode if live payments malfunction
- Monitoring: how to detect failed payments in production; webhook logging in /payment-webhooks/log
- Compliance: Pakistan tax invoice requirements (FBR); receipt format requirements
- Error handling: JazzCash/Easypaisa error codes and mapping to CRM payment statuses

---

### ADR-005 (governance) — WhatsApp Business API Provider Selection

| Field | Value |
|---|---|
| ADR-ID | ADR-005 (governance numbering) |
| Topic | Selecting a primary WhatsApp Business API provider from the 4 implemented adapters |
| Trigger | 4 adapters are implemented (Meta, Gupshup, Dialog360, Twilio) but no documentation exists on which is the recommended primary provider for production. |
| Priority | MEDIUM |
| Status | Recommended — not authored |

**Context to cover:**
- 4 implemented adapters: meta_api_adapter.py, gupshup_adapter.py, dialog360_adapter.py, twilio_adapter.py
- Provider comparison: Meta direct (official; complex onboarding; cheapest at scale), Gupshup (Pakistan-popular reseller; simpler onboarding), 360dialog (European; strong API), Twilio (US-based; most documented)
- Pakistan-specific: which providers have strong Pakistan coverage and support
- Onboarding requirements: Meta Business Manager approval (MR-001 dependency), WABA (WhatsApp Business Account) setup
- Cost model: per-message pricing differs significantly across providers
- Failover strategy: can the system switch providers if one goes down? (adapter registry supports this)
- Decision: Primary provider recommendation + failover provider + configuration process

---

### ADR-006 (governance) — Frontend Framework Migration (If Any)

| Field | Value |
|---|---|
| ADR-ID | ADR-006 (governance numbering) |
| Topic | Decision on whether to migrate from NexLink/Bootstrap HTML to a JavaScript framework (React/Vue/Next.js) for future development |
| Trigger | 75 custom pages are built as static HTML with JavaScript. As feature complexity grows, a component framework may provide better maintainability. This is a major architectural decision that must be made explicitly. |
| Priority | LOW (v1 is complete; v2 planning) |
| Status | Recommended — not authored — future planning only |

**Context to cover:**
- Current state: 169 HTML pages (75 custom + 94 NexLink), NexLink CSS, crm-shell.js, crm-api.js, crm-dummy.js
- Cost of migration: 75 custom pages would need rebuilding; 96 library pages are reference only
- Benefits of migration: component reuse, TypeScript safety, better state management, hot reload
- Risks of migration: loss of fast static deployment (currently served as static files on Render); loss of NexLink library pages; significant build time
- Alternative: continue with current approach; extract reusable JS components without framework adoption
- Decision criteria: time-to-market vs maintainability; team JS expertise; whether SPA routing is needed

---

### ADR-007 (governance) — Contract Lifecycle Management Exposure

| Field | Value |
|---|---|
| ADR-ID | ADR-007 (governance numbering) |
| Topic | Whether to expose the contract_lifecycle_management backend module via a gateway route |
| Trigger | Module 29 (contract_lifecycle_management) is fully built in Python backend (12 API endpoints) but has no gateway route or frontend UI surface. Human decision pending (D-001). |
| Priority | MEDIUM |
| Status | Recommended — not authored — blocked on human decision (D-001) |

**Context to cover:**
- Current state: backend/src/contract_lifecycle_management/ with 12 API endpoints defined
- Options: (a) Expose via new v1-contract-lifecycle.routes.js — adds contract management feature; requires frontend pages; (b) Archive — keep backend as completed work; no UI surface in v1; expose in v2
- Frontend cost: if exposed, needs at minimum a contract list page and contract detail page
- Integration points: contracts relate to Opportunities, Accounts, Invoices
- Decision: document the choice and rationale

---

## ADR Authoring Queue (Priority Order)

| ADR-ID | Priority | Blocked On | Author When |
|---|---|---|---|
| ADR-002 — Multi-tenancy isolation | HIGH | Nothing | Can be authored immediately |
| ADR-003 — AI inference model | HIGH | D-004 (human product decision) | After provider is selected |
| ADR-005 — WhatsApp provider selection | MEDIUM | MR-001 (Meta approval) / commercial decision | After provider is selected |
| ADR-004 — Payment gateway production | HIGH | P-016 (credentials) | When P-016 is cleared |
| ADR-007 — Contract lifecycle exposure | MEDIUM | D-001 (human decision) | After D-001 decision |
| ADR-006 — Frontend framework migration | LOW | v2 planning | Future version planning |

---

## ADR Format Standard

All ADRs in this project follow the format established in backend/docs/adr/ADR-001.md:
```
# ADR-XXX — Title
Date: YYYY-MM-DD
Status: Accepted | Rejected | Superseded by ADR-XXX
Deciders: [names]

## Context
[Why this decision was needed]

## Decision
[What was decided]

## Consequences
[Positive + Negative + Trade-offs + Mitigations]

## References
[Related docs and files]
```

ADR files in the governance system go to: `docs/06_decisions/ADR-XXX_title.md`
Original backend ADRs remain in: `backend/docs/adr/ADR-XXX.md`

---

*End RECOMMENDED_ADR_ROADMAP.md*
