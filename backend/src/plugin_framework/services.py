"""Plugin framework services for registration, lifecycle, and hook dispatching."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .entities import HookExecutionContext, Plugin, PluginRecord, readonly_core_view


class PluginRegistrationError(ValueError):
    """Raised when a plugin cannot be registered."""


@dataclass(frozen=True)
class HookExecutionResult:
    plugin_id: str
    hook: str
    ok: bool
    result: Any = None
    error: str | None = None


class PluginFramework:
    """Coordinates plugin install/uninstall and isolated hook execution."""

    def __init__(self, core_state: dict[str, Any] | None = None) -> None:
        self._core_state = core_state or {}
        self._plugins: dict[str, Plugin] = {}
        self._records: dict[str, PluginRecord] = {}
        self._hooks: dict[str, list[str]] = defaultdict(list)

    @property
    def installed_plugin_ids(self) -> tuple[str, ...]:
        return tuple(self._plugins.keys())

    def install(self, plugin: Plugin) -> None:
        plugin_id = plugin.manifest.plugin_id
        if plugin_id in self._plugins:
            raise PluginRegistrationError(f"Plugin already installed: {plugin_id}")

        hooks = plugin.hooks()
        record = PluginRecord(manifest=plugin.manifest, hooks=hooks)
        self._plugins[plugin_id] = plugin
        self._records[plugin_id] = record

        for hook_name in hooks:
            self._hooks[hook_name].append(plugin_id)

        plugin.on_install(self._build_context(plugin_id))

    def uninstall(self, plugin_id: str) -> None:
        plugin = self._plugins.get(plugin_id)
        record = self._records.get(plugin_id)
        if not plugin or not record:
            raise PluginRegistrationError(f"Plugin is not installed: {plugin_id}")

        plugin.on_uninstall(self._build_context(plugin_id))

        for hook_name in list(record.hooks):
            self._hooks[hook_name] = [pid for pid in self._hooks[hook_name] if pid != plugin_id]
            if not self._hooks[hook_name]:
                del self._hooks[hook_name]

        del self._plugins[plugin_id]
        del self._records[plugin_id]

    def trigger_hook(self, hook_name: str, payload: dict[str, Any]) -> list[HookExecutionResult]:
        results: list[HookExecutionResult] = []
        for plugin_id in self._hooks.get(hook_name, []):
            record = self._records[plugin_id]
            context = self._build_context(plugin_id)
            for handler in record.hooks.get(hook_name, ()):  # isolated per hook invocation
                try:
                    handler_result = handler(context, dict(payload))
                    results.append(HookExecutionResult(plugin_id=plugin_id, hook=hook_name, ok=True, result=handler_result))
                except Exception as exc:  # noqa: BLE001 - plugin errors are isolated from core runtime.
                    results.append(HookExecutionResult(plugin_id=plugin_id, hook=hook_name, ok=False, error=str(exc)))
        return results

    def get_plugin_state(self, plugin_id: str) -> dict[str, Any]:
        if plugin_id not in self._records:
            raise PluginRegistrationError(f"Plugin is not installed: {plugin_id}")
        return dict(self._records[plugin_id].state)

    def _build_context(self, plugin_id: str) -> HookExecutionContext:
        record = self._records[plugin_id]
        return HookExecutionContext(plugin_id=plugin_id, plugin_state=record.state, core_view=readonly_core_view(self._core_state))
