/* Pakistan CRM — Compliance Settings (G-08) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;

  function render(settings) {
    var rp = settings.retention_policies || {};
    var bg = settings.break_glass        || {};

    /* Retention policy fields */
    var fields = {
      'ret-financial':    (rp.financial    && rp.financial.years)    || 7,
      'ret-crm-activity': (rp.crm_activity && rp.crm_activity.years) || 3,
      'ret-audit':        (rp.audit_log    && rp.audit_log.years)    || 7,
      'ret-messages':     (rp.messages     && rp.messages.years)     || 2,
      'bg-two-approvers': bg.require_two_approvers !== false,
      'bg-ttl-hours':     bg.ttl_hours                               || 4,
      'bg-post-review':   bg.post_review_window_hours                || 24,
      'mode-gdpr':        !!settings.gdpr_mode,
      'mode-pdpa':        settings.pdpa_mode !== false,
    };

    Object.keys(fields).forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) return;
      if (el.type === 'checkbox') el.checked = !!fields[id];
      else el.value = fields[id];
    });
  }

  /* Save */
  var saveBtn = document.getElementById('btn-save-compliance');
  if (saveBtn) {
    saveBtn.addEventListener('click', function () {
      var $btn = $(this);
      $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span> Saving…');

      var payload = {
        retention_policies: {
          financial:    { years: parseInt($('#ret-financial').val())    || 7 },
          crm_activity: { years: parseInt($('#ret-crm-activity').val()) || 3 },
          audit_log:    { years: parseInt($('#ret-audit').val())        || 7 },
          messages:     { years: parseInt($('#ret-messages').val())     || 2 },
        },
        break_glass: {
          require_two_approvers: !!$('#bg-two-approvers').prop('checked'),
          ttl_hours:             parseInt($('#bg-ttl-hours').val()) || 4,
          post_review_window_hours: parseInt($('#bg-post-review').val()) || 24,
        },
        gdpr_mode: !!$('#mode-gdpr').prop('checked'),
        pdpa_mode: !!$('#mode-pdpa').prop('checked'),
      };

      function onDone() {
        $btn.prop('disabled', false).html('<i class="fi fi-rr-check me-1"></i> Saved').addClass('btn-success').removeClass('btn-primary');
        setTimeout(function () { $btn.html('Save Settings').addClass('btn-primary').removeClass('btn-success'); }, 2000);
      }
      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.complianceSettings.update(payload).then(onDone).catch(function () { $btn.prop('disabled', false).html('Save Settings'); });
      } else {
        setTimeout(onDone, 400);
      }
    });
  }

  /* Load */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.complianceSettings.get()
      .then(function (res) { render(res.data || {}); })
      .catch(function () { render({}); });
  } else {
    render({});
  }

})();
