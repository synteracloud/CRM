---
Status: L0 FROZEN
Authority Level: Critical
Freeze Date: 2026-06-24
Phase: C6 (Commercial Launch)
Derived From: CLAUDE.md, FRAMEWORK.md, FRONTEND_AUTHORITY_MASTER.md, FRONTEND_PERMISSION_MATRIX.md,
  FRONTEND_NAVIGATION_MODEL.md, DESIGN-SPEC.md, SAFE_DEFAULT_REGISTER.md
---

# L0 DESIGN CONSTRAINTS FOR CLAUDE DESIGN — Pakistan CRM OS

Hard constraints that Claude Design MUST obey during any archetype, UX, or maintenance work.
Violations of these constraints produce broken pages. All rules are derived from authority documents.

---

## Technology Constraints

**Frontend stack is frozen. No new frameworks may be introduced.**

| Layer | Approved Technology | Constraint |
|---|---|---|
| CSS Framework | NexLink (Bootstrap 5 derivative) | Only NexLink classes and Bootstrap 5 utilities. No Tailwind, no Bulma. |
| Custom CSS | crm-custom.css | MUST be linked on every custom app page. Without it, DataTable headers render misaligned. |
| Shell JS | crm-shell.js | MUST be included on every custom app page. Injects header, sidebar, footer at runtime. |
| API Layer | crm-api.js | DUMMY_MODE: false. Live API calls with graceful fallback to crm-dummy.js. |
| Charts | ApexCharts (primary), Chart.js (library reference) | Use ApexCharts for all dashboard charts. Chart.js is the NexLink library demo only. |
| Date Picker | flatpickr | Used on H-02, H-03, H-05 and all Archetype H date-range filters. |
| Data Tables | DataTables v2 | All sortable/filterable data tables. v2 API only — no v1 syntax. |
| Currency Formatter | pkr() in crm-components.js | ALL PKR amounts must use pkr(). Never format PKR manually. |
| Locale / RTL | crm-locale.js toggle | RTL is wired and required (day-1 per C-001). Inbox pages require RTL for Urdu message bubbles. |
| Auth | JWT HS256 | 15-min access tokens. 7-day HttpOnly refresh cookie. Frontend never sets x-tenant-id. |
| Idempotency | UUID v4 header | Frontend MUST generate Idempotency-Key header (UUID v4) on ALL POST/PUT/PATCH requests. |

**Prohibited Technologies (never introduce):**
- React, Vue, Angular, Svelte, or any SPA framework
- Flutter or any mobile-native framework
- TypeScript (all frontend JS is vanilla ES6)
- Webpack, Vite, or any build bundler (pure static files)
- Tailwind CSS or any non-Bootstrap utility framework

---

## Layout Constraints

### Shell Ownership Rule

crm-shell.js owns the header, sidebar, and footer. Custom pages MUST NOT duplicate any shell element.

| Element | Owner | Page Rule |
|---|---|---|
| `<aside class="app-menubar-tabs">` | crm-shell.js | NEVER include in page HTML. crm-shell.js injects it. |
| `<header class="app-header">` | crm-shell.js | NEVER include in page HTML. |
| `<footer>` | crm-shell.js | NEVER include in page HTML. Shell injects via `main.insertAdjacentHTML('afterend', FOOTER_HTML)` at line 532. Any hardcoded footer produces a double footer. |
| Page `<main>` | Page HTML | Every custom page owns its `<main>` content area only. |

**AI / Copilot pages exception:** Pages in the ai/ archetype (M-01, M-02) may have different shell structures — always read the seed file before building and copy the shell verbatim if it differs from standard.

### Card Height Rule

NexLink `.card` CSS sets `height: calc(100% - var(--bs-gutter-x))`. This clips content in three patterns. Always apply `style="height:auto"`.

| Pattern | When to Apply | Example |
|---|---|---|
| A — Identity strip / col-12 standalone card | Single card in a full-width row | `<div class="card mb-0" style="height:auto">` |
| B — Multiple stacked cards in same column | 2+ cards stacked vertically in a col-* | Every card in the stack: `style="height:auto"` |
| C — Context panel cards (col-lg-4 sidebar) | All cards in a detail page right-side panel | Every card in the panel: `style="height:auto"` |

When in doubt: add `style="height:auto"`. The only case where omitting it is intentional: equal-height columns side-by-side (single card per column, matching height is desired).

### Settings Pages Layout Rule

Settings pages (Archetype G) use a two-pane layout. Never use nav-pills inside the page body for the settings left nav.

| Element | Correct Pattern | Prohibited Pattern |
|---|---|---|
| Settings left nav | `<div class="list-group list-group-flush">` with `list-group-item list-group-item-action` | `<ul class="nav nav-pills">` — causes NexLink sidebar CSS bleed |
| Settings container | `<div class="container-fluid pb-4">` | Without `pb-4` — last card is flush against footer |
| Right-column stacked cards | `style="height:auto"` on every card | Omitting height:auto clips content |

### crm-custom.css Inclusion Rule

Every custom app page MUST have this line in `<head>`, after `styles.css`:

```html
<link rel="stylesheet" href="assets/css/crm-custom.css">
```

crm-custom.css contains the DataTables v2 header-centering fix and all table-specific alignment overrides. Omitting it breaks all DataTable column header alignment.

### Page Link Format

All internal page links MUST use the `app/xxx.html` format. Never use bare filenames or subfolder paths.

| Correct | Prohibited |
|---|---|
| `href="app/dashboard.html"` | `href="dashboard.html"` |
| `href="app/leads.html"` | `href="leads/index.html"` |
| `href="app/contacts-detail.html"` | `href="../contacts-detail.html"` |

---

## RBAC / Permission Constraints

**Core rule:** Frontend hides/disables UI elements based on scope presence in JWT. Server always enforces. A 403 must be handled gracefully — never show a raw error to the user.

### Scope-Gating Requirement

Every permission-gated UI control must check the corresponding scope from the JWT `scopes[]` array before rendering.

| Control Type | Rule |
|---|---|
| Delete buttons | Hidden when corresponding delete scope is absent. ALWAYS hidden for contacts.delete (SD-001 in effect). |
| Admin-only sections | Check against FRONTEND_PERMISSION_MATRIX.md for exact scope required per page. |
| Approve/Reject buttons | quotes.approve required. Hidden for agent and analyst. |
| Close/Resolve buttons | cases.close required. Hidden for agent. |
| Publish buttons | knowledge.publish / workflows.publish required. Hidden for agent/analyst. |
| Feature Flags page | admin.manage_feature_flags required. Accessible to tenant_owner only. |
| Tenant Dashboard | admin.manage_tenants required. Accessible to tenant_owner only. |

### Viewer / Analyst Role Rule

analyst role: read-only UI on all accessible pages. No create, edit, delete, or action buttons visible.

### Role Hierarchy for UI Decisions (not RBAC — for gating patterns only)

When scope-gating needs a shorthand:
- "All roles" = tenant_owner, tenant_admin, manager, agent, analyst, auditor (all 7 canonical roles)
- "agent+" = agent, manager, tenant_admin, tenant_owner
- "manager+" = manager, tenant_admin, tenant_owner
- "admin only" = tenant_admin, tenant_owner
- "owner only" = tenant_owner

Never use these as substitutes for actual scope checks. The server uses scopes, not role names.

---

## Pakistan-Market Constraints

These are non-negotiable. Pakistan CRM is built for Pakistani SMEs.

### Currency

| Rule | Detail |
|---|---|
| Currency: PKR only | No multi-currency. No USD display. No currency selector. |
| Format: PKR X,XX,XXX | Lakh/crore notation via `pkr()` in crm-components.js for values above 99,999. |
| Never raw number | Always run amounts through pkr() before display. |
| Payment processors | JazzCash + Easypaisa shown as STUB until OA-003 resolved. No live payment form. |

### Phone Format

- E.164 format: `+92` prefix followed by 10 digits
- Pattern: `/^\+92[0-9]{10}$/`
- Validation: enforce on all contact and lead creation forms
- Dedup: warn on blur if phone already exists in system

### Identity Document Formats

| Document | Format | Applicable Pages |
|---|---|---|
| CNIC | XXXXX-XXXXXXX-X | contact-new.html (I-02), contacts-detail.html (C-02) |
| NTN | 7-digit | org-settings.html (G-01), contacts where applicable |

### WhatsApp Priority

WhatsApp is the primary communication and lead capture channel for Pakistan market.

- **Inbox pages (L-01, L-02):** WhatsApp channel is the primary tab / first filter chip
- **Contact/Lead UI:** WhatsApp opt-in status and last WhatsApp contact must be prominent
- **Campaign builder (I-06):** WhatsApp blast is the primary campaign type
- **Engagement dashboard (A-08):** WhatsApp opt-in rate is the primary KPI
- **RTL:** Mandatory in inbox-thread.html (L-02) for Urdu message content in WhatsApp bubbles
- **PTA compliance:** Compliance hooks are built in adapters. Do not remove. P-012 pending.

### Date / Time Format

- Display format: DD/MM/YYYY
- Timezone: PKT (UTC+5) for all timestamp display
- SLA timers on cases-detail.html (C-05) and support-console.html (E-01): PKT display

---

## Filter / Tab Constraints

### Filter Chip Pattern

All tab-style filter strips MUST use NexLink nav-pills-custom. Never Bootstrap btn-group.

**Correct pattern:**
```html
<ul class="nav nav-pills nav-pills-custom p-1 bg-light rounded-5" id="FILTER_ID" role="tablist">
  <li class="nav-item"><button type="button" class="nav-link rounded-5 active" data-filter="">All</button></li>
  <li class="nav-item"><button type="button" class="nav-link rounded-5" data-filter="active">Active</button></li>
</ul>
```

**Prohibited pattern:** `<div class="btn-group btn-group-sm">` with `btn-outline-secondary` — produces 80s segmented button look.

**JS compatibility:** `$('#FILTER_ID button')` selector and `.active` class toggling are fully compatible with the nav-pills-custom pattern.

---

## DataTable Alignment Constraints

### Three-Place Rule

DataTable column alignment must be set in ALL THREE places simultaneously.

**Place 1 — HTML `<thead>`:**
```html
<th class="dt-head-center">Column Name</th>
```
ALL `<th>` elements on ANY table must be `dt-head-center`. No exceptions. Never use `dt-head-left` or `dt-head-right` on headers.

**Place 2 — JS column definition (data-driven tables only):**
```javascript
{ data: 'field', className: 'dt-body-center' }
```
Only applies when DataTables generates rows from `data:` or `ajax:`. Does NOT apply to pre-built static HTML `<tbody>` rows.

**Place 3 — crm-custom.css (required for ALL data-driven tables):**
```css
#dt_TableName.dataTable tbody > tr > td { text-align: center !important; }
#dt_TableName.dataTable tbody > tr > td:nth-child(1) { text-align: left !important; }
```
Always use `!important`. Without it, DataTables CSS overrides at runtime regardless of specificity.

### Body Alignment Guide

| Content Type | Alignment Class | Examples |
|---|---|---|
| Long task titles, description text | `dt-body-left` | Lead title, case subject, article title, note content |
| Names, IDs, emails, badges, dates, status flags, action buttons | `dt-body-center` | Contact name, lead ID, email, status badge, created_at, action icons |
| Monetary amounts (PKR, USD), numeric totals | `dt-body-right` | Amount (PKR), MRR, total, balance |

### Plain Bootstrap Tables

Tables not using DataTables (plain `<table class="table">`):
- All `<th>` elements: use `text-center` class (Bootstrap utility)
- Body `<td>` elements: use `text-start`, `text-center`, `text-end` as appropriate
- Reference: finance-analytics.html (H-04) plain Bootstrap table pattern

---

## Navigation Constraints

### Sidebar Active States

crm-shell.js manages all sidebar active states. Pages MUST NOT set active states manually in HTML.

The `a([page])` helper in crm-shell.js sets the active link based on the current URL. Do not add `.active` to any sidebar nav item in page HTML.

### Page Link Format

Always use `app/xxx.html` format in all `href` attributes. Never bare filenames, never subfolder paths.

---

## State Constraints

**Every screen must handle all 4 states. No exceptions.**

| State | Required Implementation |
|---|---|
| Loading | Skeleton card/row placeholders that mirror the live card structure. No raw spinners alone. |
| Empty | Descriptive message (explain why empty) + primary action CTA button. |
| Error | User-friendly message (never raw API error) + retry button. Gracefully fall back to crm-dummy.js data where configured. |
| Success | Full live data rendered. Permission-gated elements hidden via scope check. 403 responses handled by hiding the control silently. |

### 403 Handling Rule

When a protected API returns 403:
- The corresponding UI element was scope-gated and should already be hidden
- If the element was visible (scope gating not yet implemented — see G-007), hide it on 403 response
- Never show a 403 error modal to the user for permission-denied scenarios
- A 403 means "this user cannot do this" — hide the control, do not alert

---

## Archetype-Specific Build Rules

### Archetype A (Dashboard) — 5-Zone Layout
All dashboards MUST implement: (1) posture strip → (2) primary KPI cards → (3) execution queue DataTable → (4) trend chart → (5) risk/anomaly panel. All 5 zones are required. Zone order is fixed.

### Archetype B (List/Queue) — Filter First
All list pages MUST have filter chips (nav-pills-custom pattern) before the DataTable. Overdue/at-risk rows pinned first in queue pages (followups, collections, support console queue).

### Archetype C (Entity Detail) — Sticky Identity Strip
All entity detail pages MUST have a sticky identity strip at the top with: entity name/ID, status badge, and primary action buttons (state-gated). Context panel (col-lg-4 right side) uses `style="height:auto"` on every card.

### Archetype G (Settings) — List-Group Nav
Settings left nav MUST use `list-group list-group-flush` with `list-group-item list-group-item-action`. Never nav-pills. Container needs `pb-4`.

### Archetype H (Reporting) — Date Range First
All analytics pages MUST have a flatpickr date-range filter as the first control. Chart grid follows. DataTable drilldown at bottom.

### Archetype I (Form/Wizard) — 2-Step Max
All forms MUST use at most 2 steps. Step 1: required fields only. Step 2: optional/confirmation. Phone field on lead/contact forms: E.164 validation + dedup warning on blur.

### Archetype J (Audit) — Read-Only Immutable
All audit/compliance pages are read-only. No create, edit, or delete controls. Hash-chain verification must be visible where applicable (J-01, H-06).

### Archetype L (Inbox) — RTL Mandatory
Conversation thread (L-02) MUST support RTL for Urdu message bubbles. WhatsApp channel is primary. Voice note transcription icon: disabled (SD-006).

### Archetype M (AI/Copilot) — Advisory Banner
Both AI pages (M-01, M-02) MUST display the "Rule-based advisory — LLM inference deferred to C7" banner. All suggestions must be evidence-anchored (cite the observed data they reference).

---

## Constraints Summary Checklist

Before saving any custom app page, verify:

- [ ] `<link rel="stylesheet" href="assets/css/crm-custom.css">` is in `<head>` after `styles.css`
- [ ] No `<footer>` block in page HTML (crm-shell.js owns it)
- [ ] No `<aside class="app-menubar-tabs">` in page HTML (crm-shell.js owns it)
- [ ] No `<header class="app-header">` in page HTML (crm-shell.js owns it)
- [ ] All `<th>` elements have `dt-head-center` class (DataTables) or `text-center` class (Bootstrap)
- [ ] Stacked cards in same column have `style="height:auto"`
- [ ] All filter strips use `nav nav-pills nav-pills-custom` pattern, not `btn-group`
- [ ] Settings pages use `list-group list-group-flush` for left nav
- [ ] All PKR amounts use `pkr()` formatter
- [ ] All phone inputs validate E.164 `/^\+92[0-9]{10}$/`
- [ ] All 4 UI states handled: Loading / Empty / Error / Success
- [ ] contacts.delete button hidden (SD-001)
- [ ] JazzCash/Easypaisa shows STUB state, not live form (SD-002)
- [ ] AI pages show advisory-only banner (SD-003)
- [ ] All internal links use `app/xxx.html` format
- [ ] crm-shell.js included in script stack
- [ ] Idempotency-Key header generated (UUID v4) on all POST/PUT/PATCH calls in JS

---

*End L0_DESIGN_CONSTRAINTS_FOR_CLAUDE_DESIGN.md*
*Pakistan CRM OS — Phase C6 — L0 FROZEN — 2026-06-24*
