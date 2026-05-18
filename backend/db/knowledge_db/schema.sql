-- KNOWLEDGE_DB
-- Knowledge base articles, versions, categories, and feedback.
-- Source: src/knowledge_base/entities.py
--
-- Article categories: getting_started | billing | integrations |
--                     troubleshooting | security | account_management
-- Article status: draft | published | archived

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS knowledge_db;
SET search_path TO knowledge_db, public;

CREATE OR REPLACE FUNCTION knowledge_db.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TABLE IF NOT EXISTS tenant_ref (
  tenant_id  UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Knowledge Articles ─────────────────────────────────────────────────────────
-- Source: src/knowledge_base/entities.py KnowledgeArticle
CREATE TABLE IF NOT EXISTS knowledge_articles (
  knowledge_article_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id             UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  title                 TEXT NOT NULL,
  slug                  TEXT NOT NULL,                  -- URL-safe identifier
  body_markdown         TEXT NOT NULL DEFAULT '',
  status                TEXT NOT NULL DEFAULT 'draft',
  version               INTEGER NOT NULL DEFAULT 1,
  published_at          TIMESTAMPTZ,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT article_status_chk CHECK (status IN ('draft', 'published', 'archived')),
  UNIQUE (tenant_id, slug)
);
CREATE TRIGGER trg_knowledge_articles_updated_at BEFORE UPDATE ON knowledge_articles
  FOR EACH ROW EXECUTE FUNCTION knowledge_db.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_knowledge_articles_tenant_status  ON knowledge_articles(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_knowledge_articles_tenant_updated ON knowledge_articles(tenant_id, updated_at DESC);

-- ── Article Versions (immutable snapshot per publish) ─────────────────────────
CREATE TABLE IF NOT EXISTS article_versions (
  version_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_article_id  UUID NOT NULL REFERENCES knowledge_articles(knowledge_article_id) ON DELETE CASCADE,
  tenant_id             UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  version               INTEGER NOT NULL,
  title                 TEXT NOT NULL,
  body_markdown         TEXT NOT NULL,
  published_by          UUID,                           -- user_id; NULL = system
  published_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (knowledge_article_id, version)
);
CREATE INDEX IF NOT EXISTS idx_article_versions_article ON article_versions(knowledge_article_id, version DESC);

-- ── Article Categories ─────────────────────────────────────────────────────────
-- Source: src/knowledge_base/entities.py ARTICLE_CATEGORIES
-- Many-to-many: an article may belong to multiple categories.
CREATE TABLE IF NOT EXISTS article_categories (
  category_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_article_id  UUID NOT NULL REFERENCES knowledge_articles(knowledge_article_id) ON DELETE CASCADE,
  tenant_id             UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  category              TEXT NOT NULL,
  assigned_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT article_category_chk CHECK (category IN (
    'getting_started', 'billing', 'integrations',
    'troubleshooting', 'security', 'account_management'
  )),
  UNIQUE (knowledge_article_id, category)
);
CREATE INDEX IF NOT EXISTS idx_article_categories_tenant_cat ON article_categories(tenant_id, category);

-- ── Article Feedback ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS article_feedback (
  feedback_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_article_id  UUID NOT NULL REFERENCES knowledge_articles(knowledge_article_id) ON DELETE CASCADE,
  tenant_id             UUID NOT NULL REFERENCES tenant_ref(tenant_id) ON DELETE RESTRICT,
  user_id               UUID,                           -- NULL = anonymous
  helpful               BOOLEAN NOT NULL,               -- thumbs up/down
  comment               TEXT,
  submitted_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_article_feedback_article ON article_feedback(knowledge_article_id, submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_article_feedback_tenant  ON article_feedback(tenant_id, helpful);
