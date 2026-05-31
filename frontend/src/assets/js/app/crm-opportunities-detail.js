/* Pakistan CRM — Opportunity Detail (C-04) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var oppId = new URLSearchParams(window.location.search).get('id') || 'o-007';

  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fmtDate(iso) {
    if (!iso) return '—';
    var p = iso.split('-');
    return MONTHS[parseInt(p[1], 10) - 1] + ' ' + parseInt(p[2], 10) + ', ' + p[0];
  }
  function pkr(n) { return 'PKR ' + Number(n).toLocaleString('en-IN'); }

  var stageBadge = {
    qualification: '<span class="badge bg-info-subtle text-info">Qualification</span>',
    discovery:     '<span class="badge bg-primary-subtle text-primary">Discovery</span>',
    proposal:      '<span class="badge bg-warning-subtle text-warning">Proposal</span>',
    negotiation:   '<span class="badge bg-danger-subtle text-danger">Negotiation</span>',
    closed_won:    '<span class="badge bg-success-subtle text-success">Closed Won</span>',
    closed_lost:   '<span class="badge bg-secondary-subtle text-secondary">Closed Lost</span>'
  };
  var forecastBadge = {
    pipeline:  '<span class="badge bg-info-subtle text-info">Pipeline</span>',
    best_case: '<span class="badge bg-warning-subtle text-warning">Best Case</span>',
    commit:    '<span class="badge bg-primary-subtle text-primary">Commit</span>',
    closed:    '<span class="badge bg-success-subtle text-success">Closed</span>',
    omitted:   '<span class="badge bg-secondary-subtle text-secondary">Omitted</span>'
  };
  var actIcons = {
    call:'fi-rr-phone-call text-success', email:'fi-rr-envelope text-primary',
    whatsapp:'fi-rr-whatsapp text-success', meeting:'fi-rr-users-alt text-primary',
    note:'fi-rr-note text-warning', stage_change:'fi-rr-exchange text-info', deal_won:'fi-rr-badge-check text-success'
  };

  function render(opp, tasks, acts, quotes) {
    if (!opp) {
      /* Show first dummy opp on 404 */
      if (_d && _d.opportunities && _d.opportunities.data[0]) {
        render(_d.opportunities.data[0], tasks, acts, quotes);
      }
      return;
    }

    var TODAY  = new Date().toISOString().substring(0, 10);
    var isOver = opp.stage !== 'closed_won' && opp.stage !== 'closed_lost' && opp.close_date < TODAY;

    /* Identity strip */
    $('#opp-breadcrumb').text(opp.name);
    $('#opp-name').text(opp.name);
    $('#opp-account-label').html('<i class="fi fi-rr-building me-1"></i>' + (opp.account_name || '—'));
    $('#opp-stage-badge').html(stageBadge[opp.stage] || opp.stage);
    $('#opp-forecast-badge').html(forecastBadge[opp.forecast_category] || opp.forecast_category);
    $('#opp-amount-strip').text(pkr(opp.amount));
    if (isOver) $('#opp-overdue-badge').removeClass('d-none');

    /* Context panel */
    var weighted = Math.round(opp.amount * (opp.probability || 0) / 100);
    $('#ctx-forecast-badge').html(forecastBadge[opp.forecast_category] || opp.forecast_category);
    $('#ctx-probability').text((opp.probability || 0) + '%');
    $('#ctx-weighted-value').text(pkr(weighted));
    $('#ctx-probability-bar').css('width', (opp.probability || 0) + '%');
    $('#ctx-close-label').text('Close: ' + fmtDate(opp.close_date) + (isOver ? ' ⚠ Overdue' : ''));
    $('#ctx-account-name').text(opp.account_name || '—');
    $('#ctx-owner').text(opp.owner_id || '—');
    $('#ctx-close-date').html('<span class="' + (isOver ? 'text-danger fw-bold' : '') + '">' + fmtDate(opp.close_date) + '</span>');
    $('#ctx-opp-id').text(opp.opportunity_id);

    /* Next action from tasks */
    var oppTask = tasks.filter(function (t) { return t.entity_id === opp.opportunity_id && t.status !== 'completed'; })[0];
    if (oppTask) {
      var taskOver = oppTask.due_at.substring(0, 10) < TODAY;
      $('#ctx-next-action-title').text(oppTask.title);
      $('#ctx-next-action-meta').html(
        'Due: <strong class="' + (taskOver ? 'text-danger' : '') + '">' + fmtDate(oppTask.due_at.substring(0, 10)) + '</strong>' +
        ' · ' + (oppTask.owner_id || '—') +
        ' · <span class="badge bg-' + ({hot:'danger',warm:'warning',cold:'secondary'}[oppTask.priority] || 'secondary') + '-subtle text-' + ({hot:'danger',warm:'warning',cold:'secondary'}[oppTask.priority] || 'secondary') + '">' + (oppTask.priority || '—') + '</span>'
      );
    }

    /* Tab 1: Deal fields */
    $('#field-name').val(opp.name);
    $('#field-account').val(opp.account_name || '');
    $('#field-amount').val(Number(opp.amount).toLocaleString('en-IN'));
    $('#field-close-date').val(fmtDate(opp.close_date));
    $('#field-stage').val((opp.stage || '').replace('_', ' '));
    $('#field-forecast').val((opp.forecast_category || '').replace('_', ' '));
    $('#field-probability').val((opp.probability || 0) + '%');
    $('#field-owner').val(opp.owner_id || '');

    /* Tab 2: Stage history (derived from current stage) */
    var stageOrder = ['qualification', 'discovery', 'proposal', 'negotiation', 'closed_won'];
    var currentIdx = stageOrder.indexOf(opp.stage);
    var stageCls   = { qualification:'info', discovery:'primary', proposal:'warning', negotiation:'danger', closed_won:'success', closed_lost:'secondary' };
    var histEntries = stageOrder.slice(0, Math.max(currentIdx + 1, 1));
    var histHtml    = histEntries.map(function (s, i) {
      var cls = stageCls[s] || 'secondary';
      var cur = s === opp.stage;
      return '<div class="d-flex gap-3 ' + (i < histEntries.length - 1 ? 'mb-4' : '') + '">' +
        '<div class="d-flex flex-column align-items-center">' +
        '<div class="avatar avatar-sm bg-' + cls + '-subtle text-' + cls + ' rounded-circle"><i class="fi fi-rr-' + (cur ? 'map-marker' : 'check') + '"></i></div>' +
        (i < histEntries.length - 1 ? '<div class="flex-grow-1 border-start border-2 border-light mt-1" style="min-height:30px;"></div>' : '') +
        '</div>' +
        '<div class="pb-1"><div class="fw-semibold text-capitalize">' + s.replace('_', ' ') + (cur ? ' <span class="badge bg-' + cls + '-subtle text-' + cls + ' ms-1">Current</span>' : '') + '</div></div>' +
        '</div>';
    }).join('');
    $('#stage-history-timeline').html(histHtml);

    /* Tab 3: Quotes */
    var STATUS_BADGE = {
      draft:'<span class="badge bg-secondary-subtle text-secondary">Draft</span>',
      pending_approval:'<span class="badge bg-warning-subtle text-warning">Pending Approval</span>',
      approved:'<span class="badge bg-success-subtle text-success">Approved</span>',
      rejected:'<span class="badge bg-danger-subtle text-danger">Rejected</span>'
    };
    var linkedQuotes = quotes.filter(function (q) { return q.opportunity_id === opp.opportunity_id; });
    if (linkedQuotes.length === 0) {
      $('#quotes-list').html('<div class="text-center py-4 text-muted"><i class="fi fi-rr-file-invoice fs-1 d-block mb-2 opacity-25"></i><p class="mb-0">No quotes linked to this deal yet.</p></div>');
    } else {
      var qHtml = linkedQuotes.map(function (q) {
        var subtotal = (q.line_items || []).reduce(function (sum, li) { return sum + Math.round(li.list_price * li.qty * (1 - li.discount / 100)); }, 0);
        return '<div class="card border mb-2"><div class="card-body py-3">' +
          '<div class="d-flex justify-content-between align-items-center">' +
          '<div><div class="fw-semibold">' + (q.quote_number || q.quote_id) + '</div>' +
          '<div class="text-muted small">' + (q.account_name || '—') + ' · Expires ' + fmtDate(q.valid_until) + '</div></div>' +
          '<div class="d-flex gap-2 align-items-center">' +
          (STATUS_BADGE[q.status] || '<span class="badge bg-secondary-subtle text-secondary">' + q.status + '</span>') +
          '<span class="fw-semibold text-primary">' + pkr(subtotal) + '</span>' +
          '<a href="app/quotes-detail.html?id=' + q.quote_id + '" class="btn btn-sm btn-white btn-shadow waves-effect"><i class="fi fi-rr-eye me-1"></i>View</a>' +
          '</div></div></div></div>';
      }).join('');
      $('#quotes-list').html(qHtml);
    }

    /* Tab 4: Activity timeline */
    var oppActs = acts.filter(function (a) { return a.entity_id === opp.opportunity_id; });
    var actHtml = oppActs.length
      ? oppActs.map(function (a) {
          var icon = actIcons[a.activity_type] || 'fi-rr-dot-circle text-muted';
          return '<li class="list-group-item px-0 py-3">' +
            '<div class="d-flex gap-3 align-items-start">' +
            '<div class="avatar avatar-sm bg-light rounded-circle flex-shrink-0 d-flex align-items-center justify-content-center"><i class="fi ' + icon + '"></i></div>' +
            '<div class="flex-grow-1"><div class="fw-semibold">' + a.description + '</div>' +
            '<div class="text-muted small mt-1">' + fmtDate(a.occurred_at.substring(0, 10)) + ' · ' + (a.performed_by || '—') + '</div>' +
            '</div></div></li>';
        }).join('')
      : '<li class="list-group-item text-muted small px-0 py-3">No activity logged yet.</li>';
    $('#opp-activity-timeline').html(actHtml);

    /* Stage action buttons */
    var stageOrderFull = ['qualification', 'discovery', 'proposal', 'negotiation', 'closed_won'];
    $('#btn-advance-stage').on('click', function () {
      var idx = stageOrderFull.indexOf(opp.stage);
      if (idx >= 0 && idx < stageOrderFull.length - 1) {
        if (cfg && !cfg.DUMMY_MODE) {
          window.CRM_API.opportunities.patch(opp.opportunity_id, { stage: stageOrderFull[idx + 1] })
            .catch(function () {});
        }
        opp.stage = stageOrderFull[idx + 1];
        $('#opp-stage-badge').html(stageBadge[opp.stage] || opp.stage);
        $('#field-stage').val(opp.stage.replace('_', ' '));
        if (opp.stage === 'closed_won') {
          $(this).prop('disabled', true).text('Deal Won');
          $('#btn-mark-won').prop('disabled', true);
        }
      }
    });
    $('#btn-mark-won').on('click', function () {
      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.opportunities.patch(opp.opportunity_id, { stage: 'closed_won' }).catch(function () {});
      }
      opp.stage = 'closed_won';
      $('#opp-stage-badge').html(stageBadge['closed_won']);
      $('#btn-advance-stage').prop('disabled', true);
      $(this).prop('disabled', true);
    });
    $('#btn-mark-lost').on('click', function () {
      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.opportunities.patch(opp.opportunity_id, { stage: 'closed_lost' }).catch(function () {});
      }
      opp.stage = 'closed_lost';
      $('#opp-stage-badge').html(stageBadge['closed_lost']);
      $('#btn-advance-stage').prop('disabled', true);
      $('#btn-mark-won').prop('disabled', true);
      $(this).prop('disabled', true);
    });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.opportunities.get(oppId).catch(function () { return { data: null }; }),
      window.CRM_API.tasks.list({ entity_id: oppId, limit: 50 }).catch(function () { return { data: [] }; }),
      window.CRM_API.activities.list({ entity_id: oppId, limit: 50 }).catch(function () { return { data: [] }; }),
      window.CRM_API.quotes.list({ opportunity_id: oppId, limit: 50 }).catch(function () { return { data: [] }; })
    ]).then(function (results) {
      render(results[0].data, results[1].data || [], results[2].data || [], results[3].data || []);
    });
  } else {
    if (!_d) return;
    var opp = _d.opportunities.data.filter(function (o) { return o.opportunity_id === oppId; })[0]
           || _d.opportunities.data[0];
    render(opp, _d.tasks.data, _d.activities.data, (_d.quotes && _d.quotes.data) || []);
  }

})();
