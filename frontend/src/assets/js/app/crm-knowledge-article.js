/* Pakistan CRM — Knowledge Article (C-12) */

(function () {
  'use strict';

  var cfg       = window.CRM_CONFIG;
  var _d        = window.CRM_DUMMY;
  var articleId = new URLSearchParams(window.location.search).get('id') || null;

  var STATUS_BADGE = {
    published:'<span class="badge bg-success-subtle text-success border border-success-subtle">Published</span>',
    draft:    '<span class="badge bg-secondary-subtle text-secondary">Draft</span>',
    archived: '<span class="badge bg-dark text-white">Archived</span>',
  };
  var CAT_BADGE = {
    billing:         '<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Billing</span>',
    technical:       '<span class="badge bg-danger-subtle text-danger border border-danger-subtle">Technical</span>',
    how_to:          '<span class="badge bg-info-subtle text-info border border-info-subtle">How-To</span>',
    getting_started: '<span class="badge bg-success-subtle text-success border border-success-subtle">Getting Started</span>',
  };

  var DEMO_CONTENT = '<h6>Overview</h6><p>This article explains how to set up WhatsApp integration with NexLink CRM for receiving and sending messages through your business WhatsApp number.</p><h6>Prerequisites</h6><ul><li>A verified WhatsApp Business account</li><li>API credentials from Meta, 360dialog, Gupshup, or Twilio</li><li>Tenant Admin or Integration Admin role in CRM</li></ul><h6>Steps</h6><ol><li>Navigate to <strong>Settings → Integrations</strong></li><li>Click <strong>WhatsApp</strong> and select your provider</li><li>Enter your API credentials</li><li>Click <strong>Test Connection</strong> to verify</li><li>Save — inbound messages will route to the Omnichannel Inbox</li></ol>';

  function render(article, allArticles, users) {
    if (!article) {
      if (_d && _d.knowledgeArticles && _d.knowledgeArticles.data[0]) {
        render(_d.knowledgeArticles.data[0], _d.knowledgeArticles.data, (_d.users && _d.users.data) || []);
      }
      return;
    }

    var author = users.filter(function (u) { return u.id === article.author_id; })[0] || { display_name: '—' };

    document.getElementById('bc-article-title').textContent = article.title;
    document.getElementById('article-title').textContent    = article.title;
    document.getElementById('status-badge').innerHTML       = STATUS_BADGE[article.status] || article.status;
    document.getElementById('category-badge').innerHTML     = CAT_BADGE[article.category] || article.category;
    var staleEl = document.getElementById('stale-badge');
    if (staleEl) staleEl.innerHTML = article.stale ? '<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Stale</span>' : '';
    document.getElementById('article-author').textContent   = author.display_name;
    document.getElementById('article-updated').textContent  = article.last_updated_at ? new Date(article.last_updated_at).toLocaleDateString('en-PK', { day:'2-digit', month:'short', year:'numeric' }) : '—';

    if (article.status === 'published') {
      var btnPub = document.getElementById('btn-publish');
      if (btnPub) btnPub.style.display = 'none';
    }
    if (article.status === 'archived') {
      var btnEdit = document.getElementById('btn-edit');
      if (btnEdit) btnEdit.style.display = 'none';
      var btnPub2 = document.getElementById('btn-publish');
      if (btnPub2) btnPub2.style.display = 'none';
    }

    document.getElementById('article-content').innerHTML = DEMO_CONTENT;

    var relEl = document.getElementById('related-articles');
    if (relEl) {
      var related = allArticles.filter(function (a) { return a.article_id !== article.article_id && a.status === 'published'; }).slice(0, 3);
      relEl.innerHTML = related.map(function (a) {
        return '<a href="app/knowledge-article.html?id=' + a.article_id + '" class="d-flex align-items-center gap-2 py-2 border-bottom text-decoration-none">' +
          '<i class="fi fi-rr-book-alt text-muted"></i>' +
          '<div class="flex-grow-1"><div class="fw-semibold small">' + a.title + '</div>' +
          '<div class="small text-muted">' + (a.view_count || 0) + ' views</div></div>' +
          (CAT_BADGE[a.category] || a.category) + '</a>';
      }).join('');
    }

    var statsEl = document.getElementById('context-stats');
    if (statsEl) {
      statsEl.innerHTML = '<dl class="row mb-0 small">' +
        '<dt class="col-7 text-muted">Total Views</dt><dd class="col-5 fw-semibold">' + (article.view_count || 0) + '</dd>' +
        '<dt class="col-7 text-muted">Deflections</dt><dd class="col-5 fw-semibold">' + (article.deflection_count || 0) + '</dd>' +
        '<dt class="col-7 text-muted">Status</dt><dd class="col-5">' + article.status + '</dd>' +
        '<dt class="col-7 text-muted">Category</dt><dd class="col-5">' + (article.category || '—') + '</dd></dl>';
    }

    /* Publish button → calls API */
    var btnPubAction = document.getElementById('btn-publish');
    if (btnPubAction) {
      btnPubAction.addEventListener('click', function () {
        if (cfg && !cfg.DUMMY_MODE) {
          window.CRM_API.knowledge.publish(article.article_id)
            .then(function () { location.reload(); })
            .catch(function () {});
        }
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (cfg && !cfg.DUMMY_MODE) {
      Promise.all([
        (articleId ? window.CRM_API.knowledge.get(articleId) : Promise.resolve({ data: null })).catch(function () { return { data: null }; }),
        window.CRM_API.knowledge.list({ limit: 50 }).catch(function () { return { data: [] }; }),
        window.CRM_API.users.list().catch(function () { return { data: [] }; })
      ]).then(function (results) {
        var art  = results[0].data || (results[1].data && results[1].data[0]);
        render(art, results[1].data || [], results[2].data || []);
      });
    } else {
      if (!_d) return;
      var arts = (_d.knowledgeArticles && _d.knowledgeArticles.data) || [];
      var art  = articleId ? (arts.filter(function (a) { return a.article_id === articleId; })[0] || arts[0]) : arts[0];
      render(art, arts, (_d.users && _d.users.data) || []);
    }
  });

})();
