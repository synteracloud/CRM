"""API facade for design system registry."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import DesignSystemValidationError
from .services import DesignSystemRegistryService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "get_design_system_snapshot": {"method": "GET", "path": "/api/v1/ui/design-system"}
}


class DesignSystemApi:
    def __init__(self, service: DesignSystemRegistryService) -> None:
        self._service = service

    def get_design_system_snapshot(self, *, request_id: str) -> dict[str, Any]:
        try:
            snapshot = self._service.snapshot()
            return {"data": asdict(snapshot), "meta": {"request_id": request_id}}
        except DesignSystemValidationError as exc:
            return {
                "error": {"code": "validation_error", "message": str(exc), "details": []},
                "meta": {"request_id": request_id},
            }
