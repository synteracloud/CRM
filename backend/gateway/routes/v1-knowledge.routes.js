'use strict';

/**
 * Knowledge Base routes.
 *
 * Docs:  backend/docs/domain/cases-domain.md §7
 * Mount: /api/v1/knowledge/*
 *
 * In-memory fallback active when DB_DISABLED=true or pg unavailable.
 */

const { randomUUID } = require('crypto');
const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { SCOPES } = require('../config/rbac-scopes');

const VALID_ARTICLE_STATUS = ['draft', 'published', 'archived'];
const VALID_LANGUAGE       = ['en', 'ur'];

// ── In-memory store ───────────────────────────────────────────────────────────
const _memArticles = [
  { article_id: 'art-001', tenant_id: '_all', title: 'How to set up WhatsApp integration',  category: 'getting_started', status: 'published', language: 'en', view_count: 342, helpful_count: 28, not_helpful_count: 3,  author_id: 'u-003', tags: [], published_at: '2026-04-15T09:00:00Z', created_at: '2026-04-10T09:00:00Z', updated_at: '2026-04-15T09:00:00Z', body: '' },
  { article_id: 'art-002', tenant_id: '_all', title: 'Invoice creation and payment guide',   category: 'billing',         status: 'published', language: 'en', view_count: 215, helpful_count: 19, not_helpful_count: 2,  author_id: 'u-001', tags: [], published_at: '2026-05-01T10:00:00Z', created_at: '2026-04-28T09:00:00Z', updated_at: '2026-05-01T10:00:00Z', body: '' },
  { article_id: 'art-003', tenant_id: '_all', title: 'Managing user roles and permissions',  category: 'how_to',          status: 'published', language: 'en', view_count: 187, helpful_count: 14, not_helpful_count: 1,  author_id: 'u-003', tags: [], published_at: '2026-03-20T11:00:00Z', created_at: '2026-03-18T09:00:00Z', updated_at: '2026-03-20T11:00:00Z', body: '' },
  { article_id: 'art-004', tenant_id: '_all', title: 'Setting up SLA tiers for support',     category: 'technical',       status: 'published', language: 'en', view_count: 98,  helpful_count: 7,  not_helpful_count: 4,  author_id: 'u-002', tags: [], published_at: '2026-01-10T09:00:00Z', created_at: '2026-01-08T09:00:00Z', updated_at: '2026-01-10T09:00:00Z', body: '' },
  { article_id: 'art-005', tenant_id: '_all', title: 'CRM lead import via CSV',              category: 'getting_started', status: 'published', language: 'en', view_count: 412, helpful_count: 35, not_helpful_count: 5,  author_id: 'u-001', tags: [], published_at: '2026-04-28T14:00:00Z', created_at: '2026-04-25T09:00:00Z', updated_at: '2026-04-28T14:00:00Z', body: '' },
  { article_id: 'art-006', tenant_id: '_all', title: 'Territory assignment rules explained', category: 'how_to',          status: 'draft',     language: 'en', view_count: 0,   helpful_count: 0,  not_helpful_count: 0,  author_id: 'u-003', tags: [], published_at: null,                created_at: '2026-05-25T09:00:00Z', updated_at: '2026-05-25T09:00:00Z', body: '' },
];

function nowIso() { return new Date().toISOString(); }

const router = express.Router();

// POST /knowledge/articles — create draft
router.post(
  '/articles',
  requestValidationMiddleware(),
  requireScopes([SCOPES.KNOWLEDGE_MANAGE]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const userId   = req.auth.user_id || req.auth.sub;
    const { title, body = '', category, tags = [], language = 'en' } = req.body;

    if (!VALID_LANGUAGE.includes(language))
      return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid language.', [{ field: 'language', reason: 'must_be_en_or_ur' }]);

    const ts      = nowIso();
    const article = {
      article_id:        randomUUID(),
      tenant_id:         tenantId,
      title,
      body,
      category:          category || null,
      tags,
      status:            'draft',
      language,
      author_id:         userId,
      published_at:      null,
      view_count:        0,
      helpful_count:     0,
      not_helpful_count: 0,
      created_at:        ts,
      updated_at:        ts,
    };
    _memArticles.push(article);
    return res.status(201).json({ data: article, meta: { request_id: req.request_id } });
  },
);

// GET /knowledge/articles — list published (or all for manager/admin)
router.get(
  '/articles',
  requestValidationMiddleware(),
  requireScopes([SCOPES.KNOWLEDGE_READ]),
  async (req, res) => {
    const tenantId = req.auth.tenant_id;
    const { category, status, language } = req.query;
    const limit  = Math.min(parseInt(req.query.limit  || '25', 10), 200);
    const offset = parseInt(req.query.offset || '0', 10);

    let rows = _memArticles.filter(a => a.tenant_id === tenantId || a.tenant_id === '_all');
    // Default: show published only; managers can pass status= to filter
    if (status) {
      rows = rows.filter(a => a.status === status);
    } else {
      rows = rows.filter(a => a.status === 'published');
    }
    if (category) rows = rows.filter(a => a.category === category);
    if (language) rows = rows.filter(a => a.language === language);

    const total = rows.length;
    const page  = rows.slice(offset, offset + limit);
    return respondSuccess(res, page, { count: page.length, total, limit, offset });
  },
);

// GET /knowledge/articles/:id
router.get(
  '/articles/:article_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.KNOWLEDGE_READ]),
  async (req, res) => {
    const tenantId    = req.auth.tenant_id;
    const { article_id } = req.params;

    const a = _memArticles.find(x => x.article_id === article_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!a) return respondError(res, 404, 'NOT_FOUND', 'Article not found.');

    a.view_count += 1;  // increment on read per spec §7.3
    return respondSuccess(res, a);
  },
);

// PATCH /knowledge/articles/:id
router.patch(
  '/articles/:article_id',
  requestValidationMiddleware(),
  requireScopes([SCOPES.KNOWLEDGE_MANAGE]),
  async (req, res) => {
    const tenantId    = req.auth.tenant_id;
    const userId      = req.auth.user_id || req.auth.sub;
    const { article_id } = req.params;
    const { title, body, category, tags, language } = req.body;

    const a = _memArticles.find(x => x.article_id === article_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!a) return respondError(res, 404, 'NOT_FOUND', 'Article not found.');
    if (a.status === 'archived') return respondError(res, 409, 'CONFLICT', 'Archived articles cannot be edited.');

    if (title)    a.title    = title;
    if (body)     a.body     = body;
    if (category) a.category = category;
    if (tags)     a.tags     = tags;
    if (language) {
      if (!VALID_LANGUAGE.includes(language))
        return respondError(res, 422, 'VALIDATION_ERROR', 'Invalid language.', [{ field: 'language', reason: 'must_be_en_or_ur' }]);
      a.language = language;
    }
    a.updated_at = nowIso();
    return respondSuccess(res, a);
  },
);

// POST /knowledge/articles/:id/publish
router.post(
  '/articles/:article_id/publish',
  requestValidationMiddleware(),
  requireScopes([SCOPES.KNOWLEDGE_MANAGE]),
  async (req, res) => {
    const tenantId    = req.auth.tenant_id;
    const { article_id } = req.params;

    const a = _memArticles.find(x => x.article_id === article_id && (x.tenant_id === tenantId || x.tenant_id === '_all'));
    if (!a) return respondError(res, 404, 'NOT_FOUND', 'Article not found.');
    if (a.status === 'published') return respondSuccess(res, a);  // idempotent

    const ts   = nowIso();
    a.status       = 'published';
    a.published_at = ts;
    a.updated_at   = ts;
    return respondSuccess(res, a);
  },
);

module.exports = router;
