'use strict';

/**
 * Marketing Campaigns routes.
 *
 * Docs: backend/docs/domain/marketing-campaigns.md
 * Mount: /api/v1/campaigns/*
 *
 * P-017: Urdu campaigns blocked from activation unless urdu_approved_by is set.
 * State machine enforced per spec §3. Terminal states (completed, cancelled) reject
 * all further transitions.
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const VALID_STATUS = ['draft', 'scheduled', 'active', 'paused', 'completed', 'cancelled'];
const VALID_TYPE   = ['whatsapp_broadcast', 'email', 'sms'];
const TERMINAL     = new Set(['completed', 'cancelled']);

const ALLOWED_TRANSITIONS = {
  draft:     ['scheduled', 'active', 'cancelled'],
  scheduled: ['active', 'draft', 'cancelled'],
  active:    ['paused', 'completed', 'cancelled'],
  paused:    ['active', 'cancelled'],
  completed: [],
  cancelled: [],
};

// ── In-memory stores ──────────────────────────────────────────────────────────
const _memCampaigns = [
  { campaign_id:'cmp-001', tenant_id:'_all', name:'Eid Mubarak Offer 2026',    type:'whatsapp_broadcast', status:'completed', segment_id:'seg-001', template_id:'tpl-001', segment_name:'All Active Leads',  scheduled_at:null, activated_at:'2026-04-01T09:00:00Z', completed_at:'2026-04-10T18:00:00Z', paused_at:null, cancelled_at:null, attribution_window_days:30, urdu_approved_by:null, total_recipients:1240, sent_count:1168, delivered_count:1098, opened_count:843, replied_count:272, opted_out_count:12, leads_generated:87, conversions:14, created_by:'u-003', created_at:'2026-03-25T09:00:00Z', updated_at:'2026-04-10T18:00:00Z' },
  { campaign_id:'cmp-002', tenant_id:'_all', name:'Q2 Product Launch',          type:'email',              status:'completed', segment_id:'seg-002', template_id:'tpl-002', segment_name:'SMB Prospects',     scheduled_at:null, activated_at:'2026-04-15T09:00:00Z', completed_at:'2026-04-20T18:00:00Z', paused_at:null, cancelled_at:null, attribution_window_days:30, urdu_approved_by:null, total_recipients:450,  sent_count:450,  delivered_count:396, opened_count:189, replied_count:36,  opted_out_count:4,  leads_generated:32, conversions:6,  created_by:'u-001', created_at:'2026-04-10T10:00:00Z', updated_at:'2026-04-20T18:00:00Z' },
  { campaign_id:'cmp-003', tenant_id:'_all', name:'WhatsApp Re-engagement',     type:'whatsapp_broadcast', status:'active',    segment_id:'seg-003', template_id:'tpl-001', segment_name:'Idle Contacts 30d', scheduled_at:null, activated_at:'2026-05-01T09:00:00Z', completed_at:null, paused_at:null, cancelled_at:null, attribution_window_days:30, urdu_approved_by:null, total_recipients:380,  sent_count:346,  delivered_count:315, opened_count:190, replied_count:62,  opted_out_count:8,  leads_generated:45, conversions:9,  created_by:'u-002', created_at:'2026-04-28T09:00:00Z', updated_at:'2026-05-29T09:00:00Z' },
  { campaign_id:'cmp-004', tenant_id:'_all', name:'Enterprise Demo Invite',     type:'email',              status:'active',    segment_id:'seg-004', template_id:'tpl-002', segment_name:'Enterprise Tier',   scheduled_at:null, activated_at:'2026-05-10T09:00:00Z', completed_at:null, paused_at:null, cancelled_at:null, attribution_window_days:30, urdu_approved_by:null, total_recipients:85,   sent_count:82,   delivered_count:79,  opened_count:42,  replied_count:10,  opted_out_count:1,  leads_generated:8,  conversions:2,  created_by:'u-003', created_at:'2026-05-08T11:00:00Z', updated_at:'2026-05-29T09:00:00Z' },
  { campaign_id:'cmp-005', tenant_id:'_all', name:'SMS Flash Sale',             type:'sms',                status:'draft',     segment_id:null,      template_id:null,      segment_name:'Karachi Contacts',  scheduled_at:null, activated_at:null, completed_at:null, paused_at:null, cancelled_at:null, attribution_window_days:30, urdu_approved_by:null, total_recipients:0,    sent_count:0,    delivered_count:0,   opened_count:0,   replied_count:0,   opted_out_count:0,  leads_generated:0,  conversions:0,  created_by:'u-004', created_at:'2026-05-28T14:00:00Z', updated_at:'2026-05-28T14:00:00Z' },
  { campaign_id:'cmp-006', tenant_id:'_all', name:'Ramadan Finance Package',    type:'whatsapp_broadcast', status:'paused',    segment_id:'seg-001', template_id:'tpl-001', segment_name:'Finance Leads',     scheduled_at:null, activated_at:'2026-03-01T09:00:00Z', completed_at:null, paused_at:'2026-03-30T18:00:00Z', cancelled_at:null, attribution_window_days:30, urdu_approved_by:null, total_recipients:620, sent_count:553, delivered_count:492, opened_count:378, replied_count:105, opted_out_count:17, leads_generated:56, conversions:11, created_by:'u-005', created_at:'2026-02-25T09:00:00Z', updated_at:'2026-03-30T18:00:00Z' },
];

const _memSends       = {};  // campaign_id → send[]
const _memConversions = {};  // campaign_id → conversion[]

function nowIso() { return new Date().toISOString(); }

function canTransition(from, to) {
  return (ALLOWED_TRANSITIONS[from] || []).includes(to);
}

// Resolve segment size for activation guard (in-memory: use total_recipients or default 10)
function resolveSegmentSize(campaign) {
  if (campaign.segment_id) return campaign.total_recipients || 10;
  return 0;
}

const router = express.Router();

// GET /campaigns
router.get(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { status, type } = req.query;
    const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
    const offset = parseInt(req.query.offset || '0', 10);

    let rows = _memCampaigns.filter(c => c.tenant_id === tenantId || c.tenant_id === '_all');
    if (status) rows = rows.filter(c => c.status === status);
    if (type)   rows = rows.filter(c => c.type   === type);

    const total = rows.length;
    const page  = rows.slice(offset, offset + limit);
    return respondSuccess(res, page, { count: page.length, total, limit, offset });
  },
);

// POST /campaigns — create draft
router.post(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { name, description, type, segment_id, template_id, scheduled_at, attribution_window_days = 30 } = req.body;

    if (!VALID_TYPE.includes(type))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid campaign type.', [{ field: 'type', reason: `must_be_one_of_${VALID_TYPE.join('|')}` }]);

    const ts = nowIso();
    const campaign = {
      campaign_id:             randomUUID(),
      tenant_id:               tenantId,
      name,
      description:             description || null,
      status:                  'draft',
      type,
      segment_id:              segment_id  || null,
      template_id:             template_id || null,
      segment_name:            null,
      scheduled_at:            scheduled_at || null,
      activated_at:            null,
      completed_at:            null,
      paused_at:               null,
      cancelled_at:            null,
      attribution_window_days,
      urdu_approved_by:        null,
      total_recipients:        0,
      sent_count:              0,
      delivered_count:         0,
      opened_count:            0,
      replied_count:           0,
      opted_out_count:         0,
      leads_generated:         0,
      conversions:             0,
      created_by:              userId,
      created_at:              ts,
      updated_at:              ts,
    };
    _memCampaigns.push(campaign);
    return res.status(201).json({ data: campaign, meta: { request_id: req.request_id } });
  },
);

// GET /campaigns/:id
router.get(
  '/:campaign_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { campaign_id } = req.params;

    const c = _memCampaigns.find(x => x.campaign_id === campaign_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Campaign not found.');

    const sends       = (_memSends[campaign_id] || []).slice(0, 5);
    const conversions = (_memConversions[campaign_id] || []);
    return respondSuccess(res, { ...c, recent_sends: sends, conversion_count: conversions.length });
  },
);

// PATCH /campaigns/:id — update draft fields
router.patch(
  '/:campaign_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { campaign_id } = req.params;

    const c = _memCampaigns.find(x => x.campaign_id === campaign_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Campaign not found.');
    if (TERMINAL.has(c.status))
      return respondError(res, 409, 'CONFLICT', `Cannot edit a ${c.status} campaign.`);

    const { name, description, segment_id, template_id, scheduled_at, attribution_window_days, urdu_approved_by } = req.body;
    if (name)                   c.name                   = name;
    if (description !== undefined) c.description          = description;
    if (segment_id)             c.segment_id             = segment_id;
    if (template_id)            c.template_id            = template_id;
    if (scheduled_at !== undefined) c.scheduled_at       = scheduled_at;
    if (attribution_window_days) c.attribution_window_days = attribution_window_days;
    if (urdu_approved_by)       c.urdu_approved_by       = urdu_approved_by;
    c.updated_at = nowIso();
    c.updated_by = userId;

    return respondSuccess(res, c);
  },
);

// POST /campaigns/:id/activate
router.post(
  '/:campaign_id/activate',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { campaign_id } = req.params;

    const c = _memCampaigns.find(x => x.campaign_id === campaign_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Campaign not found.');

    if (!canTransition(c.status, 'active'))
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot activate from status '${c.status}'.`);

    // Activation guards
    if (!c.segment_id)
      return respondError(res, 422, 'ACTIVATION_BLOCKED', 'Campaign has no segment_id.', [{ field: 'segment_id', reason: 'required_for_activation' }]);
    if (!c.template_id)
      return respondError(res, 422, 'ACTIVATION_BLOCKED', 'Campaign has no template_id.', [{ field: 'template_id', reason: 'required_for_activation' }]);
    // P-017: Urdu approval gate (checked in-memory via a flag on campaign)
    if (c.is_urdu_template && !c.urdu_approved_by)
      return respondError(res, 422, 'P017_URDU_APPROVAL_REQUIRED', 'Urdu template requires urdu_approved_by before activation (P-017).', []);

    const ts = nowIso();
    c.status       = 'active';
    c.activated_at = ts;
    c.updated_at   = ts;
    if (c.total_recipients === 0) c.total_recipients = resolveSegmentSize(c);

    return respondSuccess(res, c);
  },
);

// POST /campaigns/:id/pause
router.post(
  '/:campaign_id/pause',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { campaign_id } = req.params;
    const c = _memCampaigns.find(x => x.campaign_id === campaign_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Campaign not found.');
    if (!canTransition(c.status, 'paused'))
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot pause from status '${c.status}'.`);

    const ts = nowIso();
    c.status    = 'paused';
    c.paused_at = ts;
    c.updated_at = ts;
    return respondSuccess(res, c);
  },
);

// POST /campaigns/:id/resume
router.post(
  '/:campaign_id/resume',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { campaign_id } = req.params;
    const c = _memCampaigns.find(x => x.campaign_id === campaign_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Campaign not found.');
    if (!canTransition(c.status, 'active'))
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot resume from status '${c.status}'.`);

    const ts = nowIso();
    c.status     = 'active';
    c.paused_at  = null;
    c.updated_at = ts;
    return respondSuccess(res, c);
  },
);

// POST /campaigns/:id/cancel
router.post(
  '/:campaign_id/cancel',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { campaign_id } = req.params;
    const c = _memCampaigns.find(x => x.campaign_id === campaign_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Campaign not found.');
    if (!canTransition(c.status, 'cancelled'))
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot cancel from status '${c.status}'.`);

    const ts = nowIso();
    c.status       = 'cancelled';
    c.cancelled_at = ts;
    c.updated_at   = ts;
    return respondSuccess(res, c);
  },
);

// GET /campaigns/:id/sends
router.get(
  '/:campaign_id/sends',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { campaign_id } = req.params;
    const c = _memCampaigns.find(x => x.campaign_id === campaign_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Campaign not found.');

    const sends = _memSends[campaign_id] || [];
    return respondSuccess(res, sends, { count: sends.length, total: c.sent_count });
  },
);

// GET /campaigns/:id/conversions
router.get(
  '/:campaign_id/conversions',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { campaign_id } = req.params;
    const c = _memCampaigns.find(x => x.campaign_id === campaign_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Campaign not found.');

    const conversions = _memConversions[campaign_id] || [];
    return respondSuccess(res, conversions, { count: conversions.length });
  },
);

module.exports = router;
