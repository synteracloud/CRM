"""APIs to fetch reporting dashboard data from read models only."""

from __future__ import annotations

from typing import Any

from .entities import DashboardReadModelNotFoundError
from .services import DashboardReadModelService


API_ENDPOINTS: dict[str, dict[str, str]] = {
    "get_sales_dashboard": {"method": "GET", "path": "/api/v1/reporting/dashboards/sales"},
    "get_marketing_dashboard": {"method": "GET", "path": "/api/v1/reporting/dashboards/marketing"},
    "get_support_dashboard": {"method": "GET", "path": "/api/v1/reporting/dashboards/support"},
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": []}, "meta": {"request_id": request_id}}


class DashboardApi:
    """Fetches dashboard payloads from precomputed read model projections."""

    def __init__(self, service: DashboardReadModelService) -> None:
        self._service = service

    def get_sales_dashboard(self, tenant_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(self._service.serialize(self._service.get_sales(tenant_id)), request_id)
        except DashboardReadModelNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def get_marketing_dashboard(self, tenant_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(self._service.serialize(self._service.get_marketing(tenant_id)), request_id)
        except DashboardReadModelNotFoundError as exc:
            return error("not_found", str(exc), request_id)

    def get_support_dashboard(self, tenant_id: str, request_id: str) -> dict[str, Any]:
        try:
            return success(self._service.serialize(self._service.get_support(tenant_id)), request_id)
        except DashboardReadModelNotFoundError as exc:
            return error("not_found", str(exc), request_id)
