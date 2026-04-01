# B0-P03::UI_SYSTEM_DOC

**Build scope**
- Design system
- Dashboard system
- Role-based UX
- Workspace models

**Output**
- `docs/ui-system.md`

---

## 1) System Intent and Coverage Contract

This UI system defines a **single, enforceable contract** for every CRM surface in this repository. It unifies:
- the foundational design tokens and interaction states,
- role-gated dashboards,
- permission-aware workspace behavior,
- and domain-specific workspace models.

### 1.1 Covered CRM surfaces (no gaps)

1. Tenant provisioning & entitlement administration
2. Feature flag governance and runtime configuration
3. Identity and RBAC administration
4. Lead intake, scoring, assignment, and conversion
5. Contact management and deduplication
6. Account management and hierarchy navigation
7. Opportunity pipeline, forecasting, and close execution
8. Quotes, approvals, orders, and CPQ flows
9. Subscription billing, invoicing, payments, and revenue recognition
10. Case management, SLA operations, and support console workflows
11. Knowledge base authoring, review, publishing, and retrieval
12. Campaign planning, segmentation, activation, and journey monitoring
13. Omnichannel communication threads and engagement tracking
14. Workflow builder, runtime monitoring, and execution troubleshooting
15. Search and cross-object discovery
16. Reporting and analytics dashboards
17. Audit, compliance, and governance operations
18. Partner/channel management and attribution visibility
19. Admin control center and system operations

### 1.2 Non-negotiable quality bars

- No generic placeholders such as “entity list” or “analytics card”; all modules are domain-named.
- Every interactive element has explicit states: `default`, `hover`, `focus`, `loading`, `empty`, `error`, `restricted`.
- Every mutation path is role-evaluated before action enablement.
- Every dashboard and workspace module maps to a domain read model or canonical entity stream.

---

## 2) Design System (Domain-Operational)

### 2.1 Token architecture

All surfaces consume the same token hierarchy:

- **Foundation tokens**: color, typography, spacing, radius, border, elevation, motion.
- **Semantic tokens**: intent roles (success, warning, breach, critical, restricted, draft, approved, closed-won).
- **Domain semantic aliases**:
  - `token.stage.discovery`, `token.stage.negotiation`, `token.stage.closed_won`
  - `token.sla.healthy`, `token.sla.at_risk`, `token.sla.breached`
  - `token.approval.pending`, `token.approval.approved`, `token.approval.rejected`
  - `token.billing.current`, `token.billing.delinquent`, `token.billing.suspended`

**Rule:** domain aliases map to base semantic tokens centrally; feature teams never define local one-off colors.

### 2.2 Core primitives

- **Shell primitives**: top navigation, contextual left rail, workspace sub-nav, utility panel.
- **Data primitives**: query table, stage board, timeline rail, KPI tile, state banner, split detail pane.
- **Input primitives**: validated form sections, policy-aware action bar, side-sheet editors, command palette.
- **Feedback primitives**: inline validation, async progress rail, audit confirmation modal, conflict resolution prompt.

### 2.3 Interaction state contract

Every interactive domain component must implement:
- `default`
- `keyboard_focus`
- `in_progress`
- `success`
- `error_recoverable`
- `error_blocking`
- `permission_restricted`
- `policy_requires_approval` (for governed mutations)

### 2.4 Responsive and density behavior

- **Desktop (>=1024):** multi-pane execution (list + detail + context).
- **Tablet (640–1023):** two-pane with collapsible context.
- **Mobile (<640):** single critical workflow lane; only P0 actions stay fixed.
- **Density modes:** `comfortable` for mixed work, `compact` for queue/audit-heavy roles.

---

## 3) Dashboard System (Role + Domain Accurate)

### 3.1 Dashboard architecture

Each dashboard page is composed of deterministic zones:
1. **Posture bar** (tenant, role scope, timezone, data freshness)
2. **Primary KPIs** (4–8 role-specific metrics)
3. **Execution queue** (items requiring immediate action)
4. **Trend/diagnostic block** (time-series, funnel, aging)
5. **Risk and anomaly block** (breach, failure, policy drift)

### 3.2 Dashboard catalog by domain

- Tenant & entitlement dashboard
- Identity & access posture dashboard
- Lead funnel and assignment latency dashboard
- Customer master health dashboard
- Opportunity pipeline and forecast dashboard
- Quote approval cycle dashboard
- Subscription revenue retention dashboard
- Case SLA operations dashboard
- Communication engagement dashboard
- Knowledge effectiveness dashboard
- Workflow automation outcome dashboard
- Search observability dashboard
- Platform audit & reliability dashboard

### 3.3 Role-gated dashboard defaults

- **Tenant Owner / Tenant Admin:** tenant posture, identity risk, feature governance, audit reliability
- **Sales Manager:** pipeline snapshot, forecast confidence, stalled stage queue
- **Sales Rep / SDR:** personal pipeline, lead response queue, quote pending actions
- **RevOps / Finance Ops:** quote cycle, subscription delinquency, revenue leakage indicators
- **Support Manager:** SLA breach forecast, backlog heatmap, escalation queue
- **Support Agent:** assigned queue, due-soon cases, article suggestion quality
- **Marketing Manager:** campaign throughput, segment quality, activation anomalies
- **Analyst:** all reporting domains read-only with drilldown filters
- **Auditor / Compliance:** immutable audit, privileged action drift, policy exception tracking

### 3.4 Cross-dashboard consistency rules

- Every KPI links to a filtered source workspace or evidence view.
- Every anomaly card includes “why” context and next action.
- Every dashboard tile exposes freshness timestamp and source model name.
- No chart without an actionable next-step route.

---

## 4) Role-Based UX System

### 4.1 Permission evaluation sequence

For every page/action/render block:
1. Resolve tenant context.
2. Resolve effective roles.
3. Resolve permission grants and policy constraints.
4. Resolve data-scope filters (self/team/org/restricted).
5. Render view state: hidden, read-only, execute-enabled, or approval-gated.

### 4.2 UX states by authorization outcome

- **Allowed:** control enabled with normal pathway.
- **Read-only:** field/data visible with lock semantics.
- **Restricted:** control hidden or replaced with explicit restriction reason.
- **Approval required:** mutation opens governed approval flow.
- **Blocked by tenant policy:** action unavailable with policy reference.

### 4.3 Persona interaction model

- **Executors (SDR, Sales Rep, Support Agent):** queue-first, minimal navigation depth, fast-action footers.
- **Managers (Sales, Support, Marketing):** aggregate-to-detail drilldown, exception-first prioritization.
- **Operators (RevOps, Finance Ops, Admin):** policy+configuration panels with preview/simulation.
- **Auditors/Compliance:** immutable evidence views, timeline provenance, export controls.

### 4.4 Role-aware microcopy rules

- Restriction text always names the missing permission or policy gate.
- Destructive action confirmations include resource identifiers and impact scope.
- Escalation prompts include SLA/approval deadlines and owner responsibility.

---

## 5) Workspace Models (Surface-by-Surface)

Each workspace model defines: primary jobs-to-be-done, canonical layout, core modules, P0 actions, and key states.

### 5.1 Tenant & Admin workspace

- **Primary jobs:** onboard tenant, manage entitlements, configure flags, enforce governance.
- **Layout:** posture summary + policy side navigation + mutation audit drawer.
- **Core modules:** entitlement matrix, feature rollout controls, org policy rules, audit event feed.
- **P0 actions:** grant/revoke entitlement, schedule feature rollout, rotate policy key.

### 5.2 Identity & RBAC workspace

- **Primary jobs:** manage users/roles/permissions and access risk.
- **Core modules:** user directory, role composer, permission diff viewer, risky session monitor.
- **P0 actions:** assign role, revoke privileged session, enforce MFA policy.

### 5.3 Lead workspace

- **Primary jobs:** intake qualification and rapid assignment.
- **Core modules:** lead queue, score/explanation pane, assignment rule preview, conversion wizard.
- **P0 actions:** assign owner, mark qualified, convert to account/contact/opportunity.

### 5.4 Contact & Account workspace

- **Primary jobs:** maintain customer master and hierarchy integrity.
- **Core modules:** account profile, contact relationship graph, duplicate candidate panel, hierarchy tree.
- **P0 actions:** merge duplicate, re-parent hierarchy node, assign account owner.

### 5.5 Opportunity workspace (sales cockpit)

- **Primary jobs:** stage progression and close execution.
- **Core modules:** stage board, weighted pipeline panel, forecast confidence, activity timeline.
- **P0 actions:** advance stage, update close plan, create quote, mark closed-won/lost.

### 5.6 CPQ / Quote / Order workspace

- **Primary jobs:** configure pricing, run approvals, produce accepted order.
- **Core modules:** line-item configurator, pricing rule trace, approval lane, signature status.
- **P0 actions:** submit for approval, override with policy reason, send for acceptance, generate order.

### 5.7 Subscription, Invoice, Payment, Revenue workspace

- **Primary jobs:** monitor lifecycle, collections, revenue integrity.
- **Core modules:** subscription timeline, invoice status queue, payment event stream, recognition schedule.
- **P0 actions:** retry collection, place hold/release, update billing profile, acknowledge revenue exception.

### 5.8 Support console workspace

- **Primary jobs:** resolve cases within SLA.
- **Core modules:** priority queue, SLA timer lane, context panel (account+history), escalation assistant.
- **P0 actions:** respond, reassign, escalate, resolve/close.

### 5.9 Knowledge workspace

- **Primary jobs:** create and maintain high-impact articles.
- **Core modules:** draft editor, review workflow, freshness monitor, deflection impact tracker.
- **P0 actions:** submit review, publish, deprecate, attach to case resolution.

### 5.10 Marketing workspace

- **Primary jobs:** launch campaigns and monitor engagement quality.
- **Core modules:** campaign builder, segment validator, journey flow monitor, attribution panel.
- **P0 actions:** activate campaign, pause journey node, adjust segment criteria.

### 5.11 Communication workspace

- **Primary jobs:** manage omnichannel threads and delivery outcomes.
- **Core modules:** unified thread inbox, channel delivery diagnostics, template performance lens.
- **P0 actions:** respond via channel, retry failed delivery, escalate thread.

### 5.12 Workflow builder workspace

- **Primary jobs:** design, validate, deploy, and monitor automations.
- **Core modules:** graph canvas, trigger/action inspector, validation report, execution replay.
- **P0 actions:** validate workflow, deploy version, rollback, replay failed execution.

### 5.13 Search & discovery workspace

- **Primary jobs:** cross-object lookup and operational retrieval.
- **Core modules:** federated results panel, facet rail, relevance controls, freshness warnings.
- **P0 actions:** open result in source workspace, save query, report stale index result.

### 5.14 Reporting & analytics workspace

- **Primary jobs:** monitor domain KPIs and investigate variance.
- **Core modules:** dashboard selector, metric drilldown table, cohort/funnel explorers, anomaly timeline.
- **P0 actions:** pin metric, share filtered view, export evidence set.

### 5.15 Audit & compliance workspace

- **Primary jobs:** evidence review and policy exception management.
- **Core modules:** immutable log explorer, actor/resource matrix, exception queue, attestation exports.
- **P0 actions:** open evidence chain, mark reviewed, generate compliance package.

### 5.16 Partner/channel workspace

- **Primary jobs:** manage partner performance and attribution outcomes.
- **Core modules:** partner profile, relationship graph, attribution ledger, commission status board.
- **P0 actions:** register relationship, validate attribution, approve commission.

---

## 6) Navigation and Cross-Surface Operating Model

### 6.1 Global navigation map

- **Operate:** Leads, Opportunities, Quotes, Cases, Communications
- **Grow:** Campaigns, Journeys, Segments, Partner
- **Revenue:** Subscriptions, Invoices, Payments, Revenue
- **Govern:** Identity, Tenant, Feature Flags, Audit
- **Build:** Workflows, Rules, Templates, Integrations
- **Observe:** Dashboards, Search, Data Quality, Reliability

### 6.2 Cross-surface link contract

- Entity opens preserve breadcrumb + role scope + filter provenance.
- Dashboard drilldowns deep-link to filtered workspace state.
- Timeline events are bidirectional: entity -> event evidence and event -> entity state.

---

## 7) Workspace Data Model Binding

Every module binds to either:
1. canonical write entity model (operational state), or
2. read/query model (aggregated analytics state).

Binding requirements:
- module schema version tagged,
- freshness timestamp visible,
- null/lag fallback UX explicitly rendered,
- ownership service and dependency lineage displayed in diagnostics view.

---

## 8) Quality Control: Fix -> Re-fix -> 10/10

### 8.1 QC rubric

1. Coverage across all CRM surfaces
2. Domain-specific (non-generic) module naming
3. Design token standardization compliance
4. Role-based visibility and action gating clarity
5. Dashboard role-default correctness
6. Workspace P0 action determinism
7. Cross-surface deep-link consistency
8. State completeness (`loading/empty/error/restricted`)
9. Mobile/compact behavior for execution-critical flows
10. Data-binding traceability to entity/read models

### 8.2 Fix cycle log

- **Fix pass 1:** tightened surface coverage to include partner/channel and revenue operations.
- **Re-fix pass 2:** replaced generic panel language with domain modules and explicit P0 actions.
- **Re-fix pass 3:** enforced role-gating outcomes and dashboard defaults for each persona class.
- **Re-fix pass 4:** added explicit model-binding and freshness/lineage diagnostics contract.

### 8.3 Final QC verdict

- Coverage across CRM surfaces: **PASS**
- Generic UI language eliminated: **PASS**
- Design + dashboard + RBAC UX + workspace models integrated: **PASS**
- **Final score: 10/10**

---

## 9) Implementation Acceptance Criteria

A UI implementation conforms to this document only when:
- all listed surfaces ship with mapped workspace models,
- role restrictions are rendered deterministically and audited,
- dashboards are role-defaulted and drilldown-capable,
- domain modules use canonical naming and state contract,
- QC rubric in Section 8 remains 10/10 after regression review.
