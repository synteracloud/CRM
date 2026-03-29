"""Service for assembling Admin Control Center structure, views, and interaction patterns."""

from __future__ import annotations

from .entities import (
    AdminControlCenter,
    AdminControlValidationError,
    AdminPanel,
    InteractionPattern,
    ResolvedPanel,
)

ROLE_PERMISSION_MAP: dict[str, tuple[str, ...]] = {
    "tenant_owner": (
        "tenant.settings.read",
        "tenant.settings.write",
        "users.read",
        "users.manage_roles",
        "records.read",
        "records.create",
        "records.update",
        "records.delete",
        "reports.read",
        "audit.logs.read",
        "api.tokens.manage",
        "custom_objects.manage",
        "custom_fields.manage",
        "workflow.manage",
        "integrations.manage",
        "feature_flags.manage",
    ),
    "tenant_admin": (
        "tenant.settings.read",
        "tenant.settings.write",
        "users.read",
        "users.manage_roles",
        "records.read",
        "reports.read",
        "audit.logs.read",
        "api.tokens.manage",
        "custom_objects.manage",
        "custom_fields.manage",
        "workflow.manage",
        "integrations.manage",
        "feature_flags.manage",
    ),
    "manager": (
        "users.read",
        "records.read",
        "reports.read",
    ),
    "auditor": (
        "tenant.settings.read",
        "users.read",
        "records.read",
        "reports.read",
        "audit.logs.read",
    ),
}

ADMIN_PANELS: tuple[AdminPanel, ...] = (
    AdminPanel(
        panel_id="admin_workspace_home",
        name="Admin Workspace",
        route="/app/admin",
        category="workspace",
        required_permissions=("tenant.settings.read",),
    ),
    AdminPanel(
        panel_id="users_roles_permissions",
        name="Users / Roles / Permissions",
        route="/app/admin/users",
        category="users_roles_permissions",
        required_permissions=("users.read",),
        write_permissions=("users.manage_roles",),
        critical=True,
    ),
    AdminPanel(
        panel_id="custom_object_control",
        name="Custom Field / Custom Object Control",
        route="/app/admin/custom-objects",
        category="customization",
        required_permissions=("custom_objects.manage", "custom_fields.manage"),
        write_permissions=("custom_objects.manage", "custom_fields.manage"),
        critical=True,
    ),
    AdminPanel(
        panel_id="workflow_management",
        name="Workflow Management",
        route="/app/admin/workflows",
        category="workflow",
        required_permissions=("workflow.manage",),
        write_permissions=("workflow.manage",),
        critical=True,
    ),
    AdminPanel(
        panel_id="config_flags_integrations",
        name="Config / Flags / Integrations",
        route="/app/admin/config",
        category="config",
        required_permissions=("tenant.settings.read",),
        write_permissions=("tenant.settings.write", "feature_flags.manage", "integrations.manage"),
        critical=True,
    ),
)

INTERACTION_PATTERNS: tuple[InteractionPattern, ...] = (
    InteractionPattern(
        pattern_id="safe_mutation",
        title="Two-step Save + Confirm",
        description="All write actions require validation preview and explicit confirmation before commit.",
        controls=("dry_run_validation", "confirm_commit", "audit_event"),
    ),
    InteractionPattern(
        pattern_id="default_deny_visibility",
        title="Default-Deny View Resolution",
        description="Panels are hidden unless required permissions are explicitly present in effective grants.",
        controls=("role_permission_union", "permission_gate", "tenant_scope_check"),
    ),
    InteractionPattern(
        pattern_id="workflow_guardrails",
        title="Workflow DSL Guardrails",
        description="Workflow edits validate trigger/action references and acyclic sequencing before activation.",
        controls=("dsl_schema_validation", "catalog_alignment_check", "acyclic_step_check"),
    ),
)


class AdminControlCenterService:
    def __init__(self, policy_version: str = "admin-control-v1") -> None:
        self._policy_version = policy_version

    def build(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        role_ids: tuple[str, ...],
        explicit_permissions: tuple[str, ...] = (),
    ) -> AdminControlCenter:
        if not tenant_id or not principal_id:
            raise AdminControlValidationError("tenant_id and principal_id are required")

        permissions = self._effective_permissions(role_ids=role_ids, explicit_permissions=explicit_permissions)
        views: list[ResolvedPanel] = []
        hidden_panels: list[str] = []

        for panel in ADMIN_PANELS:
            can_read = all(permission in permissions for permission in panel.required_permissions)
            can_write = all(permission in permissions for permission in panel.write_permissions)

            if can_read:
                state = "editable" if can_write or not panel.write_permissions else "read_only"
                views.append(
                    ResolvedPanel(
                        panel_id=panel.panel_id,
                        name=panel.name,
                        route=panel.route,
                        category=panel.category,
                        state=state,
                        required_permissions=panel.required_permissions,
                        write_permissions=panel.write_permissions,
                        critical=panel.critical,
                    )
                )
            else:
                hidden_panels.append(panel.panel_id)

        return AdminControlCenter(
            tenant_id=tenant_id,
            principal_id=principal_id,
            role_ids=tuple(sorted(set(role_ids))),
            permissions=tuple(sorted(permissions)),
            structure=tuple(panel.panel_id for panel in ADMIN_PANELS),
            views=tuple(views),
            interaction_patterns=INTERACTION_PATTERNS,
            hidden_panel_ids=tuple(hidden_panels),
            policy_version=self._policy_version,
        )

    @staticmethod
    def _effective_permissions(*, role_ids: tuple[str, ...], explicit_permissions: tuple[str, ...]) -> set[str]:
        permissions = set(explicit_permissions)
        for role_id in set(role_ids):
            permissions.update(ROLE_PERMISSION_MAP.get(role_id, ()))
        return permissions


def run_self_qc() -> dict[str, bool]:
    """Self-QC loop checks for control completeness, security, and critical-setting visibility."""

    service = AdminControlCenterService()
    owner = service.build(tenant_id="tenant-1", principal_id="user-owner", role_ids=("tenant_owner",))
    agent_like = service.build(tenant_id="tenant-1", principal_id="user-limited", role_ids=("manager",))

    expected_controls = {
        "users_roles_permissions",
        "custom_object_control",
        "workflow_management",
        "config_flags_integrations",
    }
    restricted_controls = {
        "custom_object_control",
        "workflow_management",
        "config_flags_integrations",
    }
    visible_for_owner = {panel.panel_id for panel in owner.views}
    hidden_for_limited = set(agent_like.hidden_panel_ids)

    checks = {
        "admin_controls_complete": expected_controls.issubset(set(owner.structure)),
        "security_respected_default_deny": restricted_controls.issubset(hidden_for_limited),
        "no_hidden_critical_settings_for_admin": all(
            not panel.critical or panel.panel_id in visible_for_owner for panel in ADMIN_PANELS
        ),
    }
    return checks
