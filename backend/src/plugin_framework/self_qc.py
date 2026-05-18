"""Self-QC checks for plugin framework requirements."""

from __future__ import annotations

from .entities import HookExecutionContext, PluginManifest
from .services import PluginFramework


class _MutatingPlugin:
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(plugin_id="plugin.mutating", display_name="Mutating", version="1.0.0")

    def hooks(self) -> dict[str, tuple]:
        return {"lead.created.v1": (self._on_event,)}

    def on_install(self, context: HookExecutionContext) -> None:
        context.plugin_state["installed"] = True

    def on_uninstall(self, context: HookExecutionContext) -> None:
        context.plugin_state["uninstalled"] = True

    def _on_event(self, context: HookExecutionContext, payload: dict[str, str]) -> str:
        context.plugin_state["count"] = context.plugin_state.get("count", 0) + 1
        try:
            context.core_view["tenant"] = "tampered"  # type: ignore[index]
        except TypeError:
            pass
        return payload.get("lead_id", "")


class _ObserverPlugin:
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(plugin_id="plugin.observer", display_name="Observer", version="1.0.0")

    def hooks(self) -> dict[str, tuple]:
        return {"lead.created.v1": (self._on_event,)}

    def on_install(self, context: HookExecutionContext) -> None:
        context.plugin_state["installed"] = True

    def on_uninstall(self, context: HookExecutionContext) -> None:
        context.plugin_state["uninstalled"] = True

    def _on_event(self, context: HookExecutionContext, payload: dict[str, str]) -> str:
        context.plugin_state["seen_core_tenant"] = str(context.core_view.get("tenant"))
        return payload.get("lead_id", "")


def run_self_qc() -> dict[str, bool]:
    framework = PluginFramework(core_state={"tenant": "tenant-1"})
    framework.install(_MutatingPlugin())
    framework.install(_ObserverPlugin())

    framework.trigger_hook("lead.created.v1", {"lead_id": "lead-1"})

    mutating_state = framework.get_plugin_state("plugin.mutating")
    observer_state = framework.get_plugin_state("plugin.observer")

    plugins_isolated = "count" in mutating_state and "count" not in observer_state
    no_core_system_interference = observer_state.get("seen_core_tenant") == "tenant-1"

    return {
        "plugins_isolated": plugins_isolated,
        "no_core_system_interference": no_core_system_interference,
    }
