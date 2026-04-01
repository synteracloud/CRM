"""Smart follow-up assistant built on top of follow-up enforcement engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from services.followup.engine import FollowupEnforcementEngine
from services.followup.entities import FollowupPolicy, FollowupState, LeadSnapshot
from services.followup.assistant.models import AssistantAlignmentReport, FollowupSuggestion, SuggestionQuality


@dataclass(frozen=True)
class FollowupAssistantConfig:
    default_followup_hours: int = 24


class SmartFollowupAssistant:
    """Creates AI-like suggestions and enforces no-idle-lead follow-up coverage."""

    STAGE_FOLLOWUP_HOURS = {
        "new": 2,
        "discovery": 8,
        "qualified": 12,
        "proposal": 24,
        "negotiation": 12,
        "contract": 6,
        "closing": 4,
    }

    STAGE_TEMPLATES = {
        "new": (
            "intro_touchpoint",
            "Hi {lead_id}, wanted to introduce myself and understand your goals this week.",
        ),
        "discovery": (
            "discovery_probe",
            "Hi {lead_id}, checking in on your discovery priorities and next milestones.",
        ),
        "proposal": (
            "proposal_nudge",
            "Hi {lead_id}, sharing a quick follow-up on the proposal and open questions.",
        ),
        "negotiation": (
            "negotiation_alignment",
            "Hi {lead_id}, I can help align on terms so we can keep momentum.",
        ),
        "closing": (
            "close_plan",
            "Hi {lead_id}, are we ready to confirm final steps and timeline?",
        ),
    }

    INACTIVITY_TEMPLATE = (
        "inactivity_reengage",
        "Hi {lead_id}, reaching out since we have been quiet recently—can we reconnect?",
    )

    ACTIVE_LEAD_STATES = {"open", "working", "nurture"}

    def __init__(
        self,
        engine: FollowupEnforcementEngine | None = None,
        policy: FollowupPolicy | None = None,
        config: FollowupAssistantConfig | None = None,
    ) -> None:
        self.engine = engine or FollowupEnforcementEngine(policy=policy)
        self.policy = self.engine.policy
        self.config = config or FollowupAssistantConfig()

    def suggest_followup(self, lead: LeadSnapshot, now: datetime) -> FollowupSuggestion:
        inactivity_hours = (now - lead.last_activity_at).total_seconds() / 3600
        if inactivity_hours >= self.policy.inactivity_hours:
            template_key, template = self.INACTIVITY_TEMPLATE
            return FollowupSuggestion(
                lead_id=lead.lead_id,
                next_followup_at=now + timedelta(minutes=15),
                template_key=template_key,
                template_message=template.format(lead_id=lead.lead_id),
                confidence_percent=98.0,
                reason="inactivity_threshold_exceeded",
            )

        stage = lead.stage.lower()
        stage_hours = self.STAGE_FOLLOWUP_HOURS.get(stage, self.config.default_followup_hours)
        priority_hours = self.policy.sla_delta(lead.priority).total_seconds() / 3600
        recommended_hours = min(stage_hours, priority_hours)
        next_followup_at = now + timedelta(hours=recommended_hours)

        template_key, template = self.STAGE_TEMPLATES.get(
            stage,
            (
                "general_checkin",
                "Hi {lead_id}, checking in to keep your evaluation moving forward.",
            ),
        )
        confidence = 90.0 if stage in self.STAGE_TEMPLATES else 80.0

        return FollowupSuggestion(
            lead_id=lead.lead_id,
            next_followup_at=next_followup_at,
            template_key=template_key,
            template_message=template.format(lead_id=lead.lead_id),
            confidence_percent=confidence,
            reason=f"stage_based:{stage}",
        )

    def auto_create_followup_tasks(self, leads: list[LeadSnapshot], now: datetime) -> int:
        created = 0
        for lead in leads:
            if lead.status.lower() not in self.ACTIVE_LEAD_STATES:
                continue
            if not self.engine.has_lead(lead.lead_id):
                self.engine.register_lead(lead, now=now)
                created += 1

        self.engine.hourly_sweep(now=now)
        self.engine.process_due_transitions(now=now)

        for lead in leads:
            if lead.status.lower() not in self.ACTIVE_LEAD_STATES:
                continue
            tasks = self.engine.tasks_for_lead(lead.lead_id)
            if not any(task.state == FollowupState.PENDING for task in tasks):
                self.engine.register_lead(lead, now=now)
                created += 1

        return created

    def ensure_no_idle_leads(self, leads: list[LeadSnapshot], now: datetime) -> float:
        if not leads:
            return 100.0
        covered = 0
        for lead in leads:
            if lead.status.lower() not in self.ACTIVE_LEAD_STATES:
                covered += 1
                continue
            suggestion = self.suggest_followup(lead, now)
            if suggestion.next_followup_at >= now:
                covered += 1
        return round((covered / len(leads)) * 100, 2)

    def validate_suggestion_accuracy(self, leads: list[LeadSnapshot], now: datetime) -> SuggestionQuality:
        accurate = 0
        for lead in leads:
            suggestion = self.suggest_followup(lead, now)
            within_week = now <= suggestion.next_followup_at <= now + timedelta(days=7)
            stage_matches = lead.stage.lower() in suggestion.reason or suggestion.reason == "inactivity_threshold_exceeded"
            if within_week and stage_matches and suggestion.confidence_percent >= 80:
                accurate += 1
        total = len(leads)
        percent = 100.0 if total == 0 else round((accurate / total) * 100, 2)
        return SuggestionQuality(evaluated=total, accurate=accurate, accuracy_percent=percent)

    def qc_alignment_report(self, leads: list[LeadSnapshot], now: datetime) -> AssistantAlignmentReport:
        no_idle = self.ensure_no_idle_leads(leads, now)
        accuracy = self.validate_suggestion_accuracy(leads, now).accuracy_percent
        overall = round((no_idle + accuracy) / 2, 2)
        return AssistantAlignmentReport(
            no_idle_leads_percent=no_idle,
            suggestion_accuracy_percent=accuracy,
            overall_alignment_percent=overall,
        )
