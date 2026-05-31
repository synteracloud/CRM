# Page Build Protocol — Pakistan CRM

**This file must be read at the start of every page build session, before writing a single line of HTML or JS.**

Source docs this protocol is compiled from:
- `FRAMEWORK.md` §0, §9, §16, §17, §24, §31
- `DESIGN-SPEC.md` §1, §2, §4, §5
- `CLAUDE.md` build checklist
- `backend/docs/ui/read-models.md`

---

## Non-Negotiable Build Rule — Archetype-Driven Builds

**All 75 custom pages must be built archetype by archetype. No exceptions.**

This rule was codified 2026-05-28 after analysis confirmed that page-by-page builds cause structural drift between pages of the same archetype.

**The rule:**
1. Pages are built in archetype groups, not individually
2. The b9-p spec for the archetype is the authority for every page in that group
3. The **first page built** in an archetype becomes the **reference implementation** — its structure, component choices, and interaction patterns are locked in
4. Every subsequent page in the same archetype is built by applying the reference to different entity/field data — the structure does not change
5. An archetype is considered done only when all its pages pass T1–T4 and are browser-locked
6. No new archetype starts until the current archetype's pages are locked

**Why:** Building B-01 and B-08 at different times without this rule produced two Archetype B pages with different structural decisions. That is now fixed. It must not recur.

---

## Phase 0 — Page Selection and Accuracy Validation

**Do this before anything else. Never build a page that hasn't cleared both checks below.**

### 0.1 — Which page to build next

1. Open **DESIGN-SPEC.md §4** — the build phase plan.
2. Find the current approved phase (confirmed by the user — do not self-assign a phase).
3. Within that phase, take the next page with status **⬜ Not started**, in priority order (top = highest priority).
4. That page is what gets built. Nothing else.

Selection rationale is already decided in §4:
- Phase 1 = Core Execution Surfaces (daily revenue + follow-up discipline)
- Phase 2 = Sales Intelligence
- Phase 3 = Finance & Collections
- …and so on. The rationale is documented in §4 — do not second-guess it.

### 0.2 — Accuracy validation before building

A page spec is only trustworthy when all four sources agree. Read them in this order and confirm they are consistent with each other:

| # | Source | What it tells you |
|---|---|---|
| 1 | **DESIGN-SPEC.md §3** entry for this page | Archetype, file name, route, status, key requirements |
| 2 | **b9-p spec doc** for this page's archetype (see DESIGN-SPEC.md §5) | Layout zones, field contracts, UI rules, API routes |
| 3 | **Domain doc** relevant to this page (e.g. `backend/docs/domain/owner-dashboard.md`) | Business logic, read model name, data field definitions |
| 4 | **`backend/docs/ui/read-models.md`** | Exact API response envelope, field names, data types |

If any two of these disagree → **stop. Raise the conflict with the user before building.** A mismatch means either a doc is stale or the spec changed. Building on a conflict produces a page that will fail QC.

Only when all four agree: proceed to Phase 1.

---

## Phase 1 — Scope Gate

1. Open **DESIGN-SPEC.md §4** — find the page in the screen inventory.
   - If it is NOT listed in the current approved phase → **stop. Ask for explicit approval. Do not proceed.**
   - If it IS listed → note the page's archetype (A–M) and its b9-p spec doc.

---

## Phase 2 — Read the Docs

2. Read **DESIGN-SPEC.md §2** — design constraints that apply to every screen:
   - RTL from day 1 (`crm-locale.js`)
   - PKR formatting via `pkr()` — never raw integers
   - Dummy mode via `crm-api.js` — never hardcode data in HTML
   - NexLink class chains only — no custom CSS outside `crm-custom.css`
   - ≤2 steps for core actions
   - Mobile-first, 360px viewport minimum

3. Read the **b9-p spec doc** for this page's archetype — layout zones, field contracts, API routes.

4. Read **FRAMEWORK.md §0** Steps 1–7 in full:
   - Step 1: Identify seed via FRAMEWORK.md §17
   - Step 2: Find `<main>` start line in seed
   - Step 3: Read seed `<main>` content in full — extract every element ID
   - Step 4: Read seed script block — record every `assets/libs/` include
   - Step 5: Cross-check every element ID against FRAMEWORK.md §24
   - Step 6: If IDs not in §24 → read seed JS file in full, add configs to §24
   - Step 7: Look up correct `CRM_PAGE` key in FRAMEWORK.md §18

5. Read **FRAMEWORK.md §16** — the per-page build checklist. Run through it mentally for this specific page before writing anything.

---

## Phase 3 — Read the Seed

6. Confirm seed path from **FRAMEWORK.md §17**.
7. Read the full seed HTML from `<main>` to `</body>` — do not skim.
8. List every element ID: chart divs, canvas IDs, table IDs, modal IDs.
9. Read the seed's script block — every `assets/libs/` line is a required include.
10. For each element ID: look up in **FRAMEWORK.md §24** and copy config verbatim. If not in §24, read the seed JS file completely before writing the driver.

---

## Phase 4 — Build

### HTML file (`app/[page].html`)

11. Use the CSS stack from **FRAMEWORK.md §31 §3.3** — exact order, do not reorder:
    ```
    flaticon → lucide → fontawesome → simplebar → node-waves → bootstrap-select
    → [page-specific vendor CSS: datatables, flatpickr, etc.]
    → styles.css (with id="main-stylesheet")
    → crm-custom.css  ← MANDATORY, always last
    ```

12. **No `<footer>` block** — `crm-shell.js` injects it at runtime. If the seed has one, delete it before saving. *(FRAMEWORK.md §16)*

13. `<base href="../">` must be the first tag inside `<head>`. *(FRAMEWORK.md §31 §3.1)*

14. Set `window.CRM_PAGE = '[key]'` before the `crm-shell.js` script tag.

15. Script load order from **FRAMEWORK.md §31 §3.4**:
    ```
    global.min.js → crm-dummy.js → crm-api.js → [CRM_PAGE script] → crm-shell.js
    → crm-components.js → appSettings.js → main.js
    → [page-specific vendor JS: datatables, apexcharts, etc.]
    → crm-[page].js → crm-locale.js
    ```

### DataTable alignment — 3 places required

16. **Place 1 — HTML `<thead>`:** Every `<th>` on ANY table must be center-aligned. Always. No exceptions.
    - DataTables: `dt-head-center` on every `<th>`
    - Plain Bootstrap tables: `text-center` on every `<th>`
    Never leave a `<th>` without an alignment class. Never use `dt-head-left` or `dt-head-right`. Reference: contacts.html (DataTable), finance-analytics.html (plain table).

17. **Place 2 — JS column definition:** Every column entry must have `className`:
    - `dt-body-left` / `dt-body-center` / `dt-body-right`
    - Use the `columns: [{ data: '...', className: 'dt-body-center' }]` pattern

18. **Place 3 — `crm-custom.css` (ALL tables, with `!important`):** DataTables' own CSS overrides `className` at runtime. Always add explicit CSS rules in `crm-custom.css` with `!important` for every DataTable:
    ```css
    #dt_TableName.dataTable tbody > tr > td { text-align: center !important; }
    #dt_TableName.dataTable tbody > tr > td:nth-child(N) { text-align: left !important; }
    ```
    Without `!important` these rules lose to DataTables' internal stylesheet regardless of specificity.

### Card height — THREE patterns require `style="height:auto"`

19. NexLink `.card` has `height: calc(100% - var(--bs-gutter-x))`. Add `style="height:auto"` in these three cases:

    **Pattern A — Identity strip** (sole card in a `col-12` standalone row):
    ```html
    <div class="card mb-0" style="height:auto">
    ```

    **Pattern B — Stacked cards in a column** (2+ cards vertically in same `col-*`):
    Every card in a stacked column must have `height:auto` — each card otherwise tries to fill 100% of the column height simultaneously, clipping content and pushing the footer up.
    ```html
    <div class="col-lg-9">
      <div class="card mb-3" style="height:auto">...</div>
      <div class="card mb-3" style="height:auto">...</div>
      <div class="card" style="height:auto">...</div>
    </div>
    ```

    **Pattern C — Context panel sidebar cards** (col-lg-4 right panels on detail pages):
    Same as Pattern B — all context panel cards need `height:auto`.

    **Rule:** When in doubt, add `height:auto`. The default is only intentional for a single card filling an entire column beside another same-height card.

### Settings / two-pane layout rules

20. Settings pages (G-series and any page with a left-nav + right-content two-column layout) have three mandatory rules that must all be applied together. Violating any one causes footer to appear mid-page and last card to be clipped. *(Root cause incident: 2026-05-29 — 5 settings pages broken)*

    **Left nav — always `list-group`, never `nav-pills`:**
    NexLink's `crm-shell.js` sidebar owns `.nav-pills` globally. A second `.nav-pills` in the page body bleeds sidebar CSS into the page nav, constraining row height.
    ```html
    <!-- CORRECT -->
    <div class="list-group list-group-flush">
      <a class="list-group-item list-group-item-action active d-flex align-items-center gap-2 py-2" href="...">
      <a class="list-group-item list-group-item-action d-flex align-items-center gap-2 py-2" href="...">
    </div>

    <!-- WRONG — do not use -->
    <div class="nav flex-column nav-pills gap-1">
      <a class="nav-link active ...">
    ```

    **Container — always `pb-4`:**
    ```html
    <div class="container-fluid pb-4">
    ```

    **All right-column cards — `style="height:auto"`** (Pattern B above applies).

### Filter chips

21. All tab-style filter strips use `nav-pills-custom` — **never `btn-group`**. *(FRAMEWORK.md §31 Filter Chip Pattern)*
    ```html
    <ul class="nav nav-pills nav-pills-custom p-1 bg-light rounded-5" id="FILTER_ID" role="tablist">
      <li class="nav-item"><button type="button" class="nav-link rounded-5 active" data-filter="">All</button></li>
      <li class="nav-item"><button type="button" class="nav-link rounded-5" data-filter="X">X</button></li>
    </ul>
    ```

### JS driver file (`crm-[page].js`)

20. All chart/table/interactive configs copied verbatim from FRAMEWORK.md §24 or seed JS.
21. Every chart/table init wrapped in an element guard: `if (el)` / `if ($('#id').length)`.
22. No hardcoded data — all values sourced from `window.CRM_DUMMY`.

---

## Phase 5 — QC and Lock

23. Run every gate in **FRAMEWORK.md §9 Review Gate** (G-01 through G-10):
    - Page renders with dummy data — no blank widgets
    - Empty state (set `data: []`) handled gracefully
    - All KPI numbers live from dummy data — change a value in `crm-dummy.js`, reload, confirm update
    - Zero console errors in DevTools
    - Responsive at 1280px and 768px
    - RTL renders correctly (`crm-locale.js` test)
    - Navigation active state set
    - Breadcrumb correct
    - PROGRESS.md entry written

24. Update **PROGRESS.md** immediately after lock — never batch updates.

---

## Quick-reference: What to read before every build

| # | File | Section | Takes |
|---|---|---|---|
| 1 | `DESIGN-SPEC.md` | §4 scope gate → §2 design constraints | 5 min |
| 2 | b9-p spec doc for this archetype | Full doc | 10 min |
| 3 | `FRAMEWORK.md` | §0 pre-build steps 1–7 | 5 min |
| 4 | `FRAMEWORK.md` | §16 build checklist | 2 min |
| 5 | Seed HTML + seed JS | Full read | 10 min |

---

## Canonical Archetype Wiring Status

**Source:** `backend/FRONTEND-BACKEND-MAPPING.md` Section 7 (fresh analysis 2026-05-28 — direct gateway file reads).
**⚠️ Previous table (Phase M-2, 2026-05-27) was produced by a hallucinating session — all "gaps closed" claims were unverified. This table supersedes it.**

Before building any page, check this table and the mapping category. Category 2 and 3 pages cannot be wired to live endpoints in their current state.

| Archetype | Gateway routes | Mapping | Wiring status | Pages wirable today |
|---|---|---|---|---|
| A — Dashboard / KPI | ✅ Leads[I]+Opps[I]+Followups[I]+Collections[I]+Forecasts[I] | Mixed | 🟡 Partial — 5 of 13 pages Cat1; 7 Cat2; 1 Cat3 | A-01/02/04/05/06 |
| B — List / Queue | ✅ Most domains inline; Contacts/Accounts/Tasks opaque proxy | Mixed | 🟡 Partial — 5 of 11 Cat1; 6 Cat2 | B-01/02/08/09/10 |
| C — Entity Detail | ✅ Most domains inline; Contacts/Accounts opaque | Mixed | 🟡 Partial — 4 of 12 Cat1; 7 Cat2; 1 Cat3 | C-01/04/06/09 |
| D — Sales Cockpit | ✅ Leads[I]+Opps[I]+Followups[I]+Forecasts[I]; Tasks[P] | Cat 1 | 🟢 All gaps claimed closed — **unverified until DUMMY_MODE=false test** | D-01 |
| E — Support Console | ❌ No case/ticket gateway routes | Cat 2 | ❌ Cannot wire — no ticket domain | None |
| F — Marketing | ❌ No marketing gateway routes | Cat 2 | ❌ Cannot wire — no backend | None |
| G — Settings / Admin | ✅ Users[I]; ❌ No routes for flags/territories/notifications/compliance | Mixed | 🟡 Partial — G-02 Cat1; rest Cat2/Cat3 | G-02 only |
| H — Reporting | ✅ Payments[I]+Collections[I]+Audit[I]+Leads[I]+Opps[I] | Mixed | 🟡 Partial — H-01/04/06 Cat1; H-02/03/05/07 Cat2 | H-01/04/06 |
| I — Form / Wizard | ✅ Leads[I]+Opps[I]+Quotes[I]; Contacts[P] opaque | Mixed | 🟡 Partial — I-01/03/05 Cat1; I-02/04/06 Cat2 | I-01/03/05 |
| J — Audit / Compliance | ✅ Audit[I in-memory]+Users[I] | Mixed | 🟡 Partial — J-01/02/04 Cat1 (in-memory caveat); J-05 Cat2 | J-01/02/04 |
| K — Builder | ✅ Quotes[I]; Price Books[S stub] | Mixed | 🟡 Partial — K-04 Cat3; K-01/02/03 Cat2; I-05 Cat1 with stub | I-05 only |
| L — Inbox | ❌ Conversation service at port 5002, not exposed at gateway | Cat 3 | ❌ Cannot wire at gateway level — conversation endpoints not in gateway | None |
| M — AI / Copilot | ❌ No AI gateway routes | Cat 2 | ❌ Cannot wire — no AI backend | None |

**Legend:**
- 🟢 Cat 1 — both sides exist, wiring theoretically possible (all still hypothetical until DUMMY_MODE=false test passes)
- 🟡 Partial — some pages in archetype are Cat 1, others are Cat 2/3
- ❌ Cat 2 — no backend domain exists; dummy-mode only
- Cat 3 — backend richer than spec, or backend at service layer not exposed at gateway

**G-024 bug:** `v1-quotes.routes.js` — `respondError`/`respondSuccess` not imported. Fix before wiring any quote endpoints or they will throw ReferenceError on any error path.
