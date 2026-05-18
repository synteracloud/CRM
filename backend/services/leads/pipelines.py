"""Default sales pipeline config for WhatsApp lead capture."""

from __future__ import annotations

from .entities import LeadStage, PipelineConfig

DEFAULT_PIPELINE_NAME = "WhatsApp Sales Pipeline"
DEFAULT_PIPELINE_STAGES: tuple[LeadStage, ...] = (
    LeadStage.NEW,
    LeadStage.QUALIFIED,
    LeadStage.NEGOTIATION,
    LeadStage.WON,
    LeadStage.LOST,
)


def default_pipeline_for_tenant(tenant_id: str) -> PipelineConfig:
    return PipelineConfig(
        pipeline_id=f"pipe-ws-{tenant_id}",
        tenant_id=tenant_id,
        name=DEFAULT_PIPELINE_NAME,
        stages=DEFAULT_PIPELINE_STAGES,
    )
