"""Entities for plugin registration, lifecycle, and hook execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol

HookHandler = Callable[["HookExecutionContext", dict[str, Any]], Any]


@dataclass(frozen=True)
class PluginManifest:
    """Static plugin metadata used by the registry."""

    plugin_id: str
    display_name: str
    version: str


@dataclass
class HookExecutionContext:
    """Execution context provided to hooks.

    `core_view` is intentionally read-only to prevent plugin mutation of core state.
    `plugin_state` is isolated and unique per plugin.
    """

    plugin_id: str
    plugin_state: dict[str, Any]
    core_view: Mapping[str, Any]


@dataclass
class PluginRecord:
    """Runtime record for an installed plugin."""

    manifest: PluginManifest
    hooks: dict[str, tuple[HookHandler, ...]] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)


class Plugin(Protocol):
    """Contract that all plugins must implement."""

    @property
    def manifest(self) -> PluginManifest: ...

    def hooks(self) -> dict[str, tuple[HookHandler, ...]]: ...

    def on_install(self, context: HookExecutionContext) -> None: ...

    def on_uninstall(self, context: HookExecutionContext) -> None: ...


def readonly_core_view(core_state: Mapping[str, Any]) -> Mapping[str, Any]:
    """Build an immutable view for plugin access to core state."""

    return MappingProxyType(dict(core_state))
