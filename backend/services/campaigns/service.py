"""CampaignsService — state machine, dispatch helpers, attribution logic.

Domain spec: backend/docs/domain/marketing-campaigns.md §3, §5, §6
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from services.campaigns.entities import (
    ALLOWED_TRANSITIONS,
    CampaignTransitionError,
    ConversionType,
    validate_activation_guards,
    validate_transition,
)


class CampaignsService:
    """Stateless service for Campaign domain business rules."""

    # ── State machine ─────────────────────────────────────────────────────────

    def apply_transition(
        self,
        campaign: dict,
        target_status: str,
        *,
        template: Optional[dict] = None,
        segment_size: int = 0,
        scheduled_at: Optional[datetime] = None,
    ) -> dict:
        """
        Validate and return field updates for a status transition.
        Raises CampaignTransitionError on invalid transition or guard failure.
        """
        validate_transition(campaign["status"], target_status)

        now = datetime.now(timezone.utc)
        updates: dict = {"status": target_status, "updated_at": now}

        if target_status in ("active", "scheduled"):
            validate_activation_guards(campaign, template=template, segment_size=segment_size)
            if target_status == "active":
                updates["activated_at"] = now
            if target_status == "scheduled":
                if not scheduled_at:
                    raise CampaignTransitionError(
                        "Transition to 'scheduled' requires scheduled_at to be set."
                    )
                updates["scheduled_at"] = scheduled_at

        if target_status == "paused":
            updates["paused_at"] = now

        if target_status == "completed":
            updates["completed_at"] = now

        if target_status == "cancelled":
            updates["cancelled_at"] = now

        if target_status == "draft" and campaign["status"] == "scheduled":
            # Rescheduling: clear scheduled_at
            updates["scheduled_at"] = None

        return updates

    # ── Idempotency key ───────────────────────────────────────────────────────

    def make_send_idempotency_key(self, campaign_id: str, contact_id: str) -> str:
        """Spec §2.4: campaign_{campaign_id}_contact_{contact_id}"""
        return f"campaign_{campaign_id}_contact_{contact_id}"

    # ── Opt-in gate ───────────────────────────────────────────────────────────

    def should_skip_contact(
        self,
        contact: dict,
        channel: str,
    ) -> Optional[str]:
        """
        Return SkipReason if the contact should be skipped, else None.
        Spec §1.2 rule 3: WhatsApp opt-in gate.
        """
        if channel == "whatsapp_broadcast" and not contact.get("whatsapp_opted_in", False):
            return "not_opted_in"
        if channel == "whatsapp_broadcast" and not contact.get("phone_e164"):
            return "no_channel"
        if channel == "email" and not contact.get("email"):
            return "no_channel"
        if channel == "sms" and not contact.get("phone_e164"):
            return "no_channel"
        return None

    # ── Merge tag resolution ──────────────────────────────────────────────────

    def resolve_merge_tags(self, template_body: str, contact: dict) -> str:
        """
        Replace {{contact.name}}, {{contact.company}} etc. with contact field values.
        Spec §2.3.
        """
        replacements = {
            "{{contact.name}}":    contact.get("display_name") or contact.get("name") or "Valued Customer",
            "{{contact.company}}": contact.get("account_name") or contact.get("company") or "",
            "{{contact.phone}}":   contact.get("phone_e164") or "",
        }
        result = template_body
        for tag, value in replacements.items():
            result = result.replace(tag, str(value))
        return result

    # ── Attribution ───────────────────────────────────────────────────────────

    def is_within_attribution_window(
        self,
        send_at: datetime,
        event_at: datetime,
        window_days: int = 30,
    ) -> bool:
        """
        Return True if event_at is within the attribution window from send_at.
        Spec §6.1.
        """
        delta = event_at - send_at
        return 0 <= delta.total_seconds() <= window_days * 86400

    def determine_conversion_type(
        self,
        entity_type: str,
        is_won: bool = False,
    ) -> str:
        """Map entity creation event to ConversionType. Spec §6.2."""
        if entity_type == "lead":
            return ConversionType.LEAD_CREATED
        if entity_type == "opportunity" and is_won:
            return ConversionType.OPPORTUNITY_WON
        return ConversionType.OPPORTUNITY_CREATED

    # ── Delivery stats ────────────────────────────────────────────────────────

    def compute_rates(self, campaign: dict) -> dict:
        """Compute delivery_rate, open_rate, reply_rate as percentages."""
        sent = campaign.get("sent_count", 0)
        if sent == 0:
            return {"delivery_rate": 0, "open_rate": 0, "reply_rate": 0}
        return {
            "delivery_rate": round(campaign.get("delivered_count", 0) / sent * 100, 1),
            "open_rate":     round(campaign.get("opened_count", 0)   / sent * 100, 1),
            "reply_rate":    round(campaign.get("replied_count", 0)  / sent * 100, 1),
        }
