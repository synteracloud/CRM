from __future__ import annotations

import unittest

from src.contract_lifecycle_management import Contract, ContractApi, ContractService, ContractTerm


class ContractLifecycleManagementTests(unittest.TestCase):
    def _term(self, version: int = 1, start: str = "2026-01-01T00:00:00Z", end: str = "2026-12-31T00:00:00Z") -> ContractTerm:
        return ContractTerm(
            term_id=f"term-{version}",
            version=version,
            effective_from=start,
            effective_to=end,
            billing_frequency="monthly",
            auto_renew=True,
            notice_period_days=30,
            renewal_term_months=12,
            payment_terms="net_30",
            termination_for_convenience=True,
        )

    def _contract(self, contract_id: str = "ct-1") -> Contract:
        return Contract(
            contract_id=contract_id,
            tenant_id="tenant-1",
            account_id="acc-1",
            order_id="ord-1",
            subscription_id="sub-1",
            invoice_summary_id="inv-1",
            owner_user_id="user-7",
            contract_number="C-2026-0001",
            title="MSA + Order Form",
            status="draft",
            currency="USD",
            total_contract_value=125000.0,
            term_start_at="2026-01-01T00:00:00Z",
            term_end_at="2026-12-31T00:00:00Z",
            renewal_alert_days=45,
            next_renewal_at="2026-12-31T00:00:00Z",
            terms=(self._term(),),
        )

    def test_lifecycle_complete_with_renewal_and_termination_paths(self) -> None:
        service = ContractService()
        service.create_contract(self._contract())
        service.submit_for_review("ct-1")
        service.approve_contract("ct-1", approved_at="2026-01-05T00:00:00Z")
        service.activate_contract("ct-1", activated_at="2026-01-06T00:00:00Z")
        service.mark_renewal_pending("ct-1")

        renewed = service.renew_contract(
            "ct-1",
            next_renewal_at="2027-12-31T00:00:00Z",
            term=self._term(version=2, start="2027-01-01T00:00:00Z", end="2027-12-31T00:00:00Z"),
        )
        self.assertEqual(renewed.status, "active")
        self.assertEqual(len(renewed.terms), 2)

        terminated = service.terminate_contract(
            "ct-1",
            terminated_at="2027-03-15T00:00:00Z",
            reason="customer_non_renewal",
        )
        self.assertEqual(terminated.status, "terminated")

    def test_contract_links_consistent(self) -> None:
        service = ContractService()
        service.create_contract(self._contract())
        updated = service.upsert_links(
            "ct-1",
            account_id="acc-2",
            order_id="ord-2",
            subscription_id="sub-2",
            invoice_summary_id="inv-2",
        )
        self.assertEqual(updated.account_id, "acc-2")
        self.assertEqual(updated.order_id, "ord-2")
        self.assertEqual(updated.subscription_id, "sub-2")
        self.assertEqual(updated.invoice_summary_id, "inv-2")

    def test_renewal_logic_explicit_alert_window(self) -> None:
        service = ContractService()
        service.create_contract(self._contract())
        service.submit_for_review("ct-1")
        service.approve_contract("ct-1", approved_at="2026-01-05T00:00:00Z")
        service.activate_contract("ct-1", activated_at="2026-01-06T00:00:00Z")

        not_due = service.contracts_with_renewal_alerts(as_of="2026-10-15T00:00:00Z")
        self.assertEqual(len(not_due), 0)

        due = service.contracts_with_renewal_alerts(as_of="2026-11-20T00:00:00Z")
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].contract_id, "ct-1")

    def test_api_contract(self) -> None:
        service = ContractService()
        api = ContractApi(service)

        created = api.create_contract(self._contract(), request_id="req-1")
        self.assertEqual(created["meta"]["request_id"], "req-1")

        api.submit_for_review("ct-1", request_id="req-2")
        api.approve_contract("ct-1", approved_at="2026-01-05T00:00:00Z", request_id="req-3")
        active = api.activate_contract("ct-1", activated_at="2026-01-06T00:00:00Z", request_id="req-4")
        self.assertEqual(active["data"]["status"], "active")

        missing = api.get_contract("missing", request_id="req-5")
        self.assertEqual(missing["error"]["code"], "not_found")


if __name__ == "__main__":
    unittest.main()
