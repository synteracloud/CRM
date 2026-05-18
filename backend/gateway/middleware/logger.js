'use strict';

/**
 * Structured JSON logger — P-022.
 *
 * Pure Node.js — no external dependencies.
 * Outputs one JSON object per line to stdout (Docker log-driver friendly).
 *
 * Fields emitted on every log entry:
 *   timestamp   ISO-8601 UTC
 *   level       debug | info | warn | error
 *   message     human-readable string
 *   service     process.env.SERVICE_NAME (default "crm-gateway")
 *   env         process.env.NODE_ENV
 *   ...extra    any additional fields passed by the caller
 *
 * Usage::
 *   const logger = require('./logger');
 *   logger.info({ event: 'http.request.completed', status_code: 200, duration_ms: 12 });
 *   logger.error({ event: 'db.query.failed', error: err.message });
 */

const LEVEL_RANKS = { debug: 0, info: 1, warn: 2, error: 3 };
const MIN_LEVEL   = (process.env.LOG_LEVEL || 'info').toLowerCase();
const MIN_RANK    = LEVEL_RANKS[MIN_LEVEL] ?? 1;

const SERVICE = process.env.SERVICE_NAME || 'crm-gateway';
const ENV     = process.env.NODE_ENV || 'development';

function write(level, data) {
  if ((LEVEL_RANKS[level] ?? 0) < MIN_RANK) return;

  const entry = typeof data === 'string'
    ? { message: data }
    : { ...data };

  const line = JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    service: SERVICE,
    env: ENV,
    ...entry,
  });

  // Use process.stdout.write so output is synchronous and never interleaved
  process.stdout.write(line + '\n');
}

const logger = {
  debug: (data) => write('debug', data),
  info:  (data) => write('info',  data),
  warn:  (data) => write('warn',  data),
  error: (data) => write('error', data),
};

module.exports = logger;
