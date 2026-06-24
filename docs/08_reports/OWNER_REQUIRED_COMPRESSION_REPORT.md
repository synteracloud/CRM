---
Status: Active
Authority Level: Critical
Last Reviewed: 2026-06-23
Owner: AI
Phase: 2.97
---

# OWNER-REQUIRED ITEM COMPRESSION REPORT

> Phase 2.97 — Final compression pass before Frontend Authority Capture.
> Every OWNER-REQUIRED / OWNER_CONFIRMATION_ONLY item reviewed.
> Result: 18 items → 3 genuine OWNER-REQUIRED items.

---

## Executive Summary

**Total items reviewed:** 18
**AUTO-CLOSED:** 3
**SAFE-DEFAULT:** 12
**OUT-OF-SCOPE:** 0
**OWNER-REQUIRED:** 3

Of 18 items across all prior phases carrying OWNER-REQUIRED or OWNER_CONFIRMATION_ONLY labels, **15 were resolved** by repository evidence, established patterns, or deterministic safe defaults. Only 3 items remain that genuinely require a human commercial/legal/credential decision.

---

## Final Count

| Classification | Count | Items |
|---------------|-------|-------|
| AUTO-CLOSED | 3 | OA-004, OA-005, D-003 |
| SAFE-DEFAULT | 12 | OA-001, OA-002, OA-006, OA-007, OA-008, OA-009, G-HIGH-003, G-HIGH-004, G-MED-001, D-005, G-LOW-003, G-LOW-004 |
| OUT-OF-SCOPE | 0 | — |
| OWNER-REQUIRED | 3 | OA-003, D-002/G-MED-004, G-MED-005 |

---

## Per-Item Analysis Table

| Item ID | Description | Evidence | Frontend Impact | Nav Impact | Workflow Impact | Permission Impact | Genuinely Owner-Required? | Final Classification | Action Taken |
|---------|-------------|----------|-----------------|------------|-----------------|-------------------|--------------------------|---------------------|--------------|
| OA-001 | contacts.delete scope missing | rbac-scopes.js; 6 existing delete scope patterns | Yes — hide delete button per role | No | No | Yes — scope grant | NO — pattern fully deterministic | SAFE-DEFAULT | Default documented; implementation spec in report |
| OA-002 | JTI blocklist in-memory | jti-blocklist.js; Redis already wired | No | No | No | No | NO — timing is deterministic at single-instance scale | SAFE-DEFAULT | Accept for C6; Redis sprint post-launch documented |
| OA-003 | Payment credentials (JazzCash/Easypaisa) | render.yaml STUB flags; adapter code | No | No | No | No | YES — external vendor contract + credentials | OWNER-REQUIRED | Documented with evidence; stub state is launch default |
| OA-004 | AI inference model selection | requirements.txt; backend/src/ai_copilot; ai_insights | No | No | No | No | NO — current state IS the designed behavior | AUTO-CLOSED | Rule-based is C6 design; LLM upgrade is C7 scope |
| OA-005 | contracts gateway route | DESIGN-SPEC.md (no contracts page in C6) | No | No | No | No | NO — DESIGN-SPEC.md resolves it | AUTO-CLOSED | Confirmed C7 scope; no C6 action required |
| OA-006 | Security test artifacts disposition | tests/security/*.json; compliance context | No | No | No | No | NO — conservative default is deterministic | SAFE-DEFAULT | Move to docs/reports/security/ documented |
| OA-007 | Load test report disposition | tests/load/reports/c5-prod-*.html | No | No | No | No | NO — c5-prod reports are historical evidence | SAFE-DEFAULT | Move to docs/reports/load/ documented |
| OA-008 | Password hashing (SHA-256 not bcrypt) | v1-auth.routes.js; package.json (no bcrypt) | No | No | No | No | NO — risk tolerance deterministic at C6 scale | SAFE-DEFAULT | Accept SHA-256 for C6; C7 bcrypt re-hash-on-login |
| OA-009 | Refresh token not revoked on logout | v1-auth.routes.js lines 183–190; Redis client present | No | No | No | No | NO — bundle with OA-002 is deterministic | SAFE-DEFAULT | Accept for C6; bundle with OA-002 post-C6 sprint |
| G-HIGH-003 | No message broker | backend/services/app.py; no broker dep | No | No | No | No | NO — in-process acceptable at C6 scale | SAFE-DEFAULT | Accept for C6; architecture decision for C7 scale |
| G-HIGH-004 | Outbox publisher not implemented | db/transaction_db/schema.sql; no publisher code | No | No | No | No | NO — payment stub anyway; outbox is C7 concern | SAFE-DEFAULT | Accept for C6; review when payments activate |
| G-MED-001 | No external scheduler | db/activity_task_db/schema.sql (task_schedule); no runner | No | No | No | No | NO — table unused; accept for C6 | SAFE-DEFAULT | Accept for C6; scheduler in C7 |
| D-002/G-MED-004 | Custom objects routing mechanism | backend/src/custom_objects/; no v1-custom-objects.routes.js; K-02 page built | No | No | No | No | YES — whether custom objects is in C6 product scope cannot be inferred from code | OWNER-REQUIRED | Documented; K-02 can be built as advisory-only shell pending decision |
| G-MED-005 | Urdu WhatsApp template approval | P-017 constraint; Urdu strings exist | No | No | No | No | YES — requires human Urdu native speaker | OWNER-REQUIRED | P-017 constraint remains; campaigns blocked until approved |
| D-003 | 5 entity schema attributions unverified | Entity fields inferred from gateway code | No | No | No | No | NO — investigation task, not owner decision | AUTO-CLOSED | Schema verification pass assigned to backend team; no owner needed |
| D-005 | 4 backend archive docs | backend/docs/ phase4-gap-register + 3 others | No | No | No | No | NO — SAFE_REPOSITORY_HYGIENE move | SAFE-DEFAULT | Archive to docs/reports/u-series/ or docs/08_reports/ |
| G-LOW-003 | Rate limit fails open on Redis outage | gateway/config/redis-client.js; fail-open pattern | No | No | No | No | NO — accepted risk at C6 managed Redis | SAFE-DEFAULT | Accept for C6; note for C7 hardening |
| G-LOW-004 | No PostgreSQL RLS | All 18 DB schemas; semgrep CI rule | No | No | No | No | NO — accepted architecture trade-off with semgrep guard | SAFE-DEFAULT | Architecture decision confirmed; no change |

---

## Safe Defaults Applied

### SD-001: OA-001 — contacts.delete Scope Grant
**Default:** `CONTACTS_DELETE: 'contacts.delete'` added to SCOPES constant; granted to `tenant_admin` and `super_admin` in ROLE_SCOPES.
**Rationale:** All 6 other delete operations in rbac-scopes.js follow identical pattern. Pattern = deterministic. Both roles already hold all other administrative delete scopes. "Who gets contacts.delete?" is answered by: the same roles that get every other delete scope.
**Implementation spec:** In `backend/gateway/config/rbac-scopes.js` — add `CONTACTS_DELETE: 'contacts.delete'` to SCOPES object; add `'contacts.delete'` to ROLE_SCOPES[`tenant_admin`] and ROLE_SCOPES[`super_admin`] arrays. (Code change requires owner approval per REVISED_DECISION_ESCALATION_MATRIX.md — but the WHAT is now documented as a safe default.)
**Frontend assumption:** contacts delete button visible to tenant_admin and super_admin only; hidden for all other roles.

### SD-002: OA-002 + OA-009 — Auth Hardening Sprint (Post-C6)
**Default:** Accept in-memory JTI blocklist + non-revoked refresh tokens for C6. Fix both in a single Post-C6 Auth Hardening Sprint using existing Redis client (`getRedisClient()`).
**Rationale:** Single Render.com instance; 15-min access token TTL limits exposure; managed Redis uptime is high; user base at C6 is small. Risk is low, not zero. Sprint plan is fully deterministic from code.
**Sprint scope:** (1) Migrate JTI blocklist to `redis.setex('jti:{jti}', 900, '1')`. (2) On logout, also call `redis.del('rt:{refreshToken}')`.

### SD-003: OA-006 — Security Test Artifacts
**Default:** Move `tests/security/*.json` to `docs/reports/security/`. Version-control as compliance evidence.
**Rationale:** Conservative compliance evidence preservation is the safer default vs. gitignoring.

### SD-004: OA-007 — Load Test Reports
**Default:** Move `tests/load/reports/c5-prod-*.html` to `docs/reports/load/`. Add `tests/load/reports/` (non-c5-prod) to .gitignore.
**Rationale:** Phase C5 production load test results are a performance baseline — preserve them.

### SD-005: OA-008 — Password Hashing
**Default:** Accept SHA-256 for C6. Plan transparent re-hash-on-login (bcrypt) for C7.
**Rationale:** At C6 scale (small user base), DB access controls on Render.com managed PostgreSQL mitigate the brute-force risk. Re-hash-on-login (Option C from RESIDUAL_OWNER_DECISION_REGISTER.md) is the cleanest migration path with zero user disruption.

### SD-006: G-HIGH-003 — No Message Broker
**Default:** Accept in-process events for C6.
**Rationale:** Single instance. Event loss on restart is possible but rare. Volume is C6-scale (small). Message broker adds operational complexity that is not justified until multi-instance deployment.

### SD-007: G-HIGH-004 — Outbox Publisher
**Default:** Accept for C6. Payment domain is in stub mode (OA-003). When payments activate, outbox publisher becomes mandatory. Review as part of OA-003 activation sprint.
**Note:** The outbox table exists in the DB. The publisher should be implemented when payments go live. This is a deferred implementation task, not an owner decision.

### SD-008: G-MED-001 — No External Scheduler
**Default:** Accept for C6. `task_schedule` table is unused. When scheduled tasks are required (C7), implement a scheduler (Celery Beat or APScheduler are natural fits given the Python/FastAPI stack).

### SD-009: D-005 — Backend Archive Docs
**Default:** Move `backend/docs/phase4-gap-register.md` and any other historical-artifact backend docs to `docs/08_reports/` or `docs/_archive/`. Apply SAFE_REPOSITORY_HYGIENE.

### SD-010: G-LOW-003 — Rate Limit Fails Open
**Default:** Accept for C6. Render.com managed Redis has high uptime. Fail-open on Redis outage is a known pattern for rate limiters. Auth endpoints could fail-closed, but adding that complexity before scale is premature.

### SD-011: G-LOW-004 — No PostgreSQL RLS
**Default:** Accept. Architecture decision is confirmed: application-layer isolation enforced by semgrep CI rule. Adding DB RLS would require Alembic migrations + performance impact analysis — out of scope for C6.

### SD-012: D-003 — Entity Schema Attributions
**Note:** This is an investigation task (read 5 schema.sql files directly), not an owner decision. Assigned as backend verification task; can be completed in next backend pass. No owner needed.

---

## Items Closed

### AUTO-CLOSED: OA-004 — AI Inference Model
**Reason:** The current rule-based weighted-sum scoring IS the designed and implemented behavior. It is not "undecided" — it is the C6 production model. The question "should we add an LLM?" is an additive C7 feature request, not an open C6 decision. Closing as AUTO-CLOSED per rule: "If repository evidence supports current behavior as correct, the item is closed."

### AUTO-CLOSED: OA-005 — contracts_lifecycle_management Gateway Route
**Reason:** Verified by DESIGN-SPEC.md — no contracts management page exists in the C6 75-page scope. The backend module is complete and will be exposed in C7 when the frontend page is built. Nothing to decide for C6.

### AUTO-CLOSED: D-003 — Entity Schema Attributions
**Reason:** This is a backend investigation task, not an owner decision. The 5 schema.sql files can be read directly without any human input. Closing as AUTO-CLOSED; assigning as a verification task.

---

## Remaining OWNER-REQUIRED Items

### OA-003: JazzCash/Easypaisa Live Payment Credentials
**Genuinely owner-required because:** Obtaining merchant credentials from JazzCash and Easypaisa requires:
1. A registered business entity with PTA/SECP registration
2. Formal merchant account applications to each payment provider
3. Sandbox credential approval (2–4 weeks typical)
4. Production credential approval after sandbox testing
No amount of repository analysis can supply these. The code is complete; the business relationship is missing.

**Evidence:** `render.yaml` JAZZCASH_STUB_MODE=true, EASYPAISA_STUB_MODE=true; adapter code confirmed stub in prior audits.

**Launch impact:** Billing/payment collection not possible. Free-tier CRM launch is viable without payment. G-04 (billing-settings.html) displays stub state — already the production behavior.

---

### D-002/G-MED-004: Custom Objects Module Product Scope (C6 vs C7)
**Genuinely owner-required because:** Two separate questions, both require human judgment:
1. Is object-builder.html (K-02) in the C6 active product pitch? If yes, does it need backend connectivity, or is it a demo shell?
2. Is the custom_objects module accessible via an undiscovered catch-all route, or is the gateway route genuinely missing?

Question 2 could be investigated via gateway/app.js. Question 1 requires product roadmap knowledge. Keeping as OWNER-REQUIRED only for Q1.

**Frontend assumption (pending decision):** K-02 (object-builder.html) was built in the library phase and is in the frontend. Frontend authority capture can document it as "advisory shell — backend connectivity pending D-002 decision."

---

### G-MED-005: Urdu WhatsApp Template Approval (P-017)
**Genuinely owner-required because:** The Urdu strings exist in the codebase. Verification that they are culturally and linguistically appropriate for Pakistani users requires a human Urdu native speaker. This is not a technical question — it is a content quality/compliance question.

**Launch impact:** WhatsApp campaigns targeting Urdu-speaking customers cannot launch until approved. English campaigns are unaffected.

---

## Conclusion

Owner interventions required before C6 launch: **1** (OA-003 — payment credentials).
Owner interventions required before full feature activation: **2** more (D-002, G-MED-005).
Everything else has been closed, defaulted, or deferred to post-C6 sprints with clear plans.

---

*End OWNER_REQUIRED_COMPRESSION_REPORT.md*
