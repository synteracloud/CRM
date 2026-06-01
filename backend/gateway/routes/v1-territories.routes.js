'use strict';

/**
 * Territory Management routes.
 *
 * Docs: backend/docs/domain/territory-management.md
 * Mount: /api/v1/territories/*
 *
 * Covers:
 *   GET/POST       /territories
 *   GET/PATCH      /territories/:id
 *   DELETE         /territories/:id           (soft deactivate)
 *   POST           /territories/:id/rules
 *   DELETE         /territories/:id/rules/:rule_id
 *   GET            /territories/assignments
 *   POST           /territories/assignments/evaluate   (dry-run)
 *   POST           /territories/assignments/:id/reassign
 *   GET            /territories/:id/performance
 *
 * Invariants enforced in-memory:
 *   - Exactly one is_default=true territory per tenant.
 *   - TerritoryAssignment is immutable (superseded_by chain on reassign).
 *   - Manual overrides are sticky (not overridden by next auto-routing).
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const VALID_CRITERIA_TYPES = ['geographic', 'postal', 'account_segment', 'rep_assigned', 'hybrid'];
const VALID_RULE_TYPES     = ['city', 'postal_code', 'region', 'geo_polygon', 'account_industry', 'account_size', 'account_tier', 'rep_explicit', 'custom_field'];
const VALID_SUBJECT_TYPES  = ['lead', 'account', 'contact'];
const VALID_ASSIGN_REASONS = ['auto_rule_match', 'manual_override', 'conflict_resolution', 'default_fallback'];
const ADMIN_ROLES          = ['admin', 'tenant_admin', 'tenant_owner'];
const MANAGER_ROLES        = ['manager', 'admin', 'tenant_admin', 'tenant_owner'];

// ── In-memory stores ──────────────────────────────────────────────────────────
const _memTerritories = [
  { territory_id:'t-001', tenant_id:'_all', name:'Punjab North',     criteria_type:'geographic',   criteria_value:{ provinces:['Punjab'], cities:['Lahore','Sheikhupura','Gujranwala'] }, assigned_reps:['u-001','u-004'], primary_manager:'u-003', parent_id:null, is_default:false, is_active:true, routing_priority:1,  created_by:'u-001', created_at:'2025-01-01T00:00:00Z', updated_at:'2025-01-01T00:00:00Z' },
  { territory_id:'t-002', tenant_id:'_all', name:'Punjab South',     criteria_type:'geographic',   criteria_value:{ provinces:['Punjab'], cities:['Multan','Bahawalpur','Faisalabad'] },  assigned_reps:['u-002'],         primary_manager:'u-003', parent_id:null, is_default:false, is_active:true, routing_priority:2,  created_by:'u-001', created_at:'2025-01-01T00:00:00Z', updated_at:'2025-01-01T00:00:00Z' },
  { territory_id:'t-003', tenant_id:'_all', name:'Sindh',            criteria_type:'geographic',   criteria_value:{ provinces:['Sindh'] },                                               assigned_reps:['u-001','u-002'], primary_manager:'u-005', parent_id:null, is_default:false, is_active:true, routing_priority:3,  created_by:'u-001', created_at:'2025-01-01T00:00:00Z', updated_at:'2025-01-01T00:00:00Z' },
  { territory_id:'t-004', tenant_id:'_all', name:'Rest of Pakistan', criteria_type:'rep_assigned', criteria_value:{},                                                                      assigned_reps:['u-003','u-005'], primary_manager:'u-005', parent_id:null, is_default:true,  is_active:true, routing_priority:99, created_by:'u-001', created_at:'2025-01-01T00:00:00Z', updated_at:'2025-01-01T00:00:00Z' },
];

const _memRules = [
  { rule_id:'r-001', territory_id:'t-001', tenant_id:'_all', rule_type:'region', field:'lead.province', operator:'in', value:{ provinces:['Punjab'] }, created_at:'2025-01-01T00:00:00Z', updated_at:'2025-01-01T00:00:00Z' },
  { rule_id:'r-002', territory_id:'t-001', tenant_id:'_all', rule_type:'city',   field:'lead.city',     operator:'in', value:{ cities:['Lahore','Sheikhupura','Gujranwala'] }, created_at:'2025-01-01T00:00:00Z', updated_at:'2025-01-01T00:00:00Z' },
  { rule_id:'r-003', territory_id:'t-002', tenant_id:'_all', rule_type:'region', field:'lead.province', operator:'in', value:{ provinces:['Punjab'] }, created_at:'2025-01-01T00:00:00Z', updated_at:'2025-01-01T00:00:00Z' },
  { rule_id:'r-004', territory_id:'t-003', tenant_id:'_all', rule_type:'region', field:'lead.province', operator:'in', value:{ provinces:['Sindh'] }, created_at:'2025-01-01T00:00:00Z', updated_at:'2025-01-01T00:00:00Z' },
];

const _memAssignments = [];
let   _assignCursor   = {}; // per-territory round-robin cursor

function nowIso() { return new Date().toISOString(); }

// ── Rule evaluation (mirrors services/territories/entities.py) ─────────────
function evalRule(rule, subject) {
  const { rule_type, operator, value = {} } = rule;
  if (rule_type === 'geo_polygon') return false; // v1: always no-match
  if (rule_type === 'rep_explicit') return true;

  const toList = (arr) => (arr || []).map(v => String(v).toLowerCase());

  if (rule_type === 'city') {
    const cities = toList(value.cities);
    const subj   = String(subject.city || '').toLowerCase();
    if (operator === 'eq' || operator === 'in') return cities.includes(subj);
    if (operator === 'not_in') return !cities.includes(subj);
  }
  if (rule_type === 'postal_code') {
    const codes = toList(value.codes);
    const subj  = String(subject.postal_code || '');
    if (operator === 'eq' || operator === 'in') return codes.includes(subj.toLowerCase());
    if (operator === 'starts_with') return codes.some(c => subj.startsWith(c));
  }
  if (rule_type === 'region') {
    const provinces = toList(value.provinces);
    const subj      = String(subject.province || subject.region || '').toLowerCase();
    if (operator === 'eq' || operator === 'in') return provinces.includes(subj);
  }
  if (rule_type === 'account_industry') {
    const vals = toList(value.industries);
    return vals.includes(String(subject.industry || '').toLowerCase());
  }
  if (rule_type === 'account_tier') {
    const vals = toList(value.tiers);
    return vals.includes(String(subject.tier || '').toLowerCase());
  }
  if (rule_type === 'account_size') {
    const vals = (value.sizes || []).map(String);
    return vals.includes(String(subject.employee_count || subject.account_size || ''));
  }
  if (rule_type === 'custom_field') {
    const cf      = subject.custom_fields || {};
    const subj_cf = String(cf[value.key] || '').toLowerCase();
    const match_vs = toList(value.match_values);
    if (operator === 'eq' || operator === 'in') return match_vs.includes(subj_cf);
    if (operator === 'contains') return match_vs.some(m => subj_cf.includes(m));
  }
  return false;
}

function evalTerritory(territory, rules, subject) {
  if (!rules || rules.length === 0) return true;
  return rules.every(r => evalRule(r, subject));
}

function rankCandidates(candidates, rulesByTerr) {
  return [...candidates].sort((a, b) => {
    const prioA = a.routing_priority ?? 99;
    const prioB = b.routing_priority ?? 99;
    if (prioA !== prioB) return prioA - prioB;
    const ruleCountA = (rulesByTerr[a.territory_id] || []).length;
    const ruleCountB = (rulesByTerr[b.territory_id] || []).length;
    if (ruleCountA !== ruleCountB) return ruleCountB - ruleCountA; // more rules = more specific
    return a.territory_id.localeCompare(b.territory_id);
  });
}

function assignRep(territory, cursor) {
  const reps = territory.assigned_reps || [];
  if (!reps.length) return territory.primary_manager || null;
  const idx = (cursor || 0) % reps.length;
  _assignCursor[territory.territory_id] = idx + 1;
  return reps[idx];
}

// ── Router ─────────────────────────────────────────────────────────────────────
const router = express.Router();

// GET /territories — list
router.get(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.TERRITORIES_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { is_active } = req.query;

    let rows = _memTerritories.filter(t => t.tenant_id === tenantId || t.tenant_id === '_all');
    if (is_active !== undefined) rows = rows.filter(t => String(t.is_active) === is_active);
    rows = rows.sort((a, b) => (a.routing_priority ?? 99) - (b.routing_priority ?? 99));

    return respondSuccess(res, rows, { count: rows.length });
  },
);

// POST /territories — create
router.post(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.TERRITORIES_ADMIN]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { name, description, criteria_type, criteria_value = {}, assigned_reps = [], primary_manager, is_default = false, routing_priority = 99, parent_id } = req.body;

    if (!VALID_CRITERIA_TYPES.includes(criteria_type))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid criteria_type.', [{ field: 'criteria_type', reason: `must_be_one_of_${VALID_CRITERIA_TYPES.join('|')}` }]);

    const ts = nowIso();

    // Enforce single default — atomically unset any previous default
    if (is_default) {
      _memTerritories
        .filter(t => (t.tenant_id === tenantId || t.tenant_id === '_all') && t.is_default)
        .forEach(t => { t.is_default = false; t.updated_at = ts; });
    }

    const territory = {
      territory_id:    randomUUID(),
      tenant_id:       tenantId,
      name,
      description:     description || null,
      parent_id:       parent_id || null,
      criteria_type,
      criteria_value,
      assigned_reps,
      primary_manager: primary_manager || null,
      is_default,
      is_active:       true,
      routing_priority,
      created_by:      userId,
      created_at:      ts,
      updated_at:      ts,
    };
    _memTerritories.push(territory);
    return res.status(201).json({ data: territory, meta: { request_id: req.request_id } });
  },
);

// GET /territories/assignments — list active assignments
router.get(
  '/assignments',
  requestValidationMiddleware(),
  requireScopes([SCOPES.TERRITORIES_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { subject_type, territory_id, assigned_rep_id } = req.query;

    let rows = _memAssignments.filter(a => a.tenant_id === tenantId && a.is_active);
    if (subject_type)    rows = rows.filter(a => a.subject_type    === subject_type);
    if (territory_id)    rows = rows.filter(a => a.territory_id    === territory_id);
    if (assigned_rep_id) rows = rows.filter(a => a.assigned_rep_id === assigned_rep_id);

    return respondSuccess(res, rows, { count: rows.length });
  },
);

// POST /territories/assignments/evaluate — dry-run evaluation
router.post(
  '/assignments/evaluate',
  requestValidationMiddleware(['subject']),
  requireScopes([SCOPES.TERRITORIES_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { subject } = req.body;

    const territories = _memTerritories.filter(t => (t.tenant_id === tenantId || t.tenant_id === '_all') && t.is_active);
    const rulesByTerr = {};
    _memRules.forEach(r => {
      if (!rulesByTerr[r.territory_id]) rulesByTerr[r.territory_id] = [];
      rulesByTerr[r.territory_id].push(r);
    });

    const candidates = territories.filter(t => evalTerritory(t, rulesByTerr[t.territory_id] || [], subject));
    const ranked     = rankCandidates(candidates, rulesByTerr);

    const defaultTerr = territories.find(t => t.is_default);
    const winner      = ranked[0] || defaultTerr || null;
    const reason      = ranked.length > 1 ? 'conflict_resolved' : ranked.length === 1 ? 'single_match' : 'default_fallback';

    return respondSuccess(res, {
      winner,
      candidates: ranked,
      reason,
      matched_count: ranked.length,
    });
  },
);

// POST /territories/assignments/:id/reassign — manual override
router.post(
  '/assignments/:assignment_id/reassign',
  requestValidationMiddleware(['territory_id']),
  requireScopes([SCOPES.TERRITORIES_WRITE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const userRole = req.auth.role || 'agent';
    const { assignment_id } = req.params;
    const { territory_id, assigned_rep_id, note } = req.body;

    if (!MANAGER_ROLES.includes(userRole))
      return respondError(res, 403, 'FORBIDDEN', 'Manual territory reassignment requires manager or admin role.');

    const old = _memAssignments.find(a => a.assignment_id === assignment_id && a.tenant_id === tenantId);
    if (!old) return respondError(res, 404, 'NOT_FOUND', 'Assignment not found.');

    const territory = _memTerritories.find(t => t.territory_id === territory_id && (t.tenant_id === tenantId || t.tenant_id === '_all'));
    if (!territory) return respondError(res, 404, 'NOT_FOUND', 'Territory not found.');

    const ts  = nowIso();
    const newA = {
      assignment_id:    randomUUID(),
      tenant_id:        tenantId,
      subject_type:     old.subject_type,
      subject_id:       old.subject_id,
      territory_id,
      assigned_rep_id:  assigned_rep_id || assignRep(territory, _assignCursor[territory_id]),
      assignment_reason:'manual_override',
      superseded_by:    null,
      is_active:        true,
      effective_at:     ts,
      created_by:       userId,
      created_at:       ts,
    };
    // Supersede old assignment
    old.is_active     = false;
    old.superseded_by = newA.assignment_id;

    _memAssignments.push(newA);
    return res.status(201).json({ data: newA, superseded: old, meta: { request_id: req.request_id } });
  },
);

// GET /territories/:id — detail with rules
router.get(
  '/:territory_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.TERRITORIES_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { territory_id } = req.params;

    const t = _memTerritories.find(x => x.territory_id === territory_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!t) return respondError(res, 404, 'NOT_FOUND', 'Territory not found.');

    const rules       = _memRules.filter(r => r.territory_id === territory_id);
    const assignments = _memAssignments.filter(a => a.territory_id === territory_id && a.is_active);

    return respondSuccess(res, { ...t, rules, active_assignment_count: assignments.length });
  },
);

// PATCH /territories/:id — update
router.patch(
  '/:territory_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.TERRITORIES_ADMIN]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { territory_id } = req.params;
    const { name, description, assigned_reps, primary_manager, routing_priority, is_default, criteria_value } = req.body;

    const t = _memTerritories.find(x => x.territory_id === territory_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!t) return respondError(res, 404, 'NOT_FOUND', 'Territory not found.');

    const ts = nowIso();

    if (is_default === true && !t.is_default) {
      // Atomically unset previous default
      _memTerritories
        .filter(x => (x.tenant_id === tenantId || x.tenant_id === '_all') && x.is_default && x.territory_id !== territory_id)
        .forEach(x => { x.is_default = false; x.updated_at = ts; });
      t.is_default = true;
    }
    if (name)              t.name              = name;
    if (description)       t.description       = description;
    if (assigned_reps)     t.assigned_reps     = assigned_reps;
    if (primary_manager)   t.primary_manager   = primary_manager;
    if (routing_priority !== undefined) t.routing_priority = routing_priority;
    if (criteria_value)    t.criteria_value    = criteria_value;
    t.updated_at = ts;

    return respondSuccess(res, t);
  },
);

// DELETE /territories/:id — soft deactivate
router.delete(
  '/:territory_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.TERRITORIES_ADMIN]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { territory_id } = req.params;

    const t = _memTerritories.find(x => x.territory_id === territory_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!t) return respondError(res, 404, 'NOT_FOUND', 'Territory not found.');
    if (t.is_default) return respondError(res, 409, 'CONFLICT', 'Cannot deactivate the default territory.');

    t.is_active   = false;
    t.updated_at  = nowIso();

    return respondSuccess(res, { territory_id, deactivated: true });
  },
);

// POST /territories/:id/rules — add rule
router.post(
  '/:territory_id/rules',
  requestValidationMiddleware(['rule_type', 'value']),
  requireScopes([SCOPES.TERRITORIES_ADMIN]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { territory_id } = req.params;
    const { rule_type, field, operator, value } = req.body;

    if (!VALID_RULE_TYPES.includes(rule_type))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid rule_type.', [{ field: 'rule_type', reason: `must_be_one_of_${VALID_RULE_TYPES.join('|')}` }]);

    const t = _memTerritories.find(x => x.territory_id === territory_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!t) return respondError(res, 404, 'NOT_FOUND', 'Territory not found.');

    const ts   = nowIso();
    const rule = {
      rule_id:      randomUUID(),
      territory_id,
      tenant_id:    tenantId,
      rule_type,
      field:        field || null,
      operator:     operator || null,
      value,
      created_at:   ts,
      updated_at:   ts,
    };
    _memRules.push(rule);
    return res.status(201).json({ data: rule, meta: { request_id: req.request_id } });
  },
);

// DELETE /territories/:id/rules/:rule_id
router.delete(
  '/:territory_id/rules/:rule_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.TERRITORIES_ADMIN]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { territory_id, rule_id } = req.params;

    const idx = _memRules.findIndex(r => r.rule_id === rule_id && r.territory_id === territory_id);
    if (idx === -1) return respondError(res, 404, 'NOT_FOUND', 'Rule not found.');

    _memRules.splice(idx, 1);
    return respondSuccess(res, { rule_id, deleted: true });
  },
);

// GET /territories/:id/performance — metrics
router.get(
  '/:territory_id/performance',
  requestValidationMiddleware(),
  requireScopes([SCOPES.TERRITORIES_READ]),
  async (req, res) => {
    const { territory_id } = req.params;
    const t = _memTerritories.find(x => x.territory_id === territory_id);
    if (!t) return respondError(res, 404, 'NOT_FOUND', 'Territory not found.');

    // Demo metrics — populated by daily aggregation job in production
    return respondSuccess(res, {
      territory_id,
      metric_date:                      new Date().toISOString().slice(0, 10),
      open_leads:                        t.territory_id === 't-001' ? 38 : t.territory_id === 't-002' ? 29 : t.territory_id === 't-003' ? 24 : 15,
      leads_added_today:                 Math.floor(Math.random() * 5) + 1,
      leads_converted:                   t.territory_id === 't-001' ? 8  : t.territory_id === 't-002' ? 5  : t.territory_id === 't-003' ? 6  : 3,
      conversion_rate:                   t.territory_id === 't-001' ? 21 : t.territory_id === 't-002' ? 17 : t.territory_id === 't-003' ? 25 : 20,
      avg_follow_up_response_time_hours: 3.2,
      overdue_follow_ups:                t.territory_id === 't-001' ? 4  : 2,
      open_invoices_amount_pkr:          1240000,
      collected_amount_pkr:              880000,
      collection_rate:                   71,
      computed_at:                       new Date().toISOString(),
    });
  },
);

module.exports = router;
