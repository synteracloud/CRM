/* Pakistan CRM — Order Detail (C-07) */

(function () {
  'use strict';

  var cfg     = window.CRM_CONFIG;
  var _d      = window.CRM_DUMMY;
  var orderId = new URLSearchParams(window.location.search).get('id') || 'ord-001';

  function pkr(n) { if (!n) return '—'; n = Number(n); if (n >= 100000) return 'PKR ' + (n / 100000).toFixed(2) + ' L'; return 'PKR ' + n.toLocaleString('en-IN'); }
  var statusCfg = { activated:'bg-success-subtle text-success', draft:'bg-secondary-subtle text-secondary', cancelled:'bg-danger-subtle text-danger' };
  var fulfCfg   = { delivered:'bg-success-subtle text-success', pending:'bg-warning-subtle text-warning', failed:'bg-danger-subtle text-danger' };

  function render(ord, invoices, quotes) {
    if (!ord) {
      if (_d && _d.orders && _d.orders.data && _d.orders.data[0]) render(_d.orders.data[0], (_d.invoices && _d.invoices.data) || [], (_d.quotes && _d.quotes.data) || []);
      return;
    }

    $('#ord-breadcrumb').text(ord.order_number || ord.order_id);
    $('#ord-number').text(ord.order_number || ord.order_id);
    $('#ord-account-label').html('<i class="fi fi-rr-building me-1"></i>' + (ord.account_name || '—'));
    $('#ord-status-badge').html('<span class="badge ' + (statusCfg[ord.status] || 'bg-secondary-subtle text-secondary') + '">' + (ord.status || '—') + '</span>');
    $('#ord-fulfillment-badge').html('<span class="badge ' + (fulfCfg[ord.fulfillment_status] || 'bg-secondary-subtle text-secondary') + '">' + (ord.fulfillment_status || '—') + '</span>');
    $('#ord-total, #ord-total-footer').text(pkr(ord.total_amount));

    var linesHtml = (ord.line_items || []).map(function (li) {
      return '<tr>' +
        '<td class="text-center">' + (li.product || li.name || '—') + '</td>' +
        '<td class="text-center">' + (li.qty || li.quantity || 1) + '</td>' +
        '<td class="text-center">' + pkr(li.unit_price || li.list_price) + '</td>' +
        '<td class="text-center">' + ((li.discount > 0) ? li.discount + '%' : '—') + '</td>' +
        '<td class="text-center fw-semibold">' + pkr(li.total || ((li.unit_price || li.list_price || 0) * (li.qty || li.quantity || 1) * (1 - (li.discount || 0) / 100))) + '</td></tr>';
    }).join('');
    $('#ord-line-items').html(linesHtml || '<tr><td colspan="5" class="text-center text-muted">No line items</td></tr>');

    $('#billing-addr').text(ord.billing_address || '—');
    $('#shipping-addr').text(ord.shipping_address || '—');
    $('#ctx-created').text(ord.created_at ? ord.created_at.slice(0, 10) : '—');
    $('#ctx-fulfil').text(ord.fulfillment_status || '—');

    var q = quotes.filter(function (q) { return q.quote_id === ord.quote_id; })[0];
    $('#ctx-quote').text(q ? (q.quote_number || q.quote_id) : (ord.quote_id || '—'));

    var linkedInv = invoices.filter(function (i) { return (ord.invoice_ids || []).indexOf(i.invoice_id || i.invoice_number) !== -1; });
    if (linkedInv.length > 0) {
      var invCls = { paid:'bg-success-subtle text-success', overdue:'bg-danger-subtle text-danger', partial:'bg-warning-subtle text-warning', sent:'bg-info-subtle text-info', draft:'bg-secondary-subtle text-secondary' };
      $('#ord-invoices-list').html(linkedInv.map(function (i) {
        return '<div class="d-flex justify-content-between align-items-center py-2 border-bottom small">' +
          '<span class="fw-semibold">' + (i.invoice_number || i.invoice_id) + '</span>' +
          '<span>' + pkr(i.total_amount) + '</span>' +
          '<span class="badge ' + (invCls[i.status] || 'bg-secondary-subtle text-secondary') + '">' + i.status + '</span></div>';
      }).join(''));
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.orders.get(orderId).catch(function () { return { data: null }; }),
      window.CRM_API.invoiceSummaries.get({ limit: 200 }).catch(function () { return { data: [] }; }),
      window.CRM_API.quotes.list({ limit: 100 }).catch(function () { return { data: [] }; })
    ]).then(function (results) {
      var ord = results[0].data;
      if (!ord && _d && _d.orders) ord = _d.orders.data.filter(function (o) { return o.order_id === orderId; })[0];
      render(ord, Array.isArray(results[1].data) ? results[1].data : [], results[2].data || []);
    });
  } else {
    if (!_d) return;
    var ords = (_d.orders && _d.orders.data) || [];
    var ord  = ords.filter(function (o) { return o.order_id === orderId; })[0] || ords[0];
    render(ord, (_d.invoices && _d.invoices.data) || [], (_d.quotes && _d.quotes.data) || []);
  }

})();
