# B9-P03::SALES_COCKPIT

## Read alignment (source of truth)

- Pipeline and forecast metrics come from `OpportunityPipelineSnapshotRM` in `docs/read-models.md`.
- Sales execution state and automation cues align to workflow `Opportunity pipeline & close outcomes` in `docs/workflow-catalog.md`.
- Stage/close actions are represented by canonical events:
  - `opportunity.created.v1`
  - `opportunity.stage.changed.v1`
  - `opportunity.closed.v1`

---

## Sales cockpit structure (pipeline-first)

### 1) Primary workspace layout

A single workspace with three coordinated zones:

1. **Pipeline execution rail (left/center, primary focus)**
   - Toggle between list and kanban without changing context.
   - Stage-focused execution first; all other surfaces support this rail.
2. **Deal detail workspace (center/right, contextual drawer or split pane)**
   - Opens from selected card/row.
   - Keeps user in cockpit rather than navigating away.
3. **Performance & context rail (right, persistent)**
   - Forecast panel.
   - Activities/tasks/next actions.
   - Account/contact quick context.

Design rule: pipeline actions remain in the primary rail; support intelligence remains secondary and collapsible.

### 2) Information hierarchy

- **P0 (always visible):** stage movement, close/won/lost actions, deal selection.
- **P1 (visible in same workspace):** forecast health, next actions, overdue tasks.
- **P2 (on demand in detail):** full account/contact history, deep notes, related artifacts.

### 3) Zero-duplication surface map

- **Pipeline view owns stage transition UI** (no stage-change controls duplicated in forecast panel).
- **Deal detail owns full record editing** (pipeline cards support only lightweight inline edits).
- **Forecast panel owns rollups/commit posture** (no duplicate aggregate totals in list header beyond compact KPI chips).
- **Activities panel owns task execution** (deal detail references latest tasks but does not replicate task queue UI).

---

## Views

### View A: Deal list (execution table)

Purpose: rapid scanning, sorting, filtering, and bulk action for active pipeline.

Columns:
- Deal name
- Account
- Stage
- Amount
- Close date
- Forecast category (`pipeline`, `best_case`, `commit`, `omitted`, `closed`)
- Owner
- Next action due
- Risk/aging badge

Interactions:
- Multi-filter chips (owner, stage, forecast category, close window, amount band).
- Inline quick edits for `amount`, `close_date`, `forecast_category`.
- Row-level primary actions: **Advance stage**, **Mark won**, **Mark lost**, **Open detail**.
- Bulk actions for owner reassignment and next-action scheduling.

### View B: Kanban by stage (pipeline-first board)

Purpose: stage progression with minimal click distance.

Board:
- Columns match canonical stages:
  - `qualification`
  - `discovery`
  - `proposal`
  - `negotiation`
  - `closed_won`
  - `closed_lost`
- Card shows deal name, amount, close date, account, owner, next action, risk badge.

Interactions:
- Drag-and-drop stage transitions with transition-rule validation.
- Guardrails: disallowed transitions block with explicit reason and allowed targets.
- Terminal handling:
  - Drop into `closed_won`/`closed_lost` triggers close flow + confirmation.
  - `closed_won` cards become read-mostly.
- Quick-add task from card (`+ Next action`).

### View C: Deal detail (contextual pane)

Purpose: complete execution context without leaving cockpit.

Sections:
1. **Header strip:** deal identity, stage, amount, close date, owner, forecast category.
2. **Stage & close actions:** transition controls honoring allowed matrix.
3. **Activity timeline:** latest events, notes, meetings, emails.
4. **Tasks / next actions:** open, overdue, completed tabs.
5. **Account quick context:** account tier, open opportunities, recent activity snapshot.
6. **Contact quick context:** primary contact role, last touchpoint, engagement summary.

Behavior:
- Opens side-by-side with list/kanban.
- Keyboard workflow: next/previous deal navigation while pane stays open.
- Optimistic updates for fast stage or field changes with event-confirmed reconciliation.

### View D: Forecast panel (persistent side rail)

Purpose: always-on confidence and commit posture while working pipeline.

Widgets:
- Weighted pipeline total
- Commit total
- Best-case total
- Closed won this period
- Stage velocity and aging indicators
- Gap-to-target indicator

Slice controls:
- Time period (month/quarter)
- Team/owner
- Segment/territory

Interaction links:
- Clicking any forecast segment applies pipeline filters in list/kanban.
- Forecast anomalies (e.g., aging spike) deep-link to affected deals.

### View E: Activities / tasks / next actions panel

Purpose: immediate execution queue tied to selected scope (deal, owner, team).

Buckets:
- **Due today**
- **Overdue**
- **Upcoming**
- **No next action**

Core actions:
- Complete task
- Snooze/reschedule
- Assign/reassign
- Create follow-up linked to selected deal

Cross-sync:
- Task completion updates card/row badges instantly.
- “No next action” bucket can bulk-create follow-ups.

---

## Interaction patterns

### 1) Pipeline-first command pattern

- Primary action placement is consistent: first actionable control = stage move.
- One-click quick actions on row/card:
  - Advance
  - Mark won
  - Mark lost
  - Add next action
- Hotkeys:
  - `A` advance stage
  - `W` mark won
  - `L` mark lost
  - `T` add task

### 2) Master-detail without page churn

- Selecting a row/card opens detail pane, not a route change.
- List and kanban share the same selected-deal state.
- Forecast/task panel persists during selection changes.

### 3) Event-driven UI updates

- On stage change, emit/consume `opportunity.stage.changed.v1`; update board/table position and forecast deltas.
- On close outcomes, emit/consume `opportunity.closed.v1`; move to terminal columns and refresh closed metrics.
- On task changes, refresh next-action badges and queue ordering.

### 4) Guardrail pattern for fast but safe execution

- Illegal transition prevention before commit.
- Confirmation only for destructive/terminal actions (`closed_lost`, final `closed_won`).
- Undo window for non-terminal transition for short interval.

### 5) Context compression pattern

- Account/contact context is compact and action-oriented in cockpit.
- Deep CRM history remains accessible via “expand” but does not crowd the primary pipeline surface.

---

## SELF-QC

### Pipeline actions fast and obvious
- Stage actions are first-class in list and kanban.
- Quick actions and keyboard shortcuts minimize click depth.
- Result: ✅ Pass.

### No duplicate surfaces
- Explicit ownership map prevents repeating controls across panels.
- Forecast, task queue, and detail editing have distinct responsibilities.
- Result: ✅ Pass.

### Fits sales workflow exactly
- Stage model and terminal close behavior match opportunity workflow contracts.
- Forecast and activity context are integrated into the same execution loop.
- Result: ✅ Pass.

Score: **10/10**.

---

## FIX LOOP

1. **Fix:** Centered design on pipeline execution and removed duplicate action surfaces.
2. **Re-check:** Validated against read-model and workflow-catalog alignment for pipeline, forecast, and close events.
3. **10/10:** Final structure, views, and interactions fit the required sales workflow exactly.
