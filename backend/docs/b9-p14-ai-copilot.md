# B9-P14::AI_COPILOT_CONVERSATIONAL_SURFACE

## Scope

Defines the **AI / Copilot / Conversational Surface** archetype — 2 named AI surfaces.
Anchored to `docs/whatsapp-execution-model.md` §10 (intent detection), `services/conversation/intent.py`, `src/ai_scoring/`.

---

## 1) Archetype Structure

AI surfaces use an **insight strip + conversational panel** pattern:

```
┌─ Context header (current record or scope) ────────────────┐
├─ AI insight strip (top — advisory, always visible) ────────┤
├─ Conversational input bar (bottom) ───────────────────────┤
├─────────────────────────────────────────────────────────── ┤
│  Response / suggestion area (center)                       │
│  - Structured cards (not freeform text)                    │
│  - Action buttons linked to CRM operations                 │
│  - Confidence indicator per suggestion                     │
└───────────────────────────────────────────────────────────┘
```

**Design rules:**
- AI suggestions are always **advisory** — no action taken without explicit user confirmation.
- Confidence scores shown per suggestion — users can dismiss low-confidence items.
- All AI-triggered actions go through the same CRM operation path as manual actions (no backdoor writes).
- Conversational input accepts natural language — routed through `services/conversation/intent.py`.

---

## 2) The 2 AI / Copilot Pages

### 2.1 — AI Copilot Insight Panel

**Route:** Embedded surface — accessible from any entity detail view and the sales cockpit.
**Source modules:** `src/ai_scoring/`, `src/predictive_models/`
**Source entities:** `lead_scores`, `score_history`, `model_feature_weights`

**Purpose:** Persistent advisory strip that surfaces AI-generated insights for the currently viewed record.

**Panel structure:**

1. **Score card** — for the current lead or opportunity:
   - Score (0–100) from `lead_scores.score_value`
   - Trend: up / flat / down vs previous period
   - Top 3 score drivers (from `model_feature_weights`) — plain-language labels

2. **Next-action suggestion** — from `gateway/services/next-action.js` `toCardData()`:
   - Suggested action label (call / WhatsApp / reminder / escalate)
   - Priority badge (urgent/high/normal → red/amber/blue)
   - Due-by display (relative time)
   - `[Take action]` button → routes to appropriate flow

3. **Risk flags** (when present):
   - Idle > threshold
   - Follow-up overdue
   - SLA breach imminent
   - Each flag has a one-tap remediation action

4. **Dismiss / snooze:** User can dismiss individual suggestions. Dismissed suggestions reappear after 24 hours if underlying condition persists.

**Read model links:**
- Score: `OpportunityPipelineSnapshotRM.weighted_pipeline` for context
- Activity: `ActivityTaskOperationalRM.overdue_task_count`

**Constraint:** Scores are advisory — `DuplicateSuggestion.action = "suggest_merge"` pattern applies. No auto-action.

---

### 2.2 — Conversational CRM

**Route:** `/app/chat` (also accessible as a floating panel from any screen)
**Source module:** `services/conversation/service.py`, `services/conversation/intent.py`
**Intent classes:** `lead_inquiry` / `payment_query` / `follow_up_response` / `support_request` / `out_of_scope`

**Purpose:** Natural language interface to CRM operations — query, update, and navigate via conversation.

**Input → response flow:**

```
User types message
       ↓
ConversationalCRMService.classify_intent(message)
       ↓
Intent: lead_inquiry    → Response card: matching leads (up to 5)
Intent: payment_query   → Response card: invoice status + [Record Payment]
Intent: follow_up_response → Response card: next follow-up task + [Log Done] / [Snooze]
Intent: support_request → Response card: recent cases + [Open New Case]
Intent: out_of_scope    → Graceful fallback: "I can help with leads, payments, and follow-ups."
```

**Response card structure:**
- Record identity (name, ID)
- Key status fields (amount, stage, due date)
- 1–2 action buttons (CRM operations, ≤2 steps)
- `[Open full record]` link

**Conversation history:**
- Last 20 exchanges shown in thread view
- System messages (e.g., "I created a follow-up task") appear as timestamped cards
- History is session-scoped — not persisted between sessions (MVP)

**Pakistan-specific:**
- Input accepted in Urdu — routed through same intent classifier
- Response in locale matching user's `locale` setting (EN / UR)
- WhatsApp-received messages from `whatsapp-execution-model.md` §10 feed through same classifier before presenting in Omnichannel Inbox

---

## 3) Interaction Patterns

1. **Advisory-only AI:** Every AI suggestion includes a `[Take action]` button and a `[Dismiss]` button. No auto-execution.
2. **Confidence transparency:** Score drivers shown as plain-language feature labels — not model internals.
3. **Conversation → CRM operation:** All conversational actions call the same service methods as manual UI actions — no separate code path.
4. **Floating panel:** Conversational CRM accessible as a slide-in panel from any screen — no navigation away from current context.
5. **Out-of-scope graceful handling:** Classifier returns `out_of_scope` → friendly redirect, not an error.
6. **Bilingual input:** Urdu input processed through same intent classifier; responses returned in user's locale.

---

## SELF-QC

- **Both Archetype.md AI pages documented:** ✅ — 2.1 (Copilot Insight Panel) + 2.2 (Conversational CRM).
- **Advisory-only constraint documented (no auto-action):** ✅
- **Intent classifier integration documented:** ✅ — 5 intent classes + out-of-scope handling.
- **Confidence + score driver transparency documented:** ✅
- **Bilingual / Urdu input documented:** ✅
- **Floating panel pattern documented:** ✅

Score: **10/10**
