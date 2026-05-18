'use strict';

/**
 * Low-bandwidth progressive loading + cache policy — P-015.
 *
 * Docs: docs/offline-sync.md §13 — Low-bandwidth transport layer
 *       docs/adoption-ux.md §3 — Low-discipline environment handling
 *
 * Implements:
 *   - Stale-while-revalidate per endpoint pattern
 *   - 7-day maximum cache staleness (§13.3)
 *   - Exponential backoff schedule for offline retry (§13.3)
 *   - Deferred load classification (critical vs non-critical)
 *   - Offline queue indicator data builder
 *
 * Usage (server-side Cache-Control headers)::
 *   const { getCacheHeader } = require('./cache-policy');
 *   res.setHeader('Cache-Control', getCacheHeader('/api/v1/leads'));
 *
 * Usage (client-side staleness check)::
 *   const { isStale, shouldFetchFresh } = require('./cache-policy');
 *   if (shouldFetchFresh(cachedEntry)) { refetch(); }
 */

// ── Constants ─────────────────────────────────────────────────────────────────

/** Maximum cache age before client must request a full snapshot (offline-sync.md §13.3). */
const MAX_STALE_AGE_MS = 7 * 24 * 60 * 60 * 1000;   // 7 days

/** Exponential backoff schedule for offline reconnect attempts (seconds). */
const OFFLINE_BACKOFF_SECONDS = Object.freeze([30, 120, 600]);  // 30s, 2m, 10m

// ── Endpoint cache policies ───────────────────────────────────────────────────
// ttl_seconds:  how long the cached response is "fresh"
// swr_seconds:  stale-while-revalidate window (serve stale while fetching fresh)
// critical:     true = always fetch fresh on app foreground (no serving stale)
// deferred:     true = non-critical; load on scroll/interaction, not on first paint

const CACHE_POLICIES = Object.freeze({
  // ── Critical — always fetch fresh on foreground ──────────────────────────
  '/api/v1/leads':                   { ttl_seconds: 30,   swr_seconds: 60,  critical: true,  deferred: false },
  '/api/v1/followups':               { ttl_seconds: 30,   swr_seconds: 60,  critical: true,  deferred: false },
  '/api/v1/collections/invoices':    { ttl_seconds: 60,   swr_seconds: 120, critical: true,  deferred: false },
  '/api/v1/leads/:id/next-action':   { ttl_seconds: 15,   swr_seconds: 30,  critical: true,  deferred: false },

  // ── Standard — stale-while-revalidate, moderate TTL ──────────────────────
  '/api/v1/leads/:id':               { ttl_seconds: 60,   swr_seconds: 120, critical: false, deferred: false },
  '/api/v1/opportunities':           { ttl_seconds: 120,  swr_seconds: 300, critical: false, deferred: false },
  '/api/v1/contacts':                { ttl_seconds: 300,  swr_seconds: 600, critical: false, deferred: false },
  '/api/v1/sync/status':             { ttl_seconds: 10,   swr_seconds: 30,  critical: false, deferred: false },

  // ── Non-critical — deferred, load on scroll/interaction ──────────────────
  '/api/v1/audit':                   { ttl_seconds: 300,  swr_seconds: 600, critical: false, deferred: true  },
  '/api/v1/reports':                 { ttl_seconds: 300,  swr_seconds: 900, critical: false, deferred: true  },
  '/api/v1/leads/:id/timeline':      { ttl_seconds: 120,  swr_seconds: 300, critical: false, deferred: true  },

  // ── Static / long-lived ──────────────────────────────────────────────────
  '/api/v1/feature-flags':           { ttl_seconds: 600,  swr_seconds: 1200, critical: false, deferred: false },
  '/api/v1/config':                  { ttl_seconds: 3600, swr_seconds: 7200, critical: false, deferred: false },
});

// ── Route matching ────────────────────────────────────────────────────────────

/**
 * Return the cache policy for a given API path.
 * Supports :param placeholders in pattern matching.
 *
 * @param {string} path — request path e.g. "/api/v1/leads/lead_abc123"
 * @returns {object|null}
 */
function getPolicyForPath(path) {
  // Exact match first
  if (CACHE_POLICIES[path]) return CACHE_POLICIES[path];

  // Pattern match: replace UUID/ID-like segments with :param
  for (const [pattern, policy] of Object.entries(CACHE_POLICIES)) {
    const regex = new RegExp(
      '^' + pattern.replace(/:[^/]+/g, '[^/]+') + '(/.*)?$',
    );
    if (regex.test(path)) return policy;
  }
  return null;
}

/**
 * Return a Cache-Control header value for a given API path.
 * Returns null if no policy is found (caller should not set Cache-Control).
 *
 * @param {string} path
 * @returns {string|null}
 */
function getCacheHeader(path) {
  const policy = getPolicyForPath(path);
  if (!policy) return null;
  // stale-while-revalidate is the core pattern — serve cached, update in background
  return `public, max-age=${policy.ttl_seconds}, stale-while-revalidate=${policy.swr_seconds}`;
}

// ── Staleness checks ──────────────────────────────────────────────────────────

/**
 * Return true if a cached entry is older than the given maxAge.
 *
 * @param {number|string} cachedAt  — timestamp in ms or ISO-8601 string
 * @param {number}        maxAgeMs  — max age in milliseconds
 * @returns {boolean}
 */
function isStale(cachedAt, maxAgeMs) {
  const cachedMs = typeof cachedAt === 'number' ? cachedAt : new Date(cachedAt).getTime();
  return (Date.now() - cachedMs) > maxAgeMs;
}

/**
 * Return true if the cache entry requires a fresh fetch (not just SWR).
 * Triggers when entry is older than MAX_STALE_AGE_MS (7 days).
 *
 * @param {{ path: string, cachedAt: number }} cacheEntry
 * @returns {boolean}
 */
function requiresFullSnapshot(cacheEntry) {
  return isStale(cacheEntry.cachedAt, MAX_STALE_AGE_MS);
}

/**
 * Return true if the item should be fetched fresh right now
 * (bypassing SWR, used for critical items on app foreground).
 *
 * @param {{ path: string, cachedAt: number }} cacheEntry
 * @returns {boolean}
 */
function shouldFetchFresh(cacheEntry) {
  const policy = getPolicyForPath(cacheEntry.path);
  if (!policy) return true;
  if (policy.critical) return true;
  return isStale(cacheEntry.cachedAt, policy.ttl_seconds * 1000);
}

// ── Offline queue indicator ───────────────────────────────────────────────────

/**
 * Build the data object for the offline queue indicator shown in the UI.
 * Docs: docs/offline-sync.md §13.3 — "UI shows offline queue count"
 *
 * @param {{ pendingCount: number, isOnline: boolean, lastSyncAt: number|null }} syncState
 * @returns {{ label: string, pendingCount: number, isOnline: boolean, showWarning: boolean }}
 */
function buildOfflineIndicator(syncState) {
  const { pendingCount = 0, isOnline = true, lastSyncAt = null } = syncState;
  const showWarning = !isOnline || pendingCount > 0;

  let label = '';
  if (!isOnline && pendingCount > 0) {
    label = `Working offline — ${pendingCount} change${pendingCount === 1 ? '' : 's'} pending`;
  } else if (!isOnline) {
    label = 'Working offline — changes will sync when connection is restored';
  } else if (pendingCount > 0) {
    label = `Syncing ${pendingCount} pending change${pendingCount === 1 ? '' : 's'}…`;
  }

  return { label, pendingCount, isOnline, showWarning, lastSyncAt };
}

/**
 * Return the next backoff delay in ms given the attempt number (0-indexed).
 * Uses the OFFLINE_BACKOFF_SECONDS schedule with capped max.
 *
 * @param {number} attempt — 0-indexed attempt number
 * @returns {number}       — delay in milliseconds
 */
function nextBackoffMs(attempt) {
  const idx = Math.min(attempt, OFFLINE_BACKOFF_SECONDS.length - 1);
  return OFFLINE_BACKOFF_SECONDS[idx] * 1000;
}

module.exports = {
  CACHE_POLICIES,
  MAX_STALE_AGE_MS,
  OFFLINE_BACKOFF_SECONDS,
  getPolicyForPath,
  getCacheHeader,
  isStale,
  requiresFullSnapshot,
  shouldFetchFresh,
  buildOfflineIndicator,
  nextBackoffMs,
};
