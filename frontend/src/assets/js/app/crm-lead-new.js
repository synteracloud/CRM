/* Pakistan CRM — New Lead Wizard (I-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  /* ── Populate owner dropdown ──────────────────────────────────────── */
  function populateOwners(users) {
    var sel = document.getElementById('lead-owner');
    if (!sel) return;
    users.forEach(function (u) {
      var opt = document.createElement('option');
      opt.value = u.id;
      opt.textContent = u.display_name;
      sel.appendChild(opt);
    });
  }

  if (cfg && !cfg.DUMMY_MODE) {
    window.CRM_API.users.list()
      .then(function (res) { populateOwners(res.data || []); })
      .catch(function () { populateOwners((_d && _d.users && _d.users.data) || []); });
  } else {
    populateOwners((_d && _d.users && _d.users.data) || []);
  }

  /* ── State ───────────────────────────────────────────────────────── */
  var step = 1;

  /* ── Elements ────────────────────────────────────────────────────── */
  var $step1    = document.getElementById('wizard-step-1');
  var $step2    = document.getElementById('wizard-step-2');
  var $success  = document.getElementById('wizard-success');

  var $dot1     = document.getElementById('tracker-dot-1');
  var $dot2     = document.getElementById('tracker-dot-2');
  var $lbl1     = document.getElementById('tracker-label-1');
  var $lbl2     = document.getElementById('tracker-label-2');
  var $conn     = document.getElementById('tracker-connector');

  var $phone    = document.getElementById('lead-phone');
  var $fname    = document.getElementById('lead-fname');
  var $lname    = document.getElementById('lead-lname');
  var $dedup    = document.getElementById('dedup-warning');
  var $dedupTxt = document.getElementById('dedup-warning-text');
  var $dedupLnk = document.getElementById('dedup-link');

  var $stage    = document.getElementById('lead-stage');
  var $owner    = document.getElementById('lead-owner');
  var $source   = document.getElementById('lead-source');

  var $namePreview  = document.getElementById('s2-name-preview');
  var $phonePreview = document.getElementById('s2-phone-preview');

  /* ── flatpickr ───────────────────────────────────────────────────── */
  if (document.getElementById('lead-followup-due')) {
    flatpickr('#lead-followup-due', { minDate: 'today', dateFormat: 'Y-m-d' });
  }

  /* ── Helpers ─────────────────────────────────────────────────────── */
  function isValidE164(val) {
    return /^\+[1-9]\d{6,14}$/.test(val.trim());
  }

  function setInvalid(el, msg) {
    el.classList.add('is-invalid');
    var fb = el.parentElement.querySelector('.invalid-feedback') ||
             document.getElementById(el.id + '-error');
    if (fb && msg) fb.textContent = msg;
  }

  function clearInvalid(el) {
    el.classList.remove('is-invalid');
    el.classList.remove('is-valid');
  }

  function markValid(el) {
    el.classList.remove('is-invalid');
    el.classList.add('is-valid');
  }

  /* ── Phone dedup check ───────────────────────────────────────────── */
  $phone.addEventListener('blur', function () {
    var val = $phone.value.trim();
    if (!val || !isValidE164(val)) return;

    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.leads.list({ contact_phone_e164: val, limit: 1 })
        .then(function (res) {
          if (res.data && res.data.length > 0) {
            var match = res.data[0];
            $dedupTxt.textContent = 'A lead with this number already exists: ' + (match.contact_name || match.lead_id) + '.';
            $dedupLnk.href = 'app/leads-detail.html?id=' + match.lead_id;
            $dedup.classList.remove('d-none');
          } else {
            $dedup.classList.add('d-none');
          }
        })
        .catch(function () { $dedup.classList.add('d-none'); });
    } else {
      /* Dummy dedup table */
      var EXISTING_PHONES = {
        '+923001234567': { name: 'Ahmed Raza',  href: 'app/leads-detail.html' },
        '+923119876543': { name: 'Sara Khan',   href: 'app/leads-detail.html' },
        '+923451122334': { name: 'Bilal Malik', href: 'app/leads-detail.html' }
      };
      var match = EXISTING_PHONES[val];
      if (match) {
        $dedupTxt.textContent = 'A lead with this number already exists: ' + match.name + '.';
        $dedupLnk.href = match.href;
        $dedup.classList.remove('d-none');
      } else {
        $dedup.classList.add('d-none');
      }
    }
  });

  $phone.addEventListener('input', function () {
    if ($dedup && !$dedup.classList.contains('d-none')) $dedup.classList.add('d-none');
    clearInvalid($phone);
  });

  [$fname, $lname].forEach(function (el) {
    el.addEventListener('input', function () { clearInvalid(el); });
  });

  /* ── Validate step 1 ─────────────────────────────────────────────── */
  function validateStep1() {
    var ok = true;
    var phoneVal = $phone.value.trim();

    clearInvalid($phone);
    clearInvalid($fname);
    clearInvalid($lname);

    if (!isValidE164(phoneVal)) {
      setInvalid($phone, 'Please enter a valid E.164 phone number (e.g. +923001234567).');
      ok = false;
    } else {
      markValid($phone);
    }

    if (!$fname.value.trim()) {
      setInvalid($fname, 'First name is required.');
      ok = false;
    } else {
      markValid($fname);
    }

    if (!$lname.value.trim()) {
      setInvalid($lname, 'Last name is required.');
      ok = false;
    } else {
      markValid($lname);
    }

    return ok;
  }

  /* ── Validate step 2 ─────────────────────────────────────────────── */
  function validateStep2() {
    var ok = true;
    [$stage, $owner, $source].forEach(function (el) {
      clearInvalid(el);
      if (!el.value) {
        el.classList.add('is-invalid');
        ok = false;
      } else {
        markValid(el);
      }
    });
    return ok;
  }

  /* ── Step tracker update ─────────────────────────────────────────── */
  function activateStep(n) {
    step = n;
    if (n === 1) {
      $dot1.style.background = 'var(--bs-primary)';
      $dot1.style.color = '#fff';
      $dot1.style.border = 'none';
      $lbl1.className = 'fw-semibold text-primary small';

      $dot2.style.background = 'var(--bs-secondary-bg)';
      $dot2.style.color = 'var(--bs-secondary-color)';
      $dot2.style.border = '2px solid var(--bs-border-color)';
      $lbl2.className = 'small text-muted';
      $conn.style.opacity = '0.3';

      $step1.classList.remove('d-none');
      $step2.classList.add('d-none');
    } else {
      $dot1.style.background = 'var(--bs-success)';
      $dot1.style.color = '#fff';
      $dot1.style.border = 'none';
      $dot1.innerHTML = '<i class="fi fi-rr-check" style="font-size:.75rem;"></i>';
      $lbl1.className = 'fw-semibold text-success small';

      $dot2.style.background = 'var(--bs-primary)';
      $dot2.style.color = '#fff';
      $dot2.style.border = 'none';
      $lbl2.className = 'fw-semibold text-primary small';
      $conn.style.opacity = '1';

      $namePreview.textContent = $fname.value.trim() + ' ' + $lname.value.trim();
      $phonePreview.textContent = $phone.value.trim();

      $step1.classList.add('d-none');
      $step2.classList.remove('d-none');
    }
  }

  /* ── Navigation handlers ─────────────────────────────────────────── */
  document.getElementById('btn-next').addEventListener('click', function () {
    if (validateStep1()) activateStep(2);
  });

  document.getElementById('btn-back').addEventListener('click', function () {
    activateStep(1);
  });

  var discardModal = new bootstrap.Modal(document.getElementById('modal-discard'));

  document.getElementById('btn-cancel-s1').addEventListener('click', function () {
    var hasData = $phone.value || $fname.value || $lname.value;
    if (hasData) {
      discardModal.show();
    } else {
      window.location.href = 'app/leads.html';
    }
  });

  document.getElementById('btn-cancel-s2').addEventListener('click', function () {
    discardModal.show();
  });

  /* ── Submit ──────────────────────────────────────────────────────── */
  document.getElementById('btn-submit').addEventListener('click', function () {
    if (!validateStep2()) return;

    var $btn = this;
    $btn.disabled = true;
    $btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Saving…';

    var notes    = document.getElementById('lead-notes');
    var followup = document.getElementById('lead-followup-due');

    var payload = {
      contact_name:      $fname.value.trim() + ' ' + $lname.value.trim(),
      contact_phone_e164: $phone.value.trim(),
      stage:             $stage.value,
      owner_id:          $owner.value,
      source:            $source.value,
      notes:             notes ? notes.value.trim() : '',
      estimated_value:   0,
      currency:          'PKR'
    };

    function onSuccess(leadId) {
      var fullName = payload.contact_name;
      document.getElementById('success-name').textContent = fullName;
      $step2.classList.add('d-none');
      $success.classList.remove('d-none');
      document.getElementById('wizard-step-tracker').closest('.card-body').classList.add('d-none');
      $btn.disabled = false;
      $btn.textContent = 'Save Lead';
    }

    function onError(err) {
      $btn.disabled = false;
      $btn.textContent = 'Save Lead';
      var msg = (err && err.error && err.error.message) ? err.error.message : 'Failed to save lead. Please try again.';
      alert(msg);
    }

    if (cfg && !cfg.DUMMY_MODE) {
      window.CRM_API.leads.create(payload)
        .then(function (res) { onSuccess(res.data && res.data.lead_id); })
        .catch(onError);
    } else {
      setTimeout(function () { onSuccess('l-new-dummy'); }, 600);
    }
  });

  /* ── Add another ─────────────────────────────────────────────────── */
  document.getElementById('btn-add-another').addEventListener('click', function () {
    [$phone, $fname, $lname].forEach(function (el) {
      el.value = '';
      el.classList.remove('is-valid', 'is-invalid');
    });
    [$stage, $owner, $source].forEach(function (el) {
      el.selectedIndex = 0;
      el.classList.remove('is-valid', 'is-invalid');
    });
    document.getElementById('lead-notes').value = '';
    $dedup.classList.add('d-none');
    $dot1.innerHTML = '1';

    document.getElementById('wizard-step-tracker').closest('.card-body').classList.remove('d-none');

    $success.classList.add('d-none');
    activateStep(1);
  });

})();
