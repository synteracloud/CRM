'use strict';

// In-memory jti revocation blocklist.
// Single-instance: revocations survive until process restart.
// Redis upgrade path: replace Map with Redis SET/EXPIRE — same interface. (deferred — needs REDIS_URL)

const _blocklist = new Map(); // jti -> expiresAt epoch-ms

const DEFAULT_TTL_MS = 15 * 60 * 1000; // matches access token max TTL (15 min)

function addRevoked(jti, ttlMs) {
  if (!jti) return;
  _blocklist.set(jti, Date.now() + (ttlMs || DEFAULT_TTL_MS));
}

function isRevoked(jti) {
  if (!jti) return false;
  const expiresAt = _blocklist.get(jti);
  if (expiresAt === undefined) return false;
  if (Date.now() >= expiresAt) {
    _blocklist.delete(jti);
    return false;
  }
  return true;
}

module.exports = { addRevoked, isRevoked };
