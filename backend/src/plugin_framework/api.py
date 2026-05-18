"""API-like facade for plugin framework operations."""

from __future__ import annotations

from typing import Any

from .services import PluginFramework, PluginRegistrationError

API_ENDPOINTS: dict[str, dict[str, str]] = {
    "install_plugin": {"method": "POST", "path": "/api/v1/plugins/installations"},
    "uninstall_plugin": {"method": "POST", "path": "/api/v1/plugins/uninstallations"},
    "trigger_hook": {"method": "POST", "path": "/api/v1/plugin-hook-executions"},
}


class PluginFrameworkApi:
    def __init__(self, framework: PluginFramework) -> None:
        self._framework = framework

    def trigger_hook(self, hook_name: str, payload: dict[str, Any], request_id: str) -> dict[str, Any]:
        try:
            results = self._framework.trigger_hook(hook_name, payload)
            return {
                "data": [result.__dict__ for result in results],
                "meta": {"request_id": request_id},
            }
        except PluginRegistrationError as exc:
            return {
                "error": {"code": "plugin_error", "message": str(exc), "details": []},
                "meta": {"request_id": request_id},
            }
