/* Pakistan CRM — Approval Lanes (K-04) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var LANES = [
    { id:'draft',            label:'Draft',            color:'secondary', btnLabel: null         },
    { id:'pending_approval', label:'Pending Approval', color:'warning',   btnLabel:'Approve'     },
    { id:'approved',         label:'Approved',         color:'success',   btnLabel:'Convert to Order' },
    { id:'rejected',         label:'Rejected',         color:'danger',    btnLabel:'Revise'      }
  ];

  function pkr(n) { return 'PKR ' + (Number(n) || 0).toLocaleString('en-PK'); }

  function calcTotal(quote) {
    return (quote.line_items || []).reduce(function (s, li) {
      return s + li.list_price * li.qty * (1 - (li.discount || 0) / 100);
    }, 0);
  }

  function renderBoard(quotes) {
    var board = document.getElementById('approval-board');
    if (!board) return;

    board.innerHTML = LANES.map(function (lane) {
      var laneQuotes = quotes.filter(function (q) { return q.status === lane.id; });
      var cards = laneQuotes.length
        ? laneQuotes.map(function (q) {
            var total    = calcTotal(q);
            var hasLarge = (q.line_items || []).some(function (li) { return (li.discount || 0) > 10; });
            return '<div class="card mb-2 border-start border-3 border-' + lane.color + '" style="height:auto">' +
              '<div class="card-body py-2">' +
              '<div class="fw-semibold small">' + (q.quote_number || q.quote_id) + '</div>' +
              '<div class="small text-muted">' + (q.account_name || '—') + '</div>' +
              '<div class="d-flex align-items-center gap-2 mt-1">' +
              '<span class="fw-bold">' + pkr(total) + '</span>' +
              (hasLarge ? '<span class="badge bg-warning-subtle text-warning border border-warning-subtle small">Discount &gt;10%</span>' : '') +
              '</div>' +
              '<div class="d-flex gap-2 mt-2">' +
              '<a href="app/quotes-detail.html?id=' + q.quote_id + '" class="btn btn-xs btn-outline-secondary">View</a>' +
              (lane.btnLabel ? '<button class="btn btn-xs btn-' + lane.color + '" data-quote-id="' + q.quote_id + '" data-action="' + lane.id + '">' + lane.btnLabel + '</button>' : '') +
              '</div></div></div>';
          }).join('')
        : '<div class="text-center text-muted small py-3">No quotes in this lane.</div>';

      return '<div class="col-lg-3">' +
        '<div class="card bg-light" style="height:auto">' +
        '<div class="card-header d-flex align-items-center justify-content-between py-2">' +
        '<span class="fw-semibold small">' + lane.label + '</span>' +
        '<span class="badge bg-' + lane.color + '">' + laneQuotes.length + '</span>' +
        '</div>' +
        '<div class="card-body pb-1">' + cards + '</div>' +
        '</div></div>';
    }).join('');

    /* Approve button clicks (live action) */
    board.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-action]');
      if (!btn) return;
      var quoteId = btn.dataset.quoteId;
      var action  = btn.dataset.action;
      if (!quoteId || !action) return;

      if (cfg && !cfg.DUMMY_MODE && action === 'pending_approval') {
        fetch(cfg.BASE_URL + '/quotes/' + quoteId + '/approve', {
          method: 'POST',
          headers: { 'Authorization': 'Bearer ' + cfg.token, 'Content-Type': 'application/json', 'x-tenant-id': cfg.tenantId }
        }).then(function () {
          /* Move card visually — just reload the board */
          var q = quotes.filter(function (q) { return q.quote_id === quoteId; })[0];
          if (q) { q.status = 'approved'; renderBoard(quotes); }
        }).catch(function () {});
      }
    });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  function load() {
    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.quotes.list({ limit: 200 })
        .then(function (res) { renderBoard(res.data || []); })
        .catch(function () { renderBoard((_d && _d.quotes && _d.quotes.data) || []); });
    } else {
      renderBoard((_d && _d.quotes && _d.quotes.data) || []);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }

})();
