"""In-memory repository for lead capture, deduplication, and timeline records."""

from __future__ import annotations

from collections import defaultdict

from .entities import Lead, LeadActivity, PipelineConfig


class LeadsRepository:
    def __init__(self) -> None:
        self.leads: dict[str, Lead] = {}
        self.active_lead_by_phone: dict[tuple[str, str], str] = {}
        self.pipelines: dict[str, PipelineConfig] = {}
        self.activities: dict[str, list[LeadActivity]] = defaultdict(list)

    def save_pipeline(self, pipeline: PipelineConfig) -> PipelineConfig:
        self.pipelines[pipeline.tenant_id] = pipeline
        return pipeline

    def get_pipeline(self, tenant_id: str) -> PipelineConfig | None:
        return self.pipelines.get(tenant_id)

    def save_lead(self, lead: Lead) -> Lead:
        self.leads[lead.lead_id] = lead
        self.active_lead_by_phone[(lead.tenant_id, lead.normalized_phone)] = lead.lead_id
        return lead

    def get_active_by_phone(self, tenant_id: str, normalized_phone: str) -> Lead | None:
        lead_id = self.active_lead_by_phone.get((tenant_id, normalized_phone))
        return self.leads.get(lead_id) if lead_id else None

    def add_activity(self, activity: LeadActivity) -> None:
        self.activities[activity.lead_id].append(activity)

    def timeline(self, lead_id: str) -> tuple[LeadActivity, ...]:
        return tuple(self.activities.get(lead_id, []))
