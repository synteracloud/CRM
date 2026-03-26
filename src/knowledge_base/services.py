"""Services for Knowledge Base article management and search."""

from __future__ import annotations

import re
from dataclasses import asdict

from .entities import (
    ARTICLE_CATEGORIES,
    ArticleNotFoundError,
    ArticleStateError,
    KnowledgeArticle,
)


class KnowledgeBaseService:
    """In-memory service implementing article CRUD + basic search logic."""

    def __init__(self) -> None:
        self._store: dict[str, KnowledgeArticle] = {}

    def list_articles(self) -> list[KnowledgeArticle]:
        return list(self._store.values())

    def create_article(self, article: KnowledgeArticle) -> KnowledgeArticle:
        if article.knowledge_article_id in self._store:
            raise ArticleStateError(f"Article already exists: {article.knowledge_article_id}")

        self._validate_categories(article.categories)
        self._validate_unique_content(article)
        self._store[article.knowledge_article_id] = article
        return article

    def get_article(self, knowledge_article_id: str) -> KnowledgeArticle:
        article = self._store.get(knowledge_article_id)
        if not article:
            raise ArticleNotFoundError(f"Article not found: {knowledge_article_id}")
        return article

    def update_article(self, knowledge_article_id: str, **changes: object) -> KnowledgeArticle:
        article = self.get_article(knowledge_article_id)
        immutable_fields = {"knowledge_article_id", "tenant_id"}
        if immutable_fields.intersection(changes.keys()):
            raise ArticleStateError("Cannot update immutable article fields.")

        if "categories" in changes:
            categories = tuple(changes["categories"])
            self._validate_categories(categories)
            changes["categories"] = categories

        updated = article.patch(**changes)
        self._validate_unique_content(updated, existing_id=knowledge_article_id)

        self._store[knowledge_article_id] = updated
        return updated

    def delete_article(self, knowledge_article_id: str) -> None:
        self.get_article(knowledge_article_id)
        del self._store[knowledge_article_id]

    def search_articles(self, tenant_id: str, query: str, category: str | None = None) -> list[dict[str, object]]:
        tokens = self._tokenize(query)
        if not tokens:
            return []

        if category is not None:
            self._validate_categories((category,))

        ranked: list[tuple[int, KnowledgeArticle]] = []
        for article in self._store.values():
            if article.tenant_id != tenant_id or article.status != "published":
                continue
            if category and category not in article.categories:
                continue

            haystack = f"{article.title} {article.body_markdown} {' '.join(article.categories)}".lower()
            score = sum(1 for token in tokens if token in haystack)
            if score > 0:
                ranked.append((score, article))

        ranked.sort(key=lambda item: (item[0], item[1].updated_at), reverse=True)
        return [
            {
                "score": score,
                "knowledge_article_id": article.knowledge_article_id,
                "title": article.title,
                "slug": article.slug,
                "categories": list(article.categories),
                "updated_at": article.updated_at,
            }
            for score, article in ranked
        ]

    def _validate_unique_content(self, incoming: KnowledgeArticle, existing_id: str | None = None) -> None:
        normalized_title = incoming.title.strip().lower()
        normalized_body = re.sub(r"\s+", " ", incoming.body_markdown).strip().lower()

        for stored in self._store.values():
            if existing_id and stored.knowledge_article_id == existing_id:
                continue
            if stored.tenant_id != incoming.tenant_id:
                continue
            stored_title = stored.title.strip().lower()
            stored_body = re.sub(r"\s+", " ", stored.body_markdown).strip().lower()
            if normalized_title == stored_title and normalized_body == stored_body:
                raise ArticleStateError(
                    "Duplicate article content detected for tenant. "
                    "Title + body must be unique per tenant."
                )

    def _validate_categories(self, categories: tuple[str, ...]) -> None:
        if not categories:
            raise ArticleStateError("At least one category is required.")
        unknown = [category for category in categories if category not in ARTICLE_CATEGORIES]
        if unknown:
            raise ArticleStateError(
                f"Unknown categories: {unknown}. Allowed categories: {list(ARTICLE_CATEGORIES)}"
            )

    @staticmethod
    def _tokenize(query: str) -> list[str]:
        return [token for token in re.findall(r"[a-zA-Z0-9_]+", query.lower()) if token]

    @staticmethod
    def serialize(article: KnowledgeArticle) -> dict[str, object]:
        data = asdict(article)
        data["categories"] = list(article.categories)
        return data
