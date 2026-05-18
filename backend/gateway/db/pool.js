'use strict';

/**
 * PostgreSQL connection pool.
 *
 * Docs: docs/data-architecture.md — PostgreSQL, domain-owned schemas
 *       docs/org-multi-tenancy.md — tenant isolation via schema per domain
 *
 * Uses the `pg` (node-postgres) library with connection pooling.
 * All queries are tenant-scoped: callers MUST pass tenantId and the
 * repository layer sets search_path accordingly.
 *
 * Environment variables:
 *   DATABASE_URL          — full postgres connection string (overrides individual vars)
 *   DB_HOST               — default: localhost
 *   DB_PORT               — default: 5432
 *   DB_NAME               — default: crm
 *   DB_USER               — required in production
 *   DB_PASSWORD           — required in production
 *   DB_POOL_MAX           — max pool connections (default: 10)
 *   DB_POOL_IDLE_MS       — idle connection timeout ms (default: 10000)
 *   DB_POOL_CONN_TIMEOUT  — connection acquire timeout ms (default: 5000)
 *   DB_SSL                — "true" to enable SSL (default: false)
 *
 * Usage:
 *   const { query, withTransaction } = require('../db/pool');
 *
 *   // Simple query (auto-returns client to pool)
 *   const { rows } = await query('SELECT * FROM lead_management.leads WHERE tenant_id = $1', [tenantId]);
 *
 *   // Transaction
 *   await withTransaction(async (client) => {
 *     await client.query('INSERT INTO ...', [...]);
 *     await client.query('UPDATE ...', [...]);
 *   });
 */

let Pool;
try {
  ({ Pool } = require('pg'));
} catch (_e) {
  // pg is not installed — provide a stub that throws on use.
  // This allows the gateway to start in dev without a DB; routes that call
  // query() will fail with a clear error rather than a missing-module crash.
  Pool = null;
}

function buildConfig() {
  if (process.env.DATABASE_URL) {
    return {
      connectionString: process.env.DATABASE_URL,
      ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false,
      max: parseInt(process.env.DB_POOL_MAX || '10', 10),
      idleTimeoutMillis: parseInt(process.env.DB_POOL_IDLE_MS || '10000', 10),
      connectionTimeoutMillis: parseInt(process.env.DB_POOL_CONN_TIMEOUT || '5000', 10),
    };
  }
  return {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432', 10),
    database: process.env.DB_NAME || 'crm',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '',
    ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false,
    max: parseInt(process.env.DB_POOL_MAX || '10', 10),
    idleTimeoutMillis: parseInt(process.env.DB_POOL_IDLE_MS || '10000', 10),
    connectionTimeoutMillis: parseInt(process.env.DB_POOL_CONN_TIMEOUT || '5000', 10),
  };
}

let _pool = null;

function getPool() {
  if (!Pool) {
    throw new Error(
      'pg package not installed. Run: npm install pg\n' +
      'Or set DB_DISABLED=true to skip DB wiring in development.',
    );
  }
  if (!_pool) {
    _pool = new Pool(buildConfig());
    _pool.on('error', (err) => {
      console.error('[db/pool] unexpected idle client error', err.message);
    });
  }
  return _pool;
}

/**
 * Execute a parameterised query using a pooled client.
 * @param {string} text   — SQL text with $1/$2 placeholders
 * @param {any[]}  params — parameter values
 * @returns {Promise<{rows: any[], rowCount: number}>}
 */
async function query(text, params) {
  const pool = getPool();
  return pool.query(text, params);
}

/**
 * Run a function inside a serialisable transaction.
 * The client is committed on success, rolled back on error, and always
 * released back to the pool.
 * @param {(client: import('pg').PoolClient) => Promise<T>} fn
 * @returns {Promise<T>}
 */
async function withTransaction(fn) {
  const pool = getPool();
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await fn(client);
    await client.query('COMMIT');
    return result;
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

/**
 * Gracefully drain and close the pool (call at process exit).
 */
async function closePool() {
  if (_pool) {
    await _pool.end();
    _pool = null;
  }
}

module.exports = { query, withTransaction, closePool, getPool };
