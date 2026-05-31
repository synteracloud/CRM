/* Pakistan CRM — Role & Permission Editor (G-03) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function render(roles) {
    var rows = roles.map(function (r) {
      var canDelete = !r.is_system && r.active_user_count === 0;
      return '<tr>' +
        '<td class="text-center fw-semibold">' + (r.label || r.name) + '</td>' +
        '<td class="text-center"><code class="small">' + r.name + '</code></td>' +
        '<td class="text-center">' + (r.active_user_count || 0) + '</td>' +
        '<td class="text-center"><span class="badge bg-info-subtle text-info">' + (r.permissions && r.permissions[0] === '*' ? 'All' : (r.permissions ? r.permissions.length : 0)) + ' permissions</span></td>' +
        '<td class="text-center">' + (r.is_system ? '<span class="badge bg-secondary-subtle text-secondary">System</span>' : '<span class="badge bg-primary-subtle text-primary">Custom</span>') + '</td>' +
        '<td class="text-center">' +
          '<button class="btn btn-xs btn-outline-primary btn-sm me-1 waves-effect btn-edit-role" data-id="' + r.role_id + '">Edit</button>' +
          (canDelete ? '<button class="btn btn-xs btn-outline-danger btn-sm waves-effect btn-del-role" data-id="' + r.role_id + '">Delete</button>' : '') +
        '</td></tr>';
    }).join('');
    $('#roles-body').html(rows || '<tr><td colspan="6" class="text-center text-muted py-3">No roles</td></tr>');

    /* Permissions list */
    var allPerms = [];
    roles.forEach(function (r) {
      (r.permissions || []).forEach(function (p) {
        if (p !== '*' && allPerms.indexOf(p) === -1) allPerms.push(p);
      });
    });
    allPerms.sort();
    $('#permissions-list').html(allPerms.map(function (p) {
      return '<span class="badge bg-light text-secondary border" style="font-family:monospace;font-size:.75rem;">' + p + '</span>';
    }).join(' '));

    /* Edit handler (inline prompt — full modal would be Phase 7 polish) */
    document.querySelectorAll('.btn-edit-role').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id    = this.dataset.id;
        var role  = roles.find(function (r) { return r.role_id === id; });
        if (!role) return;
        var newLabel = window.prompt('Role display label:', role.label || role.name);
        if (!newLabel) return;
        if (cfg && !cfg.DUMMY_MODE) {
          window.CRM_API.roles.update(id, { label: newLabel })
            .then(function () { location.reload(); })
            .catch(function (e) { alert('Error: ' + (e && e.error && e.error.message ? e.error.message : 'Save failed')); });
        } else {
          role.label = newLabel;
          render(roles);
        }
      });
    });
  }

  /* Load */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.roles.list()
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.roles && _d.roles.data) || []); });
  } else {
    render((_d && _d.roles && _d.roles.data) || []);
  }

})();
