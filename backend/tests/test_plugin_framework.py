from __future__ import annotations

import unittest

from src.plugin_framework import API_ENDPOINTS, HookExecutionContext, PluginFramework, PluginManifest, run_self_qc


class CounterPlugin:
    def __init__(self, plugin_id: str) -> None:
        self._plugin_id = plugin_id
        self.installed = False
        self.uninstalled = False

    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(plugin_id=self._plugin_id, display_name=self._plugin_id, version="1.0.0")

    def hooks(self) -> dict[str, tuple]:
        return {"lead.created.v1": (self._on_lead_created,)}

    def on_install(self, context: HookExecutionContext) -> None:
        self.installed = True
        context.plugin_state["events"] = 0

    def on_uninstall(self, context: HookExecutionContext) -> None:
        self.uninstalled = True

    def _on_lead_created(self, context: HookExecutionContext, payload: dict[str, str]) -> str:
        context.plugin_state["events"] += 1
        return payload["lead_id"]


class MutatorPlugin:
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(plugin_id="plugin.mutator", display_name="Mutator", version="1.0.0")

    def hooks(self) -> dict[str, tuple]:
        return {"lead.created.v1": (self._mutate,)}

    def on_install(self, context: HookExecutionContext) -> None:
        context.plugin_state["installed"] = True

    def on_uninstall(self, context: HookExecutionContext) -> None:
        context.plugin_state["uninstalled"] = True

    def _mutate(self, context: HookExecutionContext, payload: dict[str, str]) -> str:
        context.plugin_state["lead"] = payload["lead_id"]
        try:
            context.core_view["tenant"] = "bad"  # type: ignore[index]
        except TypeError:
            context.plugin_state["core_mutation_blocked"] = True
        return "ok"


class PluginFrameworkTests(unittest.TestCase):
    def test_install_uninstall_lifecycle_and_hook_registration(self) -> None:
        framework = PluginFramework(core_state={"tenant": "tenant-1"})
        plugin = CounterPlugin("plugin.lifecycle")

        framework.install(plugin)
        self.assertTrue(plugin.installed)
        self.assertIn("plugin.lifecycle", framework.installed_plugin_ids)

        first = framework.trigger_hook("lead.created.v1", {"lead_id": "lead-1"})
        self.assertEqual(len(first), 1)
        self.assertTrue(first[0].ok)
        self.assertEqual(first[0].result, "lead-1")

        framework.uninstall("plugin.lifecycle")
        self.assertTrue(plugin.uninstalled)
        second = framework.trigger_hook("lead.created.v1", {"lead_id": "lead-2"})
        self.assertEqual(second, [])

    def test_plugins_are_isolated_and_core_state_is_protected(self) -> None:
        framework = PluginFramework(core_state={"tenant": "tenant-1"})
        first = CounterPlugin("plugin.a")
        second = CounterPlugin("plugin.b")
        mutator = MutatorPlugin()

        framework.install(first)
        framework.install(second)
        framework.install(mutator)
        framework.trigger_hook("lead.created.v1", {"lead_id": "lead-1"})

        first_state = framework.get_plugin_state("plugin.a")
        second_state = framework.get_plugin_state("plugin.b")
        mutator_state = framework.get_plugin_state("plugin.mutator")

        self.assertEqual(first_state["events"], 1)
        self.assertEqual(second_state["events"], 1)
        self.assertTrue(mutator_state["core_mutation_blocked"])
        self.assertEqual(framework.trigger_hook("missing.hook", {"lead_id": "x"}), [])

    def test_api_endpoints_and_self_qc(self) -> None:
        self.assertEqual(API_ENDPOINTS["install_plugin"]["path"], "/api/v1/plugins/installations")
        self.assertEqual(API_ENDPOINTS["trigger_hook"]["method"], "POST")
        qc = run_self_qc()
        self.assertTrue(all(qc.values()), qc)


if __name__ == "__main__":
    unittest.main()
