/* Pakistan CRM — Shared Rendering Components */

window.CRM = window.CRM || {};

window.CRM.components = (function () {
  'use strict';

  /* ── Stage badge ─────────────────────────────────────────────── */
  const STAGE_STYLE = {
    new:          'bg-info-subtle text-info',
    contacted:    'bg-primary-subtle text-primary',
    qualified:    'bg-warning-subtle text-warning',
    proposal:     'bg-purple-subtle text-purple',
    negotiation:  'bg-orange-subtle text-orange',
    closed_won:   'bg-success-subtle text-success',
    closed_lost:  'bg-danger-subtle text-danger',
    qualification:'bg-info-subtle text-info',
    discovery:    'bg-primary-subtle text-primary',
  };
  function stageBadge(stage) {
    const cls = STAGE_STYLE[stage] || 'bg-secondary-subtle text-secondary';
    const lbl = (stage || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    return `<span class="badge ${cls} text-capitalize">${lbl}</span>`;
  }

  /* ── Priority badge ──────────────────────────────────────────── */
  const PRIORITY_STYLE = {
    urgent: 'bg-danger text-white',
    high:   'bg-warning text-dark',
    medium: 'bg-info-subtle text-info',
    low:    'bg-secondary-subtle text-secondary',
  };
  function priorityBadge(priority) {
    const cls = PRIORITY_STYLE[priority] || 'bg-secondary-subtle text-secondary';
    const lbl = (priority || '').charAt(0).toUpperCase() + (priority || '').slice(1);
    return `<span class="badge ${cls}">${lbl}</span>`;
  }

  /* ── Follow-up badge ─────────────────────────────────────────── */
  function followupBadge(state, escalation) {
    if (state === 'overdue') {
      const esc = escalation === 'strict' ? 'OVERDUE — STRICT' : escalation === 'medium' ? 'OVERDUE' : 'OVERDUE';
      return `<span class="badge bg-danger text-white"><i class="fi fi-rr-exclamation me-1"></i>${esc}</span>`;
    }
    if (state === 'pending') {
      return `<span class="badge bg-warning-subtle text-warning">Pending</span>`;
    }
    return `<span class="badge bg-success-subtle text-success">Done</span>`;
  }

  /* ── Escalation badge ────────────────────────────────────────── */
  const ESC_STYLE = { strict: 'bg-danger text-white', medium: 'bg-warning text-dark', soft: 'bg-secondary-subtle text-secondary' };
  function escalationBadge(level) {
    const cls = ESC_STYLE[level] || 'bg-secondary-subtle text-secondary';
    return `<span class="badge ${cls} text-capitalize">${level || '—'}</span>`;
  }

  /* ── Payment status badge ────────────────────────────────────── */
  const PAY_STYLE = {
    initiated:  'bg-info-subtle text-info',
    authorized: 'bg-primary-subtle text-primary',
    captured:   'bg-success-subtle text-success',
    settled:    'bg-success text-white',
    failed:     'bg-danger text-white',
    canceled:   'bg-secondary-subtle text-secondary',
    refunded:   'bg-warning-subtle text-warning',
    chargeback: 'border border-danger text-danger',
  };
  function paymentBadge(status) {
    const cls = PAY_STYLE[status] || 'bg-secondary-subtle text-secondary';
    const lbl = (status || '').charAt(0).toUpperCase() + (status || '').slice(1);
    return `<span class="badge ${cls}">${lbl}</span>`;
  }

  /* ── PKR formatter ───────────────────────────────────────────── */
  function pkr(amount) {
    if (amount == null) return '—';
    const n = Number(amount);
    if (n >= 10000000) return `PKR ${(n / 10000000).toFixed(2)} Cr`;
    if (n >= 100000)   return `PKR ${(n / 100000).toFixed(2)} L`;
    return `PKR ${n.toLocaleString('en-PK')}`;
  }

  /* ── Relative time ───────────────────────────────────────────── */
  function relativeTime(isoDate) {
    if (!isoDate) return '—';
    const diff = Date.now() - new Date(isoDate).getTime();
    const mins  = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days  = Math.floor(diff / 86400000);
    if (mins  < 1)   return 'just now';
    if (mins  < 60)  return `${mins}m ago`;
    if (hours < 24)  return `${hours}h ago`;
    if (days  < 30)  return `${days}d ago`;
    return new Date(isoDate).toLocaleDateString('en-PK', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  /* ── Due date cell (red when past) ──────────────────────────── */
  function dueCell(isoDate) {
    if (!isoDate) return '—';
    const past = new Date(isoDate) < new Date();
    const label = new Date(isoDate).toLocaleDateString('en-PK', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
    return past ? `<span class="text-danger fw-semibold">${label}</span>` : `<span>${label}</span>`;
  }

  /* ── Enforcement posture strip ───────────────────────────────── */
  function enforcementStrip(overdueCount, unassignedCount) {
    if (overdueCount === 0 && unassignedCount === 0) {
      return `<div class="alert alert-success d-flex align-items-center mb-3 py-2" role="alert">
        <i class="fi fi-rr-check-circle me-2"></i>
        <span>All follow-ups on track. No overdue or unassigned leads.</span>
      </div>`;
    }
    const parts = [];
    if (overdueCount > 0)    parts.push(`<strong>${overdueCount}</strong> overdue follow-up${overdueCount > 1 ? 's' : ''}`);
    if (unassignedCount > 0) parts.push(`<strong>${unassignedCount}</strong> unassigned lead${unassignedCount > 1 ? 's' : ''}`);
    const cls = overdueCount > 0 ? 'alert-danger' : 'alert-warning';
    return `<div class="alert ${cls} d-flex align-items-center justify-content-between mb-3 py-2" role="alert">
      <span><i class="fi fi-rr-exclamation me-2"></i>${parts.join(' &nbsp;·&nbsp; ')}</span>
      <a href="followups.html" class="btn btn-sm btn-danger">View Queue</a>
    </div>`;
  }

  /* ── Activity type icon ─────────────────────────────────────── */
  const ACT_ICON = {
    call:         'fi-rr-phone-call',
    email:        'fi-rr-envelope',
    whatsapp:     'fi-rr-comment-alt',
    meeting:      'fi-rr-calendar',
    note:         'fi-rr-note',
    stage_change: 'fi-rr-arrow-right',
    deal_won:     'fi-rr-trophy',
    deal_lost:    'fi-rr-times-circle',
  };
  function activityRow(act) {
    const icon  = ACT_ICON[act.activity_type] || 'fi-rr-dot-circle';
    const users = window.CRM_DUMMY ? window.CRM_DUMMY.userMap : {};
    const by    = users[act.performed_by] ? users[act.performed_by].display_name : act.performed_by;
    return `<li class="list-group-item d-flex align-items-center position-relative">
      <div class="avatar avatar-xs bg-primary-subtle text-primary rounded-circle me-1 flex-shrink-0">
        <i class="fi ${icon}"></i>
      </div>
      <div class="ms-2 me-auto">
        <p class="mb-0 small">${act.description}</p>
        <small class="text-muted d-block">${by}</small>
        <small class="text-muted position-absolute end-0 top-0 mt-2 me-3">${relativeTime(act.occurred_at)}</small>
      </div>
    </li>`;
  }

  /* ── Empty state ─────────────────────────────────────────────── */
  function emptyState(message) {
    return `<div class="text-center py-5 text-muted">
      <i class="fi fi-rr-inbox fs-1 d-block mb-2"></i>
      <p class="mb-0">${message || 'No records found'}</p>
    </div>`;
  }

  /* ── Error toast ─────────────────────────────────────────────── */
  function showError(msg) {
    const el = document.getElementById('crm-error-toast');
    if (el) {
      el.querySelector('.toast-body').textContent = msg;
      bootstrap.Toast.getOrCreateInstance(el).show();
    } else {
      console.error('[CRM]', msg);
    }
  }

  return { stageBadge, priorityBadge, followupBadge, escalationBadge, paymentBadge, pkr, relativeTime, dueCell, enforcementStrip, activityRow, emptyState, showError };
})();
