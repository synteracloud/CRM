<!-- OWNERSHIP
PRIMARY FOR: AI/ML feature definitions; LeadScore, ChurnPrediction, CLVEstimate entity schemas; scoring model contracts; feature weight registry; copilot suggestion generation logic; model versioning and confidence score rules.
DEFERS TO: opportunities-pipeline.md (Opportunity stage definitions and probability weights); followup-enforcement-model.md (follow-up escalation — copilot surfaces these but does not own them); cases-domain.md (case escalation — copilot surfaces these but does not own them); domain-model.md (base entity fields); event-catalog.md (canonical event names); read-models.md (CaseSLAOperationalRM, LeadFunnelPerformanceRM etc — the source read models for AI feature extraction).
DO NOT RE-DEFINE: Opportunity stages → opportunities-pipeline.md; Follow-up enforcement → followup-enforcement-model.md; Case SLA → cases-domain.md; Read model schemas → read-models.md.
-->

# AI / Predictive Models Domain Spec

## Purpose

This document is the canonical backend spec for the **AI & Predictive Models Service** — the domain that produces lead scores, churn predictions, CLV estimates, and copilot suggestions. All outputs are **advisory only**: no model output triggers an automatic action. Every suggestion is surfaced to a human with an explicit [Take Action] or [Dismiss] affordance.

**Build gates:** This doc must exist before any of the following pages can be implemented: M-01 `ai-copilot.html`, M-02 `ai-insights.html`, H-07 `report-builder.html` (AI metric section).

**Advisory constraint (non-negotiable):** All AI suggestions must carry a `confidence_score` (0.0–1.0) and an `evidence_anchor` (the specific CRM data point that drove the suggestion). No ungrounded inference. No speculative outputs based on data not in the tenant's own CRM records.

---

## 1) Core Principles

### 1.1 Advisory-Only Architecture
The system operates in **observation mode only**:
- AI reads CRM data → produces a ranked list of scored entities + suggestions.
- The frontend surfaces these as advisory cards with [Take Action] + [Dismiss].
- Taking action navigates the user to the relevant CRM record — the AI never modifies records directly.
- Every model output is tagged with the model version, confidence score, and evidence anchor.

### 1.2 Pakistan-Specific Model Calibration
- Scoring features are weighted for Pakistani SMB deal patterns: relationship-first selling, WhatsApp as primary communication, longer decision cycles for Enterprise, cash payment preference.
- Default models are rule-based (v1) for interpretability. ML models are Phase 6+ additions.
- All feature weight registries are read-only via the API — they cannot be modified without a model version bump.

### 1.3 Non-negotiable Invariants
1. No AI output has `confidence_score > 1.0` or `< 0.0`.
2. Every `CopilotSuggestion` must have an `evidence_anchor` (a specific CRM entity ID or metric name). Suggestions with no evidence are rejected at the service layer.
3. `LeadScore.score` is always 0–100 (integer).
4. Model outputs are tenant-scoped — one tenant's data never influences another tenant's model.
5. Stale scores: if a lead has not been re-scored within `model.recompute_interval_hours`, the score is flagged as stale (`is_stale = true`) in the API response.

---

## 2) Entity Model

### 2.1 LeadScore

```
LeadScore
├── score_id             : UUID (PK)
├── tenant_id            : str (required)
├── lead_id              : UUID (FK → Lead, required)
├── model_id             : str (FK → ScoringModel.model_key, e.g. "lead_score_v1")
├── score                : int (0–100)
├── score_band           : ScoreBand enum (hot | warm | cold | disqualified)
│                          — hot: 75–100 | warm: 50–74 | cold: 25–49 | disqualified: 0–24
├── trend                : ScoreTrend enum (rising | stable | falling)
├── trend_delta          : int (score change vs previous computation, nullable)
├── top_drivers          : FeatureContribution[] (see §2.5, max 5)
├── confidence_score     : decimal(3,2) (0.00–1.00)
├── is_stale             : bool (true if computed_at < now() - model.recompute_interval_hours)
├── computed_at          : datetime
└── created_at           : datetime
```

### 2.2 ChurnPrediction

```
ChurnPrediction
├── prediction_id        : UUID (PK)
├── tenant_id            : str (required)
├── account_id           : UUID (FK → Account, required)
├── model_id             : str (FK → ScoringModel.model_key, e.g. "churn_predict_v1")
├── churn_probability    : decimal(4,3) (0.000–1.000)
├── risk_band            : ChurnRiskBand enum (high | medium | low)
│                          — high: >= 0.65 | medium: 0.35–0.64 | low: < 0.35
├── top_drivers          : FeatureContribution[] (see §2.5, max 5)
├── recommended_action   : str (max 255 — e.g. "Schedule renewal call within 14 days")
├── confidence_score     : decimal(3,2)
├── evidence_anchor      : str (e.g. "account.last_invoice_paid_at = 47 days ago")
├── is_stale             : bool
├── computed_at          : datetime
└── created_at           : datetime
```

### 2.3 CLVEstimate

```
CLVEstimate
├── estimate_id          : UUID (PK)
├── tenant_id            : str (required)
├── account_id           : UUID (FK → Account, required)
├── model_id             : str (FK → ScoringModel.model_key, e.g. "clv_estimate_v1")
├── estimated_clv        : decimal(18,2) (PKR — lifetime value estimate)
├── clv_horizon_months   : int (the time horizon used, default 24)
├── confidence_score     : decimal(3,2)
├── evidence_anchor      : str (e.g. "avg monthly revenue: PKR 45,000 × 24 months × retention_rate 0.82")
├── is_stale             : bool
├── computed_at          : datetime
└── created_at           : datetime
```

### 2.4 CopilotSuggestion

```
CopilotSuggestion
├── suggestion_id        : UUID (PK)
├── tenant_id            : str (required)
├── target_user_id       : UUID (FK → User — who this suggestion is for)
├── suggestion_type      : SuggestionType enum (next_action | risk_flag | deal_nudge | follow_up_overdue | sla_breach_alert | stale_deal)
├── priority             : SuggestionPriority enum (urgent | high | medium | low)
├── title                : str (max 100 — e.g. "Call Imran Butt — negotiation stalled")
├── body                 : str (max 500 — detailed advisory text)
├── action_label         : str (max 50 — CTA label, e.g. "Open Lead", "Record Payment")
├── action_href          : str (relative URL in the CRM, e.g. "app/leads-detail.html?id=l-005")
├── evidence_anchor      : str (max 500 — the specific CRM data driving this suggestion)
├── entity_type          : str (e.g. "lead", "case", "opportunity", "invoice")
├── entity_id            : UUID (the specific entity this suggestion is about)
├── confidence_score     : decimal(3,2)
├── is_dismissed         : bool (default false — set true when user clicks Dismiss)
├── dismissed_at         : datetime (nullable)
├── is_actioned          : bool (default false — set true when user clicks Take Action)
├── actioned_at          : datetime (nullable)
├── expires_at           : datetime (nullable — suggestion auto-expires if no longer relevant)
├── created_at           : datetime
└── updated_at           : datetime
```

### 2.5 FeatureContribution

Embedded sub-entity used in `top_drivers` arrays:

```
FeatureContribution
├── feature_key   : str (e.g. "deal_stage", "follow_up_count", "days_since_contact")
├── feature_label : str (human-readable, e.g. "Deal Stage: Negotiation")
├── contribution  : int (relative weight, 0–100)
├── direction     : ContributionDirection enum (positive | negative)
└── value         : str (the actual value observed, e.g. "Negotiation", "12 days")
```

### 2.6 ScoringModel

```
ScoringModel
├── model_key            : str (PK — e.g. "lead_score_v1")
├── model_type           : ModelType enum (lead_score | churn_predict | clv_estimate)
├── version              : str (e.g. "1.0.0")
├── description          : str
├── algorithm            : AlgorithmType enum (rule_based | logistic_regression | gradient_boost)
│                          — v1 all models are rule_based; ML models are Phase 6+
├── feature_weights      : FeatureWeight[] (see §3.2)
├── recompute_interval_hours : int (how often scores are recomputed, default 24)
├── is_active            : bool
├── created_at           : datetime
└── updated_at           : datetime
```

---

## 3) Model Specifications

### 3.1 Lead Scoring Model v1 (`lead_score_v1`)

**Algorithm:** Rule-based weighted sum. Score = Σ (feature_value × feature_weight), clamped to 0–100.

| Feature key | Weight | Formula |
|---|---|---|
| `deal_stage` | 28 | OPEN=0, qualifying=10, nurturing=15, proposal=22, negotiation=28, won=0 (excluded), lost=0 |
| `follow_up_count` | 18 | min(18, follow_up_task_count × 3) |
| `estimated_value` | 14 | PKR 0–50K=5, 50K–200K=10, 200K–500K=12, 500K+=14 |
| `days_since_last_contact` | 12 | 0–3 days=12, 4–7=9, 8–14=6, 15–30=3, 30+=0 |
| `email_open_rate` | 8 | campaign email opens / sends for this contact, scaled to 0–8 |
| `source_quality` | 7 | inbound/referral=7, whatsapp_inbound=6, social=4, cold_outreach=2 |
| `account_tier` | 6 | Enterprise=6, Mid-Market=4, SMB=2, Individual=1 |
| `call_attempts` | 4 | min(4, call_count) |
| `whatsapp_replies` | 3 | min(3, whatsapp_reply_count) |

**Score band mapping:**
- 75–100: `hot` (priority: urgent)
- 50–74: `warm` (priority: high)
- 25–49: `cold` (priority: medium)
- 0–24: `disqualified` (priority: low)

### 3.2 Churn Prediction Model v1 (`churn_predict_v1`)

**Algorithm:** Rule-based risk scoring. Risk factors summed; mapped to probability band.

| Feature key | Risk contribution |
|---|---|
| `days_since_last_invoice_paid` | > 60 days: +0.35; 31–60: +0.20; 15–30: +0.10 |
| `open_support_cases` | > 3 open cases: +0.25; 1–3: +0.10 |
| `subscription_status` | `past_due`: +0.30; `paused`: +0.20 |
| `days_since_last_activity` | > 45 days: +0.15; 30–45: +0.08 |
| `follow_up_breach_count` | > 2 breached: +0.10 |
| `nps_score_low` | Last NPS < 6: +0.15 |

Risk bands: Sum >= 0.65 = `high`; 0.35–0.64 = `medium`; < 0.35 = `low`.

### 3.3 CLV Estimation Model v1 (`clv_estimate_v1`)

**Algorithm:** Historical revenue projection.

```
avg_monthly_revenue = sum(Invoice.total_amount WHERE status = paid) / months_since_first_invoice
retention_rate      = 1.0 - (churn_probability from ChurnPrediction v1)
clv_estimate        = avg_monthly_revenue × clv_horizon_months × retention_rate
```

Minimum history required: 3 months of paid invoices. If insufficient history: `confidence_score = 0.30` and `evidence_anchor` notes the limited data.

---

## 4) Copilot Suggestion Generation

### 4.1 Suggestion Types and Triggers

| Type | Trigger | Priority | Evidence anchor example |
|---|---|---|---|
| `follow_up_overdue` | `FollowupTask.status = overdue` | urgent | "follow_up task #ft-042 overdue by 3 days" |
| `sla_breach_alert` | `Case.sla_state = breached` | urgent | "case CAS-2026-001 SLA resolution breached 4 hours ago" |
| `deal_nudge` | `Opportunity.close_date < today + 7 days AND is_won = false` | high | "opportunity close date in 5 days, stage = negotiation" |
| `next_action` | `LeadScore.score >= 75 AND no_open_follow_up_task` | high | "lead score 82/100, no follow-up scheduled" |
| `stale_deal` | `Opportunity.updated_at < today - 30 days AND is_closed = false` | medium | "opportunity not updated in 34 days" |
| `risk_flag` | `ChurnPrediction.risk_band = high` | high | "account churn probability 0.71 — 2 unpaid invoices" |

### 4.2 Suggestion Refresh
- Suggestions are re-generated every 6 hours per tenant by the `copilot_refresh` scanner job.
- Dismissed suggestions (`is_dismissed = true`) are not re-generated until the underlying condition changes.
- A suggestion auto-expires when the triggering condition is resolved (e.g., overdue follow-up completed → `expires_at` set to now()).

### 4.3 Conversational Query Response
The copilot endpoint (`POST /api/v1/ai/copilot/query`) accepts a natural-language query, classifies intent, and returns structured response:

```
Intent classes (v1, rule-based regex classifier):
  lead      → return matching lead records + scores
  payment   → return overdue invoices
  followup  → return overdue follow-up tasks
  case      → return open cases + SLA state
  oob       → return canned help text
```

No LLM is used in v1. Responses are template-based using live CRM data. LLM integration is Phase 6.

---

## 5) API Endpoints

### Lead Scores

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/ai/scores/leads` | JWT | Any | List lead scores for tenant (sorted by score DESC). |
| `GET` | `/api/v1/ai/scores/leads/{lead_id}` | JWT | Any | Score detail + feature contributions for one lead. |
| `POST` | `/api/v1/ai/scores/leads/{lead_id}/recompute` | JWT | `manager`, `admin` | Force recompute score for one lead. |

### Churn Predictions

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/ai/predictions/churn` | JWT | `manager`, `admin` | List churn predictions sorted by probability DESC. |
| `GET` | `/api/v1/ai/predictions/churn/{account_id}` | JWT | `manager`, `admin` | Churn prediction detail for one account. |

### CLV Estimates

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/ai/estimates/clv` | JWT | `manager`, `admin` | List CLV estimates sorted by estimated_clv DESC. |
| `GET` | `/api/v1/ai/estimates/clv/{account_id}` | JWT | `manager`, `admin` | CLV estimate detail for one account. |

### Copilot Suggestions

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/ai/copilot/suggestions` | JWT | Any | List active suggestions for the authenticated user. |
| `POST` | `/api/v1/ai/copilot/suggestions/{id}/dismiss` | JWT | Any | Dismiss a suggestion. |
| `POST` | `/api/v1/ai/copilot/suggestions/{id}/action` | JWT | Any | Mark suggestion as actioned (user clicked Take Action). |
| `POST` | `/api/v1/ai/copilot/query` | JWT | Any | Conversational query — intent classification + structured response. |

### Model Registry (read-only)

| Method | Path | Auth | Role | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/ai/models` | JWT | `manager`, `admin` | List active scoring models + feature weight registries. |
| `GET` | `/api/v1/ai/models/{model_key}` | JWT | `manager`, `admin` | Full model spec + feature weights. |

---

## 6) RBAC Role Gates

| Operation | `sales_rep` | `agent` | `manager` | `admin` |
|---|---|---|---|---|
| View own lead scores | ✓ | — | ✓ | ✓ |
| View all lead scores | — | — | ✓ | ✓ |
| View churn predictions | — | — | ✓ | ✓ |
| View CLV estimates | — | — | ✓ | ✓ |
| View / dismiss / action suggestions | ✓ | ✓ | ✓ | ✓ |
| Conversational query | ✓ | ✓ | ✓ | ✓ |
| View model registry | — | — | ✓ | ✓ |
| Force recompute | — | — | ✓ | ✓ |

---

## 7) Events Emitted

| Event | Trigger |
|---|---|
| `ai.lead_scored` | Lead score computed or recomputed. |
| `ai.churn_predicted` | Churn prediction computed. |
| `ai.clv_estimated` | CLV estimate computed. |
| `ai.suggestion_generated` | Copilot suggestion created. |
| `ai.suggestion_dismissed` | User dismissed a suggestion. |
| `ai.suggestion_actioned` | User clicked Take Action on a suggestion. |
| `ai.query_answered` | Copilot conversational query processed. |

---

## 8) Scanner Jobs

### 8.1 Lead Score Recompute Job
- **Schedule:** Every 6 hours.
- **Action:** For all leads with `status NOT IN (won, lost, disqualified)` and `score.computed_at < now() - 6h`: recompute `lead_score_v1`. Create new `LeadScore` record. Set `is_stale = false`. Flag previous record as stale.

### 8.2 Churn Prediction Recompute Job
- **Schedule:** Daily at 03:00 PKT.
- **Action:** For all active accounts: recompute `churn_predict_v1`. Create new `ChurnPrediction` record.

### 8.3 CLV Recompute Job
- **Schedule:** Weekly (Sunday 02:00 PKT).
- **Action:** For all accounts with ≥3 months of invoice history: recompute `clv_estimate_v1`. Create new `CLVEstimate` record.

### 8.4 Copilot Suggestion Refresh Job
- **Schedule:** Every 6 hours.
- **Action:**
  1. For each user in each tenant: evaluate all suggestion triggers (§4.1).
  2. Create `CopilotSuggestion` records for new triggers not already in `is_dismissed = false` state.
  3. Expire resolved suggestions: set `expires_at = now()` where underlying condition is no longer true.

---

## 9) Implementation Acceptance Checklist

- [ ] `LeadScore`, `ChurnPrediction`, `CLVEstimate`, `CopilotSuggestion`, `ScoringModel` entities created.
- [ ] `lead_score_v1` formula implemented: weighted sum across all 9 features, clamped to 0–100.
- [ ] Score band mapping correct: hot/warm/cold/disqualified thresholds.
- [ ] `churn_predict_v1` formula implemented: feature risk contributions summed → probability band.
- [ ] `clv_estimate_v1` formula implemented: avg_monthly_revenue × horizon × (1 - churn_probability).
- [ ] All model outputs carry `confidence_score` (0.0–1.0) and `evidence_anchor` string.
- [ ] Suggestions with no `evidence_anchor` rejected at service layer (422).
- [ ] Dismissed suggestions are not re-generated until condition changes.
- [ ] Conversational query endpoint: intent classifier (5 classes) returns structured CRM data.
- [ ] All API endpoints respect RBAC role gates (§6).
- [ ] All events in §7 emitted via activity log.
- [ ] Scanner jobs (lead score, churn, CLV, copilot refresh) scheduled and testable.
- [ ] Tenant isolation enforced: no cross-tenant data leakage in any model computation.
- [ ] `is_stale = true` correctly flagged when score age exceeds `model.recompute_interval_hours`.
- [ ] Model registry is read-only via API — no PATCH/POST/DELETE on `ScoringModel`.
