/* Pakistan CRM — User Management Admin (G-02) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  /* ── Config ────────────────────────────────────────────────────────── */
  var roleCfg = {
    sales_rep:     { label:'Sales Rep',     cls:'bg-info-subtle text-info'          },
    sales_manager: { label:'Sales Manager', cls:'bg-warning-subtle text-warning'    },
    finance:       { label:'Finance',       cls:'bg-success-subtle text-success'    },
    admin:         { label:'Admin',         cls:'bg-danger-subtle text-danger'      },
    tenant_admin:  { label:'Tenant Admin',  cls:'bg-danger-subtle text-danger'      }
  };
  var statusCfg = {
    active:    { label:'Active',    cls:'bg-success-subtle text-success'     },
    inactive:  { label:'Inactive',  cls:'bg-secondary-subtle text-secondary' },
    suspended: { label:'Suspended', cls:'bg-danger-subtle text-danger'       }
  };

  function roleBadge(role) {
    var c = roleCfg[role] || { label:role, cls:'bg-secondary-subtle text-secondary' };
    return '<span class="badge ' + c.cls + '">' + c.label + '</span>';
  }
  function statusBadge(status) {
    var c = statusCfg[status] || { label:status, cls:'bg-secondary-subtle text-secondary' };
    return '<span class="badge ' + c.cls + '">' + c.label + '</span>';
  }
  function nameHtml(user, idx) {
    var n = (idx % 5) + 1;
    return '<div class="d-flex align-items-center justify-content-center gap-2">' +
      '<div class="avatar avatar-xxs rounded-circle">' +
      '<img src="assets/images/avatar/avatar' + n + '.webp" alt=""></div>' +
      '<div><div class="fw-semibold">' + user.display_name + '</div>' +
      '<div class="text-muted small">' + user.email + '</div></div></div>';
  }
  function actionHtml(user) {
    return '<div class="btn-group">' +
      '<button class="btn btn-subtle-primary btn-sm btn-shadow btn-icon dropdown-toggle" data-bs-toggle="dropdown">' +
      '<i class="fi fi-rr-menu-dots"></i></button>' +
      '<ul class="dropdown-menu dropdown-menu-end">' +
      '<li><a class="dropdown-item btn-edit-role" href="javascript:void(0);" data-uid="' + user.id + '" data-name="' + user.display_name + '" data-role="' + user.role + '">' +
      '<i class="fi fi-rr-shield-check me-2 text-primary"></i>Edit Role</a></li>' +
      '<li><a class="dropdown-item btn-suspend" href="javascript:void(0);" data-uid="' + user.id + '" data-name="' + user.display_name + '">' +
      '<i class="fi fi-rr-ban me-2 text-warning"></i>Suspend</a></li>' +
      '<li><a class="dropdown-item btn-reset-pw" href="javascript:void(0);" data-uid="' + user.id + '" data-name="' + user.display_name + '">' +
      '<i class="fi fi-rr-lock me-2 text-danger"></i>Reset Password</a></li>' +
      '</ul></div>';
  }

  /* ── Render ────────────────────────────────────────────────────────── */
  function render(users) {
    if (!$('#dt_UserManagement').length) return;

    var ADMIN_ROLES = ['tenant_admin', 'admin'];
    var statusStub = {};
    var loginStub  = {};
    var joinedStub = {};
    users.forEach(function (u, i) {
      statusStub[u.id] = 'active';
      var days = [0, 2, 1, 4, 7, 3, 5, 1, 6, 2];
      loginStub[u.id]  = days[i % days.length] === 0 ? 'Today' : days[i % days.length] + ' days ago';
      joinedStub[u.id] = u.created_at ? u.created_at.substring(0, 10) : '2026-01-01';
    });

    /* KPI strip */
    var adminCount  = users.filter(function (u) { return ADMIN_ROLES.indexOf(u.role) !== -1; }).length;
    var repCount    = users.filter(function (u) { return u.role === 'sales_rep'; }).length;
    var mgrCount    = users.filter(function (u) { return u.role === 'sales_manager'; }).length;
    $('#kpi-total-users-mgmt').text(users.length);
    $('#kpi-admin-count').text(adminCount);
    $('#kpi-rep-count').text(repCount);
    $('#kpi-manager-count').text(mgrCount);

    /* Invite select */
    var $roleSelect = $('#invite-role-select');
    if ($roleSelect.length && $roleSelect.children().length <= 1) {
      Object.keys(roleCfg).forEach(function (r) {
        $roleSelect.append('<option value="' + r + '">' + roleCfg[r].label + '</option>');
      });
    }

    var _roleFilter = '';
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
      if (settings.nTable.id !== 'dt_UserManagement') return true;
      var $row = $(settings.aoData[dataIndex].nTr);
      if (_roleFilter && $row.data('role') !== _roleFilter) return false;
      return true;
    });

    var dtUM = $('#dt_UserManagement').DataTable({
      data: users,
      searching: true,
      pageLength: 10,
      lengthChange: false,
      order: [[1, 'asc']],
      language: {
        search: '',
        searchPlaceholder: 'Search users…',
        paginate: { previous: "<i class='fi fi-rr-angle-left'></i>", next: "<i class='fi fi-rr-angle-right'></i>" }
      },
      columns: [
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type, row, meta) { return type !== 'display' ? '' : nameHtml(row, meta.row); }
        },
        { data: 'role', className: 'dt-body-center', render: function (v, t) { return t !== 'display' ? v : roleBadge(v); } },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type, row) { return type !== 'display' ? '' : statusBadge(statusStub[row.id] || 'active'); }
        },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type, row) { return type !== 'display' ? '' : (loginStub[row.id] || '—'); }
        },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type, row) { return type !== 'display' ? '' : (joinedStub[row.id] || '—'); }
        },
        {
          data: null, className: 'dt-body-center', orderable: false,
          render: function (val, type, row) { return type !== 'display' ? '' : actionHtml(row); }
        }
      ],
      createdRow: function (row, data) {
        $(row).attr('data-role', data.role || '');
      },
      initComplete: function () {
        var dtSearch = $('#dt_UserManagement_wrapper .dt-search').detach();
        $('#dt_UserManagement_Search').append(dtSearch);
        $('#dt_UserManagement_Search .dt-search').prepend('<i class="fi fi-rr-search"></i>');
        $('#dt_UserManagement_Search .dt-search label').remove();
        $('#dt_UserManagement_wrapper > .row.mt-2.justify-content-between').first().remove();
      }
    });

    $('#um-filter-role button').on('click', function () {
      $('#um-filter-role button').removeClass('active');
      $(this).addClass('active');
      _roleFilter = $(this).data('filter');
      dtUM.draw();
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
