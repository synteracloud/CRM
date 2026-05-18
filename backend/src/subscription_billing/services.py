"""Subscription billing services: lifecycle, renewal, plan changes, and invoice hooks."""

from __future__ import annotations

from dataclasses import replace

from .entities import (
    PlanChange,
    PlanChangeError,
    RecurringInvoiceHook,
    Subscription,
    SubscriptionNotFoundError,
    SubscriptionStateError,
)


LIFECYCLE_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"trialing", "active", "canceled"},
    "trialing": {"active", "canceled", "expired"},
    "active": {"past_due", "paused", "canceled", "expired"},
    "past_due": {"active", "canceled", "expired"},
    "paused": {"active", "canceled", "expired"},
    "canceled": set(),
    "expired": set(),
}

TERMINAL_STATES: set[str] = {"canceled", "expired"}


class SubscriptionBillingService:
    def __init__(self) -> None:
        self._subscriptions: dict[str, Subscription] = {}
        self._plan_changes: dict[str, PlanChange] = {}
        self._invoice_hooks: dict[str, RecurringInvoiceHook] = {}

    def list_subscriptions(self) -> list[Subscription]:
        return list(self._subscriptions.values())

    def create_subscription(self, subscription: Subscription) -> Subscription:
        if subscription.subscription_id in self._subscriptions:
            raise SubscriptionStateError(f"Subscription already exists: {subscription.subscription_id}")
        if subscription.status != "draft":
            raise SubscriptionStateError("Subscription must be created in draft status.")
        self._subscriptions[subscription.subscription_id] = subscription
        return subscription

    def get_subscription(self, subscription_id: str) -> Subscription:
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            raise SubscriptionNotFoundError(f"Subscription not found: {subscription_id}")
        return subscription

    def transition_subscription(self, subscription_id: str, to_status: str, at_time: str) -> Subscription:
        subscription = self.get_subscription(subscription_id)
        allowed = LIFECYCLE_TRANSITIONS[subscription.status]
        if to_status not in allowed:
            raise SubscriptionStateError(
                f"Invalid transition: {subscription.status} -> {to_status}. allowed={sorted(allowed)}"
            )

        updates: dict[str, str] = {"status": to_status}
        if to_status in TERMINAL_STATES:
            updates["end_date"] = at_time

        updated = replace(subscription, **updates)
        self._subscriptions[subscription_id] = updated

        if to_status == "active" and subscription.status in {"draft", "trialing", "past_due", "paused"}:
            self._queue_invoice_hook(
                subscription=updated,
                trigger_type="activation",
                invoice_reason="initial",
                run_at=at_time,
                metadata={"from_status": subscription.status, "to_status": to_status},
            )

        return updated

    def request_plan_change(self, change: PlanChange) -> PlanChange:
        subscription = self.get_subscription(change.subscription_id)
        if subscription.status in TERMINAL_STATES:
            raise PlanChangeError(f"Cannot change plan for terminal subscription status={subscription.status}")
        if change.from_plan_code != subscription.plan_code:
            raise PlanChangeError(
                "Plan change baseline mismatch: from_plan_code must match current subscription plan_code."
            )
        if change.from_plan_code == change.to_plan_code:
            raise PlanChangeError("Plan change must target a different plan_code.")

        if change.change_kind == "upgrade" and change.apply_on_renewal:
            raise PlanChangeError("Upgrades must be applied immediately; apply_on_renewal must be false.")
        if change.change_kind == "downgrade" and not change.apply_on_renewal:
            raise PlanChangeError("Downgrades must be deferred to renewal; apply_on_renewal must be true.")

        self._plan_changes[change.plan_change_id] = change

        if change.change_kind == "upgrade":
            updated = replace(subscription, plan_code=change.to_plan_code)
            self._subscriptions[subscription.subscription_id] = updated
            self._queue_invoice_hook(
                subscription=updated,
                trigger_type="plan_change",
                invoice_reason="proration",
                run_at=change.effective_at,
                metadata={"change_kind": change.change_kind, "from_plan_code": change.from_plan_code},
            )

        return change

    def renew_subscription(
        self,
        subscription_id: str,
        *,
        renewal_date: str,
        next_end_date: str,
        hook_id: str,
    ) -> Subscription:
        subscription = self.get_subscription(subscription_id)

        if subscription.status in TERMINAL_STATES:
            raise SubscriptionStateError(f"Cannot renew terminal subscription status={subscription.status}")
        if subscription.renewal_date != renewal_date:
            raise SubscriptionStateError(
                "Deterministic renewal check failed: provided renewal_date must match current subscription.renewal_date"
            )

        updated = replace(subscription, renewal_date=next_end_date, end_date=next_end_date)

        for change in self._pending_plan_changes(subscription_id):
            if change.apply_on_renewal and change.effective_at == renewal_date:
                updated = replace(updated, plan_code=change.to_plan_code)
                self._queue_invoice_hook(
                    subscription=updated,
                    trigger_type="plan_change",
                    invoice_reason="recurring",
                    run_at=renewal_date,
                    metadata={"change_kind": change.change_kind, "from_plan_code": change.from_plan_code},
                )

        self._subscriptions[subscription_id] = updated
        self._queue_invoice_hook(
            subscription=updated,
            trigger_type="renewal",
            invoice_reason="recurring",
            run_at=renewal_date,
            metadata={"renewal_for": renewal_date, "hook_id": hook_id},
        )
        return updated

    def list_invoice_hooks(self, subscription_id: str | None = None) -> list[RecurringInvoiceHook]:
        hooks = list(self._invoice_hooks.values())
        if subscription_id is None:
            return hooks
        return [hook for hook in hooks if hook.subscription_id == subscription_id]

    def _pending_plan_changes(self, subscription_id: str) -> list[PlanChange]:
        return sorted(
            [change for change in self._plan_changes.values() if change.subscription_id == subscription_id],
            key=lambda item: item.requested_at,
        )

    def _queue_invoice_hook(
        self,
        *,
        subscription: Subscription,
        trigger_type: str,
        invoice_reason: str,
        run_at: str,
        metadata: dict[str, str],
    ) -> RecurringInvoiceHook:
        hook = RecurringInvoiceHook(
            hook_id=f"hook-{len(self._invoice_hooks) + 1}",
            tenant_id=subscription.tenant_id,
            subscription_id=subscription.subscription_id,
            trigger_type=trigger_type,
            invoice_reason=invoice_reason,
            run_at=run_at,
            metadata=metadata,
        )
        self._invoice_hooks[hook.hook_id] = hook
        return hook
