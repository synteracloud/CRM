/* Pakistan CRM — Account List (B-04) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function pkr(n) {
    if (!n) return '—';
    n = Number(n);
    if (n >= 100000) return 'PKR ' + (n / 100000).toFixed(2) + ' L';
    return 'PKR ' + n.toLocaleString('en-IN');
  }

  var tierCfg = { 'Enterprise':'bg-danger-subtle text-danger', 'Mid-Market':'bg-warning-subtle text-warning', 'SMB':'bg-info-subtle text-info' };
  function tierBadge(t) { return '<span class="badge ' + (tierCfg[t] || 'bg-secondary-subtle text-secondary') + '">' + t + '</span>'; }
  function actionHtml(a) {
    return '<div class="btn-group"><button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown"><i class="fi fi-rr-menu-dots"></i></button>' +
      '<ul class="dropdown-menu dropdown-menu-end">' +
      '<li><a class="dropdown-item" href="app/accounts-detail.html?id=' + (a.account_id || '') + '"><i class="fi fi-rr-eye me-2 text-primary"></i>Open Profile</a></li>' +
      '<li><a class="dropdown-item" href="app/opportunity-new.html"><i class="fi fi-rr-chart-pie-alt me-2 text-success"></i>New Opportunity</a></li>' +
      '</ul></div>';
  }

  function render(accounts) {
    var total      = accounts.length;
    var enterprise = accounts.filter(function (a) { return a.tier === 'Enterprise'; }).length;
    var outstanding= accounts.reduce(function (s, a) { return s + (Number(a.outstanding_balance) || 0); }, 0);
    var openOpps   = accounts.reduce(function (s, a) { return s + (Number(a.open_opps) || 0); }, 0);
    $('#kpi-total-accounts').text(total);
    $('#kpi-enterprise').text(enterprise);
    $('#kpi-outstanding').text(pkr(outstanding));
    $('#kpi-open-opps').text(openOpps);

    if (!$('#dt_Accounts').length) return;

    var _tierFilter = '', _balFilter = '';
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
      if (settings.nTable.id !== 'dt_Accounts') return true;
      var $row = $(settings.aoData[dataIndex].nTr);
      if (_tierFilter && $row.data('tier') !== _tierFilter) return false;
      if (_balFilter === 'overdue' && !($row.data('balance') > 0)) return false;
      return true;
    });

    var dt = $('#dt_Accounts').DataTable({
      data: accounts.slice().sort(function (a, b) { return (a.name || '').localeCompare(b.name || ''); }),
      searching: true, pageLength: 10, lengthChange: false, order: [],
      language: { search:'', searchPlaceholder:'Search accounts…', paginate:{ previous:"<i class='fi fi-rr-angle-left'></i>", next:"<i class='fi fi-rr-angle-right'></i>" } },
      columns: [
        { data:'name',                className:'dt-body-center', render:function (v) { return '<span class="fw-semibold">' + v + '</span>'; } },
        { data:'tier',                className:'dt-body-center', render:function (v, t) { return t !== 'display' ? v : tierBadge(v || '—'); }, defaultContent:'—' },
        { data:'industry',            className:'dt-body-center', defaultContent:'—' },
        { data:'city',                className:'dt-body-center', defaultContent:'—' },
        { data:'open_opps',           className:'dt-body-center', render:function (v, t) { return t !== 'display' ? v : (v > 0 ? '<span class="badge bg-success-subtle text-success">' + v + '</span>' : '<span class="text-muted">—</span>'); }, defaultContent:'0' },
        { data:'outstanding_balance', className:'dt-body-center', render:function (v, t) { return t !== 'display' ? v : (v > 0 ? '<span class="text-danger fw-semibold">' + pkr(v) + '</span>' : '<span class="text-muted">—</span>'); }, defaultContent:'0' },
        { data:null, className:'dt-body-center', orderable:false, render:function (v, t, row) { return t !== 'display' ? '' : actionHtml(row); } }
      ],
      createdRow:function (row, data) {
        $(row).attr('data-tier', data.tier || '').attr('data-balance', data.outstanding_balance || 0);
      },
      initComplete:function () {
        var s = $('#dt_Accounts_wrapper .dt-search').detach();
        $('#dt_Accounts_Search').append(s);
        $('#dt_Accounts_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
        $('#dt_Accounts_Search .dt-search label').remove();
        $('#dt_Accounts_wrapper > .row.mt-2.justify-content-between').first().remove();
      }
    });
    $('#acc-filter-tier button').on('click', function () { $('#acc-filter-tier button').removeClass('active'); $(this).addClass('active'); _tierFilter = $(this).data('filter'); dt.draw(); });
    $('#acc-filter-balance button').on('click', function () { $('#acc-filter-balance button').removeClass('active'); $(this).addClass('active'); _balFilter = $(this).data('filter'); dt.draw(); });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.accounts.list({ limit: 200 })
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.accounts && _d.accounts.data) || []); });
  } else {
    if (!_d) return;
    render((_d.accounts && _d.accounts.data) || []);
  }

})();
