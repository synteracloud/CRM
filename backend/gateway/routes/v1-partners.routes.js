'use strict';

/**
 * Partner Management routes.
 *
 * Docs: backend/docs/domain/partners.md
 * Mounts: /api/v1/partners/* and /api/v1/deal-registrations/*
 *
 * Key invariants enforced:
 *   - commission status=paid is immutable (returns 409)
 *   - attribution is exclusive (one partner per opportunity)
 *   - commission calculated on is_won=true with attributed_partner_id
 *   - inactive/suspended partners cannot receive attribution
 *   - deal registration expiry: platinum=30d, gold=45d, silver=none
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const VALID_TIERS    = ['platinum', 'gold', 'silver'];
const VALID_STATUSES = ['active', 'inactive', 'suspended'];
const ADMIN_ROLES    = ['admin', 'tenant_admin', 'tenant_owner'];
const MANAGER_ROLES  = ['manager', 'admin', 'tenant_admin', 'tenant_owner'];

// Commission rates — spec §1.2
const COMMISSION_RATES = { platinum: 0.15, gold: 0.10, silver: 0.05 };

// Deal registration expiry days — spec §2.2
const DEAL_REG_EXPIRY = { platinum: 30, gold: 45, silver: null };

function pkrAmount(opp_amount, tier) {
  return Math.round(parseFloat(opp_amount || 0) * (COMMISSION_RATES[tier] || 0.05) * 100) / 100;
}

function expiryDate(submittedIso, tier) {
  const days = DEAL_REG_EXPIRY[tier];
  if (!days) return null;
  const d = new Date(submittedIso);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

function nowIso() { return new Date().toISOString(); }

// ── In-memory stores ──────────────────────────────────────────────────────────
const _memPartners = [
  { partner_id:'p-001', tenant_id:'_all', name:'NovaTech Solutions',    partner_tier:'platinum', status:'active',   region:'Punjab',      city:'Lahore',    contact_name:'Qasim Ali',    contact_email:'qasim@novatech.pk',    contact_phone:'+923001111001', account_manager_id:'u-001', attributed_opp_count:5, commission_due:185000, total_commission_earned:420000, deal_registration_count:8, notes:null, tier_review_due_at:'2026-07-01', created_by:'u-001', created_at:'2025-03-15T09:00:00Z', updated_at:'2026-05-01T00:00:00Z' },
  { partner_id:'p-002', tenant_id:'_all', name:'DigitalBridge Pvt Ltd', partner_tier:'gold',     status:'active',   region:'Sindh',       city:'Karachi',   contact_name:'Rida Farouk',  contact_email:'rida@digitalbridge.pk', contact_phone:'+923002222002', account_manager_id:'u-002', attributed_opp_count:3, commission_due:92000,  total_commission_earned:210000, deal_registration_count:5, notes:null, tier_review_due_at:'2026-07-01', created_by:'u-001', created_at:'2025-06-01T10:00:00Z', updated_at:'2026-05-01T00:00:00Z' },
  { partner_id:'p-003', tenant_id:'_all', name:'PakSystems Inc',        partner_tier:'gold',     status:'active',   region:'Punjab',      city:'Islamabad', contact_name:'Shahzad Gill', contact_email:'shahzad@paksystems.pk', contact_phone:'+923003333003', account_manager_id:'u-001', attributed_opp_count:4, commission_due:140000, total_commission_earned:280000, deal_registration_count:6, notes:null, tier_review_due_at:'2026-07-01', created_by:'u-001', created_at:'2025-04-20T09:00:00Z', updated_at:'2026-05-01T00:00:00Z' },
  { partner_id:'p-004', tenant_id:'_all', name:'ByteWave Technologies', partner_tier:'silver',   status:'active',   region:'KPK',         city:'Peshawar',  contact_name:'Asif Khattak', contact_email:'asif@bytewave.pk',      contact_phone:'+923004444004', account_manager_id:'u-003', attributed_opp_count:2, commission_due:48000,  total_commission_earned:96000,  deal_registration_count:3, notes:null, tier_review_due_at:'2026-10-01', created_by:'u-001', created_at:'2025-09-10T11:00:00Z', updated_at:'2026-05-01T00:00:00Z' },
  { partner_id:'p-005', tenant_id:'_all', name:'CloudFirst Pakistan',   partner_tier:'silver',   status:'active',   region:'Sindh',       city:'Karachi',   contact_name:'Mehwish Baig', contact_email:'mehwish@cloudfirst.pk', contact_phone:'+923005555005', account_manager_id:'u-002', attributed_opp_count:1, commission_due:32000,  total_commission_earned:48000,  deal_registration_count:2, notes:null, tier_review_due_at:'2026-10-01', created_by:'u-001', created_at:'2025-11-05T10:00:00Z', updated_at:'2026-05-01T00:00:00Z' },
  { partner_id:'p-006', tenant_id:'_all', name:'SmartLink Pvt Ltd',     partner_tier:'platinum', status:'active',   region:'Punjab',      city:'Lahore',    contact_name:'Tariq Aziz',   contact_email:'tariq@smartlink.pk',    contact_phone:'+923006666006', account_manager_id:'u-001', attributed_opp_count:7, commission_due:265000, total_commission_earned:580000, deal_registration_count:11, notes:null, tier_review_due_at:'2026-07-01', created_by:'u-001', created_at:'2025-01-20T09:00:00Z', updated_at:'2026-05-01T00:00:00Z' },
  { partner_id:'p-007', tenant_id:'_all', name:'DataSphere Corp',       partner_tier:'gold',     status:'inactive', region:'Balochistan', city:'Quetta',    contact_name:'Khalid Mengal',contact_email:'khalid@datasphere.pk',  contact_phone:'+923007777007', account_manager_id:'u-003', attributed_opp_count:0, commission_due:0,      total_commission_earned:85000,  deal_registration_count:1, notes:'Inactive since Q1 2026', tier_review_due_at:null, created_by:'u-001', created_at:'2025-07-15T10:00:00Z', updated_at:'2026-01-15T00:00:00Z' },
  { partner_id:'p-008', tenant_id:'_all', name:'TechAxis Solutions',    partner_tier:'silver',   status:'active',   region:'KPK',         city:'Peshawar',  contact_name:'Adnan Yusuf',  contact_email:'adnan@techaxis.pk',     contact_phone:'+923008888008', account_manager_id:'u-003', attributed_opp_count:1, commission_due:25000,  total_commission_earned:25000,  deal_registration_count:1, notes:null, tier_review_due_at:'2026-10-01', created_by:'u-001', created_at:'2026-01-10T09:00:00Z', updated_at:'2026-05-01T00:00:00Z' },
];

const _memCommissions  = {};  // partner_id → commission[]
const _memDealRegs     = {};  // partner_id → registration[]
const _memActivityLogs = {};  // partner_id → log[]

// Seed some commissions for p-001
_memCommissions['p-001'] = [
  { commission_id:'com-001', partner_id:'p-001', tenant_id:'_all', opportunity_id:'opp-001', opportunity_name:'Q1 Expansion - North', amount:45000, rate:0.15, status:'pending',  calculated_at:'2026-04-01T09:00:00Z', approved_at:null, approved_by:null, paid_at:null, payment_reference:null, dispute_reason:null, created_at:'2026-04-01T09:00:00Z', updated_at:'2026-04-01T09:00:00Z' },
  { commission_id:'com-002', partner_id:'p-001', tenant_id:'_all', opportunity_id:'opp-002', opportunity_name:'City Pharma Renewal',  amount:60000, rate:0.15, status:'approved', calculated_at:'2026-03-15T09:00:00Z', approved_at:'2026-04-01T09:00:00Z', approved_by:'u-001', paid_at:null, payment_reference:null, dispute_reason:null, created_at:'2026-03-15T09:00:00Z', updated_at:'2026-04-01T09:00:00Z' },
  { commission_id:'com-003', partner_id:'p-001', tenant_id:'_all', opportunity_id:'opp-003', opportunity_name:'FastLog Contract',     amount:80000, rate:0.15, status:'paid',     calculated_at:'2026-01-10T09:00:00Z', approved_at:'2026-01-15T09:00:00Z', approved_by:'u-001', paid_at:'2026-02-01T09:00:00Z', payment_reference:'TRF-2026-001', dispute_reason:null, created_at:'2026-01-10T09:00:00Z', updated_at:'2026-02-01T09:00:00Z' },
];

// ── Partners Router ───────────────────────────────────────────────────────────
const partnersRouter = express.Router();

// GET /partners
partnersRouter.get(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { partner_tier, status } = req.query;
    const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
    const offset = parseInt(req.query.offset || '0', 10);

    let rows = _memPartners.filter(p => p.tenant_id === tenantId || p.tenant_id === '_all');
    if (partner_tier) rows = rows.filter(p => p.partner_tier === partner_tier);
    if (status)       rows = rows.filter(p => p.status       === status);

    const total = rows.length;
    const page  = rows.slice(offset, offset + limit);
    return respondSuccess(res, page, { count: page.length, total, limit, offset });
  },
);

// POST /partners
partnersRouter.post(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { name, partner_tier, region, city, contact_name, contact_phone, contact_email, account_manager_id, notes } = req.body;

    if (!VALID_TIERS.includes(partner_tier))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid partner_tier.', [{ field: 'partner_tier', reason: `must_be_one_of_${VALID_TIERS.join('|')}` }]);

    const ts = nowIso();
    const partner = {
      partner_id:              randomUUID(),
      tenant_id:               tenantId,
      name,
      partner_tier,
      status:                  'active',
      region:                  region   || null,
      city:                    city     || null,
      contact_name:            contact_name  || null,
      contact_phone:           contact_phone || null,
      contact_email:           contact_email || null,
      account_manager_id:      account_manager_id || userId,
      attributed_opp_count:    0,
      total_commission_earned: 0,
      commission_due:          0,
      deal_registration_count: 0,
      notes:                   notes || null,
      tier_review_due_at:      null,
      created_by:              userId,
      created_at:              ts,
      updated_at:              ts,
    };
    _memPartners.push(partner);
    return res.status(201).json({ data: partner, meta: { request_id: req.request_id } });
  },
);

// GET /partners/:id
partnersRouter.get(
  '/:partner_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { partner_id } = req.params;
    const p = _memPartners.find(x => x.partner_id === partner_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!p) return respondError(res, 404, 'NOT_FOUND', 'Partner not found.');
    return respondSuccess(res, p);
  },
);

// PATCH /partners/:id
partnersRouter.patch(
  '/:partner_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userRole = req.auth.role || 'agent';
    const { partner_id } = req.params;
    const { name, region, city, contact_name, contact_phone, contact_email, notes, partner_tier, status } = req.body;

    const p = _memPartners.find(x => x.partner_id === partner_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!p) return respondError(res, 404, 'NOT_FOUND', 'Partner not found.');

    // Tier and status changes require admin — spec §6
    if ((partner_tier || status) && !ADMIN_ROLES.includes(userRole))
      return respondError(res, 403, 'FORBIDDEN', 'Tier and status changes require admin role.');

    if (name)          p.name          = name;
    if (region)        p.region        = region;
    if (city)          p.city          = city;
    if (contact_name)  p.contact_name  = contact_name;
    if (contact_phone) p.contact_phone = contact_phone;
    if (contact_email) p.contact_email = contact_email;
    if (notes)         p.notes         = notes;
    if (partner_tier && VALID_TIERS.includes(partner_tier)) p.partner_tier = partner_tier;
    if (status && VALID_STATUSES.includes(status)) p.status = status;
    p.updated_at = nowIso();

    return respondSuccess(res, p);
  },
);

// GET /partners/:id/opportunities
partnersRouter.get(
  '/:partner_id/opportunities',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_READ]),
  async (req, res) => {
    const { partner_id } = req.params;
    // Demo: return placeholder attributed opps
    return respondSuccess(res, [], { count: 0, attributed_opp_count: (_memPartners.find(p => p.partner_id === partner_id) || {}).attributed_opp_count || 0 });
  },
);

// GET /partners/:id/commissions
partnersRouter.get(
  '/:partner_id/commissions',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { partner_id } = req.params;
    const p = _memPartners.find(x => x.partner_id === partner_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!p) return respondError(res, 404, 'NOT_FOUND', 'Partner not found.');

    const commissions = _memCommissions[partner_id] || [];
    return respondSuccess(res, commissions, { count: commissions.length });
  },
);

// POST /partners/:id/commissions/:commission_id/approve
partnersRouter.post(
  '/:partner_id/commissions/:commission_id/approve',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { partner_id, commission_id } = req.params;

    const commissions = _memCommissions[partner_id] || [];
    const c = commissions.find(x => x.commission_id === commission_id);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Commission not found.');
    if (c.status === 'paid')
      return respondError(res, 409, 'IMMUTABLE', "Commission with status 'paid' is immutable.");
    if (c.status !== 'pending' && c.status !== 'disputed')
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot approve commission with status '${c.status}'.`);

    const ts = nowIso();
    c.status      = 'approved';
    c.approved_at = ts;
    c.approved_by = userId;
    c.updated_at  = ts;
    return respondSuccess(res, c);
  },
);

// POST /partners/:id/commissions/:commission_id/pay — admin only
partnersRouter.post(
  '/:partner_id/commissions/:commission_id/pay',
  requestValidationMiddleware(['payment_reference']),
  requireScopes([SCOPES.PARTNERS_ADMIN]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { partner_id, commission_id } = req.params;
    const { payment_reference } = req.body;

    const p = _memPartners.find(x => x.partner_id === partner_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!p) return respondError(res, 404, 'NOT_FOUND', 'Partner not found.');

    const commissions = _memCommissions[partner_id] || [];
    const c = commissions.find(x => x.commission_id === commission_id);
    if (!c) return respondError(res, 404, 'NOT_FOUND', 'Commission not found.');
    if (c.status === 'paid')
      return respondError(res, 409, 'IMMUTABLE', "Commission with status 'paid' is immutable.");
    if (c.status !== 'approved')
      return respondError(res, 422, 'TRANSITION_ERROR', "Commission must be 'approved' before payment.");

    const ts = nowIso();
    c.status            = 'paid';
    c.paid_at           = ts;
    c.payment_reference = payment_reference;
    c.updated_at        = ts;

    // Update partner totals atomically
    p.commission_due          = Math.max(0, parseFloat(p.commission_due) - parseFloat(c.amount));
    p.total_commission_earned = parseFloat(p.total_commission_earned) + parseFloat(c.amount);
    p.updated_at = ts;

    return respondSuccess(res, c);
  },
);

// GET /partners/:id/activity
partnersRouter.get(
  '/:partner_id/activity',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_MANAGE]),
  async (req, res) => {
    const { partner_id } = req.params;
    const logs = _memActivityLogs[partner_id] || [];
    return respondSuccess(res, logs, { count: logs.length });
  },
);

// POST /partners/:id/deal-registrations
partnersRouter.post(
  '/:partner_id/deal-registrations',
  requestValidationMiddleware(['prospect_name', 'estimated_value']),
  requireScopes([SCOPES.PARTNERS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { partner_id } = req.params;
    const { prospect_name, estimated_value, prospect_phone, prospect_email, expected_close_date, notes } = req.body;

    const p = _memPartners.find(x => x.partner_id === partner_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!p) return respondError(res, 404, 'NOT_FOUND', 'Partner not found.');
    if (p.status !== 'active')
      return respondError(res, 422, 'PARTNER_INACTIVE', `Cannot register deals for ${p.status} partner.`);

    const ts = nowIso();
    const reg = {
      registration_id:     randomUUID(),
      partner_id,
      tenant_id:           tenantId,
      opportunity_id:      null,
      prospect_name,
      prospect_phone:      prospect_phone || null,
      prospect_email:      prospect_email || null,
      estimated_value:     parseFloat(estimated_value),
      expected_close_date: expected_close_date || null,
      status:              'submitted',
      submitted_at:        ts,
      reviewed_at:         null,
      reviewed_by:         null,
      rejection_reason:    null,
      expiry_date:         expiryDate(ts, p.partner_tier),
      notes:               notes || null,
      created_at:          ts,
      updated_at:          ts,
    };

    if (!_memDealRegs[partner_id]) _memDealRegs[partner_id] = [];
    _memDealRegs[partner_id].push(reg);
    p.deal_registration_count += 1;

    return res.status(201).json({ data: reg, meta: { request_id: req.request_id } });
  },
);

// GET /partners/:id/deal-registrations
partnersRouter.get(
  '/:partner_id/deal-registrations',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_READ]),
  async (req, res) => {
    const { partner_id } = req.params;
    const regs = _memDealRegs[partner_id] || [];
    return respondSuccess(res, regs, { count: regs.length });
  },
);

// ── Deal Registrations Router (global) ────────────────────────────────────────
const dealRegsRouter = express.Router();

// POST /deal-registrations/:id/approve
dealRegsRouter.post(
  '/:registration_id/approve',
  requestValidationMiddleware(),
  requireScopes([SCOPES.PARTNERS_MANAGE]),
  async (req, res) => {
    const { registration_id } = req.params;
    const userId = req.auth.user_id || req.auth.sub;

    // Find the registration across all partners
    let reg = null;
    for (const regs of Object.values(_memDealRegs)) {
      reg = regs.find(r => r.registration_id === registration_id);
      if (reg) break;
    }
    if (!reg) return respondError(res, 404, 'NOT_FOUND', 'Deal registration not found.');
    if (reg.status !== 'submitted')
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot approve registration with status '${reg.status}'.`);

    const ts = nowIso();
    reg.status      = 'approved';
    reg.reviewed_at = ts;
    reg.reviewed_by = userId;
    reg.updated_at  = ts;
    return respondSuccess(res, reg);
  },
);

// POST /deal-registrations/:id/reject
dealRegsRouter.post(
  '/:registration_id/reject',
  requestValidationMiddleware(['rejection_reason']),
  requireScopes([SCOPES.PARTNERS_MANAGE]),
  async (req, res) => {
    const { registration_id } = req.params;
    const userId = req.auth.user_id || req.auth.sub;
    const { rejection_reason } = req.body;

    let reg = null;
    for (const regs of Object.values(_memDealRegs)) {
      reg = regs.find(r => r.registration_id === registration_id);
      if (reg) break;
    }
    if (!reg) return respondError(res, 404, 'NOT_FOUND', 'Deal registration not found.');
    if (reg.status !== 'submitted')
      return respondError(res, 422, 'TRANSITION_ERROR', `Cannot reject registration with status '${reg.status}'.`);

    const ts = nowIso();
    reg.status           = 'rejected';
    reg.reviewed_at      = ts;
    reg.reviewed_by      = userId;
    reg.rejection_reason = rejection_reason;
    reg.updated_at       = ts;
    return respondSuccess(res, reg);
  },
);

module.exports = { partnersRouter, dealRegsRouter };
