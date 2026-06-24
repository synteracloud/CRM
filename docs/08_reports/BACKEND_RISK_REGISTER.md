Status: Draft
Authority Level: High
Last Reviewed: 2026-06-22
Owner: Human

# BACKEND_RISK_REGISTER.md
> Risk assessment for Phase 2 Backend Authority Capture findings

---

## Risk Classification

**Likelihood:** High (likely before launch), Medium (possible), Low (unlikely)  
**Impact:** Critical (data breach / complete outage), High (partial outage / data loss), Medium (degraded experience), Low (minor)  
**Priority = Likelihood × Impact**

---

## Critical Priority Risks

### RISK-001: JTI Blocklist Lost on Restart / Multi-Instance
**Gap ref:** G-CRIT-001  
**Likelihood:** High (any restart, any scale-out)  
**Impact:** High (revoked tokens reusable for up to 15 minutes)  
**Scenario:** Attacker obtains user's access token. User logs out. Gateway restarts. Attacker's token is accepted again.  
**Mitigation path:** Redis JTI store with matching TTL  
**Status:** UNMITIGATED

### RISK-002: contacts.delete Route Effectively Broken or Unguarded
**Gap ref:** G-CRIT-002  
**Likelihood:** High (currently deployed)  
**Impact:** High (deletion permanently blocked OR unguarded deletion)  
**Scenario A:** The `requireScopes` comparison fails gracefully → no role can delete contacts. Feature silently missing.  
**Scenario B:** The `requireScopes` comparison on unknown scope returns true → any authenticated user can delete any contact.  
**Status:** REQUIRES IMMEDIATE VERIFICATION

---

## High Priority Risks

### RISK-003: Payment Stubs in Production (Blocker P-016)
**Gap ref:** G-HIGH-001  
**Likelihood:** High (stubs are active in render.yaml)  
**Impact:** Critical (no revenue collection possible)  
**Scenario:** User attempts to pay an invoice. JazzCash stub returns synthetic success. No real money transferred. Customer believes they paid; system shows paid.  
**Mitigation path:** Obtain live credentials; set JAZZCASH_STUB_MODE=false  
**Status:** ACTIVE BLOCKER (P-016)

### RISK-004: Post-Logout Token Reuse via Refresh Token
**Gap ref:** G-HIGH-002  
**Likelihood:** Medium (requires attacker with stolen refresh token)  
**Impact:** High (attacker retains session access for 7 days post-logout)  
**Scenario:** User logs out. Attacker (who has stolen HttpOnly refresh token cookie) calls POST /auth/refresh. If refresh token not revoked in DB, attacker receives new access token.  
**Status:** REQUIRES VERIFICATION of logout implementation

### RISK-005: In-Process Events Lost on Service Restart
**Gap ref:** G-HIGH-003  
**Likelihood:** Medium (every deployment triggers restart)  
**Impact:** Medium (missed lead assignments, missed payment reminders)  
**Scenario:** Deployment restart during lead creation. lead.created.v1 event in-flight. lead_assignment workflow never triggers. Lead has no territory assignment.  
**Mitigation path:** Persist events to DB before firing (outbox pattern already defined); implement consumer  
**Status:** PARTIALLY MITIGATED (outbox table exists; publisher not implemented)

### RISK-006: SLA Breach Notifications May Never Fire
**Gap ref:** G-MED-002  
**Likelihood:** Medium  
**Impact:** High (case SLAs breach silently; support team unaware)  
**Scenario:** High-priority case hits SLA breach threshold. No scanner emits case.sla.breached.v1. sla_breach_notify workflow never triggers. Customer escalates externally.  
**Status:** TBD REQUIRES VERIFICATION

---

## Medium Priority Risks

### RISK-007: Scheduled Tasks Never Execute
**Gap ref:** G-MED-001  
**Likelihood:** High (task_schedule table has no confirmed executor)  
**Impact:** Medium (scheduled reports, follow-up reminders via scheduler may not fire)  
**Scenario:** Follow-up task scheduled via task_schedule table. No job runner reads the table. Task never fires. Follow-up missed.  
**Status:** REQUIRES VERIFICATION

### RISK-008: Urdu WhatsApp Templates Blocked (P-017)
**Gap ref:** G-MED-005  
**Likelihood:** High (blocker is active)  
**Impact:** Medium (Pakistan-market WhatsApp campaigns cannot run in Urdu)  
**Status:** ACTIVE BLOCKER (P-017) — requires human native speaker approval

### RISK-009: Frontend 422 Errors When Pages Wired
**Gap ref:** G-MED-006  
**Likelihood:** High (all pages currently in DUMMY_MODE)  
**Impact:** Medium (all form submissions fail on first wiring without Idempotency-Key)  
**Scenario:** Developer wires first form page to live API. Every POST/PATCH returns 422 "Idempotency-Key is required". User-visible form failure.  
**Status:** KNOWN; must be added as first wiring task

### RISK-010: Dev Token Endpoint Reachable in Production
**Gap ref:** G-MED-003  
**Likelihood:** Low (render.yaml likely sets JWT_SECRET)  
**Impact:** Critical IF reachable (any user can generate unsigned JWTs and bypass auth)  
**Status:** TBD REQUIRES VERIFICATION — confirm JWT_SECRET always set in render.yaml env

---

## Low Priority Risks

### RISK-011: Cross-Schema FK Violations Possible
**Gap ref:** G-LOW-002  
**Likelihood:** Low (application layer enforces; tests cover)  
**Impact:** Medium (orphaned data; data quality issues)  
**Status:** ACCEPTED — architecture trade-off

### RISK-012: Rate Limiting Disabled During Redis Outage
**Gap ref:** G-LOW-003  
**Likelihood:** Low (Render.com Redis is managed; rarely fails)  
**Impact:** Medium (brute-force login possible during outage window)  
**Status:** ACCEPTED — fail-open is deliberate for availability

---

## Risk Summary Matrix

| Risk ID | Title | Likelihood | Impact | Priority |
|---|---|---|---|---|
| RISK-001 | JTI blocklist lost on restart | High | High | CRITICAL |
| RISK-002 | contacts.delete route broken/unguarded | High | High | CRITICAL |
| RISK-003 | Payment stubs in production | High | Critical | CRITICAL |
| RISK-004 | Post-logout token reuse | Medium | High | HIGH |
| RISK-005 | In-process events lost on restart | Medium | Medium | HIGH |
| RISK-006 | SLA breach notifications may not fire | Medium | High | HIGH |
| RISK-007 | Scheduled tasks never execute | High | Medium | HIGH |
| RISK-008 | Urdu template blocker (P-017) | High | Medium | MEDIUM |
| RISK-009 | 422 errors on first page wiring | High | Medium | MEDIUM |
| RISK-010 | Dev token endpoint in production | Low | Critical | MEDIUM |
| RISK-011 | Cross-schema FK violations | Low | Medium | LOW |
| RISK-012 | Rate limiting disabled on Redis outage | Low | Medium | LOW |

---

## Recommended Immediate Actions

1. **Verify contacts.delete behavior** (RISK-002) — read requireScopes implementation to confirm whether undefined scope causes allow or deny
2. **Verify RISK-010** — check render.yaml for JWT_SECRET presence
3. **Fix RISK-001** — migrate JTI blocklist to Redis before multi-instance deployment
4. **Verify RISK-004** — confirm DELETE /auth/sessions/current also revokes refresh token DB record
5. **Verify RISK-006** — check if SLA scanner exists in code

---

*End BACKEND_RISK_REGISTER.md*
