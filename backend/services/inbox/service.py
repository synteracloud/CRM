"""InboxService — assignment pipeline, claim/handoff logic, presence management.

Domain spec: backend/docs/domain/shared-inbox.md §3, §4
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from services.inbox.entities import (
    AssignmentReason,
    HandoffReason,
    INTENT_QUEUE_MAP,
    InboxRoutingStrategy,
    is_eligible_for_auto_assign,
    is_eligible_to_claim,
)


class InboxAssignmentError(ValueError):
    """Raised when an assignment or handoff precondition is violated."""


class InboxService:
    """Stateless service for shared inbox business rules."""

    # ── Queue routing ─────────────────────────────────────────────────────────

    def resolve_queue(self, intent: Optional[str], queues: list[dict]) -> Optional[dict]:
        """
        Select the target InboxQueue for a new conversation based on intent.
        Returns the matched queue dict, or the first active queue as fallback.
        Spec §3.2.
        """
        target_name = INTENT_QUEUE_MAP.get(intent or "", "General")
        active = [q for q in queues if q.get("is_active", True)]
        match = next((q for q in active if q["name"] == target_name), None)
        return match or (active[0] if active else None)

    # ── Auto-assign pipeline ──────────────────────────────────────────────────

    def select_agent_round_robin(
        self,
        eligible_agents: list[dict],
        last_assigned_index: int = 0,
    ) -> Optional[dict]:
        """Return next eligible agent in round-robin order."""
        if not eligible_agents:
            return None
        return eligible_agents[last_assigned_index % len(eligible_agents)]

    def select_agent_least_loaded(self, eligible_agents: list[dict]) -> Optional[dict]:
        """Return eligible agent with lowest open_conversation_count."""
        if not eligible_agents:
            return None
        return min(eligible_agents, key=lambda a: a.get("open_conversation_count", 0))

    def auto_assign(
        self,
        queue: dict,
        presence_list: list[dict],
        last_assigned_index: int = 0,
    ) -> Optional[str]:
        """
        Select agent for auto-assignment based on queue routing strategy.
        Returns agent_id or None if no eligible agent is available.
        Spec §3.1.
        """
        if not queue.get("auto_assign", True):
            return None

        eligible = [p for p in presence_list if is_eligible_for_auto_assign(p)]
        if not eligible:
            return None

        strategy = queue.get("routing_strategy", "round_robin")
        if strategy == InboxRoutingStrategy.LEAST_LOADED:
            agent = self.select_agent_least_loaded(eligible)
        else:  # round_robin and skill_based fall back to round_robin
            agent = self.select_agent_round_robin(eligible, last_assigned_index)

        return agent["agent_id"] if agent else None

    # ── Claim ─────────────────────────────────────────────────────────────────

    def validate_claim(
        self,
        conversation: dict,
        claiming_agent_id: str,
        agent_presence: dict,
    ) -> None:
        """
        Validate that a conversation can be claimed.
        Raises InboxAssignmentError if any guard fails.
        Spec §3.3.
        """
        if conversation.get("assigned_agent_id"):
            raise InboxAssignmentError(
                "Conversation is already assigned. Use handoff to reassign."
            )
        if not is_eligible_to_claim(agent_presence):
            raise InboxAssignmentError(
                f"Agent {claiming_agent_id} is not eligible to claim: "
                f"status={agent_presence.get('status')}, "
                f"count={agent_presence.get('open_conversation_count')}/{agent_presence.get('max_concurrent')}."
            )

    # ── Handoff ───────────────────────────────────────────────────────────────

    def validate_handoff(
        self,
        conversation: dict,
        requesting_agent_id: str,
        actor_role: str,
    ) -> None:
        """
        Validate that an agent can hand off a conversation.
        Raises InboxAssignmentError if the agent doesn't own the conversation
        and is not a supervisor.
        Spec §3.4.
        """
        is_supervisor = actor_role in ("manager", "admin", "tenant_admin", "tenant_owner")
        assigned = conversation.get("assigned_agent_id")

        if not is_supervisor and assigned != requesting_agent_id:
            raise InboxAssignmentError(
                "Only the assigned agent or a supervisor can hand off this conversation."
            )

    # ── Presence ──────────────────────────────────────────────────────────────

    def compute_presence_after_conversation_change(
        self,
        current_count: int,
        max_concurrent: int,
        delta: int,
    ) -> dict:
        """
        Compute presence status update after open_conversation_count changes.
        Returns dict with updated count + status suggestion.
        Spec §4.1: auto-set busy when count >= max_concurrent.
        """
        new_count = max(0, current_count + delta)
        suggested_status = "busy" if new_count >= max_concurrent else None
        return {"open_conversation_count": new_count, "suggested_status": suggested_status}
