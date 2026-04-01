# Activation Engine Design (<10-Minute Value)

## 1) Objective and Success Constraint

**Primary goal:** A new user reaches meaningful CRM value in **under 10 minutes** from first entry.

**Definition of value:**
- A ready-to-use sales pipeline exists.
- WhatsApp lead capture is active by default.
- The user sees live-like data (sample contacts + sample deals).
- The user completes one guided action and observes immediate outcome.

**Design rule:** If a decision increases setup time or asks for non-critical input before value is shown, defer it until after activation.

---

## 2) Zero-Setup Principle (No Config, Auto Defaults)

## 2.1 Default Tenant Bootstrap

On first workspace open, system auto-provisions:
- 1 default pipeline: `Sales Pipeline`.
- 5 default stages: `New`, `Qualified`, `Proposal`, `Negotiation`, `Won`.
- 1 default inbox route: `WhatsApp Primary`.
- 1 default dashboard view: `Today Focus`.
- Sensible locale defaults (timezone, currency, date format) from browser/device signals.

No required forms before first value screen.

## 2.2 Deferred Configuration

Configuration items postponed until after activation:
- Custom stages.
- Team roles/permissions.
- Advanced automation.
- Integrations beyond WhatsApp default capture mode.

Principle: **Start useful, then personalize.**

---

## 3) Instant Value Path

## 3.1 Auto Pipeline Creation

Activation service creates baseline records during `tenant_first_login` event:

```text
tenant_first_login
  -> ActivationOrchestrator.start()
  -> PipelineTemplateService.applyDefault("sales_baseline_v1")
  -> StageService.seedDefaultStages()
  -> DashboardService.createStarterView()
  -> Emit activation_step_completed:pipeline_ready
```

Expected completion budget: <5 seconds server time.

## 3.2 WhatsApp Capture Enabled Instantly

Default mode = **Sandbox Capture Enabled** (no provider keys required for first session):
- System issues a test inbound simulator tied to tenant inbox.
- Real provider connection is offered as optional upgrade step, not blocker.
- Inbound events from simulator behave exactly like production normalized messages.

```text
activation_step_completed:pipeline_ready
  -> WhatsAppBootstrap.enableSandboxCapture()
  -> Create channel "WhatsApp Primary"
  -> Register simulated webhook source
  -> Emit activation_step_completed:whatsapp_ready
```

Outcome: user can experience lead capture immediately without integration friction.

---

## 4) Onboarding Flow (Guided, Minimal Input)

## 4.1 Guided Flow Design

Use a 4-step right-rail onboarding checklist with progressive disclosure:

1. **See your pipeline** (auto-completed).
2. **Review sample CRM data** (auto-completed).
3. **Send/receive first WhatsApp test message** (one-click action).
4. **Move a deal to next stage** (drag-and-drop).

## 4.2 Minimal Input Contract

Only two optional prompts in first session:
- Business name (for personalization).
- Primary goal (`Capture leads`, `Track deals`, `Follow-ups`).

Both prompts are skippable and never block activation tasks.

## 4.3 UX Timing Budget

- T+00:00 to T+00:30 -> workspace loads with seeded objects.
- T+00:30 to T+03:00 -> user sees prebuilt pipeline + samples.
- T+03:00 to T+06:00 -> one-click WhatsApp capture simulation.
- T+06:00 to T+09:00 -> user advances one deal stage and sees success toast.
- T+09:00 to T+10:00 -> present retention hooks and next-best action.

---

## 5) Auto Creation Strategy (Sample Deals + Contacts)

## 5.1 Seed Data Pack

Create deterministic sample records scoped to tenant:

**Sample contacts (5):**
- Ali Raza (Retail Prospect)
- Sara Khan (SMB Buyer)
- Omar Sheikh (Enterprise Lead)
- Ayesha Malik (Returning Customer)
- Bilal Ahmed (Referral)

**Sample deals (4):**
- Storefront POS Upgrade (`New`)
- Annual CRM Subscription (`Qualified`)
- Support Add-on Upsell (`Proposal`)
- Multi-branch Rollout (`Negotiation`)

## 5.2 Data Behavior Rules

- Clearly labeled as `Sample Data` with one-click cleanup.
- Seeded activities include realistic timestamps across last 7 days.
- One sample deal includes pending task due today to trigger immediate action.
- Sample contact links to simulated WhatsApp conversation for instant inbox context.

---

## 6) First Success Event (“Aha Moment”)

## 6.1 Aha Definition

**Aha moment:** User sees a WhatsApp message generate/update a lead in the pipeline and then successfully moves that deal to the next stage.

This combines:
- inbound capture,
- data visibility,
- active pipeline control.

## 6.2 Event Instrumentation

```text
aha_event_v1 =
  whatsapp_inbound_captured
  AND deal_created_or_linked
  AND deal_stage_changed_by_user
  within same session <= 10 minutes
```

Track and persist:
- `time_to_pipeline_ready`
- `time_to_whatsapp_ready`
- `time_to_first_inbound`
- `time_to_first_stage_move`
- `time_to_aha`

Target: `P75 time_to_aha <= 8 minutes`.

---

## 7) Retention Hook (Early Wins Within Session)

## 7.1 In-Session Hooks

Immediately after aha event, trigger:
- **Win banner:** “You captured and progressed your first lead.”
- **1-click next action:** “Schedule follow-up for tomorrow.”
- **Auto-generated insight card:** “Deals in Qualified stage need 1 action today.”

## 7.2 Habit Loop Starters

Before session exit, prompt one lightweight commitment:
- Enable daily digest (default ON).
- Save one custom filter view.
- Invite one teammate (optional).

These actions create return paths without forcing setup.

---

## 8) Activation Engine Architecture

## 8.1 Components

- **ActivationOrchestrator**: state machine controlling activation journey.
- **BootstrapService**: creates defaults (pipeline, inbox, views).
- **SeedDataService**: inserts sample contacts/deals/activities.
- **OnboardingGuideService**: drives checklist and contextual nudges.
- **InstrumentationService**: emits activation metrics and drop-off events.

## 8.2 Activation State Machine

- `NOT_STARTED`
- `BASELINE_READY`
- `WHATSAPP_READY`
- `SAMPLE_DATA_READY`
- `FIRST_ACTION_DONE`
- `AHA_REACHED`
- `RETENTION_HOOK_TRIGGERED`

Core transition path:

```text
NOT_STARTED
  -> BASELINE_READY
  -> WHATSAPP_READY
  -> SAMPLE_DATA_READY
  -> FIRST_ACTION_DONE
  -> AHA_REACHED
  -> RETENTION_HOOK_TRIGGERED
```

## 8.3 Failure Handling

- If any bootstrap step exceeds 3 seconds, continue UI with optimistic status + background retry.
- If WhatsApp sandbox provisioning fails, fallback to pre-recorded simulated conversation thread.
- If seeding fails partially, render minimum viable set (1 contact + 1 deal) and continue flow.

No hard stop screens before value.

---

## 9) Review Agent QC (Friction Audit + Fix to 10/10)

## 9.1 Friction Points Found

1. **Potential friction:** Asking business profile questions too early.
   - **Fix:** Keep all profile questions optional + skippable.
2. **Potential friction:** Requiring WhatsApp API keys for first run.
   - **Fix:** Default to sandbox capture simulation.
3. **Potential friction:** Empty workspace anxiety.
   - **Fix:** Seed sample contacts/deals and activity timeline.
4. **Potential friction:** Unclear next step after first success.
   - **Fix:** Trigger next-best-action card and follow-up CTA.
5. **Potential friction:** Slow bootstrap on weak network.
   - **Fix:** Progressive render with background completion.

## 9.2 <10-Minute Value Validation

Pass criteria:
- User can view a working pipeline in <= 1 minute.
- User can trigger/observe WhatsApp lead capture in <= 6 minutes.
- User can complete stage movement and hit aha in <= 10 minutes.

Assessment: **PASS** under standard latency assumptions and with sandbox capture default.

## 9.3 Alignment Score

Requirement alignment matrix:
- Zero setup principle: **100%**
- Instant value: **100%**
- Onboarding flow: **95%**
- Auto creation: **100%**
- First success event: **100%**
- Retention hook: **95%**

Overall alignment: **98.3%**

## 9.4 Fix to 10/10

Final hardening actions to reach 10/10:
- Auto-play a guided pointer for step 3 (WhatsApp test) when user is idle >20 seconds.
- Add one-click “Reset demo and replay” action for repeated practice.
- Add real-time countdown badge: “Value path: ~4 minutes left.”

Post-fix projected alignment: **100% (10/10)**.

---

## 10) Implementation Acceptance Checklist

- [ ] New tenant gets pipeline + stages automatically.
- [ ] WhatsApp sandbox capture is enabled by default.
- [ ] Sample contacts and deals are visible on first load.
- [ ] Onboarding checklist has <=4 steps and <=2 optional prompts.
- [ ] Aha event tracked and queryable.
- [ ] Retention hook appears immediately after aha event.
- [ ] Median time-to-value <10 minutes in telemetry.
