---
Status: L0 FROZEN
Authority Level: Critical
Freeze Date: 2026-06-24
Phase: C6 (Commercial Launch)
Derived From: DESIGN-SPEC.md, FRONTEND_AUTHORITY_MASTER.md, FRONTEND_ROUTE_CATALOG.md,
  FRONTEND_SCREEN_CATALOG.md, FRONTEND_PERMISSION_MATRIX.md, FRONTEND_ROLE_EXPERIENCE_MATRIX.md,
  FRONTEND_WORKFLOW_TO_SCREEN_MAP.md, FRONTEND_GAP_REGISTER.md,
  docs/08_reports/POST_COLLAPSE_FRONTEND_READINESS.md
---

# L0 CLAUDE DESIGN BRIEF — Pakistan CRM OS

Concise orientation brief for Claude Design. All details derive from authority documents — nothing invented here. For full specifications, consult the referenced authority files.

---

## 1 — Project Overview

**Product:** Pakistan CRM OS — a cloud SaaS CRM built specifically for Pakistani SMEs.

**Market context:**
- Currency: PKR only (Lakh/Crore notation via `pkr()`)
- Primary communication channel: WhatsApp (not email, not phone)
- Payment processors: JazzCash + Easypaisa (in STUB state for C6 — live credentials pending OA-003)
- Identity documents: CNIC (XXXXX-XXXXXXX-X), NTN (7-digit)
- Phone format: E.164 `+92` prefix + 10 digits
- Dates: DD/MM/YYYY, timezone PKT (UTC+5)
- Language: English UI with RTL wired for Urdu (day-1 requirement per C-001)
- Compliance: PTA hooks built in adapters — do not remove

**Current state:** All 75 custom pages are BUILT, browser-approved, and wired to live API. This brief governs maintenance, QA, and future design iteration — not initial construction. All pages have status ⏳ (live-API re-verification pending Phase 6 Component 3).

**Authority reference:** `D:\SaaS\CRM\docs\03_frontend_authority\FRONTEND_AUTHORITY_MASTER.md`

---

## 2 — Technology Stack

**Frontend stack is frozen. No new frameworks may be introduced.**

| Layer | Technology | Notes |
|---|---|---|
| CSS framework | NexLink (Bootstrap 5 derivative) | NexLink class chains only. Documented in FRAMEWORK.md §30. |
| Custom CSS | `crm-custom.css` | MUST be linked on every custom app page after `styles.css`. Contains DataTables v2 header fix. |
| Shell JS | `crm-shell.js` | Injects header, sidebar, footer at runtime. Pages own `<main>` only. |
| API layer | `crm-api.js` | DUMMY_MODE: false for production. Fallback to `crm-dummy.js` on error. |
| Currency | `pkr()` in `crm-components.js` | ALL PKR amounts must use pkr(). Never format manually. |
| Locale/RTL | `crm-locale.js` | RTL toggle wired day-1. Mandatory in inbox pages for Urdu bubbles. |
| Charts | ApexCharts | Primary chart library for all dashboards. Chart.js is library demo only. |
| Date picker | flatpickr | Used on all Archetype H date-range filters. |
| Data tables | DataTables v2 | v2 API only — no v1 syntax. |
| Auth | JWT HS256 | 15-min access tokens; 7-day HttpOnly refresh cookie. |
| Idempotency | UUID v4 header | Required on ALL POST/PUT/PATCH requests. |

**Prohibited (never introduce):**
- React, Vue, Angular, Svelte, or any SPA framework
- Flutter or any mobile-native framework
- TypeScript (all JS is vanilla ES6)
- Webpack, Vite, or any build bundler (pure static files)
- Tailwind CSS or any non-Bootstrap utility framework

---

## 3 — Page Counts

| Category | Count | Location |
|---|---|---|
| Custom CRM pages (Archetypes A–M) | 75 | `frontend/src/app/*.html` (custom files) |
| NexLink library pages | 94 | `frontend/src/app/*.html` (library demos) |
| **Total** | **169** | |

**Dev server:** `npm run serve` from `D:\SaaS\CRM\frontend`, port 3001

---

## 4 — The 13 Archetypes (A–M)

| ID | Archetype Name | Page Count | Representative Pages | Key UI Patterns |
|---|---|---|---|---|
| A | Dashboard / KPI Overview | 13 | dashboard.html, sales-dashboard.html, support-dashboard.html | 5-zone layout FIXED: (1) posture strip → (2) primary KPI cards → (3) execution queue DataTable → (4) trend chart → (5) risk/anomaly panel. All 5 zones required. ApexCharts for trend/risk charts. |
| B | List / Queue / Table View | 11 | leads.html, followups.html, cases.html, collections.html | Filter chips (nav-pills-custom) before DataTable. Overdue/at-risk rows pinned first. Max 3 quick actions per row. Bulk actions strip. |
| C | Entity Detail / 360 View | 12 | leads-detail.html, contacts-detail.html, cases-detail.html, quotes-detail.html | Sticky identity strip (entity name/ID, status badge, primary action buttons). Split pane: main content (col-lg-8) + context panel (col-lg-4). Inline edit with explicit save. Activity timeline. `style="height:auto"` on all context panel cards. |
| D | Sales Cockpit | 1 | sales-cockpit.html | Pipeline execution rail + kanban deal workspace + forecast context panel + next-actions panel. Stage progression is the P0 action. |
| E | Support Console | 1 | support-console.html | 3-pane: SLA queue (left) / conversation thread (centre) / context panel (right). SLA queue sorted by due-time. Escalation controls deterministic. |
| F | Marketing Workspace | 1 | marketing-workspace.html | Campaign lifecycle: Draft → segment → activate → attribute. KPI cards + campaigns DataTable + filter chips. |
| G | Settings / Admin / RBAC | 9 | org-settings.html, user-management-crm.html, roles.html, integrations.html | Two-pane: list-group left nav (NEVER nav-pills) + content panel. `pb-4` on container. `style="height:auto"` on all right-column stacked cards. Default-deny. 2-step confirm for destructive ops. |
| H | Reporting / Analytics | 7 | sales-analytics.html, finance-analytics.html, audit-report.html, report-builder.html | flatpickr date-range filter FIRST (required). Chart grid. DataTable drilldown at bottom. |
| I | Form / Wizard / CPQ | 6 | lead-new.html, contact-new.html, case-new.html, quote-builder.html | ≤2 steps enforced. Step 1: required fields only. Step 2: optional/confirmation. Phone E.164 validation + dedup warn on blur. CPQ (I-05) is 4-step exception. |
| J | Audit / Compliance | 5 | audit-log.html, compliance-report.html, data-governance.html, rbac-audit.html | Immutable read-only. No create/edit/delete controls anywhere. Hash-chain verification visible on J-01, H-06. Signed CSV export where applicable. |
| K | Builder / Visual Canvas | 4 | workflow-builder.html, object-builder.html, rule-builder.html, approval-lanes.html | 3-pane canvas (palette/canvas/inspector) or kanban board. 1:1 UI↔DSL mapping. Validate/simulate before publish. |
| L | Inbox / Communication | 3 | inbox.html, inbox-thread.html, routing-config.html | RTL MANDATORY in L-02 for Urdu WhatsApp bubbles. WhatsApp is primary channel tab. Thread-first. Voice note transcription icon disabled (SD-006). |
| M | AI / Copilot | 2 | ai-copilot.html, ai-insights.html | Advisory-only banner REQUIRED on both pages. All suggestions must cite observed data. No ungrounded inference. Rule-based only for C6 (SD-003). |

**Spec docs (in `D:\SaaS\CRM\docs\`):**

| Archetype | Spec Doc |
|---|---|
| A | b9-p01-dashboard-kpi.md |
| B | b9-p02-list-queue.md |
| C | b9-p06-entity-detail.md |
| D | b9-p03-sales-cockpit.md |
| E | b9-p04-support-console.md |
| F | b9-p05-marketing-workspace.md |
| G | b9-p09-settings-admin.md |
| H | b9-p10-reporting-analytics.md |
| I | b9-p11-form-wizard.md |
| J | b9-p12-audit-compliance.md |
| K | b9-p07-workflow-visual-ui.md + b9-p08-builder-extensions.md |
| L | b9-p13-inbox-communication.md |
| M | b9-p14-ai-copilot.md |

---

## 5 — Users: 7 Canonical Roles

Use ONLY these role names. No others exist.

| Role | One-Line Description |
|---|---|
| `tenant_owner` | Full platform owner — all 91 scopes, all 75 pages, exclusive access to tenant dashboard and feature flags. |
| `tenant_admin` | Organisation administrator — 35 scopes, 73 of 75 pages, all admin/settings/audit except tenant provisioning and feature flags. |
| `manager` | Team lead — 25 scopes, manages pipelines/teams, approves quotes/workflows/cases, cannot access Settings/Admin sub-menus (except Territories and Routing). |
| `agent` | Standard CRM agent — 12 scopes, operational pages only (leads, contacts, cases, inbox), no analytics/admin/finance/marketing. |
| `analyst` | Read-only observer — read access across leads/contacts/accounts/collections/payments/cases/knowledge + AI scores, no write anywhere. |
| `auditor` | Compliance reader — audit log and compliance read only (`admin.read_audit_logs`), limited to J-series pages and H-06. |
| `integration_service` | Machine-to-machine — API access only, no frontend pages, no human login. |

**Role hierarchy shorthand (for gating patterns only — server uses scopes):**
- "All roles" = all 7 canonical roles
- "agent+" = agent, manager, tenant_admin, tenant_owner
- "manager+" = manager, tenant_admin, tenant_owner
- "admin only" = tenant_admin, tenant_owner
- "owner only" = tenant_owner

---

## 6 — Current State

- All 75 custom pages: **BUILT** — built, browser-approved, wired to live backend API
- All 94 library pages: **UNCHANGED** — NexLink demos, no custom authority needed
- Build phases 1–8: **ALL COMPLETE**
- DUMMY_MODE: **false** (crm-api.js set to live mode)
- Status markers in DESIGN-SPEC.md: ⏳ means "pending full live-API re-verification" (Phase 6 Component 3) — it does NOT mean the page is incomplete

**This brief governs:**
- Maintenance and bug fixes on existing pages
- QA and re-verification work
- Future design iteration within C6 scope
- Design handoffs to Claude Design for any page rebuild

---

## 7 — Design Priorities

In priority order:

1. **RBAC-aware** — every permission-gated control must check the JWT `scopes[]` array. Hide on 403; never show raw errors. See `L0_DESIGN_CONSTRAINTS_FOR_CLAUDE_DESIGN.md`.
2. **Pakistan-first** — PKR via pkr(), WhatsApp prominent, E.164 phone, DD/MM/YYYY dates, CNIC/NTN formats. Never USD, never international number formats.
3. **Shell-managed** — crm-shell.js owns header/sidebar/footer. Pages own `<main>` only. No hardcoded footers.
4. **DataTable alignment** — 3-place rule: dt-head-center on ALL `<th>`, className in JS column def, !important overrides in crm-custom.css.
5. **Responsive** — mobile-first, usable at 360px viewport. P0 actions reachable in ≤2 layers on mobile.
6. **4-state coverage** — every screen handles Loading (skeleton), Empty (message + CTA), Error (friendly message + retry), Success (live data).

---

## 8 — Known Constraints (Safe Defaults Active for C6)

| ID | Constraint | Frontend Effect |
|---|---|---|
| SD-001 | `contacts.delete` scope absent from rbac-scopes.js | Hide delete button on contacts.html and contacts-detail.html for ALL roles |
| SD-002 | JazzCash/Easypaisa credentials not obtained (P-016) | Show STUB state on billing-settings.html, invoices-detail.html, collections.html — no live payment form |
| SD-003 | AI model unselected for C6 | Show "Rule-based advisory — LLM inference deferred to C7" banner on ai-copilot.html and ai-insights.html |
| SD-004 | Urdu strings pending native speaker review (P-017) | EN strings only on notifications.html; Urdu strings exist but blocked |
| SD-005 | Facebook/Instagram Meta Business Manager setup pending | Facebook/Instagram source option hidden on lead-new.html |
| SD-006 | Voice note transcription vendor evaluation pending | Microphone/transcription icon disabled in inbox-thread.html |
| SD-007 | Contracts module deferred to C7 | No contracts page exists; do not build |
| SD-008 | Kuickpay not in scope | Kuickpay option hidden on billing-settings.html |
| SD-009 | Custom objects gateway route unconfirmed (D-002) | object-builder.html (K-02) is advisory visual shell only — no live API calls |
| SD-010 | JWT logout does not revoke refresh token | Security note only — no UX impact |
| SD-011 | SHA-256 password hashing for C6 | Compliance note only — no UX impact |
| SD-012 | PTA/FBR compliance hooks built, legal review pending | Do not remove compliance hooks from adapters |

**Remaining owner confirmations with frontend impact:**
- OA-001: contacts.delete RBAC code fix — when resolved, show delete button for tenant_admin and tenant_owner on contacts pages (no HTML changes needed — JWT will contain the scope)
- OA-003: JazzCash/Easypaisa credentials — when resolved, activate live payment form in G-04 and C-08

**Out of scope for C6:**
- Contracts module (C7 — requires v1-contracts.routes.js first)
- LLM AI inference (C7 AI sprint)
- Urdu campaign templates (P-017 review completion required)
- Custom objects live API (D-002 gateway confirmation required)

---

## 9 — Authority Reference

All frontend authority is captured in `D:\SaaS\CRM\docs\03_frontend_authority\`. The canonical read order:

| File | Purpose |
|---|---|
| `FRONTEND_AUTHORITY_MASTER.md` | Master authority index |
| `FRONTEND_ROUTE_CATALOG.md` | All 169 routes |
| `FRONTEND_SCREEN_CATALOG.md` | 75 custom screens with full field contracts |
| `FRONTEND_NAVIGATION_MODEL.md` | Sidebar structure + role visibility |
| `FRONTEND_ROLE_EXPERIENCE_MATRIX.md` | Per-role page access matrix |
| `FRONTEND_PERMISSION_MATRIX.md` | Scope-to-UI-element mapping |
| `FRONTEND_WORKFLOW_TO_SCREEN_MAP.md` | 10 workflows mapped to screens |
| `FRONTEND_API_DEPENDENCY_MAP.md` | All 228 API endpoints mapped to consumers |
| `FRONTEND_GAP_REGISTER.md` | Resolved gaps + safe defaults |
| `L0_FRONTEND_AUTHORITY_INPUT_FREEZE.md` | L0 frozen inputs (sections 1–10) |
| `L0_ROUTE_SCREEN_WORKFLOW_MATRIX.md` | Complete 169-page cross-reference matrix |
| `L0_DESIGN_CONSTRAINTS_FOR_CLAUDE_DESIGN.md` | Hard build rules for Claude Design |
| `L0_CLAUDE_DESIGN_BRIEF.md` | This file — orientation brief |

**CLAUDE.md build checklist** (`D:\SaaS\CRM\CLAUDE.md`) overrides default behavior for any custom page build.
**FRAMEWORK.md §31** is the authoritative frontend build protocol.
**DESIGN-SPEC.md §2** lists 10 design constraints that apply to all 75 custom pages.

---

## Freeze Verdict

**L0 FROZEN**

Basis: Zero blocking frontend gaps (confirmed by FRONTEND_GAP_REGISTER.md, DETERMINISM_CERTIFICATION_REPORT.md, POST_COLLAPSE_FRONTEND_READINESS.md). All 75 custom pages built and specified. All 7 roles documented. All 10 workflows mapped. All 169 routes catalogued.

---

*End L0_CLAUDE_DESIGN_BRIEF.md*
*Pakistan CRM OS — Phase C6 — L0 FROZEN — 2026-06-24*
