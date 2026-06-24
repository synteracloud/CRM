/* Pakistan CRM — Shell Injector (header + sidebar, runs synchronously before main.js) */
/* Set window.CRM_PAGE before loading this script to control sidebar active state */
(function () {
  'use strict';

  const PAGE = window.CRM_PAGE || '';

  /* Active class helper */
  function a(pages) { return pages.includes(PAGE) ? ' active' : ''; }

  /* ── Sidebar — Pakistan CRM navigation ──────────────────────── */
  const SIDEBAR_HTML = `
<aside class="app-menubar-tabs" id="appMenubar">
  <div class="app-navbar-brand">
    <a class="navbar-brand-logo" href="app/dashboard.html">
      <img src="../assets/images/logo.svg" alt="Pakistan CRM">
    </a>
  </div>
  <div class="app-navbar-tabs" data-simplebar>
    <ul class="nav" id="appMenubarTabs" role="tablist" aria-orientation="vertical">
      <!-- Dashboard -->
      <li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Dashboards">
        <a class="menu-link${a(['dashboard','leads-dashboard','sales-dashboard','quotes-dashboard','subscriptions-dashboard','support-dashboard','engagement-dashboard','knowledge-dashboard','workflows-dashboard','tenants-dashboard','identity-dashboard','audit-dashboard','contacts-health']) ? ' active' : ''}" href="#crmDashboardTab" role="tab" data-bs-toggle="tab">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path opacity="0.5" d="M2 12.2039C2 9.91549 2 8.77128 2.5192 7.82274C3.0384 6.87421 3.98695 6.28551 5.88403 5.10813L7.88403 3.86687C9.88939 2.62229 10.8921 2 12 2C13.1079 2 14.1106 2.62229 16.116 3.86687L18.116 5.10812C20.0131 6.28551 20.9616 6.87421 21.4808 7.82274C22 8.77128 22 9.91549 22 12.2039V13.725C22 17.6258 22 19.5763 20.8284 20.7881C19.6569 22 17.7712 22 14 22H10C6.22876 22 4.34315 22 3.17157 20.7881C2 19.5763 2 17.6258 2 13.725V12.2039Z" stroke="var(--bs-heading-color)" stroke-width="2"/><path d="M12 15V18" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/></svg>
        </a>
      </li>
      <!-- Sales -->
      <li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Sales">
        <a class="menu-link${a(['leads','followups','contacts','accounts','sales-cockpit','collections','invoices','tasks','activity','activities','sales-analytics','lead-new','contact-new','opportunity-new','quote-builder','leads-detail','contacts-detail','accounts-detail','opportunities-detail','quotes-detail','orders-detail','invoices-detail']) ? ' active' : ''}" href="#crmSalesTab" role="tab" data-bs-toggle="tab">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M3 3H5L5.4 5M7 13H17L21 5H5.4M7 13L5.4 5M7 13L4.707 15.293C4.077 15.923 4.523 17 5.414 17H17M17 17C15.895 17 15 17.895 15 19C15 20.105 15.895 21 17 21C18.105 21 19 20.105 19 19C19 17.895 18.105 17 17 17ZM9 19C9 20.105 8.105 21 7 21C5.895 21 5 20.105 5 19C5 17.895 5.895 17 7 17C8.105 17 9 17.895 9 19Z" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </a>
      </li>
      <!-- Support -->
      <li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Support">
        <a class="menu-link${a(['cases','support-console','inbox','inbox-thread','knowledge-article','support-analytics','case-new']) ? ' active' : ''}" href="#crmSupportTab" role="tab" data-bs-toggle="tab">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="var(--bs-heading-color)" stroke-width="2"/><path opacity="0.5" d="M12 17V11" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/><path d="M12 8.00977V7" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/></svg>
        </a>
      </li>
      <!-- Finance -->
      <li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Finance">
        <a class="menu-link${a(['finance-analytics','collections','invoices','subscriptions-dashboard','subscriptions-detail','billing-settings']) ? ' active' : ''}" href="#crmFinanceTab" role="tab" data-bs-toggle="tab">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M3 10.417C3 8.27614 3 7.20571 3.41935 6.38448C3.78417 5.6658 4.36644 5.08353 5.08512 4.71871C5.90635 4.29936 6.97678 4.29936 9.11765 4.29936H14.8824C17.0232 4.29936 18.0937 4.29936 18.9149 4.71871C19.6336 5.08353 20.2158 5.6658 20.5807 6.38448C21 7.20571 21 8.27614 21 10.417V13.5824C21 15.7233 21 16.7937 20.5807 17.6149C20.2158 18.3336 19.6336 18.9159 18.9149 19.2807C18.0937 19.7 17.0232 19.7 14.8824 19.7H9.11765C6.97678 19.7 5.90635 19.7 5.08512 19.2807C4.36644 18.9159 3.78417 18.3336 3.41935 17.6149C3 16.7937 3 15.7233 3 13.5824V10.417Z" stroke="var(--bs-heading-color)" stroke-width="2"/><path opacity="0.5" d="M3 9H21" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/><path d="M7 15H9" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/><path opacity="0.5" d="M11 15H13" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/></svg>
        </a>
      </li>
      <!-- Marketing -->
      <li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Marketing">
        <a class="menu-link${a(['marketing-workspace','marketing-analytics','campaign-new','partners','partners-detail']) ? ' active' : ''}" href="#crmMarketingTab" role="tab" data-bs-toggle="tab">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M18.364 5.636A9 9 0 1 1 5.636 18.364 9 9 0 0 1 18.364 5.636" stroke="var(--bs-heading-color)" stroke-width="2"/><path opacity="0.5" d="M12 8V12L15 15" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/></svg>
        </a>
      </li>
      <!-- Workflows -->
      <li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Automation">
        <a class="menu-link${a(['workflows-dashboard','workflow-builder','workflow-run-detail','workflow-analytics','approval-lanes','rule-builder']) ? ' active' : ''}" href="#crmAutomationTab" role="tab" data-bs-toggle="tab">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21C16.9706 21 21 16.9706 21 12" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/><path opacity="0.5" d="M16 3.46609C16.3463 3.46609 16.6848 3.54545 17 3.67964V3.64645C17 3.64645 19 5 20.5 7C22 9 21.9999 12 21.9999 12" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/><path d="M12 8L12 12L15 15" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </a>
      </li>
      <li class="nav-item-hr"></li>
      <!-- Reports -->
      <li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Reports">
        <a class="menu-link${a(['sales-analytics','marketing-analytics','support-analytics','finance-analytics','workflow-analytics','audit-report','report-builder']) ? ' active' : ''}" href="#crmReportsTab" role="tab" data-bs-toggle="tab">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path opacity="0.5" d="M3 22H21" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/><path d="M3 11C3 10.0572 3 9.58579 3.29289 9.29289C3.58579 9 4.05719 9 5 9H7C7.94281 9 8.41421 9 8.70711 9.29289C9 9.58579 9 10.0572 9 11V17H3V11Z" stroke="var(--bs-heading-color)" stroke-width="2"/><path opacity="0.5" d="M10 7C10 6.05719 10 5.58579 10.2929 5.29289C10.5858 5 11.0572 5 12 5H12C12.9428 5 13.4142 5 13.7071 5.29289C14 5.58579 14 6.05719 14 7V17H10V7Z" stroke="var(--bs-heading-color)" stroke-width="2"/><path d="M15 13C15 12.0572 15 11.5858 15.2929 11.2929C15.5858 11 16.0572 11 17 11H19C19.9428 11 20.4142 11 20.7071 11.2929C21 11.5858 21 12.0572 21 13V17H15V13Z" stroke="var(--bs-heading-color)" stroke-width="2"/></svg>
        </a>
      </li>
      <!-- Admin -->
      <li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Admin">
        <a class="menu-link${a(['org-settings','user-management-crm','roles','territories','feature-flags','integrations','notifications','compliance','data-governance','rbac-audit','audit-log','compliance-report','privacy','object-builder','routing-config','users']) ? ' active' : ''}" href="#crmAdminTab" role="tab" data-bs-toggle="tab">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="var(--bs-heading-color)" stroke-width="2"/><path opacity="0.5" d="M12 6V3M12 21V18M6 12H3M21 12H18M7.75736 7.75736L5.63604 5.63604M18.364 18.364L16.2426 16.2426M16.2426 7.75736L18.364 5.63604M5.63604 18.364L7.75736 16.2426" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/></svg>
        </a>
      </li>
      <!-- AI -->
      <li class="nav-item" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="AI">
        <a class="menu-link${a(['ai-copilot','ai-insights']) ? ' active' : ''}" href="#crmAiTab" role="tab" data-bs-toggle="tab">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path opacity="0.5" d="M2 17L12 22L22 17" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path opacity="0.5" d="M2 12L12 17L22 12" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </a>
      </li>
      <li class="nav-item-hr"></li>
      <li class="nav-item mt-auto" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Log Out">
        <a href="javascript:void(0);" class="menu-link" id="crm-logout-btn">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path opacity="0.5" d="M9.00195 7C9.01406 4.82497 9.11051 3.64706 9.87889 2.87868C10.7576 2 12.1718 2 15.0002 2H16.0002C18.8286 2 20.2429 2 21.1215 2.87868C22.0002 3.75736 22.0002 5.17157 22.0002 8V16C22.0002 18.8284 22.0002 20.2426 21.1215 21.1213C20.2429 22 18.8286 22 16.0002 22H15.0002C12.1718 22 10.7576 22 9.87889 21.1213C9.11051 20.3529 9.01406 19.175 9.00195 17" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round"/><path d="M15 12H2M2 12L5.5 9M2 12L5.5 15" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </a>
      </li>
    </ul>
  </div>
  <div class="app-tab-content">
    <div class="app-side-brands">
      <a class="navbar-brand-text" href="app/dashboard.html">Pakistan CRM</a>
    </div>
    <div class="app-content-inner">
      <div class="tab-content" id="appMenubarTabsContent">

        <!-- ── Dashboards ── -->
        <div class="tab-pane fade show active" id="crmDashboardTab" role="tabpanel" tabindex="0">
          <nav class="app-navbar" data-simplebar>
            <ul class="side-menubar">
              <li class="menu-heading"><span class="menu-label">Dashboards</span></li>
              <li class="menu-item"><a class="menu-link${a(['dashboard'])}" href="app/dashboard.html"><i class="fi fi-rr-house-blank"></i><span class="menu-label">Main Dashboard</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['leads-dashboard'])}" href="app/leads-dashboard.html"><i class="fi fi-rr-funnel"></i><span class="menu-label">Lead Funnel</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['sales-dashboard'])}" href="app/sales-dashboard.html"><i class="fi fi-rr-chart-line-up"></i><span class="menu-label">Opportunity Pipeline</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['quotes-dashboard'])}" href="app/quotes-dashboard.html"><i class="fi fi-rr-file-invoice"></i><span class="menu-label">Quote Approval</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['subscriptions-dashboard'])}" href="app/subscriptions-dashboard.html"><i class="fi fi-rr-refresh"></i><span class="menu-label">Subscription Revenue</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['support-dashboard'])}" href="app/support-dashboard.html"><i class="fi fi-rr-headset"></i><span class="menu-label">Case SLA Ops</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['engagement-dashboard'])}" href="app/engagement-dashboard.html"><i class="fi fi-rr-signal-alt"></i><span class="menu-label">Engagement</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['knowledge-dashboard'])}" href="app/knowledge-dashboard.html"><i class="fi fi-rr-book-alt"></i><span class="menu-label">Knowledge</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['workflows-dashboard'])}" href="app/workflows-dashboard.html"><i class="fi fi-rr-workflow"></i><span class="menu-label">Workflows</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['audit-dashboard'])}" href="app/audit-dashboard.html"><i class="fi fi-rr-shield-check"></i><span class="menu-label">Audit &amp; Reliability</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['identity-dashboard'])}" href="app/identity-dashboard.html"><i class="fi fi-rr-id-badge"></i><span class="menu-label">Identity &amp; Access</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['tenants-dashboard'])}" href="app/tenants-dashboard.html"><i class="fi fi-rr-building"></i><span class="menu-label">Tenants</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['contacts-health'])}" href="app/contacts-health.html"><i class="fi fi-rr-heart-rate"></i><span class="menu-label">Customer Health</span></a></li>
            </ul>
          </nav>
        </div>

        <!-- ── Sales ── -->
        <div class="tab-pane fade" id="crmSalesTab" role="tabpanel" tabindex="0">
          <nav class="app-navbar" data-simplebar>
            <ul class="side-menubar">
              <li class="menu-heading"><span class="menu-label">Pipeline</span></li>
              <li class="menu-item"><a class="menu-link${a(['sales-cockpit'])}" href="app/sales-cockpit.html"><i class="fi fi-rr-rocket-lunch"></i><span class="menu-label">Sales Cockpit</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['leads'])}" href="app/leads.html"><i class="fi fi-rr-funnel"></i><span class="menu-label">Leads</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['followups'])}" href="app/followups.html"><i class="fi fi-rr-alarm-clock"></i><span class="menu-label">Follow-ups</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['contacts'])}" href="app/contacts.html"><i class="fi fi-rr-address-book"></i><span class="menu-label">Contacts</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['accounts'])}" href="app/accounts.html"><i class="fi fi-rr-building"></i><span class="menu-label">Accounts</span></a></li>
              <li><div class="menu-divider"></div></li>
              <li class="menu-heading"><span class="menu-label">Transactions</span></li>
              <li class="menu-item"><a class="menu-link${a(['collections'])}" href="app/collections.html"><i class="fi fi-rr-sack-dollar"></i><span class="menu-label">Collections</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['invoices'])}" href="app/invoices.html"><i class="fi fi-rr-file-invoice-dollar"></i><span class="menu-label">Invoices</span></a></li>
              <li><div class="menu-divider"></div></li>
              <li class="menu-heading"><span class="menu-label">Activity</span></li>
              <li class="menu-item"><a class="menu-link${a(['activity'])}" href="app/activity.html"><i class="fi fi-rr-pulse"></i><span class="menu-label">Activity Feed</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['tasks'])}" href="app/tasks.html"><i class="fi fi-rr-checkbox"></i><span class="menu-label">Tasks</span></a></li>
              <li><div class="menu-divider"></div></li>
              <li class="menu-heading"><span class="menu-label">Create New</span></li>
              <li class="menu-item"><a class="menu-link${a(['lead-new'])}" href="app/lead-new.html"><i class="fi fi-rr-user-add"></i><span class="menu-label">New Lead</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['contact-new'])}" href="app/contact-new.html"><i class="fi fi-rr-add-user"></i><span class="menu-label">New Contact</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['opportunity-new'])}" href="app/opportunity-new.html"><i class="fi fi-rr-badge-dollar"></i><span class="menu-label">New Opportunity</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['quote-builder'])}" href="app/quote-builder.html"><i class="fi fi-rr-calculator"></i><span class="menu-label">New Quote (CPQ)</span></a></li>
            </ul>
          </nav>
        </div>

        <!-- ── Support ── -->
        <div class="tab-pane fade" id="crmSupportTab" role="tabpanel" tabindex="0">
          <nav class="app-navbar" data-simplebar>
            <ul class="side-menubar">
              <li class="menu-heading"><span class="menu-label">Support</span></li>
              <li class="menu-item"><a class="menu-link${a(['support-console'])}" href="app/support-console.html"><i class="fi fi-rr-headset"></i><span class="menu-label">Support Console</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['cases'])}" href="app/cases.html"><i class="fi fi-rr-ticket"></i><span class="menu-label">Cases</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['case-new'])}" href="app/case-new.html"><i class="fi fi-rr-add"></i><span class="menu-label">New Case</span></a></li>
              <li><div class="menu-divider"></div></li>
              <li class="menu-heading"><span class="menu-label">Inbox</span></li>
              <li class="menu-item"><a class="menu-link${a(['inbox'])}" href="app/inbox.html"><i class="fi fi-rr-inbox-in"></i><span class="menu-label">Omnichannel Inbox</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['inbox-thread'])}" href="app/inbox-thread.html"><i class="fi fi-rr-comment-alt"></i><span class="menu-label">Conversation Thread</span></a></li>
              <li><div class="menu-divider"></div></li>
              <li class="menu-heading"><span class="menu-label">Knowledge</span></li>
              <li class="menu-item"><a class="menu-link${a(['knowledge-dashboard'])}" href="app/knowledge-dashboard.html"><i class="fi fi-rr-book-alt"></i><span class="menu-label">Knowledge Base</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['knowledge-article'])}" href="app/knowledge-article.html"><i class="fi fi-rr-document"></i><span class="menu-label">Article Detail</span></a></li>
              <li><div class="menu-divider"></div></li>
              <li class="menu-item"><a class="menu-link${a(['support-analytics'])}" href="app/support-analytics.html"><i class="fi fi-rr-chart-pie-alt"></i><span class="menu-label">Support Analytics</span></a></li>
            </ul>
          </nav>
        </div>

        <!-- ── Finance ── -->
        <div class="tab-pane fade" id="crmFinanceTab" role="tabpanel" tabindex="0">
          <nav class="app-navbar" data-simplebar>
            <ul class="side-menubar">
              <li class="menu-heading"><span class="menu-label">Finance</span></li>
              <li class="menu-item"><a class="menu-link${a(['finance-analytics'])}" href="app/finance-analytics.html"><i class="fi fi-rr-chart-line-up"></i><span class="menu-label">Finance Analytics</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['collections'])}" href="app/collections.html"><i class="fi fi-rr-sack-dollar"></i><span class="menu-label">Collections Queue</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['invoices'])}" href="app/invoices.html"><i class="fi fi-rr-file-invoice-dollar"></i><span class="menu-label">Invoice Queue</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['subscriptions-dashboard'])}" href="app/subscriptions-dashboard.html"><i class="fi fi-rr-refresh"></i><span class="menu-label">Subscriptions</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['billing-settings'])}" href="app/billing-settings.html"><i class="fi fi-rr-credit-card"></i><span class="menu-label">Billing Settings</span></a></li>
            </ul>
          </nav>
        </div>

        <!-- ── Marketing ── -->
        <div class="tab-pane fade" id="crmMarketingTab" role="tabpanel" tabindex="0">
          <nav class="app-navbar" data-simplebar>
            <ul class="side-menubar">
              <li class="menu-heading"><span class="menu-label">Marketing</span></li>
              <li class="menu-item"><a class="menu-link${a(['marketing-workspace'])}" href="app/marketing-workspace.html"><i class="fi fi-rr-megaphone"></i><span class="menu-label">Marketing Workspace</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['marketing-analytics'])}" href="app/marketing-analytics.html"><i class="fi fi-rr-chart-pie-alt"></i><span class="menu-label">Marketing Analytics</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['campaign-new'])}" href="app/campaign-new.html"><i class="fi fi-rr-add"></i><span class="menu-label">New Campaign</span></a></li>
              <li><div class="menu-divider"></div></li>
              <li class="menu-heading"><span class="menu-label">Partners</span></li>
              <li class="menu-item"><a class="menu-link${a(['partners'])}" href="app/partners.html"><i class="fi fi-rr-handshake"></i><span class="menu-label">Partners</span></a></li>
            </ul>
          </nav>
        </div>

        <!-- ── Automation ── -->
        <div class="tab-pane fade" id="crmAutomationTab" role="tabpanel" tabindex="0">
          <nav class="app-navbar" data-simplebar>
            <ul class="side-menubar">
              <li class="menu-heading"><span class="menu-label">Automation</span></li>
              <li class="menu-item"><a class="menu-link${a(['workflows-dashboard'])}" href="app/workflows-dashboard.html"><i class="fi fi-rr-workflow"></i><span class="menu-label">Workflows Dashboard</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['workflow-builder'])}" href="app/workflow-builder.html"><i class="fi fi-rr-diagram-project"></i><span class="menu-label">Workflow Builder</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['approval-lanes'])}" href="app/approval-lanes.html"><i class="fi fi-rr-columns-3"></i><span class="menu-label">Approval Lanes</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['rule-builder'])}" href="app/rule-builder.html"><i class="fi fi-rr-settings-sliders"></i><span class="menu-label">Rule Builder</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['workflow-analytics'])}" href="app/workflow-analytics.html"><i class="fi fi-rr-chart-line-up"></i><span class="menu-label">Workflow Analytics</span></a></li>
            </ul>
          </nav>
        </div>

        <!-- ── Reports ── -->
        <div class="tab-pane fade" id="crmReportsTab" role="tabpanel" tabindex="0">
          <nav class="app-navbar" data-simplebar>
            <ul class="side-menubar">
              <li class="menu-heading"><span class="menu-label">Analytics</span></li>
              <li class="menu-item"><a class="menu-link${a(['sales-analytics'])}" href="app/sales-analytics.html"><i class="fi fi-rr-chart-line-up"></i><span class="menu-label">Sales Analytics</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['marketing-analytics'])}" href="app/marketing-analytics.html"><i class="fi fi-rr-megaphone"></i><span class="menu-label">Marketing Analytics</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['support-analytics'])}" href="app/support-analytics.html"><i class="fi fi-rr-headset"></i><span class="menu-label">Support Analytics</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['finance-analytics'])}" href="app/finance-analytics.html"><i class="fi fi-rr-sack-dollar"></i><span class="menu-label">Finance Analytics</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['workflow-analytics'])}" href="app/workflow-analytics.html"><i class="fi fi-rr-workflow"></i><span class="menu-label">Workflow Analytics</span></a></li>
              <li><div class="menu-divider"></div></li>
              <li class="menu-heading"><span class="menu-label">Audit &amp; Compliance</span></li>
              <li class="menu-item"><a class="menu-link${a(['audit-report'])}" href="app/audit-report.html"><i class="fi fi-rr-shield-check"></i><span class="menu-label">Audit Report</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['report-builder'])}" href="app/report-builder.html"><i class="fi fi-rr-chart-histogram"></i><span class="menu-label">Custom Report Builder</span></a></li>
            </ul>
          </nav>
        </div>

        <!-- ── Admin ── -->
        <div class="tab-pane fade" id="crmAdminTab" role="tabpanel" tabindex="0">
          <nav class="app-navbar" data-simplebar>
            <ul class="side-menubar">
              <li class="menu-heading"><span class="menu-label">Settings</span></li>
              <li class="menu-item"><a class="menu-link${a(['org-settings'])}" href="app/org-settings.html"><i class="fi fi-rr-building"></i><span class="menu-label">Organisation</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['user-management-crm'])}" href="app/user-management-crm.html"><i class="fi fi-rr-users"></i><span class="menu-label">User Management</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['roles'])}" href="app/roles.html"><i class="fi fi-rr-lock"></i><span class="menu-label">Roles &amp; Permissions</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['territories'])}" href="app/territories.html"><i class="fi fi-rr-map-marker"></i><span class="menu-label">Territories</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['integrations'])}" href="app/integrations.html"><i class="fi fi-rr-plug"></i><span class="menu-label">Integrations</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['notifications'])}" href="app/notifications.html"><i class="fi fi-rr-bell"></i><span class="menu-label">Notifications</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['feature-flags'])}" href="app/feature-flags.html"><i class="fi fi-rr-flag"></i><span class="menu-label">Feature Flags</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['routing-config'])}" href="app/routing-config.html"><i class="fi fi-rr-route"></i><span class="menu-label">Routing Config</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['object-builder'])}" href="app/object-builder.html"><i class="fi fi-rr-cube"></i><span class="menu-label">Object Builder</span></a></li>
              <li><div class="menu-divider"></div></li>
              <li class="menu-heading"><span class="menu-label">Compliance</span></li>
              <li class="menu-item"><a class="menu-link${a(['audit-log'])}" href="app/audit-log.html"><i class="fi fi-rr-list-check"></i><span class="menu-label">Audit Log</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['compliance'])}" href="app/compliance.html"><i class="fi fi-rr-shield-check"></i><span class="menu-label">Compliance Settings</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['compliance-report'])}" href="app/compliance-report.html"><i class="fi fi-rr-document"></i><span class="menu-label">Compliance Report</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['data-governance'])}" href="app/data-governance.html"><i class="fi fi-rr-database"></i><span class="menu-label">Data Governance</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['rbac-audit'])}" href="app/rbac-audit.html"><i class="fi fi-rr-user-lock"></i><span class="menu-label">RBAC Audit</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['privacy'])}" href="app/privacy.html"><i class="fi fi-rr-privacy-policy"></i><span class="menu-label">Privacy &amp; Consent</span></a></li>
            </ul>
          </nav>
        </div>

        <!-- ── AI ── -->
        <div class="tab-pane fade" id="crmAiTab" role="tabpanel" tabindex="0">
          <nav class="app-navbar" data-simplebar>
            <ul class="side-menubar">
              <li class="menu-heading"><span class="menu-label">AI Tools</span></li>
              <li class="menu-item"><a class="menu-link${a(['ai-copilot'])}" href="app/ai-copilot.html"><i class="fi fi-rr-robot"></i><span class="menu-label">AI Copilot</span></a></li>
              <li class="menu-item"><a class="menu-link${a(['ai-insights'])}" href="app/ai-insights.html"><i class="fi fi-rr-brain"></i><span class="menu-label">AI Insights</span></a></li>
            </ul>
          </nav>
        </div>

      </div>
    </div>
  </div>
</aside>`;

  /* ── Header ──────────────────────────────────────────────────── */
  const user = (window.CRM_DUMMY && window.CRM_DUMMY.users.data[0]) || { display_name: 'Ahmed Raza', email: 'ahmed@crm.pk' };
  const HEADER_HTML = `
<header class="app-header">
  <div class="app-header-inner">
    <button class="app-toggler" type="button" aria-label="app toggler">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M7.66699 12.6668L3.66699 8.00016L7.66699 3.3335" stroke="#1C274C" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" />
        <path opacity="0.5" d="M12.667 12.6668L8.66699 8.00016L12.667 3.3335" stroke="#1C274C" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>
    <div class="app-header-start d-none d-md-flex">
      <form class="d-flex align-items-center h-100 w-lg-250px w-xxl-300px position-relative" action="#">
        <button type="button" class="btn btn-sm border-0 position-absolute start-0 ms-3 p-0"><i class="fi fi-rr-search"></i></button>
        <input type="text" class="form-control form-control-fill ps-5" placeholder="Search anything's" data-bs-toggle="modal" data-bs-target="#searchResultsModal">
      </form>
      <div class="badge-standard d-none d-lg-inline-block">
        Today New Leads <span class="badge bg-primary-subtle text-primary" id="header-today-leads">—</span>
      </div>
    </div>
    <div class="app-header-end">
      <div class="px-lg-4 px-2 ps-0 d-flex align-items-center">
        <a href="javascript:void(0);" class="theme-btn">
          <svg class="icon-light" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14.1663 10.5002C14.1663 12.8013 12.3008 14.6668 9.99967 14.6668C7.69849 14.6668 5.83301 12.8013 5.83301 10.5002C5.83301 8.19898 7.69849 6.3335 9.99967 6.3335C12.3008 6.3335 14.1663 8.19898 14.1663 10.5002Z" fill="var(--bs-heading-color)" /><path fill-rule="evenodd" clip-rule="evenodd" d="M10.0003 1.5415C10.3455 1.5415 10.6253 1.82133 10.6253 2.1665V3.83317C10.6253 4.17834 10.3455 4.45817 10.0003 4.45817C9.65516 4.45817 9.37532 4.17834 9.37532 3.83317V2.1665C9.37532 1.82133 9.65516 1.5415 10.0003 1.5415ZM1.04199 10.4998C1.04199 10.1547 1.32182 9.87484 1.66699 9.87484H3.33366C3.67883 9.87484 3.95866 10.1547 3.95866 10.4998C3.95866 10.845 3.67883 11.1248 3.33366 11.1248H1.66699C1.32182 11.1248 1.04199 10.845 1.04199 10.4998ZM16.042 10.4998C16.042 10.1547 16.3218 9.87484 16.667 9.87484H18.3337C18.6788 9.87484 18.9587 10.1547 18.9587 10.4998C18.9587 10.845 18.6788 11.1248 18.3337 11.1248H16.667C16.3218 11.1248 16.042 10.845 16.042 10.4998ZM10.0003 16.5415C10.3455 16.5415 10.6253 16.8213 10.6253 17.1665V18.8332C10.6253 19.1783 10.3455 19.4582 10.0003 19.4582C9.65516 19.4582 9.37532 19.1783 9.37532 18.8332V17.1665C9.37532 16.8213 9.65516 16.5415 10.0003 16.5415Z" fill="var(--bs-heading-color)" /><g opacity="0.5"><path d="M3.05729 3.59633C3.29021 3.34158 3.68554 3.32389 3.94029 3.55681L5.79198 5.24979C6.04673 5.48271 6.06442 5.87804 5.8315 6.13279C5.59858 6.38754 5.20325 6.40524 4.94851 6.17232L3.09683 4.47933C2.84208 4.24642 2.82438 3.85108 3.05729 3.59633Z" fill="var(--bs-heading-color)" /><path d="M16.9428 3.59633C17.1758 3.85108 17.1581 4.24642 16.9033 4.47933L15.0516 6.17232C14.7968 6.40524 14.4015 6.38754 14.1686 6.13279C13.9357 5.87804 13.9534 5.48271 14.2082 5.24979L16.0598 3.55681C16.3146 3.32389 16.7099 3.34158 16.9428 3.59633Z" fill="var(--bs-heading-color)" /><path d="M14.188 14.6874C14.4321 14.4433 14.8277 14.4434 15.0718 14.6875L16.9235 16.5394C17.1676 16.7835 17.1676 17.1792 16.9235 17.4232C16.6794 17.6673 16.2837 17.6673 16.0396 17.4232L14.1879 15.5713C13.9438 15.3272 13.9439 14.9315 14.188 14.6874Z" fill="var(--bs-heading-color)" /><path d="M5.81235 14.6875C6.05643 14.9315 6.05643 15.3272 5.81235 15.5713L3.9605 17.4231C3.71642 17.6672 3.32069 17.6672 3.07662 17.4231C2.83253 17.179 2.83253 16.7834 3.07662 16.5393L4.92847 14.6874C5.17254 14.4434 5.56828 14.4434 5.81235 14.6875Z" fill="var(--bs-heading-color)" /></g></svg>
          <div class="theme-toggle"></div>
          <svg class="icon-dark" width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M16.5835 2.4225C16.4495 2.08117 15.9681 2.08117 15.834 2.4225L15.4754 3.33523C15.4345 3.43944 15.3523 3.52193 15.2485 3.56303L14.339 3.92301C13.999 4.05762 13.999 4.54067 14.339 4.67529L15.2485 5.03527C15.3523 5.07637 15.4345 5.15886 15.4754 5.26306L15.834 6.1758C15.9681 6.51712 16.4495 6.51712 16.5835 6.17581L16.9422 5.26306C16.9831 5.15886 17.0653 5.07637 17.1691 5.03527L18.0785 4.67529C18.4186 4.54067 18.4186 4.05762 18.0785 3.92301L17.1691 3.56303C17.0653 3.52193 16.9831 3.43944 16.9422 3.33523L16.5835 2.4225Z" fill="var(--bs-heading-color)" /><path d="M13.3609 7.27454C13.2267 6.93323 12.7455 6.93323 12.6113 7.27454L12.4806 7.60733C12.4396 7.71154 12.3575 7.79403 12.2536 7.83513L11.9221 7.96638C11.582 8.10099 11.582 8.58404 11.9221 8.71866L12.2536 8.8499C12.3575 8.89098 12.4396 8.97348 12.4806 9.07773L12.6113 9.41048C12.7455 9.75182 13.2267 9.75182 13.3609 9.41048L13.4916 9.07773C13.5326 8.97348 13.6147 8.89098 13.7186 8.8499L14.0501 8.71866C14.3902 8.58404 14.3902 8.10099 14.0501 7.96638L13.7186 7.83513C13.6147 7.79403 13.5326 7.71154 13.4916 7.60733L13.3609 7.27454Z" fill="var(--bs-heading-color)" /><path opacity="0.5" d="M10.0003 18.8332C14.6027 18.8332 18.3337 15.1022 18.3337 10.4998C18.3337 10.1143 17.7557 10.0505 17.5563 10.3805C16.6077 11.9503 14.8849 12.9998 12.917 12.9998C9.92541 12.9998 7.50032 10.5748 7.50032 7.58317C7.50032 5.61521 8.54982 3.89238 10.1197 2.9438C10.4497 2.7444 10.3859 2.1665 10.0003 2.1665C5.39795 2.1665 1.66699 5.89746 1.66699 10.4998C1.66699 15.1022 5.39795 18.8332 10.0003 18.8332Z" fill="var(--bs-heading-color)" /></svg>
        </a>
      </div>
      <div class="vr my-3"></div>
      <div class="d-flex align-items-center gap-sm-2 gap-0 px-lg-4 px-sm-2 px-1">
        <a href="app/inbox-email.html" class="btn btn-icon btn-action-gray rounded-circle waves-effect waves-light position-relative">
          <svg width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg"><path opacity="0.5" d="M22 11V12.5C22 17.214 22 19.5711 20.5355 21.0355C19.0711 22.5 16.714 22.5 12 22.5C7.28595 22.5 4.92893 22.5 3.46447 21.0355C2 19.5711 2 17.214 2 12.5C2 7.78595 2 5.42893 3.46447 3.96447C4.92893 2.5 7.28595 2.5 12 2.5H13.5" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" /><path d="M19 8.5C20.6569 8.5 22 7.15685 22 5.5C22 3.84315 20.6569 2.5 19 2.5C17.3431 2.5 16 3.84315 16 5.5C16 7.15685 17.3431 8.5 19 8.5Z" stroke="var(--bs-heading-color)" stroke-width="2" /><path d="M7 14.5H16" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" /><path d="M7 18H13" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" /></svg>
          <span class="position-absolute top-0 end-0 p-1 mt-1 me-1 bg-primary border border-3 border-light rounded-circle"><span class="visually-hidden">New alerts</span></span>
        </a>
        <div class="dropdown text-end">
          <button type="button" class="btn btn-icon btn-action-gray rounded-circle waves-effect waves-light" data-bs-toggle="dropdown" data-bs-auto-close="outside" aria-expanded="false">
            <svg width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18.7491 10.2096V9.50497C18.7491 5.63623 15.7274 2.5 12 2.5C8.27256 2.5 5.25087 5.63623 5.25087 9.50497V10.2096C5.25087 11.0552 5.00972 11.8818 4.5578 12.5854L3.45036 14.3095C2.43882 15.8843 3.21105 18.0249 4.97036 18.5229C9.57274 19.8257 14.4273 19.8257 19.0296 18.5229C20.789 18.0249 21.5612 15.8843 20.5496 14.3095L19.4422 12.5854C18.9903 11.8818 18.7491 11.0552 18.7491 10.2096Z" stroke="var(--bs-heading-color)" stroke-width="2" /><path opacity="0.5" d="M7.5 19.5C8.15503 21.2478 9.92246 22.5 12 22.5C14.0775 22.5 15.845 21.2478 16.5 19.5" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" /><path opacity="0.5" d="M12 6.5V10.5" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" /></svg>
          </button>
          <div class="dropdown-menu dropdown-menu-lg-end p-0 w-300px mt-2">
            <div class="px-3 py-3 border-bottom d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Notifications <span class="badge badge-sm rounded-pill bg-primary ms-2">9</span></h6>
              <i class="bi bi-x-lg cursor-pointer"></i>
            </div>
            <div class="p-2" style="height: 300px;" data-simplebar>
              <ul class="list-group list-group-hover list-group-smooth list-group-unlined">
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <div class="avatar avatar-xs avatar-status-success rounded-circle me-1">
                    <img src="../assets/images/avatar/avatar2.webp" alt="">
                  </div>
                  <div class="ms-2 me-auto">
                    <h6 class="mb-0">Emma Smith</h6>
                    <small class="text-body d-block">Need to update the details.</small>
                    <small class="text-muted position-absolute end-0 top-0 mt-2 me-3">7 hr ago</small>
                  </div>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <div class="avatar avatar-xs bg-success rounded-circle text-white">D</div>
                  <div class="ms-2 me-auto">
                    <h6 class="mb-0">Design Team</h6>
                    <small class="text-body d-block">Check your shared folder.</small>
                    <small class="text-muted position-absolute end-0 top-0 mt-2 me-3">6 hr ago</small>
                  </div>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <div class="avatar avatar-xs bg-dark rounded-circle text-white">
                    <i class="fi fi-rr-lock"></i>
                  </div>
                  <div class="ms-2 me-auto">
                    <h6 class="mb-0">Security Update</h6>
                    <small class="text-body d-block">Password successfully set.</small>
                    <small class="text-muted position-absolute end-0 top-0 mt-2 me-3">5 hr ago</small>
                  </div>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <div class="avatar avatar-xs bg-info rounded-circle text-white">
                    <i class="fi fi-rr-shopping-cart"></i>
                  </div>
                  <div class="ms-2 me-auto">
                    <h6 class="mb-0">Invoice #1432</h6>
                    <small class="text-body d-block">has been paid Amount: $899.00</small>
                    <small class="text-muted position-absolute end-0 top-0 mt-2 me-3">5 hr ago</small>
                  </div>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <div class="avatar avatar-xs bg-danger rounded-circle text-white">R</div>
                  <div class="ms-2 me-auto">
                    <h6 class="mb-0">Emma Smith</h6>
                    <small class="text-body d-block">added you to Dashboard Analytics</small>
                    <small class="text-muted position-absolute end-0 top-0 mt-2 me-3">5 hr ago</small>
                  </div>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <div class="avatar avatar-xs avatar-status-success rounded-circle me-1">
                    <img src="../assets/images/avatar/avatar3.webp" alt="">
                  </div>
                  <div class="ms-2 me-auto">
                    <h6 class="mb-0">Olivia Clark</h6>
                    <small class="text-body d-block">You can now view the "Report".</small>
                    <small class="text-muted position-absolute end-0 top-0 mt-2 me-3">4 hr ago</small>
                  </div>
                </li>
                <li class="list-group-item d-flex justify-content-between align-items-center">
                  <div class="avatar avatar-xs avatar-status-danger rounded-circle me-1">
                    <img src="../assets/images/avatar/avatar5.webp" alt="">
                  </div>
                  <div class="ms-2 me-auto">
                    <h6 class="mb-0">Isabella Walker</h6>
                    <small class="text-body d-block">@Isabella please review.</small>
                    <small class="text-muted position-absolute end-0 top-0 mt-2 me-3">2 hr ago</small>
                  </div>
                </li>
              </ul>
            </div>
            <div class="p-2">
              <a href="javascript:void(0);" class="btn w-100 btn-primary waves-effect waves-light">View all notifications</a>
            </div>
          </div>
        </div>
        <a href="../calendar.html" class="btn btn-icon btn-action-gray rounded-circle waves-effect waves-light">
          <svg width="24" height="25" viewBox="0 0 24 25" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 12.5C2 8.72876 2 6.84315 3.17157 5.67157C4.34315 4.5 6.22876 4.5 10 4.5H14C17.7712 4.5 19.6569 4.5 20.8284 5.67157C22 6.84315 22 8.72876 22 12.5V14.5C22 18.2712 22 20.1569 20.8284 21.3284C19.6569 22.5 17.7712 22.5 14 22.5H10C6.22876 22.5 4.34315 22.5 3.17157 21.3284C2 20.1569 2 18.2712 2 14.5V12.5Z" stroke="var(--bs-heading-color)" stroke-width="2" /><path opacity="0.5" d="M7 4.5V3" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" /><path opacity="0.5" d="M17 4.5V3" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" /><path opacity="0.5" d="M2.5 9.5H21.5" stroke="var(--bs-heading-color)" stroke-width="2" stroke-linecap="round" /><path d="M18 17.5C18 18.0523 17.5523 18.5 17 18.5C16.4477 18.5 16 18.0523 16 17.5C16 16.9477 16.4477 16.5 17 16.5C17.5523 16.5 18 16.9477 18 17.5Z" fill="var(--bs-heading-color)" /><path d="M18 13.5C18 14.0523 17.5523 14.5 17 14.5C16.4477 14.5 16 14.0523 16 13.5C16 12.9477 16.4477 12.5 17 12.5C17.5523 12.5 18 12.9477 18 13.5Z" fill="var(--bs-heading-color)" /><path d="M13 17.5C13 18.0523 12.5523 18.5 12 18.5C11.4477 18.5 11 18.0523 11 17.5C11 16.9477 11.4477 16.5 12 16.5C12.5523 16.5 13 16.9477 13 17.5Z" fill="var(--bs-heading-color)" /><path d="M13 13.5C13 14.0523 12.5523 14.5 12 14.5C11.4477 14.5 11 14.0523 11 13.5C11 12.9477 11.4477 12.5 12 12.5C12.5523 12.5 13 12.9477 13 13.5Z" fill="var(--bs-heading-color)" /><path d="M8 17.5C8 18.0523 7.55228 18.5 7 18.5C6.44772 18.5 6 18.0523 6 17.5C6 16.9477 6.44772 16.5 7 16.5C7.55228 16.5 8 16.9477 8 17.5Z" fill="var(--bs-heading-color)" /><path d="M8 13.5C8 14.0523 7.55228 14.5 7 14.5C6.44772 14.5 6 14.0523 6 13.5C6 12.9477 6.44772 12.5 7 12.5C7.55228 12.5 8 12.9477 8 13.5Z" fill="var(--bs-heading-color)" /></svg>
        </a>
      </div>
      <div class="vr my-3"></div>
      <div class="dropdown text-end ms-sm-3 ms-2 ms-lg-4">
        <a href="#" class="d-flex align-items-center py-2" data-bs-toggle="dropdown" data-bs-auto-close="outside">
          <div class="text-end me-2 d-none d-lg-inline-block">
            <div class="fw-bold text-dark" id="header-user-name">${user.display_name}</div>
            <small class="text-body d-block lh-sm"><i class="fi fi-rr-angle-down text-3xs me-1"></i> Manager</small>
          </div>
          <div class="avatar avatar-sm rounded-circle avatar-status-success">
            <img src="../assets/images/avatar/avatar1.webp" alt="">
          </div>
        </a>
        <ul class="dropdown-menu dropdown-menu-end w-225px mt-1">
          <li class="d-flex align-items-center p-2">
            <div class="avatar avatar-sm rounded-circle"><img src="../assets/images/avatar/avatar1.webp" alt=""></div>
            <div class="ms-2">
              <div class="fw-bold text-dark" id="header-user-name2">${user.display_name}</div>
              <small class="text-body d-block lh-sm" id="header-user-email">${user.email}</small>
            </div>
          </li>
          <li><div class="dropdown-divider my-1"></div></li>
          <li><a class="dropdown-item d-flex align-items-center gap-2" href="app/profile.html"><i class="fi fi-rr-user scale-1x"></i> View Profile</a></li>
          <li><a class="dropdown-item d-flex align-items-center gap-2" href="app/task-management.html"><i class="fi fi-rr-note scale-1x"></i> My Task</a></li>
          <li><a class="dropdown-item d-flex align-items-center gap-2" href="app/settings.html"><i class="fi fi-rr-settings scale-1x"></i> Account Settings</a></li>
          <li><a class="dropdown-item d-flex align-items-center gap-2" href="../pages/pricing.html"><i class="fi fi-rr-usd-circle scale-1x"></i> Upgrade Plan</a></li>
          <li><div class="dropdown-divider my-1"></div></li>
          <li><a class="dropdown-item d-flex align-items-center gap-2 text-danger" href="app/login-frame.html"><i class="fi fi-sr-exit scale-1x"></i> Log Out</a></li>
        </ul>
      </div>
    </div>
  </div>
</header>`;

  /* ── Add Customer modal — exact replica of seed ──────────────── */
  const MODAL_HTML = `
<div class="modal fade" id="addCustomerModal" tabindex="-1" aria-labelledby="addCustomerModal" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">New Customer</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <form class="row">
          <div class="col-lg-6 mb-3"><label class="form-label">Customer Name</label><input type="text" class="form-control" placeholder="Enter full name"></div>
          <div class="col-lg-6 mb-3"><label class="form-label">Email Address</label><input type="text" class="form-control" placeholder="Enter email"></div>
          <div class="col-lg-6 mb-3"><label class="form-label">Phone Number</label><input type="text" class="form-control" placeholder="e.g. +1 234 567 8900"></div>
          <div class="col-lg-6 mb-3"><label class="form-label">Company</label><input type="text" class="form-control" placeholder="Company name"></div>
          <div class="col-lg-6 mb-3">
            <label class="form-label">Country</label>
            <select class="form-select"><option value="">Select country</option><option value="US">United States</option><option value="UK">United Kingdom</option><option value="IN">India</option><option value="CA">Canada</option><option value="DE">Germany</option><option value="FR">France</option><option value="JP">Japan</option><option value="BR">Brazil</option><option value="EG">Egypt</option></select>
          </div>
          <div class="col-lg-6 mb-3">
            <label class="form-label">Customer Type</label>
            <select class="form-select"><option value="">Select type</option><option value="Lead">Lead</option><option value="Prospect">Prospect</option><option value="Client">Client</option></select>
          </div>
          <div class="col-lg-6 mb-3">
            <label class="form-label">Account Status</label>
            <select class="form-select"><option value="">Select status</option><option value="Active">Active</option><option value="Inactive">Inactive</option><option value="Blocked">Blocked</option></select>
          </div>
          <div class="col-lg-6 mb-3"><label class="form-label">Joined Date</label><input type="text" class="form-control flatpickr-date" readonly="readonly"></div>
        </form>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-primary ms-2">Add Customer</button>
      </div>
    </div>
  </div>
</div>
<div class="position-fixed bottom-0 end-0 p-3" style="z-index:9999">
  <div id="crm-error-toast" class="toast align-items-center text-bg-danger border-0" role="alert">
    <div class="d-flex">
      <div class="toast-body">An error occurred.</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  </div>
</div>`;

  const FOOTER_HTML = `
  <footer class="footer-wrapper bg-body">
    <div class="container-fluid">
      <div class="row g-2">
        <div class="col-lg-6 col-md-7 text-center text-md-start">
          <p class="mb-0">&copy; <span class="currentYear">${new Date().getFullYear()}</span> NexLink. Proudly powered by <a href="javascript:void(0);">LayoutDrop</a>.</p>
        </div>
        <div class="col-lg-6 col-md-5">
          <ul class="d-flex list-inline mb-0 gap-3 flex-wrap justify-content-center justify-content-md-end">
            <li><a class="text-body" href="app/dashboard.html">Home</a></li>
            <li><a class="text-body" href="javascript:void(0);">Faq's</a></li>
            <li><a class="text-body" href="javascript:void(0);">Support</a></li>
          </ul>
        </div>
      </div>
    </div>
  </footer>`;

  /* ── Inject into DOM ─────────────────────────────────────────── */
  const layout = document.querySelector('.page-layout');
  if (layout) {
    const main = layout.querySelector('main.app-wrapper');
    if (main) {
      main.insertAdjacentHTML('beforebegin', HEADER_HTML + SIDEBAR_HTML + MODAL_HTML);
      main.insertAdjacentHTML('afterend', FOOTER_HTML);
    }
  }

  /* ── Post-injection: update live header counts + activate correct sidebar tab ── */
  document.addEventListener('DOMContentLoaded', function () {
    if (window.CRM_DUMMY) {
      const todayBadge = document.getElementById('header-today-leads');
      if (todayBadge) todayBadge.textContent = window.CRM_DUMMY.todayLeads.length;
    }
    /* GAP-005: activate appsTab for Apps-panel pages so the correct sidebar panel shows */
    const appsTabPages = ['chat', 'calendar', 'inbox', 'compose', 'read-email'];
    if (appsTabPages.includes(PAGE)) {
      const appsTabEl = document.querySelector('[href="#appsTab"][data-bs-toggle="tab"]');
      if (appsTabEl) new bootstrap.Tab(appsTabEl).show();
    }
  });
})();
