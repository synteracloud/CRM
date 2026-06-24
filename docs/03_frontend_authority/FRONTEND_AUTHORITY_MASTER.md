---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Phase: C6 (Commercial Launch)
Derived From: DESIGN-SPEC.md, FEATURE_SCOPE.md, PRODUCT_WORKFLOWS.md, DOMAIN_MODEL.md, USER_ROLES_AND_PERMISSIONS.md, API_CONTRACT.md, FULLSTACK_STITCHING_CONTRACT.md, POST_COLLAPSE_FRONTEND_READINESS.md, DETERMINISM_CERTIFICATION_REPORT.md, AI_OPERATING_CONTEXT.md
---

# FRONTEND AUTHORITY MASTER — Pakistan CRM OS

## Purpose

This document is the single authoritative reference for the entire Pakistan CRM frontend. Every screen, route, permission, role experience, and navigation path documented here is derived from verified backend reality. No invention is permitted. All claims trace to the authority docs listed in the header.

---

## 1. Frontend Overview

### Technology Stack

| Layer | Technology | Source |
|---|---|---|
| CSS Framework | NexLink (Bootstrap 5 derivative) | FRAMEWORK.md §30 |
| Custom CSS | crm-custom.css (DataTables v2 alignment fix + table overrides) | CLAUDE.md §0 |
| Shell JS | crm-shell.js (sidebar, header, footer injection) | CLAUDE.md §1 |
| API Layer | crm-api.js (DUMMY_MODE: false, graceful fallback to crm-dummy.js) | AI_OPERATING_CONTEXT.md |
| Charts | ApexCharts (primary), Chart.js (library reference) | DESIGN-SPEC.md build notes |
| Date Picker | flatpickr | H-02, H-03, H-05 build notes |
| Data Tables | DataTables v2 | CLAUDE.md §2 |
| Currency | PKR only, lakh/crore notation via pkr() in crm-components.js | DESIGN-SPEC.md §2 C-004 |
| Locale | RTL supported via crm-locale.js toggle | DESIGN-SPEC.md §2 C-001 |
| Auth | JWT HS256, 15-min access token, 7-day HttpOnly refresh cookie | AUTH_AND_TENANCY_CONTRACT.md |
| Deployment | Render.com static site (frontend service) | AI_OPERATING_CONTEXT.md |

### Page Counts

| Category | Count | Description |
|---|---|---|
| Total pages | 169 | All .html files in frontend/src/app/ |
| Custom CRM pages | 75 | Archetype-driven, full authority required |
| NexLink library pages | 94 | Component demos, no custom authority |

### Custom Pages by Archetype

| Archetype | Name | Page Count |
|---|---|---|
| A | Dashboard / KPI Overview | 13 |
| B | List / Queue / Table View | 11 |
| C | Entity Detail / 360 View | 12 |
| D | Sales Cockpit | 1 |
| E | Support Console | 1 |
| F | Marketing / Campaign Workspace | 1 |
| G | Settings / Admin / RBAC | 9 |
| H | Reporting / Analytics | 7 |
| I | Form / Wizard / CPQ | 6 |
| J | Audit / Compliance | 5 |
| K | Builder / Visual Canvas | 4 |
| L | Inbox / Communication | 3 |
| M | AI / Copilot | 2 |
| **TOTAL** | | **75** |

---

## 2. Derivation Statement

This authority model derives entirely from these backend-verified source documents, in authority order:

1. **DESIGN-SPEC.md** — Master screen inventory, 75 custom pages, 13 archetypes, 8 build phases. Status of all pages.
2. **docs/00_authority/FEATURE_SCOPE.md** — 131 features, 22 modules, C0–C6 phase gates, feature freeze status.
3. **docs/00_authority/PRODUCT_WORKFLOWS.md** — 5 primary + 5 system workflows, event bus, step definitions, API calls per step.
4. **docs/00_authority/DOMAIN_MODEL.md** — 37+ entities, 18 DB schemas, relationships, business rules, state machines.
5. **docs/03_fullstack_contracts/USER_ROLES_AND_PERMISSIONS.md** — 7 roles, 91 scopes (from rbac-scopes.js), RBAC enforcement model.
6. **docs/01_backend/API_CONTRACT.md** — 228 endpoints, 44 route groups, auth flow, pagination, error codes.
7. **docs/00_authority/FULLSTACK_STITCHING_CONTRACT.md** — 22 module stitch entries, feature→entity→API→page→permission traceability.
8. **docs/08_reports/POST_COLLAPSE_FRONTEND_READINESS.md** — GO verdict, stable assumptions, constraints to document.
9. **docs/08_reports/DETERMINISM_CERTIFICATION_REPORT.md** — Certified stable items for Frontend Authority Capture.
10. **docs/07_governance/AI_OPERATING_CONTEXT.md** — Current operating state, frozen decisions, known constraints.

**No data in this authority model is invented.** Where gaps exist between documented frontend and backend, they are recorded in FRONTEND_GAP_REGISTER.md.

---

## 3. Module Summary Table

| Module | Pages | Archetype | Build Phase | Status |
|---|---|---|---|---|
| Lead Management | leads.html, leads-detail.html, lead-new.html, leads-dashboard.html | B, C, I, A | Phase 1+2 | Built ⏳ |
| Follow-up Enforcement | followups.html | B | Phase 1 | Built ⏳ |
| Contacts | contacts.html, contacts-detail.html, contact-new.html, contacts-health.html | B, C, I, A | Phase 1+8 | Built ⏳ |
| Accounts | accounts.html, accounts-detail.html | B, C | Phase 8 | Built ⏳ |
| Sales / Opportunities | opportunities-detail.html, opportunity-new.html, sales-cockpit.html, sales-dashboard.html | C, I, D, A | Phase 2 | Built ⏳ |
| CPQ / Quotes & Orders | quote-builder.html, quotes-detail.html, quotes-dashboard.html, orders-detail.html | I, C, A, C | Phase 2 | Built ⏳ |
| Finance / Collections | collections.html, invoices.html, invoices-detail.html, finance-analytics.html | B, B, C, H | Phase 3 | Built ⏳ |
| Subscriptions / Billing | subscriptions-dashboard.html, subscriptions-detail.html, billing-settings.html | A, C, G | Phase 3+6 | Built ⏳ |
| Support / Cases | cases.html, cases-detail.html, case-new.html, support-console.html, support-dashboard.html | B, C, I, E, A | Phase 4 | Built ⏳ |
| Knowledge Base | knowledge-article.html, knowledge-dashboard.html | C, A | Phase 4+8 | Built ⏳ |
| Omnichannel Inbox | inbox.html, inbox-thread.html, routing-config.html | L | Phase 5 | Built ⏳ |
| Marketing / Campaigns | marketing-workspace.html, marketing-analytics.html, campaign-new.html, engagement-dashboard.html | F, H, I, A | Phase 5+7 | Built ⏳ |
| Workflow Automation | workflow-builder.html, workflow-run-detail.html, workflows-dashboard.html, workflow-analytics.html | K, C, A, H | Phase 7+8 | Built ⏳ |
| AI / Copilot | ai-copilot.html, ai-insights.html | M | Phase 8 | Built ⏳ |
| Territories | territories.html | G | Phase 6 | Built ⏳ |
| Partners | partners.html, partners-detail.html | B, C | Phase 8 | Built ⏳ |
| Identity & Access | users.html, user-management-crm.html, identity-dashboard.html | B, G, A | Phase 6+8 | Built ⏳ |
| Audit & Compliance | audit-log.html, compliance-report.html, data-governance.html, rbac-audit.html, privacy.html, audit-dashboard.html, audit-report.html | J, H, A | Phase 8 | Built ⏳ |
| Settings / Admin | org-settings.html, integrations.html, notifications.html, feature-flags.html, compliance.html, roles.html | G | Phase 6 | Built ⏳ |
| Builder Tools | object-builder.html, rule-builder.html, approval-lanes.html | K | Phase 8 | Built ⏳ |
| Report Builder | report-builder.html, sales-analytics.html, support-analytics.html | H | Phase 8 | Built ⏳ |
| Tenant Admin | tenants-dashboard.html | A | Phase 8 | Built ⏳ |

---

## 4. Key Constraints

### Multi-tenancy
- All data scoped to `tenant_id` — never mixed across tenants
- `x-tenant-id` header extracted from JWT by gateway middleware automatically
- Frontend never sets this header manually
- Semgrep CI enforces tenant isolation in all SQL queries

### RBAC
- 7 canonical roles: tenant_owner, tenant_admin, manager, agent, analyst, auditor, integration_service
- 91 permission scopes — all explicit (no hierarchical inheritance)
- Scopes delivered in JWT `scopes[]` array
- Frontend must show/hide UI elements based on scope presence
- Frontend must never rely on role name alone — use scopes
- Server always enforces; client-side is convenience only
- Default-deny: missing scope = 403; frontend must handle 403 gracefully

### Pakistan-Market Specifics
- **Currency:** PKR only. No multi-currency. Lakh/Crore formatting above 99,999 via `pkr()`.
- **WhatsApp:** Primary interaction channel. Inbound messages auto-create Contacts and Leads.
- **Phone format:** E.164 `/^\+92[0-9]{10}$/` — validated on all contact/lead forms.
- **Payment rails:** JazzCash and Easypaisa — currently STUB (P-016 pending credentials).
- **RTL:** Infrastructure wired (crm-locale.js); day-1 requirement per C-001.
- **Timezone:** PKT (UTC+5) for all timestamp display.

### DUMMY_MODE
- `DUMMY_MODE: false` in crm-api.js (set in C1)
- All 75 pages make live API calls with graceful fallback to crm-dummy.js
- 5 pages confirmed fully wired: integrations.html, report-builder.html, data-governance.html, engagement-dashboard.html, billing-settings.html (G-04 wired but blocked by P-016)

### Idempotency
- Frontend MUST generate `Idempotency-Key` header on all POST/PUT/PATCH requests
- Duplicate key + same body → replayed response (200 with `meta.idempotency.replayed: true`)
- Duplicate key + different body → 409 conflict

---

## 5. Safe Defaults in Effect

The following safe defaults apply to all frontend UI decisions. They are derived from POST_COLLAPSE_FRONTEND_READINESS.md Phase 2.95 collapse.

| ID | Safe Default | Applies To | Documentation Requirement |
|---|---|---|---|
| SD-001 | contacts.delete — hide for all roles; document as OA-001 pending | contacts.html, contacts-detail.html | "Delete not available — OA-001 pending scope grant" |
| SD-002 | JazzCash/Easypaisa — display stub state, not live payment form | billing-settings.html (G-04), invoices-detail.html | "Payment processing stub — P-016 pending credentials" |
| SD-003 | AI features — display rule-based advisory, not LLM inference | ai-copilot.html (M-01), ai-insights.html (M-02) | "Rule-based advisory — LLM inference deferred to C7" |
| SD-004 | Notification strings — EN only (no Urdu) | notifications.html (G-06) | "Urdu strings blocked — P-017 pending review" |
| SD-005 | Facebook/Instagram lead capture — hidden | lead-new.html | Hidden div with data-unblock="MR-001" |
| SD-006 | Voice note transcription — disabled | inbox-thread.html (L-02) | Microphone icon disabled |
| SD-007 | Contracts page — not in C6 scope | N/A | Deferred to C7 |
| SD-008 | Kuickpay — hidden | billing-settings.html | data-unblock="MR-007" |
| SD-009 | Custom objects routing — advisory shell only | object-builder.html (K-02) | D-002 pending resolution |
| SD-010 | JWT logout does not revoke refresh token | Auth flow | Security note; no UX impact |
| SD-011 | Password hashing is SHA-256 for C6 | Auth flow | bcrypt migration deferred to C7 |
| SD-012 | PTA/FBR compliance — hooks built, legal review pending | WhatsApp campaigns, invoices | Compliance notes in UI where applicable |

---

## 6. Remaining Owner Decisions and Frontend Impact

All 9 Phase 2.95 decisions are collapsed. Only OA-003 is a TRUE_OWNER_DECISION (requires human sign-off):

| Decision | Status | Frontend Impact |
|---|---|---|
| OA-001: contacts.delete RBAC | OWNER_CONFIRMATION_ONLY → Option A (add scope to tenant_admin) | Hide delete button; SD-001 in effect |
| OA-002: JTI blocklist Redis migration | OWNER_CONFIRMATION_ONLY → defer post-C6 | No frontend impact |
| OA-003: JazzCash/Easypaisa credentials | TRUE_OWNER_DECISION — isolated | G-04 stub state documented; no page changes needed |
| OA-004: AI inference model | OWNER_CONFIRMATION_ONLY → rule-based for C6 | M-01, M-02 documented as rule-based shells |
| OA-005: Contracts gateway route | RESOLVED → defer to C7 | No C6 frontend page needed |
| OA-006–OA-009 | Documentation/auth concerns only | No frontend impact |

**None of these block frontend authority documentation.** The authority model is complete for C6 scope.

---

## 7. How to Use This Authority Model

1. **To understand a specific page** — go to FRONTEND_SCREEN_CATALOG.md, find by page ID (A-01 through M-02) or filename.
2. **To understand what a role can see** — go to FRONTEND_ROLE_EXPERIENCE_MATRIX.md, find the role.
3. **To understand what a permission controls** — go to FRONTEND_PERMISSION_MATRIX.md, find the scope.
4. **To trace a workflow through the UI** — go to FRONTEND_WORKFLOW_TO_SCREEN_MAP.md.
5. **To find which pages call a given API endpoint** — go to FRONTEND_API_DEPENDENCY_MAP.md.
6. **To understand navigation** — go to FRONTEND_NAVIGATION_MODEL.md.
7. **To understand dashboards** — go to FRONTEND_DASHBOARD_CATALOG.md.
8. **To find gaps** — go to FRONTEND_GAP_REGISTER.md.
9. **To verify readiness** — go to FRONTEND_AUTHORITY_READINESS_REPORT.md.

---

*End FRONTEND_AUTHORITY_MASTER.md*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
