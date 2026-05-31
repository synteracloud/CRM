/* Pakistan CRM — Quote Detail (C-06) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var quoteId = new URLSearchParams(window.location.search).get('id') || 'q-001';

  function fmtDate(iso) {
    if (!iso) return '—';
    var dt = new Date(iso);
    return dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }
  function pkr(n) { return 'PKR ' + Number(Math.round(n)).toLocaleString('en-IN'); }

  var STATUS_CFG = {
    draft:            { cls:'secondary', label:'Draft'            },
    pending_approval: { cls:'warning',   label:'Pending Approval' },
    approved:         { cls:'success',   label:'Approved'         },
    rejected:         { cls:'danger',    label:'Rejected'         },
    sent:             { cls:'info',      label:'Sent'             },
    accepted:         { cls:'success',   label:'Accepted'         },
    expired:          { cls:'secondary', label:'Expired'          }
  };
  var STAGE_CFG = {
    qualification:{ cls:'info',      label:'Qualification' },
    discovery:    { cls:'primary',   label:'Discovery'     },
    proposal:     { cls:'warning',   label:'Proposal'      },
    negotiation:  { cls:'danger',    label:'Negotiation'   },
    closed_won:   { cls:'success',   label:'Closed Won'    },
    closed_lost:  { cls:'secondary', label:'Closed Lost'   }
  };
  function statusBadge(status) {
    var c = STATUS_CFG[status] || { cls:'secondary', label:status };
    return '<span class="badge bg-' + c.cls + '-subtle text-' + c.cls + '">' + c.label + '</span>';
  }
  function stageBadge(stage) {
    var c = STAGE_CFG[stage] || { cls:'secondary', label:stage };
    return '<span class="badge bg-' + c.cls + '-subtle text-' + c.cls + '">' + c.label + '</span>';
  }

  function render(quote) {
    if (!quote) {
      if (_d && _d.quotes && _d.quotes.data[0]) render(_d.quotes.data[0]);
      return;
    }

    var lineItems   = quote.line_items || [];
    var subtotal    = lineItems.reduce(function (s, li) { return s + Math.round(li.list_price * li.qty * (1 - li.discount / 100)); }, 0);
    var listTotal   = lineItems.reduce(function (s, li) { return s + li.qty * li.list_price; }, 0);
    var discountAmt = listTotal - subtotal;

    /* Identity strip */
    var qNum = quote.quote_number || quote.quote_id;
    $('#quote-breadcrumb').text(qNum);
    $('#quote-number-display').text(qNum);
    $('#quote-status-badge').html(statusBadge(quote.status));
    $('#quote-account-label').html('<i class="fi fi-rr-building me-1"></i>' + (quote.account_name || '—'));
    $('#quote-amount-strip').text(pkr(subtotal));

    /* Context panel */
    $('#ctx-status').html(statusBadge(quote.status));
    $('#ctx-account').text(quote.account_name || '—');
    $('#ctx-opp-stage').html(stageBadge(quote.opp_stage || 'proposal'));
    $('#ctx-subtotal').text(pkr(subtotal));
    $('#ctx-valid-until').text(fmtDate(quote.valid_until));
    $('#ctx-owner').text(quote.owner_id || '—');
    $('#ctx-quote-id').text(quote.quote_id);

    /* Line items table */
    var liHtml = lineItems.map(function (li) {
      var net = Math.round(li.list_price * li.qty * (1 - li.discount / 100));
      return '<tr>' +
        '<td class="text-center fw-semibold">' + (li.name || li.product_id || '—') + '</td>' +
        '<td class="text-center">' + li.qty + '</td>' +
        '<td class="text-center">' + pkr(li.list_price) + '</td>' +
        '<td class="text-center">' + (li.discount > 0 ? li.discount + '%' : '—') + '</td>' +
        '<td class="text-end fw-semibold text-primary">' + pkr(net) + '</td>' +
        '</tr>';
    }).join('');
    var footHtml = '<tr class="table-light">' +
      '<td colspan="3" class="text-end fw-semibold">List Total</td><td></td><td class="text-end">' + pkr(listTotal) + '</td></tr>' +
      '<tr><td colspan="3" class="text-end text-success fw-semibold">Discount</td><td></td><td class="text-end text-success">— ' + pkr(discountAmt) + '</td></tr>' +
      '<tr class="table-primary"><td colspan="3" class="text-end fw-bold">Subtotal</td><td></td><td class="text-end fw-bold">' + pkr(subtotal) + '</td></tr>';
    $('#quote-line-items-body').html(liHtml + footHtml);

    /* Terms */
    $('#quote-payment-terms').text(quote.payment_terms || 'Net 30 days');
    $('#quote-delivery-terms').text(quote.delivery_terms || 'Ex Works');
    $('#quote-expiry-date').text(fmtDate(quote.valid_until));
    $('#quote-notes').text(quote.notes || '—');

    /* Approval action buttons */
    if (quote.status === 'pending_approval') {
      $('#btn-approve-quote, #btn-reject-quote').removeClass('d-none');
    }
    $('#btn-approve-quote').on('click', function () {
      if (cfg && !cfg.DUMMY_MODE) {
        fetch(cfg.BASE_URL + '/quotes/' + quote.quote_id + '/approve', {
          method: 'POST',
          headers: { 'Authorization': 'Bearer ' + cfg.token, 'Content-Type': 'application/json', 'x-tenant-id': cfg.tenantId }
        }).catch(function () {});
      }
      $('#quote-status-badge').html(statusBadge('approved'));
      $('#ctx-status').html(statusBadge('approved'));
      $(this).prop('disabled', true);
      $('#btn-reject-quote').prop('disabled', true);
    });
    $('#btn-reject-quote').on('click', function () {
      if (cfg && !cfg.DUMMY_MODE) {
        fetch(cfg.BASE_URL + '/quotes/' + quote.quote_id + '/reject', {
          method: 'POST',
          headers: { 'Authorization': 'Bearer ' + cfg.token, 'Content-Type': 'application/json', 'x-tenant-id': cfg.tenantId }
        }).catch(function () {});
      }
      $('#quote-status-badge').html(statusBadge('rejected'));
      $('#ctx-status').html(statusBadge('rejected'));
      $(this).prop('disabled', true);
      $('#btn-approve-quote').prop('disabled', true);
    });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.quotes.get(quoteId)
      .then(function (res) { render(res.data); })
      .catch(function () {
        var q = _d && _d.quotes && _d.quotes.data.filter(function (q) { return q.quote_id === quoteId; })[0];
        render(q || (_d && _d.quotes && _d.quotes.data[0]));
      });
  } else {
    if (!_d) return;
    var quote = _d.quotes.data.filter(function (q) { return q.quote_id === quoteId; })[0]
             || _d.quotes.data[0];
    render(quote);
  }

})();
