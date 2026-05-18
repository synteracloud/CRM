from __future__ import annotations

import unittest

from src.subscription_billing import LIFECYCLE_TRANSITIONS, PlanChange, Subscription, SubscriptionBillingService, SubscriptionStateError


class SubscriptionBillingServiceTests(unittest.TestCase):
    def _build_subscription(self) -> Subscription:
        return Subscription(
            subscription_id="sub-1",
            tenant_id="tenant-1",
            account_id="acct-1",
            quote_id="q-1",
            external_subscription_ref="stripe_sub_123",
            plan_code="growth-monthly",
            status="draft",
            start_date="2026-04-01",
            end_date="2026-04-30",
            renewal_date="2026-04-30",
            created_at="2026-03-29T00:00:00Z",
        )

    def test_subscription_states_complete(self) -> None:
        expected_states = {"draft", "trialing", "active", "past_due", "paused", "canceled", "expired"}
        self.assertEqual(set(LIFECYCLE_TRANSITIONS.keys()), expected_states)
        self.assertEqual(LIFECYCLE_TRANSITIONS["canceled"], set())
        self.assertEqual(LIFECYCLE_TRANSITIONS["expired"], set())

    def test_renewal_logic_is_deterministic(self) -> None:
        service = SubscriptionBillingService()
        service.create_subscription(self._build_subscription())
        service.transition_subscription("sub-1", to_status="active", at_time="2026-04-01")

        with self.assertRaises(SubscriptionStateError):
            service.renew_subscription(
                "sub-1",
                renewal_date="2026-05-01",
                next_end_date="2026-05-31",
                hook_id="renew-1",
            )

        renewed = service.renew_subscription(
            "sub-1",
            renewal_date="2026-04-30",
            next_end_date="2026-05-31",
            hook_id="renew-2",
        )
        self.assertEqual(renewed.renewal_date, "2026-05-31")

    def test_upgrade_downgrade_and_billing_hooks(self) -> None:
        service = SubscriptionBillingService()
        service.create_subscription(self._build_subscription())
        service.transition_subscription("sub-1", to_status="active", at_time="2026-04-01")

        service.request_plan_change(
            PlanChange(
                plan_change_id="pc-1",
                tenant_id="tenant-1",
                subscription_id="sub-1",
                from_plan_code="growth-monthly",
                to_plan_code="enterprise-monthly",
                change_kind="upgrade",
                requested_at="2026-04-10T00:00:00Z",
                effective_at="2026-04-10",
                apply_on_renewal=False,
            )
        )
        self.assertEqual(service.get_subscription("sub-1").plan_code, "enterprise-monthly")

        service.request_plan_change(
            PlanChange(
                plan_change_id="pc-2",
                tenant_id="tenant-1",
                subscription_id="sub-1",
                from_plan_code="enterprise-monthly",
                to_plan_code="growth-monthly",
                change_kind="downgrade",
                requested_at="2026-04-20T00:00:00Z",
                effective_at="2026-04-30",
                apply_on_renewal=True,
            )
        )

        renewed = service.renew_subscription(
            "sub-1",
            renewal_date="2026-04-30",
            next_end_date="2026-05-31",
            hook_id="renew-3",
        )
        self.assertEqual(renewed.plan_code, "growth-monthly")

        hook_reasons = [hook.invoice_reason for hook in service.list_invoice_hooks("sub-1")]
        self.assertIn("initial", hook_reasons)
        self.assertIn("proration", hook_reasons)
        self.assertIn("recurring", hook_reasons)


if __name__ == "__main__":
    unittest.main()
