# Pakistan CRM — Screen Progress

**Last updated:** 2026-05-31 — **C0 Environment Seal COMPLETE.** .env.local + seal.ps1 created; npm/pip/Playwright all confirmed writing to D:; Chromium installed at D:\CRM\.playwright-browsers\chromium-1223; c-seal baseline recorded. C1 DB Wiring is next. 5 previously blocked pages (G-04, G-05, J-03, H-07, A-08) wired with inline gateway route stubs + JS drivers. External services (billing provider, integration APIs, governance service) are pluggable later — internal homework complete. Final Hardening (Component 3) is next. ✓ = full process complete + locked.
**Protocol:** FRAMEWORK.md (seed-first normalisation)
**Ground truth for app/ directory:** `frontend/src/app/`
**Dev server:** `npm run serve` from `D:\CRM\frontend` — port 3001 (must run from this directory)
**Python env:** `D:\Python\python.exe` (3.12.10) → venv `D:\CRM\backend\.venv` → fastapi/uvicorn/pydantic installed — zero C: leakage
**Rebuild plan:** `REBUILD-PLAN.md` — 6 phases, ~21 weeks to 10/10. Task checklist: `PENDING.md` (root).

---

## Legend
| Symbol | Meaning |
|--------|---------|
| ✓ | Complete — code-verified + browser sign-off |
| ⏳ | Built — browser sign-off pending |
| 🔨 | In progress |

---

## Completed Screens

| # | Page | Seed | Status | Notes |
|---|------|------|--------|-------|
| 1 | dashboard.html | src/index.html | ✓ | crm-dashboard.js seed-identical. Approved 2026-05-12. |
| 2 | leads.html | src/leads.html | ✓ | crm-leads.js seed-identical. Approved 2026-05-12. |
| 4 | customers.html | src/customers.html | ✓ | crm-customers.js seed-identical. Approved 2026-05-12. |
| 5 | profile.html | src/profile.html | ✓ | Static page — no JS elements. crm-profile.js is a no-op stub. Approved 2026-05-12. |
| 6 | deals.html | src/deals.html | ✓ | crm-deals.js seed-identical. Approved 2026-05-12. |
| 7 | sales.html | src/sales.html | ✓ | crm-sales.js seed-identical. Approved 2026-05-12. |
| 8 | finance.html | src/finance.html | ✓ | crm-finance.js seed-identical. Approved 2026-05-12. |
| 9 | team-management.html | src/team-management.html | ✓ | crm-team-management.js seed-identical. Approved 2026-05-12. |
| 10 | employee.html | src/employee.html | ✓ | crm-employee.js flatpickr init only. Approved 2026-05-12. |
| 11 | review.html | src/review.html | ✓ | crm-review.js seed-identical. autoWidth:false on dt_RecentReviews (avatar img race condition fix). Approved 2026-05-12. |
| 12 | task-management.html | src/task-management.html | ✓ | crm-task-management.js Sortable+flatpickr dual DOMContentLoaded. Approved 2026-05-12. |
| 13 | user-management.html | src/user-management.html | ✓ | crm-user-management.js seed-identical. Modal outside container-fluid preserved. Approved 2026-05-12. |
| 14 | activities.html | src/activities.html | ✓ | crm-activities.js dt_Activities+callsChart+tasksChart+leadsChart. avatar-xxs CSS-constrained, no autoWidth:false. Approved 2026-05-13. |
| 15 | settings.html | src/settings.html | ✓ | Static 8-tab settings form. crm-settings.js no-op stub. Approved 2026-05-13. |
| 16 | marketing.html | src/marketing.html | ✓ | crm-marketing.js 6 charts (4 sparklines+adsTrendChart+leadFunnelChart). Approved 2026-05-13. |
| 17 | calendar.html | src/calendar.html | ✓ | crm-calendar.js no-op stub. plugins/fullcalendar.js handles all logic. flatpickr.min.css included. appsTab (GAP-005). Approved 2026-05-13. |
| 18 | chat.html | src/chat.html | ✓ | Static chat UI. crm-chat.js no-op stub. appsTab (GAP-005). Approved 2026-05-13. |
| 19 | inbox-email.html | src/email/inbox.html | ✓ | crm-inbox-email.js no-op stub. 7 Bootstrap tab panes. appsTab (GAP-005). No flatpickr (§19). Approved 2026-05-13. |
| 20 | email-compose.html | src/email/compose.html | ✓ | crm-email-compose.js no-op stub. tagify lib+plugin. No flatpickr (§19). appsTab (GAP-005). Approved 2026-05-13. |
| 21 | email-read.html | src/email/read-email.html | ✓ | crm-email-read.js no-op stub. Static read view. No flatpickr (§19). appsTab (GAP-005). Approved 2026-05-13. |
| 22 | login-frame.html | src/authentication/login-frame.html | ✓ | Auth page pattern (§12). crm-auth.js. JS redirects use absolute /app/ paths (§12 base-href rule). Approved 2026-05-13. |
| 23 | register-frame.html | src/authentication/register-frame.html | ✓ | Auth page pattern (§12). crm-auth.js. registerForm+registerBtn+registerSpinner+registerError IDs. Approved 2026-05-13. |
| 24 | forgot-password-frame.html | src/authentication/forgot-password-frame.html | ✓ | Native form action→app/new-password-frame.html. No JS intercept (seed has none). Cancel→app/login-frame.html. Approved 2026-05-13. |
| 25 | new-password-frame.html | src/authentication/new-password-frame.html | ✓ | Native form action→app/login-frame.html. No JS intercept (seed has none). Approved 2026-05-13. |
| 26 | error-404.html | src/pages/error-404.html | ✓ | crm-error-404.js stub. Lottie animation (#error002) via lottie.js. crm-shell.js pagesTab updated. Approved 2026-05-13. |
| 27 | pricing.html | src/pages/pricing.html | ✓ | crm-pricing.js monthly/annually toggle (#priceSwitchCheck). crm-shell.js pagesTab updated. Approved 2026-05-13. |
| 28 | under-construction.html | src/pages/under-construction.html | ✓ | crm-under-construction.js stub. Static subscribe form. crm-shell.js pagesTab updated. Approved 2026-05-13. |

---

| 29 | blog.html | src/pages/blog.html | ✓ | crm-blog.js stub. 8-card grid + pagination. Links →app/blog-details.html. crm-shell.js pagesTab updated. Approved 2026-05-13. |
| 30 | blog-list.html | src/pages/blog-list.html | ✓ | crm-blog-list.js stub. List + sidebar (recent posts, categories, tags, gallery). crm-shell.js pagesTab updated. Approved 2026-05-13. |
| 31 | blog-details.html | src/pages/blog-details.html | ✓ | crm-blog-details.js stub. Article + comments + leave-comment form + sidebar. crm-shell.js pagesTab updated. Approved 2026-05-13. |
| 32 | error-404-cover.html | src/pages/error-404-cover.html | ✓ | crm-error-404-cover.js stub. Standalone cover layout. Lottie id=error003. No crm-shell. crm-shell.js pagesTab updated. Approved 2026-05-13. |
| 33 | error-404-full.html | src/pages/error-404-full.html | ✓ | crm-error-404-full.js stub. Standalone full layout. Lottie id=error001. No crm-shell. crm-shell.js pagesTab updated. Approved 2026-05-13. |

| 34 | under-construction-cover.html | src/pages/under-construction-cover.html | ✓ | Standalone. maintenance-cover-wrapper. Lottie id=under-construction001. crm-shell.js pagesTab updated. Approved 2026-05-13. |
| 35 | under-construction-full.html | src/pages/under-construction-full.html | ✓ | Standalone. maintenance-full-wrapper. Lottie id=under-construction002. crm-shell.js pagesTab updated. Approved 2026-05-13. |
| 36 | login-basic.html | src/authentication/login-basic.html | ✓ | Standalone. auth-wrapper. Native form action→app/dashboard.html. Links to forgot-password-basic + register-basic. crm-shell.js authTab updated. Approved 2026-05-13. |
| 37 | login-cover.html | src/authentication/login-cover.html | ✓ | Standalone. auth-cover-wrapper. Native form action→app/dashboard.html. Links to forgot-password-cover + register-cover. crm-shell.js authTab updated. Approved 2026-05-13. |
| 38 | register-basic.html | src/authentication/register-basic.html | ✓ | Standalone. auth-wrapper. Native form action→app/dashboard.html. Links to login-basic. crm-shell.js authTab updated. Approved 2026-05-13. |
| 39 | register-cover.html | src/authentication/register-cover.html | ✓ | Standalone. auth-cover-wrapper. Native form action→app/dashboard.html. Links to login-cover. crm-shell.js authTab updated. Approved 2026-05-14. |
| 40 | forgot-password-basic.html | src/authentication/forgot-password-basic.html | ✓ | Standalone. auth-wrapper. Native form action→app/new-password-basic.html. Cancel→app/login-basic.html. crm-shell.js authTab updated. Approved 2026-05-14. |
| 41 | forgot-password-cover.html | src/authentication/forgot-password-cover.html | ✓ | Standalone. auth-cover-wrapper. Native form action→app/new-password-cover.html. Cancel→app/login-cover.html. crm-shell.js authTab updated. Approved 2026-05-14. |
| 42 | new-password-basic.html | src/authentication/new-password-basic.html | ✓ | Standalone. auth-wrapper. Native form action→app/login-basic.html. crm-shell.js authTab updated. Approved 2026-05-14. |
| 43 | new-password-cover.html | src/authentication/new-password-cover.html | ✓ | Standalone. auth-cover-wrapper. Native form action→app/login-cover.html. crm-shell.js authTab updated. Approved 2026-05-14. |
| 44 | dashboard-rtl.html | src/index-rtl.html | ✓ | dir="rtl". styles-rtl.css. crm-dashboard.js reused. RTL instructions alert preserved. crm-shell.js footer fix applied globally. Approved 2026-05-14. |
| 45 | apexchart.html | src/chart/apexchart.html | ✓ | 6 ApexCharts. Uses chart/apexchart.js directly. crm-shell.js chartsTab updated. Approved 2026-05-14. |
| 46 | chartjs.html | src/chart/chartjs.html | ✓ | 5 Chart.js charts. Uses chart/chartjs.js directly. crm-shell.js chartsTab updated. Approved 2026-05-14. |
| 47 | tables-basic.html | src/table/tables-basic.html | ✓ | Large table showcase. No page-specific JS (seed has none). crm-shell.js tablesTab updated. Approved 2026-05-14. |
| 48 | tables-datatable.html | src/table/tables-datatable.html | ✓ | DataTables. Uses plugins/datatable.js. crm-shell.js tablesTab updated. Approved 2026-05-14. |
| 49 | jsvectormap.html | src/maps/jsvectormap.html | ✓ | jsvectormap.min.css + jsvectormap.min.js + maps/world.js + plugins/jsvectormap.js. crm-shell.js mapsTab updated. Approved 2026-05-14. |
| 50 | leaflet.html | src/maps/leaflet.html | ✓ | leaflet.css + leaflet.js + us-states.js + plugins/leaflet.js. crm-shell.js mapsTab updated. Approved 2026-05-14. |
| 51 | flaticon.html | src/icons/flaticon.html | ✓ | Icon showcase. No page-specific JS. crm-shell.js iconsTab updated. Approved 2026-05-14. |
| 52 | fontawesome.html | src/icons/fontawesome.html | ✓ | Icon showcase. No page-specific JS. crm-shell.js iconsTab updated. Approved 2026-05-14. |
| 53 | lucide.html | src/icons/lucide.html | ✓ | Icon showcase. No page-specific JS. crm-shell.js iconsTab updated. Approved 2026-05-14. |
| 54 | accordion.html | src/components/accordion.html | ✓ | Bootstrap accordion showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 55 | alerts.html | src/components/alerts.html | ✓ | Bootstrap alerts showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 56 | badge.html | src/components/badge.html | ✓ | Bootstrap badge showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 57 | breadcrumb.html | src/components/breadcrumb.html | ✓ | Bootstrap breadcrumb showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 58 | button-group.html | src/components/button-group.html | ✓ | Bootstrap button-group showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 59 | buttons.html | src/components/buttons.html | ✓ | Bootstrap buttons showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 60 | card.html | src/components/card.html | ✓ | Bootstrap card showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 61 | carousel.html | src/components/carousel.html | ✓ | Bootstrap carousel showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 62 | collapse.html | src/components/collapse.html | ✓ | Bootstrap collapse showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 63 | dropdowns.html | src/components/dropdowns.html | ✓ | Bootstrap dropdowns showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 64 | list-group.html | src/components/list-group.html | ✓ | Bootstrap list-group showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 65 | modal.html | src/components/modal.html | ✓ | Bootstrap modal showcase. plugins/snippets.js. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 66 | navbar.html | src/components/navbar.html | ✓ | Bootstrap navbar showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 67 | offcanvas.html | src/components/offcanvas.html | ✓ | Bootstrap offcanvas showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 68 | pagination.html | src/components/pagination.html | ✓ | Bootstrap pagination showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 69 | popovers.html | src/components/popovers.html | ✓ | Bootstrap popovers showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 70 | progress.html | src/components/progress.html | ✓ | Bootstrap progress showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 71 | scrollspy.html | src/components/scrollspy.html | ✓ | Bootstrap scrollspy showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 72 | spinners.html | src/components/spinners.html | ✓ | Bootstrap spinners showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 73 | tabs.html | src/components/tabs.html | ✓ | Bootstrap tabs showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-14. |
| 74 | toasts.html | src/components/toasts.html | ✓ | Bootstrap toasts showcase. plugins/toast.js included. crm-shell.js componentsTab updated. Approved 2026-05-15. |
| 75 | tooltips.html | src/components/tooltips.html | ✓ | Bootstrap tooltips showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-15. |
| 76 | typography.html | src/components/typography.html | ✓ | Bootstrap typography showcase. No page-specific JS. crm-shell.js componentsTab updated. Approved 2026-05-15. |
| 77 | avatar.html | src/extended-ui/avatar.html | ✓ | Avatar showcase. No page-specific JS. crm-shell.js extendedTab updated. Approved 2026-05-15. |
| 78 | card-action.html | src/extended-ui/card-action.html | ✓ | Card action showcase. No page-specific JS. crm-shell.js extendedTab updated. Approved 2026-05-15. |
| 79 | drag-and-drop.html | src/extended-ui/drag-and-drop.html | ✓ | Sortable drag-drop showcase. Sortable.min.js + plugins/sortable.js. crm-shell.js extendedTab updated. Approved 2026-05-15. |
| 80 | simplebar.html | src/extended-ui/simplebar.html | ✓ | Simplebar showcase. No page-specific JS. crm-shell.js extendedTab updated. Approved 2026-05-15. |
| 81 | swiper.html | src/extended-ui/swiper.html | ✓ | Swiper carousel showcase. swiper-bundle.min.css + swiper-bundle.min.js + plugins/swiper.js. crm-shell.js extendedTab updated. Approved 2026-05-15. |
| 82 | flatpickr.html | src/forms/flatpickr.html | ✓ | Flatpickr datepicker showcase. l10n/fr.js + plugins/flatpickr.js. crm-shell.js formsTab updated. Approved 2026-05-15. |
| 83 | form-elements.html | src/forms/form-elements.html | ✓ | Form elements showcase. plugins/range.js. crm-shell.js formsTab updated. Approved 2026-05-15. |
| 84 | form-floating.html | src/forms/form-floating.html | ✓ | Form floating showcase. No page-specific JS. crm-shell.js formsTab updated. Approved 2026-05-15. |
| 85 | form-input-group.html | src/forms/form-input-group.html | ✓ | Form input group showcase. No page-specific JS. crm-shell.js formsTab updated. Approved 2026-05-15. |
| 86 | form-layout.html | src/forms/form-layout.html | ✓ | Form layout showcase. No page-specific JS. crm-shell.js formsTab updated. Approved 2026-05-15. |
| 87 | form-validation.html | src/forms/form-validation.html | ✓ | Form validation showcase. plugins/validation.js. crm-shell.js formsTab updated. Approved 2026-05-15. |
| 88 | tagify.html | src/forms/tagify.html | ✓ | Tagify showcase. tagify.css + tagify.js + plugins/tagify.js. crm-shell.js formsTab updated. Approved 2026-05-15. |
| 89 | investment.html | src/ai/investment.html | ✓ | Self-contained AI page. Own aside (ai-menubar-tabs) + header (ai-app-header). No crm-shell.js. Approved 2026-05-15. |
| 90 | new-chat.html | src/ai/new-chat.html | ✓ | Self-contained AI page. Own aside + header. No crm-shell.js. Approved 2026-05-15. |
| 91 | new-project.html | src/ai/new-project.html | ✓ | Self-contained AI page. Own aside + header. No crm-shell.js. Approved 2026-05-15. |
| 92 | plans.html | src/ai/plans.html | ✓ | Self-contained AI page. Own aside + header. No crm-shell.js. Approved 2026-05-15. |
| 93 | search-chat.html | src/ai/search-chat.html | ✓ | Self-contained AI page. Own aside + header. No crm-shell.js. Approved 2026-05-15. |
| 94 | search-image.html | src/ai/search-image.html | ✓ | Self-contained AI page. Own aside + header. No crm-shell.js. Approved 2026-05-15. |
| 95 | your-chat.html | src/ai/your-chat.html | ✓ | Self-contained AI page. Own aside + header. No crm-shell.js. Approved 2026-05-15. |
| 96 | search-apps.html | src/ai/search-apps.html | ✓ | Self-contained AI page. Own aside + header. No crm-shell.js. Approved 2026-05-15. |
| 97 | search-apps-details.html | src/ai/search-apps-details.html | ✓ | Self-contained AI page. Own aside + header. No crm-shell.js. Approved 2026-05-15. |

## Pages Built: 97
## Browser Sign-off Pending: 0
## Fully Done: 97 (96 unique pages — #3 slot unused due to deleted page)
## Total Seed Pages: 96 | Total App Pages to Build: 96 | Remaining to Build: 0

---

## Batch Sign-off History

| Batch | Pages | Approved |
|-------|-------|---------|
| Batch 1 | dashboard, leads, customers, profile, deals, sales, finance, team-management, employee | 2026-05-12 |
| Batch 2 | review, task-management, user-management, activities, settings, marketing, calendar, chat | 2026-05-13 |
| Batch 3 | inbox-email, email-compose, email-read, login-frame, register-frame | 2026-05-13 |
| Batch 4 | forgot-password-frame, new-password-frame, error-404, pricing, under-construction | 2026-05-13 |
| Batch 5 | blog, blog-list, blog-details, error-404-cover, error-404-full | 2026-05-13 |
| Batch 6 | under-construction-cover, under-construction-full, login-basic, login-cover, register-basic | 2026-05-13 |
| Batch 7 | register-cover, forgot-password-basic, forgot-password-cover, new-password-basic, new-password-cover | 2026-05-14 |
| Batch 8 | dashboard-rtl, apexchart, chartjs, tables-basic, tables-datatable | 2026-05-14 |
| Batch 9 | jsvectormap, leaflet, flaticon, fontawesome, lucide | 2026-05-14 |
| Batch 10 | accordion, alerts, badge, breadcrumb, button-group | 2026-05-14 |
| Batch 11 | buttons, card, carousel, collapse, dropdowns | 2026-05-14 |
| Batch 12 | list-group, modal, navbar, offcanvas, pagination | 2026-05-14 |
| Batch 13 | popovers, progress, scrollspy, spinners, tabs | 2026-05-14 |
| Batch 14 | toasts, tooltips, typography, avatar, card-action | 2026-05-15 |
| Batch 15 | drag-and-drop, simplebar, swiper, flatpickr, form-elements | 2026-05-15 |
| Batch 16 | form-floating, form-input-group, form-layout, form-validation, tagify | 2026-05-15 |
| Batch 17 | investment, new-chat, new-project, plans, search-chat, search-image, your-chat, search-apps, search-apps-details | 2026-05-15 |
| Session 18–19 | Doc consolidation — 93 production-readiness gaps fixed across 26 docs; linkage audit (11 issues resolved); naming normalisation (ALL-CAPS authority files, kebab-case QC docs) | 2026-05-17 |
| Session 20 | Infrastructure seal — folder restructure (V4_extracted→backend, nexlink triple-wrap→frontend); all 96 pages verified HTTP 200; npm cache → D:\CRM\.npm-cache; pip cache → D:\CRM\.pip-cache; Python 3.12.10 installed at D:\Python; venv at D:\CRM\backend\.venv; fastapi/uvicorn/pydantic installed; zero C: leakage confirmed | 2026-05-18 |
| Phase 1 | Foundation Seal COMPLETE — README.md, CHANGELOG.md, CONTRIBUTING.md, Makefile, .pre-commit-config.yaml, ADR-001/002/003, Alembic setup (sqlalchemy+psycopg2 added to requirements), docker-compose+Dockerfiles confirmed existing; 96/96 pages HTTP 200; pushed to GitHub | 2026-05-18 |
| Phase 2 | Follow-up Engine COMPLETE — SQLAlchemy ORM models (FollowupTask, FollowupEscalation, Lead, Activity); Alembic migration 0001_followup_schema; public REST API /api/v1/followups (5 endpoints, JWT-gated); JWT auth dependency (services/auth/jwt_deps.py); python-jose/pytest/httpx added to requirements; 38 tests passing (18 unit + 20 integration); 96/96 pages HTTP 200 | 2026-05-18 |
| Phase 3 | 5 Engine public APIs COMPLETE — WhatsApp (12 tests), Collections (11), Activity (10), Activation (10), DLQ (10); all 5 routers mounted in app.py; 93/93 tests passing; 96/96 pages HTTP 200; GitHub push | 2026-05-18 |
| Audit | Pre-Phase-4 audit: 9 fixes applied — P3-A Literal import, P3-B lifespan singleton wiring, P2-A RBAC escalation gate, P2-B overdue scanner, P2-C list_followups count query, P3-C invoice send endpoint, P3-D tenant isolation, P3-E utcnow() deprecation, P3-F conversation detail endpoint; 14 new tests; 308/308 tests passing; GitHub push | 2026-05-18 |
| Phase 4 Stage 1 | Full read of all 51 §F + §H specs; 30 duplication/overlap clusters identified; `backend/docs/_qc/phase4-stage1-read-log.md` written with all cluster PRIMARY designations | 2026-05-23 |
| Phase 4 Stage 2 | Doc fix + restructure complete — 71 flat docs → 9 subdirs (Diátaxis+DDD); ownership blocks on 51 files; 6 gap fills; 6 inconsistency fixes; 14 duplicate removals; all cross-refs updated; 308/308 tests | 2026-05-25 |
| Phase 4 Stage 3 Round 1 | Code overlay gap register created (28 gaps A-001→E-008); 15 gaps fixed — B-001 JWT claims, D-001 lead stages, migrations 0002+0003, 3 new ORM model files, 3 bug fixes (double-tz, JazzCash paise, _payments dict), 4 infra path fixes, 9 catalog events; 314/314 tests passing | 2026-05-25 |

---

## Phase 5 — Custom Design Pages

| ID | Page | Archetype | Status | Browser sign-off | Notes |
|---|---|---|---|---|---|
| A-01 | dashboard.html | dashboard | ⏳ | ⏳ pending | T2 FAIL — posture strip + KPI h2 hardcoded; dt_NewCustomers seed rows. |
| A-02 | leads-dashboard.html | dashboard | ⏳ | ⏳ pending | Built 2026-05-29. Reads CRM_DUMMY.leads/leadFunnelKpi/deltas. |
| A-03 | contacts-health.html | dashboard | ⏳ | ⏳ pending | Built 2026-05-29. Reads CRM_DUMMY.contacts/contactsKpi. |
| A-04 | sales-dashboard.html | dashboard | ⏳ | ⏳ pending | Re-processed 2026-05-29. CRM_DUMMY wiring verified. |
| A-05 | quotes-dashboard.html | dashboard | ⏳ | ⏳ pending | Built 2026-05-29. Reads CRM_DUMMY.quotes. |
| A-06 | subscriptions-dashboard.html | dashboard | ⏳ | ⏳ pending | Built 2026-05-29. MRR/ARR/Renewal Rate. P-016 stub. |
| A-12 | identity-dashboard.html | dashboard | ⏳ | ⏳ pending | Built 2026-05-29. Reads CRM_DUMMY.users+AUDIT_LOG. |
| A-13 | audit-dashboard.html | dashboard | ⏳ | ⏳ pending | Built 2026-05-29. Reads CRM_DUMMY.AUDIT_LOG. |
| B-01 | followups.html | resource_list | ⏳ | ⏳ pending | T2/T3/T4 FAIL (delta text; Place 3 CSS; filter vocab). |
| B-02 | leads.html | resource_list | ⏳ | ⏳ pending | T2/T3/T4 FAIL (chart data; Place 3 CSS; stage filter). |
| B-03 | contacts.html | resource_list | ⏳ | ⏳ pending | T2/T3 FAIL (delta text; Place 3 CSS). |
| B-06 | activity.html | resource_list | ⏳ | ⏳ pending | Built 2026-05-29. Read-only. Reads CRM_DUMMY.activities. |
| B-07 | tasks.html | resource_list | ⏳ | ⏳ pending | Built 2026-05-29. Overdue-pinned. Reads CRM_DUMMY.tasks. |
| B-08 | collections.html | resource_list | ⏳ | ⏳ pending | T2/T4 FAIL (delta text; status filter vocab). |
| B-09 | invoices.html | resource_list | ⏳ | ⏳ pending | Built 2026-05-29. INVOICES dataset added. Balance col, overdue red. |
| B-10 | users.html | resource_list | ⏳ | ⏳ pending | Built 2026-05-29. Admin-only. Role badge list. |
| C-01 | leads-detail.html | detail_360 | ⏳ | ⏳ pending | T2 PARTIAL (timeline partially hardcoded). |
| C-02 | contacts-detail.html | detail_360 | ⏳ | ⏳ pending | Built 2026-05-29. Demo c-001. Reads CRM_DUMMY. |
| C-04 | opportunities-detail.html | detail_360 | ⏳ | ⏳ pending | Re-processed 2026-05-29. Quotes tab reads CRM_DUMMY.quotes. |
| C-06 | quotes-detail.html | detail_360 | ⏳ | ⏳ pending | Built 2026-05-29. Reads CRM_DUMMY.quotes. |
| C-09 | subscriptions-detail.html | detail_360 | ⏳ | ⏳ pending | Built 2026-05-29. Status-gated buttons. SUBSCRIPTIONS dataset added. |
| D-01 | sales-cockpit.html | cockpit | ⏳ | ⏳ pending | Re-processed 2026-05-29. All panels CRM_DUMMY-wired. |
| G-02 | user-management-crm.html | settings_admin | ⏳ | ⏳ pending | Built 2026-05-29. 2-step Invite wizard, role/suspend/reset modals. |
| H-01 | sales-analytics.html | analytics | ⏳ | ⏳ pending | Built 2026-05-29. Pipeline KPI, stage/forecast/funnel charts, rep table. |
| H-04 | finance-analytics.html | analytics | ⏳ | ⏳ pending | Built 2026-05-29. Aging buckets, revenue trend, collections table. P-016. |
| H-06 | audit-report.html | analytics | ⏳ | ⏳ pending | Built 2026-05-29. Hash-chain verify, signed CSV export. |
| I-01 | lead-new.html | form_wizard | ⏳ | ⏳ pending | T1 FAIL (crm-custom.css missing); T2 FAIL (stage vocab stale). |
| I-03 | opportunity-new.html | form_wizard | ⏳ | ⏳ pending | Built 2026-05-29. 2-step wizard, flatpickr close date. |
| I-05 | quote-builder.html | form_wizard | ⏳ | ⏳ pending | Built 2026-05-29. 4-step CPQ. Discount >10% approval. Autosave 60s. |
| J-01 | audit-log.html | audit_compliance | ⏳ | ⏳ pending | Rebuilt 2026-05-29. Shell fixed. Badges from CRM_DUMMY. |
| J-02 | compliance-report.html | audit_compliance | ⏳ | ⏳ pending | Rebuilt 2026-05-29. KPIs from CRM_DUMMY.AUDIT_LOG. |
| J-04 | rbac-audit.html | audit_compliance | ⏳ | ⏳ pending | Rebuilt 2026-05-29. Matrix + log from CRM_DUMMY. |
| A-11 | tenants-dashboard.html | dashboard | ⏳ | ⏳ pending | Built 2026-05-29. Plan/seat/feature KPIs, entitlements queue. Reads d.tenantKpi. |
| B-04 | accounts.html | resource_list | ⏳ | ⏳ pending | Built 2026-05-29. ACCOUNTS dataset (12 records). Tier/balance filter chips. |
| C-03 | accounts-detail.html | detail_360 | ⏳ | ⏳ pending | Built 2026-05-29. 4-tab pane. Demo a-002 (City Pharma Ltd). |
| C-07 | orders-detail.html | detail_360 | ⏳ | ⏳ pending | Built 2026-05-29. ORDERS dataset. Immutable badge. Demo ord-001. |
| C-08 | invoices-detail.html | detail_360 | ⏳ | ⏳ pending | Built 2026-05-29. Total/Paid/Balance strip, payment history. Demo i-001. |
| I-02 | contact-new.html | form_wizard | ⏳ | ⏳ pending | Built 2026-05-29. 2-step wizard. Phone dedup warn on blur. |
| G-01 | org-settings.html | settings_admin | ⏳ | ⏳ pending | Built 2026-05-29. Identity/Locale/Currency/Hours. Settings left-nav. |
| G-03 | roles.html | settings_admin | ⏳ | ⏳ pending | Built 2026-05-29. Roles table + permission registry. d.roles.data. |
| G-04 | billing-settings.html | settings_admin | ⏳ | ✓ wired 2026-05-31 | Built 2026-05-29. Wired: GET /billing/subscription + GET /billing/invoices. P-016 payment section static stub. |
| G-05 | integrations.html | settings_admin | ⏳ | ✓ wired 2026-05-31 | Built 2026-05-29. Wired: GET /integrations + POST /integrations/:provider/test. Status badges live. |
| G-06 | notifications.html | settings_admin | ⏳ | ⏳ pending | Built 2026-05-29. Per-event toggle table. Quiet hours. |
| G-07 | feature-flags.html | settings_admin | ⏳ | ⏳ pending | Built 2026-05-29. Flag registry d.featureFlags. 2-person approval modal. |
| G-08 | compliance.html | settings_admin | ⏳ | ⏳ pending | Built 2026-05-29. Retention policy, data governance link, break-glass log. |
| J-03 | data-governance.html | audit_compliance | ⏳ | ✓ wired 2026-05-31 | Built 2026-05-29. Wired: GET /governance/classification + /retention + /sar + GET /privacy/consent. |
| J-05 | privacy.html | audit_compliance | ⏳ | ⏳ pending | Built 2026-05-29. Consent records, DSR list, erasure request form. |
| A-07 | support-dashboard.html | dashboard | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Posture strip, SLA breach KPIs, at-risk queue. |
| A-08 | engagement-dashboard.html | dashboard | ⏳ | ✓ wired 2026-05-31 | Cat 2. Built 2026-05-29. Wired: GET /communications/engagement + GET /campaigns. KPIs + chart live. |
| A-09 | knowledge-dashboard.html | dashboard | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Deflection rate KPIs, stale article queue. |
| A-10 | workflows-dashboard.html | dashboard | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Posture strip, execution KPIs, failed queue. |
| B-05 | cases.html | resource_list | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Dual Status×SLA filter chips, badges. |
| B-11 | partners.html | resource_list | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Tier×Status filter chips, PKR commission. |
| C-05 | cases-detail.html | detail_360 | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. SLA timer strip, 3-tab pane, escalation controls. |
| C-10 | workflow-run-detail.html | detail_360 | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Execution log, steps, error details tabs. |
| C-11 | partners-detail.html | detail_360 | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. 4-tab pane. Attribution + commission context. |
| C-12 | knowledge-article.html | detail_360 | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. State-gated Publish/Edit, 4-tab pane. |
| E-01 | support-console.html | support_console | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. 3-pane SLA queue/thread/context layout. |
| F-01 | marketing-workspace.html | marketing | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Campaigns DataTable + Status filter chips. |
| G-09 | territories.html | settings_admin | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Territory tree, rule editor, assignment config. |
| H-02 | marketing-analytics.html | analytics | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Channel engagement bar chart, opt-in trend. |
| H-03 | support-analytics.html | analytics | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. SLA breach trend line, case volume donut. |
| H-05 | workflow-analytics.html | analytics | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Pass/fail bar chart, failure-rate-by-workflow. |
| H-07 | report-builder.html | analytics | ⏳ | ✓ wired 2026-05-31 | Cat 2. Built 2026-05-29. Wired: GET/POST /reports/definitions + POST /reports/execute. Save button enabled. |
| I-04 | case-new.html | form_wizard | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. 2-step wizard. Contact live search. |
| I-06 | campaign-new.html | form_wizard | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. 2-step wizard. P-017 Urdu alert. |
| K-01 | workflow-builder.html | builder | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. 3-pane palette/canvas/inspector. Simulated graph. |
| K-02 | object-builder.html | builder | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Object type selector, field list, layout canvas. |
| K-03 | rule-builder.html | builder | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Condition + action row builder, test simulation. |
| K-04 | approval-lanes.html | builder | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. 4-lane kanban, calcTotal() per card. |
| L-01 | inbox.html | inbox | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Channel filter, 2-pane thread list/view. |
| L-02 | inbox-thread.html | inbox | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. WhatsApp-style bubbles, intent context panel. |
| L-03 | routing-config.html | settings_admin | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Queue/agent capacity/routing rules/fallback. |
| M-01 | ai-copilot.html | ai | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Advisory-only. Intent classifier chat. |
| M-02 | ai-insights.html | ai | ⏳ | ⏳ pending | Cat 2. Built 2026-05-29. Win prob dist, churn donut, CLV bar, feature weights. |

---

## Queue

**All 96 library pages complete. Custom design phase is now active — see `D:\CRM\DESIGN-SPEC.md` for the 75-page screen inventory, 13 archetypes (A–M), and 8 build phases. Start with Build Phase 1 (B-01 followups.html, B-02 leads.html, C-01 leads-detail.html, A-01 dashboard.html).**

---

## Deleted Pages (do not reference)

The following were built in earlier sessions and deleted on 2026-05-10 as non-conforming:
`leads.html`, `followups.html`, `leads-detail.html`

Rebuilt with correct filenames in sessions 5–7: `login-frame.html`, `register-frame.html`, `forgot-password-frame.html`, `new-password-frame.html`.
