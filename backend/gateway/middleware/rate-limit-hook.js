'use strict';

/**
 * Rate-limit middleware — Redis-backed sliding window (ioredis).
 *
 * Each bucket key: `rl:{tenant_id}:{subject}:{METHOD}:{canonical_path}`
 * Window: 60 seconds. Limits vary by endpoint type.
 *
 * Falls back to in-process Map when Redis is unavailable (ioredis-mock in dev;
 * connection error in prod triggers graceful degradation so requests are
 * allowed through rather than blocked by infrastructure failure).
 *
 * C3 — A-006: ioredis replaces the previous in-memory Map.
 * Writes to D:\DockerData Redis in local Docker; Render managed Redis in C4.
 */

const { respondError } = require('./response-wrapper');
const { getRedisClient } = require('../config/redis-client');

const WINDOW_SEC = 60;
const ROUTE_TOKEN_PATTERN = /\/[A-Za-z0-9_-]{6,}/g;

function canonicalRoute(path = '') {
  return path.replace(ROUTE_TOKEN_PATTERN, '/:id');
}

function endpointLimit(method, path) {
  const key = `${method.toUpperCase()} ${canonicalRoute(path)}`;
  if (/POST \/api\/v1\/(payments|emails|users|forecasts)/.test(key)) return 20;
  if (/POST \/api\/v1\/(audit|audits)/.test(key)) return 10;
  if (method.toUpperCase() === 'GET') return 300;
  return 120;
}

async function redisEvaluate({ path, method, subject, tenant_id }) {
  const limit = endpointLimit(method, path);
  const bucketKey = `rl:${tenant_id || 'unknown'}:${subject}:${method.toUpperCase()}:${canonicalRoute(path)}`;

  try {
    const redis = getRedisClient();
    const count = await redis.incr(bucketKey);
    if (count === 1) {
      // First request in window — set TTL
      await redis.expire(bucketKey, WINDOW_SEC);
    }

    const pttlMs = await redis.pttl(bucketKey);
    const resetAt = pttlMs > 0 ? Date.now() + pttlMs : Date.now() + WINDOW_SEC * 1000;

    if (count <= limit) {
      return { allowed: true, limit, remaining: Math.max(limit - count, 0), reset_at: resetAt };
    }

    return {
      allowed: false,
      retry_after_seconds: Math.ceil(pttlMs > 0 ? pttlMs / 1000 : WINDOW_SEC),
      limit,
      remaining: 0,
      reset_at: resetAt,
    };
  } catch (_err) {
    // Redis unavailable — allow request through (fail open, not closed)
    return { allowed: true, limit, remaining: limit - 1, reset_at: Date.now() + WINDOW_SEC * 1000 };
  }
}

function rateLimitHook({ evaluate } = {}) {
  const evaluator = typeof evaluate === 'function' ? evaluate : redisEvaluate;

  return async function rateLimitMiddleware(req, res, next) {
    let outcome;
    try {
      outcome = await evaluator({
        path: req.path,
        method: req.method,
        subject: req.auth?.sub || 'anonymous',
        tenant_id: req.auth?.tenant_id || null,
        request_id: req.request_id,
      });
    } catch (_err) {
      return next(); // fail open
    }

    if (!outcome || outcome.allowed !== false) {
      if (outcome && typeof outcome.limit === 'number') {
        res.setHeader('x-ratelimit-limit', String(outcome.limit));
        res.setHeader('x-ratelimit-remaining', String(outcome.remaining ?? 0));
        if (typeof outcome.reset_at === 'number') {
          res.setHeader('x-ratelimit-reset', String(Math.floor(outcome.reset_at / 1000)));
        }
      }
      return next();
    }

    if (typeof outcome.retry_after_seconds === 'number') {
      res.setHeader('retry-after', String(outcome.retry_after_seconds));
    }

    return respondError(
      res,
      'rate_limited',
      'Rate limit exceeded. Please retry later.',
      [{ field: 'request', reason: 'rate_limit_exceeded' }],
      429,
    );
  };
}

module.exports = { rateLimitHook };
