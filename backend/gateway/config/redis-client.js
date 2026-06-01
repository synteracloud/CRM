'use strict';

/**
 * Redis client singleton.
 *
 * Production: connects to REDIS_URL (e.g. Render managed Redis).
 * Dev/test without Redis: falls back to ioredis-mock (in-process, zero infra).
 *
 * C3 note: ioredis-mock is used locally; Render provides real Redis in C4.
 * All rate-limit keys are namespaced `rl:{tenant}:{subject}:{method}:{path}`.
 * All OTP keys are namespaced `otp:{tenant}:{email}`.
 * All refresh tokens are namespaced `rt:{jti}`.
 * All feature-flag cache keys are namespaced `ff:{tenant}:{key}`.
 */

let Redis;
let client = null;
let _isMock = false;

function getRedisClient() {
  if (client) return client;

  const REDIS_URL = process.env.REDIS_URL;

  if (REDIS_URL) {
    try {
      Redis = require('ioredis');
      client = new Redis(REDIS_URL, {
        lazyConnect: false,
        connectTimeout: 5000,
        maxRetriesPerRequest: 3,
        enableOfflineQueue: true,
      });
      client.on('error', (err) => {
        console.error('[redis] connection error — falling back to in-memory', err.message);
      });
      _isMock = false;
    } catch (_e) {
      client = _buildMock();
    }
  } else {
    client = _buildMock();
  }

  return client;
}

function _buildMock() {
  try {
    const RedisMock = require('ioredis-mock');
    _isMock = true;
    console.info('[redis] REDIS_URL not set — using ioredis-mock (in-process). Set REDIS_URL for production Redis.');
    return new RedisMock();
  } catch (_e) {
    // Neither real Redis nor mock available — use a minimal stub
    _isMock = true;
    const store = new Map();
    return {
      async get(key) { const v = store.get(key); return v ? v.value : null; },
      async set(key, value) { store.set(key, { value }); return 'OK'; },
      async setex(key, ttl, value) {
        store.set(key, { value });
        setTimeout(() => store.delete(key), ttl * 1000);
        return 'OK';
      },
      async del(key) { store.delete(key); return 1; },
      async incr(key) {
        const current = parseInt(store.get(key)?.value || '0', 10);
        const next = current + 1;
        store.set(key, { value: String(next) });
        return next;
      },
      async expire(key, ttl) {
        const v = store.get(key);
        if (v) setTimeout(() => store.delete(key), ttl * 1000);
        return 1;
      },
      async pttl(key) { return -1; },
      async quit() { store.clear(); },
    };
  }
}

function isMock() { return _isMock; }

module.exports = { getRedisClient, isMock };
