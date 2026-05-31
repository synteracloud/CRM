/* Pakistan CRM — Lead Detail (C-01) */

(function () {
  'use strict';

  var cfg = window.CRM_CONFIG;
  var _d  = window.CRM_DUMMY;

  /* ── Lead ID from URL params (fallback to first dummy lead) ──────── */
  var leadId = new URLSearchParams(window.location.search).get('id') || 'l-001';

  /* ── Helpers ─────────────────────────────────────────────────────── */
  function pkr(n) { return 'PKR ' + Number(n || 0).toLocaleString('en-IN'); }

  function fmtDate(iso) {
    if (!iso) return '—';
    var dt = new Date(iso);
    return dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function fmtPhone(e164) {
    if (!e164) return '—';
    var m = e164.match(/^\+92(\d{3})(\d{3})(\d{4})$/);
    return m ? '+92 ' + m[1] + ' ' + m[2] + ' ' + m[3] : e164;
  }

  function cap(str) {
    if (!str) return '—';
    return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
  }

  /* ── Config maps ─────────────────────────────────────────────────── */
  var STAGE_ORDER = ['new', 'qualifying', 'nurturing', 'proposal', 'negotiation', 'won'];

  var STAGE_CFG = {
    new:          { cls: 'primary',   label: 'New',          icon: 'fi fi-rr-check' },
    qualifying:   { cls: 'info',      label: 'Qualifying',   icon: 'fi fi-rr-phone-call' },
    nurturing:    { cls: 'warning',   label: 'Nurturing',    icon: 'fi fi-rr-handshake' },
    proposal:     { cls: 'warning',   label: 'Proposal',     icon: 'fi fi-rr-file-invoice' },
    negotiation:  { cls: 'danger',    label: 'Negotiation',  icon: 'fi fi-rr-handshake' },
    won:          { cls: 'success',   label: 'Won',          icon: 'fi fi-rr-trophy' },
    lost:         { cls: 'secondary', label: 'Lost',         icon: 'fi fi-rr-times' },
    disqualified: { cls: 'secondary', label: 'Disqualified', icon: 'fi fi-rr-ban' }
  };

  var SOURCE_CFG = {
    whatsapp:  { cls: 'success',   label: 'WhatsApp',  icon: 'fi fi-brands-whatsapp' },
    web:       { cls: 'info',      label: 'Web',       icon: 'fi fi-rr-globe' },
    referral:  { cls: 'warning',   label: 'Referral',  icon: 'fi fi-rr-user-check' },
    manual:    { cls: 'primary',   label: 'Manual',    icon: 'fi fi-rr-phone-call' },
    campaign:  { cls: 'secondary', label: 'Campaign',  icon: 'fi fi-rr-calendar' },
    import:    { cls: 'secondary', label: 'Import',    icon: 'fi fi-rr-file-import' }
  };

  var LEVEL_CFG = {
    none:       { cls: 'secondary', label: 'None' },
    reminder:   { cls: 'success',   label: 'Reminder' },
    warning:    { cls: 'warning',   label: 'Warning' },
    escalated:  { cls: 'danger',    label: 'Escalated' },
    reassigned: { cls: 'dark',      label: 'Reassigned' }
  };

  var ACTION_ICON = {
    Call:     'fi-rr-phone-call',
    WhatsApp: 'fi-brands-whatsapp',
    Reminder: 'fi-rr-bell',
    Email:    'fi-rr-envelope'
  };

  var ACTIVITY_CFG = {
    call:     { cls: 'primary', icon: 'fi fi-rr-phone-call' },
    email:    { cls: 'primary', icon: 'fi fi-rr-envelope' },
    whatsapp: { cls: 'success', icon: 'fi fi-brands-whatsapp' },
    meeting:  { cls: 'warning', icon: 'fi fi-rr-handshake' },
    note:     { cls: 'info',    icon: 'fi fi-rr-sticky-note' }
  };

  /* ── Badge helpers ────────────────────────────────────────────────── */
  function stageBadge(stage) {
    var cfg2 = STAGE_CFG[stage] || { cls: 'secondary', label: stage };
    return '<span class="badge bg-' + cfg2.cls + '-subtle text-' + cfg2.cls + ' text-capitalize">' + cfg2.label + '</span>';
  }

  function sourceBadge(source) {
    var cfg2 = SOURCE_CFG[source] || { cls: 'secondary', label: source, icon: 'fi fi-rr-info' };
    return '<span class="badge bg-' + cfg2.cls + '-subtle text-' + cfg2.cls + '">' +
      '<i class="' + cfg2.icon + ' me-1"></i>' + cfg2.label + '</span>';
  }

  /* ── Core render (receives all resolved data) ─────────────────────── */
  function render(lead, followups, activities, scoreData, ownerName) {
    if (!lead) { return; }

    /* Lead Score card */
    var bandClass = { hot: 'bg-success', warm: 'bg-primary', cold: 'bg-secondary', disqualified: 'bg-danger' };
    var sv = document.getElementById('lead-score-value');
    if (sv) sv.textContent = scoreData.score || 0;
    var sb2 = document.getElementById('lead-score-band');
    if (sb2) {
      sb2.textContent = (scoreData.score_band || 'cold').replace(/_/g, ' ');
      sb2.className = 'badge badge-sm ' + (bandClass[scoreData.score_band] || 'bg-secondary');
    }
    var sbar = document.getElementById('lead-score-bar');
    if (sbar) sbar.style.width = (scoreData.score || 0) + '%';
    var sdrv = document.getElementById('lead-score-drivers');
    if (sdrv && scoreData.top_drivers && scoreData.top_drivers.length) {
      sdrv.textContent = 'Top drivers: ' + scoreData.top_drivers.join(', ');
    }

    /* Find first overdue follow-up */
    var overdueFollowup = null;
    for (var i = 0; i < followups.length; i++) {
      if (followups[i].state === 'overdue') { overdueFollowup = followups[i]; break; }
    }

    /* Identity strip */
    var avatarSrc = 'assets/images/avatar/avatar1.webp';
    $('#lead-breadcrumb').text(lead.contact_name);
    $('#lead-avatar-img').attr({ src: avatarSrc, alt: lead.contact_name });
    $('#lead-name').text(lead.contact_name);
    $('#lead-phone-label').html('<i class="fi fi-rr-phone-call me-1"></i>' + fmtPhone(lead.contact_phone_e164));
    $('#lead-stage-badge').html(stageBadge(lead.stage));
    $('#lead-source-badge').html(sourceBadge(lead.source));

    if (overdueFollowup) {
      var lc = LEVEL_CFG[overdueFollowup.escalation_level] || { cls: 'danger', label: overdueFollowup.escalation_level };
      $('#enforcement-badge').html(
        '<span class="badge bg-' + lc.cls + '-subtle text-' + lc.cls + '">' +
          '<i class="fi fi-rr-shield-exclamation me-1"></i>' + lc.label + '</span>'
      );
    }

    /* Next Action card */
    if (overdueFollowup) {
      var of   = overdueFollowup;
      var ofLc = LEVEL_CFG[of.escalation_level] || { cls: 'danger', label: of.escalation_level };
      var ofIcon = ACTION_ICON[of.action_type] || 'fi-rr-bolt';
      var daysOver = Math.max(1, Math.ceil((Date.now() - new Date(of.due_at).getTime()) / 86400000));

      $('#next-action-card').addClass('border-danger');
      $('#next-action-icon-wrap').addClass('bg-danger-subtle text-danger').html('<i class="fi ' + ofIcon + '"></i>');
      $('#next-action-title').addClass('text-danger');
      $('#next-action-body').html(
        '<p class="mb-2"><strong>' + (of.action_type || 'Follow-up') + '</strong> — overdue by ' +
          daysOver + ' day' + (daysOver !== 1 ? 's' : '') + '.</p>' +
        '<p class="text-muted small mb-3">Enforcement level: <strong class="text-' + ofLc.cls + '">' +
          ofLc.label + '</strong>. Escalation triggers automatically if not actioned today.</p>' +
        '<button type="button" class="btn btn-sm btn-danger waves-effect w-100">' +
          '<i class="fi ' + ofIcon + ' me-1"></i>Log ' + (of.action_type || 'Follow-up') + ' Now</button>'
      );
    } else {
      $('#next-action-card').addClass('border-success');
      $('#next-action-icon-wrap').addClass('bg-success-subtle text-success').html('<i class="fi fi-rr-check-circle"></i>');
      $('#next-action-body').html('<p class="text-muted small mb-0">No overdue actions. This lead is on track.</p>');
    }

    /* Lead Info card */
    $('#info-full-name').text(lead.contact_name);
    $('#info-phone').text(fmtPhone(lead.contact_phone_e164));
    $('#info-source').text(cap(lead.source));
    $('#info-stage-badge').html(stageBadge(lead.stage));
    $('#info-owner-avatar').attr({ src: avatarSrc, alt: ownerName });
    $('#info-owner-name').text(ownerName || lead.owner_id || '—');
    $('#info-created-at').text(fmtDate(lead.created_at));
    $('#info-estimated-value').text(pkr(lead.estimated_value));

    /* Tab 1: Contact fields */
    $('#field-full-name').val(lead.contact_name);
    $('#field-phone').val(lead.contact_phone_e164);
    $('#field-email').val(lead.contact_email || '');
    $('#field-source').val(cap(lead.source));
    $('#field-priority').val(cap(lead.priority));
    $('#field-est-value').val(Number(lead.estimated_value || 0).toLocaleString('en-IN'));

    /* Tab 2: Pipeline stepper */
    var stageIdx = STAGE_ORDER.indexOf(lead.stage);
    var stepperHtml = '';
    for (var si = 0; si < STAGE_ORDER.length; si++) {
      var s    = STAGE_ORDER[si];
      var scfg = STAGE_CFG[s] || { cls: 'secondary', label: s, icon: 'fi fi-rr-circle' };
      var done    = si < stageIdx;
      var current = si === stageIdx;
      var aCls = (done || current) ? 'bg-' + scfg.cls + ' text-white' : 'bg-secondary-subtle text-secondary';
      var lCls = current ? 'text-' + scfg.cls + ' fw-semibold' : (done ? 'text-' + scfg.cls : 'text-muted');

      stepperHtml +=
        '<div class="d-flex flex-column align-items-center">' +
          '<div class="avatar avatar-sm ' + aCls + ' rounded-circle mb-1">' +
            '<i class="' + scfg.icon + ' text-2xs"></i>' +
          '</div>' +
          '<small class="' + lCls + '">' + scfg.label + '</small>' +
        '</div>';

      if (si < STAGE_ORDER.length - 1) {
        var lnCls = si < stageIdx ? 'border-' + scfg.cls : 'border-secondary opacity-25';
        stepperHtml += '<div class="flex-grow-1 border-top border-2 ' + lnCls + '" style="min-width:30px;"></div>';
      }
    }
    $('#stage-stepper').html(stepperHtml);

    var nextStage = STAGE_ORDER[stageIdx + 1];
    if (nextStage) {
      var nsCfg = STAGE_CFG[nextStage] || { label: nextStage };
      $('#btn-advance-stage').html('<i class="fi fi-rr-arrow-right me-1"></i>Advance to ' + nsCfg.label);
    } else {
      $('#btn-advance-stage').prop('disabled', true).text('Already at final stage');
    }

    $('#stage-history-body').html(
      '<tr>' +
        '<td>' + stageBadge(lead.stage) + '</td>' +
        '<td>' + fmtDate(lead.created_at) + '</td>' +
        '<td>System (' + cap(lead.source) + ')</td>' +
        '<td class="text-muted">current</td>' +
      '</tr>'
    );

    /* Tab 3: Follow-up tasks */
    var overdueCount = 0;
    for (var fi = 0; fi < followups.length; fi++) {
      if (followups[fi].state === 'overdue') overdueCount++;
    }
    if (overdueCount > 0) {
      $('#followup-count-badge').text(overdueCount).css('display', '');
    }

    var taskHtml = '';
    if (followups.length === 0) {
      taskHtml = '<p class="text-muted small">No follow-up tasks for this lead.</p>';
    } else {
      for (var fj = 0; fj < followups.length; fj++) {
        var ft    = followups[fj];
        var isOvd = ft.state === 'overdue';
        var ftLc  = LEVEL_CFG[ft.escalation_level] || { cls: 'secondary', label: ft.escalation_level };
        var ftIco = ACTION_ICON[ft.action_type] || 'fi-rr-bell';
        var cCls  = isOvd ? 'bg-danger-subtle border-0' : 'border';
        var iCls  = isOvd ? 'bg-danger text-white' : 'bg-warning-subtle text-warning';
        var dLbl  = isOvd
          ? '<span class="text-danger fw-semibold">' + fmtDate(ft.due_at) + ' — OVERDUE</span>'
          : '<span class="text-muted">Due ' + fmtDate(ft.due_at) + '</span>';
        var bCls  = isOvd ? 'btn-danger' : 'btn-outline-success';
        var attempts = ft.attempts_count !== undefined ? ft.attempts_count : 0;

        taskHtml +=
          '<div class="card ' + cCls + ' mb-2">' +
            '<div class="card-body py-3">' +
              '<div class="d-flex align-items-start justify-content-between gap-2">' +
                '<div class="d-flex align-items-start gap-2">' +
                  '<div class="avatar avatar-sm ' + iCls + ' rounded-3 flex-shrink-0">' +
                    '<i class="fi ' + ftIco + ' text-xs"></i>' +
                  '</div>' +
                  '<div>' +
                    '<div class="fw-semibold">' + (ft.action_type || 'Follow-up') + ' follow-up</div>' +
                    '<div class="small">' +
                      dLbl +
                      ' · <span class="badge bg-' + ftLc.cls + '-subtle text-' + ftLc.cls + '">' + ftLc.label + '</span>' +
                      ' · ' + attempts + ' attempt' + (attempts !== 1 ? 's' : '') +
                    '</div>' +
                  '</div>' +
                '</div>' +
                '<div class="btn-group flex-shrink-0">' +
                  '<button type="button" class="btn btn-sm ' + bCls + ' waves-effect">' +
                    '<i class="fi fi-rr-check me-1"></i>Log Done' +
                  '</button>' +
                  '<button type="button" class="btn btn-sm btn-outline-secondary waves-effect" data-bs-toggle="dropdown">' +
                    '<i class="fi fi-rr-angle-down"></i>' +
                  '</button>' +
                  '<ul class="dropdown-menu dropdown-menu-end">' +
                    '<li><a class="dropdown-item" href="javascript:void(0);">Snooze</a></li>' +
                    '<li><a class="dropdown-item" href="javascript:void(0);">Escalate</a></li>' +
                  '</ul>' +
                '</div>' +
              '</div>' +
            '</div>' +
          '</div>';
      }
    }
    $('#followup-tasks-list').html(taskHtml);

    /* Tab 4: Activity timeline */
    var actHtml = '';
    if (activities.length === 0) {
      actHtml = '<p class="text-muted small">No activity recorded for this lead.</p>';
    } else {
      for (var ai = 0; ai < activities.length; ai++) {
        var act  = activities[ai];
        var acfg = ACTIVITY_CFG[act.activity_type] || { cls: 'secondary', icon: 'fi fi-rr-info' };
        var byName = act.performed_by || '—';
        var isLast = ai === activities.length - 1;

        actHtml +=
          '<div class="d-flex gap-3 ' + (isLast ? 'mb-0' : 'mb-3') + '">' +
            '<div class="d-flex flex-column align-items-center">' +
              '<div class="avatar avatar-sm bg-' + acfg.cls + '-subtle text-' + acfg.cls + ' rounded-circle flex-shrink-0">' +
                '<i class="' + acfg.icon + ' text-xs"></i>' +
              '</div>' +
              (isLast ? '' : '<div class="border-start border-2 flex-grow-1 mt-1" style="width:2px;min-height:20px;"></div>') +
            '</div>' +
            '<div class="' + (isLast ? '' : 'pb-3') + '">' +
              '<div class="fw-semibold">' + (act.description || cap(act.activity_type)) + '</div>' +
              '<div class="text-muted small">' + fmtDate(act.occurred_at) + ' · ' + byName + '</div>' +
            '</div>' +
          '</div>';
      }
    }
    $('#activity-timeline-list').html(actHtml);
  }

  /* ── Load: live API or dummy fallback ─────────────────────────────── */
  if (cfg && !cfg.DUMMY_MODE) {
    Promise.all([
      window.CRM_API.leads.get(leadId)
        .catch(function () { return { data: null }; }),
      window.CRM_API.followups.list({ lead_id: leadId, limit: 50 })
        .catch(function () { return { data: [] }; }),
      window.CRM_API.activities.list({ entity_id: leadId, limit: 50 })
        .catch(function () { return { data: [] }; }),
      window.CRM_API.ai.scores.get(leadId)
        .catch(function () { return { data: { score: 0, score_band: 'cold', top_drivers: [] } }; })
    ])
    .then(function (results) {
      var lead       = results[0].data;
      var followups  = results[1].data || [];
      var activities = results[2].data || [];
      var aiRaw      = results[3].data || {};
      var scoreData  = { score: aiRaw.score || 0, score_band: aiRaw.score_band || 'cold', top_drivers: aiRaw.top_drivers || [] };

      if (!lead) {
        /* Lead not found — fall back silently to dummy for first test record */
        if (_d) {
          var dl = _d.leads.data.filter(function (l) { return l.lead_id === leadId; })[0] || _d.leads.data[0];
          var df = _d.followups.data.filter(function (f) { return f.lead_id === (dl && dl.lead_id); });
          var da = _d.activities.data.filter(function (a) { return a.entity_id === (dl && dl.lead_id); });
          var dScore = (_d.aiModelKpi || {}).lead_score_demo || { score: 0, score_band: 'cold', top_drivers: [] };
          render(dl, df, da, dScore, '—');
        }
        return;
      }

      render(lead, followups, activities, scoreData, lead.owner_id || '—');
    });
  } else {
    if (!_d) return;
    var lead = _d.leads.data.filter(function (l) { return l.lead_id === leadId; })[0];
    if (!lead) lead = _d.leads.data[0];
    if (!lead) return;

    var owner = _d.users.data.filter(function (u) { return u.id === lead.owner_id; })[0] || {};
    var followups  = _d.followups.data.filter(function (f) { return f.lead_id === lead.lead_id; });
    var activities = _d.activities.data.filter(function (a) { return a.entity_id === lead.lead_id; });
    var scoreData  = (_d.aiModelKpi || {}).lead_score_demo || { score: 0, score_band: 'cold', top_drivers: [] };

    render(lead, followups, activities, scoreData, owner.display_name || '—');
  }

})();
