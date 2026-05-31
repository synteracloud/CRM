/* Pakistan CRM — Sales Cockpit (D-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var TARGET = 5500000;

  function pkr(n) { return 'PKR ' + Number(n).toLocaleString('en-IN'); }
  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fmtDate(iso) {
    if (!iso) return '—';
    var p = iso.split('-');
    return MONTHS[parseInt(p[1], 10) - 1] + ' ' + parseInt(p[2], 10) + ', ' + p[0];
  }

  var stageBadge = {
    qualification:'<span class="badge bg-info-subtle text-info">Qualification</span>',
    discovery:    '<span class="badge bg-primary-subtle text-primary">Discovery</span>',
    proposal:     '<span class="badge bg-warning-subtle text-warning">Proposal</span>',
    negotiation:  '<span class="badge bg-danger-subtle text-danger">Negotiation</span>',
    closed_won:   '<span class="badge bg-success-subtle text-success">Closed Won</span>',
    closed_lost:  '<span class="badge bg-secondary-subtle text-secondary">Closed Lost</span>'
  };
  var forecastBadge = {
    pipeline: '<span class="badge bg-info-subtle text-info">Pipeline</span>',
    best_case:'<span class="badge bg-warning-subtle text-warning">Best Case</span>',
    commit:   '<span class="badge bg-primary-subtle text-primary">Commit</span>',
    closed:   '<span class="badge bg-success-subtle text-success">Closed</span>',
    omitted:  '<span class="badge bg-secondary-subtle text-secondary">Omitted</span>'
  };

  function render(rows, tasks, acts) {
    var TODAY = new Date().toISOString().substring(0, 10);

    function isOverdueClose(row) {
      return row.stage !== 'closed_won' && row.stage !== 'closed_lost' && row.close_date < TODAY;
    }

    var userMap = {};
    ((_d && _d.users && _d.users.data) || []).forEach(function (u) { userMap[u.id] = u.display_name; });

    /* Forecast computed from opps */
    var fc = (function () {
      var byCategory = { pipeline:{count:0,total_value:0}, best_case:{count:0,total_value:0}, commit:{count:0,total_value:0}, closed:{count:0,total_value:0}, omitted:{count:0,total_value:0} };
      var weighted   = 0;
      rows.forEach(function (o) {
        var cat = byCategory[o.forecast_category];
        if (cat) { cat.count++; cat.total_value += o.amount || 0; }
        weighted += (o.amount || 0) * (o.probability || 0) / 100;
      });
      return { weighted_value: Math.round(weighted), by_category: byCategory };
    }());

    /* Posture strip */
    var overdueRows = rows.filter(isOverdueClose);
    var oc = overdueRows.length;
    var ov = overdueRows.reduce(function (s, r) { return s + (r.amount || 0); }, 0);
    $('#cockpit-overdue-count').text(oc);
    $('#cockpit-overdue-plural').text(oc === 1 ? ' has' : 's have');
    $('#cockpit-overdue-value').text(pkr(ov));
    if (oc === 0) $('#cockpit-posture-row').addClass('d-none');

    /* Forecast panel */
    var pct = fc.weighted_value > 0 ? Math.round((fc.weighted_value / TARGET) * 100) : 0;
    $('#forecast-weighted-pipeline').text(pkr(fc.weighted_value));
    $('#forecast-closed-won').text(pkr(fc.by_category.closed.total_value));
    $('#forecast-commit').text(pkr(fc.by_category.commit.total_value));
    $('#forecast-best-case').text(pkr(fc.by_category.best_case.total_value));
    var gap = TARGET - fc.by_category.closed.total_value;
    $('#forecast-gap').text(pkr(gap > 0 ? gap : 0));
    $('#forecast-progress-bar').css('width', Math.min(pct, 100) + '%');
    $('#forecast-progress-label').text(pct + '% of target');

    /* Next actions panel */
    var oppTasks = tasks.filter(function (t) { return t.entity_type === 'opportunity'; });
    var overdueTaskCount = 0;
    var taskHtml = oppTasks.map(function (t) {
      var isOT = t.status !== 'completed' && t.due_at.substring(0, 10) < TODAY;
      if (isOT) overdueTaskCount++;
      var cls  = { hot:'danger', warm:'warning', cold:'secondary' }[t.priority] || 'secondary';
      var icon = t.status === 'completed' ? 'fi-rr-check-circle text-success' : (isOT ? 'fi-rr-clock text-danger' : 'fi-rr-circle text-muted');
      return '<li class="list-group-item px-3 py-2">' +
        '<div class="d-flex align-items-start gap-2">' +
        '<i class="fi ' + icon + ' mt-1 flex-shrink-0"></i>' +
        '<div class="flex-grow-1 overflow-hidden">' +
        '<div class="small fw-semibold text-truncate' + (t.status === 'completed' ? ' text-decoration-line-through text-muted' : '') + '">' + t.title + '</div>' +
        '<div class="text-muted" style="font-size:.7rem;">' + (userMap[t.owner_id] || t.owner_id) + ' · ' + fmtDate(t.due_at.substring(0, 10)) + '</div>' +
        '</div><span class="badge bg-' + cls + '-subtle text-' + cls + ' flex-shrink-0 text-capitalize">' + (t.priority || '—') + '</span>' +
        '</div></li>';
    }).join('');
    $('#cockpit-tasks-list').html(taskHtml || '<li class="list-group-item text-muted small p-3">No tasks</li>');
    if (overdueTaskCount > 0) $('#task-overdue-badge').text(overdueTaskCount + ' overdue').removeClass('d-none');

    /* DataTable */
    var _overdueOnly = false;
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
      if (settings.nTable.id !== 'dt_Pipeline') return true;
      if (_overdueOnly) {
        var rowNode = settings.aoData[dataIndex].nTr;
        if ($(rowNode).data('overdue-close') !== 1) return false;
      }
      return true;
    });

    var dtPipeline = null;
    if ($('#dt_Pipeline').length) {
      dtPipeline = $('#dt_Pipeline').DataTable({
        data: rows,
        searching: true, pageLength: 10, lengthChange: false, select: false, info: true, paging: true,
        order: [[3, 'asc']],
        language: {
          search:'', searchPlaceholder:'Search deals',
          paginate: { previous:"<i class='fi fi-rr-angle-left'></i>", next:"<i class='fi fi-rr-angle-right'></i>" }
        },
        columns: [
          {
            data: null, className:'dt-body-center',
            render: function (v, t, row) {
              if (t !== 'display') return row.name;
              return '<div class="fw-semibold">' + row.name + '</div><div class="text-muted small">' + (row.account_name || '—') + '</div>';
            }
          },
          { data:'stage', className:'dt-body-center', render: function (v, t) { return t === 'display' ? (stageBadge[v] || v) : v; } },
          { data:'amount', className:'dt-body-center', render: function (v, t) { return t !== 'display' ? v : '<span class="fw-semibold">' + pkr(v) + '</span>'; } },
          {
            data:'close_date', className:'dt-body-center',
            render: function (v, t, row) {
              if (t === 'sort' || t === 'type') return v;
              return '<span class="' + (isOverdueClose(row) ? 'text-danger fw-semibold' : '') + '">' + fmtDate(v) + '</span>';
            }
          },
          { data:'forecast_category', className:'dt-body-center', render: function (v, t) { return t === 'display' ? (forecastBadge[v] || v) : v; } },
          { data:'owner_id', className:'dt-body-center', render: function (v, t) { return t === 'display' ? (userMap[v] || v) : v; } },
          {
            data: null, className:'dt-body-center', orderable: false,
            render: function (v, t, row) {
              if (t !== 'display') return '';
              return '<div class="btn-group">' +
                '<button class="btn btn-subtle-success btn-sm btn-shadow btn-icon" data-action="advance" data-opp-id="' + row.opportunity_id + '" title="Advance Stage"><i class="fi fi-rr-arrow-circle-right"></i></button>' +
                '<button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown"><i class="fi fi-rr-menu-dots"></i></button>' +
                '<ul class="dropdown-menu dropdown-menu-end">' +
                '<li><a class="dropdown-item" href="javascript:void(0);" data-action="detail" data-opp-id="' + row.opportunity_id + '"><i class="fi fi-rr-expand me-2 text-primary"></i>Open Detail</a></li>' +
                '<li><a class="dropdown-item" href="javascript:void(0);" data-action="won" data-opp-id="' + row.opportunity_id + '"><i class="fi fi-rr-badge-check me-2 text-success"></i>Mark Won</a></li>' +
                '<li><a class="dropdown-item" href="javascript:void(0);" data-action="lost" data-opp-id="' + row.opportunity_id + '"><i class="fi fi-rr-circle-xmark me-2 text-danger"></i>Mark Lost</a></li>' +
                '</ul></div>';
            }
          }
        ],
        createdRow: function (row, data) {
          if (isOverdueClose(data)) $(row).attr('data-overdue-close', 1);
          $(row).attr('data-opp-id', data.opportunity_id).css('cursor', 'pointer');
        },
        initComplete: function () {
          var dtSearch = $('#dt_Pipeline_wrapper .dt-search').detach();
          $('#dt_Pipeline_Search').append(dtSearch);
          $('#dt_Pipeline_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
          $('#dt_Pipeline_Search .dt-search label').remove();
          $('#dt_Pipeline_wrapper > .row.mt-2.justify-content-between').first().remove();
        }
      });
    }

    /* Stage filter */
    $('#pipeline-filter-stage button').on('click', function () {
      $('#pipeline-filter-stage button').removeClass('active');
      $(this).addClass('active');
      if (dtPipeline) dtPipeline.column(1).search($(this).data('filter')).draw();
    });

    /* Forecast filter */
    $('#pipeline-filter-forecast button').on('click', function () {
      $('#pipeline-filter-forecast button').removeClass('active');
      $(this).addClass('active');
      if (dtPipeline) dtPipeline.column(4).search($(this).data('filter')).draw();
    });

    /* Overdue toggle */
    function toggleOverdueFilter() {
      _overdueOnly = !_overdueOnly;
      $('#pipeline-filter-overdue').toggleClass('btn-warning btn-outline-warning');
      if (dtPipeline) dtPipeline.draw();
    }
    $('#pipeline-filter-overdue, #show-overdue-deals').on('click', toggleOverdueFilter);

    /* Kanban */
    var stageOrder  = ['qualification','discovery','proposal','negotiation','closed_won','closed_lost'];
    var stageLabel  = { qualification:'Qualification', discovery:'Discovery', proposal:'Proposal', negotiation:'Negotiation', closed_won:'Closed Won', closed_lost:'Closed Lost' };
    var stageBorder = { qualification:'border-info', discovery:'border-primary', proposal:'border-warning', negotiation:'border-danger', closed_won:'border-success', closed_lost:'border-secondary' };
    var stageHead   = { qualification:'bg-info-subtle text-info', discovery:'bg-primary-subtle text-primary', proposal:'bg-warning-subtle text-warning', negotiation:'bg-danger-subtle text-danger', closed_won:'bg-success-subtle text-success', closed_lost:'bg-secondary-subtle text-secondary' };

    function renderKanban() {
      var grouped = {};
      stageOrder.forEach(function (s) { grouped[s] = []; });
      rows.forEach(function (r) { if (grouped[r.stage]) grouped[r.stage].push(r); });
      var html = stageOrder.map(function (stage) {
        var deals = grouped[stage];
        var cards = deals.map(function (r) {
          var overdue = isOverdueClose(r);
          return '<div class="card card-body p-2 mb-2 shadow-sm border-start border-3 ' + stageBorder[stage] + ' kanban-card" data-opp-id="' + r.opportunity_id + '" style="cursor:pointer;">' +
            '<div class="fw-semibold small mb-1 text-truncate">' + r.name + '</div>' +
            '<div class="text-muted" style="font-size:.7rem;">' + (r.account_name || '—') + '</div>' +
            '<div class="d-flex justify-content-between align-items-center mt-2">' +
            '<span class="small fw-semibold text-primary">' + pkr(r.amount) + '</span>' +
            '<span class="badge ' + (overdue ? 'bg-danger-subtle text-danger' : 'bg-light text-muted') + '" style="font-size:.65rem;">' + fmtDate(r.close_date).replace(', 2026', '') + '</span>' +
            '</div></div>';
        }).join('');
        return '<div class="flex-shrink-0" style="width:185px;">' +
          '<div class="rounded-3 px-2 py-2 mb-2 d-flex justify-content-between align-items-center ' + stageHead[stage] + '">' +
          '<strong class="small">' + stageLabel[stage].toUpperCase() + '</strong>' +
          '<span class="badge bg-white bg-opacity-75 text-dark ms-1">' + deals.length + '</span>' +
          '</div>' + (cards || '<div class="text-muted small text-center py-3 rounded-3 bg-light">No deals</div>') + '</div>';
      }).join('');
      $('#kanban-board').html(html);
    }

    /* View toggle */
    var _kanbanActive = false;
    $('#btn-toggle-view').on('click', function () {
      _kanbanActive = !_kanbanActive;
      if (_kanbanActive) {
        $('#pipeline-list-view').addClass('d-none');
        $('#pipeline-kanban-view').removeClass('d-none');
        $(this).html('<i class="fi fi-rr-table me-1"></i> List');
        renderKanban();
      } else {
        $('#pipeline-list-view').removeClass('d-none');
        $('#pipeline-kanban-view').addClass('d-none');
        $(this).html('<i class="fi fi-rr-layout-kanban me-1"></i> Kanban');
      }
    });

    /* Deal detail pane */
    var actIcons = { call:'fi-rr-phone-call', email:'fi-rr-envelope', whatsapp:'fi-rr-whatsapp', meeting:'fi-rr-users-alt', note:'fi-rr-note', stage_change:'fi-rr-exchange', deal_won:'fi-rr-badge-check' };

    function openDealPane(oppId) {
      var opp = rows.filter(function (r) { return r.opportunity_id === oppId; })[0];
      if (!opp) return;
      $('#deal-pane-name').text(opp.name);
      $('#deal-pane-stage-badge').html(stageBadge[opp.stage] || opp.stage);
      $('#deal-pane-account').text(opp.account_name || '—');
      $('#deal-pane-close-date').text(fmtDate(opp.close_date));
      $('#deal-pane-amount').text(pkr(opp.amount));

      var detailHtml =
        '<div class="col-6"><small class="text-muted">Stage</small><div class="mt-1">' + (stageBadge[opp.stage] || opp.stage) + '</div></div>' +
        '<div class="col-6"><small class="text-muted">Forecast</small><div class="mt-1">' + (forecastBadge[opp.forecast_category] || opp.forecast_category) + '</div></div>' +
        '<div class="col-6"><small class="text-muted">Amount</small><div class="fw-semibold text-primary mt-1">' + pkr(opp.amount) + '</div></div>' +
        '<div class="col-6"><small class="text-muted">Probability</small><div class="fw-semibold mt-1">' + (opp.probability || 0) + '%</div></div>' +
        '<div class="col-6"><small class="text-muted">Close Date</small><div class="fw-semibold mt-1 ' + (isOverdueClose(opp) ? 'text-danger' : '') + '">' + fmtDate(opp.close_date) + '</div></div>' +
        '<div class="col-6"><small class="text-muted">Owner</small><div class="fw-semibold mt-1">' + (userMap[opp.owner_id] || opp.owner_id) + '</div></div>' +
        '<div class="col-12"><small class="text-muted">Account</small><div class="fw-semibold mt-1">' + (opp.account_name || '—') + '</div></div>';
      $('#deal-details-body').html(detailHtml);

      var oppActs = acts.filter(function (a) { return a.entity_id === opp.opportunity_id; });
      var actHtml = oppActs.length ? oppActs.map(function (a) {
        var icon = actIcons[a.activity_type] || 'fi-rr-dot-circle';
        return '<li class="list-group-item px-0 py-2"><div class="d-flex gap-2 align-items-start">' +
          '<i class="fi ' + icon + ' text-primary mt-1 flex-shrink-0"></i>' +
          '<div><div class="small fw-semibold">' + a.description + '</div>' +
          '<div class="text-muted" style="font-size:.7rem;">' + fmtDate(a.occurred_at.substring(0, 10)) + '</div></div></div></li>';
      }).join('') : '<li class="list-group-item text-muted small px-0 py-2">No activity logged</li>';
      $('#deal-activity-list').html(actHtml);

      var oppTaskItems = tasks.filter(function (t) { return t.entity_id === opp.opportunity_id; });
      var taskHtmlPane = oppTaskItems.length ? oppTaskItems.map(function (t) {
        var cls = { hot:'danger', warm:'warning', cold:'secondary' }[t.priority] || 'secondary';
        return '<li class="list-group-item px-0 py-2">' +
          '<div class="d-flex justify-content-between align-items-start gap-2">' +
          '<div class="small fw-semibold flex-grow-1' + (t.status === 'completed' ? ' text-decoration-line-through text-muted' : '') + '">' + t.title + '</div>' +
          '<span class="badge bg-' + cls + '-subtle text-' + cls + ' flex-shrink-0">' + (t.priority || '—') + '</span></div>' +
          '<div class="text-muted mt-1" style="font-size:.7rem;">' + fmtDate(t.due_at.substring(0, 10)) + ' · ' + t.status + '</div></li>';
      }).join('') : '<li class="list-group-item text-muted small px-0 py-2">No tasks for this deal</li>';
      $('#deal-task-list').html(taskHtmlPane);

      $('#cockpit-pipeline-col').removeClass('col-xxl-9').addClass('col-xxl-5');
      $('#cockpit-deal-pane').removeClass('d-none');
      var detailsTabEl = document.getElementById('deal-details-tab');
      if (detailsTabEl && window.bootstrap) bootstrap.Tab.getOrCreateInstance(detailsTabEl).show();
    }

    function closeDealPane() {
      $('#cockpit-deal-pane').addClass('d-none');
      $('#cockpit-pipeline-col').removeClass('col-xxl-5').addClass('col-xxl-9');
    }

    $('#dt_Pipeline tbody')
      .on('click', '.btn-group button, [data-action]', function (e) {
        e.stopPropagation();
        var action = $(this).data('action');
        var oppId  = $(this).data('opp-id');
        if (action === 'detail') openDealPane(oppId);
      })
      .on('click', 'tr', function () {
        var oppId = $(this).data('opp-id');
        if (oppId) openDealPane(oppId);
      });

    $(document).on('click', '.kanban-card', function () { openDealPane($(this).data('opp-id')); });
    $('#close-deal-pane').on('click', closeDealPane);
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.opportunities.list({ limit: 200 }),
      window.CRM_API.tasks.list({ limit: 200 }),
      window.CRM_API.activities.list({ limit: 500 })
    ]).then(function (results) {
      render(results[0].data || [], results[1].data || [], results[2].data || []);
    }).catch(function () {
      render(
        (_d && _d.opportunities && _d.opportunities.data) || [],
        (_d && _d.tasks && _d.tasks.data) || [],
        (_d && _d.activities && _d.activities.data) || []
      );
    });
  } else {
    if (!_d) return;
    render(_d.opportunities.data, _d.tasks.data, _d.activities.data);
  }

})();
