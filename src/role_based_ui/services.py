"""Backend-driven role-based UI configuration service."""

from __future__ import annotations

from .entities import UiConfig, UiConfigValidationError, UiSectionRule

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
    ),
    "tenant_admin": (
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
    ),
    "manager": (
        "users.read",
        "records.read",
        "records.create",
        "records.update",
        "reports.read",
    ),
    "agent": (
        "records.read",
        "records.create",
        "records.update",
    ),
    "analyst": (
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
    "integration_service": (
        "records.read",
        "records.create",
        "records.update",
    ),
    "platform_security_ops": (),
}

DEFAULT_UI_SECTIONS: tuple[UiSectionRule, ...] = (
    UiSectionRule(
        section_id="dashboard",
        title="Dashboard",
        route="/app/dashboard",
        required_permissions=("records.read",),
    ),
    UiSectionRule(
        section_id="records_workspace",
        title="Records Workspace",
        route="/app/records",
        required_permissions=("records.read",),
    ),
    UiSectionRule(
        section_id="record_editor",
        title="Record Editor",
        route="/app/records/editor",
        required_permissions=("records.create", "records.update"),
        visibility_mode="any",
    ),
    UiSectionRule(
        section_id="reports",
        title="Reports",
        route="/app/reports",
        required_permissions=("reports.read",),
    ),
    UiSectionRule(
        section_id="user_admin",
        title="User Administration",
        route="/app/admin/users",
        required_permissions=("users.manage_roles",),
        allowed_roles=("tenant_owner", "tenant_admin"),
    ),
    UiSectionRule(
        section_id="tenant_settings",
        title="Tenant Settings",
        route="/app/admin/tenant",
        required_permissions=("tenant.settings.write",),
        allowed_roles=("tenant_owner", "tenant_admin"),
    ),
    UiSectionRule(
        section_id="audit_logs",
        title="Audit Logs",
        route="/app/security/audit-logs",
        required_permissions=("audit.logs.read",),
    ),
)


class RoleBasedUiConfigService:
    """Resolves visible UI sections from principal roles and permissions."""

    def __init__(
        self,
        policy_version: str = "rbac-ui-v1",
        role_permissions: dict[str, tuple[str, ...]] | None = None,
        section_rules: tuple[UiSectionRule, ...] = DEFAULT_UI_SECTIONS,
    ) -> None:
        self._policy_version = policy_version
        self._role_permissions = role_permissions or ROLE_PERMISSION_MAP
        self._section_rules = section_rules
        self._validate_rules()

    def resolve(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        role_ids: tuple[str, ...],
        explicit_permissions: tuple[str, ...] = (),
    ) -> UiConfig:
        if not tenant_id or not principal_id:
            raise UiConfigValidationError("tenant_id and principal_id are required")

        permissions = self._effective_permissions(role_ids, explicit_permissions)
        visible_sections: list[UiSectionRule] = []
        hidden_sections: list[str] = []

        for section in self._section_rules:
            if self._is_visible(section, role_ids, permissions):
                visible_sections.append(section)
            else:
                hidden_sections.append(section.section_id)

        return UiConfig(
            tenant_id=tenant_id,
            principal_id=principal_id,
            role_ids=tuple(sorted(set(role_ids))),
            permissions=tuple(sorted(permissions)),
            visible_sections=tuple(visible_sections),
            hidden_section_ids=tuple(hidden_sections),
            policy_version=self._policy_version,
        )

    def _effective_permissions(self, role_ids: tuple[str, ...], explicit_permissions: tuple[str, ...]) -> set[str]:
        permissions: set[str] = set(explicit_permissions)
        for role_id in set(role_ids):
            permissions.update(self._role_permissions.get(role_id, ()))
        return permissions

    @staticmethod
    def _is_visible(section: UiSectionRule, role_ids: tuple[str, ...], permissions: set[str]) -> bool:
        if section.allowed_roles and not set(role_ids).intersection(section.allowed_roles):
            return False

        if not section.required_permissions:
            return True

        if section.visibility_mode == "all":
            return all(permission in permissions for permission in section.required_permissions)
        return any(permission in permissions for permission in section.required_permissions)

    def _validate_rules(self) -> None:
        known_modes = {"all", "any"}
        seen_ids: set[str] = set()
        for rule in self._section_rules:
            if rule.section_id in seen_ids:
                raise UiConfigValidationError(f"duplicate section_id: {rule.section_id}")
            seen_ids.add(rule.section_id)
            if rule.visibility_mode not in known_modes:
                raise UiConfigValidationError(f"invalid visibility_mode: {rule.visibility_mode}")
            if not rule.route.startswith("/"):
                raise UiConfigValidationError(f"route must start with '/': {rule.route}")
