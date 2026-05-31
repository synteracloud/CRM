/* Pakistan CRM — New Opportunity Form (I-03) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  function pkr(n) {
    if (!n || isNaN(n)) return '—';
    n = Number(n);
    if (n >= 10000000) return 'PKR ' + (n / 10000000).toFixed(2) + ' Cr';
    if (n >= 100000)   return 'PKR ' + (n / 100000).toFixed(2) + ' L';
    return 'PKR ' + n.toLocaleString('en-IN');
  }

  function buildAccountOptions(contacts, opps) {
    var accountSet = {};
    contacts.forEach(function (c) { if (c.account_name) accountSet[c.account_name] = true; });
    opps.forEach(function (o) { if (o.account_name) accountSet[o.account_name] = true; });
    var $account = $('#opp-account');
    Object.keys(accountSet).sort().forEach(function (name) {
      $account.append('<option value="' + name + '">' + name + '</option>');
    });
  }

  function buildContactOptions(contacts) {
    var $contact = $('#opp-contact');
    contacts.forEach(function (c) {
      $contact.append('<option value="' + c.contact_id + '">' + c.display_name + ' (' + (c.account_name || '—') + ')</option>');
    });
  }

  function buildOwnerOptions(users) {
    var $owner = $('#opp-owner');
    users.forEach(function (u) {
      $owner.append('<option value="' + u.id + '">' + u.display_name + '</option>');
    });
  }

  function initForm(users, contacts, opps) {
    buildAccountOptions(contacts, opps);
    buildContactOptions(contacts);
    buildOwnerOptions(users);

    $('#opp-amount').on('input', function () {
      var val = parseFloat($(this).val());
      $('#opp-amount-preview').text(isNaN(val) ? '—' : pkr(val));
    });

    if (window.flatpickr) {
      flatpickr('#opp-close-date', { dateFormat: 'Y-m-d', minDate: 'today' });
    }
  }

  var currentStep = 1;

  function activateTracker(step) {
    var PRIMARY = 'background:var(--bs-primary);color:#fff;border:none;';
    var DONE    = 'background:var(--bs-success);color:#fff;border:none;';
    var IDLE    = 'background:var(--bs-secondary-bg);color:var(--bs-secondary-color);border:2px solid var(--bs-border-color);';

    $('#tracker-dot-1').attr('style', 'width:32px;height:32px;font-size:.85rem;' + (step > 1 ? DONE : PRIMARY));
    $('#tracker-dot-1').html(step > 1 ? '<i class="fi fi-rr-check" style="font-size:.8rem;"></i>' : '1');
    $('#tracker-label-1').toggleClass('fw-semibold text-primary', step === 1).toggleClass('text-success', step > 1);

    $('#tracker-dot-2').attr('style', 'width:32px;height:32px;font-size:.85rem;' + (step === 2 ? PRIMARY : IDLE));
    $('#tracker-label-2').toggleClass('fw-semibold text-primary', step === 2).toggleClass('text-muted', step < 2);

    $('#tracker-connector').css('opacity', step > 1 ? '1' : '.3').css('border-color', step > 1 ? 'var(--bs-success)' : '');
  }

  function validateStep1() {
    var valid = true;
    var name  = $('#opp-name').val().trim();
    var acct  = $('#opp-account').val();
    var amt   = $('#opp-amount').val();

    if (!name) { $('#opp-name').addClass('is-invalid');   valid = false; } else { $('#opp-name').removeClass('is-invalid').addClass('is-valid'); }
    if (!acct) { $('#opp-account').addClass('is-invalid'); valid = false; } else { $('#opp-account').removeClass('is-invalid').addClass('is-valid'); }
    if (!amt || isNaN(parseFloat(amt)) || parseFloat(amt) < 0) { $('#opp-amount').addClass('is-invalid'); valid = false; } else { $('#opp-amount').removeClass('is-invalid').addClass('is-valid'); }
    return valid;
  }

  function validateStep2() {
    var valid = true;
    var closeDate = $('#opp-close-date').val();
    var owner     = $('#opp-owner').val();

    if (!closeDate) { $('#opp-close-date').addClass('is-invalid'); valid = false; } else { $('#opp-close-date').removeClass('is-invalid').addClass('is-valid'); }
    if (!owner)     { $('#opp-owner').addClass('is-invalid');       valid = false; } else { $('#opp-owner').removeClass('is-invalid').addClass('is-valid'); }
    return valid;
  }

  function bindNavigation() {
    $('#btn-next').on('click', function () {
      if (!validateStep1()) return;
      $('#s2-name-preview').text($('#opp-name').val().trim());
      $('#s2-account-preview').text($('#opp-account').val());
      $('#s2-amount-preview').text(pkr(parseFloat($('#opp-amount').val())));
      $('#wizard-step-1').addClass('d-none');
      $('#wizard-step-2').removeClass('d-none');
      currentStep = 2;
      activateTracker(2);
    });

    $('#btn-back').on('click', function () {
      $('#wizard-step-2').addClass('d-none');
      $('#wizard-step-1').removeClass('d-none');
      currentStep = 1;
      activateTracker(1);
    });

    $('#btn-cancel-s1, #btn-cancel-s2').on('click', function () {
      new bootstrap.Modal(document.getElementById('modal-discard')).show();
    });

    $('#btn-submit').on('click', function () {
      if (!validateStep2()) return;

      var $btn = $(this);
      $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-1" role="status"></span> Saving…');

      var payload = {
        name:         $('#opp-name').val().trim(),
        account_name: $('#opp-account').val(),
        contact_id:   $('#opp-contact').val() || null,
        amount:       parseFloat($('#opp-amount').val()) || 0,
        currency:     'PKR',
        close_date:   $('#opp-close-date').val(),
        stage:        $('#opp-stage').val() || 'qualification',
        forecast_category: $('#opp-forecast').val() || 'pipeline',
        owner_id:     $('#opp-owner').val(),
        notes:        $('#opp-notes').val() ? $('#opp-notes').val().trim() : ''
      };

      function onSuccess(oppName) {
        $('#success-name').text(oppName);
        $('#wizard-step-2').addClass('d-none');
        $('#wizard-success').removeClass('d-none');
        $btn.prop('disabled', false).text('Save Opportunity');
      }

      function onError(err) {
        $btn.prop('disabled', false).text('Save Opportunity');
        var msg = (err && err.error && err.error.message) ? err.error.message : 'Failed to save. Please try again.';
        alert(msg);
      }

      if (cfg && !cfg.DUMMY_MODE) {
        window.CRM_API.opportunities.create ?
          window.CRM_API.opportunities.create(payload)
            .then(function () { onSuccess(payload.name); })
            .catch(onError)
          : (function () {
              /* create not yet in CRM_API — use raw post */
              fetch(window.CRM_CONFIG.BASE_URL + '/opportunities', {
                method: 'POST',
                headers: { 'Authorization': 'Bearer ' + window.CRM_CONFIG.token, 'Content-Type': 'application/json', 'x-tenant-id': window.CRM_CONFIG.tenantId },
                body: JSON.stringify(payload)
              }).then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
                .then(function () { onSuccess(payload.name); })
                .catch(onError);
            }());
      } else {
        setTimeout(function () { onSuccess(payload.name); }, 600);
      }
    });

    $('#btn-add-another').on('click', function () {
      $('#wizard-success').addClass('d-none');
      $('#wizard-step-1').removeClass('d-none');
      $('input, select, textarea').val('').removeClass('is-valid is-invalid');
      $('#opp-amount-preview').text('—');
      currentStep = 1;
      activateTracker(1);
    });
  }

  /* ── Load ──────────────────────────────────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.users.list(),
      window.CRM_API.contacts.list({ limit: 200 }),
      window.CRM_API.opportunities.list({ limit: 200 })
    ]).then(function (results) {
      initForm(results[0].data || [], results[1].data || [], results[2].data || []);
      bindNavigation();
    }).catch(function () {
      var users    = (_d && _d.users && _d.users.data)            || [];
      var contacts = (_d && _d.contacts && _d.contacts.data)       || [];
      var opps     = (_d && _d.opportunities && _d.opportunities.data) || [];
      initForm(users, contacts, opps);
      bindNavigation();
    });
  } else {
    if (!_d) return;
    initForm(_d.users.data, _d.contacts.data, _d.opportunities.data);
    bindNavigation();
  }

})();
