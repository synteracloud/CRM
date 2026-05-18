from __future__ import annotations

import unittest

from src.knowledge_base import KnowledgeArticle, KnowledgeBaseService
from src.knowledge_base.entities import ArticleStateError


class KnowledgeBaseServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = KnowledgeBaseService()

    def test_rejects_duplicate_content_per_tenant(self) -> None:
        base = KnowledgeArticle(
            knowledge_article_id="ka-1",
            tenant_id="tenant-1",
            title="Reset MFA",
            slug="reset-mfa",
            body_markdown="Steps to reset MFA in your profile.",
            status="published",
            version=1,
            published_at="2026-03-26T00:00:00Z",
            updated_at="2026-03-26T00:00:00Z",
            categories=("security",),
        )
        self.service.create_article(base)

        duplicate = KnowledgeArticle(
            knowledge_article_id="ka-2",
            tenant_id="tenant-1",
            title="reset mfa",
            slug="reset-mfa-copy",
            body_markdown="Steps   to reset MFA in your profile.",
            status="published",
            version=1,
            published_at="2026-03-26T01:00:00Z",
            updated_at="2026-03-26T01:00:00Z",
            categories=("security",),
        )

        with self.assertRaises(ArticleStateError):
            self.service.create_article(duplicate)

    def test_rejects_unknown_categories(self) -> None:
        with self.assertRaises(ArticleStateError):
            self.service.create_article(
                KnowledgeArticle(
                    knowledge_article_id="ka-1",
                    tenant_id="tenant-1",
                    title="Custom",
                    slug="custom",
                    body_markdown="Body",
                    status="published",
                    version=1,
                    published_at="2026-03-26T00:00:00Z",
                    updated_at="2026-03-26T00:00:00Z",
                    categories=("unknown",),
                )
            )

    def test_basic_search_filters_by_category_and_status(self) -> None:
        self.service.create_article(
            KnowledgeArticle(
                knowledge_article_id="ka-1",
                tenant_id="tenant-1",
                title="Configure SSO integration",
                slug="configure-sso",
                body_markdown="Use SAML metadata and map assertion fields.",
                status="published",
                version=2,
                published_at="2026-03-26T00:00:00Z",
                updated_at="2026-03-26T03:00:00Z",
                categories=("integrations", "security"),
            )
        )
        self.service.create_article(
            KnowledgeArticle(
                knowledge_article_id="ka-2",
                tenant_id="tenant-1",
                title="Draft billing notes",
                slug="draft-billing",
                body_markdown="This should not show in search.",
                status="draft",
                version=1,
                published_at=None,
                updated_at="2026-03-26T02:00:00Z",
                categories=("billing",),
            )
        )

        results = self.service.search_articles(tenant_id="tenant-1", query="sso assertion", category="integrations")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["knowledge_article_id"], "ka-1")


if __name__ == "__main__":
    unittest.main()
