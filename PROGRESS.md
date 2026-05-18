# Pakistan CRM — Screen Progress

**Last updated:** 2026-05-18 (Phase 3 complete — 5 public API engines, 93 tests passing; Phase 4 frontend custom pages next)
**Protocol:** FRAMEWORK.md (seed-first normalisation)
**Ground truth for app/ directory:** `frontend/src/app/`
**Dev server:** `npm run serve` from `D:\CRM\frontend` — port 3001 (must run from this directory)
**Python env:** `D:\Python\python.exe` (3.12.10) → venv `D:\CRM\backend\.venv` → fastapi/uvicorn/pydantic installed — zero C: leakage
**Rebuild plan:** `REBUILD-PLAN.md` — 5 phases, ~15 weeks to 10/10. Task checklist: `PENDING.md` (root).

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

---

## Queue

**All 96 library pages complete. Custom design phase is now active — see `D:\CRM\DESIGN-SPEC.md` for the 75-page screen inventory, 13 archetypes (A–M), and 8 build phases. Start with Build Phase 1 (B-01 followups.html, B-02 leads.html, C-01 leads-detail.html, A-01 dashboard.html).**

---

## Deleted Pages (do not reference)

The following were built in earlier sessions and deleted on 2026-05-10 as non-conforming:
`leads.html`, `followups.html`, `leads-detail.html`

Rebuilt with correct filenames in sessions 5–7: `login-frame.html`, `register-frame.html`, `forgot-password-frame.html`, `new-password-frame.html`.
