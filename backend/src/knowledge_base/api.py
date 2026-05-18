"""API contracts for Knowledge Base Service, aligned to docs/api-standards.md."""

from __future__ import annotations

from typing import Any

from .entities import ArticleNotFoundError, ArticleStateError, KnowledgeArticle
from .services import KnowledgeBaseService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "list_articles": {"method": "GET", "path": "/api/v1/knowledge-articles"},
    "create_article": {"method": "POST", "path": "/api/v1/knowledge-articles"},
    "get_article": {"method": "GET", "path": "/api/v1/knowledge-articles/{knowledge_article_id}"},
    "update_article": {"method": "PATCH", "path": "/api/v1/knowledge-articles/{knowledge_article_id}"},
    "delete_article": {"method": "DELETE", "path": "/api/v1/knowledge-articles/{knowledge_article_id}"},
    "search_articles": {"method": "GET", "path": "/api/v1/knowledge-article-searches"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str, details: list[dict[str, str]] | None = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details or []},
        "meta": {"request_id": request_id},
    }


class KnowledgeBaseApi:
    def __init__(self, service: KnowledgeBaseService) -> None:
        self._service = service

    def list_articles(self, request_id: str) -> dict[str, Any]:
        return success([self._service.serialize(a) for a in self._service.list_articles()], request_id)

    def create_article(self, article: KnowledgeArticle, request_id: str) -> dict[str, Any]:
        try:
            created = self._service.create_article(article)
            return success(self._service.serialize(created), request_id)
        except ArticleStateError as exc:
            return error("validation_error", str(exc), request_id)

    def get_article(self, knowledge_article_id: str, request_id: str) -> dict[str, Any]:
        try:
            article = self._service.get_article(knowledge_article_id)
            return success(self._service.serialize(article), request_id)
        except ArticleNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def update_article(self, knowledge_article_id: str, changes: dict[str, object], request_id: str) -> dict[str, Any]:
        try:
            article = self._service.update_article(knowledge_article_id, **changes)
            return success(self._service.serialize(article), request_id)
        except ArticleNotFoundError as exc:
            return error("not_found", str(exc), request_id)
        except ArticleStateError as exc:
            return error("validation_error", str(exc), request_id)

    def delete_article(self, knowledge_article_id: str, request_id: str) -> dict[str, Any]:
        try:
            self._service.delete_article(knowledge_article_id)
            return success({"deleted": True}, request_id)
        except ArticleNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def search_articles(
        self,
        tenant_id: str,
        query: str,
        request_id: str,
        category: str | None = None,
    ) -> dict[str, Any]:
        try:
            return success(self._service.search_articles(tenant_id=tenant_id, query=query, category=category), request_id)
        except ArticleStateError as exc:
            return error("validation_error", str(exc), request_id)
