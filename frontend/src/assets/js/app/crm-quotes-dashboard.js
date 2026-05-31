/* Pakistan CRM — Quote Approval Dashboard (A-05) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fmtDate(iso) {
    if (!iso) return '—';
    var p = (iso.indexOf('T') !== -1 ? iso.split('T')[0] : iso).split('-');
    return MONTHS[parseInt(p[1], 10) - 1] + ' ' + parseInt(p[2], 10) + ', ' + p[0];
  }
  function pkr(n) { return 'PKR ' + Number(Math.round(n)).toLocaleString('en-IN'); }

  function quoteTotal(q) {
    return (q.line_items || []).reduce(function (s, li) {
      return s + Math.round(li.qty * li.list_price * (1 - li.discount / 100));
    }, 0);
  }

  var STATUS_CFG = {
    draft:            { cls:'secondary', label:'Draft'            },
    pending_approval: { cls:'warning',   label:'Pending Approval' },
    approved:         { cls:'success',   label:'Approved'         },
    rejected:         { cls:'danger',    label:'Rejected'         }
  };

  function render(quotes) {
    var pending   = quotes.filter(function (q) { return q.status === 'pending_approval'; });
    var approved  = quotes.filter(function (q) { return q.status === 'approved'; });
    var drafts    = quotes.filter(function (q) { return q.status === 'draft'; });
    var totalValue= quotes.reduce(function (s, q) { return s + quoteTotal(q); }, 0);

    if (pending.length === 0) {
      $('#quote-posture-row').addClass('d-none');
    } else {
      $('#pending-approval-count').text(pending.length);
      $('#pending-plural').text(pending.length === 1 ? ' is' : 's are');
    }

    $('#kpi-total-quotes').text(quotes.length);
    $('#kpi-pending-approval').text(pending.length);
    $('#kpi-total-value').text(pkr(totalValue));

    var allDiscounts = [];
    quotes.forEach(function (q) {
      (q.line_items || []).forEach(function (li) {
        if (li.discount > 0) allDiscounts.push(li.discount);
      });
    });
    var avgDisc = allDiscounts.length > 0 ? Math.round(allDiscounts.reduce(function (s, v) { return s + v; }, 0) / allDiscounts.length) : 0;
    var maxDisc = allDiscounts.length > 0 ? Math.max.apply(null, allDiscounts) : 0;

    $('#risk-avg-discount').text(avgDisc + '%');
    $('#risk-max-discount').text(maxDisc + '%');
    $('#risk-draft-count').text(drafts.length);
    $('#discount-bar').css('width', Math.min(avgDisc * 5, 100) + '%');
    $('#discount-label').text('Avg discount: ' + avgDisc + '% across all line items');

    $('#pending-queue-badge').text(pending.length);

    var listHtml;
    if (pending.length === 0) {
      listHtml = '<div class="text-center py-4 text-muted small"><i class="fi fi-rr-badge-check fs-3 d-block mb-2 opacity-25"></i>No quotes pending approval.</div>';
    } else {
      listHtml = '<ul class="list-group list-group-flush">' +
        pending.map(function (q) {
          var total   = quoteTotal(q);
          var hasDisc = (q.line_items || []).some(function (li) { return li.discount > 10; });
          return '<li class="list-group-item px-3 py-3">' +
            '<div class="d-flex align-items-start justify-content-between gap-3">' +
            '<div class="flex-grow-1">' +
            '<div class="fw-semibold">' + (q.quote_number || q.quote_id) + '</div>' +
            '<div class="text-muted small mt-1"><i class="fi fi-rr-building me-1"></i>' + (q.account_name || '—') +
            ' · Expires ' + fmtDate(q.valid_until) + '</div></div>' +
            '<div class="text-end">' +
            '<div class="fw-bold text-primary small">' + pkr(total) + '</div>' +
            (hasDisc ? '<div class="text-warning small"><i class="fi fi-rr-exclamation me-1"></i>Discount &gt;10%</div>' : '') +
            '</div></div>' +
            '<div class="d-flex gap-2 mt-2">' +
            '<a href="app/quotes-detail.html?id=' + q.quote_id + '" class="btn btn-xs btn-outline-primary btn-sm py-0 px-2 waves-effect"><i class="fi fi-rr-eye me-1"></i>Review</a>' +
            '</div></li>';
        }).join('') + '</ul>';
    }
    $('#pending-quotes-list').html(listHtml);

    /* Status breakdown table */
    var statusRows = Object.keys(STATUS_CFG).map(function (s) {
      var cnt = quotes.filter(function (q) { return q.status === s; });
      var val = cnt.reduce(function (sum, q) { return sum + quoteTotal(q); }, 0);
      return '<tr>' +
        '<td class="text-center"><span class="badge bg-' + STATUS_CFG[s].cls + '-subtle text-' + STATUS_CFG[s].cls + '">' + STATUS_CFG[s].label + '</span></td>' +
        '<td class="text-center">' + cnt.length + '</td>' +
        '<td class="text-center">' + pkr(val) + '</td>' +
        '</tr>';
    }).join('');
    $('#quote-status-breakdown').html(statusRows);
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.quotes.list({ limit: 200 })
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.quotes && _d.quotes.data) || []); });
  } else {
    if (!_d) return;
    render(_d.quotes.data);
  }

})();
