---
Status: Active
Authority Level: Critical
Created: 2026-06-23
Derived From: DESIGN-SPEC.md §3 Archetype A, FEATURE_SCOPE.md, API_CONTRACT.md, DOMAIN_MODEL.md
---

# FRONTEND DASHBOARD CATALOG — Pakistan CRM OS

All 13 Archetype A dashboard pages documented in full. Each dashboard is the primary KPI entry point for its domain module.

**Spec:** docs/b9-p01-dashboard-kpi.md
**5-Zone Layout (all dashboards):** posture strip → primary KPI cards → execution queue → trend chart → risk/anomaly panel

---

## A-01 — Owner / Sales Dashboard

**File:** dashboard.html
**Route:** /app/dashboard
**Target Role(s):** tenant_owner, tenant_admin, manager (primary); all roles post-login
**Description:** Executive entry point. Business posture at a glance — follow-up compliance, pipeline health, revenue momentum, risk flags.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Follow-up compliance | GET /followups | % completed this week |
| Idle leads count | GET /leads (status=idle) | Count of leads with no activity 7+ days |
| Pipeline value (PKR) | GET /forecasts | Weighted pipeline total |
| Open opportunities | GET /opportunities | Count active deals |
| Deals at risk | GET /ai/copilot/suggestions (type=stale_deal) | Count of stale deal alerts |
| Follow-up overdue | GET /followups (state=overdue) | Count overdue tasks |

**Posture Strip:** Follow-up compliance score (green/amber/red based on % overdue)

**Execution Queue:** Top 5 overdue follow-ups — lead name, owner, due date, escalation badge

**Trend Chart:** Pipeline value vs. closed won over last 30 days (line chart)

**Risk / Anomaly Panel:** AI Copilot suggestions (urgent/high priority only) — leads at risk, SLA breaches, delinquent payments

**Permissions Required:** leads.read, opportunities.read, analytics.view_basic, ai.view_scores

**Actions Available:**
- "Go to Follow-up Queue" → followups.html
- "View Lead Queue" → leads.html
- "View Pipeline" → sales-cockpit.html
- Click on risk flag → leads-detail.html or cases-detail.html

**Navigation Paths:**
- Entry: Direct URL after login (default landing page)
- Entry: Sidebar home icon
- Exit: Any sidebar nav item; any queue link

**Pakistan-Market:** Pipeline value in PKR with lakh/crore notation. WhatsApp activity counts included in follow-up compliance metric.

---

## A-02 — Lead Funnel Dashboard

**File:** leads-dashboard.html
**Route:** /app/sales/leads/dashboard
**Target Role(s):** All CRM roles
**Description:** Lead pipeline funnel visualization — stage distribution, conversion rates, idle counts.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Total active leads | GET /leads | Count (status=open/working) |
| New this week | GET /leads (created_at filter) | Count |
| Stage distribution | GET /leads | Count per stage |
| Conversion rate (new→won) | GET /leads | (won count / total) % |
| Average time in stage | GET /leads (updated_at delta) | Days |

**Posture Strip:** Idle lead count (leads with no follow-up activity 7+ days)

**Execution Queue:** Top 5 idle leads — most days without activity

**Trend Chart:** Funnel chart — leads per stage (new→qualifying→nurturing→proposal→negotiation→won/lost)

**Risk Panel:** Leads stuck in stage 14+ days without update

**Permissions Required:** leads.read

**Actions Available:**
- Navigate to lead queue (filtered by stage)
- Navigate to follow-up queue
- Create new lead

**Pakistan-Market:** Lead source breakdown includes WhatsApp (primary), web, import, manual, referral, campaign.

---

## A-03 — Customer Health Dashboard

**File:** contacts-health.html
**Route:** /app/contacts/health
**Target Role(s):** manager, tenant_admin
**Description:** Contact base health — completeness scores, open cases, idle contacts.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Total contacts | GET /contacts | Count |
| Avg completeness score | GET /contacts | Mean completeness_score (0–100) |
| Contacts with open cases | GET /contacts + GET /cases | Count where open_cases > 0 |
| Idle contacts (no touchpoint 30d) | GET /contacts | Count where last_touchpoint > 30 days ago |
| Missing phone (E.164) | GET /contacts | Count where phone_e164 null/invalid |

**Posture Strip:** Overall completeness health (avg completeness_score, green/amber/red thresholds)

**Execution Queue:** Bottom 10 contacts by completeness_score (lowest first) — click to edit

**Trend Chart:** Completeness score distribution (histogram or bar chart — 0–20, 21–40, 41–60, 61–80, 81–100 buckets)

**Risk Panel:** Contacts with open_cases > 3 or last_touchpoint > 60 days

**Permissions Required:** contacts.read, cases.read

**Actions Available:**
- Navigate to contact list (filtered by completeness)
- Navigate to case queue (filtered by contact)

---

## A-04 — Opportunity Pipeline Dashboard

**File:** sales-dashboard.html
**Route:** /app/sales/dashboard
**Target Role(s):** manager, tenant_admin, tenant_owner
**Description:** Deal pipeline health — forecast categories, stage funnel, rep performance, win rate.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Weighted pipeline (PKR) | GET /forecasts | weighted_value (sum of amount × category_weight) |
| Commit forecast (PKR) | GET /forecasts | by_category.commit |
| Win rate (MTD) | GET /opportunities | closed_won / (closed_won + closed_lost) % |
| Avg deal size (PKR) | GET /opportunities | mean amount (stage=closed_won) |
| Pipeline velocity | Computed | Avg days from qualification to close |

**Posture Strip:** Pipeline coverage ratio (weighted_pipeline / revenue_target)

**Execution Queue:** Deals requiring action this week (probability > 70%, close_date within 14 days)

**Trend Chart (dual):**
- Stage funnel (bar chart by stage with count + PKR value)
- Forecast category donut (pipeline/best_case/commit/closed/omitted)

**Risk Panel:** Stale deals (no stage change 30+ days); deals in negotiation > 60 days

**Permissions Required:** opportunities.read, ai.view_forecasts

**Forecast Category Weights (from forecasting.js):**
- pipeline: 0.25
- best_case: 0.50
- commit: 0.75
- closed: 1.00
- omitted: 0.00

**Stage Weights (from v1-forecasts.routes.js):**
- qualification: 0.10, discovery: 0.20, proposal: 0.40, negotiation: 0.70
- closed_won: 1.00, closed_lost: 0.00

**Pakistan-Market:** All amounts PKR. Lakh/crore notation above 99,999.

---

## A-05 — Quote Approval Dashboard

**File:** quotes-dashboard.html
**Route:** /app/sales/quotes/dashboard
**Target Role(s):** manager, tenant_admin, tenant_owner
**Description:** Pending quote approvals queue — value at risk, discount level, opportunity links.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Pending approvals | GET /quotes (requires_approval=true, status=sent) | Count |
| Total value pending (PKR) | GET /quotes | Sum of amount for pending |
| Approved this week | GET /quotes (status=approved, week filter) | Count |
| Avg discount (pending) | GET /quotes | Mean discount_pct |

**Posture Strip:** Approval backlog age (oldest pending approval in days)

**Execution Queue:** All quotes requiring approval — sorted by created_at DESC. Columns: quote_id, account, amount, discount_pct, age (days pending).

**Trend Chart:** Approval decisions over 30 days (approved vs. rejected bar chart)

**Risk Panel:** Quotes expired (status=expired); high-discount quotes (discount_pct > 20%)

**Permissions Required:** quotes.read, quotes.approve

**Actions Available:**
- Click quote row → quotes-detail.html
- Approve/reject inline (pending approval quotes only)
- Navigate to CPQ builder

**Pakistan-Market:** All quote amounts in PKR.

---

## A-06 — Subscription Revenue Dashboard

**File:** subscriptions-dashboard.html
**Route:** /app/finance/subscriptions/dashboard
**Target Role(s):** manager, tenant_admin, tenant_owner
**Description:** Recurring revenue health — MRR, ARR, churn rate, renewal compliance, delinquent subscriptions.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| MRR (PKR) | GET /subscriptions | Sum of mrr (status=active) |
| ARR (PKR) | GET /subscriptions | Sum of arr (status=active) |
| Churn rate (MTD) | GET /subscriptions | Cancelled / (active + cancelled) % |
| Renewal rate (90d) | GET /subscriptions | Renewals / (renewals + churned) % |
| Delinquent count | GET /subscriptions (status=past_due) | Count |

**Posture Strip:** Delinquency rate (past_due / total active %)

**Execution Queue:** Delinquent subscriptions (status=past_due) — account, days overdue, MRR at risk

**Trend Chart:** Cohort retention chart — monthly MRR by account cohort

**Risk Panel:** Subscriptions due for renewal in next 30 days with churn prediction risk_band=high

**Permissions Required:** analytics.view_basic, collections.view_overdue

**Actions Available:**
- Navigate to subscription detail
- Navigate to collections queue (for delinquent)

**Pakistan-Market:** MRR/ARR in PKR with lakh/crore notation. P-016 stub comment present.

---

## A-07 — Case SLA Operations Dashboard

**File:** support-dashboard.html
**Route:** /app/support/dashboard
**Target Role(s):** manager, tenant_admin
**Description:** SLA compliance command center — breach count, at-risk queue, volume trend.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Active SLA breaches | GET /cases (sla_state=breached) | Count |
| At-risk cases | GET /cases (sla_state=at_risk) | Count |
| Resolution time (avg hours) | GET /cases (status=CLOSED) | Mean time to resolution |
| CSAT score | GET /cases (csat field) | Avg rating (if available) |
| Cases closed today | GET /cases (status=CLOSED, date filter) | Count |

**Posture Strip:** SLA compliance rate (on_track / total %) — green > 90%, amber 75–90%, red < 75%

**Execution Queue:** Top 10 at-risk cases (ordered by sla_resolution_due_at ASC) — case number, priority, sla_tier, agent, minutes remaining

**Trend Chart:** Case volume area chart — new vs. closed vs. escalated over 14 days

**Risk Panel:** Cases with escalation_level > 1; cases awaiting first response > 30 min (tier_1_critical)

**Permissions Required:** cases.read, analytics.view_basic

**Actions Available:**
- Navigate to at-risk case detail
- Navigate to support console
- Navigate to case queue filtered by SLA state

**Pakistan-Market:** WhatsApp-sourced cases are flagged with channel badge. SLA timers in PKT timezone display.

---

## A-08 — Communication Engagement Dashboard

**File:** engagement-dashboard.html
**Route:** /app/marketing/engagement
**Target Role(s):** manager, tenant_admin, tenant_owner
**Description:** WhatsApp and email engagement metrics — delivery, open, reply rates; active campaigns; channel breakdown.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Delivery rate | GET /communications/engagement | delivered / sent % |
| Open rate | GET /communications/engagement | opened / delivered % |
| Reply rate | GET /communications/engagement | replied / delivered % |
| WhatsApp opt-in rate | GET /communications/engagement | opted_in / total_contacts % |
| Active campaigns | GET /campaigns (status=active) | Count |

**Posture Strip:** Overall engagement health (reply_rate threshold green/amber/red)

**Execution Queue:** Active campaigns list — name, channel, sent count, open rate, created_at

**Trend Chart:** Channel engagement bar chart — WhatsApp vs. email vs. SMS delivery/open/reply

**Risk Panel:** Campaigns with delivery rate < 70%; high bounce rate alerts

**Wired:** Yes (2026-05-31 via v1-communications.routes.js)

**Permissions Required:** campaigns.read, analytics.view_basic

**Actions Available:**
- Navigate to campaign detail
- Navigate to marketing workspace
- Navigate to inbox

**Pakistan-Market:** WhatsApp is primary channel — opt-in rate is primary KPI. PTA compliance note where applicable.

---

## A-09 — Knowledge Effectiveness Dashboard

**File:** knowledge-dashboard.html
**Route:** /app/support/knowledge/dashboard
**Target Role(s):** manager, tenant_admin
**Description:** Article usage metrics — deflection rate, stale articles, adoption trend.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Total articles published | GET /knowledge (status=published) | Count |
| Deflection rate | Computed from GET /cases + GET /knowledge link data | % cases resolved via article |
| Stale articles | GET /knowledge (last_updated > 90 days, status=published) | Count |
| Articles linked to cases | GET /knowledge | Count with case links |

**Posture Strip:** Deflection rate (green > 30%, amber 15–30%, red < 15%)

**Execution Queue:** Stale articles — oldest last_published first; click to edit

**Trend Chart:** Adoption trend — articles viewed per week over 8 weeks

**Risk Panel:** High-view articles with stale content; articles with negative feedback count

**Permissions Required:** knowledge.read, analytics.view_basic

**Actions Available:**
- Navigate to article detail
- Publish stale article (knowledge.publish)

---

## A-10 — Workflow Automation Dashboard

**File:** workflows-dashboard.html
**Route:** /app/workflows/dashboard
**Target Role(s):** manager, tenant_admin, tenant_owner
**Description:** Workflow execution health — execution KPIs, failed queue, pass/fail bar chart.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Total executions (7d) | GET /workflows/runs | Count |
| Success rate | GET /workflows/runs | succeeded / total % |
| Failed count | GET /workflows/runs (status=failed) | Count |
| Avg execution time (ms) | GET /workflows/runs | Mean duration |
| Active workflows | GET /workflows (status=active) | Count |

**Posture Strip:** Failure count (red badge if failed > 5 in last 24h)

**Execution Queue:** Failed workflow runs — workflow name, trigger event, failed_at, error summary

**Trend Chart:** Pass/fail bar chart — daily succeeded vs. failed over 14 days

**Risk Panel:** System workflows with repeated failures (WF-001 through WF-005 monitoring)

**Permissions Required:** workflows.read, analytics.view_basic

**Actions Available:**
- Navigate to run detail
- Retry failed execution (workflows.read — retry is on run detail page)
- Navigate to workflow builder

---

## A-11 — Tenant & Entitlement Dashboard

**File:** tenants-dashboard.html
**Route:** /app/admin/tenants
**Target Role(s):** tenant_owner only
**Description:** Platform-wide tenant overview — plan distribution, seat usage, entitlements at limit.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Total tenants | GET /admin/tenants | Count |
| Active tenants (90d) | GET /admin/tenants | Count with recent API calls |
| Entitlements at limit | GET /admin/tenants | Count where seat_used >= seat_limit |
| Revenue (PKR) | Aggregated tenant billing | Total MRR across tenants |

**Posture Strip:** Entitlement pressure (entitlements_at_limit / total %)

**Execution Queue:** Tenants at or over entitlement limits — tenant name, plan, seat_used, seat_limit

**Trend Chart:** Tenant summary table — plan/seat/feature distribution

**Risk Panel:** Tenants with payment overdue; inactive tenants (>30 days no API calls)

**Permissions Required:** admin.manage_tenants (tenant_owner only)

**Actions Available:** Navigate to tenant detail; trigger plan upgrade (if applicable)

---

## A-12 — Identity & Access Posture Dashboard

**File:** identity-dashboard.html
**Route:** /app/admin/identity
**Target Role(s):** tenant_admin, tenant_owner
**Description:** User lifecycle and access posture — role distribution, escalation events, login activity.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Total users | GET /admin/users | Count |
| Active users (7d) | GET /admin/users (last_login_at filter) | Count |
| Suspended users | GET /admin/users (status=suspended) | Count |
| Role distribution | GET /admin/users | Count per role |
| Escalation events (30d) | GET /admin/audit-logs (escalation type) | Count |

**Posture Strip:** Escalation event count (flag if escalations > 5 in 24h)

**Execution Queue:** Recent escalation events — actor, action, entity, timestamp

**Trend Chart:** Login activity chart — daily active users over 30 days

**Risk Panel:** Failed login attempts; privilege escalation events; suspended users with recent activity

**Permissions Required:** admin.read_audit_logs, admin.manage_users

**Actions Available:**
- Navigate to user management
- Navigate to RBAC audit
- Navigate to audit log (filtered by escalation events)

---

## A-13 — Platform Audit & Reliability Dashboard

**File:** audit-dashboard.html
**Route:** /app/admin/audit/dashboard
**Target Role(s):** tenant_admin, tenant_owner
**Description:** Audit event volume and deny-rate monitoring — platform security posture.

**KPI Cards / Widgets:**
| Widget | Data Source | Metric |
|---|---|---|
| Total events (24h) | GET /admin/audit-logs | Count |
| Allow events | GET /admin/audit-logs (outcome=allow) | Count |
| Deny events | GET /admin/audit-logs (outcome=deny) | Count |
| Warn events | GET /admin/audit-logs (outcome=warn) | Count |
| Deny rate | Computed | deny / total % |

**Posture Strip:** Deny event count (red badge if deny > threshold in 1h)

**Execution Queue:** Recent deny events — actor, action, entity, resource, timestamp

**Trend Chart:** Action-type breakdown chart — stacked bar (allow/deny/warn) by hour over 24h

**Risk Panel:** Repeated deny events for same actor (potential brute force or misconfiguration)

**Permissions Required:** admin.read_audit_logs

**Actions Available:**
- Navigate to audit log (full log with filters)
- Navigate to audit report (signed CSV export)
- Navigate to compliance report

---

*End FRONTEND_DASHBOARD_CATALOG.md*
*13 Archetype A dashboard pages documented*
*Pakistan CRM OS — Phase C6 — 2026-06-23*
