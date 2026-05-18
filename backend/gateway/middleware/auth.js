'use strict';

/**
 * JWT signature verification — P-021.
 *
 * Docs: pending.md P-021 — Auth enforcement middleware
 *       gateway/config/env-config.js — JWT_SECRET / JWT_PUBLIC_KEY required in production
 *
 * Supports:
 *   HS256 — symmetric HMAC-SHA256.  Requires JWT_SECRET env var.
 *   RS256 — asymmetric RSA-SHA256.  Requires JWT_PUBLIC_KEY env var (PEM format).
 *
 * Algorithm is read from the JWT header; only HS256 and RS256 are accepted.
 * Unknown algorithms are rejected — prevents the "alg:none" vulnerability.
 *
 * Usage::
 *   const { verifyJwt } = require('./auth');
 *   const { valid, payload, error } = verifyJwt(token);
 */

const crypto = require('crypto');

// ── Algorithm guard ────────────────────────────────────────────────────────────
const ALLOWED_ALGORITHMS = new Set(['HS256', 'RS256']);

// ── Base64url helpers ─────────────────────────────────────────────────────────

function base64urlDecode(str) {
  const padded = str.replace(/-/g, '+').replace(/_/g, '/');
  const padding = (4 - (padded.length % 4)) % 4;
  return Buffer.from(padded + '='.repeat(padding), 'base64');
}

function base64urlEncode(buf) {
  return buf.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

// ── JWT parsing ───────────────────────────────────────────────────────────────

function parseJwt(token) {
  if (typeof token !== 'string') return null;
  const parts = token.split('.');
  if (parts.length !== 3) return null;

  try {
    const header  = JSON.parse(base64urlDecode(parts[0]).toString('utf8'));
    const payload = JSON.parse(base64urlDecode(parts[1]).toString('utf8'));
    return { header, payload, signingInput: `${parts[0]}.${parts[1]}`, signature: parts[2] };
  } catch {
    return null;
  }
}

// ── HS256 verification ────────────────────────────────────────────────────────

function verifyHs256(signingInput, signature, secret) {
  if (!secret) return false;
  const expected = base64urlEncode(
    crypto.createHmac('sha256', secret).update(signingInput).digest(),
  );
  // Constant-time comparison
  try {
    const aBuf = Buffer.from(expected, 'ascii');
    const bBuf = Buffer.from(signature, 'ascii');
    if (aBuf.length !== bBuf.length) return false;
    return crypto.timingSafeEqual(aBuf, bBuf);
  } catch {
    return false;
  }
}

// ── RS256 verification ────────────────────────────────────────────────────────

function verifyRs256(signingInput, signature, publicKeyPem) {
  if (!publicKeyPem) return false;
  try {
    const sigBuf = base64urlDecode(signature);
    return crypto.verify(
      'RSA-SHA256',
      Buffer.from(signingInput, 'ascii'),
      { key: publicKeyPem, format: 'pem' },
      sigBuf,
    );
  } catch {
    return false;
  }
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Verify a JWT token's signature and return its payload if valid.
 *
 * @param {string} token  — raw Bearer token value (without "Bearer " prefix)
 * @param {object} [opts] — optional overrides for secret/key (for testing)
 * @param {string} [opts.secret]    — HS256 secret (defaults to JWT_SECRET env var)
 * @param {string} [opts.publicKey] — RS256 PEM (defaults to JWT_PUBLIC_KEY env var)
 * @returns {{ valid: boolean, payload: object|null, error: string|null }}
 */
function verifyJwt(token, opts = {}) {
  const parsed = parseJwt(token);
  if (!parsed) {
    return { valid: false, payload: null, error: 'malformed_token' };
  }

  const alg = parsed.header.alg;
  if (!ALLOWED_ALGORITHMS.has(alg)) {
    return { valid: false, payload: null, error: `unsupported_algorithm:${alg}` };
  }

  let signatureValid = false;

  if (alg === 'HS256') {
    const secret = opts.secret || process.env.JWT_SECRET || '';
    signatureValid = verifyHs256(parsed.signingInput, parsed.signature, secret);
  } else if (alg === 'RS256') {
    const publicKey = opts.publicKey || process.env.JWT_PUBLIC_KEY || '';
    signatureValid = verifyRs256(parsed.signingInput, parsed.signature, publicKey);
  }

  if (!signatureValid) {
    return { valid: false, payload: null, error: 'invalid_signature' };
  }

  return { valid: true, payload: parsed.payload, error: null };
}

module.exports = { verifyJwt };
