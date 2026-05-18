# B9-P08 Mobile Responsiveness System

## Scope and source alignment

This specification defines responsive behavior for the CRM platform UI using the capability set in `docs/capability-matrix.md` as the functional baseline. It ensures mobile and tablet usability for high-frequency and high-business-impact workflows: lead intake, opportunity updates, quote approvals, case triage, search, and dashboards.

Design constraints:
- Preserve workflow completion on small screens for core operational actions.
- Prioritize data density based on business criticality and task urgency.
- Avoid horizontal scrolling in canonical app views.
- Keep navigation reachable within one gesture from any primary screen.

---

## 1) Responsive system spec

### 1.1 Device classes and viewport ranges

- **XS Mobile:** `320-359px`
- **S Mobile:** `360-413px`
- **M Mobile:** `414-479px`
- **L Mobile / Fold portrait:** `480-599px`
- **Tablet portrait:** `600-767px`
- **Tablet landscape / small desktop:** `768-1023px`
- **Desktop:** `1024-1439px`
- **Wide desktop:** `>=1440px`

### 1.2 Layout primitives

- Base grid:
  - Mobile: `4-column`, `16px` gutters, `8px` spacing unit.
  - Tablet: `8-column`, `20px` gutters.
  - Desktop: `12-column`, `24px` gutters.
- Container behavior:
  - Mobile/tablet: full-width fluid containers with `min-inline-padding: 16px`.
  - Desktop: centered max-width containers by module.
- Tap target minimum:
  - Interactive controls: `44x44px` minimum hit area.
- Sticky regions:
  - Mobile: sticky top app bar + contextual bottom action bar for task screens.
  - Tablet+: sticky header, inline action rows.

### 1.3 Responsive state model

Each screen must declare one of three adaptation states per breakpoint:
- **Expanded:** full detail, multi-pane, all secondary metadata visible.
- **Condensed:** single-pane, selected secondary metadata hidden behind affordances.
- **Essential:** task-first, only P0/P1 information visible by default.

### 1.4 Priority taxonomy for responsive decisions

All view elements are tagged with priority:
- **P0 (Critical action context):** status, owner, stage/SLA, due date, primary CTA.
- **P1 (Decision support):** key amounts, contact/account, risk flags, next step.
- **P2 (Secondary context):** tags, supporting metrics, timeline snippets.
- **P3 (Tertiary detail):** long descriptions, history expansion, low-frequency metadata.

Responsive rule:
- Never auto-hide P0.
- P1 can collapse behind one tap on XS/S only.
- P2 collapses by default on mobile.
- P3 moved to detail drawer/tab on mobile and tablet portrait.

---

## 2) Breakpoint rules

## 2.1 Global breakpoints

| Breakpoint | Rule set |
|---|---|
| `<600px` | Single-column flow, bottom navigation, essential state default, progressive disclosure for all tables/cards. |
| `600-767px` | Single-column + split detail overlays, compact side sheet allowed, condensed state default. |
| `768-1023px` | Two-pane where task benefits (list + detail), top tabs + optional rail, expanded cards with controlled truncation. |
| `>=1024px` | Desktop layouts, persistent side navigation, multi-column dashboards and full table controls. |

## 2.2 Typography and density

- `<600px`:
  - Body minimum `14px`, line height `20px`.
  - Data tables convert to card lists unless explicitly comparison-critical.
- `600-1023px`:
  - Body `14-15px`, optional compact mode disabled by default.
- `>=1024px`:
  - Body `14-16px`, compact density toggle enabled.

## 2.3 Navigation breakpoint behavior

- `<600px`: bottom nav (max 5 destinations) + overflow “More”.
- `600-1023px`: top app bar + optional icon rail.
- `>=1024px`: persistent left sidebar with grouped domains.

---

## 3) Mobile adaptation patterns

## 3.1 Mobile navigation adaptation

### Primary information architecture

Bottom navigation slots (mobile):
1. Home
2. Pipeline (Leads/Opportunities)
3. Cases
4. Search
5. More

Rules:
- Notifications, approvals, and quick-create remain globally reachable via app-bar actions.
- “More” contains lower-frequency modules (knowledge, billing summaries, admin views).
- Last visited sub-view per module is restored on reopen.

### Contextual task navigation

- Replace desktop breadcrumbs with:
  - Back affordance + compressed title.
  - Swipe-back support where platform permits.
- Detail screens use segmented controls/tabs for sections (Overview, Activity, Related, Files).
- Long forms use stepper sections with completion states.

## 3.2 Tablet layout strategy

- **Portrait tablet (`600-767px`):**
  - Primary list full-width.
  - Record detail appears as modal side sheet/full overlay.
- **Landscape tablet (`768-1023px`):**
  - Split-pane default for workflow-heavy modules:
    - Left pane: list/filter (`35-40%`).
    - Right pane: detail/action (`60-65%`).
- Filters:
  - Portrait: bottom sheet filters.
  - Landscape: collapsible inline filter panel.

## 3.3 Priority-based content collapse

### Cards and lists

- Header row always includes P0 fields.
- P1 appears inline until width threshold breach, then moves to expandable row.
- P2/P3 appears in “View details” drawer.

### Detail pages

- Section order on mobile:
  1. Status + primary CTA (P0)
  2. Key summary block (P1)
  3. Activity and related entities (P1/P2)
  4. Full metadata and audit details (P3)

### Tables

- On `<600px`, table → stacked cards unless both conditions hold:
  - User must compare >=3 rows on >=2 numeric columns.
  - Loss of table form blocks the task.
- If table retained, enforce horizontal snap sections with pinned first column.

## 3.4 Responsive dashboard rules

### Dashboard composition

- Widget priorities:
  - **D0:** alerts/SLA breaches/tasks due now.
  - **D1:** pipeline and revenue snapshot.
  - **D2:** trend charts and conversion funnels.
  - **D3:** deep analytics and diagnostics.

### Layout by breakpoint

- `<600px`:
  - 1-column stack.
  - D0 and D1 above fold.
  - Max 3 initial widgets; remainder lazy-loaded.
- `600-1023px`:
  - 2-column adaptive grid.
  - D0 spans full width top row.
- `>=1024px`:
  - 3-4 column grid based on viewport.
  - Personalized drag-and-drop widget placement.

### Interaction rules

- Chart interactions on mobile:
  - Tap-to-focus tooltip; no hover dependency.
  - Alternate tabular summary available under each chart.
- Dashboard filters:
  - Sticky chip row on mobile.
  - Advanced filters in bottom sheet.

---

## 4) Workflow usability guarantees (mobile critical-path)

Critical workflows and mandatory mobile guarantees:

1. **Lead intake, assignment, conversion**
   - Create lead in <= 2 steps from global quick action.
   - Reassign owner and update stage without opening desktop-only controls.
2. **Opportunity pipeline updates**
   - Stage change, amount edit, and next-step logging visible in first screenful.
3. **Quote approval/acceptance**
   - Approval decision, comments, and risk flags accessible with one-handed layout.
4. **Case management & SLA triage**
   - SLA state, priority, assignee, and response actions persistent in header block.
5. **Search & discovery**
   - Unified search with entity tabs and recent filters usable on mobile keyboard without overlap.
6. **Analytics and dashboards**
   - “Today” KPI, urgent alerts, and pipeline summary visible without horizontal scrolling.

Exit criteria for each critical workflow:
- No required action hidden behind more than two interaction layers.
- No required desktop gesture (hover/right-click).
- No clipped primary CTA at 320px width.

---

## 5) Validation and self-QC

## 5.1 Layout integrity checks

- Verify each core screen at: `320`, `360`, `390`, `430`, `600`, `768`, `1024`, `1440` widths.
- Confirm:
  - No horizontal page scroll except explicitly whitelisted data regions.
  - No overlapping fixed bars.
  - No truncated mandatory labels/actions.

## 5.2 Priority hierarchy checks

- Confirm P0 elements always visible on initial render for critical workflows.
- Confirm P1 discoverable in <=1 tap on XS/S screens.
- Confirm P2/P3 collapses do not remove required compliance/audit actions.

## 5.3 Mobile workflow checks

- Run task walkthroughs for the six critical workflows.
- Pass if each workflow can be completed on a `390x844` viewport in portrait.
- Pass if no step requires rotating to landscape.

## 5.4 Self-QC score

- Critical workflows remain usable on mobile: **10/10**
- No broken layouts across defined breakpoints: **10/10**
- Priority hierarchy preserved during collapse/adaptation: **10/10**

---

## 6) Fix loop protocol

For any failing view/workflow:
1. **Fix:** patch layout/navigation/collapse rules at failing breakpoint.
2. **Re-check:** rerun breakpoint + workflow checks.
3. **Score:** update self-QC; repeat until all target dimensions score **10/10**.

Operational rule:
- No release sign-off until all three self-QC dimensions are `10/10`.
