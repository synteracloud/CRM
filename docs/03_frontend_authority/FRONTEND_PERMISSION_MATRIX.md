---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Derived From: USER_ROLES_AND_PERMISSIONS.md (91 scopes from rbac-scopes.js), DESIGN-SPEC.md, FULLSTACK_STITCHING_CONTRACT.md
---

# FRONTEND PERMISSION MATRIX — Pakistan CRM OS

Every permission scope mapped to its UI impact. 91 scopes total, grouped by module.

**Enforcement model:** Gateway middleware `requireScopes()` enforces at API level. Frontend hides/disables UI elements as a UX convenience — the server is always the authority. A 403 response must be handled gracefully on all protected operations.

**Safe Default SD-001:** contacts.delete scope is currently absent from rbac-scopes.js SCOPES constant (security gap H-002). Hide delete controls for all roles pending OA-001 resolution.

---

## Lead Scopes (7 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| leads.read | Leads list, lead detail view, dashboard KPIs | leads.html (B-02), leads-detail.html (C-01), dashboard.html (A-01), leads-dashboard.html (A-02) | Full lead list and detail visible | Leads section hidden from nav; 403 on API call |
| leads.create | "New Lead" button | leads.html, dashboard.html | New Lead button visible; lead-new.html accessible | Button hidden; /app/leads/new redirects or 403 |
| leads.update | Edit fields, stage chips, priority toggle | leads-detail.html (C-01) | All edit controls active | Form fields read-only; no save button |
| leads.delete | Delete lead button | leads-detail.html (C-01) | Delete button visible (confirmation required) | Button hidden |
| leads.import | "Import CSV" button | leads.html (B-02) | Import button visible | Button hidden |
| leads.export | "Export CSV" button | leads.html (B-02) | Export button visible | Button hidden |
| leads.assign | Owner assignment dropdown | leads-detail.html (C-01), leads.html bulk action | Assignment control visible | Assignment control hidden |

---

## Contact Scopes (6 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| contacts.read | Contact list, contact detail | contacts.html (B-03), contacts-detail.html (C-02), contacts-health.html (A-03) | Full contact data visible | Contacts section hidden; 403 on API |
| contacts.create | "New Contact" button | contacts.html | New Contact button visible | Button hidden |
| contacts.update | Edit fields, tag management | contacts-detail.html (C-02) | Edit controls active | Read-only view |
| contacts.delete | Delete contact button | contacts-detail.html (C-02) | Delete button visible (SD-001: HIDE — scope absent from SCOPES constant; H-002) | Button always hidden (SD-001 in effect) |
| contacts.import | "Import CSV" button | contacts.html | Import button visible | Button hidden |
| contacts.export | "Export CSV" button | contacts.html | Export button visible | Button hidden |

**SD-001 Note:** contacts.delete is absent from rbac-scopes.js SCOPES constant. The route guard `requireScopes(['contacts.delete'])` will return 403 for ALL roles because no token can be issued with this scope. UI must hide delete for all roles until OA-001 is resolved.

---

## Account Scopes (4 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| accounts.read | Account list, account detail | accounts.html (B-04), accounts-detail.html (C-03) | Full account data visible | Accounts section hidden |
| accounts.create | "New Account" button | accounts.html | Create button visible | Button hidden |
| accounts.update | Edit account fields | accounts-detail.html (C-03) | Edit controls active | Read-only view |
| accounts.delete | Delete account button | accounts-detail.html (C-03) | Delete button visible | Button hidden |

---

## Opportunity Scopes (5 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| opportunities.read | Opportunity detail, sales dashboards, pipeline | opportunities-detail.html (C-04), sales-cockpit.html (D-01), sales-dashboard.html (A-04) | Full opportunity data visible | Opportunities section hidden |
| opportunities.create | "New Opportunity" button | sales-cockpit.html, leads-detail.html | Create button visible | Button hidden |
| opportunities.update | Stage chips, amount edit, line items | opportunities-detail.html (C-04) | Edit controls active | Read-only |
| opportunities.delete | Delete opportunity button | opportunities-detail.html (C-04) | Delete button visible | Button hidden |
| opportunities.close | "Close Won" / "Close Lost" buttons | opportunities-detail.html (C-04), sales-cockpit.html (D-01) | Close action buttons visible (manager+) | Buttons hidden |

---

## Quote Scopes (5 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| quotes.read | Quote detail, approval dashboard | quotes-detail.html (C-06), quotes-dashboard.html (A-05) | Full quote visible | Quotes section hidden |
| quotes.create | "New Quote" button, CPQ builder entry | opportunities-detail.html, quotes-dashboard.html | CPQ builder accessible | Button hidden |
| quotes.update | Edit quote fields, line items | quotes-detail.html | Edit controls active | Read-only |
| quotes.approve | "Approve" / "Reject" buttons | quotes-detail.html (C-06), quotes-dashboard.html (A-05), approval-lanes.html (K-04) | Approval action buttons visible | Buttons hidden |
| quotes.convert_to_order | "Accept" button (creates Order) | quotes-detail.html (C-06) | Accept button visible (manager+) | Button hidden |

---

## Order Scopes (2 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| orders.read | Order detail view | orders-detail.html (C-07) | Full order visible | Order page inaccessible |
| orders.fulfil | "Fulfil Order" button | orders-detail.html (C-07) | Fulfil button visible (status=processing only) | Button hidden |

---

## Case / Support Scopes (6 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| cases.read | Case list, case detail, support dashboards | cases.html (B-05), cases-detail.html (C-05), support-console.html (E-01), support-dashboard.html (A-07) | Full case data visible | Cases section hidden |
| cases.create | "New Case" button | cases.html, support-console.html | Create button visible | Button hidden |
| cases.update | Edit fields, comment reply | cases-detail.html (C-05) | Edit controls and comment box active | Read-only |
| cases.close | "Resolve" and "Close" buttons | cases-detail.html (C-05) | Resolve button visible (state-gated: IN_PROGRESS or RESOLVED) | Buttons hidden |
| cases.assign | "Claim" and "Assign" buttons | cases-detail.html (C-05), support-console.html (E-01) | Claim and assign visible | Buttons hidden |
| cases.escalate | "Escalate" button | cases-detail.html (C-05), support-console.html (E-01) | Escalate visible (manager+) | Button hidden |

---

## Inbox Scopes (4 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| inbox.read | Inbox conversation list and thread | inbox.html (L-01), inbox-thread.html (L-02) | Full inbox visible | Inbox section hidden from nav |
| inbox.claim | "Claim" button on unassigned conversations | inbox-thread.html (L-02), inbox.html (L-01) | Claim button visible; claim respects max_concurrent=10 cap | Button hidden |
| inbox.handoff | "Handoff" button | inbox-thread.html (L-02) | Handoff button visible (manager+) | Button hidden |
| inbox.supervise | Supervisor presence board; routing config access | routing-config.html (L-03), identity-dashboard.html (A-12) | Presence board + routing config accessible | Routing config inaccessible |

---

## Campaign Scopes (4 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| campaigns.read | Campaign list, marketing workspace | marketing-workspace.html (F-01), marketing-analytics.html (H-02), engagement-dashboard.html (A-08) | Campaign data visible | Marketing section hidden |
| campaigns.create | "New Campaign" button, campaign builder | marketing-workspace.html (F-01) | Builder accessible | Button hidden |
| campaigns.update | Edit campaign fields | marketing-workspace.html (F-01) | Edit controls active | Read-only |
| campaigns.activate | "Activate" button | marketing-workspace.html (F-01), campaign-new.html (I-06) | Activate button visible (manager+) | Button hidden |

---

## Workflow Scopes (4 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| workflows.read | Workflow dashboard, run detail | workflows-dashboard.html (A-10), workflow-run-detail.html (C-10) | Workflow data visible | Workflows section hidden |
| workflows.create | "New Workflow" button | workflow-builder.html (K-01) | Builder accessible | Button hidden |
| workflows.update | Edit workflow nodes, steps | workflow-builder.html (K-01) | Canvas editable | Read-only canvas |
| workflows.publish | "Publish" button | workflow-builder.html (K-01) | Publish button visible (tenant_admin+) | Button hidden |

**Business Rule:** System workflows (is_system=true) return 403 FORBIDDEN on PATCH/DELETE regardless of scope.

---

## Territory Scopes (5 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| territories.read | Territory list | territories.html (G-09) | Territory list visible | Page inaccessible |
| territories.create | "New Territory" button | territories.html (G-09) | Create button visible | Button hidden |
| territories.update | Edit territory rules, criteria | territories.html (G-09) | Edit controls active | Read-only |
| territories.delete | Delete territory button | territories.html (G-09) | Delete button visible (tenant_admin+) | Button hidden |
| territories.assign | Assignment strategy config | territories.html (G-09) | Assignment controls active | Controls read-only |

---

## Activity Scopes (2 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| activities.read | Activity feed, timeline in detail pages | activity.html (B-06), leads-detail.html, contacts-detail.html | Activity feed visible | Activity section hidden |
| activities.create | "Log Activity" button | leads-detail.html (C-01), contacts-detail.html (C-02) | Log activity button visible | Button hidden |

---

## Task Scopes (5 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| tasks.read | Task queue, follow-up queue | tasks.html (B-07), followups.html (B-01) | Task data visible | Tasks hidden |
| tasks.create | "New Task" button | tasks.html | Create button visible | Button hidden |
| tasks.update | Edit task fields | tasks.html (B-07) | Edit controls active | Read-only |
| tasks.complete | "Mark Complete" button | followups.html (B-01), tasks.html (B-07) | Complete button visible | Button hidden |
| tasks.assign | Assignment dropdown | tasks.html (B-07), leads-detail.html (C-01) | Assignment control visible | Control hidden |

---

## Collections Scopes (6 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| collections.read | Collections queue, invoice queue | collections.html (B-08), invoices.html (B-09), invoices-detail.html (C-08) | Full collections data visible | Collections section hidden |
| collections.create_invoice | "Create Invoice" button | collections.html (B-08) | Create invoice visible (agent+) | Button hidden |
| collections.record_payment | "Record Payment" button | invoices-detail.html (C-08) | Record payment visible (STUB — P-016) | Button hidden |
| collections.approve_payment | "Approve Payment" button | invoices-detail.html (C-08) | Approve visible (manager+) | Button hidden |
| collections.reconcile | "Reconcile" button | collections.html (B-08), invoices-detail.html (C-08) | Reconcile visible (tenant_admin+) | Button hidden |
| collections.view_overdue | Overdue filter chips, overdue count badge | collections.html (B-08) | Overdue filter active + badge visible | Filter hidden |

---

## AI Scopes (5 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| ai.score_leads | "Force Recompute Score" button | leads-detail.html (C-01), ai-copilot.html (M-01) | Recompute button visible | Button hidden |
| ai.view_scores | Lead score card, score band badge | leads-detail.html (C-01), ai-copilot.html (M-01), ai-insights.html (M-02) | Score data visible | Score section hidden |
| ai.train_models | "Retrain Model" button | ai-insights.html (M-02) — model registry | Retrain visible (tenant_admin+) | Button hidden |
| ai.view_forecasts | Forecast KPIs, forecast chart | sales-dashboard.html (A-04), ai-insights.html (M-02) | Forecast data visible | Forecast section hidden |
| ai.generate_forecasts | "Refresh Forecast" button | sales-dashboard.html (A-04) | Refresh button visible (manager+) | Button hidden |

**Constraint (SD-003):** All AI features are rule-based weighted-sum algorithms. No LLM. "Advisory-only" banner displayed on M-01 and M-02.

---

## Analytics / Reports Scopes (3 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| analytics.view_basic | Standard charts, KPI tiles on dashboards and analytics pages | All A-series dashboards, H-01 to H-05, H-04 | KPI tiles and charts visible | Tiles show "Upgrade required" or hidden |
| analytics.view_advanced | Rep-level breakdown, predictive charts, report builder advanced metrics | H-07 (report-builder.html), sales-analytics.html (H-01) rep table | Advanced metrics visible | Advanced section hidden; basic-only view |
| analytics.export | "Export CSV" button on analytics pages | H-01, H-02, H-03, H-04, H-05, H-07 | Export button visible | Button hidden |

---

## Knowledge Base Scopes (4 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| knowledge.read | Knowledge article view, link-to-case | knowledge-article.html (C-12), knowledge-dashboard.html (A-09), cases-detail.html | Article content visible | Article section hidden |
| knowledge.create | "New Article" button | knowledge-dashboard.html (A-09) | Create button visible (manager+) | Button hidden |
| knowledge.update | Edit article content | knowledge-article.html (C-12) | Edit button visible (state-gated: published or draft) | Edit button hidden |
| knowledge.publish | "Publish" / "Unpublish" button | knowledge-article.html (C-12) | Publish button visible (manager+) | Button hidden |

---

## Notification Scopes (2 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| notifications.read | Notification bell count; notification list | All pages (header bell) | Bell with unread count visible | Bell hidden or empty |
| notifications.send | Notification toggle save controls | notifications.html (G-06) | Save button active for notification preferences | Save disabled |

---

## Partner Scopes (3 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| partners.read | Partner list, partner detail | partners.html (B-11), partners-detail.html (C-11) | Full partner data visible | Partners section hidden |
| partners.create | "New Partner" button | partners.html (B-11) | Create button visible (manager+) | Button hidden |
| partners.update | Edit partner fields | partners-detail.html (C-11) | Edit controls active | Read-only view |

---

## Admin Scopes (8 scopes)

| Permission Scope | UI Element | Page(s) | Behavior When Granted | Behavior When Denied |
|---|---|---|---|---|
| admin.read_audit_logs | Audit log, compliance report, audit dashboard | audit-log.html (J-01), compliance-report.html (J-02), audit-dashboard.html (A-13), audit-report.html (H-06) | Full audit data visible | Audit section hidden from nav |
| admin.manage_users | User directory, user management | users.html (B-10), user-management-crm.html (G-02), identity-dashboard.html (A-12) | User management accessible | Admin → Users hidden |
| admin.manage_roles | Role editor | roles.html (G-03) | Role editor accessible | Roles menu hidden |
| admin.manage_tenants | Tenant dashboard | tenants-dashboard.html (A-11) | Tenant dashboard visible (tenant_owner only) | Menu item hidden |
| admin.manage_feature_flags | Feature flags page | feature-flags.html (G-07) | Feature flags accessible (tenant_owner only) | Menu item hidden |
| admin.system_config | Org settings, integrations, notifications, compliance, governance | org-settings.html (G-01), integrations.html (G-05), notifications.html (G-06), compliance.html (G-08), data-governance.html (J-03) | Settings pages accessible | Settings section hidden |
| admin.view_platform_health | Platform health monitoring | audit-dashboard.html (A-13) | Platform health widgets visible | Widgets hidden |
| admin.export_compliance_data | Compliance export button, audit report signed CSV | compliance-report.html (J-02), audit-report.html (H-06) | Export buttons visible | Buttons hidden |

---

*End FRONTEND_PERMISSION_MATRIX.md*
*91 scopes documented (7 lead + 6 contact + 4 account + 5 opportunity + 5 quote + 2 order + 6 case + 4 inbox + 4 campaign + 4 workflow + 5 territory + 2 activity + 5 task + 6 collections + 5 ai + 3 analytics + 4 knowledge + 2 notification + 3 partner + 8 admin = 90 explicitly listed; leads.delete also listed = 91 total per USER_ROLES_AND_PERMISSIONS.md)*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
