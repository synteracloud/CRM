'use strict';
/**
 * AI / Predictive Models routes — /api/v1/ai
 *
 * Spec: backend/docs/domain/ai-predictive-models.md
 * Advisory-only: no AI output triggers an automatic action.
 *
 * In-memory fallback active when DB_DISABLED=true.
 * All outputs carry confidence_score (0.0–1.0) and evidence_anchor.
 */

const express = require('express');
const { respondSuccess, respondError } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const router = express.Router();

// ── Seeded in-memory data ────────────────────────────────────────────────────

const _LEAD_SCORES = [
  { score_id:'ls-001', tenant_id:'t-001', lead_id:'l-005', model_id:'lead_score_v1', score:82, score_band:'hot',          trend:'rising',  trend_delta:7,  confidence_score:0.85, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'deal_stage', feature_label:'Deal Stage: negotiation', contribution:28, direction:'positive', value:'negotiation' }, { feature_key:'follow_up_count', feature_label:'Follow-ups: 6', contribution:18, direction:'positive', value:'6' }, { feature_key:'estimated_value', feature_label:'Value: PKR 500K', contribution:14, direction:'positive', value:'500000' }] },
  { score_id:'ls-002', tenant_id:'t-001', lead_id:'l-012', model_id:'lead_score_v1', score:78, score_band:'hot',          trend:'stable',  trend_delta:1,  confidence_score:0.85, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'deal_stage', feature_label:'Deal Stage: negotiation', contribution:28, direction:'positive', value:'negotiation' }, { feature_key:'estimated_value', feature_label:'Value: PKR 650K', contribution:14, direction:'positive', value:'650000' }, { feature_key:'follow_up_count', feature_label:'Follow-ups: 5', contribution:15, direction:'positive', value:'5' }] },
  { score_id:'ls-003', tenant_id:'t-001', lead_id:'l-017', model_id:'lead_score_v1', score:74, score_band:'warm',         trend:'rising',  trend_delta:5,  confidence_score:0.85, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'deal_stage', feature_label:'Deal Stage: proposal', contribution:22, direction:'positive', value:'proposal' }, { feature_key:'estimated_value', feature_label:'Value: PKR 750K', contribution:14, direction:'positive', value:'750000' }, { feature_key:'follow_up_count', feature_label:'Follow-ups: 4', contribution:12, direction:'positive', value:'4' }] },
  { score_id:'ls-004', tenant_id:'t-001', lead_id:'l-004', model_id:'lead_score_v1', score:66, score_band:'warm',         trend:'stable',  trend_delta:0,  confidence_score:0.85, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'deal_stage', feature_label:'Deal Stage: proposal', contribution:22, direction:'positive', value:'proposal' }, { feature_key:'source_quality', feature_label:'Source: manual', contribution:7, direction:'positive', value:'manual' }] },
  { score_id:'ls-005', tenant_id:'t-001', lead_id:'l-011', model_id:'lead_score_v1', score:63, score_band:'warm',         trend:'falling', trend_delta:-4, confidence_score:0.85, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'deal_stage', feature_label:'Deal Stage: proposal', contribution:22, direction:'positive', value:'proposal' }, { feature_key:'days_since_last_contact', feature_label:'Last Contact: 12 days', contribution:6, direction:'negative', value:'12' }] },
  { score_id:'ls-006', tenant_id:'t-001', lead_id:'l-015', model_id:'lead_score_v1', score:54, score_band:'warm',         trend:'rising',  trend_delta:6,  confidence_score:0.85, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'deal_stage', feature_label:'Deal Stage: qualifying', contribution:10, direction:'positive', value:'qualifying' }] },
  { score_id:'ls-007', tenant_id:'t-001', lead_id:'l-003', model_id:'lead_score_v1', score:48, score_band:'cold',         trend:'stable',  trend_delta:2,  confidence_score:0.85, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'deal_stage', feature_label:'Deal Stage: qualifying', contribution:10, direction:'positive', value:'qualifying' }] },
  { score_id:'ls-008', tenant_id:'t-001', lead_id:'l-002', model_id:'lead_score_v1', score:38, score_band:'cold',         trend:'falling', trend_delta:-8, confidence_score:0.85, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'days_since_last_contact', feature_label:'Last Contact: 8 days', contribution:6, direction:'negative', value:'8' }] },
  { score_id:'ls-009', tenant_id:'t-001', lead_id:'l-001', model_id:'lead_score_v1', score:22, score_band:'disqualified', trend:'falling', trend_delta:-5, confidence_score:0.80, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'deal_stage', feature_label:'Deal Stage: new', contribution:0, direction:'negative', value:'new' }] },
  { score_id:'ls-010', tenant_id:'t-001', lead_id:'l-014', model_id:'lead_score_v1', score:18, score_band:'disqualified', trend:'falling', trend_delta:-3, confidence_score:0.75, is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'deal_stage', feature_label:'Deal Stage: qualifying', contribution:10, direction:'positive', value:'qualifying' }, { feature_key:'source_quality', feature_label:'Source: campaign', contribution:3, direction:'negative', value:'campaign' }] },
];

const _CHURN_PREDICTIONS = [
  { prediction_id:'cp-001', tenant_id:'t-001', account_id:'acc-001', model_id:'churn_predict_v1', churn_probability:0.710, risk_band:'high',   confidence_score:0.82, evidence_anchor:'last invoice paid 67 days ago; subscription status: past_due; open support cases: 4', recommended_action:'Schedule renewal call within 14 days and review open invoices.', is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'days_since_last_invoice_paid', feature_label:'Invoice overdue 67 days', contribution:35, direction:'negative', value:'67' }] },
  { prediction_id:'cp-002', tenant_id:'t-001', account_id:'acc-002', model_id:'churn_predict_v1', churn_probability:0.480, risk_band:'medium', confidence_score:0.80, evidence_anchor:'last invoice paid 38 days ago; subscription status: active; open support cases: 2', recommended_action:'Send relationship check-in WhatsApp within 7 days.', is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'days_since_last_invoice_paid', feature_label:'Invoice overdue 38 days', contribution:20, direction:'negative', value:'38' }] },
  { prediction_id:'cp-003', tenant_id:'t-001', account_id:'acc-003', model_id:'churn_predict_v1', churn_probability:0.220, risk_band:'low',    confidence_score:0.84, evidence_anchor:'last invoice paid 12 days ago; subscription status: active; open support cases: 0', recommended_action:'Account is healthy — maintain standard follow-up cadence.', is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'subscription_status', feature_label:'Subscription: active', contribution:0, direction:'positive', value:'active' }] },
  { prediction_id:'cp-004', tenant_id:'t-001', account_id:'acc-004', model_id:'churn_predict_v1', churn_probability:0.680, risk_band:'high',   confidence_score:0.79, evidence_anchor:'last invoice paid 72 days ago; subscription status: paused; open support cases: 1', recommended_action:'Schedule renewal call within 14 days and review open invoices.', is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[{ feature_key:'subscription_status', feature_label:'Subscription: paused', contribution:20, direction:'negative', value:'paused' }] },
  { prediction_id:'cp-005', tenant_id:'t-001', account_id:'acc-005', model_id:'churn_predict_v1', churn_probability:0.120, risk_band:'low',    confidence_score:0.88, evidence_anchor:'last invoice paid 5 days ago; subscription status: active; open support cases: 0', recommended_action:'Account is healthy — maintain standard follow-up cadence.', is_stale:false, computed_at:'2026-05-30T00:00:00Z', top_drivers:[] },
];

const _CLV_ESTIMATES = [
  { estimate_id:'clv-001', tenant_id:'t-001', account_id:'acc-001', model_id:'clv_estimate_v1', estimated_clv:1296000.00, clv_horizon_months:24, confidence_score:0.72, evidence_anchor:'avg monthly revenue: PKR 90,000 × 24 months × retention_rate 0.60', is_stale:false, computed_at:'2026-05-30T00:00:00Z' },
  { estimate_id:'clv-002', tenant_id:'t-001', account_id:'acc-002', model_id:'clv_estimate_v1', estimated_clv:2246400.00, clv_horizon_months:24, confidence_score:0.76, evidence_anchor:'avg monthly revenue: PKR 180,000 × 24 months × retention_rate 0.52', is_stale:false, computed_at:'2026-05-30T00:00:00Z' },
  { estimate_id:'clv-003', tenant_id:'t-001', account_id:'acc-003', model_id:'clv_estimate_v1', estimated_clv:3168000.00, clv_horizon_months:24, confidence_score:0.81, evidence_anchor:'avg monthly revenue: PKR 165,000 × 24 months × retention_rate 0.80', is_stale:false, computed_at:'2026-05-30T00:00:00Z' },
  { estimate_id:'clv-004', tenant_id:'t-001', account_id:'acc-004', model_id:'clv_estimate_v1', estimated_clv:950400.00,  clv_horizon_months:24, confidence_score:0.68, evidence_anchor:'avg monthly revenue: PKR 120,000 × 24 months × retention_rate 0.33', is_stale:false, computed_at:'2026-05-30T00:00:00Z' },
  { estimate_id:'clv-005', tenant_id:'t-001', account_id:'acc-005', model_id:'clv_estimate_v1', estimated_clv:4233600.00, clv_horizon_months:24, confidence_score:0.87, evidence_anchor:'avg monthly revenue: PKR 200,000 × 24 months × retention_rate 0.88', is_stale:false, computed_at:'2026-05-30T00:00:00Z' },
];

const _COPILOT_SUGGESTIONS = [
  { suggestion_id:'sug-001', tenant_id:'t-001', target_user_id:'u-001', suggestion_type:'follow_up_overdue', priority:'urgent', title:'Overdue Follow-up: Tariq Mehmood', body:'Follow-up task ft-042 is overdue by 3 days. Lead score: 22/100. Risk of lead going cold.', action_label:'View Follow-up', action_href:'app/followups.html', evidence_anchor:'follow_up task #ft-042 overdue by 3 days; lead_id: l-001', entity_type:'lead', entity_id:'l-001', confidence_score:0.92, is_dismissed:false, dismissed_at:null, is_actioned:false, actioned_at:null, expires_at:null, created_at:'2026-05-30T06:00:00Z', updated_at:'2026-05-30T06:00:00Z' },
  { suggestion_id:'sug-002', tenant_id:'t-001', target_user_id:'u-002', suggestion_type:'deal_nudge',        priority:'high',   title:'Close Date This Week: Imran Butt', body:'Opportunity close date is in 4 days. Stage: negotiation. Score 82/100 — highest in portfolio.', action_label:'Open Lead',    action_href:'app/leads-detail.html?id=l-005', evidence_anchor:'opportunity close date in 4 days; stage=negotiation; lead_score=82', entity_type:'lead', entity_id:'l-005', confidence_score:0.88, is_dismissed:false, dismissed_at:null, is_actioned:false, actioned_at:null, expires_at:null, created_at:'2026-05-30T06:00:00Z', updated_at:'2026-05-30T06:00:00Z' },
  { suggestion_id:'sug-003', tenant_id:'t-001', target_user_id:'u-001', suggestion_type:'risk_flag',         priority:'high',   title:'High Churn Risk: City Pharma Ltd', body:'Account churn probability is 0.71. 67-day payment overdue + subscription past_due. Revenue at risk: PKR 1.3M.', action_label:'View Account',  action_href:'app/accounts-detail.html?id=acc-001', evidence_anchor:'account.churn_probability=0.71; last_invoice_paid_at=67 days ago; subscription=past_due', entity_type:'account', entity_id:'acc-001', confidence_score:0.85, is_dismissed:false, dismissed_at:null, is_actioned:false, actioned_at:null, expires_at:null, created_at:'2026-05-30T06:00:00Z', updated_at:'2026-05-30T06:00:00Z' },
  { suggestion_id:'sug-004', tenant_id:'t-001', target_user_id:'u-002', suggestion_type:'next_action',       priority:'high',   title:'Hot Lead — No Follow-up: Mariam Zaidi', body:'Lead score 78/100 (hot band). No open follow-up task scheduled. Stage: negotiation.', action_label:'Schedule Follow-up', action_href:'app/leads-detail.html?id=l-012', evidence_anchor:'lead_score=78; no_open_follow_up_task=true; stage=negotiation', entity_type:'lead', entity_id:'l-012', confidence_score:0.87, is_dismissed:false, dismissed_at:null, is_actioned:false, actioned_at:null, expires_at:null, created_at:'2026-05-30T06:00:00Z', updated_at:'2026-05-30T06:00:00Z' },
  { suggestion_id:'sug-005', tenant_id:'t-001', target_user_id:'u-003', suggestion_type:'stale_deal',        priority:'medium', title:'Stale Deal: Waqar Ijaz (34 days)', body:'Opportunity not updated in 34 days. Stage: proposal. Value: PKR 750K. Consider re-engagement.', action_label:'Open Lead',    action_href:'app/leads-detail.html?id=l-017', evidence_anchor:'opportunity.updated_at=34 days ago; stage=proposal; estimated_value=750000', entity_type:'lead', entity_id:'l-017', confidence_score:0.80, is_dismissed:false, dismissed_at:null, is_actioned:false, actioned_at:null, expires_at:null, created_at:'2026-05-30T06:00:00Z', updated_at:'2026-05-30T06:00:00Z' },
  { suggestion_id:'sug-006', tenant_id:'t-001', target_user_id:'u-001', suggestion_type:'sla_breach_alert',  priority:'urgent', title:'SLA Breached: CAS-2026-001', body:'Case CAS-2026-001 SLA resolution breached 4 hours ago. Priority: High. Assigned to u-001.', action_label:'Open Case',    action_href:'app/cases-detail.html?id=c-001', evidence_anchor:'case CAS-2026-001 SLA resolution breached 4 hours ago; sla_state=breached', entity_type:'case', entity_id:'c-001', confidence_score:0.95, is_dismissed:false, dismissed_at:null, is_actioned:false, actioned_at:null, expires_at:null, created_at:'2026-05-30T06:00:00Z', updated_at:'2026-05-30T06:00:00Z' },
];

const _SCORING_MODELS = [
  { model_key:'lead_score_v1',    model_type:'lead_score',    version:'1.0.0', algorithm:'rule_based', recompute_interval_hours:6,   is_active:true,  description:'Rule-based weighted-sum lead scoring for Pakistani SMB deals.' },
  { model_key:'churn_predict_v1', model_type:'churn_predict', version:'1.0.0', algorithm:'rule_based', recompute_interval_hours:24,  is_active:true,  description:'Rule-based churn risk scoring for active accounts.' },
  { model_key:'clv_estimate_v1',  model_type:'clv_estimate',  version:'1.0.0', algorithm:'rule_based', recompute_interval_hours:168, is_active:true,  description:'Historical revenue projection: avg_monthly × horizon × retention_rate.' },
];

// Mutable copies for in-memory operations
let leadScores      = [..._LEAD_SCORES];
let churnPredictions = [..._CHURN_PREDICTIONS];
let clvEstimates    = [..._CLV_ESTIMATES];
let suggestions     = [..._COPILOT_SUGGESTIONS];

// ── Lead scores ──────────────────────────────────────────────────────────────

router.get('/scores/leads', requireScopes([SCOPES.AI_SCORES_READ]), (req, res) => {
  const { score_band, lead_id, limit = 50 } = req.query;
  let results = leadScores.filter(s => s.tenant_id === (req.auth?.tenant_id || 't-001'));
  if (score_band) results = results.filter(s => s.score_band === score_band);
  if (lead_id)    results = results.filter(s => s.lead_id === lead_id);
  results = results.sort((a, b) => b.score - a.score).slice(0, Number(limit));
  respondSuccess(res, results, { total_items: results.length, total_pages: 1, page: 1, limit: Number(limit) });
});

router.get('/scores/leads/:lead_id', requireScopes([SCOPES.AI_SCORES_READ]), (req, res) => {
  const score = leadScores.find(
    s => s.lead_id === req.params.lead_id && s.tenant_id === (req.auth?.tenant_id || 't-001')
  );
  if (!score) return respondError(res, 'not_found', `No score found for lead ${req.params.lead_id}`, [], 404);
  respondSuccess(res, score);
});

router.post('/scores/leads/:lead_id/recompute', requireScopes([SCOPES.AI_SCORES_RECOMPUTE]), (req, res) => {
  const idx = leadScores.findIndex(
    s => s.lead_id === req.params.lead_id && s.tenant_id === (req.auth?.tenant_id || 't-001')
  );
  if (idx === -1) return respondError(res, 'not_found', `No score found for lead ${req.params.lead_id}`, [], 404);
  // Simulate recompute: set is_stale=false and update computed_at
  leadScores[idx] = { ...leadScores[idx], is_stale: false, computed_at: new Date().toISOString() };
  respondSuccess(res, leadScores[idx]);
});

// ── Churn predictions ────────────────────────────────────────────────────────

router.get('/predictions/churn', requireScopes([SCOPES.AI_PREDICTIONS_READ]), (req, res) => {
  const { risk_band } = req.query;
  let results = churnPredictions.filter(p => p.tenant_id === (req.auth?.tenant_id || 't-001'));
  if (risk_band) results = results.filter(p => p.risk_band === risk_band);
  results = results.sort((a, b) => b.churn_probability - a.churn_probability);
  respondSuccess(res, results, { total_items: results.length, total_pages: 1, page: 1 });
});

router.get('/predictions/churn/:account_id', requireScopes([SCOPES.AI_PREDICTIONS_READ]), (req, res) => {
  const pred = churnPredictions.find(
    p => p.account_id === req.params.account_id && p.tenant_id === (req.auth?.tenant_id || 't-001')
  );
  if (!pred) return respondError(res, 'not_found', `No churn prediction for account ${req.params.account_id}`, [], 404);
  respondSuccess(res, pred);
});

// ── CLV estimates ────────────────────────────────────────────────────────────

router.get('/estimates/clv', requireScopes([SCOPES.AI_CLV_READ]), (req, res) => {
  let results = clvEstimates.filter(e => e.tenant_id === (req.auth?.tenant_id || 't-001'));
  results = results.sort((a, b) => b.estimated_clv - a.estimated_clv);
  respondSuccess(res, results, { total_items: results.length, total_pages: 1, page: 1 });
});

router.get('/estimates/clv/:account_id', requireScopes([SCOPES.AI_CLV_READ]), (req, res) => {
  const est = clvEstimates.find(
    e => e.account_id === req.params.account_id && e.tenant_id === (req.auth?.tenant_id || 't-001')
  );
  if (!est) return respondError(res, 'not_found', `No CLV estimate for account ${req.params.account_id}`, [], 404);
  respondSuccess(res, est);
});

// ── Copilot suggestions ──────────────────────────────────────────────────────

// must be declared BEFORE /:id routes to avoid collision
router.post('/copilot/query', requireScopes([SCOPES.AI_COPILOT]), (req, res) => {
  const { query } = req.body || {};
  if (!query) return respondError(res, 'validation_error', 'query field is required', [], 422);

  const text = query.toLowerCase();
  let intent = 'oob';
  if (/lead|prospect|contact/.test(text)) intent = 'lead';
  else if (/payment|invoice|collection|paid|bill/.test(text)) intent = 'payment';
  else if (/follow[\- ]?up|overdue|task/.test(text)) intent = 'followup';
  else if (/case|ticket|support/.test(text)) intent = 'case';

  const intentSummaries = {
    lead:     'Showing matching lead records and scores.',
    payment:  'Showing overdue invoices requiring attention.',
    followup: 'Showing overdue follow-up tasks.',
    case:     'Showing open support cases.',
    oob:      'I can help with leads, payments, follow-ups, and support cases.',
  };

  respondSuccess(res, {
    query,
    intent,
    summary:    intentSummaries[intent],
    model_id:   'copilot_query_v1',
    records:    [],
    actions:    [],
    answered_at: new Date().toISOString(),
  });
});

router.get('/copilot/suggestions', requireScopes([SCOPES.AI_COPILOT]), (req, res) => {
  const { priority, suggestion_type, include_dismissed = false } = req.query;
  const userId = req.auth?.sub || 'u-001';
  let results = suggestions.filter(s => s.tenant_id === (req.auth?.tenant_id || 't-001'));
  if (!include_dismissed || include_dismissed === 'false') results = results.filter(s => !s.is_dismissed);
  if (priority)        results = results.filter(s => s.priority === priority);
  if (suggestion_type) results = results.filter(s => s.suggestion_type === suggestion_type);
  // Sort by priority weight
  const WEIGHT = { urgent: 4, high: 3, medium: 2, low: 1 };
  results = results.sort((a, b) => (WEIGHT[b.priority] || 0) - (WEIGHT[a.priority] || 0));
  respondSuccess(res, results, { total_items: results.length });
});

router.post('/copilot/suggestions/:id/dismiss', requireScopes([SCOPES.AI_COPILOT]), (req, res) => {
  const idx = suggestions.findIndex(s => s.suggestion_id === req.params.id);
  if (idx === -1) return respondError(res, 'not_found', `Suggestion ${req.params.id} not found`, [], 404);
  suggestions[idx] = { ...suggestions[idx], is_dismissed: true, dismissed_at: new Date().toISOString(), updated_at: new Date().toISOString() };
  respondSuccess(res, suggestions[idx]);
});

router.post('/copilot/suggestions/:id/action', requireScopes([SCOPES.AI_COPILOT]), (req, res) => {
  const idx = suggestions.findIndex(s => s.suggestion_id === req.params.id);
  if (idx === -1) return respondError(res, 'not_found', `Suggestion ${req.params.id} not found`, [], 404);
  suggestions[idx] = { ...suggestions[idx], is_actioned: true, actioned_at: new Date().toISOString(), updated_at: new Date().toISOString() };
  respondSuccess(res, suggestions[idx]);
});

// ── Model registry (read-only) ────────────────────────────────────────────────

router.get('/models', requireScopes([SCOPES.AI_MODELS_READ]), (req, res) => {
  respondSuccess(res, _SCORING_MODELS, { total_items: _SCORING_MODELS.length });
});

router.get('/models/:model_key', requireScopes([SCOPES.AI_MODELS_READ]), (req, res) => {
  const model = _SCORING_MODELS.find(m => m.model_key === req.params.model_key);
  if (!model) return respondError(res, 'not_found', `Model ${req.params.model_key} not found`, [], 404);
  respondSuccess(res, model);
});

module.exports = router;
