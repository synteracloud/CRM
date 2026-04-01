"""API wrapper for role-based UI config endpoint."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import UiConfigValidationError
from .services import ResponsiveLayoutService, RoleBasedUiConfigService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "get_ui_config": {"method": "GET", "path": "/api/v1/ui/config"},
    "get_responsive_layout": {"method": "GET", "path": "/api/v1/ui/responsive-layout"},
}


class RoleBasedUiApi:
    def __init__(
        self,
        service: RoleBasedUiConfigService,
        responsive_service: ResponsiveLayoutService | None = None,
    ) -> None:
        self._service = service
        self._responsive_service = responsive_service or ResponsiveLayoutService()

    def get_ui_config(
        self,
        *,
        request_id: str,
        tenant_id: str,
        principal_id: str,
        role_ids: tuple[str, ...],
        explicit_permissions: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        try:
            payload = self._service.resolve(
                tenant_id=tenant_id,
                principal_id=principal_id,
                role_ids=role_ids,
                explicit_permissions=explicit_permissions,
            )
            return {"data": asdict(payload), "meta": {"request_id": request_id}}
        except UiConfigValidationError as exc:
            return {
                "error": {"code": "validation_error", "message": str(exc), "details": []},
                "meta": {"request_id": request_id},
            }

    def get_responsive_layout(
        self,
        *,
        request_id: str,
        viewport_width: int,
    ) -> dict[str, Any]:
        try:
            layout = self._responsive_service.resolve(viewport_width=viewport_width)
            return {"data": asdict(layout), "meta": {"request_id": request_id}}
        except UiConfigValidationError as exc:
            return {
                "error": {"code": "validation_error", "message": str(exc), "details": []},
                "meta": {"request_id": request_id},
            }
