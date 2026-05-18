"""In-memory repository for lead capture, deduplication, and timeline records."""

from __future__ import annotations

from collections import defaultdict

from .entities import Lead, LeadActivity, PipelineConfig
from .fuzzy_match import FuzzyMatchResult, suggest_duplicate


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

    def detect_duplicate_contact(self, phone_e164: str, tenant_id: str) -> Lead | None:
        """Return existing lead for the given E.164 phone within a tenant, or None.

        Anti-Lead Loss Guarantee: same phone number → same contact. Never create a
        duplicate Contact stub when a lead already exists for this phone.

        Docs: docs/whatsapp-execution-model.md §11 — Anti-Lead Loss Guarantee
        """
        return self.get_active_by_phone(tenant_id, phone_e164)

    def detect_duplicate_by_name(
        self,
        candidate_name: str,
        tenant_id: str,
        feature_flags: dict | None = None,
        max_suggestions: int = 3,
    ) -> FuzzyMatchResult:
        """Return fuzzy-match duplicate suggestions for a candidate contact name.

        Gated behind the ``contact.fuzzy_name_match`` feature flag — returns an
        empty result immediately when the flag is absent or disabled.

        Never auto-merges; result is always advisory (action="suggest_merge").

        Docs: docs/whatsapp-execution-model.md §11 — Anti-Lead Loss Guarantee
              pending.md P-018 — Fuzzy name match for duplicate contact detection
              BEHAV-002

        Args:
            candidate_name:  Name of the incoming contact.
            tenant_id:       Tenant scope — only compares leads within the tenant.
            feature_flags:   Dict of enabled flags for this tenant.
                             Expected shape: {"contact.fuzzy_name_match": True, ...}
            max_suggestions: Maximum number of suggestions to surface (default 3).

        Returns:
            FuzzyMatchResult — empty suggestions tuple when flag disabled or
            no contacts meet the 0.85 threshold.
        """
        from .fuzzy_match import SIMILARITY_THRESHOLD

        _flags = feature_flags or {}
        if not _flags.get("contact.fuzzy_name_match", False):
            return FuzzyMatchResult(
                candidate_name=candidate_name,
                suggestions=(),
                threshold_used=SIMILARITY_THRESHOLD,
            )

        # Build contact list from in-memory leads scoped to the tenant.
        # Excludes leads without a contact name (phone-only leads).
        existing_contacts = [
            {
                "contact_id": lead.lead_id,
                "contact_name": lead.contact_name,
            }
            for lead in self.leads.values()
            if lead.tenant_id == tenant_id and getattr(lead, "contact_name", None)
        ]

        return suggest_duplicate(
            candidate_name=candidate_name,
            existing_contacts=existing_contacts,
            max_suggestions=max_suggestions,
        )

    def add_activity(self, activity: LeadActivity) -> None:
        self.activities[activity.lead_id].append(activity)

    def timeline(self, lead_id: str) -> tuple[LeadActivity, ...]:
        return tuple(self.activities.get(lead_id, []))
