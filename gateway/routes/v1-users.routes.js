const express = require('express');
const { requestValidationMiddleware } = require('../middleware/request-validation');
const { respondSuccess } = require('../middleware/response-wrapper');

const router = express.Router();

router.get('/', requestValidationMiddleware(), (req, res) => {
  return respondSuccess(
    res,
    [
      {
        id: 'usr_01HZX7X4QW2D7B2K4A0G5R9M2C',
        email: 'jane.doe@example.com',
        display_name: 'Jane Doe',
        status: 'active',
        created_at: '2026-03-26T12:00:00Z',
        updated_at: '2026-03-26T12:00:00Z',
      },
    ],
    {
      pagination: {
        page: Number(req.query.page || 1),
        page_size: Number(req.query.page_size || 25),
        total_items: 1,
        total_pages: 1,
      },
    },
  );
});

router.post(
  '/',
  requestValidationMiddleware(['email', 'display_name', 'status']),
  (req, res) => {
    const now = '2026-03-26T12:00:00Z';

    return res.status(201).json({
      data: {
        id: 'usr_01NEW7X4QW2D7B2K4A0G5R9M2C',
        email: req.body.email,
        display_name: req.body.display_name,
        status: req.body.status,
        created_at: now,
        updated_at: now,
      },
      meta: {
        request_id: req.request_id,
      },
    });
  },
);

module.exports = router;
