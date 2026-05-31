/* Pakistan CRM — User Directory (B-10) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var roleCfg = {
    sales_rep:     { label: 'Sales Rep',     cls: 'bg-info-subtle text-info'       },
    sales_manager: { label: 'Sales Manager', cls: 'bg-warning-subtle text-warning' },
    finance:       { label: 'Finance',       cls: 'bg-success-subtle text-success' },
    admin:         { label: 'Admin',         cls: 'bg-danger-subtle text-danger'   },
    tenant_admin:  { label: 'Tenant Admin',  cls: 'bg-danger-subtle text-danger'   }
  };
  var statusCfg = {
    active:    { label: 'Active',    cls: 'bg-success-subtle text-success'     },
    inactive:  { label: 'Inactive',  cls: 'bg-secondary-subtle text-secondary' },
    suspended: { label: 'Suspended', cls: 'bg-danger-subtle text-danger'       }
  };

  function roleBadge(role) {
    var c = roleCfg[role] || { label: role, cls: 'bg-secondary-subtle text-secondary' };
    return '<span class="badge ' + c.cls + '">' + c.label + '</span>';
  }
  function statusBadge(status) {
    var c = statusCfg[status] || { label: status, cls: 'bg-secondary-subtle text-secondary' };
    return '<span class="badge ' + c.cls + '">' + c.label + '</span>';
  }
  function nameHtml(user, rowIdx) {
    var n = (rowIdx % 5) + 1;
    return '<div class="d-flex align-items-center justify-content-center gap-2">' +
           '<div class="avatar avatar-xxs rounded-circle">' +
           '<img src="assets/images/avatar/avatar' + n + '.webp" alt=""></div>' +
           '<div><div>' + user.display_name + '</div>' +
           '<div class="text-muted small">' + user.email + '</div></div></div>';
  }
  function actionHtml() {
    return '<div class="btn-group">' +
      '<button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle"' +
      ' data-bs-toggle="dropdown"><i class="fi fi-rr-menu-dots"></i></button>' +
      '<ul class="dropdown-menu dropdown-menu-end">' +
      '<li><a class="dropdown-item" href="javascript:void(0);">' +
      '<i class="fi fi-rr-shield-check me-2 text-primary"></i>Edit Roles</a></li>' +
      '<li><a class="dropdown-item" href="javascript:void(0);">' +
      '<i class="fi fi-rr-ban me-2 text-warning"></i>Suspend</a></li>' +
      '<li><a class="dropdown-item" href="javascript:void(0);">' +
      '<i class="fi fi-rr-lock me-2 text-danger"></i>Reset Password</a></li>' +
      '</ul></div>';
  }

  function render(users) {
    if (!$('#dt_Users').length) return;

    var repCount   = users.filter(function (u) { return u.role === 'sales_rep'; }).length;
    var mgrCount   = users.filter(function (u) { return u.role === 'sales_manager'; }).length;
    var adminCount = users.filter(function (u) { return u.role === 'admin' || u.role === 'tenant_admin'; }).length;

    $('#kpi-total-users').text(users.length);
    $('#kpi-sales-reps').text(repCount);
    $('#kpi-managers').text(mgrCount);
    $('#kpi-active-users').text(users.length);

    var _roleFilter   = '';
    var _statusFilter = '';

    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
      if (settings.nTable.id !== 'dt_Users') return true;
      var $row = $(settings.aoData[dataIndex].nTr);
      if (_roleFilter   && $row.data('role')   !== _roleFilter)   return false;
      if (_statusFilter && $row.data('status') !== _statusFilter) return false;
      return true;
    });

    var dtUsers = $('#dt_Users').DataTable({
      data: users,
      searching: true,
      pageLength: 10,
      lengthChange: false,
      order: [[0, 'asc']],
      language: {
        search: '',
        searchPlaceholder: 'Search users…',
        paginate: { previous: "<i class='fi fi-rr-angle-left'></i>", next: "<i class='fi fi-rr-angle-right'></i>" }
      },
      columns: [
        {
          data: null, className: 'dt-body-center',
          render: function (val, type, row, meta) { return type !== 'display' ? row.display_name : nameHtml(row, meta.row); }
        },
        { data: 'role', className: 'dt-body-center', render: function (v, t) { return t !== 'display' ? v : roleBadge(v); } },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type) { return type !== 'display' ? '' : statusBadge('active'); }
        },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type) { return type !== 'display' ? '' : '—'; }
        },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type, row) { return type !== 'display' ? '' : actionHtml(row); }
        }
      ],
      createdRow: function (row, data) {
        $(row).attr('data-role', data.role || '').attr('data-status', 'active');
      },
      initComplete: function () {
        var dtSearch = $('#dt_Users_wrapper .dt-search').detach();
        $('#dt_Users_Search').append(dtSearch);
        $('#dt_Users_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
        $('#dt_Users_Search .dt-search label').remove();
        $('#dt_Users_wrapper > .row.mt-2.justify-content-between').first().remove();
      }
    });

    $('#users-filter-role button').on('click', function () {
      $('#users-filter-role button').removeClass('active');
      $(this).addClass('active');
      _roleFilter = $(this).data('filter');
      dtUsers.draw();
    });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.users.list()
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.users && _d.users.data) || []); });
  } else {
    if (!_d) return;
    render(_d.users.data || []);
  }

})();
