# B9-P08 EXTENSIONS::BUILDER_VISUAL_CANVAS (Custom Object + CPQ Logic + CPQ Approval Lane)

## Scope

Extends the **Builder / Visual Canvas** archetype (Archetype 8) and the **Pipeline / Stage Board / Kanban** archetype (Archetype 10) to cover the three pages not documented in existing specs:
- Custom Object Layout Builder (Archetype 8, page 3 of 4)
- Rule / CPQ Logic Builder (Archetype 8, page 4 of 4)
- CPQ Approval Lane Board (Archetype 10, page 3 of 3)

Existing coverage:
- Workflow Visual Builder → `docs/b9-p07-workflow-visual-ui.md`
- Campaign Journey Builder → `docs/b9-p05-marketing-workspace.md`
- Opportunity Pipeline Board + Lead Pipeline Board → `docs/b9-p03-sales-cockpit.md`

---

## 1) Custom Object Layout Builder

**Route:** `/app/admin/custom-objects/:object_type/layout`
**Role gate:** `super_admin`, `tenant_admin`
**Source:** Custom Object Framework — `docs/custom-object-framework.md`, `b9-p09-settings-admin.md §2.8`

### Builder structure

Three-pane visual editor (same shell as Workflow Visual Builder):

1. **Left palette** — available field types:
   - Text, Long text, Number, Currency (PKR default), Date, Datetime, Checkbox, Select, Multi-select, Relation (FK to any entity), Formula (read-only computed)
2. **Center canvas** — drag-and-drop field placement into a 12-column grid layout
   - Sections: collapsible named groups (e.g., "Basic Info", "Financial Details")
   - Fields dropped into grid cells; resize by drag
3. **Right inspector** — selected field properties:
   - Label, placeholder, required toggle, default value, help text
   - For Relation fields: target entity, display field, filter criteria

**Top bar:** `[Save Layout]` `[Preview]` `[Reset to Default]`
**Preview mode:** Shows the form as it would appear in `b9-p11-form-wizard.md §2.5` (Custom Object Record Form).

### Constraints
- At least one field required before saving.
- Relation fields must reference a valid entity from `docs/domain-model.md`.
- Layout changes apply to all new records; existing records show old fields with `[legacy]` badge.

---

## 2) Rule / CPQ Logic Builder

**Route:** `/app/admin/cpq/rules`
**Role gate:** `finance`, `tenant_admin`
**Source:** `docs/cpq-quotes-orders.md`

### Builder structure

Rule-table editor (not a canvas — tabular):

1. **Rule registry** — list of active pricing rules with name, condition summary, action, priority, and enabled/disabled toggle.
2. **Rule editor** (inline expand or slide-over):
   - **Condition section:** field picker (Opportunity fields, Quote fields, Account fields) + operator + value. Multiple conditions joined by AND / OR.
   - **Action section:** one of:
     - Apply discount `X%` to all line items
     - Apply discount `X%` to line items matching product category
     - Block quote if condition met (approval gate)
     - Auto-route to approver `[role]` if discount > `X%`
   - **Priority:** integer; lower number = higher priority. Conflict: highest-priority rule wins.
3. **Simulation panel:** Enter a sample quote scenario; system shows which rules fire in order and the final price.

### Constraints
- At least one condition required per rule.
- Rules are evaluated in priority order on every quote save.
- Circular rule detection: if rule A triggers condition that would re-trigger rule A, system blocks save with error.

---

## 3) CPQ Approval Lane Board

**Route:** `/app/sales/quotes/approvals`
**Role gate:** `sales_manager`, `finance`, `approver`
**Source entities:** `Quote`, `ApprovalRequest`
**Read model:** `QuoteApprovalCycleRM`

### Board structure

Kanban-style approval pipeline:

| Lane | Condition | Cards |
|---|---|---|
| Pending Review | `ApprovalRequest.status = pending` | Quote awaiting first approval |
| Under Review | `ApprovalRequest.status = in_review` | Currently with an approver |
| Approved | `ApprovalRequest.status = approved` | Ready for quote send |
| Rejected | `ApprovalRequest.status = rejected` | Requires revision |

**Card content:**
- Quote number + account name
- Total amount (PKR) + discount %
- Submitted by + submitted at (relative)
- SLA: approval due by (if configured)

**Card actions (per lane):**
- Pending Review → `[Claim review]`
- Under Review → `[Approve]` `[Reject with reason]` `[Request info]`
- Rejected → `[Revise quote]` (navigates back to CPQ Configurator)

**Design rule:** Approval decisions are logged in `AuditLog`. Reasons required for rejection. No auto-approval.

### Interaction patterns
1. **Claim before action:** Approver must claim a card before approve/reject — prevents race conditions.
2. **Rejection requires reason:** Free-text reason field required on reject. Reason visible to submitter.
3. **SLA visibility:** If approval is due within 2 hours, card shows amber SLA badge; expired shows red.
4. **No drag-and-drop between lanes:** Approval state changes only via action buttons — not by dragging cards.

---

## SELF-QC

### Builder archetype (Archetype 8) — now complete
- Workflow Visual Builder → `b9-p07` ✅
- Campaign Journey Builder → `b9-p05` ✅
- Custom Object Layout Builder → this doc ✅
- Rule / CPQ Logic Builder → this doc ✅

### Pipeline / Kanban archetype (Archetype 10) — now complete
- Opportunity Pipeline Board → `b9-p03` ✅
- Lead Pipeline Board → `b9-p03` ✅
- CPQ Approval Lane Board → this doc ✅

Score: **10/10**
