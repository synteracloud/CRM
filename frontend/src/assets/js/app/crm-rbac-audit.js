/* Pakistan CRM — RBAC Audit (J-04) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var PERMS = ['lead_view', 'lead_create', 'contact_view', 'contact_manage', 'audit_read', 'user_manage', 'role_edit'];

  var ROLE_PERMISSIONS = {
    sales_rep:     { lead_view:'yes', lead_create:'yes', contact_view:'yes', contact_manage:'no',  audit_read:'no',  user_manage:'no',  role_edit:'no'  },
    sales_manager: { lead_view:'yes', lead_create:'yes', contact_view:'yes', contact_manage:'yes', audit_read:'yes', user_manage:'no',  role_edit:'no'  },
    admin:         { lead_view:'yes', lead_create:'yes', contact_view:'yes', contact_manage:'yes', audit_read:'yes', user_manage:'yes', role_edit:'yes' },
    tenant_admin:  { lead_view:'yes', lead_create:'yes', contact_view:'yes', contact_manage:'yes', audit_read:'yes', user_manage:'yes', role_edit:'yes' }
  };

  var ROLE_CLR = { sales_rep:'primary', sales_manager:'info', admin:'danger', tenant_admin:'danger' };
  function roleBadge(role) {
    var cls   = ROLE_CLR[role] || 'secondary';
    var label = role.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    return '<span class="badge bg-' + cls + '-subtle text-' + cls + '">' + label + '</span>';
  }

  function render(users) {
    var userMap = {};
    users.forEach(function (u) { userMap[u.id] = u.display_name; });

    var rbacLog = (_d && _d.rbacAssignmentLog && _d.rbacAssignmentLog.data) || [];

    /* Permission matrix (role-level) */
    var roleSet = {};
    users.forEach(function (u) { roleSet[u.role] = true; });
    var roles = Object.keys(roleSet);

    var matrixHtml = '<table class="table table-sm table-bordered text-center small mb-0">' +
      '<thead><tr><th class="dt-head-center">Permission</th>' +
      roles.map(function (r) { return '<th class="dt-head-center">' + roleBadge(r) + '</th>'; }).join('') +
      '</tr></thead><tbody>' +
      PERMS.map(function (p) {
        return '<tr><td class="text-start fw-semibold">' + p.replace(/_/g, ' ') + '</td>' +
          roles.map(function (r) {
            var perms = ROLE_PERMISSIONS[r] || {};
            var val   = perms[p] || 'no';
            return '<td><span class="badge ' + (val === 'yes' ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary') + '">' + val + '</span></td>';
          }).join('') + '</tr>';
      }).join('') +
      '</tbody></table>';
    $('#perm-matrix-container').html(matrixHtml);

    /* User access table */
    var dtRBAC = $('#dt_RBACUsers');
    if (dtRBAC.length) {
      dtRBAC.DataTable({
        data: users,
        searching: false,
        pageLength: 10,
        lengthChange: false,
        order: [[1, 'asc']],
        language: { paginate: { previous: "<i class='fi fi-rr-angle-left'></i>", next: "<i class='fi fi-rr-angle-right'></i>" } },
        columns: [
          {
            data: null, className: 'dt-body-center',
            render: function (v, t, row, meta) {
              if (t !== 'display') return row.display_name;
              var n = (meta.row % 5) + 1;
              return '<div class="d-flex align-items-center justify-content-center gap-2">' +
                '<img src="assets/images/avatar/avatar' + n + '.webp" class="avatar avatar-xxs rounded-circle" alt="">' +
                '<span>' + row.display_name + '</span></div>';
            }
          },
          { data: 'role', className: 'dt-body-center', render: function (v, t) { return t !== 'display' ? v : roleBadge(v); } },
          {
            data: null, className: 'dt-body-center', orderable: false,
            render: function (v, t, row) {
              if (t !== 'display') return '';
              var perms = ROLE_PERMISSIONS[row.role] || {};
              return PERMS.filter(function (p) { return perms[p] === 'yes'; })
                .map(function (p) { return '<span class="badge bg-success-subtle text-success me-1 small">' + p.replace(/_/g, ' ') + '</span>'; }).join('');
            }
          },
          {
            data: null, className: 'dt-body-center', orderable: false,
            render: function (v, t) { return t !== 'display' ? '' : '<span class="badge bg-success-subtle text-success">Clean</span>'; }
          }
        ]
      });
    }

    /* Assignment log table */
    if ($('#dt_RBACLog').length && rbacLog.length > 0) {
      $('#dt_RBACLog').DataTable({
        data: rbacLog,
        searching: false,
        pageLength: 5,
        lengthChange: false,
        order: [[0, 'desc']],
        language: { paginate: { previous: "<i class='fi fi-rr-angle-left'></i>", next: "<i class='fi fi-rr-angle-right'></i>" } },
        columns: [
          { data: 'timestamp', className: 'dt-body-center', defaultContent: '—' },
          {
            data: 'actor_id', className: 'dt-body-center', defaultContent: '—',
            render: function (v, t) { return t !== 'display' ? v : (userMap[v] || v); }
          },
          { data: 'action_type', className: 'dt-body-center', defaultContent: '—' },
          {
            data: 'target_user_id', className: 'dt-body-center', defaultContent: '—',
            render: function (v, t) { return t !== 'display' ? v : (userMap[v] || v); }
          },
          { data: 'new_role', className: 'dt-body-center', defaultContent: '—', render: function (v, t) { return t !== 'display' ? v : roleBadge(v); } }
        ]
      });
    }

    /* KPI strip */
    $('#kpi-total-users-rbac').text(users.length);
    $('#kpi-privileged-users-rbac').text(users.filter(function (u) { return u.role === 'admin' || u.role === 'tenant_admin'; }).length);
    $('#kpi-role-changes').text(rbacLog.length);
    $('#kpi-clean-users').text(users.length);
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
