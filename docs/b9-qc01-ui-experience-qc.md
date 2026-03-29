# B9-QC01::UI_EXPERIENCE_QC

## Inputs reviewed
- All B9 outputs:
  - `docs/b9-p03-sales-cockpit.md`
  - `docs/b9-p04-support-console.md`
  - `docs/b9-p05-marketing-workspace.md`
  - `docs/b9-p07-workflow-visual-ui.md`
  - `docs/b9-p08-mobile-responsiveness-system.md`
- Cross-check docs:
  - `docs/ui-foundations.md`
  - `docs/capability-matrix.md`
  - `docs/read-models.md`
  - `docs/workflow-dsl.md`
  - `docs/workflow-catalog.md`

## Validation rubric (10 checks)

### 1) Design system covers all major surfaces
- `docs/ui-foundations.md` explicitly scopes tenant/admin, CRM operations, support, communication, workflow, search, analytics, and governance.
- Surface coverage aligns with `docs/capability-matrix.md` domain list.
- Result: ✅ Pass.

### 2) Dashboards are role-accurate (coverage)
- Reporting service defines role-to-dashboard mappings with explicit defaults (`tenant_owner`, `tenant_admin`, `manager`, `analyst`, `agent`, `auditor`).
- Dynamic dashboard rendering enforces role eligibility before returning payload.
- Result: ✅ Pass.

### 3) Dashboards are role-accurate (verified behavior)
- Re-check via tests confirms:
  - Allowed dashboard sets are resolved correctly by role.
  - Forbidden dashboard requests are rejected.
  - Default dashboard behavior is deterministic.
- Result: ✅ Pass.

### 4) Sales cockpit supports pipeline-first work
- B9 sales cockpit keeps stage progression as P0 action, with list/kanban primary rail, quick stage actions, and forecast/tasks as secondary context.
- Event-driven updates wired to `opportunity.stage.changed.v1` and `opportunity.closed.v1` preserve execution flow.
- Result: ✅ Pass.

### 5) Support console supports SLA-driven work
- Queue-first console sorted by SLA due-time and always-visible SLA timer.
- Escalation actions are deterministic by SLA state (`healthy`, `at_risk`, `breached`).
- Result: ✅ Pass.

### 6) Marketing workspace supports campaign work
- Guided campaign lifecycle from draft → segment validation → activation → attribution/journey/performance → completion.
- Each workspace view binds to explicit read-model metrics.
- Result: ✅ Pass.

### 7) Admin center controls system safely
- Admin control center applies default-deny panel visibility and permission-gated write states.
- Critical mutation patterns include two-step confirm, audit event controls, and workflow guardrails.
- Result: ✅ Pass.

### 8) Workflow UI maps to DSL and engine
- Visual builder has 1:1 UI↔DSL field mapping for triggers, conditions, sequencing, actions.
- Engine supports graph import/export with validation, action type constraints, referential checks, and strategy semantics.
- Result: ✅ Pass.

### 9) Responsive behavior preserves critical actions
- Mobile responsiveness spec enforces P0 visibility, <=2 interaction layers for required actions, and no desktop-only gestures.
- Critical workflows (lead, pipeline, quote, case, search, dashboards) have explicit mobile guarantees and breakpoint checks.
- Result: ✅ Pass.

### 10) Cross-surface consistency and re-check
- Shared foundations (tokens/layout/state patterns) + role-based UI section resolution + role-gated dashboards + workflow/admin guardrails form a consistent operational model.
- Re-check executed with focused unit suite spanning dashboards, support, marketing, admin, workflow engine, and role-based UI.
- Result: ✅ Pass.

## Fix / Re-check loop
- Issues found: none requiring patch-level model changes.
- Re-check completed with test verification across relevant modules.

## Final score
- Score: **10/10**
- Output: **PASS**
