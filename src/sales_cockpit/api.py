"""API contracts for sales cockpit workspace."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .workspace import build_sales_cockpit

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "get_workspace": {"method": "GET", "path": "/api/v1/sales/cockpit/workspace"},
}


class SalesCockpitApi:
    def get_workspace(self, request_id: str) -> dict[str, Any]:
        workspace = build_sales_cockpit()
        return {"data": asdict(workspace), "meta": {"request_id": request_id}}
