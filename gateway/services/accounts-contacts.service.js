const crypto = require('crypto');
const { createAccountEntity } = require('../entities/account.entity');
const { createContactEntity } = require('../entities/contact.entity');

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function buildId(prefix) {
  return `${prefix}_${crypto.randomUUID()}`;
}

class AccountsContactsService {
  constructor() {
    this.accountsByTenant = new Map();
    this.contactsByTenant = new Map();
  }

  getTenantMap(container, tenantId) {
    if (!container.has(tenantId)) {
      container.set(tenantId, new Map());
    }
    return container.get(tenantId);
  }

  listAccounts(tenantId) {
    return [...this.getTenantMap(this.accountsByTenant, tenantId).values()];
  }

  getAccount(tenantId, accountId) {
    return this.getTenantMap(this.accountsByTenant, tenantId).get(accountId) || null;
  }

  createAccount(tenantId, payload, actorUserId) {
    const ts = nowIso();
    const account = createAccountEntity({
      account_id: buildId('acc'),
      tenant_id: tenantId,
      owner_user_id: payload.owner_user_id || actorUserId,
      name: payload.name,
      industry: payload.industry || null,
      segment: payload.segment || null,
      status: payload.status || 'active',
      billing_address: payload.billing_address || null,
      created_at: ts,
      updated_at: ts,
    });

    this.getTenantMap(this.accountsByTenant, tenantId).set(account.account_id, account);
    return account;
  }

  updateAccount(tenantId, accountId, patch) {
    const account = this.getAccount(tenantId, accountId);
    if (!account) return null;

    const next = {
      ...account,
      ...patch,
      updated_at: nowIso(),
    };

    this.getTenantMap(this.accountsByTenant, tenantId).set(accountId, next);
    return next;
  }

  deleteAccount(tenantId, accountId) {
    const accountMap = this.getTenantMap(this.accountsByTenant, tenantId);
    const existed = accountMap.delete(accountId);

    if (existed) {
      const contactMap = this.getTenantMap(this.contactsByTenant, tenantId);
      for (const [contactId, contact] of contactMap.entries()) {
        if (contact.account_id === accountId) {
          contactMap.set(contactId, {
            ...contact,
            account_id: null,
            updated_at: nowIso(),
          });
        }
      }
    }

    return existed;
  }

  listContacts(tenantId) {
    return [...this.getTenantMap(this.contactsByTenant, tenantId).values()];
  }

  getContact(tenantId, contactId) {
    return this.getTenantMap(this.contactsByTenant, tenantId).get(contactId) || null;
  }

  createContact(tenantId, payload, actorUserId) {
    const ts = nowIso();
    const contact = createContactEntity({
      contact_id: buildId('con'),
      tenant_id: tenantId,
      account_id: payload.account_id || null,
      owner_user_id: payload.owner_user_id || actorUserId,
      first_name: payload.first_name,
      last_name: payload.last_name,
      email: payload.email || null,
      phone: payload.phone || null,
      lifecycle_status: payload.lifecycle_status || 'lead',
      created_at: ts,
      updated_at: ts,
    });

    this.getTenantMap(this.contactsByTenant, tenantId).set(contact.contact_id, contact);
    return contact;
  }

  updateContact(tenantId, contactId, patch) {
    const contact = this.getContact(tenantId, contactId);
    if (!contact) return null;

    const next = {
      ...contact,
      ...patch,
      updated_at: nowIso(),
    };

    this.getTenantMap(this.contactsByTenant, tenantId).set(contactId, next);
    return next;
  }

  deleteContact(tenantId, contactId) {
    return this.getTenantMap(this.contactsByTenant, tenantId).delete(contactId);
  }

  linkContactToAccount(tenantId, accountId, contactId) {
    const account = this.getAccount(tenantId, accountId);
    const contact = this.getContact(tenantId, contactId);

    if (!account || !contact) {
      return null;
    }

    return this.updateContact(tenantId, contactId, { account_id: accountId });
  }

  unlinkContactFromAccount(tenantId, accountId, contactId) {
    const contact = this.getContact(tenantId, contactId);
    if (!contact || contact.account_id !== accountId) {
      return null;
    }

    return this.updateContact(tenantId, contactId, { account_id: null });
  }
}

const accountsContactsService = new AccountsContactsService();

module.exports = {
  accountsContactsService,
};
