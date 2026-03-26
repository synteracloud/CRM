"""API-shaped wrapper for layout builder operations."""

from __future__ import annotations

from typing import Any

from .entities import DynamicFieldDefinition, LayoutConfig, LayoutValidationError
from .services import LayoutBuilderService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "build_layout": {"method": "POST", "path": "/api/v1/custom-objects/{objectKey}/layouts/build"}
}


def success(data: Any, request_id: str) -> dict[str, Any]:
    return {"data": data, "meta": {"request_id": request_id}}


def error(code: str, message: str, request_id: str) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": []},
        "meta": {"request_id": request_id},
    }


class CustomObjectLayoutApi:
    def __init__(self, service: LayoutBuilderService) -> None:
        self._service = service

    def build_layout(
        self, fields: list[DynamicFieldDefinition], layout: LayoutConfig, request_id: str
    ) -> dict[str, Any]:
        try:
            return success(self._service.build_ui_schema(fields, layout), request_id)
        except LayoutValidationError as exc:
            return error("layout_validation_error", str(exc), request_id)
