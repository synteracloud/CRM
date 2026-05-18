"""Knowledge Base domain entities aligned to docs/domain-model.md."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


KNOWLEDGE_ARTICLE_FIELDS: tuple[str, ...] = (
    "knowledge_article_id",
    "tenant_id",
    "title",
    "slug",
    "body_markdown",
    "status",
    "version",
    "published_at",
    "updated_at",
    "categories",
)

ARTICLE_CATEGORIES: tuple[str, ...] = (
    "getting_started",
    "billing",
    "integrations",
    "troubleshooting",
    "security",
    "account_management",
)


@dataclass(frozen=True)
class KnowledgeArticle:
    """Canonical KnowledgeArticle entity definition from the domain model."""

    knowledge_article_id: str
    tenant_id: str
    title: str
    slug: str
    body_markdown: str
    status: str
    version: int
    published_at: str | None
    updated_at: str
    categories: tuple[str, ...]

    def patch(self, **changes: Any) -> "KnowledgeArticle":
        """Return an updated immutable copy of the article."""
        return replace(self, **changes)


class ArticleNotFoundError(KeyError):
    """Raised when an article cannot be found for a given id."""


class ArticleStateError(ValueError):
    """Raised when article lifecycle/content validation fails."""
