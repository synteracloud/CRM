---
Status: Active
Authority Level: High
Last Reviewed: 2026-06-23
Owner: AI
Phase: 3.5 — Project Memory Layer Establishment
---

# OUT_OF_SCOPE REGISTER

> Intentionally deferred items, future phase work, and planned post-C6 sprints.
> These are NOT gaps — they are documented planned deferrals with clear future phase assignments.
> Presence in this register means: "the system is working correctly for C6; this is planned for later."

---

## OOS-001: OA-005 / D-001 — contracts_lifecycle_management Gateway Route (C7)

**Item ID:** OA-005 / D-001
**Title:** contract_lifecycle_management module — no C6 gateway route (deferred to C7)
**Classification:** OUT_OF_SCOPE
**Current Status:** Deferred — C7 scope
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md; AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS D-001
**Evidence Source:** DESIGN-SPEC.md — no contracts page in C6 75-page scope; backend/src/contract_lifecycle_management/api.py — 12 API endpoints built and tested
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97 (AUTO-CLOSED); DECISION_COLLAPSE_REGISTER.md Phase 3.25 (confirmed)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** The backend contracts module is complete (12 API endpoints, full test suite). No C6 frontend page maps to contracts per DESIGN-SPEC.md. Gateway route is deferred to C7 when the contracts frontend page is built.

**Detailed Explanation:** backend/src/contract_lifecycle_management/ is a fully built Python module. However, the DESIGN-SPEC.md defines 75 custom pages across 13 archetypes (A–M) — no contracts page is included. Without a frontend page, there is no reason to expose the gateway route. The module is complete, tested, and waiting for C7.

**C7 Sprint Plan:**
1. Design contracts page per new archetype (extend DESIGN-SPEC.md)
2. Create backend/gateway/routes/v1-contracts.routes.js using any of the 44 existing route files as pattern
3. Add contracts.* RBAC scopes to rbac-scopes.js (following OA-001 pattern for scope grant)
4. Build frontend page (app/contracts.html or similar)
5. Wire frontend to live API

**Affected Components:** backend/src/contract_lifecycle_management/ (built, not exposed), backend/gateway/routes/ (no v1-contracts.routes.js in C6)
**Affected Routes:** 12 contract lifecycle endpoints (Python defined, not proxied in C6)
**Affected APIs:** Contract Lifecycle Management API (C7)
**Affected Workflows:** Contract creation, approval, renewal (C7)
**Affected Roles:** account_manager, tenant_admin, legal (C7 roles TBD)

**Owner Required:** NO (scope is confirmed deferred; C7 sprint plan is documented)
**External Dependency:** NO

**Future Phase:** C7 — create gateway route, build frontend page, add RBAC scopes

**Reopen Criteria (bring back to C6):** If owner explicitly decides contracts module must be exposed in C6 (requires DESIGN-SPEC.md update and scope change approval).

**Related Documents:** DESIGN-SPEC.md, backend/src/contract_lifecycle_management/, AI_OPERATING_CONTEXT.md D-001
**Related Register Entries:** AC-002 (AUTO_CLOSED_REGISTER.md — the closure decision)

---

## OOS-002: AI-001 — LLM Inference Provider Integration (C7)

**Item ID:** AI-001
**Title:** LLM inference model integration — deferred to C7 (rule-based is C6 production)
**Classification:** OUT_OF_SCOPE
**Current Status:** Deferred — C7 scope. Rule-based scoring is the C6 production state.
**Original Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS AI-001; FEATURE_SCOPE.md Blocked list
**Evidence Source:** backend/requirements.txt (no openai/anthropic/google SDK); backend/src/ai_copilot/services.py (rule-based); backend/src/ai_insights/services.py (rule-based); FEATURE_SCOPE.md §14 features 86–93 all "Built (rule-based)"
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97 (AUTO-CLOSED as OA-004); confirmed DECISION_COLLAPSE_REGISTER.md Phase 3.25
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass (AUTO-CLOSED OA-004)

**Decision Summary:** Rule-based weighted-sum scoring IS the documented and designed C6 AI behavior. LLM integration is an additive C7 feature. The AI copilot and insights pages are advisory shells using rule-based scoring — this is correct, not a gap.

**Detailed Explanation:** All 8 AI features (FEATURE_SCOPE.md §14, features 86–93) are documented as "Built (rule-based only)" or "Built (rule-based)". This is not a placeholder — it is the designed C6 implementation. The advisory-only posture (M-01 ai-copilot.html, M-02 ai-insights.html) is the C6 product. Adding an LLM provider is an upgrade, not a fix.

**C7 Sprint Plan:**
1. Select LLM provider (Claude Haiku recommended for cost + Urdu language support)
2. Add SDK to backend/requirements.txt (anthropic, openai, or equivalent)
3. Set API key in Render.com environment (ANTHROPIC_API_KEY or OPENAI_API_KEY)
4. Replace rule-based scoring functions with LLM calls in ai_copilot/services.py and ai_insights/services.py
5. Update FEATURE_SCOPE.md status from "Built (rule-based)" to "Built (LLM-powered)"

**Affected Components:** backend/src/ai_copilot/, backend/src/ai_insights/, backend/requirements.txt, frontend/src/app/ai-copilot.html (M-01), frontend/src/app/ai-insights.html (M-02)
**Affected Routes:** GET /ai-copilot/*, GET /ai-insights/*, POST /ai-copilot/chat
**Affected APIs:** AI Copilot API, AI Insights API
**Affected Workflows:** AI-powered lead scoring, churn prediction, CLV estimation, copilot suggestions
**Affected Roles:** All roles (advisory visible to all)

**Owner Required:** NO (scope is confirmed deferred to C7)
**External Dependency:** YES (when activated: LLM provider API key needed — ED-category)

**Future Phase:** C7 — LLM provider integration sprint

**Reopen Criteria (bring back to C6):** If owner decides LLM inference is a C6 launch requirement (major scope change — adds API cost, latency, and provider dependency).

**Related Documents:** backend/src/ai_copilot/, backend/src/ai_insights/, FEATURE_SCOPE.md §14, AI_OPERATING_CONTEXT.md AI-001
**Related Register Entries:** AC-001 (AUTO_CLOSED_REGISTER.md — OA-004 closure decision)

---

## OOS-003: MR-007 — Kuickpay Payment Adapter (Blocked / Post-C6)

**Item ID:** MR-007
**Title:** Kuickpay adapter — blocked pending credentials
**Classification:** OUT_OF_SCOPE
**Current Status:** Not rendered in UI — post-C6 activation
**Original Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS MR-007
**Evidence Source:** UI hidden element; no Kuickpay adapter in backend/adapters/pakistan/payments/ (or stub only)
**Resolution Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS (confirmed constraint)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.5 Memory Layer Establishment

**Decision Summary:** Kuickpay adapter is blocked pending API credentials. Not rendered in UI. Post-C6 activation after JazzCash and Easypaisa are operational.

**Detailed Explanation:** Kuickpay is a third Pakistani payment provider. The UI element is hidden (not rendered). Activation requires Kuickpay API credentials, which like JazzCash and Easypaisa require a merchant account application. Lower priority than JazzCash/Easypaisa (market share consideration).

**Affected Components:** Frontend UI (hidden), Kuickpay adapter (stub or not yet built)
**Affected Routes:** POST /payments/kuickpay/* (if implemented)
**Affected APIs:** Kuickpay API (external)
**Affected Workflows:** Payment processing (Kuickpay path)
**Affected Roles:** tenant_admin, customers

**Owner Required:** YES (provider relationship) once prioritized
**External Dependency:** YES — Kuickpay merchant account

**Future Phase:** Post-C6 — activate after JazzCash + Easypaisa are operational

**Reopen Criteria:** If owner decides Kuickpay should be prioritized before JazzCash/Easypaisa activation.

**Related Documents:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS MR-007
**Related Register Entries:** ED-001, ED-002 (higher-priority payment providers)

---

## OOS-004: AUTH-C7 — Bcrypt Password Migration

**Item ID:** AUTH-C7
**Title:** SHA-256 → bcrypt password migration (transparent re-hash on login)
**Classification:** OUT_OF_SCOPE
**Current Status:** Accepted SHA-256 for C6; bcrypt migration deferred to C7 Security Sprint
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md OA-008; OWNER_REQUIRED_COMPRESSION_REPORT.md SD-005
**Evidence Source:** backend/gateway/routes/v1-auth.routes.js (SHA-256 hashing); package.json (no bcrypt)
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97 (SAFE-DEFAULT SD-005)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** SHA-256 password hashing is accepted for C6. Transparent re-hash-on-login (bcrypt) is documented and planned for C7 Security Sprint. Risk at C6 scale with managed DB: low.

**C7 Sprint Plan:**
1. Add `bcrypt` to backend/gateway/package.json
2. In v1-auth.routes.js login handler: after successful SHA-256 verification, re-hash with bcrypt and update DB. Add detection of hash format (sha256: prefix vs $2b$ prefix).
3. New registrations use bcrypt from sprint date
4. Over time, all active users are transparently migrated on next login

**Affected Components:** backend/gateway/routes/v1-auth.routes.js, package.json
**Affected Routes:** POST /auth/login (migration happens transparently), POST /auth/register (new bcrypt from day 1 of sprint)
**Affected APIs:** Auth API
**Affected Workflows:** Login (transparent migration), registration (new algo)
**Affected Roles:** All users

**Owner Required:** NO
**External Dependency:** NO

**Future Phase:** C7 Security Sprint (bundle with SD-002 post-C6 Auth Sprint if timing aligns)

**Reopen Criteria (accelerate to C6):** If a data breach occurs before C7 (must expedite migration).

**Related Documents:** SAFE_DEFAULT_REGISTER.md SD-005, backend/gateway/routes/v1-auth.routes.js
**Related Register Entries:** AUTH-C7b (OOS-005 below)

---

## OOS-005: AUTH-C7b — Redis JTI Blocklist + Refresh Token Revocation

**Item ID:** AUTH-C7b
**Title:** JTI blocklist Redis migration + refresh token revocation on logout (Post-C6 Auth Sprint)
**Classification:** OUT_OF_SCOPE
**Current Status:** Accepted for C6; Post-C6 Auth Sprint documented
**Original Source:** OWNER_APPROVAL_ITEMS_BEFORE_PHASE3.md OA-002 + OA-009; OWNER_REQUIRED_COMPRESSION_REPORT.md SD-002
**Evidence Source:** backend/gateway/middleware/jti-blocklist.js (in-memory Set); backend/gateway/routes/v1-auth.routes.js lines 183–190 (no refresh token delete on logout)
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97 (SAFE-DEFAULT SD-002)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** Both auth gaps are accepted for C6 (low risk on single-instance deployment). Both are bundled into a single Post-C6 Auth Sprint with a fully documented implementation plan.

**Post-C6 Sprint Plan:**
1. **OA-002 (JTI Redis migration):** In jti-blocklist.js, replace `const revokedJtis = new Set()` with Redis calls: `redis.setex('jti:{jti}', 900, '1')` (TTL = 15 min = access token TTL). Add getRedisClient() import.
2. **OA-009 (refresh token revocation):** In DELETE /sessions/current handler: read `req.cookies?.crm_refresh_token`, call `redis.del('rt:{refreshToken}')`, clear cookie. ~3–5 lines.
Both changes are TIER 2 (touch protected auth files) — require TIER 2 review at implementation time.

**Affected Components:** backend/gateway/middleware/jti-blocklist.js (OA-002), backend/gateway/routes/v1-auth.routes.js (OA-009)
**Affected Routes:** All authenticated routes (JTI check), DELETE /auth/sessions/current (logout)
**Affected APIs:** Auth API
**Affected Workflows:** Login/logout security model
**Affected Roles:** All authenticated users

**Owner Required:** NO (risk acceptance documented; TIER 2 review at implementation time)
**External Dependency:** NO

**Future Phase:** Post-C6 Auth Sprint (first sprint after commercial launch)

**Reopen Criteria (accelerate to C6):** If multi-instance deployment is needed before Auth Sprint (escalates OA-002 risk — must fix JTI blocklist before adding second instance).

**Related Documents:** SAFE_DEFAULT_REGISTER.md SD-002, backend/gateway/middleware/jti-blocklist.js, backend/gateway/routes/v1-auth.routes.js
**Related Register Entries:** AUTH-C7 (OOS-004)

---

## OOS-006: BROKER-C7 — Message Broker for Multi-Instance Events

**Item ID:** BROKER-C7
**Title:** Message broker (Celery/RabbitMQ/Redis Streams) for multi-instance deployment
**Classification:** OUT_OF_SCOPE
**Current Status:** In-process InMemoryEventBus accepted for C6; broker evaluation deferred to C7
**Original Source:** BACKEND_GAP_REGISTER.md G-HIGH-003; OWNER_REQUIRED_COMPRESSION_REPORT.md SD-006
**Evidence Source:** backend/src/event_bus/core.py InMemoryEventBus; no broker dependency in requirements.txt or package.json
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97 (SAFE-DEFAULT SD-006)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** InMemoryEventBus is the correct C6 architecture for single-instance deployment. Message broker evaluation and implementation is deferred to C7 when multi-instance scale is needed.

**C7 Sprint Plan:**
1. Evaluate broker options: Redis Streams (already in infra), RabbitMQ, Celery + Kombu
2. Implement broker-backed EventBus implementing the same InMemoryEventBus interface
3. Swap implementation — all publishers use same interface; no publisher code changes
4. Deploy as additional Render.com service or use existing Redis Streams

**Affected Components:** backend/src/event_bus/ (replace InMemoryEventBus with broker-backed implementation)
**Affected Routes:** N/A (internal)
**Affected APIs:** N/A
**Affected Workflows:** All 5 system workflows (event-driven components)
**Affected Roles:** N/A

**Owner Required:** NO
**External Dependency:** NO (Redis already in infra; broker choice may require additional Render service)

**Future Phase:** C7 Architecture Sprint (triggered by multi-instance deployment need)

**Reopen Criteria:** If Render.com auto-scaling adds a second gateway instance before C7 (in-process bus becomes inadequate — cross-instance events would be lost).

**Related Documents:** backend/src/event_bus/, SAFE_DEFAULT_REGISTER.md SD-006, backend/docs/infrastructure/event-catalog.md
**Related Register Entries:** G-HIGH-003 (SAFE_DEFAULT_REGISTER.md SD-006)

---

## OOS-007: SCHED-C7 — External Task Scheduler

**Item ID:** SCHED-C7
**Title:** External task scheduler (Celery Beat / APScheduler) — deferred to C7
**Classification:** OUT_OF_SCOPE
**Current Status:** task_schedule table unused; no scheduler process in C6
**Original Source:** BACKEND_GAP_REGISTER.md G-MED-001; OWNER_REQUIRED_COMPRESSION_REPORT.md SD-008
**Evidence Source:** db/activity_task_db/schema.sql (task_schedule table defined but unused); requirements.txt (no celery/apscheduler)
**Resolution Source:** OWNER_REQUIRED_COMPRESSION_REPORT.md Phase 2.97 (SAFE-DEFAULT SD-008)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 2.97 Owner-Required Compression Pass

**Decision Summary:** No C6 feature requires scheduled (timer-based) task execution. All system workflows are event-driven. task_schedule table was built speculatively. Scheduler implementation is deferred to C7.

**C7 Sprint Plan:**
1. Select scheduler: Celery Beat (if complex schedules needed) or APScheduler (simpler, embedded)
2. Add to requirements.txt
3. Implement scheduled tasks using task_schedule table as job store
4. Deploy as additional Render.com worker service (or embedded in services process)

**Affected Components:** db/activity_task_db/schema.sql (task_schedule table), backend/ (no scheduler process)
**Affected Routes:** N/A (background scheduler)
**Affected APIs:** N/A (internal scheduled jobs)
**Affected Workflows:** Future scheduled workflows (daily digest, weekly reports, etc.)
**Affected Roles:** N/A

**Owner Required:** NO
**External Dependency:** NO

**Future Phase:** C7 — when a specific scheduled feature is required

**Reopen Criteria:** If a C6 feature requires time-based scheduling (must implement scheduler before feature can launch).

**Related Documents:** db/activity_task_db/schema.sql, backend/requirements.txt, SAFE_DEFAULT_REGISTER.md SD-008
**Related Register Entries:** G-MED-001 (SAFE_DEFAULT_REGISTER.md SD-008)

---

## OOS-008: FBR-COMP — FBR Invoice Formatting Compliance

**Item ID:** FBR-COMP
**Title:** FBR (Federal Board of Revenue) invoice formatting compliance
**Classification:** OUT_OF_SCOPE
**Current Status:** Pending legal review — not a launch blocker
**Original Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS (FBR compliance)
**Evidence Source:** Invoice formatting not verified against FBR requirements; NTN/STRN not implemented as DB fields (O-TBD-003 confirmed); adapters/pakistan/ compliance-adapter.md hooks built
**Resolution Source:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS; O-TBD-003 (AUTO_CLOSED_REGISTER.md AC-011)
**Resolution Date:** 2026-06-23
**Resolved By:** Phase 3.5 Memory Layer Establishment

**Decision Summary:** FBR invoice formatting requirements have not been verified. NTN/STRN are not DB fields (confirmed O-TBD-003). Legal review of FBR requirements is pending. Not a C6 launch blocker — invoices function correctly without FBR-specific fields.

**Detailed Explanation:** Pakistan's Federal Board of Revenue (FBR) may require specific fields on commercial invoices (NTN number, STRN number, FBR invoice portal integration). The compliance-adapter hooks exist in adapters/pakistan/ but the specific requirements have not been verified by legal review. The current invoice implementation (POST /invoice-summaries) generates invoices without NTN/STRN fields. For B2B SaaS at C6 scale, FBR registration may not be mandatory depending on revenue threshold.

**What legal review must determine:**
1. Is FBR registration required at C6 revenue level?
2. Must invoices include NTN/STRN fields?
3. Is FBR e-invoicing portal integration required?
4. What are PTA compliance requirements for commercial messages?

**Affected Components:** Invoice generation routes, adapters/pakistan/compliance-adapter.md, db schemas (potential NTN/STRN field addition)
**Affected Routes:** POST /invoice-summaries, GET /invoice-summaries/:id
**Affected APIs:** Finance/Billing API
**Affected Workflows:** Invoice generation, tax compliance
**Affected Roles:** tenant_admin (billing), finance users

**Owner Required:** YES (when legal review is initiated)
**External Dependency:** YES (legal review + potentially FBR API integration)

**Future Phase:** Post-C6 legal review sprint (or C7)

**Reopen Criteria:** If legal review determines FBR registration is mandatory at current revenue level (accelerates to active implementation).

**Related Documents:** AI_OPERATING_CONTEXT.md KNOWN_CONSTRAINTS (FBR compliance), adapters/pakistan/, AC-011 (O-TBD-003 CNIC/NTN/STRN confirmed not in DB)
**Related Register Entries:** AC-011 (AUTO_CLOSED_REGISTER.md)

---

## Summary

| Item ID | Deferred Phase | Trigger for Activation | Launch Blocker |
|---------|---------------|----------------------|----------------|
| OOS-001 (OA-005) | C7 | When contracts frontend page is designed | NO |
| OOS-002 (AI-001) | C7 | When LLM provider is selected | NO |
| OOS-003 (MR-007) | Post-C6 | After JazzCash + Easypaisa operational | NO |
| OOS-004 (AUTH-C7) | C7 Security Sprint | After C6 launch | NO |
| OOS-005 (AUTH-C7b) | Post-C6 Auth Sprint | First sprint post-launch | NO |
| OOS-006 (BROKER-C7) | C7 Architecture Sprint | When multi-instance needed | NO |
| OOS-007 (SCHED-C7) | C7 | When first scheduled feature needed | NO |
| OOS-008 (FBR-COMP) | Post-C6 legal review | When legal review initiated | NO |

**No OUT_OF_SCOPE item blocks the C6 commercial launch.**

---

*End OUT_OF_SCOPE_REGISTER.md — 8 items (OOS-001 through OOS-008) — Phase 3.5 (2026-06-23)*
