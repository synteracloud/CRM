'use strict';

/**
 * Canonical RBAC scope registry.
 *
 * Docs: docs/identity-auth-rbac.md — 6 canonical roles + permission matrix
 *       docs/security-model.md — default-deny, least-privilege enforcement
 *
 * Rules:
 *   - ROLE_SCOPES is the single source of truth for role → allowed scopes.
 *   - Route handlers call requireScopes([...]) with scopes from SCOPES.
 *   - Auth middleware validates that the JWT role grants all required scopes.
 *   - Default-deny: any scope not in ROLE_SCOPES[role] is denied.
 */

const SCOPES = Object.freeze({
  // Leads
  LEADS_READ:    'leads.read',
  LEADS_CREATE:  'leads.create',
  LEADS_UPDATE:  'leads.update',
  LEADS_DELETE:  'leads.delete',
  LEADS_ASSIGN:  'leads.assign',

  // Opportunities / Deals
  OPPORTUNITIES_READ:   'opportunities.read',
  OPPORTUNITIES_CREATE: 'opportunities.create',
  OPPORTUNITIES_UPDATE: 'opportunities.update',
  OPPORTUNITIES_CLOSE:  'opportunities.close',

  // Follow-ups
  FOLLOWUPS_READ:     'followups.read',
  FOLLOWUPS_CREATE:   'followups.create',
  FOLLOWUPS_COMPLETE: 'followups.complete',
  FOLLOWUPS_SNOOZE:   'followups.snooze',

  // Collections / Invoices
  COLLECTIONS_READ:       'collections.read',
  COLLECTIONS_INVOICE:    'collections.invoice',
  COLLECTIONS_RECONCILE:  'collections.reconcile',

  // Payments (existing routes)
  PAYMENTS_READ:   'payments.read',
  PAYMENTS_CREATE: 'payments.create',
  PAYMENTS_UPDATE: 'payments.update',
  REVENUE_READ:    'revenue.read',

  // Contacts & Accounts
  CONTACTS_READ:   'contacts.read',
  CONTACTS_CREATE: 'contacts.create',
  CONTACTS_UPDATE: 'contacts.update',
  ACCOUNTS_READ:   'accounts.read',
  ACCOUNTS_CREATE: 'accounts.create',
  ACCOUNTS_UPDATE: 'accounts.update',

  // CPQ
  QUOTES_READ:    'quotes.read',
  QUOTES_CREATE:  'quotes.create',
  QUOTES_UPDATE:  'quotes.update',
  ORDERS_READ:    'orders.read',

  // Sync
  SYNC_WRITE: 'sync.write',
  SYNC_READ:  'sync.read',

  // Admin
  USERS_READ:   'users.read',
  USERS_CREATE: 'users.create',
  USERS_UPDATE: 'users.update',
  AUDIT_READ:   'audit.read',

  // Subscriptions / Billing
  SUBSCRIPTIONS_READ:   'subscriptions.read',
  SUBSCRIPTIONS_CREATE: 'subscriptions.create',
  SUBSCRIPTIONS_UPDATE: 'subscriptions.update',

  // Cases / Support Tickets (Sprint 5B-1)
  CASES_READ:   'cases.read',
  CASES_CREATE: 'cases.create',
  CASES_UPDATE: 'cases.update',
  CASES_ADMIN:  'cases.admin',   // assign, force-close, escalate, queue management

  // Knowledge Base (Sprint 5B-1)
  KNOWLEDGE_READ:   'knowledge.read',
  KNOWLEDGE_MANAGE: 'knowledge.manage',  // create, publish, archive articles

  // Shared Inbox (Sprint 5B-2)
  INBOX_READ:  'inbox.read',   // view conversations + presence board
  INBOX_WRITE: 'inbox.write',  // claim, send messages, update own presence
  INBOX_ADMIN: 'inbox.admin',  // handoff any conversation, manage queues

  // Territories (Sprint 5B-3)
  TERRITORIES_READ:  'territories.read',   // list + view + performance
  TERRITORIES_WRITE: 'territories.write',  // manual reassignment
  TERRITORIES_ADMIN: 'territories.admin',  // create, update, deactivate, manage rules

  // Marketing / Campaigns (Sprint 5B-4)
  CAMPAIGNS_READ:   'campaigns.read',    // view campaigns, segments, templates
  CAMPAIGNS_MANAGE: 'campaigns.manage',  // create, edit, activate, pause, cancel

  // Partners (Sprint 5B-5)
  PARTNERS_READ:   'partners.read',    // view partners, deal registrations
  PARTNERS_MANAGE: 'partners.manage',  // create, edit, approve/reject deals, approve commission
  PARTNERS_ADMIN:  'partners.admin',   // pay commission, change tier/status

  // Workflows (Sprint 5B-6)
  WORKFLOWS_READ:   'workflows.read',    // view definitions, executions, stats
  WORKFLOWS_MANAGE: 'workflows.manage',  // create, publish, retry, cancel executions

  // AI / Predictive Models (Sprint 5B-7)
  AI_SCORES_READ:    'ai.scores.read',       // view lead scores
  AI_SCORES_RECOMPUTE: 'ai.scores.recompute', // force-recompute a score (manager+)
  AI_PREDICTIONS_READ: 'ai.predictions.read', // view churn predictions (manager+)
  AI_CLV_READ:       'ai.clv.read',          // view CLV estimates (manager+)
  AI_COPILOT:        'ai.copilot',           // copilot suggestions + query (all roles)
  AI_MODELS_READ:    'ai.models.read',       // model registry (manager+)
});

// Role → granted scopes mapping.
// Roles from docs/identity-auth-rbac.md.
const ROLE_SCOPES = Object.freeze({
  tenant_owner: Object.values(SCOPES),   // all scopes

  tenant_admin: [
    SCOPES.LEADS_READ, SCOPES.LEADS_CREATE, SCOPES.LEADS_UPDATE, SCOPES.LEADS_DELETE, SCOPES.LEADS_ASSIGN,
    SCOPES.OPPORTUNITIES_READ, SCOPES.OPPORTUNITIES_CREATE, SCOPES.OPPORTUNITIES_UPDATE, SCOPES.OPPORTUNITIES_CLOSE,
    SCOPES.FOLLOWUPS_READ, SCOPES.FOLLOWUPS_CREATE, SCOPES.FOLLOWUPS_COMPLETE, SCOPES.FOLLOWUPS_SNOOZE,
    SCOPES.COLLECTIONS_READ, SCOPES.COLLECTIONS_INVOICE, SCOPES.COLLECTIONS_RECONCILE,
    SCOPES.PAYMENTS_READ, SCOPES.PAYMENTS_CREATE, SCOPES.PAYMENTS_UPDATE, SCOPES.REVENUE_READ,
    SCOPES.CONTACTS_READ, SCOPES.CONTACTS_CREATE, SCOPES.CONTACTS_UPDATE,
    SCOPES.ACCOUNTS_READ, SCOPES.ACCOUNTS_CREATE, SCOPES.ACCOUNTS_UPDATE,
    SCOPES.QUOTES_READ, SCOPES.QUOTES_CREATE, SCOPES.QUOTES_UPDATE, SCOPES.ORDERS_READ,
    SCOPES.SYNC_WRITE, SCOPES.SYNC_READ,
    SCOPES.USERS_READ, SCOPES.USERS_CREATE, SCOPES.USERS_UPDATE,
    SCOPES.SUBSCRIPTIONS_READ, SCOPES.SUBSCRIPTIONS_CREATE, SCOPES.SUBSCRIPTIONS_UPDATE,
    SCOPES.CASES_READ, SCOPES.CASES_CREATE, SCOPES.CASES_UPDATE, SCOPES.CASES_ADMIN,
    SCOPES.KNOWLEDGE_READ, SCOPES.KNOWLEDGE_MANAGE,
    SCOPES.INBOX_READ, SCOPES.INBOX_WRITE, SCOPES.INBOX_ADMIN,
    SCOPES.TERRITORIES_READ, SCOPES.TERRITORIES_WRITE, SCOPES.TERRITORIES_ADMIN,
    SCOPES.CAMPAIGNS_READ, SCOPES.CAMPAIGNS_MANAGE,
    SCOPES.PARTNERS_READ, SCOPES.PARTNERS_MANAGE, SCOPES.PARTNERS_ADMIN,
    SCOPES.WORKFLOWS_READ, SCOPES.WORKFLOWS_MANAGE,
    SCOPES.AI_SCORES_READ, SCOPES.AI_SCORES_RECOMPUTE,
    SCOPES.AI_PREDICTIONS_READ, SCOPES.AI_CLV_READ,
    SCOPES.AI_COPILOT, SCOPES.AI_MODELS_READ,
  ],

  manager: [
    SCOPES.LEADS_READ, SCOPES.LEADS_CREATE, SCOPES.LEADS_UPDATE, SCOPES.LEADS_ASSIGN,
    SCOPES.OPPORTUNITIES_READ, SCOPES.OPPORTUNITIES_CREATE, SCOPES.OPPORTUNITIES_UPDATE, SCOPES.OPPORTUNITIES_CLOSE,
    SCOPES.FOLLOWUPS_READ, SCOPES.FOLLOWUPS_CREATE, SCOPES.FOLLOWUPS_COMPLETE, SCOPES.FOLLOWUPS_SNOOZE,
    SCOPES.COLLECTIONS_READ, SCOPES.COLLECTIONS_INVOICE,
    SCOPES.PAYMENTS_READ, SCOPES.REVENUE_READ,
    SCOPES.CONTACTS_READ, SCOPES.CONTACTS_CREATE, SCOPES.CONTACTS_UPDATE,
    SCOPES.ACCOUNTS_READ, SCOPES.ACCOUNTS_CREATE, SCOPES.ACCOUNTS_UPDATE,
    SCOPES.QUOTES_READ, SCOPES.QUOTES_CREATE, SCOPES.QUOTES_UPDATE, SCOPES.ORDERS_READ,
    SCOPES.SYNC_WRITE, SCOPES.SYNC_READ,
    SCOPES.USERS_READ,
    SCOPES.CASES_READ, SCOPES.CASES_CREATE, SCOPES.CASES_UPDATE, SCOPES.CASES_ADMIN,
    SCOPES.KNOWLEDGE_READ, SCOPES.KNOWLEDGE_MANAGE,
    SCOPES.INBOX_READ, SCOPES.INBOX_WRITE, SCOPES.INBOX_ADMIN,
    SCOPES.TERRITORIES_READ, SCOPES.TERRITORIES_WRITE,
    SCOPES.CAMPAIGNS_READ, SCOPES.CAMPAIGNS_MANAGE,
    SCOPES.PARTNERS_READ, SCOPES.PARTNERS_MANAGE,
    SCOPES.WORKFLOWS_READ, SCOPES.WORKFLOWS_MANAGE,
    SCOPES.AI_SCORES_READ, SCOPES.AI_SCORES_RECOMPUTE,
    SCOPES.AI_PREDICTIONS_READ, SCOPES.AI_CLV_READ,
    SCOPES.AI_COPILOT, SCOPES.AI_MODELS_READ,
  ],

  agent: [
    SCOPES.LEADS_READ, SCOPES.LEADS_CREATE, SCOPES.LEADS_UPDATE,
    SCOPES.OPPORTUNITIES_READ, SCOPES.OPPORTUNITIES_CREATE, SCOPES.OPPORTUNITIES_UPDATE,
    SCOPES.FOLLOWUPS_READ, SCOPES.FOLLOWUPS_CREATE, SCOPES.FOLLOWUPS_COMPLETE, SCOPES.FOLLOWUPS_SNOOZE,
    SCOPES.COLLECTIONS_READ,
    SCOPES.PAYMENTS_READ,
    SCOPES.CONTACTS_READ, SCOPES.CONTACTS_CREATE, SCOPES.CONTACTS_UPDATE,
    SCOPES.ACCOUNTS_READ,
    SCOPES.QUOTES_READ, SCOPES.QUOTES_CREATE,
    SCOPES.SYNC_WRITE, SCOPES.SYNC_READ,
    SCOPES.CASES_READ, SCOPES.CASES_CREATE, SCOPES.CASES_UPDATE,
    SCOPES.KNOWLEDGE_READ,
    SCOPES.INBOX_READ, SCOPES.INBOX_WRITE,
    SCOPES.TERRITORIES_READ,
    SCOPES.CAMPAIGNS_READ,
    SCOPES.PARTNERS_READ,
    SCOPES.WORKFLOWS_READ,
    SCOPES.AI_SCORES_READ, SCOPES.AI_COPILOT,
  ],

  analyst: [
    SCOPES.LEADS_READ,
    SCOPES.OPPORTUNITIES_READ,
    SCOPES.FOLLOWUPS_READ,
    SCOPES.COLLECTIONS_READ,
    SCOPES.PAYMENTS_READ, SCOPES.REVENUE_READ,
    SCOPES.CONTACTS_READ,
    SCOPES.ACCOUNTS_READ,
    SCOPES.QUOTES_READ, SCOPES.ORDERS_READ,
    SCOPES.SUBSCRIPTIONS_READ,
    SCOPES.SYNC_READ,
    SCOPES.CASES_READ,
    SCOPES.KNOWLEDGE_READ,
    SCOPES.AI_SCORES_READ, SCOPES.AI_PREDICTIONS_READ, SCOPES.AI_CLV_READ, SCOPES.AI_MODELS_READ,
  ],

  auditor: [
    SCOPES.AUDIT_READ,
    SCOPES.LEADS_READ,
    SCOPES.PAYMENTS_READ, SCOPES.REVENUE_READ,
    SCOPES.COLLECTIONS_READ,
    SCOPES.SYNC_READ,
  ],

  integration_service: Object.values(SCOPES),  // service accounts get all scopes
});

/**
 * Check whether a role grants all of the required scopes.
 * Returns true only if every required scope is in the role's grant list.
 */
function roleGrantsScopes(role, requiredScopes) {
  const granted = new Set(ROLE_SCOPES[role] || []);
  return requiredScopes.every((s) => granted.has(s));
}

module.exports = { SCOPES, ROLE_SCOPES, roleGrantsScopes };
