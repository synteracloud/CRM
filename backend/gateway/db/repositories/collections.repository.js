'use strict';

/**
 * Collections repository — DB-backed CRUD for transaction_db.
 *
 * Docs: docs/collections-engine-model.md
 *       db/transaction_db/schema.sql
 *       db/transaction_db/migrations/0003_add_payments_revenue.up.sql
 *
 * Schema: transaction_db
 * Tables: subscription, invoice_summary, payment_event, payment,
 *         payment_status_history, revenue_ledger
 *
 * Key: Status transitions on payment go through the DB stored procedure
 *      transaction_db.apply_payment_status_transition(), which enforces the
 *      FSM, writes payment_status_history, and appends to revenue_ledger atomically.
 *
 * Payment status FSM (enforced by is_valid_payment_status_transition):
 *   initiated → authorized | failed | canceled
 *   authorized → captured | failed | canceled
 *   captured → settled | partially_refunded | refunded | chargeback
 *   settled → partially_refunded | refunded | chargeback
 *   partially_refunded → refunded | chargeback
 */

const { query, withTransaction } = require('../pool');

const VALID_SUBSCRIPTION_STATUSES = ['draft', 'trialing', 'active', 'paused', 'past_due', 'canceled', 'expired'];
const VALID_INVOICE_STATUSES      = ['draft', 'open', 'paid', 'void', 'uncollectible'];
const VALID_PAYMENT_STATUSES      = ['initiated', 'authorized', 'captured', 'settled', 'failed', 'canceled', 'partially_refunded', 'refunded', 'chargeback'];
const VALID_PAYMENT_EVENT_TYPES   = ['authorized', 'captured', 'settled', 'failed', 'refunded', 'chargeback'];
const VALID_PAYMENT_METHODS       = ['card', 'bank_transfer', 'wallet', 'ach', 'other'];

class CollectionsRepository {
  // ── Subscriptions ─────────────────────────────────────────────────────────────

  async createSubscription(tenantId, data) {
    const {
      subscription_id,
      account_id,
      quote_id,
      external_subscription_ref,
      plan_code,
      status = 'draft',
      start_date,
      end_date,
      renewal_date,
    } = data;

    const { rows } = await query(
      `INSERT INTO transaction_db.subscription
         (subscription_id, tenant_id, account_id, quote_id, external_subscription_ref,
          plan_code, status, start_date, end_date, renewal_date)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
       RETURNING *`,
      [
        subscription_id, tenantId, account_id, quote_id || null,
        external_subscription_ref || null, plan_code, status,
        start_date, end_date || null, renewal_date || null,
      ],
    );
    return rows[0];
  }

  async findSubscriptionById(tenantId, subscriptionId) {
    const { rows } = await query(
      `SELECT * FROM transaction_db.subscription
       WHERE tenant_id = $1 AND subscription_id = $2`,
      [tenantId, subscriptionId],
    );
    return rows[0] || null;
  }

  async listSubscriptions(tenantId, { account_id, status, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (account_id) { conditions.push(`account_id = $${p++}`); params.push(account_id); }
    if (status)     { conditions.push(`status = $${p++}`);     params.push(status); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM transaction_db.subscription
       WHERE ${conditions.join(' AND ')}
       ORDER BY created_at DESC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  async updateSubscription(tenantId, subscriptionId, patch) {
    const allowed = ['status', 'end_date', 'renewal_date', 'plan_code', 'external_subscription_ref'];
    const fields = Object.keys(patch).filter((k) => allowed.includes(k));
    if (fields.length === 0) throw new Error('no valid fields to update');

    const sets = fields.map((f, i) => `${f} = $${i + 3}`).join(', ');
    const values = fields.map((f) => patch[f]);

    const { rows } = await query(
      `UPDATE transaction_db.subscription SET ${sets}
       WHERE tenant_id = $1 AND subscription_id = $2
       RETURNING *`,
      [tenantId, subscriptionId, ...values],
    );
    return rows[0] || null;
  }

  // ── Invoices ──────────────────────────────────────────────────────────────────

  async createInvoice(tenantId, data) {
    const {
      invoice_summary_id,
      subscription_id,
      external_invoice_ref,
      invoice_number,
      amount_due,
      currency,
      status = 'draft',
      due_date,
      issued_at,
    } = data;

    const { rows } = await query(
      `INSERT INTO transaction_db.invoice_summary
         (invoice_summary_id, tenant_id, subscription_id, external_invoice_ref,
          invoice_number, amount_due, currency, status, due_date, issued_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
       RETURNING *`,
      [
        invoice_summary_id, tenantId, subscription_id,
        external_invoice_ref || null, invoice_number,
        amount_due, currency, status, due_date, issued_at,
      ],
    );
    return rows[0];
  }

  async findInvoiceById(tenantId, invoiceId) {
    const { rows } = await query(
      `SELECT * FROM transaction_db.invoice_summary
       WHERE tenant_id = $1 AND invoice_summary_id = $2`,
      [tenantId, invoiceId],
    );
    return rows[0] || null;
  }

  async listInvoices(tenantId, { subscription_id, status, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (subscription_id) { conditions.push(`subscription_id = $${p++}`); params.push(subscription_id); }
    if (status)          { conditions.push(`status = $${p++}`);           params.push(status); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM transaction_db.invoice_summary
       WHERE ${conditions.join(' AND ')}
       ORDER BY due_date DESC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  async updateInvoiceStatus(tenantId, invoiceId, { status, amount_paid }) {
    const sets = [];
    const params = [tenantId, invoiceId];
    let p = 3;

    if (status !== undefined)     { sets.push(`status = $${p++}`);      params.push(status); }
    if (amount_paid !== undefined) { sets.push(`amount_paid = $${p++}`); params.push(amount_paid); }
    if (sets.length === 0) throw new Error('no valid fields to update');

    const { rows } = await query(
      `UPDATE transaction_db.invoice_summary SET ${sets.join(', ')}
       WHERE tenant_id = $1 AND invoice_summary_id = $2
       RETURNING *`,
      params,
    );
    return rows[0] || null;
  }

  // ── Payment Events ────────────────────────────────────────────────────────────

  async createPaymentEvent(tenantId, data) {
    const {
      payment_event_id,
      subscription_id,
      invoice_summary_id,
      external_payment_ref,
      event_type,
      amount,
      currency,
      event_time,
      status,
    } = data;

    const { rows } = await query(
      `INSERT INTO transaction_db.payment_event
         (payment_event_id, tenant_id, subscription_id, invoice_summary_id,
          external_payment_ref, event_type, amount, currency, event_time, status)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
       RETURNING *`,
      [
        payment_event_id, tenantId,
        subscription_id || null, invoice_summary_id || null,
        external_payment_ref || null, event_type,
        amount, currency, event_time, status,
      ],
    );
    return rows[0];
  }

  async listPaymentEvents(tenantId, { invoice_summary_id, status, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (invoice_summary_id) { conditions.push(`invoice_summary_id = $${p++}`); params.push(invoice_summary_id); }
    if (status)             { conditions.push(`status = $${p++}`);             params.push(status); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM transaction_db.payment_event
       WHERE ${conditions.join(' AND ')}
       ORDER BY event_time DESC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  // ── Payments ──────────────────────────────────────────────────────────────────

  async createPayment(tenantId, data) {
    const {
      payment_id,
      subscription_id,
      invoice_summary_id,
      external_payment_ref,
      payment_method_type,
      amount,
      currency,
      status = 'initiated',
      initiated_at,
    } = data;

    const { rows } = await query(
      `INSERT INTO transaction_db.payment
         (payment_id, tenant_id, subscription_id, invoice_summary_id,
          external_payment_ref, payment_method_type, amount, currency, status, initiated_at)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
       RETURNING *`,
      [
        payment_id, tenantId,
        subscription_id || null, invoice_summary_id || null,
        external_payment_ref || null, payment_method_type,
        amount, currency, status,
        initiated_at || new Date().toISOString(),
      ],
    );
    return rows[0];
  }

  async findPaymentById(tenantId, paymentId) {
    const { rows } = await query(
      `SELECT * FROM transaction_db.payment
       WHERE tenant_id = $1 AND payment_id = $2`,
      [tenantId, paymentId],
    );
    return rows[0] || null;
  }

  async listPayments(tenantId, { subscription_id, invoice_summary_id, status, limit = 25, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (subscription_id)  { conditions.push(`subscription_id = $${p++}`);  params.push(subscription_id); }
    if (invoice_summary_id) { conditions.push(`invoice_summary_id = $${p++}`); params.push(invoice_summary_id); }
    if (status)           { conditions.push(`status = $${p++}`);           params.push(status); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM transaction_db.payment
       WHERE ${conditions.join(' AND ')}
       ORDER BY created_at DESC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }

  // Atomic FSM-validated status transition — delegates to DB stored procedure.
  // The procedure: validates the transition, updates payment, writes
  // payment_status_history, and appends to revenue_ledger (on settled/refunded/chargeback).
  async transitionPaymentStatus(tenantId, paymentId, { new_status, changed_at, reason, changed_by_user_id }) {
    const { rows } = await query(
      `SELECT * FROM transaction_db.apply_payment_status_transition($1, $2, $3, $4, $5, $6)`,
      [
        tenantId, paymentId, new_status,
        changed_at || new Date().toISOString(),
        reason || null,
        changed_by_user_id || null,
      ],
    );
    return rows[0] || null;  // { payment_id, previous_status, current_status }
  }

  async listPaymentStatusHistory(tenantId, paymentId) {
    const { rows } = await query(
      `SELECT * FROM transaction_db.payment_status_history
       WHERE tenant_id = $1 AND payment_id = $2
       ORDER BY changed_at ASC`,
      [tenantId, paymentId],
    );
    return rows;
  }

  // ── Revenue Ledger ────────────────────────────────────────────────────────────

  // Ledger entries are written automatically by apply_payment_status_transition.
  // This method provides a read-only view for reporting.
  async listRevenueLedger(tenantId, { payment_id, limit = 50, offset = 0 } = {}) {
    const conditions = ['tenant_id = $1'];
    const params = [tenantId];
    let p = 2;

    if (payment_id) { conditions.push(`payment_id = $${p++}`); params.push(payment_id); }

    params.push(limit, offset);
    const { rows } = await query(
      `SELECT * FROM transaction_db.revenue_ledger
       WHERE ${conditions.join(' AND ')}
       ORDER BY recognized_at DESC
       LIMIT $${p} OFFSET $${p + 1}`,
      params,
    );
    return rows;
  }
}

module.exports = {
  CollectionsRepository,
  VALID_SUBSCRIPTION_STATUSES,
  VALID_INVOICE_STATUSES,
  VALID_PAYMENT_STATUSES,
  VALID_PAYMENT_EVENT_TYPES,
  VALID_PAYMENT_METHODS,
};
