const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondError, respondSuccess } = require('../middleware/response-wrapper');
const { requireScopes } = require('../middleware/auth-rbac');
const { validateContactInput } = require('../entities/contact.entity');
const { accountsContactsService } = require('../services/accounts-contacts.service');

const router = express.Router();

const createFields = [
  'account_id',
  'owner_user_id',
  'first_name',
  'last_name',
  'email',
  'phone',
  'lifecycle_status',
];
const patchFields = createFields;

router.get('/', requestValidationMiddleware(), requireScopes(['contacts.read']), (req, res) => {
  const data = accountsContactsService.listContacts(req.auth.tenant_id);
  return respondSuccess(res, data, {
    pagination: {
      page: Number(req.query.page || 1),
      page_size: Number(req.query.page_size || 25),
      total_items: data.length,
      total_pages: 1,
    },
  });
});

router.post('/', requestValidationMiddleware(createFields), requireScopes(['contacts.create']), (req, res) => {
  const errors = validateContactInput(req.body);
  if (errors.length > 0) {
    return respondError(res, 'validation_error', 'One or more fields are invalid.', errors, 422);
  }

  if (req.body.account_id) {
    const account = accountsContactsService.getAccount(req.auth.tenant_id, req.body.account_id);
    if (!account) {
      return respondError(
        res,
        'validation_error',
        'One or more fields are invalid.',
        [{ field: 'account_id', reason: 'must_reference_existing_account' }],
        422,
      );
    }
  }

  const contact = accountsContactsService.createContact(req.auth.tenant_id, req.body, req.auth.sub);
  return res.status(201).json({
    data: contact,
    meta: { request_id: req.request_id },
  });
});

router.get('/:contact_id', requestValidationMiddleware(), requireScopes(['contacts.read']), (req, res) => {
  const contact = accountsContactsService.getContact(req.auth.tenant_id, req.params.contact_id);
  if (!contact) {
    return respondError(res, 'not_found', 'Contact not found.', [{ field: 'contact_id', reason: 'not_found' }], 404);
  }

  return respondSuccess(res, contact);
});

router.patch('/:contact_id', requestValidationMiddleware(patchFields), requireScopes(['contacts.update']), (req, res) => {
  const errors = validateContactInput(req.body, { partial: true });
  if (errors.length > 0) {
    return respondError(res, 'validation_error', 'One or more fields are invalid.', errors, 422);
  }

  if (req.body.account_id) {
    const account = accountsContactsService.getAccount(req.auth.tenant_id, req.body.account_id);
    if (!account) {
      return respondError(
        res,
        'validation_error',
        'One or more fields are invalid.',
        [{ field: 'account_id', reason: 'must_reference_existing_account' }],
        422,
      );
    }
  }

  const contact = accountsContactsService.updateContact(req.auth.tenant_id, req.params.contact_id, req.body);
  if (!contact) {
    return respondError(res, 'not_found', 'Contact not found.', [{ field: 'contact_id', reason: 'not_found' }], 404);
  }

  return respondSuccess(res, contact);
});

router.delete('/:contact_id', requestValidationMiddleware(), requireScopes(['contacts.delete']), (req, res) => {
  const deleted = accountsContactsService.deleteContact(req.auth.tenant_id, req.params.contact_id);
  if (!deleted) {
    return respondError(res, 'not_found', 'Contact not found.', [{ field: 'contact_id', reason: 'not_found' }], 404);
  }

  return respondSuccess(res, { contact_id: req.params.contact_id, deleted: true });
});

module.exports = router;
