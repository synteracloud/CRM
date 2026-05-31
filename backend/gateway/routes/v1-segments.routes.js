'use strict';

/**
 * Campaign Segments routes.
 *
 * Docs: backend/docs/domain/marketing-campaigns.md §4
 * Mount: /api/v1/segments/*
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const VALID_ENTITY_TYPES = ['lead', 'contact'];

const _memSegments = [
  { segment_id:'seg-001', tenant_id:'_all', name:'All Active Leads',   entity_type:'lead',    rules:[{ rule_id:'r1', field:'lead.stage', operator:'in', value:['qualifying','nurturing','proposal','negotiation'], logic:'and' }], estimated_size:847, last_validated_at:'2026-05-01T00:00:00Z', is_dynamic:true,  created_by:'u-001', created_at:'2026-01-01T00:00:00Z', updated_at:'2026-05-01T00:00:00Z' },
  { segment_id:'seg-002', tenant_id:'_all', name:'SMB Prospects',       entity_type:'contact', rules:[{ rule_id:'r2', field:'contact.account_tier', operator:'in', value:['smb','mid_market'], logic:'and' }], estimated_size:312, last_validated_at:'2026-04-15T00:00:00Z', is_dynamic:true,  created_by:'u-001', created_at:'2026-02-01T00:00:00Z', updated_at:'2026-04-15T00:00:00Z' },
  { segment_id:'seg-003', tenant_id:'_all', name:'Idle Contacts 30d',   entity_type:'contact', rules:[{ rule_id:'r3', field:'contact.last_activity_days', operator:'gte', value:30, logic:'and' }], estimated_size:380, last_validated_at:'2026-04-28T00:00:00Z', is_dynamic:true,  created_by:'u-002', created_at:'2026-03-01T00:00:00Z', updated_at:'2026-04-28T00:00:00Z' },
  { segment_id:'seg-004', tenant_id:'_all', name:'Enterprise Tier',     entity_type:'contact', rules:[{ rule_id:'r4', field:'contact.account_tier', operator:'eq', value:'enterprise', logic:'and' }], estimated_size:85,  last_validated_at:'2026-05-10T00:00:00Z', is_dynamic:false, created_by:'u-003', created_at:'2026-04-01T00:00:00Z', updated_at:'2026-05-10T00:00:00Z' },
  { segment_id:'seg-005', tenant_id:'_all', name:'WhatsApp Opted-in',   entity_type:'contact', rules:[{ rule_id:'r5', field:'contact.whatsapp_opted_in', operator:'eq', value:true, logic:'and' }], estimated_size:843, last_validated_at:'2026-05-29T00:00:00Z', is_dynamic:true,  created_by:'u-001', created_at:'2026-01-01T00:00:00Z', updated_at:'2026-05-29T00:00:00Z' },
];

function nowIso() { return new Date().toISOString(); }

const router = express.Router();

// GET /segments
router.get(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const rows = _memSegments.filter(s => s.tenant_id === tenantId || s.tenant_id === '_all');
    return respondSuccess(res, rows, { count: rows.length });
  },
);

// POST /segments
router.post(
  '/',
  requestValidationMiddleware(['name', 'entity_type']),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { name, description, entity_type, rules = [], is_dynamic = true } = req.body;

    if (!VALID_ENTITY_TYPES.includes(entity_type))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid entity_type.', [{ field: 'entity_type', reason: 'must_be_lead_or_contact' }]);

    const ts = nowIso();
    const segment = {
      segment_id:        randomUUID(),
      tenant_id:         tenantId,
      name,
      description:       description || null,
      entity_type,
      rules,
      estimated_size:    0,
      last_validated_at: null,
      is_dynamic,
      created_by:        userId,
      created_at:        ts,
      updated_at:        ts,
    };
    _memSegments.push(segment);
    return res.status(201).json({ data: segment, meta: { request_id: req.request_id } });
  },
);

// GET /segments/:id
router.get(
  '/:segment_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { segment_id } = req.params;
    const s = _memSegments.find(x => x.segment_id === segment_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!s) return respondError(res, 404, 'NOT_FOUND', 'Segment not found.');
    return respondSuccess(res, s);
  },
);

// PATCH /segments/:id
router.patch(
  '/:segment_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { segment_id } = req.params;
    const s = _memSegments.find(x => x.segment_id === segment_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!s) return respondError(res, 404, 'NOT_FOUND', 'Segment not found.');

    const { name, description, rules, is_dynamic } = req.body;
    if (name)             s.name        = name;
    if (description)      s.description = description;
    if (rules)            s.rules       = rules;
    if (is_dynamic !== undefined) s.is_dynamic = is_dynamic;
    s.updated_at = nowIso();
    return respondSuccess(res, s);
  },
);

// POST /segments/:id/validate
router.post(
  '/:segment_id/validate',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { segment_id } = req.params;
    const s = _memSegments.find(x => x.segment_id === segment_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!s) return respondError(res, 404, 'NOT_FOUND', 'Segment not found.');

    // Demo validation: use estimated_size or default
    const size    = s.estimated_size || Math.floor(Math.random() * 500) + 10;
    const ts      = nowIso();
    s.estimated_size    = size;
    s.last_validated_at = ts;
    s.updated_at        = ts;

    return respondSuccess(res, {
      segment_id,
      estimated_size: size,
      last_validated_at: ts,
      sample: [
        { contact_id: 'c-001', display_name: 'Tariq Mehmood',  city: 'Lahore'  },
        { contact_id: 'c-002', display_name: 'Nadia Hussain',  city: 'Karachi' },
        { contact_id: 'c-003', display_name: 'Kamran Iqbal',   city: 'Lahore'  },
      ],
    });
  },
);

module.exports = router;
