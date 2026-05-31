/* Pakistan CRM — Invoice Detail (C-08) */

(function () {
  'use strict';

  var cfg       = window.CRM_CONFIG;
  var _d        = window.CRM_DUMMY;
  var invoiceId = new URLSearchParams(window.location.search).get('id') || 'i-001';

  function pkr(n) { if (!n && n !== 0) return '—'; n = Number(n); if (n >= 100000) return 'PKR ' + (n/100000).toFixed(2) + ' L'; return 'PKR ' + n.toLocaleString('en-IN'); }
  var statusCfg = {
    paid:           'bg-success-subtle text-success',
    overdue:        'bg-danger-subtle text-danger',
    partial:        'bg-warning-subtle text-warning',
    sent:           'bg-info-subtle text-info',
    open:           'bg-info-subtle text-info',
    draft:          'bg-secondary-subtle text-secondary',
    void:           'bg-secondary-subtle text-secondary',
    uncollectible:  'bg-danger-subtle text-danger',
  };

  function render(inv) {
    if (!inv) {
      /* Fall back to first dummy invoice */
      var fallback = (_d && _d.invoices && _d.invoices.data && _d.invoices.data[0]);
      if (fallback) render(fallback);
      return;
    }

    var totalAmt  = Number(inv.total_amount || inv.amount_due)    || 0;
    var paidAmt   = Number(inv.paid_amount  || inv.amount_paid)   || 0;
    var balance   = totalAmt - paidAmt;
    var status    = inv.status || 'draft';

    /* Header strip */
    $('#inv-breadcrumb').text(inv.invoice_number || inv.invoice_summary_id || '—');
    $('#inv-number').text(inv.invoice_number || '—');
    $('#inv-account-label').html('<i class="fi fi-rr-building me-1"></i>' + (inv.account_name || '—'));
    $('#inv-status-badge').html('<span class="badge ' + (statusCfg[status] || 'bg-secondary-subtle text-secondary') + '">' + status + '</span>');
    $('#inv-balance-header').text(balance > 0 ? pkr(balance) : pkr(0))
      .toggleClass('text-danger', balance > 0).toggleClass('text-success', balance <= 0);

    /* Detail fields */
    $('#inv-total').text(pkr(totalAmt));
    $('#inv-paid').text(pkr(paidAmt));
    $('#inv-due').text(inv.due_date || '—');
    $('#det-inv-number').text(inv.invoice_number || '—');
    $('#det-account').text(inv.account_name || '—');
    $('#det-total').text(pkr(totalAmt));
    $('#det-paid').text(pkr(paidAmt));
    $('#det-balance').text(pkr(balance));
    $('#det-due').text(inv.due_date || '—');
    $('#det-status').html('<span class="badge ' + (statusCfg[status] || 'bg-secondary-subtle text-secondary') + '">' + status + '</span>');
    $('#det-created').text(inv.issued_at ? inv.issued_at.slice(0, 10) : (inv.created_at ? inv.created_at.slice(0, 10) : '—'));

    /* Line items */
    var lineItems = inv.line_items || [];
    if (lineItems.length > 0) {
      var liHtml = lineItems.map(function (li) {
        var net = Number(li.total || ((li.unit_price || li.list_price || 0) * (li.qty || li.quantity || 1) * (1 - (li.discount || 0) / 100))) || 0;
        return '<tr>' +
          '<td class="text-center">' + (li.description || li.name || li.product || '—') + '</td>' +
          '<td class="text-center">' + (li.qty || li.quantity || 1) + '</td>' +
          '<td class="text-center">' + pkr(li.unit_price || li.list_price) + '</td>' +
          '<td class="text-center">' + ((li.discount || 0) > 0 ? li.discount + '%' : '—') + '</td>' +
          '<td class="text-center fw-semibold">' + pkr(net) + '</td></tr>';
      }).join('');
      $('#inv-line-items').html(liHtml);
    }

    /* Payment history */
    var payments = inv.payment_history || [];
    if (payments.length > 0) {
      $('#payment-history').html(payments.map(function (p) {
        return '<div class="d-flex align-items-start gap-2 py-2 border-bottom">' +
          '<div class="avatar avatar-xxs rounded-circle bg-success-subtle text-success mt-1"><i class="fi fi-rr-check"></i></div>' +
          '<div><div class="small fw-semibold">Payment received — ' + pkr(p.amount) + '</div>' +
          '<div class="text-muted" style="font-size:.75rem;">' + (p.method || 'Bank transfer') + ' · ' + (p.date || p.recorded_at || '') + '</div></div></div>';
      }).join(''));
    } else if (paidAmt > 0) {
      $('#payment-history').html(
        '<div class="d-flex align-items-start gap-2 py-2 border-bottom">' +
        '<div class="avatar avatar-xxs rounded-circle bg-success-subtle text-success mt-1"><i class="fi fi-rr-check"></i></div>' +
        '<div><div class="small fw-semibold">Payment received — ' + pkr(paidAmt) + '</div>' +
        '<div class="text-muted" style="font-size:.75rem;">Bank transfer · ' + (inv.due_date || '—') + '</div></div></div>'
      );
    } else {
      $('#payment-history').html('<p class="text-muted small text-center py-3">No payments recorded</p>');
    }

    /* Reconciliation strip */
    $('#recon-status').text(status === 'paid' ? 'Reconciled' : 'Pending')
      .removeClass('bg-secondary-subtle text-secondary')
      .addClass(status === 'paid' ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning');

    /* Action button gates */
    if (status === 'paid') $('#btn-record-payment').addClass('d-none');
    if (status !== 'sent' && status !== 'partial' && status !== 'overdue') $('#btn-send-wa-reminder').addClass('d-none');

    /* Record Payment action */
    var recBtn = document.getElementById('btn-record-payment');
    if (recBtn) {
      recBtn.addEventListener('click', function () {
        var cid = inv.invoice_id || inv.invoice_summary_id;
        if (!cid) { alert('No invoice ID available.'); return; }
        if (cfg && !cfg.DUMMY_MODE) {
          var amount = window.prompt('Payment amount (PKR):');
          if (!amount) return;
          window.CRM_API.collections.recordPayment(cid, { amount_paid: Number(amount), method: 'bank_transfer' })
            .then(function () { location.reload(); })
            .catch(function () { alert('Error recording payment.'); });
        } else {
          alert('Payment recorded (dummy mode — not persisted).');
        }
      });
    }
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.invoiceSummaries.getById(invoiceId)
      .then(function (res) { render(res.data); })
      .catch(function () {
        var inv = (_d && _d.invoices && _d.invoices.data && _d.invoices.data.filter(function (i) { return i.invoice_id === invoiceId || i.invoice_number === invoiceId; })[0]);
        render(inv || (_d && _d.invoices && _d.invoices.data && _d.invoices.data[0]));
      });
  } else {
    if (!_d) return;
    var inv = (_d.invoices && _d.invoices.data && _d.invoices.data.filter(function (i) { return i.invoice_id === invoiceId; })[0]) ||
              (_d.invoices && _d.invoices.data && _d.invoices.data[0]);
    render(inv || null);
  }

})();
