const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { validateAccountInput } = require('../entities/account.entity');
const { accountsContactsService } = require('../services/accounts-contacts.service');

const router = express.Router();

const createFields = ['owner_user_id', 'name', 'industry', 'segment', 'status', 'billing_address'];
const patchFields = ['owner_user_id', 'name', 'industry', 'segment', 'status', 'billing_address'];

router.get('/', requestValidationMiddleware(), requireScopes(['accounts.read']), (req, res) => {
  const data = accountsContactsService.listAccounts(req.auth.tenant_id);
  return respondSuccess(res, data, {
    pagination: {
      page: Number(req.query.page || 1),
      page_size: Number(req.query.page_size || 25),
      total_items: data.length,
      total_pages: 1,
    },
  });
});

router.post('/', requestValidationMiddleware(createFields), requireScopes(['accounts.create']), (req, res) => {
  const errors = validateAccountInput(req.body);
  if (errors.length > 0) {
    return respondError(res, 'validation_error', 'One or more fields are invalid.', errors, 422);
  }

  const account = accountsContactsService.createAccount(req.auth.tenant_id, req.body, req.auth.sub);
  return res.status(201).json({
    data: account,
    meta: { request_id: req.request_id },
  });
});

router.get('/:account_id', requestValidationMiddleware(), requireScopes(['accounts.read']), (req, res) => {
  const account = accountsContactsService.getAccount(req.auth.tenant_id, req.params.account_id);
  if (!account) {
    return respondError(res, 'not_found', 'Account not found.', [{ field: 'account_id', reason: 'not_found' }], 404);
  }

  return respondSuccess(res, account);
});

router.patch('/:account_id', requestValidationMiddleware(patchFields), requireScopes(['accounts.update']), (req, res) => {
  const errors = validateAccountInput(req.body, { partial: true });
  if (errors.length > 0) {
    return respondError(res, 'validation_error', 'One or more fields are invalid.', errors, 422);
  }

  const account = accountsContactsService.updateAccount(req.auth.tenant_id, req.params.account_id, req.body);
  if (!account) {
    return respondError(res, 'not_found', 'Account not found.', [{ field: 'account_id', reason: 'not_found' }], 404);
  }

  return respondSuccess(res, account);
});

router.delete('/:account_id', requestValidationMiddleware(), requireScopes(['accounts.delete']), (req, res) => {
  const deleted = accountsContactsService.deleteAccount(req.auth.tenant_id, req.params.account_id);
  if (!deleted) {
    return respondError(res, 'not_found', 'Account not found.', [{ field: 'account_id', reason: 'not_found' }], 404);
  }

  return respondSuccess(res, { account_id: req.params.account_id, deleted: true });
});

router.put(
  '/:account_id/contacts/:contact_id',
  requestValidationMiddleware(),
  requireScopes(['accounts.contacts.link']),
  (req, res) => {
    const contact = accountsContactsService.linkContactToAccount(req.auth.tenant_id, req.params.account_id, req.params.contact_id);

    if (!contact) {
      return respondError(
        res,
        'not_found',
        'Account or contact not found.',
        [
          { field: 'account_id', reason: 'not_found_or_not_accessible' },
          { field: 'contact_id', reason: 'not_found_or_not_accessible' },
        ],
        404,
      );
    }

    return respondSuccess(res, contact);
  },
);

router.delete(
  '/:account_id/contacts/:contact_id',
  requestValidationMiddleware(),
  requireScopes(['accounts.contacts.unlink']),
  (req, res) => {
    const contact = accountsContactsService.unlinkContactFromAccount(req.auth.tenant_id, req.params.account_id, req.params.contact_id);

    if (!contact) {
      return respondError(
        res,
        'not_found',
        'Linked account-contact relationship not found.',
        [{ field: 'relationship', reason: 'not_found' }],
        404,
      );
    }

    return respondSuccess(res, contact);
  },
);

module.exports = router;
