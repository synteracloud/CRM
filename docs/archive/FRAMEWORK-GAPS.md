> **RETIRED** — Gaps documented here have been resolved and incorporated into FRAMEWORK.md. This is a historical record only.
> Content preserved for historical reference. Do not update this document.
> Retired: 2026-06-21 (Documentation Normalization Phase)

# Framework Gaps Register

## Purpose

This file records every gap, ambiguity, and missing rule discovered during page normalisation — from the first page to the current build. It is the primary mechanism for driving the system toward zero drift and 100% seed alignment. The workflow is:

1. **Discover** — a gap is found while building or verifying a page
2. **Log here** — add an entry with full context while it is fresh
3. **Resolve** — implement the fix (code change, framework section addition, or documented exception)
4. **Normalise** — mark resolved and record exactly what was added/changed

This file is updated after every page normalisation session. Closed entries are never deleted — they are the permanent record of how the system improved.

---

## Status Key

| Status | Meaning |
|--------|---------|
| `OPEN` | Gap identified, not yet resolved |
| `IN PROGRESS` | Resolution being implemented |
| `RESOLVED` | Fix implemented and normalised |

---

## Open Gaps Summary

| Gap ID | Description | Discovered on | Status |
|--------|-------------|--------------|--------|
| GAP-002 | Sidebar hrefs point to seed paths for unbuilt pages | dashboard.html | RESOLVED — 2026-05-15 (all 96 library pages complete) |
| GAP-005 | Sidebar icon tab active state hardcoded to dashboardTab | dashboard.html | RESOLVED — 2026-05-12 |
| GAP-006 | marketing.html seed source unconfirmed | §17 review | RESOLVED — 2026-05-12 |
| GAP-026 | DataTables with avatar img columns need autoWidth:false | review.html | RESOLVED — 2026-05-12 |
| GAP-027 | `<link id="main-stylesheet">` missing — appSettings.js cannot apply theme, causing chart/DT width drift | activities.html | RESOLVED — 2026-05-12 |
| GAP-007 | crm-dummy.js hard dependency not explicit in FRAMEWORK §4 | crm-shell.js review | RESOLVED |
| GAP-008 | Seed opportunityTrendChart Y-axis formatter is a seed bug | leads.html | OPEN (preserved verbatim) |
| GAP-014 | §19 and §22 conflict on lib inclusion rule | leads.html | RESOLVED |
| GAP-016 | App page filenames must match seed filenames exactly | customers.html | RESOLVED |
| GAP-017 | HTML rows compressed to single-line format causing attribute loss | customers.html | RESOLVED |
| GAP-018 | Seed profile.html references non-existent `assets/js/dashboard.js` | profile.html | OPEN (seed bug) |
| GAP-019 | Seed deals.js `fill.gradient` duplicate key — second overwrites first | deals.html | OPEN (seed bug, preserved verbatim) |
| GAP-020 | crm-shell notifications replaced with Pakistan CRM custom items instead of seed items | crm-shell sign-off | RESOLVED |
| GAP-021 | crm-shell user dropdown missing 3 menu items + wrong labels | crm-shell sign-off | RESOLVED |
| GAP-022 | crm-shell header nav hrefs wrong for app/ subdirectory (email, calendar, user dropdown) | crm-shell sign-off | RESOLVED |
| GAP-023 | crm-shell calendar SVG missing 4 day dots + extra locale toggle + wrong aria-label | crm-shell sign-off | RESOLVED |
| GAP-024 | crm-shell logo img src and href wrong for app/ subdirectory (missing ../ prefix) | sales.html review | RESOLVED |
| GAP-025 | sales.html built without `<base href="../">` — all asset paths used explicit ../ instead | sales.html review | RESOLVED |

---

## Gap Entries

---

### GAP-001 — Sidebar `a()` helper was dead code

**Discovered during:** dashboard.html normalisation (2026-05-10)
**Status:** RESOLVED — 2026-05-10

**Description:**
`crm-shell.js` defined `function a(pages)` to return `' active'` when `window.CRM_PAGE` matched a page key. The function was never called — all sidebar `<a class="menu-link">` items used static class strings. Active sidebar highlighting never worked on any page.

**Root cause:**
Template literals in `SIDEBAR_HTML` used plain `class="menu-link"` instead of `class="menu-link${a(['key'])}"`.

**Resolution:**
Applied `${a(['key'])}` to all 16 sidebar links across Dashboard and Apps tabs. Updated dashboard link href from `index.html` to `app/dashboard.html`.

**Normalised into FRAMEWORK.md:**
§4 CRM_PAGE values table confirmed; §18 CRM_PAGE Key Registry added.

---

### GAP-002 — Sidebar hrefs still point to seed files for unbuilt pages

**Discovered during:** dashboard.html normalisation (2026-05-10)
**Status:** RESOLVED — 2026-05-15 (all 96 NexLink library pages complete; all sidebar hrefs updated)

**Note for custom design phase:** New Pakistan CRM custom pages (DESIGN-SPEC.md) may introduce additional sidebar entries. Apply the same rule: never add a sidebar href until the target custom page is built AND browser-verified.

**Description:**
`crm-shell.js` sidebar links for all unbuilt pages still point to seed-relative paths (e.g. `customers.html`, `deals.html`). Clicking them loads the raw seed template with no header or sidebar.

**Impact:**
Navigation to any unbuilt page from the sidebar bypasses the framework entirely.

**Rule:**
Never update a sidebar href until the target page is built AND browser-verified. A broken link is worse than a seed link.

**Resolved so far (all library pages):**
- `href="app/dashboard.html"` — 2026-05-10
- `href="app/leads.html"` — 2026-05-11 (via GAP-003)
- `href="app/followups.html"` — 2026-05-11 (via GAP-004)
- `href="app/customers.html"` — 2026-05-11
- `href="app/deals.html"` — 2026-05-11
- `href="app/sales.html"` — 2026-05-12
- `href="app/finance.html"` — 2026-05-12
- `href="app/team-management.html"` — 2026-05-12
- `href="app/employee.html"` — 2026-05-12
- `href="app/review.html"` — 2026-05-12
- `href="app/task-management.html"` — 2026-05-12
- `href="app/user-management.html"` — 2026-05-12
- `href="app/activities.html"` — 2026-05-12 (session 4)
- `href="app/calendar.html"` — 2026-05-12 (session 4)
- `href="app/chat.html"` — 2026-05-12 (session 4)

**Remaining (unbuilt pages — do not update until verified):**
`email/inbox.html`, `email/compose.html`, `email/read-email.html`, auth pages, settings.html, marketing.html.

---

### GAP-003 — No `leads` link in the sidebar at all

**Discovered during:** FRAMEWORK.md §17 review (2026-05-10)
**Status:** RESOLVED — 2026-05-11

**Description:**
The seed sidebar (and therefore `crm-shell.js`) had no leads link. The seed menu goes: Default Dashboard → Sales → Finance → Team → Employees → Customers → Review → Tasks → User Management → Activities → Deals. No Leads entry.

**Resolution:**
Added immediately after Default Dashboard: `<a class="menu-link${a(['leads'])}" href="app/leads.html">` with icon `fi fi-rr-funnel`.

**Normalised into FRAMEWORK.md:**
§20 Sidebar Link Update Protocol table updated.

---

### GAP-004 — No `followups` link in the sidebar at all

**Discovered during:** FRAMEWORK.md §17 review (2026-05-10)
**Status:** RESOLVED — 2026-05-11

**Description:**
Same as GAP-003 but for Follow-ups. No follow-up queue entry in the seed sidebar.

**Resolution:**
Added immediately after Leads: `<a class="menu-link${a(['followups'])}" href="app/followups.html">` with icon `fi fi-rr-clock-three`.

---

### GAP-005 — Sidebar icon tab active state is hardcoded to Dashboard panel

**Discovered during:** FRAMEWORK.md §4 review (2026-05-10)
**Status:** RESOLVED — 2026-05-12 *(see full entry below)*

---

### GAP-006 — `app/marketing.html` seed source unconfirmed

**Discovered during:** FRAMEWORK.md §17 review (2026-05-10)
**Status:** RESOLVED — 2026-05-12 *(see full entry below)*

---

### GAP-007 — `crm-dummy.js` dependency behaviour not documented in FRAMEWORK §4

**Discovered during:** crm-shell.js review (2026-05-10)
**Status:** RESOLVED — 2026-05-12

**Description:**
`crm-shell.js` reads `window.CRM_DUMMY` to populate the header avatar/name and todayLeads badge. The load order in §3 enforces the correct sequence (crm-dummy.js at position 2, crm-shell.js at position 5) but §4 did not describe what actually happens when the dependency is absent.

**Source of truth — crm-shell.js:**
- Line 310: `const user = (window.CRM_DUMMY && window.CRM_DUMMY.users.data[0]) || { display_name: 'Ahmed Raza', ... }` — header has an explicit fallback, so it still renders if crm-dummy.js is absent.
- Line 522: `if (window.CRM_DUMMY) { todayBadge.textContent = ... }` — badge is guarded, stays at HTML default if absent.
This is a **soft dependency with partial degradation**, not a hard failure.

**Resolution:**
Added note to FRAMEWORK.md §4 citing exact line numbers, describing fallback behaviour accurately. Never characterised as a "hard dependency" — that was incorrect per the code.

---

### GAP-008 — Seed `opportunityTrendChart` Y-axis formatter is a seed bug

**Discovered during:** leads.html normalisation (2026-05-11)
**Status:** OPEN — preserved verbatim by design

**Description:**
`dashboard.js` formatter: `"$" + (value / 100) + "M"`. With `min: 700000`, this renders `$7000M` instead of the intended `$0.70M`. The correct formula would be `(value / 1000000).toFixed(2) + "M"`.

**Impact:**
Y-axis labels on both `src/leads.html` (seed) and `app/leads.html` (CRM) show wrong values. Both pages are wrong in the same way — they match each other.

**Rule:**
Do not fix during the verbatim normalisation phase. Fix only when the post-normalisation CRM customisation phase begins for leads.html, and record it here as resolved at that point.

---

### GAP-009 — `crm-dashboard.js` was Pakistan-specific, not seed-identical

**Discovered during:** Pre-normalisation audit (2026-05-10)
**Status:** RESOLVED — 2026-05-10

**Description:**
The original `crm-dashboard.js` contained Pakistan CRM business logic — `CRM_DUMMY` calls for dynamic KPI population, `CRM_API` calls, custom Pakistani chart data. None of this matched the seed `dashboard.js` configs. The dashboard page was functionally a custom build, not a seed replica.

**Root cause:**
The file was written before the seed-first normalisation protocol was established. It was treating the dashboard as a CRM feature page rather than a visual replica.

**Resolution:**
Complete rewrite of `crm-dashboard.js` (778 lines → 1227 lines). All chart configs extracted verbatim from `src/assets/js/dashboard/dashboard.js`. Todolist interactivity merged from `src/assets/js/plugins/todolist.js`. All Pakistan-specific data removed from the driver.

**Normalised into FRAMEWORK.md:**
§8 Seed-First Normalisation Protocol; §9 Page Driver Pattern.

---

### GAP-010 — Chart configs invented from memory instead of read from seed JS

**Discovered during:** leads.html visual verification (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
When writing `crm-leads.js`, the `opportunityTrendChart` config was written from scratch rather than extracted from `dashboard.js`. This produced wrong chart type (solid line instead of dashed), wrong data series, wrong Y-axis bounds, wrong fill opacity — every visual property was different from the seed.

**Root cause:**
No rule existed requiring the seed JS file to be read before writing a page driver. The seed `leads.html` script block loads `dashboard.js`, which contains the exact `opportunityTrendChartConfig` — but `dashboard.js` was never opened.

**Impact:**
The opportunity trend chart on `app/leads.html` looked completely different from `src/leads.html`.

**Resolution:**
- Read `dashboard.js` in full (1133 lines)
- Extracted all 13 element configs verbatim
- Added FRAMEWORK.md §24 (Seed JS Element Catalogue) as the permanent lookup
- Added hard rule to §22: "Never write a chart config from memory — check §24 first, then read seed JS"
- Pre-build checklist added as §0

---

### GAP-011 — `dt_ScrollVertical` incorrectly initialised as a DataTable

**Discovered during:** leads.html visual verification (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
`crm-leads.js` initialised `#dt_ScrollVertical` as a DataTable with `pageLength:6`. The seed's `dashboard.js` has no `dt_ScrollVertical` config at all — the table renders as a plain HTML table with all 10 rows visible in source order.

**Root cause:**
Assumed all elements with a `dt_` prefix needed DataTable initialisation. Did not read `dashboard.js` to confirm.

**Impact:**
- Table rows reordered alphabetically by DataTable's default sort (column 0)
- Only 6 rows shown with pagination instead of all 10
- Visual mismatch on both row order and row count

**Resolution:**
Removed DataTable init for `dt_ScrollVertical`. Added entry to §24 explicitly marked "NOT INITIALISED — plain HTML table."

---

### GAP-012 — `dt_NewCustomers` missing `select:false` and `columnDefs` from seed config

**Discovered during:** leads.html visual verification (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
`crm-leads.js` DataTable init for `#dt_NewCustomers` was missing two properties present in the seed `dashboard.js` config: `select: false` and `columnDefs: [{ targets: [0], orderable: false }]`.

**Root cause:**
Partial copy of the config pattern from memory — did not read the seed JS verbatim.

**Impact:**
Column 0 (Lead Name) was sortable in our page; seed makes it non-sortable. Clicking the column header changed row order unexpectedly.

**Resolution:**
Added `select: false` and `columnDefs: [{ targets: [0], orderable: false }]` to match seed exactly.

---

### GAP-013 — Footer missing from all built pages

**Discovered during:** followups.html visual verification (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
Every seed page (`src/index.html`, `src/leads.html`, `src/activities.html`, etc.) contains a `<footer class="footer-wrapper bg-body">` element inside `.page-layout` after `</main>`. All three built pages (`app/dashboard.html`, `app/leads.html`, `app/followups.html`) were missing this footer entirely.

**Root cause:**
Two compounding failures:
1. FRAMEWORK.md §2 page template skeleton omitted the footer — it went directly from `</main>` to `</div>` closing `.page-layout`.
2. `crm-shell.js` only calls `insertAdjacentHTML('beforebegin', ...)` — it injects header and sidebar **before** `<main>` and never touches anything after `</main>`. No automatic injection of footer exists.

Since the template was wrong and no injection covered it, every page built from the template was structurally short by one footer element.

**Impact:**
Page height shorter than seed on all three built pages. Visible when comparing side by side.

**Resolution:**
- Added footer to `app/dashboard.html`, `app/leads.html`, `app/followups.html`
- Added footer to FRAMEWORK.md §2 page template skeleton (permanent fix for all future pages)
- Footer Home link set to `href="app/dashboard.html"` per §21 inter-page linking rules

---

### GAP-014 — §19 and §22 conflict on lib inclusion rule

**Discovered during:** leads.html normalisation (2026-05-11)
**Status:** RESOLVED — 2026-05-12

**Description:**
FRAMEWORK.md §19 stated "Include only the libs a page actually uses" but then added "if the seed loads a lib, the app page needs it too" — contradicting the first sentence within the same section. §22 said "Translate each seed lib script 1:1" which amplified the contradiction.

**Root cause:**
The conflict was inside §19 itself, not just between §19 and §22. The seed's script block is sometimes a template carry-over (e.g. `src/leads.html` loads `flatpickr.min.js` but has no date picker inputs).

**Resolution:**
- §19 rewritten: seed script block is a starting point, not an authority. **HTML elements are the definitive test.** If the element type is absent from the page HTML, exclude the lib regardless of what the seed loads.
- §22 updated: use seed script block as a reference, cross-check against §19, §19 wins on conflict.
- Single source of truth: the page's own HTML elements.

---

### GAP-015 — No pre-build checklist enforced before writing page files

**Discovered during:** Pattern review after leads.html errors (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
No formal starting ritual existed. Each page build started directly from memory or partial reference to the framework. This caused GAP-010, GAP-011, GAP-012, and GAP-013 — all of which were preventable if seed files had been fully read first.

**Root cause:**
FRAMEWORK.md described what to do but not when and in what order. The build process had no enforced entry point.

**Resolution:**
Added FRAMEWORK.md §0 (Pre-Build Checklist) — a 10-step mandatory starting ritual. Steps cover: seed identification, main content extraction, element ID inventory, seed JS reading, §24 cross-check, lib detection, footer confirmation, and tracking file updates. Added rule: "If you skip any step and something is wrong, the cause will always trace back to a skipped step."

---

## Normalisation Log

| Gap ID | Resolved in session | What changed |
|--------|--------------------|-|
| GAP-001 | 2026-05-10 | `crm-shell.js` — `a()` applied to all sidebar links; FRAMEWORK.md §4, §18 updated |
| GAP-003 | 2026-05-11 | `crm-shell.js` — Leads link added to dashboardTab; FRAMEWORK.md §20 updated |
| GAP-004 | 2026-05-11 | `crm-shell.js` — Follow-ups link added to dashboardTab; FRAMEWORK.md §20 updated |
| GAP-009 | 2026-05-10 | `crm-dashboard.js` — full rewrite to seed-identical; FRAMEWORK.md §8, §9 added |
| GAP-010 | 2026-05-11 | `crm-leads.js` — opportunityTrendChart replaced with verbatim seed config; FRAMEWORK.md §22 hard rule + §24 catalogue added |
| GAP-011 | 2026-05-11 | `crm-leads.js` — dt_ScrollVertical DataTable init removed; §24 updated with NOT INITIALISED note |
| GAP-012 | 2026-05-11 | `crm-leads.js` — dt_NewCustomers select:false + columnDefs added to match seed |
| GAP-013 | 2026-05-11 | Footer added to dashboard.html, leads.html, followups.html; FRAMEWORK.md §2 template updated |
| GAP-015 | 2026-05-11 | FRAMEWORK.md §0 Pre-Build Checklist added (10 steps) |
| GAP-002 (customers) | 2026-05-11 | `crm-shell.js` — `href="customers.html"` updated to `href="app/customers.html"` |
| GAP-017 | 2026-05-11 | `customers.html` — `aria-expanded="false"` restored on all dropdowns; trailing spaces restored; `&` restored in header; FRAMEWORK.md §8 verbatim rule tightened |

---

### GAP-018 — Seed `profile.html` references non-existent `assets/js/dashboard.js`

**Discovered during:** profile.html normalisation (2026-05-11)
**Status:** OPEN — seed bug, not actionable

**Description:**
`src/profile.html` script block loads `<script src="assets/js/dashboard.js">`. This file does not exist. The real shared JS is at `assets/js/dashboard/dashboard.js` (with a subdirectory). The seed has a broken path.

**Impact:**
In the seed, loading `profile.html` produces a 404 on `dashboard.js`. Since the page has no element IDs requiring JS initialisation, this has no visible effect — the page works fine without it.

**Resolution in our page:**
The broken script reference is not included in `app/profile.html`. The page has zero JS-initialised elements so no page-specific lib scripts are loaded at all. `crm-profile.js` is a no-op stub included for framework consistency only.
| GAP-016 | 2026-05-11 | `contacts.html` renamed to `customers.html`; `crm-contacts.js` → `crm-customers.js`; CRM_PAGE `contacts` → `customers`; FRAMEWORK.md §17/§18/§20 updated; naming rule added to §17 |
| GAP-007 | 2026-05-12 | FRAMEWORK.md §4 updated with accurate soft-dependency note citing crm-shell.js lines 310 and 522 |
| GAP-014 | 2026-05-12 | FRAMEWORK.md §19 and §22 rewritten — HTML elements are authoritative, seed script block is a reference only, §19 wins all conflicts |
| GAP-024 | 2026-05-12 | crm-shell.js logo img src → `../assets/images/logo.svg`; both brand hrefs → `../index.html`; safe for base-href and non-base-href pages |
| GAP-025 | 2026-05-12 | sales.html — added `<base href="../">`, removed `../` from all asset/script paths, breadcrumb + footer hrefs fixed to `app/dashboard.html` |
| GAP-002 (team/employee/review/task/user) | 2026-05-12 | `crm-shell.js` — 5 more hrefs updated: `app/team-management.html`, `app/employee.html`, `app/review.html`, `app/task-management.html`, `app/user-management.html` |
| GAP-026 | 2026-05-12 | autoWidth:false rule added for DataTables with avatar img columns; applied to dt_RecentReviews; §24 updated for dt_Activities, dt_RecentReviews |
| GAP-005 | 2026-05-12 | crm-shell.js DOMContentLoaded — added appsTab activation for pages: chat, calendar, inbox, compose, read-email |
| GAP-002 (activities/calendar/chat) | 2026-05-12 | `crm-shell.js` — 3 more hrefs updated: `app/activities.html`, `app/calendar.html`, `app/chat.html` |
| GAP-006 | 2026-05-12 | marketing.html seeded from `src/marketing.html` — confirmed correct seed; `src/assets/js/dashboard/marketing.js` is the page driver source |
| GAP-027 | 2026-05-12 | Added `id="main-stylesheet"` to styles.css link in activities, settings, marketing, calendar, chat — all 5 batch-2 pages were missing it; FRAMEWORK.md §head template already has it at line 112 |

---

### GAP-016 — App page filenames must match seed filenames exactly

**Discovered during:** customers.html build (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
FRAMEWORK.md §17 mapped `src/customers.html` to `app/contacts.html` — using the CRM entity name ("contacts") instead of the seed filename ("customers"). This caused a visible mismatch: the URL showed `contacts.html`, the sidebar said "Customers", the breadcrumb said "Customers", and the seed was `customers.html`. No reason justified the deviation.

**Root cause:**
§17 was written with CRM data-model naming in mind rather than the rule of matching the seed filename. No rule existed requiring filenames to match.

**Impact:**
URL mismatch vs seed. CRM_PAGE key was `'contacts'` but sidebar and breadcrumb said "Customers". Confusion about which name is authoritative.

**Resolution:**
- Renamed `app/contacts.html` → `app/customers.html`
- Renamed `crm-contacts.js` → `crm-customers.js`
- CRM_PAGE changed from `'contacts'` to `'customers'`
- `crm-shell.js` `a(['contacts'])` → `a(['customers'])`, href updated
- FRAMEWORK.md §17, §18, §20 updated

**Rule added to FRAMEWORK.md §17:**
*App page filename must match the seed filename exactly. CRM_PAGE key must also match the filename stem. No semantic renaming — if the seed is `customers.html`, the app page is `app/customers.html` and CRM_PAGE is `'customers'`.*

---

### GAP-019 — Seed `deals.js` duplicate `fill.gradient` key silently drops first value

**Discovered during:** deals.html normalisation (2026-05-11)
**Status:** OPEN — seed bug, preserved verbatim

**Description:**
`deals.js` `dealsValueTrendChartConfig.fill` defines two gradient objects using the same `gradient` key. JavaScript silently overwrites the first with the second, so Income and Expenses lines share the same gradient instead of having separate ones. This is a bug in the seed template.

**Impact:**
Both chart series use the secondary-color gradient at render time. The Income series' primary-color gradient is discarded. Both seed and our page show the same incorrect behaviour — no visual divergence, but a latent quality issue.

**Resolution:**
Preserved verbatim per §8 (seed bugs must be replicated exactly). Logged for future remediation when seed template is upgraded.

---

### GAP-020 — crm-shell HEADER_HTML notification items replaced with Pakistan CRM content

**Discovered during:** nav bar sign-off review post deals.html (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
The `HEADER_HTML` notification dropdown contained 3 Pakistan CRM-specific items (Overdue Follow-up/Ali Khan, New Lead/Sara Ahmed, Deal Closed/Kamran Ltd) with letter-initial avatars. The seed has 7 items with real avatar images and Western-context content (Emma Smith, Design Team, Security Update, Invoice #1432, etc.). The badge count was dynamic `3` via `id="header-notif-count"` vs seed's static `9`.

**Root cause:**
Shell was written with CRM localisation in mind before the seed-first normalisation rule was established. The notification items and badge were invented as CRM content rather than copied from seed.

**Impact:**
Every page using crm-shell.js showed wrong notification content and count. Opening the notifications dropdown revealed immediate visual mismatch vs seed.

**Resolution:**
- Replaced 3 CRM items with exact 7 seed items (verbatim content, timestamps, avatar classes)
- Avatar image paths prefixed with `../assets/` to be correct from `app/` subdirectory
- Badge changed from dynamic `id="header-notif-count">3` to static seed value `9`

---

### GAP-021 — crm-shell user dropdown missing 3 menu items + wrong labels

**Discovered during:** nav bar sign-off review post deals.html (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
Shell user dropdown had only 2 items (Settings, Sign Out) and 1 divider. Seed has 5 items (View Profile, My Task, Account Settings, Upgrade Plan, Log Out) and 2 dividers. Missing items: View Profile (`fi-rr-user`), My Task (`fi-rr-note`), Upgrade Plan (`fi-rr-usd-circle`). Existing items had wrong labels: "Settings" → "Account Settings", "Sign Out" → "Log Out".

**Root cause:**
Shell user dropdown was written as a minimal CRM dropdown rather than a seed replica. No §0 pre-build checklist audit was applied to the shell.

**Impact:**
Every page showed a truncated user menu missing 3 items. Labels did not match seed.

**Resolution:**
- Added View Profile (`href="profile.html"`), My Task (`href="../task-management.html"`), Upgrade Plan (`href="../pages/pricing.html"`)
- Fixed labels: "Settings" → "Account Settings", "Sign Out" → "Log Out"
- Fixed logout href to `../authentication/login-basic.html`
- Added second divider before Log Out per seed structure
- Fixed avatar img path to `../assets/images/avatar/avatar1.webp`

---

### GAP-022 — crm-shell header nav button hrefs wrong for app/ subdirectory

**Discovered during:** nav bar sign-off review post deals.html (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
Shell is injected into pages living in `src/app/`. All hrefs must be relative from `app/`, meaning seed root paths need a `../` prefix for sibling directories. Multiple hrefs were wrong:

| Element | Was | Should be |
|---------|-----|-----------|
| Email button | `app/inbox-email.html` | `../email/inbox.html` |
| Calendar button | `app/calendar.html` | `../calendar.html` |
| Settings item | `app/settings.html` | `settings.html` (in app/) |
| Log Out item | `app/login.html` | `../authentication/login-basic.html` |

The email button also used the wrong filename (`inbox-email.html` vs seed's `inbox.html`).

**Root cause:**
Shell was written from the app/ subfolder perspective for some hrefs but not others. Email had wrong filename from memory. No href path audit was performed against seed.

**Resolution:**
All hrefs fixed as shown in table above.

**Rule to add to FRAMEWORK.md:**
Shell hrefs for pages outside `app/` must use `../` prefix. Pages inside `app/` use the bare filename. Never invent filenames — use seed filename exactly.

---

### GAP-024 — crm-shell logo img src and href unresolvable from app/ subdirectory

**Discovered during:** sales.html browser review (2026-05-12)
**Status:** RESOLVED — 2026-05-12

**Description:**
`crm-shell.js` used `src="assets/images/logo.svg"` and `href="index.html"` for the logo. Pages using `<base href="../">` resolve these correctly (base makes `assets/...` resolve from `src/`). Pages without base href (sales.html was built without it) resolve from `app/` — `assets/images/logo.svg` → `app/assets/images/logo.svg` which does not exist. Logo did not display and logo link was broken.

**Resolution:**
Changed crm-shell.js to `src="../assets/images/logo.svg"` and `href="../index.html"` for both brand elements. This is safe for both base-href pages (going above root is a no-op) and non-base-href pages.

---

### GAP-025 — sales.html built without `<base href="../">` — inconsistent with all other pages

**Discovered during:** sales.html browser review (2026-05-12)
**Status:** RESOLVED — 2026-05-12

**Description:**
Pages 1–6 (dashboard, leads, followups, customers, profile, deals) all use `<base href="../">` and bare `assets/...` paths. sales.html (page 7) was built without `<base href="../">` and used explicit `../assets/...` throughout head, body, and script block. Also missing Google Fonts link (3 lines). Breadcrumb and footer home hrefs pointed to `../index.html` (seed root) instead of `app/dashboard.html`.

**Root cause:**
Build session for sales.html did not follow the page template from FRAMEWORK.md §2 exactly. The template has `<base href="../">` but it was omitted.

**Impact:**
Logo and all assets could not resolve. Font fell back to system sans-serif (Instrument Sans not loaded). Breadcrumb/footer home links pointed to seed page instead of CRM dashboard.

**Resolution:**
- Added `<base href="../">` as first child of `<head>`
- Removed `../` from all CSS and script `src/href` attributes
- Added Google Fonts 3-line block
- Fixed breadcrumb and footer home hrefs to `app/dashboard.html`

**Rule reinforced in FRAMEWORK.md §2:**
Every app page must begin with `<base href="../">` immediately after `<head>`. All asset paths use bare `assets/...` — never `../assets/...`.

---

### GAP-023 — crm-shell calendar SVG missing 4 day dots + extra locale toggle + wrong aria-label

**Discovered during:** nav bar sign-off review post deals.html (2026-05-11)
**Status:** RESOLVED — 2026-05-11

**Description:**
Three separate structural differences between shell HEADER_HTML and seed header:

1. **Calendar SVG dots**: Shell had 2 of 6 calendar day dot paths. Missing: `(17,13.5)`, `(12,17.5)`, `(7,17.5)`, `(7,13.5)`. Calendar icon showed fewer date markers than seed.

2. **Locale toggle**: Shell had an extra `<button id="crm-locale-toggle">اردو</button>` element not present in seed. This added a visible extra button in the nav bar.

3. **app-toggler aria-label**: Shell had `aria-label="Toggle sidebar"` vs seed's `aria-label="app toggler"`.

**Root cause:**
Calendar SVG was copied partially. Locale toggle was added as a CRM feature that predates the seed-first rule. aria-label was rewritten from memory.

**Resolution:**
- Added 4 missing calendar dot `<path>` elements to SVG
- Removed locale toggle button
- Fixed aria-label to `"app toggler"` per seed

---

### GAP-026 — DataTables with avatar img columns need autoWidth:false

**Discovered during:** review.html browser verification (2026-05-12)
**Status:** RESOLVED — 2026-05-12

**Description:**
DataTables `autoWidth: true` (default) calculates column widths at JS initialisation time. If a column contains `<img>` tags (avatars, product images) and the images have not loaded when DataTables initialises, the column measures narrower than its true width, causing other columns to take more space than intended. The resulting layout does not match the seed.

**Root cause:**
The seed page's sidebar is static HTML — the page is fully loaded and settled before DataTables runs. The CRM page's sidebar is injected by `crm-shell.js` at parse time, which triggers a re-layout. If avatar images are in-flight at that moment, `autoWidth` miscalculates.

**Rule:**
`autoWidth: false` is required ONLY when the DataTable contains `<img>` tags that are **not** CSS-size-constrained (i.e., images rendered at their natural dimensions). If avatar images are wrapped in `.avatar.avatar-xxs` (or similar sized classes with explicit `width`/`height` px), the image dimensions are fixed by CSS and the race condition does not occur — leave `autoWidth` at its default (`true`).

**Resolution:**
- Added `autoWidth: false` to `#dt_RecentReviews` in `crm-review.js` (review avatars are unconstrained)
- `#dt_Activities` uses `avatar-xxs` (CSS-constrained) — `autoWidth: false` was initially added then REMOVED (2026-05-12) after it caused column spacing drift vs seed
- Applies to any future DataTable: check whether avatar wrapper class has explicit px dimensions before adding `autoWidth: false`

---

### GAP-005 — Sidebar icon tab active state hardcoded to dashboardTab

**Discovered during:** FRAMEWORK.md §4 review (2026-05-10)
**Status:** RESOLVED — 2026-05-12

**Description:**
The left-rail icon tabs switch sidebar panels via Bootstrap `data-bs-toggle="tab"`. The Dashboard icon tab had `class="menu-link active"` hardcoded. Pages with `CRM_PAGE = 'calendar'` or `'chat'` (Apps tab pages) showed the Dashboard panel instead of the Apps panel.

**Impact:**
Apps-tab pages (calendar, chat, inbox) showed the wrong sidebar panel (Dashboard links instead of Apps links).

**Resolution:**
Added post-injection logic to `crm-shell.js` DOMContentLoaded handler. Maps appsTab CRM_PAGE values (`chat, calendar, inbox, compose, read-email`) to `#appsTab` and programmatically activates it via `bootstrap.Tab`. Implemented when first Apps-tab pages (calendar.html, chat.html) were built.

---

### GAP-006 — `app/marketing.html` seed source unconfirmed

**Discovered during:** FRAMEWORK.md §17 review (2026-05-10)
**Status:** RESOLVED — 2026-05-12

**Description:**
`src/marketing.html` was unconfirmed as the correct seed source for `app/marketing.html`.

**Resolution:**
Confirmed `src/marketing.html` is the correct seed. Seed JS driver is `src/assets/js/dashboard/marketing.js` (6 ApexCharts: revChart, aovChart, purchaseChart, growthChart, adsTrendChart, leadFunnelChart). No DataTables elements in main content — datatables lib excluded per §19 despite seed loading it. FRAMEWORK.md §17 and §24 updated.
