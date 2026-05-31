/* Pakistan CRM — Org Settings (G-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;

  function render(settings) {
    /* Populate form fields */
    var fields = {
      'org-name':          settings.tenant_name   || '',
      'org-timezone':      settings.timezone        || 'Asia/Karachi',
      'org-date-format':   settings.date_format     || 'DD/MM/YYYY',
      'org-language':      settings.language_default|| 'en',
      'org-currency':      settings.base_currency   || 'PKR',
      'org-lakh-notation': settings.lakh_crore_notation,
      'org-biz-start':     (settings.business_hours && settings.business_hours.start) || '09:00',
      'org-biz-end':       (settings.business_hours && settings.business_hours.end)   || '19:00',
    };
    Object.keys(fields).forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) return;
      if (el.type === 'checkbox') el.checked = !!fields[id];
      else if (el.tagName === 'SELECT' || el.tagName === 'INPUT') el.value = fields[id] || '';
    });
  }

  /* Save handler */
  var saveBtn = document.getElementById('btn-save-org');
  if (saveBtn) {
    saveBtn.addEventListener('click', function () {
      var $btn = $(this);
      $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span> Saving…');

      var payload = {};
      ['org-name','org-timezone','org-date-format','org-language','org-currency'].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) {
          var key = { 'org-name':'tenant_name', 'org-timezone':'timezone', 'org-date-format':'date_format', 'org-language':'language_default', 'org-currency':'base_currency' }[id];
          payload[key] = el.value;
        }
      });
      var lakhEl = document.getElementById('org-lakh-notation');
      if (lakhEl) payload.lakh_crore_notation = lakhEl.checked;
      var startEl = document.getElementById('org-biz-start'), endEl = document.getElementById('org-biz-end');
      if (startEl && endEl) payload.business_hours = { start: startEl.value, end: endEl.value, timezone: 'Asia/Karachi', days: ['mon','tue','wed','thu','fri','sat'] };

      function onDone() {
        $btn.prop('disabled', false).html('<i class="fi fi-rr-check me-1"></i> Saved').addClass('btn-success').removeClass('btn-primary');
        setTimeout(function () { $btn.html('Save Changes').addClass('btn-primary').removeClass('btn-success'); }, 2000);
      }
      function onError() { $btn.prop('disabled', false).html('Save Changes'); alert('Error saving. Please try again.'); }

      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.orgSettings.update(payload).then(onDone).catch(onError);
      } else {
        setTimeout(onDone, 400);
      }
    });
  }

  /* Load */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.orgSettings.get()
      .then(function (res) { render(res.data || {}); })
      .catch(function () { render({}); });
  } else {
    render({});
  }

})();
