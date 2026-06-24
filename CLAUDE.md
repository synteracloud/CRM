# Pakistan CRM — Claude Instructions

## MANDATORY: Pre-build reading sequence — read these docs before touching any page

Before building or editing any `app/*.html` page, read these in order. No exceptions.

| # | Doc | What to read | Why |
|---|---|---|---|
| 1 | `DESIGN-SPEC.md` §1 + §2 + §3 | Confirm page is in scope (§3). Read design constraints (§2). Note the archetype and its b9-p spec doc. | Scope gate + design rules |
| 2 | `FRAMEWORK.md` §31 | Full frontend build protocol: CSS stack, script stack, shell rules, QC tiers | The authoritative build spec — all CSS/JS stack rules live here |
| 3 | `CLAUDE.md` build checklist (below) | All recurring bug rules: footer, crm-custom.css, DataTable alignment, filter chips | Project-specific overrides on top of FRAMEWORK.md |
| 4 | The b9-p spec doc for the page's archetype | Layout zones, field contracts, API routes for this specific page type | Page-specific requirements |
| 5 | `crm-dummy.js` — the data shape for this page's dataset | Field names, data types, KPI keys | Prevents mismatched field references in JS |

**Only after reading all five** may you read the seed file and start building.

---

## MANDATORY: Scope gate — never touch files outside the approved phase

**Before touching ANY file**, check DESIGN-SPEC.md §4 to confirm the page is in the currently approved build phase.

**Rule:** If a file is not explicitly listed in the current phase's page table, DO NOT touch it — not for bug fixes, not for consistency, not for any reason. Stop and ask first.

**Why this rule exists:** Claude applied bug fixes to 24 unauthorized pages (library pages, unbuilt phases) in a single session after being asked to fix 7 Phase 1 pages only. Out-of-scope changes are never approved implicitly.

**How to apply:**
1. User names a task → identify which page(s) are involved.
2. Cross-check each page against DESIGN-SPEC.md §4 current phase list.
3. If the page is in scope → proceed.
4. If the page is NOT in scope → stop, name the page, and ask for explicit approval before touching it.

---

## MANDATORY: Read the full seed before building any page

Before building any app/ page, use the Read tool on the seed file and read it completely.
Do NOT rely on PowerShell line-count scripts alone — they show numbers, not structure.

**Why this rule exists:** AI section pages (src/ai/*.html) have a completely different body
structure — their own `<aside class="ai-menubar-tabs">` and `<header class="app-header ai-app-header">`
baked into the HTML, no crm-shell.js. This was only discovered after pages were built wrong
and the user caught it in the browser.

**What to verify in every seed before building:**
1. Does it have `<aside class="app-menubar-tabs">` (standard CRM shell) or its own aside?
2. Does it have a standard `<header class="app-header">` or its own, or none?
3. Does its script stack include crm-shell.js? If not, do NOT add it.
4. Are there inter-page links (e.g. `ai/xxx.html`, `forms/xxx.html`) that need rewriting to `app/xxx.html`?
5. Are there extra CSS libs in `<head>` not in the standard stack?

**Rule: if the seed does not have the standard CRM aside/header, copy the full seed verbatim
and only rewrite internal folder paths (e.g. ai/ → app/, forms/ → app/).**

---

## Current phase
**Library phase complete** (96 NexLink pages). Custom design phase is now active.
**Phase gate:** `D:\CRM\DESIGN-SPEC.md` — 75 custom pages, 13 archetypes (A–M), 8 build phases.
- App pages live in: `D:\CRM\frontend\src\app\`
- Dev server: `npm run serve` from `D:\CRM\frontend`, port 3001
- Screen artefacts (QC records): `D:\CRM\docs\reports\session\SCREEN-ARTEFACTS.md`

## Path translation rule
All internal seed links must be rewritten:
- `href="index.html"` → `href="app/dashboard.html"`
- `href="<folder>/xxx.html"` → `href="app/xxx.html"` (for any subfolder)
- `href="profile.html"` → `href="app/profile.html"` (bare filenames in self-contained pages)

---

## Build checklist — recurring UI bugs (NEVER repeat)

### 0. crm-custom.css — must be linked on EVERY custom app page
`crm-custom.css` contains the DataTables v2 header-centering fix and any table-specific alignment overrides. Without it, all DataTable column headers render misaligned.
**Rule:** Every `app/*.html` page must have this line in `<head>`, after `styles.css`:
```html
<link rel="stylesheet" href="assets/css/crm-custom.css">
```
Check for it before saving any page file. If it is missing, add it.

### 1. Footer — crm-shell.js owns it, pages must NOT have one
`crm-shell.js` line 532 calls `main.insertAdjacentHTML('afterend', FOOTER_HTML)` which injects the complete footer at runtime.
**Rule:** Custom app pages must contain NO `<footer>` block of any kind. If a seed has one, delete it entirely before saving the page file. Hardcoded footers and the shell-injected footer both render → double footer.

### 2. DataTable alignment — THREE places required, not two
Without explicit classes, Bootstrap + DataTables apply inconsistent defaults per column content.
**Rule:** Alignment must be set in ALL THREE places. Use DataTables-native classes ONLY — Bootstrap `text-*` classes are overridden by DataTables CSS.

**Place 1 — HTML thead:**
```html
<th class="dt-head-left/center/right">
```

**Place 2 — JS column definition (data-driven tables only):**
```javascript
{ data: 'field', className: 'dt-body-left/center/right' }
```
This works only when DataTables generates rows from `data:` or `ajax:`. It does NOT apply to pre-existing static HTML `<tbody>` rows.

**Place 3 — crm-custom.css (ALL data-driven tables, not just static):**
DataTables' own CSS and NexLink base styles can override `className` on generated `<td>` elements. Always add explicit per-table CSS rules in `crm-custom.css` with `!important` to guarantee alignment:
```css
/* All columns same alignment: */
#dt_TableName.dataTable tbody > tr > td { text-align: center !important; }
/* Per-column overrides where needed: */
#dt_TableName.dataTable tbody > tr > td:nth-child(N) { text-align: left !important; }
```
**Rule:** Always use `!important` on these overrides. Without it, DataTables CSS wins at runtime regardless of specificity.

**HEADER RULE — ALL `<th>` on ANY table must be center-aligned. No exceptions.**
- DataTables: `dt-head-center` on every `<th>`
- Plain Bootstrap tables: `text-center` on every `<th>`
Never leave a `<th>` without an alignment class on any table type. Never use `dt-head-left` or `dt-head-right`.
Reference: contacts.html (DataTable), finance-analytics.html (plain Bootstrap table).

Body alignment guide (JS `className` + crm-custom.css only):
- `dt-body-left` — long task titles, description text
- `dt-body-center` — names, IDs, emails, badges, dates, status flags, action buttons
- `dt-body-right` — monetary amounts (PKR, USD), numeric totals

### 3. NexLink card fixed height — THREE patterns require `style="height:auto"`

NexLink's `.card` CSS sets `height: calc(100% - var(--bs-gutter-x))`. This causes clipping in three scenarios — all require `style="height:auto"` on the card element.

**Pattern A — Identity strip / standalone card (col-12, single card in row):**
```html
<div class="row mb-3">
  <div class="col-12">
    <div class="card mb-0" style="height:auto">
```

**Pattern B — Multiple stacked cards in the same column:**
When 2+ cards are stacked vertically inside a single `col-*`, each card tries to be `calc(100% - gutter)` of the column height simultaneously. Every card in a stacked column must have `height:auto`.
```html
<div class="col-lg-9">
  <div class="card mb-3" style="height:auto">...</div>  <!-- every card -->
  <div class="card" style="height:auto">...</div>       <!-- every card -->
</div>
```

**Pattern C — Context panel cards (col-lg-4 sidebar):**
Same as Pattern B — all context panel cards on detail pages need `height:auto`.

**Rule:** When in doubt, add `height:auto`. Omitting it on a single-card column is the only case where the default is intentional (equal-height columns side by side).

### 4. Settings pages — two-pane layout rules (never repeat the footer/clip bug)

Root cause (2026-05-29): using `nav flex-column nav-pills` for the settings left nav inside the page body caused NexLink's sidebar CSS (which owns `.nav-pills` globally) to bleed in, constraining the row height. Combined with missing `height:auto` on stacked right-column cards, this clipped all content and pushed the footer to mid-page.

**Rule — Settings left nav:** always use `list-group`, never `nav-pills` inside page body:
```html
<div class="list-group list-group-flush">
  <a class="list-group-item list-group-item-action active d-flex align-items-center gap-2 py-2" href="...">
  <a class="list-group-item list-group-item-action d-flex align-items-center gap-2 py-2" href="...">
</div>
```

**Rule — Settings container:** always add `pb-4` to prevent last card being flush against footer:
```html
<div class="container-fluid pb-4">
```

**Rule — All stacked right-column cards:** `style="height:auto"` on every card (see §3 Pattern B above).

### 5. Filter chips — use NexLink nav-pills-custom, NOT btn-group
`btn-group btn-group-sm` + `btn-outline-secondary` produces Bootstrap's default gray segmented buttons — the "80s tab" look.
**Rule:** All tab-style filter strips must use the NexLink pill pattern:
```html
<ul class="nav nav-pills nav-pills-custom p-1 bg-light rounded-5" id="FILTER_ID" role="tablist">
  <li class="nav-item"><button type="button" class="nav-link rounded-5 active" data-filter="">All</button></li>
  <li class="nav-item"><button type="button" class="nav-link rounded-5" data-filter="X">X</button></li>
</ul>
```
The JS selector `$('#FILTER_ID button')` and `active` class toggling are fully compatible — no JS changes needed.
