/* Pakistan CRM — Notification Settings (G-06) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;

  var DEFAULT_EVENTS = [
    { key:'new_lead',         label:'New lead created',    inapp:true,  email:true,  wa:false, sms:false },
    { key:'followup_overdue', label:'Follow-up overdue',   inapp:true,  email:true,  wa:true,  sms:false },
    { key:'lead_assigned',    label:'Lead assigned to me', inapp:true,  email:false, wa:false, sms:false },
    { key:'sla_breach',       label:'SLA breach',          inapp:true,  email:true,  wa:false, sms:false },
    { key:'payment_received', label:'Payment received',    inapp:true,  email:true,  wa:true,  sms:false },
    { key:'quote_approved',   label:'Quote approved',      inapp:true,  email:true,  wa:false, sms:false },
    { key:'deal_won',         label:'Deal won',            inapp:true,  email:true,  wa:false, sms:false },
    { key:'invoice_overdue',  label:'Invoice overdue',     inapp:true,  email:true,  wa:true,  sms:false },
  ];

  function toggle(id, checked) {
    return '<div class="form-check form-switch d-flex justify-content-center mb-0">' +
      '<input class="form-check-input" type="checkbox" id="' + id + '" ' + (checked ? 'checked' : '') + '></div>';
  }

  function renderEvents(prefs) {
    var eventsData = DEFAULT_EVENTS.map(function (e) {
      var live = prefs && prefs.events && prefs.events[e.key];
      return {
        key:   e.key,
        label: e.label,
        inapp: live ? !!live.in_app    : e.inapp,
        email: live ? !!live.email     : e.email,
        wa:    live ? !!live.whatsapp  : e.wa,
        sms:   live ? !!live.sms       : e.sms,
      };
    });

    var rows = eventsData.map(function (e) {
      return '<tr>' +
        '<td class="text-center">' + e.label + '</td>' +
        '<td class="text-center">' + toggle('t-inapp-'  + e.key, e.inapp) + '</td>' +
        '<td class="text-center">' + toggle('t-email-'  + e.key, e.email) + '</td>' +
        '<td class="text-center">' + toggle('t-wa-'     + e.key, e.wa)    + '</td>' +
        '<td class="text-center">' + toggle('t-sms-'    + e.key, e.sms)   + '</td>' +
        '</tr>';
    }).join('');
    $('#notif-rules-body').html(rows);

    /* Quiet hours */
    if (prefs && prefs.quiet_hours) {
      var qh = prefs.quiet_hours;
      var qhEl = document.getElementById('quiet-hours-enabled');
      if (qhEl) qhEl.checked = !!qh.enabled;
      var startEl = document.getElementById('quiet-start'), endEl = document.getElementById('quiet-end');
      if (startEl) startEl.value = qh.start || '22:00';
      if (endEl)   endEl.value   = qh.end   || '08:00';
    }

    /* Save button */
    var saveBtn = document.getElementById('btn-save-notifications');
    if (saveBtn) {
      saveBtn.addEventListener('click', function () {
        var $btn = $(this);
        $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span> Saving…');

        var payload = { events: {} };
        eventsData.forEach(function (e) {
          payload.events[e.key] = {
            in_app:    !!(document.getElementById('t-inapp-' + e.key) || {}).checked,
            email:     !!(document.getElementById('t-email-' + e.key) || {}).checked,
            whatsapp:  !!(document.getElementById('t-wa-'    + e.key) || {}).checked,
            sms:       !!(document.getElementById('t-sms-'   + e.key) || {}).checked,
          };
        });
        var qhToggle = document.getElementById('quiet-hours-enabled');
        payload.quiet_hours = {
          enabled:  qhToggle ? qhToggle.checked : false,
          start:    (document.getElementById('quiet-start') || {}).value || '22:00',
          end:      (document.getElementById('quiet-end')   || {}).value || '08:00',
          timezone: 'Asia/Karachi',
        };

        function onDone() {
          $btn.prop('disabled', false).html('<i class="fi fi-rr-check me-1"></i> Saved').addClass('btn-success').removeClass('btn-primary');
          setTimeout(function () { $btn.html('Save Preferences').addClass('btn-primary').removeClass('btn-success'); }, 2000);
        }
        if (cfg && !cfg.DUMMY_MODE) {
          window.CRM_API.notificationPreferences.update(payload).then(onDone).catch(function () { $btn.prop('disabled', false).html('Save Preferences'); });
        } else {
          setTimeout(onDone, 400);
        }
      });
    }
  }

  /* Load */
  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.notificationPreferences.get()
      .then(function (res) { renderEvents(res.data || {}); })
      .catch(function () { renderEvents({}); });
  } else {
    renderEvents({});
  }

})();
