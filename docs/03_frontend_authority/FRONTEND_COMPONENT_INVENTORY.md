---
Status: Active
Authority Level: Reference
Created: 2026-06-23
Derived From: CLAUDE.md (build rules), FRAMEWORK.md §31, DESIGN-SPEC.md §2, DETERMINISM_CERTIFICATION_REPORT.md
---

# FRONTEND COMPONENT INVENTORY — Pakistan CRM OS

Reusable frontend components and patterns across the 75 custom pages.

---

## 1. Shell Components (crm-shell.js)

crm-shell.js is the mandatory shell script for all 75 custom CRM pages. It is NOT present on NexLink library pages.

### What crm-shell.js Provides

| Component | Description | Key Rule |
|---|---|---|
| Sidebar / `<aside class="app-menubar-tabs">` | Primary navigation sidebar with CRM menu structure | Never hardcode `<aside>` in page HTML — shell owns it |
| Header / `<header class="app-header">` | Application header with logo, search, notifications, user menu | Never hardcode `<header>` in page HTML |
| Footer injection | `main.insertAdjacentHTML('afterend', FOOTER_HTML)` at line 532 | Never hardcode `<footer>` in page HTML — double footer bug |
| Active nav highlighting | Sets `active` class on sidebar link matching current URL | No page action needed |
| Mobile menu toggle | Hamburger collapse for mobile viewports | Built into shell |
| Page title update | Sets `<title>` from page `data-title` attribute | Set data-title on `<main>` |

### Shell Script Stack (all custom pages)
```html
<script src="assets/js/vendors/jquery.min.js"></script>
<script src="assets/js/vendors/bootstrap.bundle.min.js"></script>
<script src="assets/js/app/crm-shell.js"></script>
<script src="assets/js/app/crm-api.js"></script>
<script src="assets/js/app/crm-dummy.js"></script>
<script src="assets/js/app/crm-<pagename>.js"></script>
```

### Required `<main>` Structure
```html
<main class="app-main">
  <div class="container-fluid">
    <!-- page content -->
  </div>
</main>
```

---

## 2. CSS Framework Stack

### Required `<head>` links (all custom pages)
```html
<link rel="stylesheet" href="assets/css/styles.css">
<link rel="stylesheet" href="assets/css/crm-custom.css">
```

**crm-custom.css MUST be present on every custom page.** Missing it causes DataTable header misalignment.

### CSS Components Available

| Component | Source | Class Pattern |
|---|---|---|
| Base layout | NexLink styles.css | `.app-main`, `.app-header`, `.app-menubar-tabs` |
| Grid | Bootstrap 5 (via NexLink) | `.row`, `.col-*` |
| Cards | NexLink | `.card`, `.card-body`, `.card-header` |
| Badges | Bootstrap | `.badge`, `.bg-*` |
| Filter pills | NexLink nav-pills-custom | `.nav-pills-custom.rounded-5` |
| Tables | Bootstrap | `.table`, `.table-responsive` |
| DataTables | DataTables v2 | `.dataTable`, `dt-head-*`, `dt-body-*` |
| Icons | Lucide / Flaticon | `<i data-lucide="name">` |
| RTL | crm-locale.js | `dir="rtl"` on `<html>` |
| Modals | Bootstrap | `.modal`, `.modal-dialog` |
| Toasts | Bootstrap | `.toast-container`, `.toast` |
| Spinners | Bootstrap | `.spinner-border` |

### NexLink Card Fixed Height Rule (CLAUDE.md §3)
NexLink `.card` defaults to `height: calc(100% - var(--bs-gutter-x))`. Override required in 3 patterns:

| Pattern | When | Fix |
|---|---|---|
| A — Identity strip / col-12 single card | Full-width standalone card | `style="height:auto"` on `.card` |
| B — Multiple stacked cards in same column | 2+ cards in col-lg-9 or similar | `style="height:auto"` on EVERY card |
| C — Context panel cards (col-lg-4 sidebar) | All context panel cards in detail pages | `style="height:auto"` on EVERY card |

---

## 3. crm-api.js — API Client

**Location:** `frontend/src/assets/js/app/crm-api.js`
**DUMMY_MODE:** false (set in C1 — live API on all 75 pages)

### What crm-api.js Provides

| Function | Description |
|---|---|
| `CRM_API.get(path, params)` | GET request with JWT Bearer token |
| `CRM_API.post(path, body)` | POST with Idempotency-Key generation |
| `CRM_API.patch(path, body)` | PATCH with JWT Bearer token |
| `CRM_API.delete(path)` | DELETE with JWT Bearer token |
| Token management | Reads `accessToken` from localStorage or memory |
| Token refresh | Silent refresh via POST /auth/refresh on 401 |
| Graceful fallback | On API error, falls back to crm-dummy.js data |
| Error handling | Logs error; shows toast notification |

### Required Header Pattern
```javascript
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json',
  'Idempotency-Key': generateUUID()  // Required on all POST/PUT/PATCH
}
```

---

## 4. crm-dummy.js — Fallback Data

**Location:** `frontend/src/assets/js/app/crm-dummy.js`
**Usage:** Graceful fallback when API is unavailable (not primary source — DUMMY_MODE: false)

### CRM_DUMMY Data Namespaces Available

| Namespace | Description |
|---|---|
| `CRM_DUMMY.leads` | Lead records array |
| `CRM_DUMMY.leadFunnelKpi` | Lead funnel KPI object |
| `CRM_DUMMY.deltas` | KPI delta/trend values |
| `CRM_DUMMY.contacts` | Contact records array |
| `CRM_DUMMY.contactsKpi` | Contact health KPIs |
| `CRM_DUMMY.quotes` | Quote records array |
| `CRM_DUMMY.cases` | Case records array |
| `CRM_DUMMY.caseSlaKpi` | SLA KPI values |
| `CRM_DUMMY.messageThreads` | Conversation thread records |
| `CRM_DUMMY.campaigns` | Campaign records |
| `CRM_DUMMY.knowledgeArticles` | Knowledge article records |
| `CRM_DUMMY.knowledgeKpi` | Knowledge effectiveness KPIs |
| `CRM_DUMMY.workflowExecutions` | Workflow execution records |
| `CRM_DUMMY.workflowKpi` | Workflow performance KPIs |
| `CRM_DUMMY.tenantKpi` | Tenant entitlement KPIs |
| `CRM_DUMMY.AUDIT_LOG` | Audit log entries |
| `CRM_DUMMY.users` | User records with roles |
| `CRM_DUMMY.roles` | Role definitions |
| `CRM_DUMMY.rbacAssignmentLog` | RBAC assignment events |
| `CRM_DUMMY.featureFlags` | Feature flag registry |
| `CRM_DUMMY.territories` | Territory and rule records |
| `CRM_DUMMY.ACCOUNTS` | Account records |
| `CRM_DUMMY.INVOICES` | Invoice records |
| `CRM_DUMMY.SUBSCRIPTIONS` | Subscription records |
| `CRM_DUMMY.ORDERS` | Order records |
| `CRM_DUMMY.partners` | Partner records |

---

## 5. DataTables v2 Instances

All data-driven tables use DataTables v2. Every table requires alignment in THREE places (CLAUDE.md §2).

### Active DataTable IDs (75 custom pages)

| Table ID | Page | Description |
|---|---|---|
| `dt_Followups` | followups.html (B-01) | Follow-up task queue |
| `dt_ScrollVertical` (leads) | leads.html (B-02) | Lead queue with vertical scroll |
| `dt_Contacts` | contacts.html (B-03) | Contact list |
| `dt_Accounts` | accounts.html (B-04) | Account list |
| `dt_Cases` | cases.html (B-05) | Case queue |
| `dt_Activity` | activity.html (B-06) | Activity feed |
| `dt_Tasks` | tasks.html (B-07) | Task queue |
| `dt_Collections` | collections.html (B-08) | Collections queue |
| `dt_Invoices` | invoices.html (B-09) | Invoice queue |
| `dt_Users` | users.html (B-10) | User directory |
| `dt_Partners` | partners.html (B-11) | Partner list |
| Per-page detail tables | All C-series pages | Activity timeline, line items, history tabs |
| `dt_AuditLog` | audit-log.html (J-01) | Audit event list |
| `dt_WorkflowRuns` | workflows-dashboard.html (A-10) | Execution queue |
| `dt_Executions` | workflow-analytics.html (H-05) | Analytics DataTable |
| Various analytics tables | H-01 through H-05 | Rep performance, cases, campaigns tables |

### DataTable Alignment Rule (CLAUDE.md §2 — THREE places required)

**Place 1 — HTML thead:**
```html
<th class="dt-head-center">Column Name</th>
<!-- ALL headers must be dt-head-center — no exceptions -->
```

**Place 2 — JS column definition:**
```javascript
{ data: 'field', className: 'dt-body-center' }
// dt-body-left: long text, titles
// dt-body-center: names, dates, badges, IDs, status
// dt-body-right: PKR amounts, numeric totals
```

**Place 3 — crm-custom.css:**
```css
#dt_TableName.dataTable tbody > tr > td { text-align: center !important; }
#dt_TableName.dataTable tbody > tr > td:nth-child(N) { text-align: left !important; }
```

---

## 6. Chart / KPI Components

### ApexCharts Instances (primary charting library)

| Chart Type | Pages | Description |
|---|---|---|
| Bar chart | A-07 (SLA breach), A-08 (channel), A-10 (pass/fail), H-01, H-02, H-03, H-05 | Column/bar distribution charts |
| Line chart | A-07 (case volume), H-01 (trend), H-02 (WhatsApp trend) | Time-series trend lines |
| Donut chart | A-04 (forecast category), H-03 (case volume) | Proportional breakdowns |
| Funnel chart | A-02 (lead stages), H-01 (lead funnel) | Pipeline funnel visualization |
| Area chart | A-07 (case volume trend) | Volume over time |
| Live preview chart | H-07 (report builder) | Dynamic chart from report execution |

### KPI Card Pattern (all dashboard pages)

```html
<div class="col-md-3">
  <div class="card mb-0" style="height:auto">
    <div class="card-body">
      <h6 class="card-title text-muted">Metric Name</h6>
      <h2 id="kpi_MetricName" class="fs-3 fw-bold">—</h2>
      <span id="delta_MetricName" class="text-success small">+0%</span>
    </div>
  </div>
</div>
```

All KPI `<h2>` elements must have unique `id` attributes for JS setters (T2 requirement per DESIGN-SPEC.md A-01 notes).

### PKR Formatting Function (crm-components.js)

```javascript
pkr(amount)  // Returns "PKR 1,50,000" (lakh notation) or "PKR 3.25 Cr" (crore notation)
// Rule: NEVER show raw integers for monetary values
// Source: DESIGN-SPEC.md §2 C-004
```

---

## 7. Form Patterns

### 2-Step Wizard Pattern (all Archetype I pages)

```html
<!-- Step 1: Required fields only -->
<div id="step1" class="wizard-step">
  <h6>Step 1 of 2</h6>
  <!-- required fields -->
  <button class="btn btn-primary" onclick="nextStep()">Continue</button>
</div>

<!-- Step 2: Confirmation + optional extras -->
<div id="step2" class="wizard-step d-none">
  <h6>Step 2 of 2</h6>
  <!-- optional fields or confirmation summary -->
  <button class="btn btn-secondary" onclick="prevStep()">Back</button>
  <button class="btn btn-primary" onclick="submitForm()">Confirm</button>
</div>
```

**Rule:** ≤2 steps enforced (DESIGN-SPEC.md §2 C-002). Every primary user action in ≤2 interactions.

### Phone E.164 Validation Pattern

```javascript
// Used in lead-new.html (I-01), contact-new.html (I-02)
const phoneRegex = /^\+92[0-9]{10}$/;
// Dedup warning on blur when existing contact found with same phone
```

### Settings Two-Pane Layout (all Archetype G pages)

```html
<div class="row">
  <!-- Left nav: list-group (NOT nav-pills — see CLAUDE.md §4) -->
  <div class="col-lg-3">
    <div class="list-group list-group-flush">
      <a class="list-group-item list-group-item-action active" href="org-settings.html">Organization</a>
      <a class="list-group-item list-group-item-action" href="billing-settings.html">Billing</a>
      <!-- ... shared settings nav items ... -->
    </div>
  </div>
  <!-- Right content: stacked cards (all must have style="height:auto") -->
  <div class="col-lg-9 pb-4">
    <div class="card mb-3" style="height:auto">...</div>
    <div class="card" style="height:auto">...</div>
  </div>
</div>
```

**Rule (CLAUDE.md §4):** Left nav MUST use `list-group`, NOT `nav-pills`. Using nav-pills inside page body causes NexLink sidebar CSS bleed and content clipping.

---

## 8. Filter Chip Pattern

All tab-style filter strips use the NexLink pill pattern (CLAUDE.md §5):

```html
<ul class="nav nav-pills nav-pills-custom p-1 bg-light rounded-5" id="statusFilter" role="tablist">
  <li class="nav-item">
    <button type="button" class="nav-link rounded-5 active" data-filter="">All</button>
  </li>
  <li class="nav-item">
    <button type="button" class="nav-link rounded-5" data-filter="active">Active</button>
  </li>
</ul>
```

**Rule:** NEVER use `btn-group btn-group-sm + btn-outline-secondary` (produces Bootstrap gray "80s tab" look).

**Filter activation JS pattern:**
```javascript
$('#statusFilter button').on('click', function() {
  $('#statusFilter button').removeClass('active');
  $(this).addClass('active');
  const filterVal = $(this).data('filter');
  table.column(N).search(filterVal).draw();
});
```

---

## 9. Modal Patterns

### Confirm Dialog (2-step destructive actions)

```html
<!-- All destructive operations (delete, suspend, force-close) use confirm modals -->
<div class="modal fade" id="confirmSuspendModal">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5>Confirm Suspend User</h5>
      </div>
      <div class="modal-body">
        <p>Are you sure you want to suspend this user? This action cannot be undone immediately.</p>
      </div>
      <div class="modal-footer">
        <button type="button" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-danger" id="confirmSuspendBtn">Suspend</button>
      </div>
    </div>
  </div>
</div>
```

### 2-Step Invite Modal (user-management-crm.html G-02)
Step 1: Email + role selection
Step 2: Confirmation summary → POST /admin/users/invite

### Dual-Approval Modal (feature-flags.html G-07)
For flags with requires_dual_approval=true: second approver confirmation overlay required before PATCH /feature-flags/:id

---

## 10. Activity Timeline Pattern (Archetype C detail pages)

```html
<div class="timeline">
  <div class="timeline-item" data-activity-type="whatsapp">
    <div class="timeline-icon"><i data-lucide="message-circle"></i></div>
    <div class="timeline-content">
      <span class="timeline-date text-muted">2026-05-29, 14:32 PKT</span>
      <p>WhatsApp message received from contact</p>
    </div>
  </div>
  <!-- ... more events ... -->
</div>
```

Activity types: whatsapp, email, call, meeting, note, status_change, assignment, followup

---

## 11. State-Gated Buttons Pattern (Archetype C entity detail pages)

Buttons that only appear when entity is in the correct state:

```javascript
// cases-detail.html example
function renderCaseActions(caseStatus) {
  document.getElementById('claimBtn').classList.toggle('d-none', caseStatus !== 'OPEN');
  document.getElementById('resolveBtn').classList.toggle('d-none', !['IN_PROGRESS','WAITING_ON_CUSTOMER'].includes(caseStatus));
  document.getElementById('closeBtn').classList.toggle('d-none', caseStatus !== 'RESOLVED');
  document.getElementById('escalateBtn').classList.toggle('d-none', ['CLOSED','RESOLVED'].includes(caseStatus));
}
```

State machines enforced by both UI visibility AND API (422 on invalid transition).

---

## 12. SLA Timer Component (support-console.html E-01, cases-detail.html C-05)

```javascript
// Countdown timer for SLA due dates
function startSlaTimer(dueAt) {
  const interval = setInterval(() => {
    const remaining = new Date(dueAt) - new Date();
    if (remaining <= 0) {
      document.getElementById('slaTimer').textContent = 'BREACHED';
      document.getElementById('slaTimer').classList.add('text-danger');
      clearInterval(interval);
    } else {
      const hours = Math.floor(remaining / 3600000);
      const mins = Math.floor((remaining % 3600000) / 60000);
      document.getElementById('slaTimer').textContent = `${hours}h ${mins}m`;
    }
  }, 60000);
}
```

SLA timer in support-console.html header shows oldest active breach countdown globally.

---

## 13. Common Patterns Across 75 Custom Pages

| Pattern | Pages | Description |
|---|---|---|
| crm-shell.js shell | All 75 | Sidebar + header + footer injection |
| crm-custom.css | All 75 | DataTable header alignment fix |
| ApexCharts | 13 dashboard + 7 analytics | KPI visualization |
| DataTables v2 | All B-series + dashboards | Sortable, filterable tables |
| nav-pills-custom filter chips | B-02 (leads), B-05 (cases), B-08 (collections), B-09 (invoices), F-01 (campaigns), L-01 (inbox) | NexLink pill filter strips |
| Settings two-pane + list-group | All G-series (9 pages) | Settings left-nav pattern |
| 2-step wizard | All I-series (6 pages) | Form with ≤2 steps |
| Sticky identity strip | All C-series (12 pages) | Entity header with key fields |
| Activity timeline | C-01, C-02, C-04 | Entity change history |
| State-gated buttons | C-05 (cases), C-06 (quotes), C-09 (subscriptions), C-10 (workflows), C-12 (knowledge) | Context-dependent action visibility |
| height:auto on cards | C-series context panels, all G-series | NexLink card clip fix |
| PKR formatting pkr() | All finance pages | Currency formatting |
| E.164 phone validation | I-01, I-02 | Phone dedup and format |
| flatpickr date picker | H-02, H-03, H-05 | Date range filter |
| Hash chain verification | J-01 (audit-log), H-06 (audit-report) | Immutable audit trail display |
| Advisory-only banner | M-01, M-02 | AI rule-based advisory disclaimer |

---

*End FRONTEND_COMPONENT_INVENTORY.md*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
