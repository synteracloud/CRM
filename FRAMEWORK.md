# CRM UI Framework — Complete Reference

**Working directory:** `D:\CRM\frontend\src\`
**Serve from:** `npm run serve` from `D:\CRM\frontend` — port 3001

---

## 0. Pre-Build Checklist — Execute Before Writing Any File

This is the mandatory starting ritual for every page. Do not write a single line of HTML or JS until every step below is complete. Steps must be executed in order.

```
STEP 1 — Identify seed
  └─ Look up the page in FRAMEWORK.md §17 (Seed-to-Page Mapping)
  └─ Confirm the seed HTML file path (e.g. src/activities.html)

STEP 2 — Find <main> start line in seed HTML
  └─ Grep for: main class="app-wrapper"
  └─ Note the line number — read from there, not from line 1

STEP 3 — Read seed HTML <main> content in full
  └─ Extract all element IDs: chart divs, canvas IDs, table IDs, modal IDs
  └─ List them — you will look each one up in Step 5

STEP 4 — Read seed HTML script block
  └─ Script block is at the bottom of <body>, before </body>
  └─ Record every assets/libs/... script → these are the lib includes
  └─ Record the seed page JS file (e.g. assets/js/dashboard/activities.js)

STEP 5 — Cross-check §24 for every element ID from Step 3
  └─ If element is catalogued in §24 → copy config verbatim from §24
  └─ If element is NOT in §24 → go to Step 6

STEP 6 — Read seed JS file(s) from Step 4 (only if new IDs found in Step 5)
  └─ Read the entire file — do not skim
  └─ For each element ID from Step 3: find its config or confirm it has none
  └─ "Has no config" = plain HTML element, no JS init needed
  └─ Add every new config to FRAMEWORK.md §24 BEFORE writing the driver

STEP 7 — Set CRM_PAGE key
  └─ Look up the correct key in FRAMEWORK.md §18

STEP 8 — Confirm NO hardcoded footer exists in the page
  └─ crm-shell.js injects the footer at runtime via insertAdjacentHTML('afterend', FOOTER_HTML)
  └─ Do NOT add <footer> to any page file — the shell owns it
  └─ If a seed has a footer block, delete it before saving

STEP 9 — NOW write the files
  └─ app/[page].html — verbatim <main> from seed (no footer) + correct script block
  └─ crm-[page].js  — all configs verbatim from §24 or seed JS
  └─ crm-shell.js   — add sidebar link if page is new to the sidebar

STEP 10 — Update tracking files after build
  └─ FRAMEWORK.md §24  — confirm all new element IDs are catalogued
  └─ PROGRESS.md        — add page to built list
```

**Rule:** If you skip any step and something is wrong on the page, the cause will always trace back to a skipped step. These steps exist because every known build error so far was caused by a skipped step.

---

## 1. What the Framework Is

The framework is a set of JavaScript files in `src/assets/js/app/` that wrap the NexLink template so every page shares the same header, sidebar, dummy data, and API layer. The framework eliminates the ~400 lines of sidebar/header HTML that the seed hardcodes on every page. Instead, each page contains only its own `<main>` content and a script block — everything else is injected at runtime.

**Framework files (never modify without strong reason):**

| File | Purpose | State |
|------|---------|-------|
| `crm-shell.js` | Injects header + sidebar + Add Customer modal into `.page-layout` | Final |
| `crm-api.js` | API wrapper. `DUMMY_MODE: true` flips to real backend. | Final |
| `crm-dummy.js` | Single source of all fake data — Pakistan names, PKR values, realistic CRM records | Final |
| `crm-components.js` | Shared renderers: badges, formatters, empty state, error toast | Final |
| `crm-locale.js` | RTL / Urdu toggle. Reads `dir` attribute. | Final |
| `crm-auth.js` | Login page logic only | Final |

**Page-specific drivers** (one per page, lives alongside the page HTML):

| File | Page |
|------|------|
| `crm-dashboard.js` | `app/dashboard.html` — seed-identical chart configs |

---

## 2. Page HTML Template

Every page in `src/app/` follows this exact skeleton. Copy it verbatim. Do not deviate.

**CRITICAL — `<base href="../">` is mandatory.** It must be the first element inside `<head>`, before all other tags. Without it: every `assets/...` path resolves from `app/` instead of `src/`, the logo image breaks, all CSS and JS fails to load, and fonts fall back to system default. Omitting it caused logo + font failure on sales.html (GAP-025). Never use `../assets/...` paths — always bare `assets/...` with base href in place.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <base href="../">
  <meta charset="utf-8">
  <meta name="theme-color" content="#5955D1">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PAGE TITLE — NexLink CRM</title>
  <link rel="icon" type="image/png" href="assets/images/favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..700;1,400..700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/libs/flaticon/css/all/all.css">
  <link rel="stylesheet" href="assets/libs/lucide/lucide.css">
  <link rel="stylesheet" href="assets/libs/fontawesome/css/all.min.css">
  <link rel="stylesheet" href="assets/libs/simplebar/simplebar.css">
  <link rel="stylesheet" href="assets/libs/node-waves/waves.css">
  <link rel="stylesheet" href="assets/libs/bootstrap-select/css/bootstrap-select.min.css">
  <link rel="stylesheet" href="assets/libs/datatables/datatables.min.css">
  <link rel="stylesheet" href="assets/libs/flatpickr/flatpickr.min.css">
  <link id="main-stylesheet" rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
  <div class="page-layout">
    <!-- header + sidebar injected by crm-shell.js -->
    <main class="app-wrapper">
      <div class="container-fluid">

        <div class="app-page-head d-flex align-items-center justify-content-between">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb mb-0">
              <li class="breadcrumb-item">
                <a href="app/dashboard.html"><i class="fi fi-rr-home"></i> Home</a>
              </li>
              <li class="breadcrumb-item active" aria-current="page">PAGE NAME</li>
            </ol>
          </nav>
        </div>

        <!-- ═══════════════════════════════════════════════════════ -->
        <!-- PAGE CONTENT — verbatim copy from seed, then customise -->
        <!-- ═══════════════════════════════════════════════════════ -->

      </div>
    </main>

    <!-- footer injected by crm-shell.js — do NOT add one here -->
  </div>

  <!-- ── Script block — FRAMEWORK.md §3 load order ──────────────────── -->
  <script src="assets/libs/global/global.min.js"></script>
  <script src="assets/js/app/crm-dummy.js"></script>
  <script src="assets/js/app/crm-api.js"></script>
  <script>window.CRM_PAGE = 'PAGE_KEY';</script>
  <script src="assets/js/app/crm-shell.js"></script>
  <script src="assets/js/app/crm-components.js"></script>
  <script src="assets/js/appSettings.js"></script>
  <script src="assets/js/main.js"></script>
  <!-- add only the libs the page actually uses: -->
  <script src="assets/libs/sortable/Sortable.min.js"></script>      <!-- if draggable lists -->
  <script src="assets/libs/chartjs/chart.js"></script>              <!-- if Chart.js canvas -->
  <script src="assets/libs/apexcharts/apexcharts.min.js"></script>  <!-- if ApexCharts -->
  <script src="assets/libs/datatables/datatables.min.js"></script>  <!-- if DataTable -->
  <script src="assets/libs/flatpickr/flatpickr.min.js"></script>    <!-- if date pickers -->
  <script src="assets/js/app/crm-PAGE.js"></script>
</body>
</html>
```

### Rules
- `<base href="../">` is mandatory on every page in `app/` — without it, all `assets/` paths resolve from `app/` and break.
- `window.CRM_PAGE` must be set **before** `crm-shell.js` loads. The shell reads it synchronously to set the active sidebar item.
- Load order is fixed: global → dummy → api → CRM_PAGE → shell → components → appSettings → main → libs → page driver.
- Only include lib scripts the page actually uses. Unused lib loads waste time and can cause errors if the lib expects a DOM element.
- `crm-locale.js` is not needed when page content is static (all text hardcoded in HTML). Include it only when the page renders dynamic text that needs locale switching.

---

## 3. Script Load Order

```
1. global.min.js          — jQuery, Bootstrap, SimpleBar, Waves (all globals)
2. crm-dummy.js           — window.CRM_DUMMY
3. crm-api.js             — window.CRM_API, window.CRM_CONFIG
4. window.CRM_PAGE = '…'  — inline, sets page identity
5. crm-shell.js           — injects header + sidebar + modal (reads CRM_PAGE)
6. crm-components.js      — window.CRM.components
7. appSettings.js         — theme/settings
8. main.js                — Bootstrap init, SimpleBar init, Waves
9. Sortable.min.js        — (if needed)
10. chart.js              — Chart.js (if needed)
11. apexcharts.min.js     — ApexCharts (if needed)
12. datatables.min.js     — DataTables (if needed)
13. flatpickr.min.js      — Flatpickr (if needed)
14. crm-[page].js         — page driver (last, always)
```

**Why this order matters:**
- Shell (step 5) must run after dummy/api so the header can read `CRM_DUMMY.users` for the avatar/name.
- Chart libs (steps 9–13) must be available before the page driver (step 14) calls `new ApexCharts(...)` or `new Chart(...)`.
- The page driver runs last so all globals, libs, and DOM are guaranteed ready.

---

## 4. How crm-shell.js Works

`crm-shell.js` is an IIFE that runs synchronously when its `<script>` tag is parsed. It:

1. Reads `window.CRM_PAGE` to know which sidebar item gets `.active`
2. Builds the full sidebar HTML string (exact replica of seed `src/index.html` sidebar)
3. Builds the full header HTML string (search bar, theme toggle, notifications dropdown, avatar)
4. Builds the Add Customer modal HTML
5. Calls `layout.querySelector('main.app-wrapper').insertAdjacentHTML('beforebegin', HEADER + SIDEBAR + MODAL)`

**DOM requirement:** The page must have:
```html
<div class="page-layout">
  <main class="app-wrapper">...</main>
</div>
```

The shell inserts before `<main>`. If `.page-layout` or `main.app-wrapper` is missing, nothing is injected and the page will have no header or sidebar — silently.

**After injection** (inside a `DOMContentLoaded` listener): the shell updates `#header-today-leads` badge from `CRM_DUMMY.todayLeads.length`.

**crm-dummy.js dependency (soft — verified in crm-shell.js):**
`crm-dummy.js` must load before `crm-shell.js` (it is already at position 2 in the load order vs position 5). If absent:
- Header avatar/name falls back to hardcoded `{ display_name: 'Ahmed Raza', email: 'ahmed@crm.pk' }` — shell line 310 has an explicit `||` fallback, so the header still renders.
- `#header-today-leads` badge will not update — shell line 522 is guarded by `if (window.CRM_DUMMY)`, so it silently stays at its HTML default value.
This is a **soft dependency with partial degradation**, not a silent total failure. Never remove `crm-dummy.js` from the load order.

### CRM_PAGE values → active sidebar tab

| CRM_PAGE value | Active tab |
|---------------|-----------|
| `'dashboard'` | Dashboard tab |
| `'leads'` | Dashboard tab (leads is a sub-page) |
| `'customers'` | Dashboard tab |
| `'followups'` | Dashboard tab |
| `'calendar'` | Apps tab |
| `'inbox'` | Apps tab |
| *(not set)* | No active tab |

---

## 5. How crm-api.js Works

```js
window.CRM_CONFIG = {
  DUMMY_MODE: true,           // flip to false when backend is live
  BASE_URL: 'http://localhost:3000/api/v1',
  get token() { return localStorage.getItem('crm_token'); }
};
```

When `DUMMY_MODE: true`, every API call returns a resolved Promise with data from `window.CRM_DUMMY`. When `false`, it makes real fetch() calls to `BASE_URL` with `Authorization: Bearer <token>`.

**Available endpoints:**
```js
CRM_API.auth.login(email, password)
CRM_API.leads.list(params)
CRM_API.leads.get(id)
CRM_API.leads.patch(id, body)
CRM_API.leads.nextAction(id)
CRM_API.followups.list(params)
CRM_API.followups.complete(id)
CRM_API.opportunities.list(params)
CRM_API.opportunities.patch(id, body)
CRM_API.contacts.list(params)
CRM_API.contacts.get(id)
CRM_API.contacts.create(payload)
CRM_API.activities.list(params)
CRM_API.tasks.list(params)
CRM_API.tasks.create(body)
CRM_API.invoiceSummaries.get(params)
CRM_API.forecasts.get(params)
CRM_API.users.list()
```

**Response envelope** (all endpoints, dummy and real):
```js
{ data: [...], meta: { count, total, limit, offset } }
```
Single-record endpoints: `{ data: { ...record }, meta: {} }`

---

## 6. How crm-dummy.js Works

All dummy data is in `window.CRM_DUMMY`. Fields:

| Field | Type | Description |
|-------|------|-------------|
| `users` | `{ data: [...], meta: {...} }` | 5 Pakistan reps/managers |
| `userMap` | `{ user_id: user }` | Fast lookup by ID |
| `leads` | `{ data: [...], meta: {...} }` | 20 leads, all stages, PKR values |
| `followups` | `{ data: [...], meta: {...} }` | 12 followups (overdue/pending/completed) |
| `contacts` | `{ data: [...], meta: {...} }` | Contact records |
| `opportunities` | `{ data: [...], meta: {...} }` | Pipeline opportunities |
| `activities` | `{ data: [...], meta: {...} }` | Activity log entries |
| `tasks` | `{ data: [...], meta: {...} }` | Task records |
| `todayLeads` | `[...]` | Leads created today (for header badge) |
| `invoiceSummaries` | `{...}` | Invoice KPI summary |
| `forecasts` | `{...}` | Forecast data |

**Do not use `CRM_DUMMY` for static content pages.** If the page content is hardcoded from the seed (e.g., dashboard.html), the page driver must not call `CRM_DUMMY` — it would make the output non-deterministic.

---

## 7. How crm-components.js Works

All renderers are on `window.CRM.components`:

| Function | Returns |
|----------|---------|
| `stageBadge(stage)` | Bootstrap badge for lead stage |
| `priorityBadge(priority)` | Bootstrap badge for urgent/high/medium/low |
| `followupBadge(state, escalation)` | Badge for overdue/pending/completed |
| `escalationBadge(level)` | Badge for strict/medium/soft |
| `paymentBadge(status)` | Badge for payment lifecycle states |
| `pkr(amount)` | Formats number as PKR Cr/L/raw |
| `relativeTime(isoDate)` | "2h ago", "3d ago", etc. |
| `dueCell(isoDate)` | Red span if past due |
| `enforcementStrip(overdueCount, unassignedCount)` | Alert bar shown at top of queue pages |
| `activityRow(act)` | `<li>` for activity timeline |
| `emptyState(message)` | Centered empty state div |
| `showError(msg)` | Shows `#crm-error-toast` (injected by shell) |

---

## 8. Seed-First Normalisation Protocol

**Rule:** Every page's `<main>` content must be a verbatim copy of its corresponding seed page before any CRM customisation.

**Seed directory:** `src/` (the root HTML files — `index.html`, `leads.html`, `customers.html`, etc.)
**CRM pages directory:** `src/app/`

**Steps to build a new page:**

1. Identify the seed file (e.g., `src/leads.html` → `src/app/leads.html`)
2. Copy the seed's `<main class="app-wrapper">...</main>` content verbatim into the page template
3. Adjust the breadcrumb `href` from `href="leads.html"` to `href="app/leads.html"` (one level deeper due to `<base href="../">`)
4. Set `window.CRM_PAGE` to the correct page key
5. Write a `crm-[page].js` that initialises only what is on the page — charts, DataTables, interactivity

**What "verbatim" means:**
- Same element IDs (do not rename chart IDs, table IDs, or modal IDs)
- Same static values (hardcoded numbers, labels, category names, trailing spaces)
- Same CSS class chains on every element
- Same SVG icons (copy the exact `<path>` data — do not substitute)
- Same chart types (if seed uses `heatmap`, use `heatmap` — never substitute `bar`)
- Same HTML attributes on every element — including `aria-expanded`, `aria-label`, `data-*` attributes, `type`, `role`. Do not drop attributes when compressing or reformatting rows.
- Same character encoding — if the seed uses a literal `&`, copy `&`. Do not encode or decode entities.
- Same whitespace in text nodes — if the seed has a trailing space inside a `<td>`, preserve it.

**Never compress multi-line seed HTML into single-line rows.** Compressing multi-line HTML to single-line drops attributes and whitespace. Copy each row exactly as written in the seed — same indentation, same line breaks, same attributes. If the seed has 12 lines per row, your copy has 12 lines per row.

**What to do after the verbatim copy:**
- Pakistan-specific customisation (PKR currency, Urdu labels, local data) goes in the page driver JS, not in the HTML
- The HTML stays seed-identical so visual regression is trivial to check

---

## 9. Page Driver Pattern (crm-[page].js)

The page driver is the only file where page-specific logic lives. It is always the last script to load.

**For seed-replica pages (static content):** The driver only initialises charts and interactivity — it does NOT call `CRM_API` or `CRM_DUMMY` for display data because the HTML already has the static values hardcoded.

```js
// Pattern: guard every element before initialising
const el = document.querySelector('#myChart');
if (el) {
  new ApexCharts(el, config).render();
}

// DataTable pattern
if ($('#dt_TableName').length) {
  const dt = $('#dt_TableName').DataTable({
    searching: true,
    pageLength: 6,
    lengthChange: false,
    info: true,
    paging: true,
    language: {
      search: "",
      searchPlaceholder: 'Search',
      paginate: {
        previous: "<i class='fi fi-rr-angle-left'></i>",
        next:     "<i class='fi fi-rr-angle-right'></i>",
        first:    "<i class='fi fi-rr-angle-double-left'></i>",
        last:     "<i class='fi fi-rr-angle-double-right'></i>"
      }
    },
    initComplete: function () {
      var dtSearch = $('#dt_TableName_wrapper .dt-search').detach();
      $('#dt_TableName_Search').append(dtSearch);
      $('#dt_TableName_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
      $('#dt_TableName_Search .dt-search label').remove();
      $('#dt_TableName_wrapper > .row.mt-2.justify-content-between').first().remove();
    }
  });
}

// Chart.js canvas pattern (must use DOMContentLoaded — runs after all scripts)
function initCanvasChart() {
  const canvas = document.getElementById('myCanvasChart');
  if (!canvas) return;
  new Chart(canvas.getContext('2d'), { type: 'doughnut', data: {...}, options: {...} });
}
document.addEventListener('DOMContentLoaded', initCanvasChart);
```

**Why `DOMContentLoaded` only for Chart.js canvas:** ApexCharts renders into a `<div>` using its own async mechanism and works fine when called at script-parse time (bottom of body). Chart.js renders synchronously onto a `<canvas>` element and needs the element to be fully ready — using `DOMContentLoaded` defers it safely past all script execution.

---

## 10. DataTable Search Box Relocation

Every DataTable on every page uses this pattern to move the search box out of the DataTable wrapper and into a custom `<div id="dt_TableName_Search">` that is placed in the card header.

```html
<!-- In the card header HTML (from seed, verbatim): -->
<div id="dt_NewCustomers_Search" class="d-flex align-items-center gap-2"></div>

<!-- DataTable init (in page driver): -->
initComplete: function () {
  var dtSearch = $('#dt_NewCustomers_wrapper .dt-search').detach();
  $('#dt_NewCustomers_Search').append(dtSearch);
  $('#dt_NewCustomers_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
  $('#dt_NewCustomers_Search .dt-search label').remove();
  $('#dt_NewCustomers_wrapper > .row.mt-2.justify-content-between').first().remove();
}
```

The `_Search` div ID is always `dt_[TableID]_Search`. The wrapper row removal cleans up the default DataTable layout row.

---

## 11. Todo List / Sortable Pattern

Pages with a sortable todo/task list must:
1. Include `Sortable.min.js` in the script block (before the page driver)
2. Use `id="todoList"` on the `<ul>` (seed's exact ID)
3. Use `id="todoAdd"`, `id="todoInput"`, `id="todoPriority"` on the add-task controls
4. Include sortable-handle SVG on every `<li>` item (copy from seed verbatim)
5. Add the todolist interactivity block in the page driver (see `crm-dashboard.js` bottom section)

The interactivity block is a `$(document).ready()` wrapper containing:
- `#todoAdd` click: prepends new `<li>` with timestamp
- `.form-check-input` change: toggles `del` + colour class based on `check-{priority}` class
- `new Sortable(document.getElementById('todoList'), { handle: '.sortable-handle', animation: 150 })`
- `.item-delete` click: removes parent `<li>`

---

## 12. Auth Pages

Auth pages follow a different pattern from app/ pages — no `<div class="page-layout">` wrapper, no `crm-shell.js`, no `window.CRM_PAGE`. However, **not all auth pages use crm-auth.js**. Script blocks differ per page — always read the seed's script block exactly, never assume pattern carries across all four.

**login-frame.html and register-frame.html** — use `crm-auth.js` (async submit intercept, token storage, redirect):
```html
<script src="assets/libs/global/global.min.js"></script>
<script src="assets/js/app/crm-dummy.js"></script>
<script src="assets/js/app/crm-api.js"></script>
<script src="assets/js/appSettings.js"></script>
<script src="assets/js/main.js"></script>
<script src="assets/js/app/crm-auth.js"></script>
```

**forgot-password-frame.html and new-password-frame.html** — NO `crm-auth.js`. Plain HTML form `action` navigation only. Seed has no JS intercept:
```html
<script src="assets/libs/global/global.min.js"></script>
<script src="assets/js/app/crm-dummy.js"></script>
<script src="assets/js/app/crm-api.js"></script>
<script src="assets/js/appSettings.js"></script>
<script src="assets/js/main.js"></script>
```

**CRITICAL — seed script block audit rule:** Never assume a pattern (e.g. "auth pages use crm-auth.js") applies to multiple pages. For every page, read the seed's `<script>` list verbatim and replicate it exactly. Similarly read the seed's `<form action>` attributes — do not add JS intercepts that are not present in the seed. Overgeneralizing a pattern is the root cause of the crm-auth.js-on-forgot/reset bug (2026-05-13).

**CRITICAL — JS redirects must use absolute paths.** Auth pages have `<base href="../">` which sets `document.baseURI` to `http://localhost:3001/`. Browsers resolve relative URLs assigned to `window.location.href` against `document.baseURI`, NOT `document.URL`. So `window.location.href = 'dashboard.html'` navigates to `http://localhost:3001/dashboard.html` (404), not `/app/dashboard.html`. Always use root-relative absolute paths in crm-auth.js:
```js
window.location.href = '/app/dashboard.html';   // ✓ absolute — always correct
window.location.href = 'dashboard.html';         // ✗ relative — resolves via baseURI to root
```
HTML `href=` and `action=` attributes are unaffected — they use `<base href>` as intended and `app/dashboard.html` resolves correctly to `/app/dashboard.html`.

---

## 13. Globals Available at Runtime

After `global.min.js` loads, these are available everywhere:

| Global | Source |
|--------|--------|
| `$` / `jQuery` | jQuery (bundled in global.min.js) |
| `bootstrap` | Bootstrap 5 |
| `ApexCharts` | ApexCharts |
| `Chart` | Chart.js |
| `SimpleBar` | SimpleBar |
| `Waves` | Node Waves |
| `flatpickr` | Flatpickr (after flatpickr.min.js) |
| `Sortable` | SortableJS (after Sortable.min.js) |
| `window.CRM_DUMMY` | After crm-dummy.js |
| `window.CRM_API` | After crm-api.js |
| `window.CRM_CONFIG` | After crm-api.js |
| `window.CRM.components` | After crm-components.js |
| `window.CRM_PAGE` | Set inline before crm-shell.js |

---

## 14. CSS / Theming

- **Theme color:** `#5955D1` (indigo/primary)
- **CSS variables used in chart configs:** `var(--bs-primary)`, `var(--bs-info)`, `var(--bs-body-color)`, `var(--bs-body-bg)`, `var(--bs-border-color)`, `var(--bs-body-font-family)`, `var(--bs-white)`, `var(--bs-heading-color)`
- **Never hardcode hex values in chart configs** — use the CSS variables so dark mode works
- **Main stylesheet:** `assets/css/styles.css` (loaded via `<link id="main-stylesheet">`)
- **Dark mode:** toggled by the theme button in the header (handled by `appSettings.js`)
- **RTL:** toggled by the اردو button in the header (handled by `crm-locale.js`)

---

## 15. File Locations Quick Reference

```
src/
├── index.html                          ← SEED: default dashboard
├── leads.html                          ← SEED: leads list
├── customers.html                      ← SEED: customers
├── [other seed pages].html
├── app/                                ← CRM PAGES (built here)
│   ├── dashboard.html                  ← BUILT (seed-identical + framework)
│   └── [future pages go here]
├── assets/
│   ├── css/styles.css                  ← main stylesheet
│   ├── js/
│   │   ├── app/
│   │   │   ├── crm-shell.js            ← framework core
│   │   │   ├── crm-api.js              ← framework core
│   │   │   ├── crm-dummy.js            ← framework core
│   │   │   ├── crm-components.js       ← framework core
│   │   │   ├── crm-locale.js           ← framework core
│   │   │   ├── crm-auth.js             ← auth pages only
│   │   │   └── crm-dashboard.js        ← dashboard page driver
│   │   ├── appSettings.js
│   │   ├── main.js
│   │   └── dashboard/dashboard.js      ← SEED JS (read-only reference)
│   └── libs/
│       ├── global/global.min.js        ← jQuery + Bootstrap + all globals
│       ├── apexcharts/apexcharts.min.js
│       ├── chartjs/chart.js
│       ├── datatables/datatables.min.js
│       ├── flatpickr/flatpickr.min.js
│       └── sortable/Sortable.min.js
```

---

## 16. Build Checklist (per page)

Before marking any page complete:

- [ ] Seed file identified and read in full
- [ ] `<main>` content copied verbatim from seed (same IDs, same static values, same SVGs)
- [ ] `<base href="../">` present in `<head>`
- [ ] `window.CRM_PAGE` set to correct key before `crm-shell.js`
- [ ] Script load order matches FRAMEWORK.md §3
- [ ] Only required lib scripts included
- [ ] **No `<footer>` block in page HTML** — crm-shell.js injects the footer at runtime. If seed has one, delete it.
- [ ] Page driver written — every chart/table/interactive element initialised
- [ ] Element guards on all chart/table inits (`if (el)` / `if ($('#id').length)`)
- [ ] DataTable search relocation pattern applied where DataTable exists
- [ ] **Every DataTable column has alignment in THREE places** — (1) `class="dt-head-left/center/right"` on every `<th>`; (2) `className: 'dt-body-left/center/right'` on every JS column definition; (3) explicit CSS rules in `crm-custom.css` with `!important` for every data-driven table (e.g. `#dt_Name.dataTable tbody > tr > td { text-align: center !important; }`). DataTables' own stylesheet overrides `className` at runtime regardless of specificity — without the `!important` rule in place 3, body cells misalign.
- [ ] **`style="height:auto"` on cards — THREE patterns (all required):**
  NexLink `.card` sets `height: calc(100% - var(--bs-gutter-x))`. Add `style="height:auto"` in all three cases:
  - **Pattern A** — Sole card in a `col-12` standalone row (identity strip, summary banner)
  - **Pattern B** — Any card in a column containing 2+ stacked cards (each would otherwise fill 100% of column height, clipping content and displacing footer)
  - **Pattern C** — Context panel sidebar cards (col-lg-4 on detail pages)
  When in doubt, add `height:auto` — the only safe omission is a single card filling an entire column beside another equal-height card.
- [ ] **Settings / two-pane pages — three mandatory rules (nav-pills collision fix, 2026-05-29):**
  Using `.nav-pills` in the page body conflicts with crm-shell.js sidebar which owns `.nav-pills` globally. This constrained row height, clipped right-column content, and pushed the footer to mid-page on all 5 affected G-series pages.
  - Left nav: `list-group list-group-flush` + `list-group-item list-group-item-action` — never `nav flex-column nav-pills`
  - Container: `<div class="container-fluid pb-4">`
  - All right-column cards: `style="height:auto"` (Pattern B above)
- [ ] **Filter chip strips use `nav-pills-custom` pattern** — NOT `btn-group btn-group-sm`. See §31 below.
- [ ] Breadcrumb `href` corrected for `app/` subdirectory depth
- [ ] Page opens in browser with no console errors
- [ ] All charts render with correct chart type matching seed
- [ ] DataTable paginates, search works
- [ ] Interactive elements (tabs, todo list, modals) function correctly

---

## 31. Filter Chip Pattern (nav-pills-custom)

All tab-style filter strips must use the NexLink pill pattern. `btn-group btn-group-sm` + `btn-outline-secondary` produces Bootstrap's generic gray segmented buttons and must not be used for filters.

**Correct pattern:**
```html
<ul class="nav nav-pills nav-pills-custom p-1 bg-light rounded-5" id="FILTER_ID" role="tablist">
  <li class="nav-item"><button type="button" class="nav-link rounded-5 active" data-filter="">All</button></li>
  <li class="nav-item"><button type="button" class="nav-link rounded-5" data-filter="X">X</button></li>
</ul>
```

The JS selector `$('#FILTER_ID button')` and `active` class toggling work identically — no JS changes needed when using this pattern. Standalone toggle buttons (e.g. "Overdue Only", "Has Open Case") are not filter strips and may remain as `btn btn-sm btn-outline-danger/warning`.

---

## 17. Seed-to-Page Mapping Table

Every `app/` page must be seeded from one of these source files. This is the authoritative mapping. Never invent a page layout — always start from the corresponding seed.

| app/ page (to build) | Seed source file | Seed JS driver reference |
|----------------------|-----------------|--------------------------|
| `app/dashboard.html` | `src/index.html` | `src/assets/js/dashboard/dashboard.js` |
| `app/leads.html` | `src/leads.html` | `src/assets/js/app/crm-leads.js` (existing, needs normalisation) |
| `app/customers.html` | `src/customers.html` | `src/assets/js/app/crm-customers.js` |
| `app/deals.html` | `src/deals.html` | `src/assets/js/crm-app/crm.js` |
| `app/activities.html` | `src/activities.html` | seed JS |
| `app/calendar.html` | `src/calendar.html` | seed JS |
| `app/chat.html` | `src/chat.html` | seed JS |
| `app/inbox-email.html` | `src/email/inbox.html` | seed JS |
| `app/email-compose.html` | `src/email/compose.html` | `crm-email-compose.js` |
| `app/email-read.html` | `src/email/read-email.html` | `crm-email-read.js` |
| `app/settings.html` | `src/settings.html` | seed JS |
| `app/profile.html` | `src/profile.html` | seed JS |
| `app/finance.html` | `src/finance.html` | seed JS |
| `app/sales.html` | `src/sales.html` | seed JS |
| `app/team-management.html` | `src/team-management.html` | seed JS |
| `app/employee.html` | `src/employee.html` | `crm-employee.js` |
| `app/user-management.html` | `src/user-management.html` | `crm-user-management.js` |
| `app/task-management.html` | `src/task-management.html` | seed JS |
| `app/review.html` | `src/review.html` | seed JS |
| `app/marketing.html` | `src/marketing.html` | seed JS |
| `app/login-frame.html` | `src/authentication/login-frame.html` | `crm-auth.js` |
| `app/register-frame.html` | `src/authentication/register-frame.html` | `crm-auth.js` |
| `app/forgot-password-frame.html` | `src/authentication/forgot-password-frame.html` | `crm-forgot-password-frame.js` (native form, no JS intercept) |
| `app/new-password-frame.html` | `src/authentication/new-password-frame.html` | `crm-new-password-frame.js` (native form, no JS intercept) |
| `app/error-404.html` | `src/pages/error-404.html` | `crm-error-404.js` |
| `app/pricing.html` | `src/pages/pricing.html` | `crm-pricing.js` |
| `app/under-construction.html` | `src/pages/under-construction.html` | `crm-under-construction.js` |
| `app/blog.html` | `src/pages/blog.html` | `crm-blog.js` |
| `app/blog-list.html` | `src/pages/blog-list.html` | `crm-blog-list.js` |
| `app/blog-details.html` | `src/pages/blog-details.html` | `crm-blog-details.js` |
| `app/error-404-cover.html` | `src/pages/error-404-cover.html` | `crm-error-404-cover.js` |
| `app/error-404-full.html` | `src/pages/error-404-full.html` | `crm-error-404-full.js` |
| `app/under-construction-cover.html` | `src/pages/under-construction-cover.html` | `crm-under-construction-cover.js` |
| `app/under-construction-full.html` | `src/pages/under-construction-full.html` | `crm-under-construction-full.js` |
| `app/login-basic.html` | `src/authentication/login-basic.html` | `crm-login-basic.js` |
| `app/login-cover.html` | `src/authentication/login-cover.html` | `crm-login-cover.js` |
| `app/register-basic.html` | `src/authentication/register-basic.html` | `crm-register-basic.js` |
| `app/register-cover.html` | `src/authentication/register-cover.html` | `crm-register-cover.js` |
| `app/forgot-password-basic.html` | `src/authentication/forgot-password-basic.html` | `crm-forgot-password-basic.js` (native form, no JS intercept) |
| `app/forgot-password-cover.html` | `src/authentication/forgot-password-cover.html` | `crm-forgot-password-cover.js` (native form, no JS intercept) |
| `app/new-password-basic.html` | `src/authentication/new-password-basic.html` | `crm-new-password-basic.js` (native form, no JS intercept) |
| `app/new-password-cover.html` | `src/authentication/new-password-cover.html` | `crm-new-password-cover.js` (native form, no JS intercept) |
| `app/dashboard-rtl.html` | `src/index-rtl.html` | `crm-dashboard-rtl.js` |
| `app/investment.html` | `src/ai/investment.html` | `crm-investment.js` |
| `app/new-chat.html` | `src/ai/new-chat.html` | `crm-new-chat.js` |
| `app/new-project.html` | `src/ai/new-project.html` | `crm-new-project.js` |
| `app/plans.html` | `src/ai/plans.html` | `crm-plans.js` |
| `app/search-chat.html` | `src/ai/search-chat.html` | `crm-search-chat.js` |
| `app/search-image.html` | `src/ai/search-image.html` | `crm-search-image.js` |
| `app/your-chat.html` | `src/ai/your-chat.html` | `crm-your-chat.js` |
| `app/search-apps.html` | `src/ai/search-apps.html` | `crm-search-apps.js` |
| `app/search-apps-details.html` | `src/ai/search-apps-details.html` | `crm-search-apps-details.js` |
| `app/apexchart.html` | `src/chart/apexchart.html` | `crm-apexchart.js` |
| `app/chartjs.html` | `src/chart/chartjs.html` | `crm-chartjs.js` |
| `app/accordion.html` | `src/components/accordion.html` | `crm-accordion.js` |
| `app/alerts.html` | `src/components/alerts.html` | `crm-alerts.js` |
| `app/badge.html` | `src/components/badge.html` | `crm-badge.js` |
| `app/breadcrumb.html` | `src/components/breadcrumb.html` | `crm-breadcrumb.js` |
| `app/button-group.html` | `src/components/button-group.html` | `crm-button-group.js` |
| `app/buttons.html` | `src/components/buttons.html` | `crm-buttons.js` |
| `app/card.html` | `src/components/card.html` | `crm-card.js` |
| `app/carousel.html` | `src/components/carousel.html` | `crm-carousel.js` |
| `app/collapse.html` | `src/components/collapse.html` | `crm-collapse.js` |
| `app/dropdowns.html` | `src/components/dropdowns.html` | `crm-dropdowns.js` |
| `app/list-group.html` | `src/components/list-group.html` | `crm-list-group.js` |
| `app/modal.html` | `src/components/modal.html` | `crm-modal.js` |
| `app/navbar.html` | `src/components/navbar.html` | `crm-navbar.js` |
| `app/offcanvas.html` | `src/components/offcanvas.html` | `crm-offcanvas.js` |
| `app/pagination.html` | `src/components/pagination.html` | `crm-pagination.js` |
| `app/popovers.html` | `src/components/popovers.html` | `crm-popovers.js` |
| `app/progress.html` | `src/components/progress.html` | `crm-progress.js` |
| `app/scrollspy.html` | `src/components/scrollspy.html` | `crm-scrollspy.js` |
| `app/spinners.html` | `src/components/spinners.html` | `crm-spinners.js` |
| `app/tabs.html` | `src/components/tabs.html` | `crm-tabs.js` |
| `app/toasts.html` | `src/components/toasts.html` | `crm-toasts.js` |
| `app/tooltips.html` | `src/components/tooltips.html` | `crm-tooltips.js` |
| `app/typography.html` | `src/components/typography.html` | `crm-typography.js` |
| `app/avatar.html` | `src/extended-ui/avatar.html` | `crm-avatar.js` |
| `app/card-action.html` | `src/extended-ui/card-action.html` | `crm-card-action.js` |
| `app/drag-and-drop.html` | `src/extended-ui/drag-and-drop.html` | `crm-drag-and-drop.js` |
| `app/simplebar.html` | `src/extended-ui/simplebar.html` | `crm-simplebar.js` |
| `app/swiper.html` | `src/extended-ui/swiper.html` | `crm-swiper.js` |
| `app/flatpickr.html` | `src/forms/flatpickr.html` | `crm-flatpickr.js` |
| `app/form-elements.html` | `src/forms/form-elements.html` | `crm-form-elements.js` |
| `app/form-floating.html` | `src/forms/form-floating.html` | `crm-form-floating.js` |
| `app/form-input-group.html` | `src/forms/form-input-group.html` | `crm-form-input-group.js` |
| `app/form-layout.html` | `src/forms/form-layout.html` | `crm-form-layout.js` |
| `app/form-validation.html` | `src/forms/form-validation.html` | `crm-form-validation.js` |
| `app/tagify.html` | `src/forms/tagify.html` | `crm-tagify.js` |
| `app/flaticon.html` | `src/icons/flaticon.html` | `crm-flaticon.js` |
| `app/fontawesome.html` | `src/icons/fontawesome.html` | `crm-fontawesome.js` |
| `app/lucide.html` | `src/icons/lucide.html` | `crm-lucide.js` |
| `app/jsvectormap.html` | `src/maps/jsvectormap.html` | `crm-jsvectormap.js` |
| `app/leaflet.html` | `src/maps/leaflet.html` | `crm-leaflet.js` |
| `app/tables-basic.html` | `src/table/tables-basic.html` | `crm-tables-basic.js` |
| `app/tables-datatable.html` | `src/table/tables-datatable.html` | `crm-tables-datatable.js` |

**Filename rule:** The `app/` page filename must match the seed filename exactly. The CRM_PAGE key must match the filename stem. No semantic renaming — if the seed is `customers.html`, the app page is `app/customers.html` and CRM_PAGE is `'customers'`. Deviations cause URL/label mismatches and sidebar inconsistencies.

**When no exact seed match exists:** find the closest structural match from the seed directory (e.g., a detail page with no seed equivalent uses the closest list page as a layout reference). Document the substitution in a comment at the top of the page file.

---

## 18. CRM_PAGE Key Registry

`window.CRM_PAGE` must be set to one of these exact string values. The shell uses `a(pages)` which checks `pages.includes(PAGE)` — wrong values cause no active state silently.

| CRM_PAGE value | Page |
|----------------|------|
| `'dashboard'` | `app/dashboard.html` |
| `'leads'` | `app/leads.html` |
| `'customers'` | `app/customers.html` |
| `'followups'` | `app/followups.html` |
| `'deals'` | `app/deals.html` |
| `'activities'` | `app/activity.html` (B-06 Activity Feed — custom CRM page) |
| `'calendar'` | `app/calendar.html` |
| `'chat'` | `app/chat.html` |
| `'inbox'` | `app/inbox-email.html` |
| `'settings'` | `app/settings.html` |
| `'profile'` | `app/profile.html` |
| `'finance'` | `app/finance.html` |
| `'sales'` | `app/sales.html` |
| `'team'` | `app/team-management.html` |
| `'tasks'` | `app/tasks.html` (B-07 Task Queue — custom CRM page) |
| `'review'` | `app/review.html` |
| `'marketing'` | `app/marketing.html` |
| `'employees'` | `app/employees.html` |
| `'user-management'` | `app/users.html` (B-10 User Directory — custom CRM page) |
| `'leads-detail'` | `app/leads-detail.html` (C-01 Lead Detail — detail page, no sidebar highlight) |
| `'opportunities-detail'` | `app/opportunities-detail.html` (C-04 Opportunity Detail — detail page) |
| `'contacts-detail'` | `app/contacts-detail.html` (C-02 Customer 360 — detail page) |
| `'quotes-detail'` | `app/quotes-detail.html` (C-06 Quote Detail — detail page) |
| `'leads-dashboard'` | `app/leads-dashboard.html` (A-02 Lead Funnel Dashboard) |
| `'contacts-health'` | `app/contacts-health.html` (A-03 Customer Health Dashboard) |
| `'quotes-dashboard'` | `app/quotes-dashboard.html` (A-05 Quote Approval Dashboard) |
| `'identity-dashboard'` | `app/identity-dashboard.html` (A-12 Identity & Access Posture Dashboard) |
| `'audit-dashboard'` | `app/audit-dashboard.html` (A-13 Platform Audit & Reliability Dashboard) |
| `'sales-analytics'` | `app/sales-analytics.html` (H-01 Sales Analytics) |
| `'finance-analytics'` | `app/finance-analytics.html` (H-04 Finance Analytics) |
| `'audit-report'` | `app/audit-report.html` (H-06 Audit Report) |
| `'opportunity-new'` | `app/opportunity-new.html` (I-03 New Opportunity Form) |
| `'quote-builder'` | `app/quote-builder.html` (I-05 CPQ Quote Builder) |
| `'sales-dashboard'` | `app/sales-dashboard.html` (A-04 Opportunity Pipeline Dashboard) |
| `'sales-cockpit'` | `app/sales-cockpit.html` (D-01 Sales Cockpit) |
| `'audit-log'` | `app/audit-log.html` (J-01 Audit Log) |
| `'compliance-report'` | `app/compliance-report.html` (J-02 Compliance Report) |
| `'rbac-audit'` | `app/rbac-audit.html` (J-04 RBAC Audit) |
| `'chat'` | `app/chat.html` |
| `'compose'` | `app/email-compose.html` |
| `'read-email'` | `app/email-read.html` |
| `'user-management-crm'` | `app/user-management-crm.html` (G-02 User Management Admin) |
| `'invoices'` | `app/invoices.html` (B-09 Invoice Queue) |
| `'subscriptions-detail'` | `app/subscriptions-detail.html` (C-09 Subscription Detail) |
| `'subscriptions-dashboard'` | `app/subscriptions-dashboard.html` (A-06 Subscription Revenue Dashboard) |
| `'tenants-dashboard'` | `app/tenants-dashboard.html` (A-11 Tenant & Entitlement Dashboard) |
| `'accounts'` | `app/accounts.html` (B-04 Account List) |
| `'accounts-detail'` | `app/accounts-detail.html` (C-03 Account Profile) |
| `'orders-detail'` | `app/orders-detail.html` (C-07 Order Detail) |
| `'invoices-detail'` | `app/invoices-detail.html` (C-08 Invoice Detail) |
| `'contact-new'` | `app/contact-new.html` (I-02 New Contact Form) |
| `'org-settings'` | `app/org-settings.html` (G-01 Organization Settings) |
| `'roles'` | `app/roles.html` (G-03 Role & Permission Editor) |
| `'billing-settings'` | `app/billing-settings.html` (G-04 Billing & Subscription Settings) |
| `'integrations'` | `app/integrations.html` (G-05 Integration Settings) |
| `'notifications'` | `app/notifications.html` (G-06 Notification Settings) |
| `'feature-flags'` | `app/feature-flags.html` (G-07 Feature Flags) |
| `'compliance-settings'` | `app/compliance.html` (G-08 Compliance Settings) |
| `'data-governance'` | `app/data-governance.html` (J-03 Data Governance Console) |
| `'privacy'` | `app/privacy.html` (J-05 Consent & Privacy Manager) |
| `'support-dashboard'` | `app/support-dashboard.html` (A-07 Support Operations Dashboard) |
| `'engagement-dashboard'` | `app/engagement-dashboard.html` (A-08 Engagement & Comms Dashboard) |
| `'knowledge-dashboard'` | `app/knowledge-dashboard.html` (A-09 Knowledge Base Dashboard) |
| `'workflows-dashboard'` | `app/workflows-dashboard.html` (A-10 Workflow Automation Dashboard) |
| `'cases'` | `app/cases.html` (B-05 Case List) |
| `'partners'` | `app/partners.html` (B-11 Partner List) |
| `'cases-detail'` | `app/cases-detail.html` (C-05 Case Detail) |
| `'workflow-run-detail'` | `app/workflow-run-detail.html` (C-10 Workflow Run Detail) |
| `'partners-detail'` | `app/partners-detail.html` (C-11 Partner Profile) |
| `'knowledge-article'` | `app/knowledge-article.html` (C-12 Knowledge Article Detail) |
| `'support-console'` | `app/support-console.html` (E-01 Support Console) |
| `'marketing-workspace'` | `app/marketing-workspace.html` (F-01 Marketing Workspace) |
| `'territories'` | `app/territories.html` (G-09 Territory Management) |
| `'marketing-analytics'` | `app/marketing-analytics.html` (H-02 Marketing Analytics) |
| `'support-analytics'` | `app/support-analytics.html` (H-03 Support Analytics) |
| `'workflow-analytics'` | `app/workflow-analytics.html` (H-05 Workflow Analytics) |
| `'report-builder'` | `app/report-builder.html` (H-07 Report Builder) |
| `'case-new'` | `app/case-new.html` (I-04 New Case Form) |
| `'campaign-new'` | `app/campaign-new.html` (I-06 New Campaign Wizard) |
| `'workflow-builder'` | `app/workflow-builder.html` (K-01 Workflow Builder) |
| `'object-builder'` | `app/object-builder.html` (K-02 Object Builder) |
| `'rule-builder'` | `app/rule-builder.html` (K-03 Rule Builder) |
| `'approval-lanes'` | `app/approval-lanes.html` (K-04 Approval Lanes Kanban) |
| `'inbox'` | `app/inbox.html` (L-01 Shared Inbox) |
| `'inbox-thread'` | `app/inbox-thread.html` (L-02 Inbox Thread View) |
| `'routing-config'` | `app/routing-config.html` (L-03 Routing Configuration) |
| `'ai-copilot'` | `app/ai-copilot.html` (M-01 AI Copilot) |
| `'ai-insights'` | `app/ai-insights.html` (M-02 AI Insights Dashboard) |

Auth pages do not set `CRM_PAGE` — they do not load `crm-shell.js`.

---

## 19. Library Matrix

Include only the libs a page actually uses. The seed's script block is a **starting point, not an authority** — seed pages sometimes carry over libs from a shared template that the specific page never uses. The HTML elements on the page are the definitive test: if the element type listed in the table below is absent from the page's HTML, exclude the lib regardless of what the seed script block says.

| Lib script | Include when |
|-----------|-------------|
| `Sortable.min.js` | Page has draggable list (sortable-handle elements) |
| `chartjs/chart.js` | Page has `<canvas>` chart (Chart.js doughnut/line/bar) |
| `apexcharts/apexcharts.min.js` | Page has `<div id="chart...">` ApexCharts element |
| `datatables/datatables.min.js` | Page has `<table id="dt_...">` DataTable |
| `flatpickr/flatpickr.min.js` | Page has date/time picker inputs |

**How to detect from a seed page:** scan the seed's `<script>` block at the bottom of `<body>`. Every `<script src="...libs/...">` tag maps directly to one of the entries above. Copy the lib set exactly.

**Libs already in `global.min.js` (do NOT add separately):**
jQuery, Bootstrap 5, SimpleBar, Node Waves, Bootstrap Select, Popper.js

---

## 20. Sidebar Link Update Protocol

`crm-shell.js` currently contains sidebar links pointing to **seed file paths** (e.g., `href="index.html"`, `href="customers.html"`). These are correct for the seed but wrong for the CRM — they bypass the framework entirely.

**Rule:** Each time a new `app/` page is built and verified, update the corresponding `href` in `crm-shell.js` to point to `app/pagename.html`.

**Current sidebar hrefs that need updating as pages are built:**

| Current href in crm-shell.js | Update to |
|-----------------------------|-----------|
| `href="index.html"` (Default Dashboard) | `href="app/dashboard.html"` |
| `href="customers.html"` | `href="app/customers.html"` |
| `href="leads.html"` (if added) | `href="app/leads.html"` |
| `href="deals.html"` | `href="app/deals.html"` |
| `href="activities.html"` | `href="app/activities.html"` |
| `href="calendar.html"` | `href="app/calendar.html"` |
| `href="chat.html"` | `href="app/chat.html"` |
| `href="email/inbox.html"` | `href="app/inbox-email.html"` |

**Never update a href until the target page is built and browser-verified.** A broken link is worse than a seed link.

Since `crm-shell.js` uses `<base href="../">` resolution (pages are in `app/`), `href="app/dashboard.html"` resolves correctly to `src/app/dashboard.html` from any `app/` page.

---

## 21. Inter-Page Linking Rules

All pages live in `src/app/`. All pages have `<base href="../">`. This means **all hrefs are resolved relative to `src/`**, not relative to `src/app/`.

| Link target | Correct href | Wrong href |
|-------------|-------------|-----------|
| Another app/ page | `href="app/leads.html"` | `href="leads.html"` |
| Seed page (should not happen in production) | `href="index.html"` | — |
| Asset | `href="assets/images/logo.svg"` | `href="../assets/images/logo.svg"` |
| Auth page | `href="app/login.html"` | `href="login.html"` |

**Breadcrumb home link** is always `href="app/dashboard.html"` on every page.

**Subdirectory pages** (e.g., `app/leads/detail.html`) would need `<base href="../../">` and all hrefs adjusted accordingly. Avoid subdirectories — keep all pages flat in `src/app/` to maintain a single consistent `<base href="../">`.

---

## 22. How to Read a Seed Page (Lib Detection Procedure)

Before building any app page, read the seed's script block to extract the exact lib set. The seed script block is always at the bottom of `<body>`, before `</body>`.

**What to look for:**

```html
<!-- These are the libs section — note every assets/libs/... script -->
<script src="assets/libs/sortable/Sortable.min.js"></script>
<script src="assets/libs/chartjs/chart.js"></script>
<script src="assets/libs/apexcharts/apexcharts.min.js"></script>
<script src="assets/libs/datatables/datatables.min.js"></script>
<script src="assets/libs/flatpickr/flatpickr.min.js"></script>

<!-- The seed's own page JS — read this file to extract chart configs -->
<script src="assets/js/dashboard/dashboard.js"></script>
```

Use the seed's script block as a reference for which libs the page likely needs. Before including each lib, cross-check against §19 — if the seed loads a lib but the page HTML has no matching element type, exclude it. When §19 and the seed script block conflict, **§19 wins** (HTML elements are authoritative). The seed's own page JS (`assets/js/dashboard/dashboard.js`, etc.) is your source for the page driver — copy its configs verbatim into `crm-[page].js`.

**HARD RULE — No invented configs:**
Before writing a single line of a page driver, open the seed JS file(s) the page loads and grep for every element ID present on the page. If a config exists in the seed JS, copy it verbatim — data, type, height, formatters, every property. If an element has **no** config in any seed JS file, it renders without JS (plain HTML). Never write a chart config, DataTable config, or any element initialisation from memory. Check §24 first — if the config is already catalogued there, copy from the catalogue. If not catalogued, read the seed JS file, copy the config, then add it to §24.

---

## 24. Seed JS Element Catalogue

**Purpose:** Every chart and DataTable element ID found in the seed JS files, with its exact config properties. Before writing any page driver, look up the element ID here. If it is listed, copy the config verbatim. If it is not listed, read the seed JS file, copy the config, and add it here.

**Source files catalogued:**
- `src/assets/js/dashboard/dashboard.js` — loaded by `src/index.html`, `src/leads.html`, `src/review.html`, and others
- `src/assets/js/dashboard/activities.js` — loaded exclusively by `src/activities.html`
- `src/assets/js/dashboard/deals.js` — loaded exclusively by `src/deals.html`
- `src/assets/js/dashboard/sales.js` — loaded exclusively by `src/sales.html`
- `src/assets/js/dashboard/finance.js` — loaded exclusively by `src/finance.html`
- `src/assets/js/app/crm-team-management.js` — loaded exclusively by `src/app/team-management.html` (verbatim from seed `management.js`)
- `src/assets/js/app/crm-review.js` — loaded exclusively by `src/app/review.html` (verbatim from seed `review.js`)
- `src/assets/js/app/crm-user-management.js` — loaded exclusively by `src/app/user-management.html` (verbatim from seed `user-management.js`)
- `src/assets/js/dashboard/marketing.js` — loaded exclusively by `src/marketing.html`
- `src/assets/js/plugins/fullcalendar.js` — loaded exclusively by `src/calendar.html`

All configs are guarded with `if (element)` so they only run when the element exists on the page.

---

### DataTables

| Element ID | pageLength | columnDefs | Search div ID | Notes |
|-----------|-----------|-----------|--------------|-------|
| `#dt_NewCustomers` | 6 | targets:[0] orderable:false | `#dt_NewCustomers_Search` | select:false, standard search relocation pattern |
| `#dt_CustomerList` | 12 | targets:[0] orderable:false | `#dt_CustomerList_Search` | select:false, standard search relocation pattern |
| `#dt_ScrollVertical` | **NOT INITIALISED** | — | `#dt_ScrollVertical_Search` (empty) | Plain HTML table — no DataTable init in dashboard.js. Renders all rows in source order with no pagination. Do NOT wrap in DataTable. |
| `#dt_Tasks` | 10 | col[1] orderable:false, col[5] orderable:false | `#dt_Tasks_Search` | Custom B-07 Task Queue. Data-driven from `CRM_DUMMY.tasks.data`. Pre-sorted overdue-first. Custom search ext: `_overdueOnly`, `_entityFilter`, `_ownerFilter`. createdRow sets data-overdue/data-entity-type/data-owner. |
| `#dt_Activities` | 10 | col[3] orderable:false, col[5] orderable:false | `#dt_Activities_Search` | Custom B-06 Activity Feed. Data-driven from `CRM_DUMMY.activities.data`. Pre-sorted occurred_at DESC. Custom search ext: `_typeFilter`, `_actorFilter`. createdRow sets data-type/data-actor. Read-only (no edit/delete). |
| `#dt_Users` | 10 | col[3] orderable:false, col[4] orderable:false, col[5] orderable:false | `#dt_Users_Search` | Custom B-10 User Directory. Data-driven from `CRM_DUMMY.users.data`. Sorted display_name ASC. Custom search ext: `_roleFilter`, `_statusFilter`. Status/last_login stubbed (not in dummy data). createdRow sets data-role/data-status. |

---

### ApexCharts

**`#chartTrafficSources`**
- Type: `bar`, stacked horizontal, stackType:`100%`, height:95
- Series: 5 (Organic Search 41.5, Direct 27, Referral 18, Social 10.3, Email 3.2)
- Fill colours: `rgba(--bs-primary-rgb, 0.1/0.25/0.50/0.75/1.0)`
- No axes labels, no grid, no legend
- Tooltip: `val + "%"`

**`#chartOrderByTime`**
- Type: `heatmap`, height:250
- Series: 5 time slots (8am/10am/12pm/2pm/4pm) × 7 days (Mon–Sun)
- Color ranges: 0–10 → `#E0E7FF`, 11–25 → `#A5B4FC`, 26–50 → `#6366F1`
- stroke width:2, color:`var(--bs-body-bg)` (cell borders)
- No grid, no legend

**`#chartDealsOverview`**
- Type: `area`, height:225
- Series: `[95,95,70,70,95,95,55,55,85,85]` (name:'Growth')
- Stroke: smooth, width:2, color:`var(--bs-info)`
- Fill: solid, `rgba(--bs-info-rgb, 0.1)`, opacity:1
- Markers: hover size:6, strokeColors:`var(--bs-info)`, strokeWidth:3
- Y-axis: min:0, max:100, hidden; X-axis: Jan–Sep, hidden; grid: hidden

**`#chartLeadAnalytics`**
- Type: `area`, height:120 (sparkline style)
- Series: `[80,95,75,90,75,90]` (name:'Growth')
- Stroke: smooth, width:2, color:`var(--bs-primary)`
- Fill: solid, `rgba(--bs-primary-rgb, 0.1)`, opacity:1
- Markers: hover size:6, strokeColors:`var(--bs-primary)`, strokeWidth:3
- All axes hidden, grid hidden

**`#statusChart`**
- Type: `radialBar`, height:350, sparkline enabled
- Series: `[35]`
- startAngle:-95, endAngle:95
- Track: `rgba(--bs-white-rgb, 0.3)`, strokeWidth:'100%', margin:25
- Value formatter: returns `$5.7m` (static — ignores val)
- Fill: `var(--bs-white)`

**`#chartRevenue`**
- Type: `bar`, height:280
- Series default: `[120,350,450,120,200,180,300,120,250,350,250,180]` (Jan–Dec)
- columnWidth:70%, borderRadius:4
- Fill: gradient vertical, gradientToColors:`var(--bs-info)`, opacityFrom:1, opacityTo:0.6
- Y-axis: min:0, max:500, formatter:`val + 'K'`
- Tab switching via `#todayRevenueTab`, `#weekRevenueTab`, `#monthRevenueTab` event listeners

**`#chartContacts`**
- Type: `bar`, height:120, width:150 (sparkline)
- Series: `[120,350,450,300,120,250]`
- columnWidth:60%, borderRadius:2
- Fill: gradient vertical, gradientToColors:`var(--bs-info)`, opacityFrom:1, opacityTo:0.6
- All axes hidden

**`#chartRetentionRate`**
- Type: `bar`, stacked, height:295
- Series: SMEs `[40,80,70,20,20,25]`, Startups `[20,25,25,50,20,20]`, Enterprises `[20,20,20,20,15,15]`
- X-axis: Jan–Jun; Y-axis hidden
- Fill colours: `var(--bs-primary)`, `rgba(--bs-primary-rgb,0.4)`, `rgba(--bs-primary-rgb,0.1)`
- Legend: position bottom

**`#reviewSourcesChart`**
- Type: `bar`, stacked horizontal, stackType:`100%`, height:95
- Series: 5 (Website 30, Google 25, App Store 20, Play Store 15, Social Media 10)
- Fill colours: `rgba(--bs-primary-rgb, 0.1/0.25/0.50/0.75/1.0)` (same as chartTrafficSources)
- No axes, no grid, no legend; stroke width:0; animations enabled

**`#opportunityTrendChart`**
- Type: `area`, height:280
- Series: `[890000,760000,1020000,960000,880000,910000,940000,1000000,980000,920000,970000,1010000]`
- Colors: `["var(--bs-primary)","var(--bs-dark)"]`
- Stroke: smooth, width:2, **dashArray:5** (dashed line)
- Fill: gradient vertical, shade:'light', shadeIntensity:0.1, opacityFrom:0.08, opacityTo:0.01, stops:[20,100]
- Markers: size:0, hover size:6, strokeColors:`var(--bs-primary)`
- Y-axis: **min:700000, max:1100000**, tickAmount:5, formatter:`"$" + (value/100) + "M"` *(seed bug — renders "$7000M" etc. Preserve verbatim.)*
- X-axis: Jan–Dec, axisBorder color:`var(--bs-border-color)`
- Grid: strokeDashArray:5, yaxis lines show:true
- Legend: hidden

---

### Chart.js (canvas elements — require DOMContentLoaded)

**`#chartTasksOverview`**
- Type: `doughnut` (Chart.js, not ApexCharts)
- Data: `[5,6,4]`
- Labels: `['Salary','Bonus','Commission','Overtime','Reimbursement','Benefits']` (6 labels, 3 data points — seed inconsistency, preserve verbatim)
- BackgroundColors: `['#5955D1','#ACAAE8','#DEDDF6']`
- borderRadius:3, spacing:0, hoverOffset:5, borderWidth:3, borderColor:'#fff'
- cutout: `'70%'`
- Custom `centerTextPlugin` — shows total or hovered value in centre
- Legend: hidden; Tooltip: disabled
- **Must use `document.addEventListener('DOMContentLoaded', fn)` — canvas element**

---

### From `deals.js` (source: `src/assets/js/dashboard/deals.js`)

**`#dt_NewCustomers`** (same config as dashboard.js — see above)

**`#chartDeals`**
- Type: `area`, height:320
- Series: 2 — Income `[3500,5000,4200,5500,5000,6200,4800,6500,5800,7200,6600,7500]`, Expenses `[2500,3100,2900,3700,3300,4100,3600,3900,4200,4000,4600,4300]`
- Colors: `["var(--bs-primary)","var(--bs-secondary)"]`
- Stroke: smooth, width:[2,2], dashArray:[0,5] (Income solid, Expenses dashed)
- Fill: gradient vertical, opacityFrom:0.08→0.01 (note: seed has duplicate `gradient` key — second definition wins, both series get secondary gradient — seed bug, preserved verbatim)
- Y-axis: min:0, max:8000, tickAmount:5, formatter:`"$"+(value/100)+"K"`
- X-axis: Jan–Dec; grid strokeDashArray:5; legend hidden
- **Tab switching** via `#todayDealsTab`, `#weekDealsTab`, `#monthDealsTab` event listeners (same pattern as `#chartRevenue`)

**`#chartDealPipeline`**
- Type: `bar`, height:340, stacked:false
- Series: 2 — Deals `[850,550,1210,950,750,1520,1310]`, Value($) `[960000,810000,720000,610000,490000,1830000,400000]`
- X-axis categories: New Lead, Contacted, Qualified, Proposal Sent, Negotiation, Closed Won, Closed Lost
- Colors: `["var(--bs-primary)","rgba(var(--bs-primary-rgb),0.1)"]`
- columnWidth:55%, borderRadius:3
- **Dual Y-axis**: left (deal count, plain), right (opposite:true, formatter:`"$"+(value/10000)+"K"`)
- Tooltip: series index 1 → `'$'+val.toLocaleString()`, series 0 → plain number
- Grid: strokeDashArray:5, xaxis lines show:true; legend hidden

---

### From `sales.js` (source: `src/assets/js/dashboard/sales.js`)

**`#dt_RecentSales`**
- DataTable, pageLength:5, select:false, columnDefs targets[0] orderable:false
- Search relocation to `#dt_RecentSales_Search` (standard pattern)

**`#dt_TopSellingItems`**
- DataTable, pageLength:5, select:false, columnDefs targets[0] orderable:false
- Search relocation to `#dt_TopSellingItems_Search` (standard pattern)

**`#SalesChart`**
- Type: `area`, height:320
- Series: 2 — Income `[3500,5000,4200,5500,5000,6200,4800,6500,5800,7200,6600,7500]`, Expenses `[2500,3100,2900,3700,3300,4100,3600,3900,4200,4000,4600,4300]`
- Colors: `["var(--bs-primary)","var(--bs-danger)"]`
- Stroke: smooth, width:[2,2], dashArray:[0,0] (both solid)
- Fill: gradient vertical — same duplicate key bug as deals.js (seed bug, preserved verbatim)
- Y-axis: min:0, max:8000, tickAmount:5, formatter:`"$"+(value/100)+"K"`
- X-axis: Jan–Dec; grid strokeDashArray:5
- **Legend: show:true, position:'bottom'** (differs from deals — legend is visible here)
- **Tab switching** via `#todayRevenueTab`, `#weekRevenueTab`, `#monthRevenueTab`

**`#VisitorsChart`**
- Type: `bar`, height:295
- Series: 2 — Current `[4500,2050,3100,4800,1800,2500]`, Last Month `[4040,2050,4200,2800,1800,2050]`
- Colors: `['var(--bs-primary)','var(--bs-light)']`
- Fill: single gradient vertical, gradientToColors:`var(--bs-info)`, opacityFrom:1, opacityTo:0.6
- columnWidth:75%, borderRadius:4; dataLabels disabled; stroke width:0
- X-axis categories: `['Mobile'],['Desktop'],['Tablet'],['iPad pro'],['iPhone'],['Other']` (array-wrapped)
- Y-axis: hidden (`show:false`)
- Animations: easeinout, speed:800

**`#SalesGrowthChart`**
- Type: `area`, height:280
- Series: 1 — unnamed `[1000,2050,3100,4800,4800,1800,4500]`
- Colors: `['var(--bs-primary)']`; stroke color: `var(--bs-info)`, width:2, smooth
- Fill: single gradient vertical, gradientToColors:`var(--bs-info)`, opacityFrom:0.2, opacityTo:0.06
- X-axis: Mon–Sun; Y-axis: min:0, max:6000, tickAmount:4, formatter:`"$"+(value/100)+"K"`
- Animations: easeinout, speed:800

**`#MonthlyTargetChart`**
- Type: `radialBar`, height:350, sparkline enabled
- Series: `[75]`
- startAngle:-95, endAngle:95
- Track: `rgba(var(--bs-primary-rgb), 0.6)`, strokeWidth:'10%', margin:25
- Value formatter: returns `${totalEarning}%` where `totalEarning = 75.7` (hardcoded — ignores val)
- Fill: `colors: ['var(--bs-primary)']`
- Guard: `typeof MonthlyTargetChart !== undefined && MonthlyTargetChart !== null`

---

### From `activities.js` (source: `src/assets/js/dashboard/activities.js`)

**`#dt_Activities`**
- DataTable, pageLength:6, select:false, columnDefs targets[0] orderable:false
- Search relocation to `#dt_Activities_Search` (standard pattern)
- Agent Name column contains `avatar-xxs` avatar imgs — CSS-constrained (explicit px dimensions), so race condition does NOT apply; `autoWidth: false` is NOT used here (see GAP-026 clarification)

**`#callsChart`**
- Type: `line`, height:300
- Series: 3 — Calls `[40,55,38,62,70,68,80]`, Tasks `[20,27,19,31,45,34,40]`, Leads `[10,13,9,15,28,17,20]`
- Colors: primary, secondary, warning
- Stroke: curve:smooth, width:[3], dashArray:[0,8,5] (solid/dashed/dash-dot)
- Markers: hover size:6, strokeColors:`var(--bs-info)`
- X-axis: Mon–Sun; grid strokeDashArray:5; legend hidden

**`#tasksChart`**
- Type: `bar`, height:300
- Series: 1 — Completed Tasks `[12,18,14,22,25,20,30]`
- columnWidth:45%, borderRadius:2
- Color: primary; dataLabels disabled; grid strokeDashArray:5
- X-axis: Mon–Sun

**`#leadsChart`**
- Type: `donut`, height:260
- Series: `[35,20,45]`, labels:`['Closed','In Progress','New']`
- Colors: primary, info, success
- Donut size:65%; total label:'Total Leads', formatter returns 100 (35+20+45)
- dataLabels disabled; stroke width:0; legend hidden; tooltip disabled

---

### From `finance.js` (source: `src/assets/js/dashboard/finance.js`)

**`#summeryChart`** (note: seed spells it "summery" not "summary" — preserve verbatim)
- ApexCharts line, height:300
- 2 series: Revenue `[300000,80000,300000,300000,290000,210000,350000,500000,380000]`, Expenses `[0,200000,350000,180000,190000,400000,400000,280000,220000]`
- colors: `["var(--bs-secondary)","var(--bs-primary)"]`
- stroke: width:[2,2], curve:smooth, dashArray:[8,0] (Revenue dashed, Expenses solid)
- yaxis: min:500000, max:0 (seed bug — min>max, ApexCharts auto-corrects; preserve verbatim), tickAmount:5, formatter: `(value/1000)+"K"`
- xaxis: 8 categories `['Jan','Feb','Mar','May','Jun','July','Aug','Sep']` (9 data points, 8 labels — seed bug; preserve verbatim)
- legend: show:true, position:bottom, horizontalAlign:center
- Guard: `typeof summeryChart !== undefined && summeryChart !== null`

**`#expenseChart`** — Chart.js doughnut (canvas element)
- Custom `centerTextPlugin`: draws total (sum of data) + "Sources" label at center
- Data: `[800,600,400,200]` — Salaries, Rent, Software, Marketing
- backgroundColor: `['#5955D1','#ACAAE8','#d1d0f7','#DEDDF6']` (hardcoded hex, not CSS vars)
- cutout:65%, devicePixelRatio:2, borderRadius:3, borderWidth:3, borderColor/hoverBorderColor:'#fff'
- Legend: display:false; tooltip label callback: `context.label: context.formattedValue`
- Triggered via `document.addEventListener('DOMContentLoaded', expenseChartConfig)`

**`#dt_RecentTransactions`**
- DataTable, pageLength:5, select:false, lengthChange:false, info:true, paging:true
- Search relocation to `#dt_RecentTransactions_Search` (standard pattern)
- columnDefs: targets[0] orderable:false

**`#monthlyStatusChart`**
- ApexCharts radialBar, height:350, series:[70], sparkline enabled
- startAngle:-95, endAngle:95
- track: background `rgba(var(--bs-white-rgb),0.3)`, strokeWidth:'100%', margin:25
- value formatter hardcodes `75K` regardless of series value (seed inconsistency — HTML shows "92%"; preserve verbatim)
- fill: colors:`['var(--bs-white)']`
- Guard: `typeof monthlyStatusChart !== undefined && monthlyStatusChart !== null`

---

### From `management.js` (source: `src/assets/js/app/crm-team-management.js`, verbatim from seed `management.js`)

**`#dt_TeamPerformance`**
- DataTable, pageLength:6, select:false, columnDefs targets:[0] orderable:false
- Search relocation to `#dt_TeamPerformance_Search` (standard pattern)

**`#TeamPerformanceChart`**
- Type: `bar`, height:285
- Series: 3 — Team 1 `[70,82,88,95,40,60]`, Team 2 `[60,72,78,85,75,92]`, Team 3 `[55,65,70,78,65,50]`
- Colors: `["var(--bs-primary)","var(--bs-success)","var(--bs-warning)"]`
- columnWidth:65%, borderRadius:4; stroke show:true, width:3, color:`var(--bs-body-bg)`
- X-axis: Jan–Jun; Y-axis: formatter `v + "%"`; grid strokeDashArray:4
- Legend: position bottom, horizontalAlign center, markers radius:10
- Tooltip: `v + "%"`
- Guard: `typeof TeamPerformanceChart !== undefined && TeamPerformanceChart !== null`

**`#chartNewTeam`**
- Type: `bar`, height:230, width:250
- Series: 1 — unnamed `[120,350,120,300,450,250]`
- Color: `var(--bs-primary)`; columnWidth:60%, borderRadius:2; dataLabels disabled
- X/Y axes: all labels and borders hidden
- Fill: gradient vertical, gradientToColors:`var(--bs-info)`, opacityFrom:1, opacityTo:0.6, stops:[20,100]
- Tooltip: `"" + val + " New Member"`; legend hidden
- Guard: `if (chartNewTeam)`

---

### From `review.js` (source: `src/assets/js/app/crm-review.js`, verbatim from seed `review.js`)

**`#dt_RecentReviews`**
- DataTable, pageLength:5, **autoWidth:false**, select:false, lengthChange:false, info:true, paging:true
- columnDefs targets:[0] orderable:false
- Search relocation to `#dt_RecentReviews_Search` (standard pattern)
- Customer column contains avatar `<img>` elements — `autoWidth: false` prevents column-width race condition on image load (GAP-026)

**`#dt_TopRated`**
- DataTable, pageLength:5, select:false, lengthChange:false, info:true, paging:true
- columnDefs targets:[0] orderable:false
- Search relocation to `#dt_TopRated_Search` (standard pattern)

**`#reviewTrendChart`**
- Type: `area`, height:270
- Series: 1 — Reviews `[1500,4000,4200,5500,4000,5200,7800,6200,5000,4200,7000,7950]`
- Colors: `["var(--bs-primary)"]`; stroke smooth, width:[3], dashArray:[0,5]
- Fill: gradient vertical, opacityFrom:0.08, opacityTo:0.01
- Y-axis: min:0, max:8000, tickAmount:5, formatter `"" + (value/100) + "K"`
- X-axis: Jan–Dec; grid strokeDashArray:5; legend show:true, position:bottom
- **Tab switching** via `#todayReviewTrendTab`, `#weekReviewTrendTab`, `#monthReviewTrendTab`
- Tooltip: `"" + val + "K"`

---

### From `user-management.js` (source: `src/assets/js/app/crm-user-management.js`)

**`#dt_UserList`**
- DataTable, pageLength:6, select:false, lengthChange:false, info:true, paging:true
- columnDefs targets:[0] orderable:false
- Search relocation to `#dt_UserList_Search` (standard pattern)

---

### From `employee.js` (source: `src/assets/js/app/crm-employee.js`)

- **flatpickr('.flatpickr-date', {})** — applied to all `.flatpickr-date` inputs with empty options (date-only, default format)
- No chart or DataTable elements — driver is flatpickr init only

---

### From `task.js` (source: `src/assets/js/app/crm-task-management.js`)

- **Sortable** — applied to `#taskWrapper1`, `#taskWrapper2`, `#taskWrapper3`, `#taskWrapper4`
  - `group: 'shared'`, `animation: 150`
  - Guard: early return if `!window.Sortable`
  - Wrapped in `document.addEventListener('DOMContentLoaded', ...)`
- **flatpickr('.flatpickr-date', {})** — applied in a separate DOMContentLoaded listener

---

### From `marketing.js` (source: `src/assets/js/dashboard/marketing.js`)

**`#revChart`**
- Type: `bar`, height:90, sparkline enabled
- Series: 1 — unnamed `[40,60,50,70,50,67,54]`
- Color: `var(--bs-primary)`; stroke width:0; fill gradient vertical, opacityFrom:0.5→0.00
- Tooltip: disabled

**`#aovChart`**
- Type: `area`, height:90, sparkline enabled
- Series: 1 — unnamed `[44,46,46,45,47,46,46]`
- Color: `var(--bs-dark)`; stroke width:2, dashArray:[5]
- Fill gradient vertical, opacityFrom:0.05→0.01; tooltip disabled

**`#purchaseChart`**
- Type: `bar`, height:90, sparkline enabled
- Series: 1 — unnamed `[180,210,240,200,260,300,310]`
- Color: `rgba(var(--bs-info-rgb),0.6)`; columnWidth:60%; stroke width:0; tooltip disabled

**`#growthChart`**
- Type: `area`, height:90, sparkline enabled
- Series: 1 — unnamed `[50,20,70,20,60,20,95]`
- Color: `var(--bs-success)`; stroke width:2, dashArray:[5]
- Fill gradient vertical, opacityFrom:0.08→0.01; tooltip disabled

**`#adsTrendChart`**
- Type: `area`, height:320
- Series: 1 — Clicks `[1500,4000,4200,5500,4000,5200,7800,6200,5000,4200,7000,7950]`
- Colors: `["var(--bs-primary)","var(--bs-danger)"]`; stroke **stepline** curve, width:[2], dashArray:[5]
- Fill: gradient vertical, gradientToColors:`var(--bs-primary)`, opacityFrom:0.08→0.01
- Y-axis: min:0, max:8000, tickAmount:5; X-axis: Jan–Dec; grid strokeDashArray:5
- Legend: show:true, position:bottom, markers size:5 circle

**`#leadFunnelChart`**
- Type: `bar`, height:440, horizontal:true, distributed:true, barHeight:65%, borderRadius:3
- Series: 1 — Leads `[8140,5720,4860,3640,2220,1910]`
- Colors: 6× `var(--bs-primary)` (one per bar — distributed forces per-bar coloring)
- dataLabels enabled, formatter: `val + " (" + ((val/base)*100).toFixed(1) + "%)"` where base array is `[8140,5720,4860,3640,2220,1910]`
- X-axis categories: New Leads/Contacted/Qualified/In Progress/Closed Won/Closed Lost
- Grid borderColor:`#e6e6e6`, strokeDashArray:4; legend hidden

---

### From `fullcalendar.js` (source: `src/assets/js/plugins/fullcalendar.js`)

- **flatpickr on `#eventStartDate`** — `enableTime: true, dateFormat: "Y-m-d H:i"`
- **flatpickr on `#eventEndDate`** — `enableTime: true, dateFormat: "Y-m-d H:i"`
- **FullCalendar.Calendar on `#calendar`** — `initialView: 'dayGridMonth'`, editable:true, droppable:true
  - headerToolbar: left:`prev,next today`, center:`title`, right:`dayGridMonth,timeGridWeek,timeGridDay`
  - Draggable external events via `#external-events` (`.fc-event` items)
  - 6 predefined events: Meeting with Team (primary), Client Call (success), Webinar (warning), Team Lunch (danger), Project Deadline (info), Performance Review (secondary)
  - eventClick handler: shows `#eventDetailsModal` with event details
  - eventForm submit: adds event from modal inputs
- All wrapped in `document.addEventListener('DOMContentLoaded', ...)`

---

## 23. What NOT to Do

- **Never build page content from scratch** — always start from the seed verbatim
- **Never rename element IDs** — chart IDs and table IDs must match the seed exactly so the page driver can find them
- **Never use `CRM_DUMMY` or `CRM_API` for static display values** — if the seed hardcodes "5,758", keep "5,758" in the HTML
- **Never add `<aside>` or `<header>` to page HTML** — crm-shell.js injects these; duplicating them breaks layout
- **Never load a lib script twice** — global.min.js already bundles jQuery/Bootstrap; do not add separate jQuery/Bootstrap script tags
- **Never omit `<base href="../">`** — every asset path will resolve from `app/` and 404
- **Never set `window.CRM_PAGE` after `crm-shell.js` loads** — the shell reads it synchronously at parse time

---

## 25. Design-Phase Build Methodology

Absorbed from: `SYSTEMATIC UI FRAMEWORK.md` (L0–L12 layer model) · `SOP-BUILD.md` (§§1–10) · `SCREEN-PROTOCOL.md` (mode declaration + stop gates) — all three source files deleted 2026-05-17; content lives here.

This section governs custom Pakistan CRM page builds (design phase). Every page — new build or audit — follows this protocol. No HTML is written until Steps 1–5 artefacts are filed.

---

### 25.1 — Archetype Table (L1)

Every CRM page belongs to one archetype. The archetype determines slot structure and allowed components.

| Archetype | Description | CRM Page Examples |
|---|---|---|
| `dashboard` | Aggregate KPIs, charts, activity feeds | Owner Dashboard, Sales Analytics |
| `resource_list` | Filterable, sortable tabular data | Lead Queue, Contacts, Followups |
| `detail_view` | Single entity, full field set, timeline | Lead Detail, Contact Detail |
| `form` | Create/edit entity with validation | Add Lead, Edit Contact, Quick Add |
| `analytics` | Deep chart/report views, date range controls | Sales Analytics, Marketing Reports |
| `settings` | Config, preferences, admin controls | Settings, User Management, Audit Log |

---

### 25.2 — Mode Declaration

Declare before any screen work begins:

| Mode | When to use | What artefacts do |
|------|------------|-------------------|
| **BUILD** | Screen does not exist yet | Artefacts written as design specs → code written against them |
| **AUDIT** | Screen already exists | Artefacts derived from seed + existing page → page checked against them |

Both modes produce identical artefacts. BUILD writes then codes. AUDIT writes then checks.

---

### 25.3 — Per-Screen Artefact Sequence (Steps 1–9)

**Step 1 — L0: Seed Audit Card**

Before building any page, audit its closest NexLink seed equivalent.

```
Page URL (seed equivalent):
Archetype (from §25.1):
Column layout:              (e.g. col-xxl-8 + col-xxl-4)
Card count:
Chart types used:
Table columns:
Badges / status indicators:
Interactive elements:
Components shared with other pages:
Data source: static / dynamic
```

**Step 2 — L2: Behaviour Contract**

```
Page:
Archetype:
User Intent:    (one sentence — what does the user come here to do?)
Primary Actions:
  1.
  2.
  3.
Secondary Actions:
States: loading | empty | error | populated | filtered
Key Transitions:
  - [trigger] → [outcome]
Data Dependencies:
  - [CRM_DUMMY key] drives [what]
```

**Step 3 — L2.5: Wireframe**

ASCII layout per archetype. Created once per archetype, reused for all pages of that type. Format rules: ASCII only, slot labels in CAPS, data bindings in `[brackets]`, interactive elements marked with `[action]`.

**resource_list archetype:**
```
┌─────────────────────────────────────────────────────────────┐
│ PAGE-HEAD                                                    │
│  BREADCRUMB: Home > [page_title]          [Add] [Import]    │
├─────────────────────────────────────────────────────────────┤
│ FILTER-ROW                                                   │
│  [source▼]  [stage▼]  [owner▼]  [date range]  🔍 [search]  │
├─────────────────────────────────────────────────────────────┤
│ DATA-TABLE                                                   │
│  ☐  NAME        PHONE       EMAIL       STAGE   OWNER  ACT  │
│  ─  ─────────  ──────────  ──────────  ──────  ─────  ───  │
│  ☐  [name]     [phone]     [email]     BADGE   AVATAR  ⋮    │
├─────────────────────────────────────────────────────────────┤
│ PAGINATION                                                   │
│  Showing [x]–[y] of [total]          [‹] [1] [2] [3] [›]   │
└─────────────────────────────────────────────────────────────┘
```

**dashboard archetype:**
```
┌─────────────────────────────────────────────────────────────┐
│ PAGE-HEAD: BREADCRUMB                                        │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  KPI-CARD    │  KPI-CARD    │  CHART-CARD  │  KPI-CARD      │
│  [metric]    │  [metric]    │  [chart]     │  [metric]      │
├──────────────┴──────────────┼──────────────┴────────────────┤
│  CHART-CARD (full width)    │  KPI-CARD                      │
│  [chart]                    │  [metric]                      │
├─────────────────────────────┴────────────────────────────────┤
│  PANEL-LEFT (col-8)         │  PANEL-RIGHT (col-4)           │
│  SECTION-CARD [title]       │  SECTION-CARD [title]          │
│  [list items]               │  [list items]                  │
└──────────────────────────────────────────────────────────────┘
```

**Step 4 — L4.5: Data Contract Table**

For every dynamic element: declare source before writing code. If a field is not in CRM_DUMMY, add it before proceeding.

```
Element ID / slot     | CRM_DUMMY key          | Field(s)           | Derived formula
─────────────────────────────────────────────────────────────────────────────────────
kpi-leads-value       | leads.data             | .length            | count
kpi-leads-badge       | leads.data             | created_at         | % change vs prior 30d
sidebar-overdue-count | overdueFollowups       | .length            | direct
```

Rule: No placeholder `—` values. No deferred wiring. Every element covered before HTML is touched.

**Step 5 — L9: Assembly Spec**

```
Page: [name].html
Archetype:
Shell: crm-shell.js — CRM_PAGE='[name]'
Seed equivalent:
Column layout:

Slots (top to bottom, left to right):
  1. [slot name] — [component] — [data binding]
  2.
  ...

Components required from crm-components.js:
  -
New components needed (not yet in crm-components.js):
  -
Page JS file: crm-[name].js
```

**Step 6 — L8: Component Check**

Before writing any rendering code, check the component registry in `crm-components.js`:
- All components required by the assembly spec exist → proceed
- Component marked inline-only → migrate or note as L8 debt
- Component not yet built → build before page code starts
- Never re-implement a component inline if it already exists in crm-components.js

**Step 7 — BUILD or AUDIT Execution**

BUILD mode:
1. Follow HTML scaffold in §2 exactly
2. Script load order per §3 — no deviation
3. Every dynamic value flows from CRM_DUMMY via the data contract (Step 4)
4. Run §16 Build Checklist before handing to QC

AUDIT mode:
1. Compare built page slot-by-slot against assembly spec (Step 5)
2. Compare every dynamic element against data contract (Step 4)
3. Compare visual layout against wireframe (Step 3)
4. Log every deviation using the QC Fail format in §26.5
5. Fix all gaps before proceeding to Step 8

**Step 8 — T1–T4 QC**

Run all four tiers in order. See §26 for full checklists. A page that has not passed all four tiers is not done.

**Step 9 — Deploy Gate**

See §26.6. Every item checked before declaring a page done.

---

### 25.4 — Per-Screen Record Template

File this before Step 1. This is the header block for every ARTEFACTS file.

```
Screen Record: [page].html
Date started:
Mode: BUILD / AUDIT
Seed equivalent:

ARTEFACTS (Steps 1–6)
[ ] L0  Seed Audit Card        — filed
[ ] L2  Behaviour Contract     — written
[ ] L2.5 Wireframe             — exists (new / cited from §25.3)
[ ] L4.5 Data Contract Table   — all dynamic elements covered
[ ] L9  Assembly Spec          — written
[ ] L8  Component Check        — inventory complete

BUILD COMPLETION / AUDIT GAP FIXES (Step 7)
[ ] §16 Build Checklist passed (BUILD mode)
[ ] All gaps fixed and code-verified (AUDIT mode)

QC (Step 8)
[ ] T1 Structure:  PASS / FAIL / IN PROGRESS
[ ] T2 Data:       PASS / FAIL / IN PROGRESS
[ ] T3 Visual:     PASS / FAIL / IN PROGRESS
[ ] T4 Behaviour:  PASS / FAIL / IN PROGRESS

DEPLOY (Step 9)
[ ] Deploy gate: CLEARED

Overall: DONE / IN PROGRESS / BLOCKED
Sign-off:
```

---

### 25.5 — Stop Gate Summary

| Gate | Condition to pass |
|------|-------------------|
| After Step 1 | Seed audit card filed |
| After Step 2 | Behaviour contract written |
| After Step 3 | Wireframe exists for this archetype |
| After Step 4 | Data contract covers every dynamic element |
| After Step 5 | Assembly spec written |
| After Step 6 | Component inventory complete, gaps noted |
| After Step 7 | BUILD: §16 checklist passed · AUDIT: all gaps fixed |
| After Step 8 | T1 PASS · T2 PASS · T3 PASS · T4 PASS |
| After Step 9 | Deploy gate cleared |

---

### 25.6 — What This Process Bans

- Starting T1–T4 before artefacts (Steps 1–5) are written
- Writing HTML before the assembly spec (Step 5) is frozen
- Deferring data contract entries with "to be wired later"
- Verifying T3 from screenshots or memory instead of the wireframe
- Verifying T2 from console output instead of source code inspection
- Re-implementing a component inline if it already exists in crm-components.js
- Declaring a page done without a signed-off per-screen record

---

## 26. QC Protocol

Absorbed from: `SOP-QC.md` (T1–T4 tiers · deploy gate · regression protocol · QC fail format) — source file deleted 2026-05-17; content lives here.

**Rule: A page that has not passed all four QC tiers is not done. It is in progress.**

---

### 26.1 — QC Tiers Overview

| Tier | Name | What it checks | Who runs it |
|------|------|----------------|-------------|
| T1 | Structure | Script load order, DOM structure, sidebar, header | Builder (self-check) |
| T2 | Data | Every dynamic value populated, PKR formatting | Builder (self-check) |
| T3 | Visual | Layout vs wireframe at canonical breakpoints | Reviewer |
| T4 | Behaviour | All states and interactions from behaviour contract | Reviewer |

Canonical breakpoints: **1440px** (primary) and **1920px** (expanded sidebar).

---

### 26.2 — T1: Structure Checklist

Run before showing the page to anyone.

```
SCRIPT & SHELL
[ ] CRM_PAGE constant set before crm-shell.js loads
[ ] Script load order matches §3 exactly
[ ] crm-dummy.js loads before crm-shell.js
[ ] crm-components.js loads before page JS
[ ] No 404 errors in browser console for any script or asset
[ ] No JavaScript errors in browser console on load

DOM STRUCTURE
[ ] <div class="page-layout"> wraps everything
[ ] <main class="app-wrapper"> present
[ ] <div class="container-fluid"> is the direct child of app-wrapper
[ ] app-page-head with breadcrumb is first child of container-fluid
[ ] Breadcrumb shows: Home > [Page Title]
[ ] All IDs referenced in page JS exist in the HTML
[ ] No duplicate IDs on the page

SIDEBAR
[ ] Sidebar renders (not blank)
[ ] Correct tab is active in icon strip (matches CRM_PAGE)
[ ] Correct panel is visible in expanded sidebar (matches CRM_PAGE)
[ ] Active menu item is highlighted in the panel
[ ] Overdue count badge visible and non-zero (if followups data has overdue)

HEADER
[ ] "Pakistan CRM" brand text renders
[ ] User name and role render (from CRM_DUMMY.users.data[0])
[ ] "Today New Leads" count renders (non-zero)
[ ] Theme toggle present
[ ] Calendar icon links to app/calendar.html
[ ] Notification badge count renders
```

---

### 26.3 — T2: Data Checklist

Verify every dynamic value is populated. No `—` placeholders, no `undefined`, no `NaN`.

```
GENERAL
[ ] Zero hardcoded values — every number comes from CRM_DUMMY
[ ] No element shows '—' or 'undefined' or 'NaN' after JS executes
[ ] No element shows the placeholder text from the HTML

KPI CARDS (dashboard archetype)
[ ] Primary value (h2) populates from data
[ ] Badge/delta populates and shows correct sign (+/-)
[ ] "Vs last month" or secondary line populates
[ ] Sparkline chart renders (not a blank box)

DATA TABLES (resource_list archetype)
[ ] Table has rows — not empty on first load
[ ] All columns populate for every row (no blank cells)
[ ] Status badges show correct colour for each stage
[ ] Owner column shows name (not user_id)
[ ] Action column renders
[ ] Pagination shows correct "Showing X–Y of Z"

CHARTS
[ ] Every chart container renders an SVG (not a blank div)
[ ] Chart data points match domain data (not hardcoded test values)
[ ] Chart axes / labels render if specified
[ ] No ApexCharts error in console

SIDEBAR DYNAMIC VALUES
[ ] sidebar-overdue-count updates from CRM_DUMMY.overdueFollowups.length
[ ] header-today-leads updates from CRM_DUMMY.todayLeads.length
[ ] header-notif-count renders

PKR FORMATTING
[ ] All monetary values use PKR prefix
[ ] Values ≥ 1,00,000 use Lakh notation (PKR 4.5L)
[ ] Values ≥ 1,00,00,000 use Crore notation (PKR 2.3Cr)
[ ] No raw number without PKR prefix
```

---

### 26.4 — T3: Visual Checklist

Compare built page against wireframe (§25.3) at 1440px and 1920px.

```
LAYOUT
[ ] Column grid matches the assembly spec
[ ] No cards overflow their containers
[ ] No horizontal scrollbar at 1440px
[ ] Card spacing is consistent (1rem gutters)
[ ] Page head breadcrumb aligns correctly

SIDEBAR (1920px)
[ ] Sidebar expands to full panel (320px)
[ ] Dashboard tab panel shows all 11 nav items
[ ] CRM tab panel shows Leads, Pipeline, Contacts sections
[ ] Active item highlighted correctly

SIDEBAR (1440px)
[ ] Sidebar shows icon strip only (80px) — media query fires at ≤1480px
[ ] Hover on icon strip expands panel
[ ] No layout shift when sidebar expands

CARDS & COMPONENTS
[ ] KPI cards: value is visually prominent (h2), supporting text smaller
[ ] Status badges: colour matches stage
[ ] Chart containers are not taller than their card allows

TYPOGRAPHY & COLOUR
[ ] No raw Bootstrap default colours — all colours via semantic classes
[ ] No inline styles except where deliberately set by JS
[ ] Font is 'Instrument Sans' throughout

SEED COMPARISON (seed-equivalent pages)
[ ] Section card titles match seed equivalents
[ ] Table column order matches seed
[ ] KPI card layout matches seed structure
```

---

### 26.5 — T4: Behaviour Checklist

Walk through every state in the L2 behaviour contract.

```
STATES
[ ] Loading state: page renders gracefully before JS executes
[ ] Populated state: all dynamic content visible with CRM_DUMMY data
[ ] Empty state: empty CRM_DUMMY data shows empty state message (not blank)
[ ] Error state: JS error is caught and does not break page layout

INTERACTIONS (resource_list pages)
[ ] Filter dropdowns render and are clickable
[ ] Search input accepts text
[ ] Table rows are clickable
[ ] Action dropdown on each row opens
[ ] Pagination buttons render

INTERACTIONS (dashboard pages)
[ ] Chart tooltips appear on hover
[ ] "View All" links on cards point to correct pages
[ ] Dropdown menus (⋮) on cards open and close

NAVIGATION
[ ] Breadcrumb Home link → app/dashboard.html
[ ] Sidebar nav links navigate correctly
[ ] No broken links (404) on any nav item for built pages

THEME
[ ] Dark mode toggle switches theme
[ ] Theme persists on page reload
[ ] Both light and dark mode: no invisible text, no broken contrast
```

---

### 26.6 — QC Fail Protocol

When any tier fails, log using this format:

```
Page: [name].html
Tier: T[1|2|3|4]
Item: [exact checklist item]
Observed: [what was seen]
Expected: [what should be seen]
Root cause: [why it happened — specific, not vague]
Fix: [what code change resolves it]
```

Rules:
1. Fix before proceeding — do not move to next tier with an open failure
2. Re-run the full tier after the fix — fixes can introduce regressions
3. Never claim a fix without source file inspection. Console output and screenshots are not verification.

---

### 26.7 — Deploy Gate

Before any page goes to staging or production:

```
[ ] All four QC tiers passed
[ ] No console errors at runtime
[ ] No 404s for any asset (scripts, images, fonts)
[ ] Page tested in Chrome and Firefox (minimum)
[ ] Page tested at 1440px and 1920px
[ ] Page tested at 768px (tablet — layout must not break)
[ ] Dark mode tested
[ ] All links to other built pages verified
[ ] Links to unbuilt pages point to # (not broken hrefs)
[ ] crm-dummy.js data is realistic (no test values unless intentional)
[ ] No commented-out debug code in shipped files
```

---

### 26.8 — Regression Protocol

When any shared file changes (`crm-shell.js`, `crm-dummy.js`, `crm-components.js`, `main.js`, `styles.css`), run regression on all previously built pages:

```
[ ] T1 Structure — sidebar renders on all built pages
[ ] T2 Data — all dynamic values still populate
[ ] T3 Visual — no layout breaks at 1440px
[ ] T4 Behaviour — nav active states correct on all pages
```

---

### 26.9 — QC Record Template

Copy this per page when QC begins:

```
QC Record: [page].html
Date started:
Builder:
Reviewer:

T1 Structure: [ ] PASS  [ ] FAIL  [ ] IN PROGRESS
T2 Data:      [ ] PASS  [ ] FAIL  [ ] IN PROGRESS
T3 Visual:    [ ] PASS  [ ] FAIL  [ ] IN PROGRESS
T4 Behaviour: [ ] PASS  [ ] FAIL  [ ] IN PROGRESS

Overall: [ ] DONE  [ ] IN PROGRESS  [ ] BLOCKED

Failures:
[log failures here using the fail protocol format in §26.6]

Sign-off:
```

---

## 27. Naming Conventions

Absorbed from: `SOP-BUILD.md §8`

Consistent naming across all 96+ pages prevents ID collisions and makes the JS predictable.

| Item | Convention | Example |
|---|---|---|
| HTML page | `[feature].html` | `leads.html`, `leads-detail.html` |
| Page JS driver | `crm-[feature].js` | `crm-leads.js`, `crm-followups.js` |
| Chart container IDs | `chart[PascalCase]` | `chartLeadAnalytics`, `chartRevenue` |
| KPI value IDs | `kpi-[metric]-value` | `kpi-contacts-value` |
| KPI badge IDs | `kpi-[metric]-badge` | `kpi-contacts-badge` |
| Table body IDs | `[feature]-table-body` | `leads-table-body`, `followupsTableBody` |
| List container IDs | `[feature]-list` | `dash-tasks-list` |
| DataTable search slot | `dt_[TableID]_Search` | `dt_contactsTable_Search` |
| CRM_PAGE constant | lowercase, hyphenated | `'leads-detail'`, `'followups'` |
| Modal IDs | `#[action][Entity]Modal` | `#addContactModal`, `#editLeadModal` |
| Filter dropdown IDs | `[prefix]-filter-[field]` | `fq-filter-owner`, `fq-filter-state` |
| KPI count IDs (custom pages) | `[prefix]-[metric]-count` | `fq-overdue-count`, `fq-pending-count` |

**Anti-patterns to avoid:**
- Never use sequential IDs (`id1`, `id2`) — always semantic names
- Never reuse an ID across pages for different purposes — IDs in crm-shell.js HTML are global to every page
- Never use camelCase for page filenames — always hyphenated (`leads-detail.html`, not `leadsDetail.html`)

---

## 28. Pakistan Market Constraints (L3)

Absorbed from: `SYSTEMATIC UI FRAMEWORK.md §L3 — Market Overlay`

These constraints override generic UX defaults for every Pakistan CRM page. Not guidelines — hard rules.

| Constraint | Rule | Bad example | Good example |
|---|---|---|---|
| Currency | PKR prefix always. Lakh/Crore notation ≥1L | `450,000` | `PKR 4.5L` |
| Phone format | +92 prefix, 11-digit display | `03001234567` | `0300-1234567` |
| Date in tables | DD/MM/YYYY | `2026-05-07` | `07/05/2026` |
| Date in feeds | Relative | `2026-05-07` | `2 days ago` |
| Channel priority | WhatsApp surfaced above email | Email button first | WhatsApp button first |
| Identity cues | Owner name + avatar on every assigned record | Owner ID only | `Ahmed Raza [avatar]` |
| Urdu copy | English placeholder only — hold for P-017 speaker review | Auto-translated Urdu | English with Urdu flag |
| RTL layout | Not required for V1 — do not add RTL hooks | `dir="rtl"` on body | English LTR only |
| Number grouping | Pakistani notation (2-2-3 grouping) | `1,000,000` | `10,00,000` |

**Buildable now (MR-004 / MR-005):**
- MR-004: Daily WhatsApp summary push — send PKR/lead summary at 9am and 6pm
- MR-005: Excel import/export — `.xlsx` with Pakistan field names and PKR columns

**Blocked (credentials needed):**
- MR-001/002: JazzCash and Easypaisa live integration — need merchant credentials (P-016)
- MR-003: SMS OTP — need Telenor/Jazz SMS gateway account

---

## 29. QC Worked Example — dashboard.html

Absorbed from: `SOP-QC.md §7 — Worked Example: Dashboard QC Audit (Batch 0)`

This is the retrospective QC pass for `dashboard.html`. Use it as a reference for how each tier is applied in practice.

### T1 — Structure: PASS
- CRM_PAGE = 'dashboard' set before crm-shell.js ✓
- Script load order correct ✓
- All referenced IDs exist in HTML ✓
- No console errors on load ✓
- Sidebar renders with correct active tab ✓

### T2 — Data: PASS (with fixes)
- All KPI cards populate from CRM_DUMMY ✓
- PKR formatting: `pkrShort()` removed; all values now use `C.pkr()` (Cr/L with PKR prefix) — **fix required**
- `funnel-total-value` was missing PKR prefix — **fix required**
- Task checkboxes priority-coloured: was conditional on status, changed to unconditional — **fix required**
- Revenue chart: was hardcoded 12-month array, now uses `CRM_DUMMY.invoiceSummaries.monthly_trend` — **fix required**
- chartFollowupRate: now derives from `CRM_DUMMY.followupTrend` (6-month summary added to crm-dummy.js) — **data added**
- chartLeadsByHour: now derives from `CRM_DUMMY.leadsByHour` (heatmap matrix added to crm-dummy.js) — **data added**

### T3 — Visual: PASS (with fixes)
- Column layout correct ✓
- Deals Overview: `grid.padding.bottom` increased 30→55 (data point at -20 was clipping pill) — **fix required**
- Task checkboxes: CSS `:checked`-only rule wrong; added unchecked `.check-*{border-color}` rules to styles.css — **fix required**

### T4 — Behaviour: PASS
- Dark mode toggle, chart tooltips, sidebar hover, View All links — all confirmed ✓

**Lessons for all future audits:**
- T2 exposed 6 data violations T3/T4 would never have caught — always run T2 exhaustively
- Expect new crm-dummy.js data fields to be added during T2 for each new custom page
- Any styles.css change during T3 requires re-running T1/T3 regression on all built pages

---

## §30 — UI Fidelity & NexLink Component Catalogue

# UI Fidelity Protocol — NexLink Template Full Extraction
**Version:** 2.0 — Complete  
**Date:** 2026-05-05  
**Source:** Direct HTML audit of all 18 seed screens (deals, sales, finance, activities, profile, customers, task-management, index, + sidebar/header)  
**Authority:** Every page built or rebuilt must pass all 15 fidelity gates before lock-in.

---

## Part 1 — KPI / Stat Card Variants (5 real patterns)

The template uses FIVE distinct stat card layouts. Use the right one per context.

### 1A — Deals/Leads Funnel KPI (avatar-left + 3-dot menu)
Source: `deals.html`
```html
<div class="card">
  <div class="card-header d-flex justify-content-between align-items-center border-0">
    <div class="d-flex align-items-center me-auto">
      <div class="avatar avatar-sm bg-primary-subtle text-primary rounded-circle me-2">
        <i class="fi fi-rr-handshake"></i>
      </div>
      <h6 class="mb-0">Total Deals</h6>
    </div>
    <div class="btn-group">
      <button class="btn btn-action-primary btn-sm btn-icon waves-effect dropdown-toggle"
              type="button" data-bs-toggle="dropdown">
        <i class="fi fi-bs-menu-dots"></i>
      </button>
      <ul class="dropdown-menu dropdown-menu-end">
        <li><a class="dropdown-item" href="#">Edit</a></li>
        <li><a class="dropdown-item" href="#">Delete</a></li>
      </ul>
    </div>
  </div>
  <div class="card-body">
    <h2 class="mb-1">1,240</h2>
    <div class="d-flex align-items-center">
      <span class="badge badge-sm bg-success-subtle text-success me-2">+18%</span>
      <span>from last week</span>
    </div>
  </div>
</div>
```

### 1B — Sales KPI (avatar-top + badge-right in body)
Source: `sales.html`
```html
<div class="card">
  <div class="card-header pb-0 border-0">
    <div class="avatar bg-primary-subtle text-primary rounded-circle">
      <i class="fi fi-rr-wallet"></i>
    </div>
  </div>
  <div class="card-body d-flex align-items-end">
    <div class="clearfix me-auto">
      <p class="mb-1">Total Earning</p>
      <h2 class="mb-0">$12,354</h2>
    </div>
    <span class="badge bg-success-subtle text-success">+12.4%</span>
  </div>
</div>
```

### 1C — Activities Dual-Stat KPI (avatar-right + today/week split + footer)
Source: `activities.html`
```html
<div class="card">
  <div class="card-header d-flex justify-content-between align-items-center border-0 pb-0">
    <div class="clearfix">
      <h6 class="card-title mb-1">New User Signups</h6>
      <small>Track daily user acquisition</small>
    </div>
    <div class="ms-auto">
      <div class="avatar bg-primary-subtle text-primary rounded-3">
        <i class="fi fi-rr-user"></i>
      </div>
    </div>
  </div>
  <div class="card-body">
    <div class="row">
      <div class="col-6">
        <span>Today</span>
        <h4 class="mb-0">128</h4>
      </div>
      <div class="col-6 text-end">
        <span>This Week</span>
        <h4 class="mb-0">840</h4>
      </div>
    </div>
  </div>
  <div class="card-footer d-flex justify-content-between align-items-center px-0 mx-3">
    <div class="d-flex align-items-center">
      <span class="badge bg-success-subtle text-success me-2">+12%</span>
      <span>from last week</span>
    </div>
    <small>Updated today</small>
  </div>
</div>
```
- Note: avatar uses `rounded-3` (square-ish), not `rounded-circle`
- Footer: `px-0 mx-3` gives inset padding matching card sides

### 1D — Finance Inline KPI (avatar inline, no header)
Source: `finance.html`
```html
<div class="card">
  <div class="card-body d-flex gap-3 align-items-center">
    <div class="avatar bg-success-subtle rounded-circle text-success">
      <i class="fi fi-rr-coins"></i>
    </div>
    <div class="clearfix">
      <span class="fw-semibold text-muted">Total Revenue</span>
      <h2 class="fw-bold mb-0 mt-1">$120,540</h2>
    </div>
  </div>
</div>
```
- No card-header at all — avatar and text side-by-side directly in card-body
- Label: `span fw-semibold text-muted`, value: `h2 fw-bold mb-0 mt-1`

### 1E — Colored Target Card (gradient bg + footer split stats)
Source: `finance.html`
```html
<div class="card overflow-hidden bg-primary ovarlay-primary-gradient border-0"
     style="background-image: url(assets/images/wind.gif); background-position: center; background-size: cover;">
  <div class="card-header pb-0 border-0 d-flex align-items-center justify-content-between z-1 position-relative">
    <h6 class="card-title mb-0 text-white">Monthly Target</h6>
    <div class="btn-group"><!-- 3-dot SVG menu --></div>
  </div>
  <div class="card-body pt-2 pb-0">
    <div class="d-flex gap-2 align-items-center">
      <h2 class="mb-0 text-white">92%</h2>
      <span class="text-white">+15% vs last month</span>
    </div>
    <div class="mb-5 z-n1 position-relative">
      <div id="monthlyStatusChart"></div>
      <div class="text-white mt-n5 text-center">673 Orders</div><!-- chart center label -->
    </div>
  </div>
  <div class="card-footer border-0 pt-3">
    <div class="bg-body py-3 px-3 rounded-3 d-flex">
      <div class="text-center w-50 py-2">
        <h4 class="mb-0">$75K</h4>
        <span class="text-primary text-2xs fw-semibold d-block">Target</span>
      </div>
      <div class="vr opacity-50"></div>
      <div class="text-center w-50 py-2">
        <h4 class="mb-0">$15k</h4>
        <span class="text-primary text-2xs fw-semibold d-block">Revenue</span>
      </div>
      <div class="vr opacity-50"></div>
      <div class="text-center w-50 py-2">
        <h4 class="mb-0">$8.5k</h4>
        <span class="text-primary text-2xs fw-semibold d-block">Today</span>
      </div>
    </div>
  </div>
</div>
```
- All text inside is `text-white`; footer gets `bg-body` panel with `vr opacity-50` dividers
- Chart label centered via `mt-n{n} text-center`

---

## Part 2 — Chart Cards

### 2A — Chart card with nav-pills-custom period toggle
Source: `deals.html`, `sales.html`
```html
<div class="card">
  <div class="card-header pb-0 border-0 d-flex flex-wrap gap-2 align-items-center justify-content-between">
    <h6 class="card-title mb-0">Sales Report</h6>
    <ul class="nav nav-pills nav-pills-custom nav-fill p-1 bg-light rounded-5" id="chartTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link rounded-5" data-bs-toggle="tab" type="button" role="tab">Today</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link rounded-5" data-bs-toggle="tab" type="button" role="tab">Week</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link active rounded-5" data-bs-toggle="tab" type="button" role="tab">Month</button>
      </li>
    </ul>
  </div>
  <div class="card-body pb-0">
    <div class="d-flex gap-5"><!-- optional inline stats above chart -->
      <div class="mb-2">
        <h2 class="mb-0">87,352</h2>
        Average Income <span class="badge badge-sm bg-success-subtle text-success ms-1">+12.4%</span>
      </div>
    </div>
    <div id="chartId" class="mx-n3"></div><!-- mx-n3 bleeds chart to card edges -->
  </div>
</div>
```
- Period tabs: `nav-pills-custom nav-fill p-1 bg-light rounded-5` — pill style, not tab style
- Chart div gets `mx-n3` to bleed edge-to-edge within card padding

### 2B — Chart card with selectpicker filter
Source: `finance.html`
```html
<div class="card-header border-0 d-flex pb-0 justify-content-between align-items-center">
  <h6 class="card-title mb-0">Revenue vs Expenses</h6>
  <select class="selectpicker" data-style="btn-sm btn-outline-light btn-shadow waves-effect">
    <option>This Year</option>
    <option>Last Year</option>
  </select>
</div>
<div class="card-body p-2">
  <div id="summeryChart"></div>
</div>
```

### 2C — Chart legend (fa square color indicators)
Source: `sales.html`, `finance.html`
```html
<div class="d-grid gap-1">
  <div class="d-flex gap-1 align-items-center py-1 mx-1">
    <i class="fa fa-square text-primary me-1"></i>
    Paid
    <strong class="text-dark fw-semibold ms-auto">75%</strong>
  </div>
  <div class="d-flex gap-1 align-items-center py-1 mx-1">
    <i class="fa fa-square text-primary text-opacity-75 me-1"></i>
    Cancelled
    <strong class="text-dark fw-semibold ms-auto">22%</strong>
  </div>
  <div class="d-flex gap-1 align-items-center py-1 mx-1">
    <i class="fa fa-square text-primary text-opacity-50 me-1"></i>
    Refunded
    <strong class="text-dark fw-semibold ms-auto">3%</strong>
  </div>
</div>
```
- Use `text-opacity-{10|25|50|75}` to vary the same color across legend items
- Value: `strong text-dark fw-semibold ms-auto`

### 2D — Donut/Radial chart with center label
Source: `finance.html`, `sales.html`
```html
<div class="maxw-175px ratio ratio-1x1 m-auto">
  <canvas id="expenseChart"></canvas>
</div>
<!-- OR for ApexCharts radial: -->
<div id="monthlyStatusChart"></div>
<div class="mt-n5 text-center">32,500 Sales</div><!-- negative margin pulls label into chart -->
```

---

## Part 3 — Table Card Pattern
Source: `deals.html`, `customers.html`, `finance.html`

```html
<div class="card overflow-hidden">
  <div class="card-header d-flex flex-wrap gap-3 align-items-center justify-content-between border-0 pb-0">
    <h6 class="card-title mb-0">Recent Deals</h6>
    <div id="dt_TableName_Search"></div><!-- DataTables injects search input here -->
  </div>
  <div class="card-body px-1 pt-2 pb-2">
    <table id="dt_TableName" class="table table-sm display table-row-rounded data-row-checkbox" style="width:100%">
      <thead class="table-light">
        <tr>
          <th class="minw-50px pe-0">
            <div class="form-check">
              <input class="form-check-input" data-row-checkbox type="checkbox">
            </div>
          </th>
          <th class="minw-150px">Client Name</th>
          <th class="minw-150px">Stage</th>
          <th class="minw-150px">Value</th>
          <th class="minw-150px">Assigned To</th>
          <th class="minw-150px">Closing Date</th>
          <th class="minw-150px">Status</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="pe-0">
            <div class="form-check p-0 w-auto d-inline-block">
              <input class="form-check-input m-0" data-checkbox type="checkbox">
            </div>
          </td>
          <td>John Miller</td>
          <td>Proposal Sent</td>
          <td>$45,000</td>
          <td>Emily Watson</td>
          <td>Dec 10, 2025</td>
          <td>
            <span class="badge badge-lg bg-primary-subtle text-primary">In Progress</span>
          </td>
          <td>
            <div class="btn-group float-end">
              <button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle"
                      data-bs-toggle="dropdown">
                <i class="fi fi-rr-menu-dots"></i>
              </button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="#">Edit</a></li>
                <li><a class="dropdown-item" href="#">Delete</a></li>
              </ul>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

**Column width classes:** `minw-50px` (checkbox), `minw-150px` (standard), `minw-200px` (name/long text)  
**Row checkbox:** `data-row-checkbox` on thead input; `data-checkbox` on tbody inputs  
**Action dropdown:** `btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle` + `float-end`  
**Status badge in table:** use `badge-lg` (not `badge-sm`)  
**Finance transactions table:** no `data-row-checkbox` — read-only tables omit the checkbox column

---

## Part 4 — Profile / Entity Detail Page
Source: `profile.html`

### 4A — Left sidebar card (col-lg-4)
```html
<div class="col-lg-4 col-sm-12">
  <div class="card">
    <div class="card-header pb-0 border-0">
      <!-- Avatar + name in header, separated by border-bottom -->
      <div class="mb-4 border-bottom pb-4 d-flex border-0 justify-content-between align-items-start">
        <div class="d-flex align-items-center">
          <div class="avatar avatar-xl rounded-circle position-relative me-3">
            <img src="..." alt="">
            <!-- edit overlay badge -->
            <a href="#" class="avatar avatar-xxs bg-primary rounded-circle text-white position-absolute top-0 mt-n1 me-n1 end-0">
              <i class="fi fi-rr-camera text-1xs"></i>
            </a>
          </div>
          <div class="clearfix">
            <h4 class="fw-bold mb-0">Name</h4>
            <small class="mb-0">Role / subtitle</small>
          </div>
        </div>
        <button class="btn btn-white btn-sm btn-shadow btn-icon waves-effect" type="button">
          <i class="fi fi-rr-pencil"></i>
        </button>
      </div>
    </div>
    <div class="card-body pt-0">

      <!-- Each section -->
      <div class="mb-4 border-bottom pb-4">
        <div class="mb-3">
          <h4 class="card-title mb-0">Basic Information</h4>
        </div>
        <div class="clearfix">
          <div class="mb-3">
            <span class="mb-1">Full Name</span>
            <p class="text-dark fw-semibold mb-0">Liam Anderson</p>
          </div>
          <div class="mb-3">
            <span class="mb-1">Phone</span>
            <p class="text-dark fw-semibold mb-0">+92 300 123 4567</p>
          </div>
        </div>
      </div>

      <!-- Social links section -->
      <div class="mb-4 border-bottom pb-4">
        <div class="mb-3">
          <h4 class="card-title mb-0">Contact Channels</h4>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <a href="#" class="btn btn-icon btn-sm btn-subtle-facebook waves-effect waves-light">
            <i class="fa-brands fa-facebook-f"></i>
          </a>
          <!-- btn-subtle-twitter, btn-subtle-instagram, btn-subtle-linkedin -->
        </div>
      </div>

      <!-- Progress/skills section (last — no border-bottom) -->
      <div class="mb-0">
        <div class="mb-3">
          <h4 class="card-title mb-0">Skill / Score</h4>
        </div>
        <div class="row align-items-center g-2 mb-3">
          <div class="col-sm-3">Label</div>
          <div class="col-sm-9">
            <div class="progress progress-sm">
              <div class="progress-bar" style="width: 85%"></div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</div>
```

**Field pattern:** `<span class="mb-1">Label</span>` then `<p class="text-dark fw-semibold mb-0">Value</p>`  
**Section separator:** `mb-4 border-bottom pb-4` on each section div  
**Section title:** `h4 card-title mb-0`  
**Edit button:** `btn btn-white btn-sm btn-shadow btn-icon waves-effect`

### 4B — Main content area (col-lg-8)
```html
<div class="col-lg-8 col-sm-12">
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">Account Settings</h4><!-- h4 in settings/form cards -->
    </div>
    <div class="card-body">
      <form>
        <div class="row mb-3">
          <div class="col-md-6">
            <label class="form-label">Full Name</label><!-- plain form-label, NOT fw-semibold -->
            <input type="text" class="form-control" value="...">
          </div>
          <div class="col-md-6">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" value="...">
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label">Bio</label>
          <textarea class="form-control" rows="5"></textarea>
        </div>
        <div class="text-end">
          <button type="submit" class="btn btn-success waves-effect waves-light">Save Changes</button>
        </div>
      </form>
    </div>
  </div>
</div>
```
- Save button: `btn btn-success` (not btn-primary) in profile/settings forms
- Form labels: plain `form-label` — no `fw-semibold small` (that was wrong in v1 protocol)

---

## Part 5 — Kanban / Task Board
Source: `task-management.html`

```html
<div class="row" id="taskWrapper">
  <!-- Column -->
  <div class="col-xxl-3 col-md-6">
    <div class="card bg-primary-subtle shadow-none h-auto">
      <div class="card-header p-3 d-flex align-items-center justify-content-between border-0 pb-0">
        <h6 class="card-title mb-0">New Task</h6>
        <div class="d-flex gap-2">
          <button type="button" class="btn btn-sm btn-icon btn-action-primary waves-effect">
            <i class="fi fi-rr-plus text-2xs"></i>
          </button>
          <div class="btn-group">
            <button class="btn btn-white btn-sm btn-shadow btn-icon waves-effect dropdown-toggle"
                    type="button" data-bs-toggle="dropdown">
              <i class="fi fi-rr-menu-dots"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li><a class="dropdown-item" href="#">Add</a></li>
              <li><a class="dropdown-item" href="#">Edit</a></li>
            </ul>
          </div>
        </div>
      </div>
      <!-- Cards container — Sortable.js target -->
      <div class="card-body p-3 d-grid gap-3" id="taskWrapper1">

        <!-- Individual task card -->
        <div class="card card-action cursor-move action-border-primary h-auto mb-0">
          <div class="card-header p-3 d-flex align-items-center justify-content-between border-0 pb-0">
            <h6 class="card-title mb-0">Hero Section Design</h6>
            <div class="d-flex">
              <button type="button" class="btn btn-sm btn-icon btn-action-primary waves-effect">
                <i class="fi fi-rr-pencil"></i>
              </button>
              <div class="btn-group">
                <button class="btn btn-sm btn-icon btn-action-gray waves-effect dropdown-toggle"
                        type="button" data-bs-toggle="dropdown">
                  <i class="fi fi-br-menu-dots-vertical"></i><!-- vertical dots -->
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li><a class="dropdown-item" href="#">Add</a></li>
                  <li><a class="dropdown-item" href="#">Edit</a></li>
                </ul>
              </div>
            </div>
          </div>
          <div class="card-body pt-2 p-3 text-1xs">
            <p>Task description text.</p>
            <!-- Date grid -->
            <div class="d-flex gap-2 mb-3">
              <div class="text-start w-50">
                <span>Start Date</span>
                <span class="text-dark d-block fw-semibold">14 Aug 2024</span>
              </div>
              <div class="text-start w-50">
                <span>End Date</span>
                <span class="text-dark d-block fw-semibold">20 Aug 2024</span>
              </div>
            </div>
            <!-- Animated progress -->
            <div class="progress progress-sm bg-primary-subtle mb-3">
              <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 15%"></div>
            </div>
            <!-- Footer: avatar group + status selector -->
            <div class="d-flex gap-2 justify-content-between">
              <div class="avatar-group">
                <div class="avatar avatar-xs rounded-circle border border-2 border-white">
                  <img src="assets/images/avatar/avatar1.webp" alt="">
                </div>
                <a href="#" class="avatar avatar-xs rounded-circle bg-primary-subtle text-primary border border-2 border-white">
                  <i class="fi fi-rr-plus text-2xs"></i><!-- add member -->
                </a>
              </div>
              <div class="dropdown select-status">
                <button class="btn btn-sm btn-subtle-primary dropdown-toggle waves-effect waves-light"
                        type="button" data-bs-toggle="dropdown">
                  Select Status
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li><a class="dropdown-item" href="#" data-class="btn-subtle-primary">New</a></li>
                  <li><a class="dropdown-item" href="#" data-class="btn-subtle-info">In Progress</a></li>
                  <li><a class="dropdown-item" href="#" data-class="btn-subtle-secondary">Pending</a></li>
                  <li><a class="dropdown-item" href="#" data-class="btn-subtle-success">Done</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <!-- /task card -->

      </div>
    </div>
  </div>
  <!-- /column -->
</div>
```

**Column card:** `card bg-{color}-subtle shadow-none h-auto`  
**Column header padding:** `p-3` (full, not `pb-0` only)  
**Add button:** `btn btn-sm btn-icon btn-action-primary waves-effect`  
**Column menu button:** `btn btn-white btn-sm btn-shadow btn-icon waves-effect dropdown-toggle`  
**Task card:** `card card-action cursor-move action-border-{color} h-auto mb-0`  
**Task menu icon:** `fi fi-br-menu-dots-vertical` (vertical, not horizontal)  
**Task body:** `card-body pt-2 p-3 text-1xs`  
**Progress:** `progress-sm bg-primary-subtle` + `progress-bar-striped progress-bar-animated`  
**Avatar group:** `avatar-group` class with `border border-2 border-white` on each avatar  
**Status button class changes** via `data-class` attribute on dropdown items

---

## Part 6 — Notification List / Activity Feed
Source: `deals.html` header, `activities.html`

```html
<!-- Container -->
<div class="p-2" style="height: 300px;" data-simplebar>
  <ul class="list-group list-group-hover list-group-smooth list-group-unlined">
    <li class="list-group-item d-flex justify-content-between align-items-center">
      <!-- Avatar with online status -->
      <div class="avatar avatar-xs avatar-status-success rounded-circle me-1">
        <img src="assets/images/avatar/avatar2.webp" alt="">
      </div>
      <!-- OR initials avatar -->
      <div class="avatar avatar-xs bg-success rounded-circle text-white">D</div>
      <!-- OR icon avatar -->
      <div class="avatar avatar-xs bg-dark rounded-circle text-white">
        <i class="fi fi-rr-lock"></i>
      </div>

      <div class="ms-2 me-auto">
        <h6 class="mb-0">Emma Smith</h6>
        <small class="text-body d-block">Need to update the details.</small>
        <small class="text-muted position-absolute end-0 top-0 mt-2 me-3">7 hr ago</small>
      </div>
    </li>
  </ul>
</div>
<!-- Footer -->
<div class="p-2">
  <a href="#" class="btn w-100 btn-primary waves-effect waves-light">View all</a>
</div>
```

**Time position:** `position-absolute end-0 top-0 mt-2 me-3` — floats to top-right of list item  
**Avatar status variants:** `avatar-status-success`, `avatar-status-danger`, `avatar-status-warning`  
**Always:** `list-group-hover list-group-smooth list-group-unlined` — never plain `list-group`

---

## Part 7 — Button Catalogue (sourced from template)

| Use case | Exact classes |
|---|---|
| Primary CTA | `btn btn-primary waves-effect waves-light` |
| Success save | `btn btn-success waves-effect waves-light` |
| Light/cancel | `btn btn-light waves-effect` |
| White icon (edit overlay) | `btn btn-white btn-sm btn-shadow btn-icon waves-effect` |
| Column menu | `btn btn-white btn-sm btn-shadow btn-icon waves-effect dropdown-toggle` |
| Header add | `btn btn-sm btn-icon btn-action-primary waves-effect` |
| Card 3-dot menu | `btn btn-action-primary btn-sm btn-icon waves-effect dropdown-toggle` |
| Table row action | `btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle` |
| Task menu (gray) | `btn btn-sm btn-icon btn-action-gray waves-effect dropdown-toggle` |
| Status pill | `btn btn-sm btn-subtle-{color} dropdown-toggle waves-effect waves-light` |
| Full-width footer | `btn w-100 btn-primary waves-effect waves-light` |
| Link-style | `btn-link` (anchor tag) |

---

## Part 8 — Badge Rules

```html
<!-- Standard (table status, general) -->
<span class="badge bg-primary-subtle text-primary">Active</span>

<!-- Large (prominent table status) -->
<span class="badge badge-lg bg-primary-subtle text-primary">In Progress</span>

<!-- Small (trend %, count indicators) -->
<span class="badge badge-sm bg-success-subtle text-success me-2">+18%</span>

<!-- Pill count (header, section counts) -->
<span class="badge badge-sm rounded-pill bg-primary ms-2">9</span>

<!-- Solid (high urgency) -->
<span class="badge bg-danger text-white">OVERDUE</span>

<!-- Menu badge (sidebar) -->
<span class="badge badge-sm text-bg-success">+12%</span>
```

---

## Part 9 — Avatar Rules

| Size | Class | Use |
|---|---|---|
| xxs | `avatar avatar-xxs` | Edit overlay, flags |
| xs | `avatar avatar-xs` | List items, table cells, kanban |
| sm | `avatar avatar-sm` | Header user, card headers |
| (default) | `avatar` | KPI card icons |
| xl | `avatar avatar-xl` | Profile page left sidebar |

**Shape variants:** `rounded-circle` (people), `rounded-3` (icons/activities), `rounded` (logos)  
**Status dot:** `avatar-status-success` / `avatar-status-danger` added to avatar div  
**Avatar group:** wrap in `<div class="avatar-group">`, each avatar gets `border border-2 border-white`  
**Initials:** 2 letters, no spaces — cycle through 6 colors by index % 6

---

## Part 10 — Page Header (Breadcrumb)
Source: all pages

```html
<div class="app-page-head d-flex align-items-center justify-content-between">
  <div class="clearfix">
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb mb-0">
        <li class="breadcrumb-item">
          <a href="app/dashboard.html"><i class="fi fi-rr-home"></i> Home</a>
        </li>
        <li class="breadcrumb-item active" aria-current="page">Page Name</li>
      </ol>
    </nav>
  </div>
  <!-- Right side: filters, action buttons -->
  <div class="d-flex gap-2 flex-wrap">
    <!-- toolbar -->
  </div>
</div>
```

- Breadcrumb is inside `clearfix` div — no `h5` page title below it (the template does NOT add one; v1 protocol was wrong)
- Task management variant wraps in `d-flex flex-wrap gap-3 align-items-center justify-content-between` with nav-pills-custom tab switcher below

---

## Part 11 — Modal Rules

```html
<div class="modal fade" id="modalId" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered {modal-sm|modal-lg}">
    <div class="modal-content">
      <div class="modal-header py-3">
        <h5 class="modal-title">Title</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form>
          <div class="row">
            <div class="col-12 mb-3">
              <input type="text" class="form-control" placeholder="...">
            </div>
            <div class="col-12 mb-3">
              <select class="form-select">...</select>
            </div>
            <div class="col-12 text-end">
              <button class="btn btn-light waves-effect waves-light me-2" data-bs-dismiss="modal">Close</button>
              <button class="btn btn-primary waves-effect waves-light">Confirm</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
```
- Always `modal-dialog-centered`
- Header: `py-3`
- Buttons inside body (not footer) in `col-12 text-end` — OR use `modal-footer`
- Close: `btn-light`, confirm: `btn-primary`

---

## Part 12 — Header Injection (crm-shell.js)

The full header must include:
```html
<div class="badge-standard d-none d-lg-inline-block">
  Today New Leads
  <span class="badge bg-primary-subtle text-primary" id="header-today-leads">0</span>
</div>
```
- `badge-standard` is a NexLink custom class for the header pill badge
- `form-control-fill` on the search input (not `form-control` alone)

Notification dropdown structure:
- Outer: `dropdown-menu dropdown-menu-lg-end p-0 w-300px mt-2`
- Header: `px-3 py-3 border-bottom d-flex justify-content-between`
- Body: `p-2` height `300px` data-simplebar
- Footer: `p-2` with `btn w-100 btn-primary`

---

## Part 13 — Progress Bar Rules

```html
<!-- Standard thin -->
<div class="progress progress-sm">
  <div class="progress-bar" style="width: 85%"></div>
</div>

<!-- Kanban animated -->
<div class="progress progress-sm bg-primary-subtle">
  <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 30%"></div>
</div>

<!-- Stacked (sales status) -->
<div class="progress-stacked bg-transparent mb-4">
  <div class="progress bg-transparent" style="width: 75%">
    <div class="progress-bar bg-primary"></div>
  </div>
  <div class="progress bg-transparent" style="width: 20%">
    <div class="progress-bar bg-primary bg-opacity-75"></div>
  </div>
</div>

<!-- Skills row (profile) -->
<div class="row align-items-center g-2 mb-3">
  <div class="col-sm-3">Label</div>
  <div class="col-sm-9">
    <div class="progress progress-sm">
      <div class="progress-bar" style="width: 92%"></div>
    </div>
  </div>
</div>
```

---

## Part 14 — Page Layout Grid Patterns

| Pattern | Columns |
|---|---|
| Dashboard KPI row (4 cards) | `col-xxl-3 col-md-6` |
| Dashboard KPI row (6 funnel) | `col-xxl-2 col-md-4` |
| Chart + feed | `col-xl-8` + `col-xl-4` |
| Finance KPI (4 cards) | `col-xxl-3 col-sm-6` |
| Finance main + sidebar | `col-xxl-9 col-xl-8` + `col-xxl-3 col-xl-4` |
| Profile / detail | `col-lg-4 col-sm-12` + `col-lg-8 col-sm-12` |
| Kanban (4 columns) | `col-xxl-3 col-md-6` |
| Full-width table | `col-xxl-12` or `col-lg-12` |
| Activities KPI (4 cards) | `col-xxl-3 col-md-6` |

---

## Part 15 — Seed Screen → CRM Page Direct Map

| Our page | Seed screen | Extract |
|---|---|---|
| `dashboard.html` | `index.html` + `sales.html` | 1A/1B KPI cards, nav-pills-custom chart toggle, list-group feed, notification pattern |
| `followups.html` | `customers.html` | Table card (3A), 1A KPI cards |
| `leads.html` | `customers.html` + `deals.html` | Table card, 1A funnel KPIs, selectpicker filter |
| `leads-detail.html` | `profile.html` | 4A sidebar card (field pattern, border-bottom sections), 4B form main, list-group feed |
| `opportunities.html` | `deals.html` | Table card, 1A KPI cards, nav-pills-custom chart |
| `cockpit.html` | `task-management.html` | Full kanban (Part 5), nav-pills-custom view switch |
| `contacts.html` | `customers.html` | Direct table card match |
| `contacts-detail.html` | `profile.html` | Direct profile match |
| `finance.html` | `finance.html` | 1D inline KPI, 1E colored card, 2B selectpicker, 2C legend, stacked progress |
| `activities.html` | `activities.html` | 1C dual-stat KPI, list-group feed |
| `tasks.html` | `task-management.html` | Full kanban |
| `settings.html` | `profile.html` (right col) | 4B form pattern |

---

## Part 16 — The 15 Fidelity Gates

Before any page is marked LOCKED:

| Gate | Check |
|---|---|
| F-01 | Correct KPI card variant used per page (1A/1B/1C/1D/1E) |
| F-02 | All tables: `table table-sm display table-row-rounded data-row-checkbox` |
| F-03 | All tables: checkbox col (`data-row-checkbox` / `data-checkbox`) + `btn-subtle-primary btn-shadow` action dropdown |
| F-04 | DataTables search: `<div id="dt_{Name}_Search">` placeholder in card-header |
| F-05 | All scrollable card bodies: `data-simplebar` + fixed height |
| F-06 | All list/feed: `list-group-hover list-group-smooth list-group-unlined` |
| F-07 | Every clickable element has `waves-effect` |
| F-08 | Chart cards use `nav-pills-custom nav-fill p-1 bg-light rounded-5` for period toggle |
| F-09 | Profile sidebar uses field pattern: `<span class="mb-1">Label</span>` + `<p class="text-dark fw-semibold mb-0">Value</p>` |
| F-10 | Profile sidebar sections separated by `mb-4 border-bottom pb-4` |
| F-11 | Avatar sizing correct per use (xs = list, sm = header/card, xl = profile) |
| F-12 | Kanban columns: `bg-{color}-subtle shadow-none h-auto`; task cards: `cursor-move action-border-{color} h-auto mb-0` |
| F-13 | All modals: `modal-dialog-centered`, header `py-3`, buttons `btn-light` + `btn-primary` |
| F-14 | Colored/gradient card: `ovarlay-primary-gradient`, footer uses `bg-body rounded-3 d-flex` with `vr opacity-50` dividers |
| F-15 | No console errors; RTL toggle works; no broken asset paths |

---

## §31 — Frontend Build Protocol

# Frontend Build Protocol

**Version:** 1.0  
**Applies to:** All pages in `D:\CRM\frontend\src\app\`  
**Must be read before touching any HTML file.**

---

## 1. Non-Negotiable Rules

1. **No page is locked without passing the review gate** (Section 9).
2. **No hardcoded data in HTML** — all numbers, names, and dynamic content rendered by JS from `crm-dummy.js`.
3. **No inline `<script>` blocks in page body** — all JS in `src/assets/js/app/`.
4. **No inline `style="..."` on elements** — use Bootstrap utility classes or SCSS.
5. **No left/right in CSS** — use Bootstrap `start`/`end` logical property utilities only (RTL compliance).
6. **Every page must render without errors** in both LTR and RTL mode before review.
7. **`docs/reports/session/PROGRESS.md` updated immediately** after each page is locked — never batch updates.
8. **No page is built outside the `src/app/` directory** — original template files are read-only references.

---

## 2. Directory Structure

```
src/
  app/                         ← ALL our app pages live here
    login.html
    register.html
    forgot-password.html
    reset-password.html
    dashboard.html
    leads.html
    leads-detail.html
    followups.html
    opportunities.html
    cockpit.html
    contacts.html
    contacts-detail.html
    finance.html
    activities.html
    tasks.html
    calendar.html
    inbox-whatsapp.html
    inbox-email.html
    analytics-sales.html
    marketing.html
    admin-users.html
    admin-audit.html
    settings.html
    quotes.html
    quotes-new.html
    orders.html
    ai.html

  assets/
    js/
      app/                     ← ALL our custom JS lives here
        crm-dummy.js           ← all dummy data (single source of truth)
        crm-api.js             ← API wrapper (dummy mode + real mode toggle)
        crm-components.js      ← shared HTML rendering functions
        crm-auth.js            ← auth page logic
        crm-dashboard.js       ← dashboard page logic
        crm-leads.js           ← leads queue + detail logic
        crm-followups.js       ← follow-up queue logic
        crm-opportunities.js   ← opportunities list + kanban logic
        crm-contacts.js        ← contacts list + detail logic
        crm-finance.js         ← finance page logic
        crm-activities.js      ← activities + tasks + calendar logic
        crm-inbox.js           ← email + WhatsApp inbox logic
        crm-admin.js           ← admin pages logic
```

**Original template files** (`src/index.html`, `src/leads.html`, etc.) — never edit, read-only references.

---

## 3. HTML Shell Rules

### 3.1 Base Tag
Every page in `src/app/` MUST have this as the first tag inside `<head>`:
```html
<base href="../">
```
This resolves all asset paths (`assets/css/`, `assets/libs/`, `assets/images/`) relative to `src/`, not `src/app/`. Do not omit. Do not change the path.

### 3.2 Title Format
```html
<title>Pakistan CRM — {Page Name}</title>
```

### 3.3 Stylesheet Block (exact order, do not reorder)
```html
<!-- Required vendor CSS -->
<link rel="stylesheet" href="assets/libs/flaticon/css/all/all.css">
<link rel="stylesheet" href="assets/libs/lucide/lucide.css">
<link rel="stylesheet" href="assets/libs/fontawesome/css/all.min.css">
<link rel="stylesheet" href="assets/libs/simplebar/simplebar.css">
<link rel="stylesheet" href="assets/libs/node-waves/waves.css">
<link rel="stylesheet" href="assets/libs/bootstrap-select/css/bootstrap-select.min.css">
<!-- Page-specific vendor CSS (add only what the page uses) -->
<!-- e.g. <link rel="stylesheet" href="assets/libs/datatables/datatables.min.css"> -->
<!-- e.g. <link rel="stylesheet" href="assets/libs/flatpickr/flatpickr.min.css"> -->
<!-- Main stylesheet — MUST carry id="main-stylesheet" for RTL switcher -->
<link id="main-stylesheet" rel="stylesheet" href="assets/css/styles.css">
<!-- CRM custom overrides — MANDATORY on every app page, always last -->
<link rel="stylesheet" href="assets/css/crm-custom.css">
```

### 3.4 Script Block (exact order, always at end of `<body>`)
```html
<!-- Required vendor JS — always last 3 lines of body -->
<script src="assets/libs/global/global.min.js"></script>
<script src="assets/js/appSettings.js"></script>
<script src="assets/js/main.js"></script>
<!-- Page-specific vendor JS (add only what the page uses) -->
<!-- e.g. <script src="assets/libs/datatables/datatables.min.js"></script> -->
<!-- App JS — after all vendor JS -->
<script src="assets/js/app/crm-dummy.js"></script>
<script src="assets/js/app/crm-api.js"></script>
<script src="assets/js/app/crm-components.js"></script>
<script src="assets/js/app/crm-{module}.js"></script>
<!-- RTL locale switcher — always last -->
<script src="assets/js/app/crm-locale.js"></script>
```

### 3.5 Template to Use as Reference per Page Type

| Page type | Reference template | Copy section |
|---|---|---|
| Auth (login/register/password) | `src/authentication/login-basic.html` | Full file, change content card only |
| DataTable list page | `src/leads.html` | Full file, change table section only |
| Detail / profile page | `src/customers.html` | Full file, change content panels only |
| Dashboard | `src/index.html` | Full file, change widget/chart sections only |
| BUILD page (no template) | `src/leads.html` | Copy shell + nav, replace body content completely |

---

## 4. Navigation Wiring

### 4.1 Active State
Every page must set the sidebar active state in its page JS:
```javascript
// At top of crm-{module}.js
document.addEventListener('DOMContentLoaded', () => {
  // Activate the correct sidebar tab
  const tab = document.querySelector('[href="#dashboardTab"]'); // change per page
  if (tab) tab.classList.add('active');
});
```

### 4.2 Sidebar Tab → Page Group Mapping
| Sidebar tab ID | Pages |
|---|---|
| `#dashboardTab` | dashboard.html |
| `#appsTab` | leads.html, followups.html, contacts.html, opportunities.html, cockpit.html |
| `#pagesTab` | finance.html, analytics-sales.html, marketing.html |
| `#authenticationTab` | login.html, register.html, forgot-password.html, reset-password.html |

### 4.3 Breadcrumb Pattern
```html
<div class="page-header-left">
  <h5 class="page-title">Page Title</h5>
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb mb-0">
      <li class="breadcrumb-item"><a href="dashboard.html">Home</a></li>
      <li class="breadcrumb-item active">Page Title</li>
    </ol>
  </nav>
</div>
```

---

## 5. Dummy Data Standard

### 5.1 Location
All dummy data lives in one file: `src/assets/js/app/crm-dummy.js`.  
No other file may define dummy data. No HTML may contain hardcoded data values.

### 5.2 Format
Every dummy dataset MUST exactly mirror the API response envelope:
```javascript
// Correct
window.CRM_DUMMY = {
  leads: {
    data: [ /* lead objects */ ],
    meta: { count: 20, total: 847, limit: 25, offset: 0 }
  }
};

// Wrong — missing envelope
window.CRM_DUMMY = {
  leads: [ /* lead objects */ ]
};
```

### 5.3 Field Constraints
- Phone numbers: `+92` prefix, E.164 format (`+923001234567`)
- Currency: `PKR` — format as `PKR 1,20,000` (Pakistani lakh notation)
- Dates: ISO 8601 UTC (`2026-05-04T10:30:00Z`)
- Names: Mix of Pakistani names (Urdu romanised) and English names
- Cities: Karachi, Lahore, Islamabad, Rawalpindi, Peshawar, Quetta, Faisalabad, Multan

### 5.4 Minimum Records per Entity
| Entity | Minimum dummy records |
|---|---|
| leads | 20 (spread across all 7 stages) |
| followups | 15 (mix of pending/overdue/completed) |
| contacts | 15 |
| opportunities | 12 (spread across all stages) |
| activities | 20 (last 30 days) |
| tasks | 12 |
| users (owners) | 5 |

### 5.5 Overdue Enforcement Data
Follow-up dummy data MUST include at minimum:
- 3 `overdue` records with `escalation_level: "strict"`
- 3 `overdue` records with `escalation_level: "medium"`
- 4 `pending` records
- 2 `completed` records

This ensures the enforcement posture strip renders in a non-trivial state on every review.

---

## 6. API Wiring Pattern

### 6.1 Mode Toggle
```javascript
// In crm-api.js
window.CRM_CONFIG = {
  DUMMY_MODE: true,             // flip to false when backend is live
  BASE_URL: 'http://localhost:3000/api/v1',
  get token() { return localStorage.getItem('crm_token'); }
};
```

### 6.2 Function Signature (all API functions follow this pattern)
```javascript
async function apiLeads(params = {}) {
  if (window.CRM_CONFIG.DUMMY_MODE) {
    return window.CRM_DUMMY.leads;
  }
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`${window.CRM_CONFIG.BASE_URL}/leads?${qs}`, {
    headers: { 'Authorization': `Bearer ${window.CRM_CONFIG.token}` }
  });
  return res.json();
}
```

### 6.3 Error Display
All API errors render into a shared `#crm-error-toast` element (defined in crm-components.js). No `alert()` calls.

---

## 7. Component Rendering Rules

### 7.1 Shared Components (defined in `crm-components.js`)
| Function | Returns | Used on |
|---|---|---|
| `renderStageBadge(stage)` | HTML string | Lead rows, detail header |
| `renderPriorityBadge(priority)` | HTML string | Lead rows, task rows |
| `renderFollowupBadge(state, escalation)` | HTML string | Lead rows, followup rows, detail page |
| `renderEnforcementStrip(overdueCount, unassignedCount)` | HTML string | All dashboards |
| `renderPaymentBadge(status)` | HTML string | Finance, order detail |
| `renderPKR(amount)` | string | All monetary fields |
| `renderRelativeTime(isoDate)` | string | Activity feed, created_at columns |
| `renderAuditRow(event)` | HTML string | Audit log (read-only, no edit icons) |

### 7.2 DataTable Initialisation Pattern
```javascript
// Standard DataTable init for all list pages
function initTable(tableId, columns, data) {
  $(`#${tableId}`).DataTable({
    data: data,
    columns: columns,
    pageLength: 25,
    responsive: true,
    dom: '<"row"<"col-sm-6"l><"col-sm-6"f>>t<"row"<"col-sm-6"i><"col-sm-6"p>>',
    language: { search: '', searchPlaceholder: 'Search...' }
  });
}
```

---

## 8. RTL Compliance Checklist (per page)

- [ ] `<link id="main-stylesheet">` has the `id` attribute set
- [ ] No `left` / `right` in any inline style or page-specific SCSS
- [ ] All flex/grid alignment uses `start`/`end` not `left`/`right`
- [ ] RTL switcher script loads last in body scripts
- [ ] Manually test: open page, run `localStorage.setItem('crm_locale','ur')` in console, reload — layout should flip

---

## 9. Review Gate (must pass before page is locked)

A page is **not locked** until all of the following pass:

| # | Gate | How to verify |
|---|---|---|
| G-01 | Page renders with dummy data — no blank/empty widgets | Open in browser via `npm run dev` |
| G-02 | Page renders in empty state — zero records handled gracefully | Set dummy dataset to `data: []`, reload |
| G-03 | All KPI numbers are live from dummy data (not HTML text nodes) | Change a value in `crm-dummy.js`, reload — number must update |
| G-04 | No console errors | DevTools Console tab — zero errors |
| G-05 | Responsive at 1280px and 768px viewport | DevTools Device toolbar |
| G-06 | RTL renders correctly | Run RTL test (Section 8 checklist) |
| G-07 | Blocked surfaces hidden | P-016 items must show "Coming soon" badge, no real pay buttons |
| G-08 | Navigation active state set | Correct sidebar item highlighted |
| G-09 | Breadcrumb correct | Correct page title in breadcrumb |
| G-10 | `docs/reports/session/PROGRESS.md` entry written | Check file after locking |

---

## 10. Lock-In Definition

A page is **locked** when:
1. All 10 review gates pass
2. `docs/reports/session/PROGRESS.md` has an entry with: page name, route, status (LOCKED), date, and any deviations noted
3. The mapping file (`FRONTEND-BACKEND-MAPPING.md`) status column for that page updated from `DIRECT/EXTEND/BUILD` to `LOCKED`

---

## 11. Phase Lock Definition

A phase is **locked** when all pages in that phase are individually locked.  
Only after phase lock does build begin on the next phase.

---

## 12. Deviation Handling

If a page requires a deviation from this protocol (e.g., a vendor lib conflict, a template layout incompatibility):
1. Document the deviation in the page's `<!-- DEV-NOTE: ... -->` HTML comment at top of body
2. Record the deviation in `docs/reports/session/PROGRESS.md` under the page entry
3. Do not silently diverge — every deviation is visible and traceable

---

## 13. Blocked Surfaces Reference

Never render these without explicit unblock:

| Surface | Blocked by | What to render instead |
|---|---|---|
| JazzCash / Easypaisa pay button | P-016 | `<span class="badge bg-secondary">Payment integration pending</span>` |
| Easypaisa webhook status | P-016 | Same badge |
| Urdu UI strings | P-017 | English placeholder + `<!-- UR_TODO: urdu string here -->` comment |
| Facebook/Instagram lead form | MR-001 | Hidden div with `data-unblock="MR-001"` attribute |
| Voice note transcription | MR-003 | Microphone icon with `disabled` attribute |

---

## 14. File Checklist Before Committing a Page

```
[ ] src/app/<page>.html created in correct directory
[ ] <base href="../"> present as first head tag
[ ] <link id="main-stylesheet"> has id attribute
[ ] No inline scripts in body
[ ] No hardcoded data values in HTML
[ ] Page-specific JS file created in src/assets/js/app/
[ ] crm-dummy.js has data for this page
[ ] crm-api.js has API function(s) for this page
[ ] All review gates (G-01 to G-10) checked
[ ] PROGRESS.md updated
[ ] FRONTEND-BACKEND-MAPPING.md status updated to LOCKED
```

---

## §32 — Seed Archetype Normalisation Protocol

# Seed-to-Archetype Normalisation Protocol
## Version 1.0 — Pakistan CRM OS / NexLink v1.3.0

**Purpose:** A deterministic formula for building any CRM archetype page as a pixel-for-pixel replica of its NexLink seed screen. Follow every rule below in sequence. No judgment calls, no approximations, no "close enough." Any deviation from this protocol is the cause of back-and-forth iteration.

---

## Phase 0 — Mandatory Seed Audit (BEFORE touching any code)

Read these three files in this exact order before writing a single character:

| Step | File to read | What you extract |
|---|---|---|
| 0-A | `src/[seed-page].html` | Full HTML — grid, card patterns, class chains, IDs, text labels, badge classes, script tags |
| 0-B | `src/assets/js/dashboard/[page].js` or `src/assets/js/[scope]/[page].js` | Every chart config verbatim — type, height, width, colors, fill, plotOptions, series data, axis options |
| 0-C | `src/assets/js/chart/apexchart.js` and `src/assets/js/chart/chartjs.js` | Any shared chart plugin code or config patterns used across pages |

**Do not start Phase 1 if any of these files have not been fully read.**

Seed page-to-JS file mapping:

| Our page | Seed HTML | Seed JS |
|---|---|---|
| dashboard.html | index.html | assets/js/dashboard/dashboard.js |
| leads.html | customers.html + leads.html | assets/js/dashboard/leads.js |
| followups.html | activities.html | assets/js/dashboard/activities.js |
| leads-detail.html | profile.html | assets/js/dashboard/management.js |
| opportunities.html | deals.html | assets/js/dashboard/deals.js |
| finance.html | finance.html | assets/js/dashboard/finance.js |
| contacts.html | user-management.html | assets/js/dashboard/user-management.js |
| analytics.html | analytics.html | assets/js/dashboard/analytics.js |
| sales-cockpit.html | sales.html | assets/js/dashboard/sales.js |
| review.html | review.html | assets/js/dashboard/review.js |

---

## Phase 1 — Script Dependency Audit

**Rule:** Before writing page JS, grep the seed HTML for ALL `<script src="assets/libs/...">` tags. Add every one of them to our page's script block in the same load order.

Correct load order for all pages:
```html
<script>window.CRM_PAGE = 'page-name';</script>
<script src="assets/js/app/crm-dummy.js"></script>
<script src="assets/js/app/crm-api.js"></script>
<script src="assets/js/app/crm-components.js"></script>
<script src="assets/js/app/crm-shell.js"></script>
<script src="assets/libs/global/global.min.js"></script>
<script src="assets/js/appSettings.js"></script>
<script src="assets/js/main.js"></script>
<!-- Add seed-required libs here in seed order -->
<script src="assets/libs/chartjs/chart.js"></script>         <!-- only if seed uses Chart.js canvas -->
<script src="assets/libs/apexcharts/apexcharts.min.js"></script>
<script src="assets/libs/datatables/datatables.min.js"></script>
<script src="assets/libs/flatpickr/flatpickr.min.js"></script>
<script src="assets/libs/simplebar/simplebar.min.js"></script>
<!-- etc. -->
<script src="assets/js/app/crm-[page].js"></script>
<script src="assets/js/app/crm-locale.js"></script>
```

**Flag:** If the seed page uses a lib we have not added, stop and add it before continuing.

---

## Phase 2 — Navigation & Sidebar Icons

**Root cause of icon size mismatch:** The seed navbar uses inline 24×24 SVG icons. Flaticon `<i class="fi fi-rr-*">` tags render at a different size and appearance.

**Rule 2-A: Sidebar nav icons must be inline SVG, 24×24.**
Copy the exact SVG path data from `src/index.html` lines 358–470 for each nav item. Never substitute flaticon `<i>` classes.

**Rule 2-B: SVG color must use CSS var.**
All SVG strokes must use `stroke="var(--bs-heading-color)"`. Active state is controlled by the `.active` class on `.menu-link`, not by changing the SVG color inline.

**Rule 2-C: Nav item tooltip pattern.**
```html
<li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="[Label]">
  <a class="menu-link [active]" href="...">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="...">
      <!-- exact seed SVG path here -->
    </svg>
  </a>
</li>
```

**Rule 2-D: Sidebar panel menu items (expanded panel).**
Menu items inside panels use flaticon `fi` classes because they appear as text+icon list items, not pure icon buttons. The size class is `scale-1x` for these only:
```html
<i class="fi fi-rr-[icon] scale-1x"></i> Label
```

**crm-shell.js sidebar nav items must be updated** to replace all `<i class="fi fi-rr-*">` with the correct 24×24 SVG from the seed before any new page is reviewed.

---

## Phase 3 — Chart Fidelity Rules

This is the most critical phase. Follow every sub-rule without exception.

### Rule 3-A: Chart type is non-negotiable

Extract the exact `chart.type` from the seed JS file. Never substitute a different chart type regardless of perceived visual similarity.

| If seed says | Build exactly |
|---|---|
| `type: 'bar'` | bar — vertical bars |
| `type: 'bar'` + `horizontal: true` + `stacked: true` + `stackType: '100%'` | horizontal stacked 100% bar |
| `type: 'bar'` + `stacked: true` (no stackType) | stacked grouped bar |
| `type: 'area'` | area with fill |
| `type: 'line'` | line, no fill |
| `type: 'radialBar'` | radialBar — never donut |
| `type: 'heatmap'` | heatmap — never bar sparkline |
| `type: 'doughnut'` (Chart.js) | Chart.js canvas element — never ApexCharts div |
| Chart.js `new Chart(ctx, ...)` | requires `<canvas id="...">` not `<div id="...">` |

### Rule 3-B: Dimensions must be exact

Copy `height`, `width`, `columnWidth`, `barHeight`, `borderRadius`, `cutout`, `startAngle`, `endAngle` verbatim from the seed JS. No rounding, no approximation.

### Rule 3-C: Colors must use CSS variables

In ApexCharts: always `var(--bs-primary)`, `var(--bs-info)`, `rgba(var(--bs-primary-rgb), 0.X)`.
In Chart.js canvas context: hex is required because CSS vars don't resolve in canvas — use `#5955D1`, `#ACAAE8`, `#DEDDF6` as extracted from seed.

Never use hardcoded hex in ApexCharts config. This breaks dark mode and theme switching.

### Rule 3-D: Fill type must match exactly

| Seed fill | Our fill |
|---|---|
| `type: 'gradient', gradientToColors: ['var(--bs-info)']` | gradient primary→info |
| `type: 'solid', colors: ['rgba(var(--bs-primary-rgb), 0.1)']` | solid, NOT gradient |
| `fill: { opacity: 1, colors: ['rgba(var(--bs-primary-rgb), 0.X)'] }` per-series | array of opacity fills |
| `fill: { colors: ['var(--bs-white)'] }` (radialBar) | white fill |

### Rule 3-E: Series data — the visual proportion rule

Charts exist to communicate proportions, not exact CRM values. The seed's static data arrays establish the visual proportions (bar heights, area curves, heatmap intensities) that define the screen's visual character.

**Rule:** Use seed's static data as the visual baseline. CRM-computed values populate KPI text labels only — not chart series arrays — **unless** the chart's purpose is explicitly to show a live CRM metric (e.g., pipeline status radialBar, lead sources stacked bar).

Specific cases:
- `chartRevenue` bar chart → use seed data `[120,350,450,120,200,180,300,120,250,350,250,180]` as the month series; actual PKR totals appear in the KPI text element only
- `chartLeadAnalytics` area → use seed data `[80,95,75,90,75,90]` as static growth index; actual lead count appears in KPI h2 only
- `chartDealsOverview` area → use seed data `[95,95,70,70,95,95,55,55,85,85]` as static growth curve
- `chartFollowupRate` stacked bar → use seed data arrays; actual completion rate appears in KPI h2 only
- `chartLeadsByHour` heatmap → use seed data arrays (activity pattern, not computed from CRM)
- **Exception:** `chartLeadSources` stacked bar uses computed `srcC.*` values because the chart IS the source breakdown metric
- **Exception:** `chartPipelineStatus` radialBar uses computed `wonPct` because the chart IS the win rate metric
- **Exception:** `chartTasksOverview` doughnut uses computed `tasksPend/tasksInPr/tasksDone` because the chart IS the task breakdown

### Rule 3-F: Grid and axis options — copy verbatim

Grid `borderColor`, `strokeDashArray`, `padding` values; yaxis `min`, `max`, `tickAmount`; xaxis `categories`; label `fontSize`, `fontFamily` — all must be copied exactly from the seed JS. These micro-settings control the chart's visual density and spacing.

### Rule 3-G: Tooltip, legend, dataLabels — copy verbatim

`dataLabels: { enabled: false }` means no labels. `legend: { show: false }` means hidden. `legend: { position: 'bottom' }` means bottom. Do not add or remove these settings from the seed's config.

---

## Phase 4 — KPI Card Fidelity Rules

### Rule 4-A: Read the seed's exact KPI text patterns

Before writing any KPI element, read the seed HTML and extract:
- The exact badge class chain: `badge badge-sm bg-X-subtle text-X`
- The exact footer text label (static label + computed value pattern)
- Whether the badge text is static (`+2.57%`) or computed

### Rule 4-B: Static vs computed badge values

If the seed shows a static value like `+2.57%` on a badge, it means the badge is a visual indicator, not a live metric. Options:
- Wire it to a real month-over-month computation from dummy data
- Keep it as a visually representative static value

Never leave it empty or as `—`. An empty badge breaks the layout proportions.

### Rule 4-C: Footer elements must all be present

Every KPI card footer in the seed has: a static label, a dynamic value, and a directional arrow/link. All three must be present. Missing elements collapse the card to a different height than the seed.

### Rule 4-D: Sparkline positioning

Cards with sparklines in the footer use:
```html
<div class="card-footer border-0 p-0">
  <div id="chartXxx" class="my-n3 mx-n1"></div>  <!-- negative margins pull chart flush -->
  <div class="position-absolute bottom-0 ...">Text</div>
</div>
```
The `my-n3 mx-n1` and `position-absolute bottom-0` pattern creates the flush-edge sparkline effect. Never use a normal card-body div for sparkline containers.

---

## Phase 5 — CSS Class Chain Preservation

### Rule 5-A: Copy every class, in order

The seed's class chains are not decorative — each class activates specific CSS. A missing class breaks spacing, shadows, borders, or animations.

Non-negotiable class chains to copy verbatim:

| Element | Exact class chain |
|---|---|
| 3-dot menu button | `btn btn-action-primary btn-sm btn-icon waves-effect dropdown-toggle` |
| KPI card wrapper | `card` (plain — no `card-action`, no `action-border-*`) |
| KPI card header | `card-header d-flex align-items-center justify-content-between border-0 pb-0` |
| Chart sparkline container | `mb-n4 mt-n3` (inside card-body, negative margins flush chart to edges) |
| Area sparkline footer | `card-footer border-0 p-0` + inner div `my-n3 mx-n1` |
| Revenue chart container | `div id="chartRevenue" class="revenue-chart"` |
| Retention/Follow-up Rate chart | `div id="chart" class="retention-chart mt-n1"` |
| Traffic/Lead Sources chart | `div id="chart" class="chart-rounded my-1"` |
| Gradient card outer | `card overflow-hidden bg-primary border-0 ovarlay-primary-gradient` (note: typo "ovarlay" is intentional — it's the template's own CSS class) |
| Gradient card header | `z-1 position-relative` (z-index above the background gif) |
| Gradient card body | `pt-0 border-light border-bottom border-opacity-10` |
| Gradient card radial div | `mb-5 mt-n3 z-n1 position-relative` |
| Gradient card legend icon | `fa-solid fa-square` (FontAwesome solid, not outline) |
| Stacked progress bar | `progress-stacked bg-transparent` > `progress bg-transparent` > `progress-bar bg-white [bg-opacity-50] [bg-opacity-25]` |
| Upcoming/meeting list item | `p-3 bg-light bg-opacity-50 mb-2 rounded` |
| Deals Overview chart wrapper | `card-footer border-0 p-0` + `my-n3 mx-n1` |
| Deals floating badge | `position-absolute bottom-0 px-3 py-2 rounded-5 shadow-sm translate-middle start-50` |
| Lead Funnel progress bars | `progress progress-[color] progress-overlap mb-1` > `progress-label` + `progress-value` + `progress-bar` |
| DataTable card | `card overflow-hidden` |
| DataTable body | `card-body px-1 pt-2 pb-2` |
| Table classes | `table table-sm display table-row-rounded data-row-checkbox` |
| Table action button | `btn btn-subtle-primary btn-sm btn-shadow btn-icon waves-effect dropdown-toggle` |
| Stage/status badge | `badge badge-lg bg-X-subtle text-X` (note: `badge-lg` not `badge-sm`) |
| Period toggle | `nav nav-pills nav-pills-custom nav-fill p-1 bg-light rounded-5` |
| Legend indicator | `fa fa-square text-primary text-opacity-{10|25|50|75}` (opacity suffix matches the corresponding fill opacity) |
| Upcoming scrollable | `card-body gradient-layer` style `height: 325px` + `data-simplebar` |

### Rule 5-B: Preserve background images on gradient card

```html
<div class="card overflow-hidden bg-primary border-0 ovarlay-primary-gradient"
     style="background-image: url(assets/images/wind.gif); background-position: center; background-size: cover;">
```
The animated gif creates the gradient card's visual texture. Never remove it.

### Rule 5-C: Breadcrumb must be wrapped in clearfix

```html
<div class="app-page-head d-flex align-items-center justify-content-between">
  <div class="clearfix">  <!-- ← required wrapper -->
    <nav aria-label="breadcrumb">
      <ol class="breadcrumb mb-0">...</ol>
    </nav>
  </div>
</div>
```

---

## Phase 6 — Data Binding ID Convention

### Rule 6-A: IDs are the only thing that changes

When adapting a seed card to CRM data, only these things change:
- The `id="..."` attribute on dynamic elements
- The text labels (card title, legend labels, axis labels)
- The data binding in JS (which CRM API call populates which element)

Everything else — class chains, chart configs (with Rule 3-E exceptions), HTML structure, nesting depth — stays identical to the seed.

### Rule 6-B: Revenue tab button IDs must match exactly

The seed revenue chart tab buttons use IDs `todayRevenueTab`, `weekRevenueTab`, `monthRevenueTab`. Our page must use these exact IDs so the event listener pattern matches the seed.

---

## Phase 7 — Pre-Commit Visual Verification Gate

**Do not mark any page DONE until all checks pass.**

Open both URLs in adjacent browser tabs and step through this checklist:
- Our page: `http://localhost:3001/app/[page].html`
- Seed page: `http://localhost:3001/[seed].html`

### Structural checks
- [ ] Grid column widths match (col-xxl-X, col-lg-X values identical)
- [ ] Number of cards matches
- [ ] Card height/proportion matches for each card
- [ ] Card header layout (title left, 3-dot right) matches

### Navigation checks
- [ ] Sidebar icon size matches (24×24 SVG, not smaller flaticon)
- [ ] Active nav item highlight matches
- [ ] Header bar (logo, search, avatar) matches

### Chart checks (one per chart)
- [ ] Chart TYPE matches (bar vs area vs radialBar vs heatmap etc.)
- [ ] Chart HEIGHT matches
- [ ] Chart FILL style matches (solid vs gradient vs opacity array)
- [ ] Chart COLOR matches (primary vs info)
- [ ] Seed's visual bar/area PROPORTIONS match (reference Rule 3-E)
- [ ] Chart legend/indicators match (position, icon style, opacity)
- [ ] Chart axes visible/hidden matches

### KPI checks
- [ ] All badge classes match (badge-sm vs badge-lg, color classes)
- [ ] All footer text labels present and formatted correctly
- [ ] All static text (labels, section headers) match the seed character-for-character

### Table checks
- [ ] Column count matches
- [ ] Checkbox column present
- [ ] Row action button style matches
- [ ] Badge size in rows matches

### Color/indicator checks
- [ ] Legend indicator icons use `fa fa-square text-primary text-opacity-{10|25|50|75}` 
- [ ] Legend opacity progression matches the chart fill opacity array order

---

## Quick Reference — Known Deviations to Never Repeat

These are mistakes made during dashboard normalization. They are permanent reminders.

| Mistake | Correct rule |
|---|---|
| Used `<div>` for chartTasksOverview | Chart.js requires `<canvas>` — always check chart engine before choosing element type |
| Used area chart for chartRevenue | Always read seed JS before writing chart code — revenue is a bar chart |
| Used donut for chartLeadSources | Seed uses horizontal stacked bar 100% — chart type is sacred |
| Used line chart for chartFollowupRate | Seed uses stacked bar — chart type is sacred |
| Used donut for chartPipelineStatus | Seed uses radialBar semi-circle — chart type is sacred |
| Used bar sparkline for chartLeadsByHour | Seed uses heatmap — chart type is sacred |
| Used donut for chartPipelineStatus | Seed uses radialBar — chart type is sacred |
| Used hardcoded `#5955D1` in ApexCharts | Use `var(--bs-primary)` — breaks theming |
| Used `rgba(89,85,209,0.1)` in ApexCharts | Use `rgba(var(--bs-primary-rgb), 0.1)` — breaks theming |
| Used `<i class="fi fi-rr-*">` for sidebar nav items | Seed uses 24×24 SVG inline — flaticon renders smaller |
| Computed CRM data for revenue bar chart series | Use seed's static proportional data — computed data produces wrong visual ratios |
| Added gradient fill to chartLeadAnalytics | Seed uses solid fill `rgba(primary-rgb, 0.1)` — gradient is wrong |
| Used dual-series for revenue chart | Seed is single-series bar — never add series not in seed |
| Forgot Chart.js script tag | Always audit seed HTML script tags (Phase 1) before building |

---

## Application Checklist — Per New Page

Copy this to the top of every new build task:

```
[ ] 0-A Seed HTML fully read
[ ] 0-B Seed page JS fully read
[ ] 0-C Plugin JS files noted
[ ] Phase 1: Script tags audited, all libs present
[ ] Phase 2: All sidebar SVG icons are 24×24 inline SVG
[ ] Phase 3: All chart types extracted from seed JS, not assumed
[ ] Phase 3: All chart dims copied verbatim (height, width, columnWidth, etc.)
[ ] Phase 3: All chart fill types copied verbatim
[ ] Phase 3: Static data used for visual charts; computed data for metric charts only
[ ] Phase 4: All KPI badge classes match seed
[ ] Phase 4: All KPI footer elements present (no empty slots)
[ ] Phase 5: All class chains copied verbatim
[ ] Phase 6: Only IDs and text labels changed from seed
[ ] Phase 7: Visual diff gate passed — all checkboxes ticked
```

---

*Last updated: 2026-05-06 — authored from dashboard normalization session. Extend with new patterns as each screen is normalised.*
