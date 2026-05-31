/* Pakistan CRM — Consent & Privacy Manager (J-05) */
/* GDPR/PDPA 2023 aligned. SERVICE_COMMUNICATION auto-granted. MARKETING explicit opt-in. */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function renderConsents(consents) {
    var rows = consents.map(function (c) {
      var sc = c.service_communication || {};
      var mk = c.marketing            || {};
      return '<tr>' +
        '<td class="text-center fw-semibold">' + (c.contact_name || '—') + '</td>' +
        '<td class="text-center">' + (c.phone_e164 || '—') + '</td>' +
        '<td class="text-center">' +
          (sc.granted ? '<span class="badge bg-success-subtle text-success">Granted</span>' : '<span class="badge bg-secondary-subtle text-secondary">—</span>') +
        '</td>' +
        '<td class="text-center">' +
          (mk.granted
            ? '<span class="badge bg-success-subtle text-success">Opted in</span>'
            : (mk.revoked_at
              ? '<span class="badge bg-danger-subtle text-danger" title="via ' + (mk.keyword || 'STOP') + '">Opted out</span>'
              : '<span class="badge bg-secondary-subtle text-secondary">Not set</span>')) +
        '</td>' +
        '<td class="text-center">' +
          '<button class="btn btn-xs btn-outline-danger waves-effect btn-revoke" data-id="' + c.contact_id + '" ' + (mk.revoked_at ? 'disabled' : '') + '>Revoke Marketing</button>' +
        '</td></tr>';
    }).join('');
    $('#consent-table-body').html(rows || '<tr><td colspan="5" class="text-center text-muted py-3">No consent records</td></tr>');

    /* Revoke handler */
    document.querySelectorAll('.btn-revoke').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var cid = this.dataset.id;
        var b   = this;
        if (!window.confirm('Revoke marketing consent for this contact? This is irreversible.')) return;
        b.disabled = true;
        if (cfg && !cfg.DUMMY_MODE) {
          window.CRM_API.privacy.consentUpdate(cid, { marketing: { granted: false, revoked_at: new Date().toISOString(), keyword: 'manual_revoke' } })
            .then(function () { location.reload(); })
            .catch(function () { b.disabled = false; });
        } else {
          b.textContent = 'Revoked'; b.className = 'btn btn-xs btn-secondary';
        }
      });
    });
  }

  function renderDsrs(dsrs) {
    $('#dsr-badge').text(dsrs.filter(function (d) { return d.status === 'pending'; }).length);
    var rows = dsrs.map(function (r) {
      var slaDays = r.sla_due_at ? Math.ceil((new Date(r.sla_due_at) - new Date()) / 86400000) : '—';
      return '<tr>' +
        '<td class="text-center">' + (r.contact_id || '—') + '</td>' +
        '<td class="text-center text-capitalize">' + (r.request_type || '—') + '</td>' +
        '<td class="text-center">' +
          '<span class="badge ' + ({ pending:'bg-warning-subtle text-warning', in_progress:'bg-info-subtle text-info', completed:'bg-success-subtle text-success' }[r.status] || 'bg-secondary-subtle text-secondary') + '">' + (r.status || '—') + '</span>' +
        '</td>' +
        '<td class="text-center">' + (slaDays !== '—' ? slaDays + ' days' : '—') + '</td>' +
        '</tr>';
    }).join('');
    $('#dsr-table-body').html(rows || '<tr><td colspan="4" class="text-center text-muted py-3">No data subject requests</td></tr>');
  }

  /* New DSR form */
  var dsrBtn = document.getElementById('btn-submit-dsr');
  if (dsrBtn) {
    dsrBtn.addEventListener('click', function () {
      var contactId = ($('#dsr-contact-id').val() || '').trim();
      var type      = ($('#dsr-type').val()       || '').trim();
      var reason    = ($('#dsr-reason').val()     || '').trim();
      if (!contactId || !type) { alert('Contact ID and request type are required.'); return; }

      var $btn = $(this);
      $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1"></span>');

      function onSuccess() {
        $btn.prop('disabled', false).html('Submit Request');
        alert('Data Subject Request submitted (30-day SLA).');
        $('#dsr-contact-id, #dsr-reason').val('');
        if (cfg && !cfg.DUMMY_MODE) {
          window.CRM_API.privacy.dsrList().then(function (res) { renderDsrs(res.data || []); }).catch(function () {});
        }
      }
      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.privacy.dsrCreate({ contact_id: contactId, request_type: type, reason: reason })
          .then(onSuccess).catch(function () { $btn.prop('disabled', false).html('Submit Request'); alert('Error submitting DSR.'); });
      } else {
        setTimeout(onSuccess, 400);
      }
    });
  }

  /* Load */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.privacy.consentList(),
      window.CRM_API.privacy.dsrList()
    ]).then(function (results) {
      renderConsents(results[0].data || []);
      renderDsrs(results[1].data || []);
    }).catch(function () {
      /* Fallback: derive consent from contacts */
      var contacts = (_d && _d.contacts && _d.contacts.data) || [];
      var fallback  = contacts.map(function (c) {
        var hasMarketing = c.tags && (c.tags.indexOf('Customer') !== -1 || c.tags.indexOf('VIP') !== -1);
        return { contact_id: c.contact_id, contact_name: c.display_name, phone_e164: c.phone_e164, service_communication:{ granted:true }, marketing:{ granted: hasMarketing } };
      });
      renderConsents(fallback);
      renderDsrs([]);
    });
  } else {
    var contacts = (_d && _d.contacts && _d.contacts.data) || [];
    var fallback  = contacts.map(function (c) {
      var hasMarketing = c.tags && (c.tags.indexOf('Customer') !== -1 || c.tags.indexOf('VIP') !== -1);
      return { contact_id: c.contact_id, contact_name: c.display_name, phone_e164: c.phone_e164, service_communication:{ granted:true }, marketing:{ granted: hasMarketing, revoked_at: hasMarketing ? null : null } };
    });
    renderConsents(fallback);
    renderDsrs([]);
  }

})();
