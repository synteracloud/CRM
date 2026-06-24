---
Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: AI
Phase: 2.95
---

# FRONTEND IMPACT ANALYSIS

> For each residual decision, explicit assessment of impact on all frontend dimensions.
> Source: Phase 2.95 Residual Decision Collapse.

---

## How to Read This Document

Each decision is assessed against 10 frontend dimensions:
- **Navigation** — does it change which pages appear in the sidebar/topbar?
- **Menus** — does it change dropdown menus or action menus?
- **Screens** — does it add, remove, or restructure any page?
- **Dashboards** — does it change KPI tiles, charts, or summary panels?
- **Permissions** — does it change what buttons/actions are shown per role?
- **Workflows** — does it change multi-step flows (create → edit → confirm)?
- **Forms** — does it change field definitions, validation, or submission behavior?
- **Components** — does it change reusable UI components?
- **User Journeys** — does it change the end-to-end path a user follows?
- **Role Experiences** — does it change what different user roles see or can do?

---

## OA-001 — contacts.delete RBAC Scope

| Dimension | Impact | Detail |
|-----------|--------|--------|
| Navigation | None | All nav items unchanged |
| Menus | None | No menu changes |
| Screens | None | contacts.html page unchanged |
| Dashboards | None | No dashboard changes |
| **Permissions** | **YES — minor** | Delete button/action must be hidden for viewer, field_agent, support_agent, tenant_owner. Visible only for tenant_admin, super_admin. |
| Workflows | None | Delete workflow path exists but gated |
| Forms | None | No form changes |
| Components | Minimal | Delete button component must check for contacts.delete scope in JWT scopes array |
| **User Journeys** | **YES — minor** | Tenant owner cannot delete contacts until OA-001 is approved. Known constraint. |
| Role Experiences | Minimal | tenant_admin/super_admin see delete; others do not |

**Frontend Action Required:** When building contacts page authority, document: "Delete contact action requires contacts.delete scope. Grant pending OA-001 approval. Hide delete controls for roles without this scope."

---

## OA-002 — JTI Blocklist In-Memory

| Dimension | Impact | Detail |
|-----------|--------|--------|
| Navigation | None | — |
| Menus | None | — |
| Screens | None | — |
| Dashboards | None | — |
| Permissions | None | — |
| Workflows | None | Logout flow calls DELETE /auth/sessions/current — unchanged |
| Forms | None | — |
| Components | None | — |
| User Journeys | None | User logs out, token cleared locally, redirected to login — same behavior |
| Role Experiences | None | — |

**Frontend Action Required:** None. Frontend behavior is identical whether JTI store is in-memory or Redis.

---

## OA-003 — JazzCash/Easypaisa Stub Mode

| Dimension | Impact | Detail |
|-----------|--------|--------|
| Navigation | None | Billing settings page remains in nav |
| Menus | None | — |
| **Screens** | **Minimal** | billing-settings.html (G-04) payment section shows stub responses. If owner chooses Option C (disable payment section), hide the payment methods panel. |
| Dashboards | None | — |
| Permissions | None | — |
| Workflows | None | Payment initiation flow exists and returns stub confirmation |
| **Forms** | **Minimal** | Payment method form submits to stub adapter — currently returns success without processing. Frontend should display "Sandbox mode" indicator if design calls for it. |
| Components | None | — |
| User Journeys | None | User completes payment form → receives stub response → same UX |
| Role Experiences | None | — |

**Frontend Action Required:** Document G-04 payment section as "Stub mode — P-016 constraint. Wire payment method form. Display stub response state. Production behavior activated when OA-003 credentials received."

---

## OA-004 — AI Inference Model

| Dimension | Impact | Detail |
|-----------|--------|--------|
| Navigation | None | ai-copilot.html (M-01), ai-insights.html (M-02) remain in nav |
| Menus | None | — |
| Screens | None | Both pages built and functional with rule-based results |
| **Dashboards** | **None** | Rule-based scores display identically to LLM scores from frontend perspective |
| Permissions | None | — |
| Workflows | None | — |
| Forms | None | — |
| Components | None | Score display components are provider-agnostic |
| User Journeys | None | User views AI insights — result format unchanged regardless of model |
| Role Experiences | None | — |

**Frontend Action Required:** Document M-01/M-02 as "Rule-based advisory — AI inference model deferred to C7. API contract for AI scores is stable regardless of backend model."

---

## OA-005 — contract_lifecycle_management No Gateway Route

| Dimension | Impact | Detail |
|-----------|--------|--------|
| Navigation | None | No contracts page in DESIGN-SPEC.md C6 scope — nothing to add or remove |
| Menus | None | — |
| Screens | None | No contracts screen in C6 build |
| Dashboards | None | — |
| Permissions | None | — |
| Workflows | None | — |
| Forms | None | — |
| Components | None | — |
| User Journeys | None | — |
| Role Experiences | None | — |

**Frontend Action Required:** None. No contracts page in C6 scope. Gateway route and frontend page deferred to C7.

---

## OA-006 — Security Test Artifacts

| Dimension | Impact | Detail |
|-----------|--------|--------|
| Navigation | None | — |
| Menus | None | — |
| Screens | None | — |
| Dashboards | None | — |
| Permissions | None | — |
| Workflows | None | — |
| Forms | None | — |
| Components | None | — |
| User Journeys | None | — |
| Role Experiences | None | — |

**Frontend Action Required:** None — file disposition has zero frontend impact.

---

## OA-007 — Load Test Reports

| Dimension | Impact | Detail |
|-----------|--------|--------|
| Navigation | None | — |
| All other dimensions | None | — |

**Frontend Action Required:** None.

---

## OA-008 — Password Hashing Algorithm

| Dimension | Impact | Detail |
|-----------|--------|--------|
| Navigation | None | — |
| Menus | None | — |
| Screens | None | login.html, register.html unchanged |
| Dashboards | None | — |
| Permissions | None | — |
| Workflows | None | Login/register flows call same endpoints |
| **Forms** | **None** | Password form fields unchanged — hashing is backend-only |
| Components | None | — |
| User Journeys | None | Login journey identical regardless of hash algorithm |
| Role Experiences | None | — |

**Frontend Action Required:** None. Backend hashing is opaque to frontend.

---

## OA-009 — Refresh Token Not Revoked on Logout

| Dimension | Impact | Detail |
|-----------|--------|--------|
| Navigation | None | — |
| Menus | None | — |
| Screens | None | — |
| Dashboards | None | — |
| Permissions | None | — |
| Workflows | None | Logout flow: frontend calls DELETE /auth/sessions/current → clears local state → redirects to login. Behavior unchanged. |
| Forms | None | — |
| Components | None | — |
| User Journeys | None | From user perspective, logout completes successfully regardless of refresh token state |
| Role Experiences | None | — |

**Frontend Action Required:** None. The security gap is invisible to frontend behavior.

---

## Summary

| Decision | Any Frontend Impact? | Action Required |
|----------|---------------------|-----------------|
| OA-001 | Yes (minor — permissions) | Document contacts delete scope constraint; hide button per role |
| OA-002 | No | None |
| OA-003 | Yes (minimal — stub UI) | Document G-04 stub state; wire payment form to stub response |
| OA-004 | No | Document M-01/M-02 as rule-based |
| OA-005 | No | None — no C6 contracts page |
| OA-006 | No | None |
| OA-007 | No | None |
| OA-008 | No | None |
| OA-009 | No | None |

**No decision creates a navigation, menu, workflow, or user journey change.**
**No decision removes or restructures any existing screen.**
**Frontend Authority Capture may proceed for all 75 pages without constraint from any residual decision.**

---

*End FRONTEND_IMPACT_ANALYSIS.md*
