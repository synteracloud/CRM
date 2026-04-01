"""Design-system registry service aligned to docs/ui-system.md."""

from __future__ import annotations

from .entities import ComponentContract, DesignSystemSnapshot, DesignSystemValidationError, DesignToken

INTERACTION_STATE_CONTRACT: tuple[str, ...] = (
    "default",
    "keyboard_focus",
    "in_progress",
    "success",
    "error_recoverable",
    "error_blocking",
    "permission_restricted",
)

DEFAULT_TOKENS: tuple[DesignToken, ...] = (
    DesignToken("token.color.bg.canvas", "foundation", "#0b1020", "Application canvas background"),
    DesignToken("token.type.body.md", "foundation", "14/20", "Standard operational body text"),
    DesignToken("token.space.4", "foundation", "16", "Default spacing unit"),
    DesignToken("token.radius.md", "foundation", "8", "Card and panel radius"),
    DesignToken("token.intent.success", "semantic", "#0d9f6e", "Success semantic intent"),
    DesignToken("token.intent.warning", "semantic", "#cf7a00", "Warning semantic intent"),
    DesignToken("token.intent.critical", "semantic", "#c13636", "Critical semantic intent"),
    DesignToken("token.intent.restricted", "semantic", "#5f6673", "Restricted semantic intent"),
    DesignToken("token.stage.discovery", "domain_alias", "token.intent.warning", "Opportunity stage discovery"),
    DesignToken("token.stage.negotiation", "domain_alias", "token.intent.warning", "Opportunity stage negotiation"),
    DesignToken("token.stage.closed_won", "domain_alias", "token.intent.success", "Opportunity stage closed-won"),
    DesignToken("token.sla.healthy", "domain_alias", "token.intent.success", "SLA healthy"),
    DesignToken("token.sla.at_risk", "domain_alias", "token.intent.warning", "SLA at-risk"),
    DesignToken("token.sla.breached", "domain_alias", "token.intent.critical", "SLA breached"),
    DesignToken("token.approval.pending", "domain_alias", "token.intent.warning", "Approval pending"),
    DesignToken("token.approval.approved", "domain_alias", "token.intent.success", "Approval approved"),
    DesignToken("token.approval.rejected", "domain_alias", "token.intent.critical", "Approval rejected"),
    DesignToken("token.billing.current", "domain_alias", "token.intent.success", "Billing current"),
    DesignToken("token.billing.delinquent", "domain_alias", "token.intent.warning", "Billing delinquent"),
    DesignToken("token.billing.suspended", "domain_alias", "token.intent.restricted", "Billing suspended"),
)

DEFAULT_COMPONENTS: tuple[ComponentContract, ...] = (
    ComponentContract("shell.top_navigation", "shell", INTERACTION_STATE_CONTRACT),
    ComponentContract("shell.contextual_left_rail", "shell", INTERACTION_STATE_CONTRACT),
    ComponentContract("data.query_table", "data", INTERACTION_STATE_CONTRACT),
    ComponentContract("data.stage_board", "data", INTERACTION_STATE_CONTRACT),
    ComponentContract("input.validated_form_section", "input", INTERACTION_STATE_CONTRACT),
    ComponentContract(
        "input.policy_aware_action_bar",
        "input",
        INTERACTION_STATE_CONTRACT + ("policy_requires_approval",),
    ),
    ComponentContract("feedback.inline_validation", "feedback", INTERACTION_STATE_CONTRACT),
    ComponentContract("feedback.audit_confirmation_modal", "feedback", INTERACTION_STATE_CONTRACT),
)


class DesignSystemRegistryService:
    def __init__(
        self,
        *,
        version: str = "design-system-v1",
        tokens: tuple[DesignToken, ...] = DEFAULT_TOKENS,
        components: tuple[ComponentContract, ...] = DEFAULT_COMPONENTS,
    ) -> None:
        self._version = version
        self._tokens = tokens
        self._components = components
        self._validate()

    def snapshot(self) -> DesignSystemSnapshot:
        alias_map = {token.token_id: token.value for token in self._tokens if token.category == "domain_alias"}
        return DesignSystemSnapshot(
            version=self._version,
            token_count=len(self._tokens),
            component_count=len(self._components),
            tokens=self._tokens,
            components=self._components,
            alias_map=alias_map,
        )

    def _validate(self) -> None:
        token_ids = set()
        semantic_ids: set[str] = set()
        for token in self._tokens:
            if token.token_id in token_ids:
                raise DesignSystemValidationError(f"duplicate token id: {token.token_id}")
            token_ids.add(token.token_id)
            if token.category == "semantic":
                semantic_ids.add(token.token_id)

        for token in self._tokens:
            if token.category == "domain_alias" and token.value not in semantic_ids:
                raise DesignSystemValidationError(
                    f"domain alias must map to semantic token: {token.token_id} -> {token.value}"
                )

        component_ids = set()
        for component in self._components:
            if component.component_id in component_ids:
                raise DesignSystemValidationError(f"duplicate component id: {component.component_id}")
            component_ids.add(component.component_id)
            missing = set(INTERACTION_STATE_CONTRACT).difference(component.required_states)
            if missing:
                raise DesignSystemValidationError(
                    f"component missing required states: {component.component_id} missing {sorted(missing)}"
                )
