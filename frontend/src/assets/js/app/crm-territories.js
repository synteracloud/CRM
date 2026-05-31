/* Pakistan CRM — Territories (G-09) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var CRITERIA_BADGE = {
    geographic:      '<span class="badge bg-primary-subtle text-primary border border-primary-subtle">Geographic</span>',
    rep_assigned:    '<span class="badge bg-secondary-subtle text-secondary">Rep Assigned</span>',
    account_segment: '<span class="badge bg-info-subtle text-info border border-info-subtle">Account Segment</span>',
  };

  function render(territories, userMap) {
    var tbody = document.getElementById('territory-table-body');
    if (!tbody) return;

    tbody.addEventListener('click', function (e) {
      var btn = e.target.closest('.btn-edit-territory');
      if (!btn) return;
      var id   = btn.dataset.id;
      var name = window.prompt('New territory name:');
      if (!name) return;
      btn.disabled = true;
      window.CRM_API.territories.update(id, { name: name })
        .then(function () { location.reload(); })
        .catch(function () { btn.disabled = false; });
    });

    tbody.innerHTML = territories.map(function (t) {
      var manager = userMap[t.primary_manager] || { display_name: t.primary_manager || '—' };
      var reps = (t.assigned_reps || []).map(function (rid) { return (userMap[rid] || { display_name: rid }).display_name; }).join(', ');
      return '<tr>' +
        '<td class="text-center fw-semibold">' + t.name + '</td>' +
        '<td class="text-center">' + (CRITERIA_BADGE[t.criteria_type] || t.criteria_type || '—') + '</td>' +
        '<td class="text-center">' + manager.display_name + '</td>' +
        '<td class="text-center small">' + (reps || '—') + '</td>' +
        '<td class="text-center">' + (t.routing_priority || '—') + '</td>' +
        '<td class="text-center">' + (t.is_default ? '<span class="badge bg-success">Default</span>' : '—') + '</td>' +
        '<td class="text-center"><button class="btn btn-xs btn-outline-primary btn-edit-territory" data-id="' + t.territory_id + '">Edit</button></td></tr>';
    }).join('');
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      Promise.all([
        window.CRM_API.territories.list({ limit: 100 }),
        window.CRM_API.users.list()
      ]).then(function (results) {
        var terrs   = results[0].data || [];
        var users   = results[1].data || [];
        var userMap = {};
        users.forEach(function (u) { userMap[u.id] = u; });
        render(terrs, userMap);
      }).catch(function () {
        var terrs   = (_d && _d.territories && _d.territories.data) || [];
        var userMap = (_d && _d.userMap) || {};
        render(terrs, userMap);
      });
    } else {
      var terrs   = (_d && _d.territories && _d.territories.data) || [];
      var userMap = (_d && _d.userMap) || {};
      render(terrs, userMap);
    }
  });

})();
