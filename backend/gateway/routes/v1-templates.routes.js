'use strict';

/**
 * Message Templates routes.
 *
 * Docs: backend/docs/domain/marketing-campaigns.md §2.3
 * Mount: /api/v1/templates/*
 *
 * P-017: Templates with language="ur" set is_urdu=true.
 * WhatsApp templates require meta_template_status="approved" before campaign activation.
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const VALID_CHANNEL     = ['whatsapp_broadcast', 'email', 'sms'];
const VALID_META_STATUS = ['pending', 'approved', 'rejected', 'paused'];

const _memTemplates = [
  { template_id:'tpl-001', tenant_id:'_all', name:'Eid Mubarak Offer',        channel:'whatsapp_broadcast', language:'en', subject:null, body:'Eid Mubarak! 🌙 Celebrate with our special offer — 20% off on all CRM plans this Eid. Reply "YES" to claim.', footer:'Reply STOP to unsubscribe', cta_label:'Claim Offer', cta_url:'https://nexlink.crm/offer', meta_template_name:'eid_mubarak_offer_2026', meta_template_status:'approved', is_urdu:false, created_by:'u-001', created_at:'2026-03-20T09:00:00Z', updated_at:'2026-03-20T09:00:00Z' },
  { template_id:'tpl-002', tenant_id:'_all', name:'Q2 Product Launch Email',   channel:'email',              language:'en', subject:'Exciting news from NexLink CRM', body:'We have launched new features in NexLink CRM. Book a free demo at [link]. Reply "DEMO" to schedule.', footer:null, cta_label:'Book Demo', cta_url:'https://nexlink.crm/demo', meta_template_name:null, meta_template_status:null, is_urdu:false, created_by:'u-001', created_at:'2026-04-05T09:00:00Z', updated_at:'2026-04-05T09:00:00Z' },
  { template_id:'tpl-003', tenant_id:'_all', name:'Payment Reminder WhatsApp', channel:'whatsapp_broadcast', language:'en', subject:null, body:'Your invoice is due soon. Amount: {{contact.amount}}. Pay now to avoid late fees. Reply "PAID" once done.', footer:'Reply STOP to unsubscribe', cta_label:'Pay Now', cta_url:'https://nexlink.crm/pay', meta_template_name:'payment_reminder_v1', meta_template_status:'approved', is_urdu:false, created_by:'u-002', created_at:'2026-02-01T09:00:00Z', updated_at:'2026-02-01T09:00:00Z' },
  { template_id:'tpl-004', tenant_id:'_all', name:'Re-engagement Message',     channel:'whatsapp_broadcast', language:'en', subject:null, body:'Aap ko miss kiya! We noticed you have not logged in recently. Let us help you get back on track. Reply "HELP" for support.', footer:'Reply STOP to unsubscribe', cta_label:'Get Help', cta_url:null, meta_template_name:'reengagement_v1', meta_template_status:'approved', is_urdu:false, created_by:'u-002', created_at:'2026-04-01T09:00:00Z', updated_at:'2026-04-01T09:00:00Z' },
];

function nowIso() { return new Date().toISOString(); }

const router = express.Router();

// GET /templates
router.get(
  '/',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { channel, language } = req.query;
    let rows = _memTemplates.filter(t => t.tenant_id === tenantId || t.tenant_id === '_all');
    if (channel)  rows = rows.filter(t => t.channel  === channel);
    if (language) rows = rows.filter(t => t.language === language);
    return respondSuccess(res, rows, { count: rows.length });
  },
);

// POST /templates
router.post(
  '/',
  requestValidationMiddleware(['name', 'channel', 'body']),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { name, channel, language = 'en', subject, body, footer, cta_label, cta_url, meta_template_name } = req.body;

    if (!VALID_CHANNEL.includes(channel))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid channel.', [{ field: 'channel', reason: `must_be_one_of_${VALID_CHANNEL.join('|')}` }]);

    const is_urdu = language === 'ur';
    const ts = nowIso();
    const template = {
      template_id:          randomUUID(),
      tenant_id:            tenantId,
      name,
      channel,
      language,
      subject:              subject              || null,
      body,
      footer:               footer               || null,
      cta_label:            cta_label            || null,
      cta_url:              cta_url              || null,
      meta_template_name:   meta_template_name   || null,
      meta_template_status: channel === 'whatsapp_broadcast' ? 'pending' : null,
      is_urdu,
      created_by:           userId,
      created_at:           ts,
      updated_at:           ts,
    };
    _memTemplates.push(template);
    return res.status(201).json({ data: template, meta: { request_id: req.request_id } });
  },
);

// GET /templates/:id
router.get(
  '/:template_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { template_id } = req.params;
    const t = _memTemplates.find(x => x.template_id === template_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!t) return respondError(res, 404, 'NOT_FOUND', 'Template not found.');
    return respondSuccess(res, t);
  },
);

// PATCH /templates/:id
router.patch(
  '/:template_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.CAMPAIGNS_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { template_id } = req.params;
    const t = _memTemplates.find(x => x.template_id === template_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!t) return respondError(res, 404, 'NOT_FOUND', 'Template not found.');

    const { name, body, subject, footer, cta_label, cta_url, meta_template_status } = req.body;
    if (name)        t.name        = name;
    if (body)        t.body        = body;
    if (subject)     t.subject     = subject;
    if (footer)      t.footer      = footer;
    if (cta_label)   t.cta_label   = cta_label;
    if (cta_url)     t.cta_url     = cta_url;
    if (meta_template_status) {
      if (!VALID_META_STATUS.includes(meta_template_status))
        return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid meta_template_status.', []);
      t.meta_template_status = meta_template_status;
    }
    t.updated_at = nowIso();
    return respondSuccess(res, t);
  },
);

module.exports = router;
