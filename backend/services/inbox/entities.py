"""Inbox domain entities: presence status, assignment reason, handoff reason enums.

Domain spec: backend/docs/domain/shared-inbox.md §2, §3, §4
"""
from __future__ import annotations

from enum import Enum


class PresenceStatus(str, Enum):
    ONLINE  = "online"
    AWAY    = "away"
    BUSY    = "busy"
    OFFLINE = "offline"


class AssignmentReason(str, Enum):
    AUTO_ROUTED         = "auto_routed"
    CLAIMED             = "claimed"
    SUPERVISOR_ASSIGNED = "supervisor_assigned"
    HANDOFF             = "handoff"


class HandoffReason(str, Enum):
    AGENT_UNAVAILABLE  = "agent_unavailable"
    CAPACITY_EXCEEDED  = "capacity_exceeded"
    SKILL_MATCH        = "skill_match"
    MANUAL             = "manual"
    ESCALATION         = "escalation"


class InboxRoutingStrategy(str, Enum):
    ROUND_ROBIN  = "round_robin"
    LEAST_LOADED = "least_loaded"
    CLAIM_FIRST  = "claim_first"
    SKILL_BASED  = "skill_based"


# Intent → default queue name mapping — spec §3.2
INTENT_QUEUE_MAP: dict[str, str] = {
    "lead_inquiry":       "Sales",
    "payment_query":      "Billing",
    "support_request":    "Support",
    "follow_up_response": "Sales",
}

# Routing-eligible presence statuses (for auto-assign and claim)
AUTO_ASSIGN_ELIGIBLE = {PresenceStatus.ONLINE}
CLAIM_ELIGIBLE       = {PresenceStatus.ONLINE, PresenceStatus.AWAY}

# Agent eligibility check — spec §2.3
def is_eligible_for_auto_assign(presence: dict) -> bool:
    return (
        presence.get("status") == PresenceStatus.ONLINE
        and presence.get("open_conversation_count", 0) < presence.get("max_concurrent", 10)
    )


def is_eligible_to_claim(presence: dict) -> bool:
    return (
        presence.get("status") in (PresenceStatus.ONLINE, PresenceStatus.AWAY)
        and presence.get("open_conversation_count", 0) < presence.get("max_concurrent", 10)
    )
