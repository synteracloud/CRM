# Adoption UX + Behavioral Design

**Source:** Behaviour.md — ADDENDUM_PAKISTAN_WEDGE §2, §8, §9, §12, §14, §15
**Audience:** Product, engineering, design — all decisions that affect first-session experience

This document defines the behavioral design layer that sits on top of the technical architecture. The system must not only work correctly — it must be adopted and used daily by users who may forget tasks, ignore notifications, and delay actions.

---

## 1) Behavioral Design Principles

These six principles govern every product decision. When two design options conflict, use these as the tiebreaker.

| # | Principle | What it means in practice |
|---|---|---|
| 1 | **Adapt to user behavior** | System learns from usage patterns; never forces new workflows on users before value is proven. Default settings match real behavior, not best practices. |
| 2 | **Near-zero manual data entry** | Every inbound WhatsApp message, every payment callback, every status change auto-updates the system. Forms are the exception, not the default path. |
| 3 | **Natural habit alignment** | WhatsApp is the primary surface. Agents should never need to leave their existing tools to keep the CRM updated. |
| 4 | **Reduced cognitive load** | Every core action in ≤2 steps (see `ui-foundations.md §6`). No multi-step configuration for day-1 workflows. Labels must be plain language. |
| 5 | **Immediate visible value** | User must see a result within 60 seconds of first login. First lead captured, first follow-up shown, first dashboard panel populated. |
| 6 | **Gradual discipline** | Enforcement increases with usage maturity. Day 1: advisory only. Day 15: gentle blocking with easy overrides. Day 30+: full enforcement. (See `followup-enforcement-model.md §1.2`) |

---

## 2) Feature Visibility Ordering

Revenue-generating features surface first. Configuration and advanced features are progressively disclosed.

### Tier 1 — Always visible (day 1, all roles)

These features generate or protect revenue. They must be accessible from the home screen / bottom navigation in ≤1 tap:

- **Lead pipeline** — current leads, stage, next follow-up due
- **Follow-up queue** — what's due today, overdue
- **Collections** — outstanding invoices, total owed, cash position
- **Quick actions** — "New Lead", "Record Payment", "Send Follow-up"

### Tier 2 — Visible after first session

These features become prominent after the user has completed at least one Tier 1 action:

- Deal and opportunity pipeline
- Employee activity (managers only)
- Reminders and escalation status
- Owner dashboard panels (owner role only)

### Tier 3 — Discoverable (surfaced on demand)

These features require navigation or search. Not on home screen by default:

- Analytics and reports
- Workflow automation builder
- Custom pipeline stages
- Team management and RBAC settings

### Tier 4 — Advanced / Expert mode (hidden by default)

Only accessible via Settings:

- API integrations and webhook configuration
- Custom object framework
- Feature flag overrides
- Audit log export

**Rule:** Moving a feature from Tier 3 to Tier 2 requires user evidence (>50% of tenants use it within 7 days of onboarding). Moving from Tier 4 to Tier 3 requires owner approval.

---

## 3) Low-Discipline Environment Handling

The system must be designed for users who will forget tasks, ignore notifications, and delay actions. This is not a failure mode — it is the expected operating condition.

### System responses to low-discipline behavior

| Behavior | System Response |
|---|---|
| Agent ignores follow-up | System re-surfaces it every time agent opens app. Follow-up count badge on pipeline screen. |
| Agent delays recording payment | Collections panel shows "unrecorded payments" count. Daily WhatsApp digest to agent includes pending items. |
| Agent doesn't update lead stage | Lead surfaces as "idle" in owner dashboard. System doesn't delete or penalize — surfaces visibility. |
| Agent doesn't check CRM for 3 days | WhatsApp digest sent at day start. Next action suggestions sent to agent's phone. |
| Owner ignores dashboard | Weekly summary sent via WhatsApp: X leads, Y follow-ups overdue, Z outstanding invoices. |

### Automation-First Default

When in doubt, the system acts — it does not wait:

- **No owner assigned?** → Auto-assign to default queue owner.
- **No follow-up scheduled?** → Auto-schedule at default SLA interval.
- **Payment reminder due?** → Auto-send if tenant has enabled WhatsApp reminders.
- **Lead idle past threshold?** → Auto-flag as at-risk; surface to manager.

The system never silently ignores a condition that has a known default action.

---

## 4) Time-to-Value Design Contract

The system must deliver a meaningful, visible result within the user's first session.

### Session 1 targets

| Milestone | Target Time | What the user sees |
|---|---|---|
| First pipeline view | < 30 seconds after login | Pre-seeded sample pipeline with 4 deals |
| First WhatsApp test | < 3 minutes | Send test message → see it appear in lead timeline |
| First stage advance | < 6 minutes | Drag/tap deal to next stage |
| "Aha moment" reached | < 10 minutes | Both WhatsApp capture AND stage advance completed |

### Feedback events (success signals shown to user)

Every first-time achievement triggers a visible success signal:

- First lead captured → banner: "Your first lead is in the system. It won't slip away."
- First follow-up completed → banner: "Follow-up done. Next one scheduled automatically."
- First payment recorded → banner: "Payment recorded. Invoice updated."
- First collection reminder sent → banner: "Reminder sent. You'll be notified when they respond."

These are not generic toasts — they reference the specific action and reinforce the system's value proposition.

### Retention hooks (after Aha moment)

1. **Daily digest opt-in**: "Get your daily lead and follow-up summary on WhatsApp — yes/no?"
2. **Saved filter view**: system auto-saves "My Leads Today" filter after first use.
3. **Teammate invite**: "Your team can see what you see — invite them now."

---

## 5) Adoption Success Criteria

The system is succeeding at adoption when all of the following are true for a tenant:

| Metric | Target |
|---|---|
| First lead captured | ≤ 10 minutes from first login |
| Follow-ups automatically maintained | ≥ 90% of open leads have a pending follow-up |
| Owner can see full activity | Owner dashboard loaded and viewed ≥ 3x in first week |
| Collections visible and improving | Outstanding invoices list viewed ≥ 2x in first week |
| Daily active usage | Agent opens app ≥ 5 days in first 2 weeks |

When these metrics are achieved, the system has earned the right to increase enforcement level from Phase 1 (soft) to Phase 2 (medium).

---

## 6) Cross-References

| Topic | Document |
|---|---|
| Zero-setup onboarding (technical) | `docs/activation-model.md` |
| ≤2 steps interaction rule | `docs/ui-foundations.md §6` |
| Gradual enforcement model | `docs/followup-enforcement-model.md §1.2` |
| Next action suggestion | `docs/followup-enforcement-model.md §2 — D. Next Action Suggestion` |
| Anti-lead loss guarantee | `docs/whatsapp-execution-model.md §11` |
| Shadow tracking | `docs/activity-control-model.md §8.1` |
| Bilingual + localization | `docs/pakistan-adapter-architecture.md §3.E, §3.F` |
| Mobile-first + low bandwidth | `docs/offline-sync.md §13`, `docs/b9-p08-mobile-responsiveness-system.md` |
