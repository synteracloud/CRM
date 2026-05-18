'use strict';

/**
 * Contacts + Accounts repository — DB-backed CRUD for contact_account_db.
 *
 * Docs: docs/domain-model.md — Contact, Account entities
 *       db/contact_account_db/schema.sql
 *
 * Schema: contact_account_db
 * Tables: contacts, accounts
 *
 * Rules:
 *   - (tenant_id, phone_e164) is the deduplication key for contacts — UNIQUE constraint
 *   - All queries tenant-scoped
 *   - findByPhone is the Anti-Lead-Loss Guarantee lookup (BEHAV-002)
 */

const { query, withTransaction } = require('../pool');

const VALID_STATUSES    = ['active', 'inactive', 'blocked'];
const VALID_LIFECYCLES  = ['lead', 'prospect', 'customer', 'churned'];

class ContactsRepository {
  // ── Contacts ─────────────────────────────────────────────────────────────────

  async createContact(tenantId, data) {
    const {
      contact_id,
      first_name,
      last_name,
      email,
      phone_e164,
      account_id,
      owner_id,
      status = 'active',
      lifecycle = 'lead',
      tags = [],
    } = data;

    const { rows } = await query(
      `INSERT INTO contact_account_db.contacts
         (contact_id, tenant_id, first_name, last_name, email, phone_e164,
          account_id, owner_id, status, lifecycle, tags)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
       ON CONFLICT (tenant_id, phone_e164) DO NOTHING
       RETURNING *`,
      [
        contact_id, tenantId, first_name || null, last_name || null,
        email || null, phone_e164, account_id || null, owner_id || null,
        status, lifecycle, JSON.stringify(tags),
      ],
    );
    return rows[0] || null;  // null = duplicate (conflict suppressed)
  }

  async findContactById(tenantId, contactId) {
    const { rows } = await query(
      `SELECT * FROM contact_account_db.contacts
       WHERE tenant_id = $1 AND contact_id = $2`,
      [tenantId, contactId],
    );
    return rows[0] || null;
  }

  // Anti-Lead-Loss Guarantee lookup (BEHAV-002) — keyed on E.164 phone
  async findContactByPhone(tenantId, phoneE164) {
    const { rows } = await query(
      `SELECT * FROM contact_account_db.contacts
       WHERE tenant_id = $1 AND phone_e164 = $2`,
      [tenantId, phoneE164],
    );
    return rows[0] || null;
  }

  async listContacts(tenantId, { status, lifecycle, account_id, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (status)     { conditions.push(`status = $${p++}`);     params.push(status); }
    if (lifecycle)  { conditions.push(`lifecycle = $${p++}`);  params.push(lifecycle); }
    if (account_id) { conditions.push(`account_id = $${p++}`); params.push(account_id); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM contact_account_db.contacts
       WHERE ${conditions.join(' AND ')}
       ORDER BY created_at DESC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  async updateContact(tenantId, contactId, patch) {
    const allowed = ['first_name', 'last_name', 'email', 'account_id', 'owner_id', 'status', 'lifecycle', 'tags'];
    const fields = Object.keys(patch).filter((k) => allowed.includes(k));
    if (fields.length === 0) throw new Error('no valid fields to update');

    const sets = fields.map((f, i) => `${f} = $${i + 3}`).join(', ');
    const values = fields.map((f) => (f === 'tags' ? JSON.stringify(patch[f]) : patch[f]));

    const { rows } = await query(
      `UPDATE contact_account_db.contacts SET ${sets}
       WHERE tenant_id = $1 AND contact_id = $2
       RETURNING *`,
      [tenantId, contactId, ...values],
    );
    return rows[0] || null;
  }

  // ── Accounts ─────────────────────────────────────────────────────────────────

  async createAccount(tenantId, data) {
    const { account_id, name, domain, industry, size_band, owner_id, parent_account_id } = data;
    const { rows } = await query(
      `INSERT INTO contact_account_db.accounts
         (account_id, tenant_id, name, domain, industry, size_band, owner_id, parent_account_id)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
       RETURNING *`,
      [account_id, tenantId, name, domain || null, industry || null,
       size_band || null, owner_id || null, parent_account_id || null],
    );
    return rows[0];
  }

  async findAccountById(tenantId, accountId) {
    const { rows } = await query(
      `SELECT * FROM contact_account_db.accounts
       WHERE tenant_id = $1 AND account_id = $2`,
      [tenantId, accountId],
    );
    return rows[0] || null;
  }

  async listAccounts(tenantId, { owner_id, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (owner_id) { conditions.push(`owner_id = $${p++}`); params.push(owner_id); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM contact_account_db.accounts
       WHERE ${conditions.join(' AND ')}
       ORDER BY name ASC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  async updateAccount(tenantId, accountId, patch) {
    const allowed = ['name', 'domain', 'industry', 'size_band', 'owner_id', 'parent_account_id'];
    const fields = Object.keys(patch).filter((k) => allowed.includes(k));
    if (fields.length === 0) throw new Error('no valid fields to update');

    const sets = fields.map((f, i) => `${f} = $${i + 3}`).join(', ');
    const values = fields.map((f) => patch[f]);

    const { rows } = await query(
      `UPDATE contact_account_db.accounts SET ${sets}
       WHERE tenant_id = $1 AND account_id = $2
       RETURNING *`,
      [tenantId, accountId, ...values],
    );
    return rows[0] || null;
  }
}

module.exports = { ContactsRepository, VALID_STATUSES, VALID_LIFECYCLES };
