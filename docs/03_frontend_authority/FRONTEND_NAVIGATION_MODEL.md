---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Derived From: DESIGN-SPEC.md (routes), USER_ROLES_AND_PERMISSIONS.md (role visibility), FEATURE_SCOPE.md (module structure)
---

# FRONTEND NAVIGATION MODEL — Pakistan CRM OS

Complete navigation structure — primary sidebar, secondary sub-menus, header navigation, and role-based visibility.

**Shell Owner:** crm-shell.js (sidebar, header, footer injection)
**Footer:** Injected by crm-shell.js at runtime via `main.insertAdjacentHTML('afterend', FOOTER_HTML)` — never hardcoded in page HTML

---

## 1. Primary Sidebar Navigation

The sidebar is injected by crm-shell.js. All custom app pages include crm-shell.js and do NOT contain their own `<aside>` elements.

Sidebar uses NexLink `app-menubar-tabs` class pattern.

| # | Menu Item | Icon | Route | Roles Visible | Module |
|---|---|---|---|---|---|
| 1 | Dashboard | home | /app/dashboard | All roles | Core |
| 2 | Follow-ups | bell / clock | /app/followups | All roles | Follow-up Enforcement |
| 3 | Leads | funnel | /app/leads | All roles | Lead Management |
| 4 | Contacts | users | /app/contacts | All roles | Contacts |
| 5 | Accounts | building | /app/accounts | All roles | Accounts |
| 6 | Collections | credit-card | /app/collections | All roles | Finance |
| 7 | Sales ▼ | chart-bar | (sub-menu) | All roles | Sales |
| 8 | Finance ▼ | dollar-sign | (sub-menu) | All roles | Finance |
| 9 | Support ▼ | headset | (sub-menu) | agent+ | Support |
| 10 | Inbox | message-circle | /app/inbox | agent+ | Inbox |
| 11 | Marketing ▼ | megaphone | (sub-menu) | manager+ | Marketing |
| 12 | Workflows ▼ | git-branch | (sub-menu) | manager+ | Workflows |
| 13 | Partners | handshake | /app/partners | All roles | Partners |
| 14 | AI ▼ | cpu | (sub-menu) | All roles | AI |
| 15 | Reports ▼ | bar-chart-2 | (sub-menu) | All roles | Reports |
| 16 | Activity | activity | /app/activity | All roles | Activity |
| 17 | Tasks | check-square | /app/tasks | All roles | Tasks |
| 18 | Admin ▼ | shield | (sub-menu) | tenant_admin, tenant_owner | Admin |
| 19 | Settings ▼ | settings | (sub-menu) | tenant_admin, tenant_owner | Settings |

---

## 2. Secondary Navigation (Sub-menus)

### Sales Sub-menu
| Item | Route | Roles Visible |
|---|---|---|
| Sales Cockpit | /app/sales/cockpit | All roles |
| Pipeline Dashboard | /app/sales/dashboard | All roles |
| Lead Dashboard | /app/sales/leads/dashboard | All roles |
| Quote Dashboard | /app/sales/quotes/dashboard | manager+ |
| Approval Lanes | /app/sales/approval-lanes | manager+ |

### Finance Sub-menu
| Item | Route | Roles Visible |
|---|---|---|
| Invoices | /app/finance/invoices | All roles |
| Subscriptions | /app/finance/subscriptions/dashboard | All roles |

### Support Sub-menu
| Item | Route | Roles Visible |
|---|---|---|
| Cases | /app/support/cases | All roles |
| Console | /app/support/console | agent+ |
| Dashboard | /app/support/dashboard | All roles |
| Knowledge Base | /app/support/knowledge/dashboard | All roles |

### Marketing Sub-menu
| Item | Route | Roles Visible |
|---|---|---|
| Campaigns | /app/marketing/campaigns | manager+ |
| Campaign Builder | /app/marketing/campaigns/new | manager+ |
| Analytics | /app/reports/marketing | All roles |
| Engagement | /app/marketing/engagement | All roles |

### Workflows Sub-menu
| Item | Route | Roles Visible |
|---|---|---|
| Dashboard | /app/workflows/dashboard | All roles |
| Builder | /app/workflows/builder | manager+ |
| Analytics | /app/reports/workflows | manager+ |

### AI Sub-menu
| Item | Route | Roles Visible |
|---|---|---|
| Copilot | /app/ai/copilot | All roles |
| Insights | /app/ai/insights | manager+ |

### Reports Sub-menu
| Item | Route | Roles Visible |
|---|---|---|
| Sales Analytics | /app/reports/sales | All roles |
| Finance Analytics | /app/reports/finance | All roles |
| Support Analytics | /app/reports/support | All roles |
| Workflow Analytics | /app/reports/workflows | manager+ |
| Audit Report | /app/reports/audit | tenant_admin, tenant_owner |
| Report Builder | /app/reports/builder | All roles |

### Admin Sub-menu (tenant_admin + tenant_owner only)
| Item | Route | Roles Visible |
|---|---|---|
| Users | /app/admin/users | tenant_admin, tenant_owner |
| User Management | /app/admin/users/manage | tenant_admin, tenant_owner |
| Roles | /app/admin/roles | tenant_admin, tenant_owner |
| Identity Dashboard | /app/admin/identity | tenant_admin, tenant_owner |
| Feature Flags | /app/admin/feature-flags | tenant_owner only |
| Territories | /app/admin/territories | manager, tenant_admin, tenant_owner |
| Routing | /app/admin/routing | manager, tenant_admin, tenant_owner |
| Governance | /app/admin/governance | tenant_admin, tenant_owner |
| RBAC Audit | /app/admin/rbac-audit | tenant_admin, tenant_owner |
| Objects | /app/admin/objects | tenant_admin, tenant_owner |
| Rules | /app/admin/rules | tenant_admin, tenant_owner |
| Audit Dashboard | /app/admin/audit/dashboard | tenant_admin, tenant_owner |
| Tenants | /app/admin/tenants | tenant_owner only |

### Settings Sub-menu (tenant_admin + tenant_owner only)
| Item | Route | Roles Visible |
|---|---|---|
| Organization | /app/settings/org | tenant_admin, tenant_owner |
| Billing | /app/settings/billing | tenant_admin, tenant_owner |
| Integrations | /app/settings/integrations | tenant_admin, tenant_owner |
| Notifications | /app/settings/notifications | tenant_admin, tenant_owner |
| Compliance | /app/settings/compliance | tenant_admin, tenant_owner |
| Privacy | /app/settings/privacy | tenant_admin, tenant_owner |

---

## 3. Header Navigation

The header is injected by crm-shell.js. Standard header elements across all custom pages:

| Element | Type | Behavior |
|---|---|---|
| App name / Logo | Brand link | Links to /app/dashboard |
| Search | Global search input | Placeholder — no live search API confirmed in C6 scope |
| Notifications bell | Icon button | Shows unread notification count; links to notification list |
| User avatar / name | Dropdown trigger | User menu dropdown |
| User menu: Profile | Link | Links to /profile or user settings |
| User menu: Settings | Link | Links to /app/settings/org (admin) |
| User menu: Logout | Button | Calls DELETE /auth/sessions/current; clears local token; redirects to login |

**SLA Timer (Support Console only):** support-console.html (E-01) has a global SLA timer in its custom header showing oldest active breach countdown.

---

## 4. Role-Based Navigation Visibility

Which navigation sections are visible per role:

| Navigation Section | tenant_owner | tenant_admin | manager | agent | analyst |
|---|---|---|---|---|---|
| Dashboard | Y | Y | Y | Y | Y |
| Follow-ups | Y | Y | Y | Y | Y (read-only) |
| Leads | Y | Y | Y | Y | Y (read-only) |
| Contacts | Y | Y | Y | Y | Y (read-only) |
| Accounts | Y | Y | Y | Y | Y (read-only) |
| Collections | Y | Y | Y | Y | Y (read-only) |
| Sales sub-menu | Y | Y | Y | Y | Y (read-only) |
| Finance sub-menu | Y | Y | Y | N | Y (read-only) |
| Support sub-menu | Y | Y | Y | Y | Y (read-only) |
| Inbox | Y | Y | Y | Y | N |
| Marketing sub-menu | Y | Y | Y | N | N |
| Workflows sub-menu | Y | Y | Y | N | N |
| Partners | Y | Y | Y | Y | Y (read-only) |
| AI sub-menu | Y | Y | Y | Y | Y (read-only) |
| Reports sub-menu | Y | Y | Y | Y | Y (basic) |
| Activity | Y | Y | Y | Y | Y |
| Tasks | Y | Y | Y | Y | Y (read-only) |
| Admin sub-menu | Y | Y | N | N | N |
| Settings sub-menu | Y | Y | N | N | N |

Note: Admin and Settings sub-menus are only visible to tenant_admin and tenant_owner. The "Tenants" menu item within Admin is only visible to tenant_owner.

---

## 5. Navigation Entry Points Per Module

Key entry points for each major module:

| Module | Primary Entry | Secondary Entry | Deep-link Pattern |
|---|---|---|---|
| Lead Management | Sidebar "Leads" | Dashboard queue links | /app/leads/:lead_id |
| Follow-up Enforcement | Sidebar "Follow-ups" | Dashboard "Go to Queue" | /app/followups |
| Contacts | Sidebar "Contacts" | Lead detail "View Contact" | /app/contacts/:id/360 |
| Accounts | Sidebar "Accounts" | Contact detail "Account" | /app/accounts/:id |
| Sales / Opportunities | Sidebar "Sales" → "Cockpit" | Lead detail "Convert to Deal" | /app/opportunities/:id |
| CPQ / Quotes | Sales → "Quote Dashboard" | Opportunity detail "New Quote" | /app/sales/quotes/:id |
| Finance / Collections | Sidebar "Collections" | Dashboard risk panel | /app/finance/invoices/:id |
| Support / Cases | Sidebar "Support" → "Cases" | Dashboard "At Risk" queue | /app/support/cases/:id |
| Inbox | Sidebar "Inbox" | Support console thread select | /app/inbox/:thread_id |
| Marketing | Sidebar "Marketing" → "Campaigns" | Engagement dashboard | /app/marketing/campaigns |
| Workflows | Sidebar "Workflows" → "Dashboard" | Admin tools | /app/workflows/runs/:id |
| AI | Sidebar "AI" → "Copilot" | Lead detail score panel | /app/ai/copilot |
| Reports | Sidebar "Reports" | Dashboard "View Analytics" | /app/reports/sales |
| Admin | Sidebar "Admin" | Settings shortcuts | /app/admin/users |
| Settings | Sidebar "Settings" | User menu "Settings" | /app/settings/org |

---

## 6. Breadcrumb Pattern

All custom pages use NexLink breadcrumb components for orientation:

| Pattern | Example |
|---|---|
| Single level | Dashboard |
| Two levels | Leads > Lead Detail |
| Three levels | Sales > Quotes > Quote #Q-2026-001 |
| Settings | Settings > Organization |
| Admin | Admin > Users > User Management |

---

## 7. Mobile Navigation

Per DESIGN-SPEC.md §2 C-003:
- All pages must be usable on 360px viewport
- WhatsApp is the primary mobile surface
- P0 actions (create lead, mark follow-up complete, reply to case) must be reachable in ≤2 taps on mobile
- Sidebar collapses to hamburger menu on mobile
- Bottom tab bar for core actions on mobile (if implemented in crm-shell.js)

---

*End FRONTEND_NAVIGATION_MODEL.md*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
