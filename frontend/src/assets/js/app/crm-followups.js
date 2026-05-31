/* Pakistan CRM — Follow-up Queue Page Driver */

(function () {
  'use strict';

  var cfg   = window.CRM_CONFIG;
  var _d    = window.CRM_DUMMY;
  var today = new Date().toISOString().slice(0, 10);

  /* ── Module-level filter state (shared with ext.search) ──────────── */
  var _overdueActive = false;

  /* ── Badge/display helpers ────────────────────────────────────────── */
  var levelBadge = {
    none:       '<span class="badge bg-secondary-subtle text-secondary">None</span>',
    reminder:   '<span class="badge bg-success-subtle text-success">Reminder</span>',
    warning:    '<span class="badge bg-warning-subtle text-warning">Warning</span>',
    escalated:  '<span class="badge bg-danger-subtle text-danger">Escalated</span>',
    reassigned: '<span class="badge bg-dark-subtle text-dark">Reassigned</span>'
  };

  var actionBadge = {
    Call:     '<span class="badge bg-primary-subtle text-primary"><i class="fi fi-rr-phone-call me-1"></i>Call</span>',
    WhatsApp: '<span class="badge bg-success-subtle text-success"><i class="fi fi-brands-whatsapp me-1"></i>WhatsApp</span>',
    Reminder: '<span class="badge bg-info-subtle text-info"><i class="fi fi-rr-bell me-1"></i>Reminder</span>'
  };

  var statusBadge = {
    overdue:   '<span class="badge bg-danger-subtle text-danger">Overdue</span>',
    pending:   '<span class="badge bg-warning-subtle text-warning">Pending</span>',
    completed: '<span class="badge bg-success-subtle text-success">Completed</span>'
  };

  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  function fmtDate(iso) {
    if (!iso) return '—';
    var dt = new Date(iso);
    return MONTHS[dt.getMonth()] + ' ' + dt.getDate() + ', ' + dt.getFullYear();
  }

  var AVATARS = [1,2,3,4,5,6,7,8,9,10].map(function (n) {
    return 'assets/images/avatar/avatar' + n + '.webp';
  });

  function avatarImg(idx) {
    return '<div class="avatar avatar-xxs rounded-circle me-2"><img src="' + AVATARS[idx % AVATARS.length] + '" alt=""></div>';
  }

  /* ── Custom search extension (registered once at module level) ────── */
  $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
    if (settings.nTable.id !== 'dt_Followups') return true;
    if (!_overdueActive) return true;
    return $(settings.aoData[dataIndex].nTr).data('overdue') === 1;
  });

  /* ── Core render — works with live or dummy data ──────────────────── */
  function render(rows, leadNameMap) {
    leadNameMap = leadNameMap || {};

    /* KPI */
    var overdue   = rows.filter(function (r) { return r.state === 'overdue'; });
    var pending   = rows.filter(function (r) { return r.state === 'pending'; });
    var completed = rows.filter(function (r) {
      return r.state === 'completed' && r.due_at && r.due_at.startsWith(today);
    });
    var dueToday = pending.filter(function (r) { return r.due_at && r.due_at.startsWith(today); });

    $('#kpi-pending').text(pending.length);
    $('#kpi-overdue').text(overdue.length);
    $('#kpi-completed-today').text(completed.length);
    $('#kpi-due-today').text(dueToday.length);

    /* Enforcement strip */
    var overdueCount = overdue.length;
    if (overdueCount > 0) {
      $('#overdue-count').text(overdueCount);
      $('#overdue-plural').text(overdueCount === 1 ? ' is' : 's are');
      $('#enforcement-strip-row').removeClass('d-none');
    } else {
      $('#enforcement-strip-row').addClass('d-none');
    }

    if (!$('#dt_Followups').length) return;

    var dtFollowups = $('#dt_Followups').DataTable({
      data: rows,
      searching: true,
      pageLength: 10,
      select: false,
      lengthChange: false,
      info: true,
      paging: true,
      order: [[2, 'asc']],
      language: {
        search: '',
        searchPlaceholder: 'Search',
        paginate: {
          previous: "<i class='fi fi-rr-angle-left'></i>",
          next:     "<i class='fi fi-rr-angle-right'></i>",
          first:    "<i class='fi fi-rr-angle-double-left'></i>",
          last:     "<i class='fi fi-rr-angle-double-right'></i>"
        }
      },
      columns: [
        {
          data: 'lead_name',
          className: 'dt-body-left',
          orderable: false,
          render: function (val, type, row, meta) {
            var name = val || leadNameMap[row.lead_id] || row.lead_id || '—';
            if (type !== 'display') return name;
            return '<div class="d-flex align-items-center">' + avatarImg(meta.row) +
              '<div>' + name + '<div class="text-muted small">' + (row.rule_type || '').replace(/_/g, ' ') + '</div></div></div>';
          }
        },
        {
          data: 'action_type',
          className: 'dt-body-center',
          defaultContent: '—',
          render: function (val, type) {
            return type === 'display' ? (actionBadge[val] || val || '—') : (val || '');
          }
        },
        {
          data: 'due_at',
          className: 'dt-body-center',
          render: function (val, type, row) {
            if (type === 'sort' || type === 'type') return val;
            var cls = row.state === 'overdue' ? ' class="text-danger fw-semibold"' : '';
            return '<span' + cls + '>' + fmtDate(val) + '</span>';
          }
        },
        {
          data: 'escalation_level',
          className: 'dt-body-center',
          defaultContent: 'none',
          render: function (val, type) {
            return type === 'display' ? (levelBadge[val] || val || '—') : (val || '');
          }
        },
        { data: 'attempts_count', className: 'dt-body-center', defaultContent: '0' },
        {
          data: 'state',
          className: 'dt-body-center',
          render: function (val, type) {
            return type === 'display' ? (statusBadge[val] || val) : val;
          }
        },
        {
          data: null,
          className: 'dt-body-center',
          orderable: false,
          render: function (val, type, row) {
            if (type !== 'display') return '';
            return '<div class="btn-group"><button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown"><i class="fi fi-rr-menu-dots"></i></button>' +
              '<ul class="dropdown-menu dropdown-menu-end">' +
              '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-check-circle me-2 text-success"></i>Mark Complete</a></li>' +
              '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-snooze me-2 text-warning"></i>Snooze</a></li>' +
              '<li><a class="dropdown-item" href="javascript:void(0);"><i class="fi fi-rr-user-add me-2 text-primary"></i>Reassign</a></li>' +
              '</ul></div>';
          }
        }
      ],
      createdRow: function (row, data) {
        if (data.state === 'overdue') $(row).attr('data-overdue', 1);
      },
      initComplete: function () {
        var dtSearch = $('#dt_Followups_wrapper .dt-search').detach();
        $('#dt_Followups_Search').append(dtSearch);
        $('#dt_Followups_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
        $('#dt_Followups_Search .dt-search label').remove();
        $('#dt_Followups_wrapper > .row.mt-2.justify-content-between').first().remove();
      }
    });

    /* Filter chips */
    $('#filter-action-type button').on('click', function () {
      $('#filter-action-type button').removeClass('active');
      $(this).addClass('active');
      dtFollowups.column(1).search($(this).data('filter')).draw();
    });

    $('#filter-level button').on('click', function () {
      $('#filter-level button').removeClass('active');
      $(this).addClass('active');
      dtFollowups.column(3).search($(this).data('filter')).draw();
    });

    $('#filter-overdue').on('click', function () {
      _overdueActive = !_overdueActive;
      $(this).toggleClass('btn-danger btn-outline-danger');
      dtFollowups.draw();
    });

    $('#show-overdue-only').on('click', function () {
      if (!_overdueActive) {
        _overdueActive = true;
        $('#filter-overdue').removeClass('btn-outline-danger').addClass('btn-danger');
        dtFollowups.draw();
      }
    });
  }

  /* ── Load: live API or dummy fallback ─────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.followups.list({ limit: 200 }),
      window.CRM_API.leads.list({ limit: 200 })
    ])
    .then(function (results) {
      var followups = (results[0].data) || [];
      var leads     = (results[1].data) || [];
      var nameMap   = {};
      leads.forEach(function (l) { nameMap[l.lead_id] = l.contact_name; });
      render(followups, nameMap);
    })
    .catch(function () {
      render((_d && _d.followups && _d.followups.data) || [], {});
    });
  } else {
    if (!_d) return;
    render(_d.followups.data, {});
  }

})();
