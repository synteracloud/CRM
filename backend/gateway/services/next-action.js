'use strict';

/**
 * Next-action card service — P-014.
 *
 * Docs: docs/followup-enforcement-model.md §2.D — Next Action Suggestion
 *       docs/adoption-ux.md §2 (Tier 1 — follow-up queue)
 *       gateway/routes/v1-leads.routes.js — GET /:id/next-action (data source)
 *
 * This module fetches the next-action suggestion for a lead and maps it to
 * display-ready card data.  All UI priority-to-style mappings live here —
 * never in component code.
 *
 * Priority badges:  urgent → red / critical
 *                   high   → amber / warning
 *                   normal → default / info
 *
 * Usage::
 *   const { fetchNextAction, toCardData } = require('./next-action');
 *   const suggestion = await fetchNextAction(leadId, authHeader);
 *   const card = toCardData(suggestion, locale);
 */

const http  = require('http');
const https = require('https');
const { getString, interpolate } = require('./i18n');

const GATEWAY_BASE_URL = process.env.GATEWAY_BASE_URL || 'http://localhost:3000';

// ── Priority → display style mapping ─────────────────────────────────────────

const PRIORITY_STYLE = Object.freeze({
  urgent: { colorRole: 'color.state.critical', badgeType: 'critical', icon: '🔴' },
  high:   { colorRole: 'color.state.warning',  badgeType: 'warning',  icon: '🟡' },
  normal: { colorRole: 'color.state.info',     badgeType: 'info',     icon: '🔵' },
});

// ── Action → i18n key mapping ─────────────────────────────────────────────────

const ACTION_I18N_KEY = Object.freeze({
  call:           'next_action.call',
  send_whatsapp:  'next_action.send_whatsapp',
  send_reminder:  'next_action.send_reminder',
  escalate:       'next_action.escalate',
  close:          'next_action.close',
});

// ── HTTP fetch ────────────────────────────────────────────────────────────────

/**
 * Fetch the next-action suggestion for a lead from the gateway's own API.
 * Uses the internal route which calls the followup service.
 *
 * @param {string} leadId      — lead identifier
 * @param {string} authHeader  — "Bearer <token>" value
 * @param {string} tenantId    — tenant identifier (required by auth middleware)
 * @returns {Promise<object>}  — NextActionSuggestion | stub
 */
function fetchNextAction(leadId, authHeader, tenantId) {
  return new Promise((resolve, reject) => {
    const url    = `${GATEWAY_BASE_URL}/api/v1/leads/${encodeURIComponent(leadId)}/next-action`;
    const parsed = new URL(url);
    const client = parsed.protocol === 'https:' ? https : http;

    const req = client.get(
      {
        hostname: parsed.hostname,
        port:     parsed.port || (parsed.protocol === 'https:' ? 443 : 80),
        path:     `${parsed.pathname}${parsed.search}`,
        headers: {
          'Authorization': authHeader,
          'x-tenant-id':   tenantId,
          'Accept':        'application/json',
        },
      },
      (res) => {
        let body = '';
        res.on('data', (chunk) => { body += chunk; });
        res.on('end', () => {
          try {
            const parsed = JSON.parse(body);
            resolve(parsed.data || parsed);
          } catch {
            reject(new Error('Invalid JSON from next-action endpoint'));
          }
        });
      },
    );
    req.on('error', reject);
    req.setTimeout(5000, () => { req.destroy(); reject(new Error('next-action timeout')); });
  });
}

// ── Display mapping ────────────────────────────────────────────────────────────

/**
 * Map a NextActionSuggestion to display-ready card data.
 *
 * @param {object} suggestion  — response from GET /leads/:id/next-action
 * @param {string} [locale]    — "en" | "ur" (default "en")
 * @returns {object}           — card display data
 */
function toCardData(suggestion, locale = 'en') {
  if (!suggestion || suggestion._stub) {
    return {
      available:      false,
      stub:           true,
      title:          getString('next_action.title', locale),
      message:        getString('error.generic', locale),
      actionLabel:    null,
      priorityStyle:  PRIORITY_STYLE.normal,
      dueBy:          null,
      raw:            suggestion || null,
    };
  }

  const priority     = suggestion.priority || 'normal';
  const actionKey    = ACTION_I18N_KEY[suggestion.suggested_action] || 'next_action.send_reminder';
  const actionLabel  = getString(actionKey, locale);
  const priorityStyle = PRIORITY_STYLE[priority] || PRIORITY_STYLE.normal;

  let dueByDisplay = null;
  if (suggestion.due_by) {
    const due = new Date(suggestion.due_by);
    const now = new Date();
    const diffMs = due - now;
    if (diffMs < 0) {
      dueByDisplay = getString('next_action.overdue', locale);
    } else {
      const diffMin = Math.round(diffMs / 60000);
      if (diffMin < 60) {
        dueByDisplay = interpolate(getString('next_action.due_by', locale), { when: `${diffMin}m` });
      } else {
        const diffHr = Math.round(diffMin / 60);
        dueByDisplay = interpolate(getString('next_action.due_by', locale), { when: `${diffHr}h` });
      }
    }
  }

  return {
    available:      true,
    stub:           false,
    title:          getString('next_action.title', locale),
    actionLabel,
    reason:         suggestion.reason,
    priority,
    priorityStyle,
    dueBy:          suggestion.due_by,
    dueByDisplay,
    leadId:         suggestion.lead_id,
    suggestedAction: suggestion.suggested_action,
    raw:            suggestion,
  };
}

module.exports = { fetchNextAction, toCardData, PRIORITY_STYLE, ACTION_I18N_KEY };
