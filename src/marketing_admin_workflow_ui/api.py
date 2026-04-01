"""API contracts for integrated marketing/admin/workflow UI model."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .services import build_integrated_ui_model, run_self_qc

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "get_integrated_ui": {"method": "GET", "path": "/api/v1/ui/marketing-admin-workflow"},
    "get_integrated_ui_qc": {"method": "GET", "path": "/api/v1/ui/marketing-admin-workflow/qc"},
}


class MarketingAdminWorkflowUiApi:
    def get_integrated_ui(self, request_id: str) -> dict[str, Any]:
        return {
            "data": asdict(build_integrated_ui_model()),
            "meta": {"request_id": request_id},
        }

    def get_integrated_ui_qc(self, request_id: str) -> dict[str, Any]:
        return {
            "data": run_self_qc(),
            "meta": {"request_id": request_id},
        }
