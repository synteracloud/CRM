from __future__ import annotations

import unittest

from src.territory_management import (
    PrincipalContext,
    Territory,
    TerritoryManagementApi,
    TerritoryManagementService,
    TerritoryRule,
)


class TerritoryManagementServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TerritoryManagementService()
        self.admin = PrincipalContext(
            user_id="u-admin",
            tenant_id="tenant-1",
            role="Tenant Admin",
            permissions=frozenset({"records.read", "records.update", "records.create"}),
        )
        self.agent = PrincipalContext(
            user_id="u-ae-1",
            tenant_id="tenant-1",
            role="Agent",
            permissions=frozenset({"records.read"}),
        )

    def test_hierarchical_model_and_multi_subject_assignment_is_deterministic(self) -> None:
        self.service.create_territory(
            Territory(
                territory_id="t-na",
                tenant_id="tenant-1",
                name="North America",
                code="NA",
                parent_territory_id=None,
                level=0,
            )
        )
        self.service.create_territory(
            Territory(
                territory_id="t-na-west",
                tenant_id="tenant-1",
                name="NA West",
                code="NA-W",
                parent_territory_id="t-na",
                level=1,
            )
        )

        self.service.register_rule(
            TerritoryRule(
                rule_id="r-account-enterprise-west",
                tenant_id="tenant-1",
                territory_id="t-na-west",
                subject_type="account",
                priority=90,
                criteria={"tenant_id": "tenant-1", "region": "west", "segment": "enterprise"},
                owner_type="team",
                owner_id="team-west-enterprise",
            )
        )
        self.service.register_rule(
            TerritoryRule(
                rule_id="r-account-west-fallback",
                tenant_id="tenant-1",
                territory_id="t-na-west",
                subject_type="account",
                priority=80,
                criteria={"tenant_id": "tenant-1", "region": "west"},
                owner_type="team",
                owner_id="team-west-general",
            )
        )
        self.service.register_rule(
            TerritoryRule(
                rule_id="r-lead-smb-west",
                tenant_id="tenant-1",
                territory_id="t-na-west",
                subject_type="lead",
                priority=70,
                criteria={"tenant_id": "tenant-1", "region": "west", "segment": "smb"},
                owner_type="user",
                owner_id="u-ae-1",
            )
        )
        self.service.register_rule(
            TerritoryRule(
                rule_id="r-user-west",
                tenant_id="tenant-1",
                territory_id="t-na-west",
                subject_type="user",
                priority=10,
                criteria={"tenant_id": "tenant-1", "region": "west"},
                owner_type="team",
                owner_id="team-west-general",
            )
        )
        self.service.register_rule(
            TerritoryRule(
                rule_id="r-team-west",
                tenant_id="tenant-1",
                territory_id="t-na-west",
                subject_type="team",
                priority=10,
                criteria={"tenant_id": "tenant-1", "region": "west"},
                owner_type="team",
                owner_id="team-west-general",
            )
        )

        account_assignment = self.service.assign_subject(
            principal=self.admin,
            subject_type="account",
            subject_id="acct-1",
            subject_facts={"tenant_id": "tenant-1", "region": "west", "segment": "enterprise"},
            assigned_at="2026-03-29T00:00:00Z",
        )
        lead_assignment = self.service.assign_subject(
            principal=self.admin,
            subject_type="lead",
            subject_id="lead-1",
            subject_facts={"tenant_id": "tenant-1", "region": "west", "segment": "smb"},
            assigned_at="2026-03-29T00:00:00Z",
        )
        user_assignment = self.service.assign_subject(
            principal=self.admin,
            subject_type="user",
            subject_id="u-ae-2",
            subject_facts={"tenant_id": "tenant-1", "region": "west"},
            assigned_at="2026-03-29T00:00:00Z",
        )
        team_assignment = self.service.assign_subject(
            principal=self.admin,
            subject_type="team",
            subject_id="team-west-general",
            subject_facts={"tenant_id": "tenant-1", "region": "west"},
            assigned_at="2026-03-29T00:00:00Z",
        )

        self.assertEqual(account_assignment.assignment_rule, "r-account-enterprise-west")
        self.assertEqual(account_assignment.owner_id, "team-west-enterprise")
        self.assertEqual(lead_assignment.owner_id, "u-ae-1")
        self.assertEqual(user_assignment.subject_type, "user")
        self.assertEqual(team_assignment.subject_type, "team")

        coverage = self.service.get_coverage(principal=self.admin, territory_id="t-na-west")
        self.assertEqual(coverage["covered_subject_count"], 4)
        self.assertEqual(coverage["lineage"], ("t-na-west", "t-na"))

    def test_security_boundaries_prevent_cross_tenant_and_unscoped_access(self) -> None:
        self.service.create_territory(
            Territory(
                territory_id="t-eu",
                tenant_id="tenant-2",
                name="Europe",
                code="EU",
                parent_territory_id=None,
                level=0,
            )
        )

        api = TerritoryManagementApi(self.service)
        forbidden = api.get_coverage(principal=self.admin, territory_id="t-eu", request_id="req-1")
        self.assertEqual(forbidden["error"]["code"], "forbidden")

        self.service.create_territory(
            Territory(
                territory_id="t-na",
                tenant_id="tenant-1",
                name="North America",
                code="NA",
                parent_territory_id=None,
                level=0,
            )
        )
        self.service.register_rule(
            TerritoryRule(
                rule_id="r-lead-west",
                tenant_id="tenant-1",
                territory_id="t-na",
                subject_type="lead",
                priority=50,
                criteria={"tenant_id": "tenant-1", "region": "west"},
                owner_type="user",
                owner_id="u-ae-1",
            )
        )
        self.service.assign_subject(
            principal=self.admin,
            subject_type="lead",
            subject_id="lead-1",
            subject_facts={"tenant_id": "tenant-1", "region": "west"},
            assigned_at="2026-03-29T00:00:00Z",
        )
        visible = api.get_assignment(
            principal=self.agent,
            subject_type="lead",
            subject_id="lead-1",
            request_id="req-2",
        )
        self.assertIn("data", visible)


if __name__ == "__main__":
    unittest.main()
