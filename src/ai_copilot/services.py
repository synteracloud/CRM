"""Context-aware CRM copilot logic grounded in real workflow and entity data."""

from __future__ import annotations

from .entities import CopilotContext, CopilotSuggestion, CopilotSuggestionResult, CopilotValidationError


class CopilotService:
    """Builds suggestions with strict evidence requirements to avoid hallucinated actions."""

    _WORKFLOW_ACTIONS: dict[str, tuple[dict[str, object], ...]] = {
        "Lead intake, assignment, conversion": (
            {
                "action_type": "notify_owner",
                "title": "Notify assigned lead owner",
                "rationale": "Lead has an assignment update and owner follow-up is pending.",
                "required_keys": ("lead_status", "assigned_user_id", "activity_event_count_7d"),
                "predicate": lambda d: d["lead_status"] in {"new", "working"} and d["activity_event_count_7d"] == 0,
                "confidence": 0.83,
            },
            {
                "action_type": "suggest_conversion_readiness_check",
                "title": "Run lead conversion readiness check",
                "rationale": "Lead has high quality and engagement signals needed for conversion.",
                "required_keys": ("lead_score", "has_contact", "has_account"),
                "predicate": lambda d: d["lead_score"] >= 80 and d["has_contact"] is True and d["has_account"] is False,
                "confidence": 0.78,
            },
        ),
        "Opportunity pipeline & close outcomes": (
            {
                "action_type": "recommend_stage_progression",
                "title": "Advance opportunity stage review",
                "rationale": "Opportunity has sustained engagement and quote coverage to support progression.",
                "required_keys": ("opportunity_stage", "activity_event_count_30d", "quote_count"),
                "predicate": lambda d: d["opportunity_stage"] in {"qualification", "proposal"}
                and d["activity_event_count_30d"] >= 6
                and d["quote_count"] >= 1,
                "confidence": 0.76,
            },
            {
                "action_type": "trigger_close_plan",
                "title": "Initiate close-plan checklist",
                "rationale": "Opportunity is in negotiation with near-term close date.",
                "required_keys": ("opportunity_stage", "close_days_out", "amount"),
                "predicate": lambda d: d["opportunity_stage"] == "negotiation"
                and d["close_days_out"] <= 14
                and d["amount"] > 0,
                "confidence": 0.8,
            },
        ),
        "Case management & SLA": (
            {
                "action_type": "escalate_case",
                "title": "Escalate case due to SLA risk",
                "rationale": "Case is open and remaining SLA window is low.",
                "required_keys": ("case_status", "sla_minutes_remaining", "priority"),
                "predicate": lambda d: d["case_status"] == "open" and d["sla_minutes_remaining"] <= 60,
                "confidence": 0.88,
            },
        ),
    }

    def suggest(self, context: CopilotContext) -> CopilotSuggestionResult:
        self._validate_context(context)
        action_defs = self._WORKFLOW_ACTIONS.get(context.workflow_name)
        if not action_defs:
            raise CopilotValidationError(f"Unsupported workflow for copilot suggestions: {context.workflow_name}")

        suggestions: list[CopilotSuggestion] = []
        for idx, action_def in enumerate(action_defs, start=1):
            required_keys = action_def["required_keys"]
            if not all(key in context.observed_data for key in required_keys):
                continue

            predicate = action_def["predicate"]
            if not predicate(context.observed_data):
                continue

            evidence = {key: context.observed_data[key] for key in required_keys}
            suggestions.append(
                CopilotSuggestion(
                    suggestion_id=f"{context.primary_entity_id}:{idx}",
                    tenant_id=context.tenant_id,
                    action_type=str(action_def["action_type"]),
                    title=str(action_def["title"]),
                    rationale=str(action_def["rationale"]),
                    evidence=evidence,
                    confidence=float(action_def["confidence"]),
                )
            )

        return CopilotSuggestionResult(
            tenant_id=context.tenant_id,
            user_id=context.user_id,
            workflow_name=context.workflow_name,
            primary_entity_type=context.primary_entity_type,
            primary_entity_id=context.primary_entity_id,
            suggestions=tuple(suggestions),
        )

    def _validate_context(self, context: CopilotContext) -> None:
        if not context.tenant_id:
            raise CopilotValidationError("tenant_id is required")
        if not context.user_id:
            raise CopilotValidationError("user_id is required")
        if not context.primary_entity_id:
            raise CopilotValidationError("primary_entity_id is required")
        if not context.primary_entity_type:
            raise CopilotValidationError("primary_entity_type is required")
        if not isinstance(context.observed_data, dict) or not context.observed_data:
            raise CopilotValidationError("observed_data must include real workflow/entity data")
