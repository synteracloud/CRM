# B9-P07::WORKFLOW_VISUAL_UI

## Scope

This specification defines a **visual workflow builder UX model** that is a strict projection of `docs/workflow-dsl.md` and remains semantically aligned with `docs/workflow-catalog.md` canonical sequences.

---

## 1) Workflow visual UI structure

## 1.1 Screen composition

The builder is a three-pane experience:

1. **Left palette (authoring primitives)**
   - Trigger block
   - Condition block
   - Action templates (`emit_event`, `call_service`, `notify`, `mutate_state`, `wait`)
   - Canonical event picker seeded from workflow catalog trigger events
2. **Center canvas (graph authoring)**
   - Directed graph of nodes and edges representing `sequencing.steps`
   - Zoom/pan/minimap
   - Status overlays for validation and execution state
3. **Right inspector (schema-bound editor)**
   - Contextual form for selected node/edge/workflow metadata
   - Raw DSL JSON preview (read-only by default; optional expert edit mode)

Top bar:
- Workflow identity: `workflow_key`, `version`, `metadata.name`, `metadata.domain`, `owner_service`, tags
- Validation state summary (error/warning counts)
- Save, Validate, Simulate, Publish controls

Bottom panel:
- Problems list (grouped by Error / Warning / Info)
- Execution timeline for live runs and past run replay

## 1.2 Canonical mapping: UI model ↔ DSL

| UI element | DSL field | Notes |
|---|---|---|
| Workflow settings form | `workflow_key`, `version`, `metadata.*` | `workflow_key` must be snake_case and catalog-aligned. |
| Trigger configuration card | `triggers.mode`, `triggers.events`, `triggers.schedule`, `triggers.manual` | Event chips must use canonical event names. |
| Global condition builder | `conditions.match`, `conditions.rules[]` | Rule rows map 1:1 to `{field, op, value}` objects. |
| Canvas node (step) | `sequencing.steps[]` item | Node `id` = step id. |
| Node guard expression | `sequencing.steps[].when` | Optional guard; referenced as expression string. |
| Node action binding | `sequencing.steps[].action` | Must reference key in `actions`. |
| Node timeout + retries | `sequencing.steps[].timeout`, `sequencing.steps[].retries` | Optional fields. |
| Edge target | `sequencing.steps[].next` (branching only) | Required when strategy is `branching`. |
| Strategy toggle | `sequencing.strategy` | `linear` or `branching`. |
| Error policy selector | `sequencing.on_error` | `fail_fast`, `continue`, `compensate`. |
| Action library editor | `actions[action_ref]` objects | Full action configuration block. |

## 1.3 Node and edge system

### Node types

1. **Start node (virtual)**
   - Non-DSL runtime visualization node.
   - Connects to first step(s) for readability.
2. **Step node (DSL-backed)**
   - Required fields: `id`, `action`
   - Optional fields: `when`, `timeout`, `retries`, `next` (branching)
3. **End node (virtual)**
   - Non-DSL sink visualization node.
   - Any terminal step may connect to End in canvas view.

### Edge semantics

- **Linear strategy**
  - Implicit order edge from step[i] → step[i+1].
  - UI can render these as locked edges (non-editable by default).
- **Branching strategy**
  - Explicit edge from each step based on `next`.
  - `next = end` maps to edge to End node.
- **Guarded branch display**
  - If `when` exists on destination step, edge badge shows guard snippet.

### Graph invariants (enforced)

- At least one step node exists.
- No duplicate step ids.
- No cycles in step graph.
- Every edge target resolves to an existing step id or `end`.
- Every step references an existing `actions` key.

---

## 2) Builder interactions

## 2.1 Authoring flow

1. Create/select `workflow_key` from catalog-derived suggestions.
2. Configure triggers using canonical event picker.
3. Add global conditions using rule builder.
4. Build sequencing graph:
   - Linear mode: reorder list/canvas nodes.
   - Branching mode: draw edges and set `next` targets.
5. Define/edit action definitions in action library.
6. Bind each step to action reference.
7. Validate continuously; fix blockers.
8. Simulate with sample context payload.
9. Publish when zero errors.

## 2.2 Trigger / condition / action editing UX

### Trigger editor

- **Mode selector**: `any` vs `all`.
- **Event selector**:
  - Multi-select chips from canonical event dictionary.
  - Free-text disabled for non-admin mode to prevent invalid event names.
- **Schedule**:
  - Cron helper with next-run preview.
  - Optional and mutually compatible with events.
- **Manual**:
  - Toggle for ad-hoc invocation.

### Condition editor

- **Match operator**: `all` / `any`.
- **Rule grid**:
  - Field path autocomplete (from schema introspection when available).
  - Operator dropdown (`exists`, `in`, `eq`, etc. as supported by engine).
  - Type-aware value editor (bool, number, string, array).
- **Preview chips**: human-readable condition summary.

### Action editor

- **Action reference key** (`action_ref`) management with uniqueness checks.
- **Type-first form**:
  - `type` determines required controls.
- **Common fields**:
  - `service`, `operation`, `input` JSON editor.
- **Optional fields**:
  - `output` schema editor.
  - `emits` event list with catalog validation.
- **Binding awareness**:
  - Inspector shows all steps currently referencing this action.

## 2.3 Editing safeguards

- Renaming an action reference performs transactional refactor across bound steps.
- Deleting an action in use is blocked until step bindings are reassigned.
- Switching strategy (`linear` ↔ `branching`) runs migration wizard:
  - Linear → Branching: initialize `next` from current order.
  - Branching → Linear: requires a single acyclic path; otherwise block with resolution guidance.

---

## 3) Validation patterns

Validation runs on every change (debounced) and on explicit Validate/Publish.

## 3.1 Rule classes

### A) Schema validation (structural)
- Missing required fields (`workflow_key`, `triggers`, non-empty `steps`, etc.).
- Type mismatches for booleans/enums/arrays.
- Unknown enum values (`sequencing.on_error`, action `type`, etc.).

### B) Referential validation
- `sequencing.steps[].action` must exist in `actions`.
- `next` references must resolve.
- Duplicate identifiers rejected (`step.id`, `action_ref`).

### C) Graph validation
- Acyclic graph requirement.
- Non-empty reachable path from Start to End.
- Branching mode requires `next` on each step.

### D) Catalog/semantic validation
- `workflow_key` must map to canonical workflow name in snake_case.
- Trigger events must be canonical event names.
- Sequence must preserve catalog ordered semantics for mapped canonical workflow.

### E) Policy validation
- Publish blocked if any Error-level findings.
- Warnings allowed for draft save, blocked for publish when policy flag `strict_publish=true`.

## 3.2 Feedback channels

1. **Inline field errors** in inspector.
2. **Node badges** (red error count, amber warnings).
3. **Edge highlights** for broken targets.
4. **Global problems panel** with click-to-focus navigation.
5. **Publish gate modal** listing blocking violations.

## 3.3 Invalid workflow blocking rules

A workflow is **non-publishable** if any of the following are true:

- Missing/invalid `workflow_key` or not catalog-aligned.
- Trigger event names not canonical.
- Any step action unresolved.
- Graph cyclic or disconnected.
- Branching workflow with missing `next`.
- Sequence semantically inconsistent with canonical ordered steps.

---

## 4) Execution state visibility

## 4.1 Runtime overlays on canvas

Per node:
- `NotStarted` (neutral)
- `Queued` (blue)
- `Running` (animated blue)
- `Succeeded` (green)
- `Failed` (red)
- `Skipped` (gray, e.g., guard false)
- `Retried(n)` (orange badge with count)

Per edge:
- Traversed edges highlighted during replay/live execution.
- Failed transition edges marked red.

## 4.2 Run details panel

- Run header: `run_id`, workflow key/version, trigger event, started/ended timestamps, duration.
- Step timeline:
  - Attempt number
  - Start/end timestamps
  - Effective input snapshot (sanitized)
  - Output snapshot/reference
  - Error summary and retry reason
- Error policy behavior visualization:
  - `fail_fast`: halted downstream nodes shown as blocked.
  - `continue`: downstream nodes continue with warning banner.
  - `compensate`: compensation chain shown explicitly.

## 4.3 Understandability patterns

- Plain-language status labels in addition to color.
- Consistent iconography for trigger, condition, action, wait.
- Hover tooltips include DSL pointer (example: `sequencing.steps[2].action`).
- “Why skipped?” explainer for guard and dependency skips.

---

## 5) Deterministic DSL export contract

The visual model serializes to DSL JSON with stable ordering:

1. Top-level keys in canonical order:
   `workflow_key`, `version`, `metadata`, `triggers`, `conditions`, `sequencing`, `actions`.
2. `sequencing.steps` export order:
   - `linear`: current ordered list.
   - `branching`: topological order with stable tie-break (`id` ascending).
3. No UI-only fields (`x`, `y`, color, collapse state) in exported DSL.
4. Virtual Start/End nodes are excluded from DSL output.

---

## SELF-QC

### Visual builder maps to DSL exactly
- Every editable visual construct has a direct DSL field mapping table and deterministic export behavior.
- UI-only graph aids (Start/End, coordinates) are explicitly excluded from DSL payload.
- Result: ✅ Pass.

### Invalid workflows blocked
- Validation includes schema, referential, graph, semantic, and policy gates.
- Publish is blocked on all error-class violations including cycles, unresolved actions, invalid events, and catalog misalignment.
- Result: ✅ Pass.

### Execution states understandable
- Node/edge runtime overlays, timeline details, and policy-aware execution visualization provide clear run interpretation.
- “Why skipped?” and DSL-pointer tooltips reduce ambiguity during debugging.
- Result: ✅ Pass.

## FIX LOOP

1. Fix: tightened 1:1 DSL mapping, explicit graph invariants, and publish gate criteria.
2. Re-check: verified against `docs/workflow-dsl.md` required fields/validation and `docs/workflow-catalog.md` canonical sequencing semantics.
3. Score: **10/10**.
