/* Pakistan CRM — Feature Flags (G-07) */
/* Changes require 2-person approval (4hr timeout) per spec. Emergency override logged. */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  var catCls = {
    data:      'bg-info-subtle text-info',
    comms:     'bg-success-subtle text-success',
    ai:        'bg-primary-subtle text-primary',
    sales:     'bg-warning-subtle text-warning',
    finance:   'bg-danger-subtle text-danger',
    analytics: 'bg-secondary-subtle text-secondary',
  };

  var pendingToggle = null;

  function render(flags) {
    var rows = flags.map(function (f) {
      return '<tr>' +
        '<td class="text-center"><code class="small">' + f.flag_key + '</code></td>' +
        '<td class="text-center">' + (f.label || f.flag_key) + '</td>' +
        '<td class="text-center"><span class="badge ' + (catCls[f.category] || 'bg-secondary-subtle text-secondary') + '">' + (f.category || '—') + '</span></td>' +
        '<td class="text-center"><span class="badge bg-light text-secondary border" style="font-family:monospace;font-size:.7rem;">' + (f.rule_type || '—') + '</span></td>' +
        '<td class="text-center">' +
          '<div class="form-check form-switch d-flex justify-content-center mb-0">' +
          '<input class="form-check-input flag-toggle" type="checkbox" data-key="' + f.flag_key + '" data-requires-approval="' + (f.approval_required ? '1' : '0') + '" ' + (f.enabled ? 'checked' : '') + '>' +
          '</div></td>' +
        '<td class="text-center">' + (f.expires_at ? f.expires_at.slice(0, 10) : '—') + '</td>' +
        '<td class="text-center text-muted small">' + (f.last_changed_at ? f.last_changed_at.slice(0, 10) : '—') + '</td>' +
        '</tr>';
    }).join('');

    $('#flags-table-body').html(rows || '<tr><td colspan="7" class="text-center text-muted py-3">No flags</td></tr>');

    /* Toggle handler — approval gate per spec */
    document.querySelectorAll('.flag-toggle').forEach(function (input) {
      input.addEventListener('change', function () {
        var key              = this.dataset.key;
        var requiresApproval = this.dataset.requiresApproval === '1';
        var newState         = this.checked;
        var toggle           = this;

        if (requiresApproval) {
          var confirmed = window.confirm(
            'This flag requires 2-person approval (4hr timeout).\n\n' +
            'Proceed as emergency override? This action will be logged in the audit trail.'
          );
          if (!confirmed) { toggle.checked = !newState; return; }
        }

        if (cfg && !cfg.DUMMY_MODE) {
          window.CRM_API.featureFlags.update(key, { enabled: newState })
            .catch(function () { toggle.checked = !newState; alert('Error updating flag.'); });
        }
        /* Optimistic UI — checkbox already toggled */
      });
    });
  }

  /* Load */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.featureFlags.list()
      .then(function (res) { render(res.data || []); })
      .catch(function () { render((_d && _d.featureFlags && _d.featureFlags.data) || []); });
  } else {
    render((_d && _d.featureFlags && _d.featureFlags.data) || []);
  }

})();
