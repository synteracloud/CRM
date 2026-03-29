"""API facade for Admin Control Center."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import AdminControlValidationError
from .services import AdminControlCenterService

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "get_admin_control_center": {"method": "GET", "path": "/api/v1/admin/control-center"},
}


class AdminControlCenterApi:
    def __init__(self, service: AdminControlCenterService) -> None:
        self._service = service

    def get_admin_control_center(
        self,
        *,
        request_id: str,
        tenant_id: str,
        principal_id: str,
        role_ids: tuple[str, ...],
        explicit_permissions: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        try:
            payload = self._service.build(
                tenant_id=tenant_id,
                principal_id=principal_id,
                role_ids=role_ids,
                explicit_permissions=explicit_permissions,
            )
            return {"data": asdict(payload), "meta": {"request_id": request_id}}
        except AdminControlValidationError as exc:
            return {
                "error": {"code": "validation_error", "message": str(exc), "details": []},
                "meta": {"request_id": request_id},
            }
