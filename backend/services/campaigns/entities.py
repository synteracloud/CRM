"""Campaign domain entities: status enum, state machine, transition guards.

Domain spec: backend/docs/domain/marketing-campaigns.md §3
P-017: Urdu approval gate enforced in apply_transition().
"""
from __future__ import annotations

from enum import Enum
from typing import Optional


class CampaignStatus(str, Enum):
    DRAFT     = "draft"
    SCHEDULED = "scheduled"
    ACTIVE    = "active"
    PAUSED    = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, Enum):
    WHATSAPP_BROADCAST = "whatsapp_broadcast"
    EMAIL              = "email"
    SMS                = "sms"


class SendStatus(str, Enum):
    QUEUED    = "queued"
    SENT      = "sent"
    DELIVERED = "delivered"
    READ      = "read"
    REPLIED   = "replied"
    FAILED    = "failed"
    SKIPPED   = "skipped"


class SkipReason(str, Enum):
    NOT_OPTED_IN = "not_opted_in"
    NO_CHANNEL   = "no_channel"
    DUPLICATE    = "duplicate"
    OPTED_OUT    = "opted_out"


class ConversionType(str, Enum):
    LEAD_CREATED         = "lead_created"
    OPPORTUNITY_CREATED  = "opportunity_created"
    OPPORTUNITY_WON      = "opportunity_won"


# Spec §3.1 — allowed transitions
ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "draft":     ["scheduled", "active", "cancelled"],
    "scheduled": ["active", "draft", "cancelled"],
    "active":    ["paused", "completed", "cancelled"],
    "paused":    ["active", "cancelled"],
    "completed": [],   # terminal
    "cancelled": [],   # terminal
}

# Spec §5.2 — WhatsApp rate limit: 80 msg/min
RATE_LIMIT_PER_MIN: dict[str, int] = {
    "whatsapp_broadcast": 80,
    "sms":   200,
    "email": 500,
}


class CampaignTransitionError(ValueError):
    """Raised when a campaign state transition is invalid or a guard fails."""


def validate_transition(from_status: str, to_status: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(from_status, [])
    if to_status not in allowed:
        raise CampaignTransitionError(
            f"Transition {from_status!r} → {to_status!r} is not permitted. "
            f"Allowed from {from_status!r}: {allowed}"
        )


def validate_activation_guards(
    campaign: dict,
    template: Optional[dict] = None,
    segment_size: int = 0,
) -> None:
    """
    Enforce all pre-activation guards.
    Raises CampaignTransitionError if any guard fails.
    Spec §3.2 + §1.2.
    """
    if not campaign.get("segment_id"):
        raise CampaignTransitionError(
            "Activation blocked: campaign has no segment_id."
        )
    if not campaign.get("template_id"):
        raise CampaignTransitionError(
            "Activation blocked: campaign has no template_id."
        )
    if segment_size < 1:
        raise CampaignTransitionError(
            "Activation blocked: segment resolves to 0 eligible contacts."
        )
    if template and template.get("channel") == CampaignType.WHATSAPP_BROADCAST:
        if template.get("meta_template_status") not in ("approved", None):
            raise CampaignTransitionError(
                f"Activation blocked: WhatsApp template meta_template_status is "
                f"{template.get('meta_template_status')!r} — must be 'approved'."
            )
    # P-017 gate: Urdu approval required
    if template and template.get("is_urdu") and not campaign.get("urdu_approved_by"):
        raise CampaignTransitionError(
            "Activation blocked (P-017): Urdu template requires urdu_approved_by to be set. "
            "A native Urdu speaker must sign off before this campaign can be activated."
        )
