from __future__ import annotations

import unittest

from src.rule_engine import (
    ActionDefinition,
    ConditionRule,
    RuleDefinition,
    RuleEngineApi,
    RuleEngineService,
    RuleValidationError,
)


class RuleEngineServiceTests(unittest.TestCase):
    def test_evaluate_deterministic_conditions_and_trigger_actions(self) -> None:
        service = RuleEngineService()
        service.register_rule(
            RuleDefinition(
                rule_id="rule-lead-qualified",
                tenant_id="tenant-1",
                workflow_key="lead_intake_assignment_conversion",
                trigger_event="lead.created.v1",
                priority=10,
                match="all",
                conditions=(
                    ConditionRule(field="context.tenant_id", op="exists", value=True),
                    ConditionRule(field="context.entity.lead_status", op="in", value=["new", "qualified"]),
                    ConditionRule(field="context.entity.score", op="gte", value=80),
                ),
                actions=(
                    ActionDefinition(
                        action_id="notify_owner",
                        type="notify",
                        target="Notification Orchestrator",
                        payload={
                            "lead_id": "${context.entity.id}",
                            "owner_id": "${context.entity.owner_id}",
                            "template": "new-qualified-lead",
                        },
                    ),
                ),
            )
        )

        context = {
            "context": {
                "tenant_id": "tenant-1",
                "entity": {"id": "lead-1", "lead_status": "qualified", "score": 95, "owner_id": "user-9"},
            }
        }

        result = service.evaluate(trigger_event="lead.created.v1", tenant_id="tenant-1", context=context)
        self.assertEqual(result.matched_rule_ids, ("rule-lead-qualified",))
        self.assertEqual(result.evaluations[0].matched, True)
        self.assertEqual(result.evaluations[0].actions[0]["payload"]["lead_id"], "lead-1")
        self.assertEqual(result.evaluations[0].actions[0]["payload"]["owner_id"], "user-9")

    def test_rejects_ambiguous_rules(self) -> None:
        service = RuleEngineService()
        baseline = RuleDefinition(
            rule_id="r1",
            tenant_id="tenant-1",
            workflow_key="lead_intake_assignment_conversion",
            trigger_event="lead.created.v1",
            priority=10,
            match="all",
            conditions=(ConditionRule(field="context.entity.lead_status", op="eq", value="new"),),
            actions=(
                ActionDefinition(
                    action_id="a1",
                    type="notify",
                    target="Notification Orchestrator",
                    payload={"template": "x"},
                ),
            ),
        )
        service.register_rule(baseline)

        with self.assertRaises(RuleValidationError):
            service.register_rule(
                RuleDefinition(
                    rule_id="r2",
                    tenant_id="tenant-1",
                    workflow_key="lead_intake_assignment_conversion",
                    trigger_event="lead.created.v1",
                    priority=10,
                    match="all",
                    conditions=(ConditionRule(field="context.entity.score", op="gt", value=70),),
                    actions=(
                        ActionDefinition(
                            action_id="a2",
                            type="call_service",
                            target="Territory & Assignment Service",
                            payload={"lead_id": "${context.entity.id}"},
                        ),
                    ),
                )
            )

        with self.assertRaises(RuleValidationError):
            service.register_rule(
                RuleDefinition(
                    rule_id="r3",
                    tenant_id="tenant-1",
                    workflow_key="lead_intake_assignment_conversion",
                    trigger_event="lead.created.v1",
                    priority=11,
                    match="all",
                    conditions=(ConditionRule(field="context.entity.lead_status", op="eq", value="new"),),
                    actions=(
                        ActionDefinition(
                            action_id="a3",
                            type="notify",
                            target="Notification Orchestrator",
                            payload={"template": "duplicate"},
                        ),
                    ),
                )
            )


class RuleEngineApiTests(unittest.TestCase):
    def test_api_evaluate_response_shape(self) -> None:
        service = RuleEngineService()
        api = RuleEngineApi(service)

        create = api.create_rule(
            RuleDefinition(
                rule_id="rule-contact",
                tenant_id="tenant-99",
                workflow_key="contact_engagement",
                trigger_event="contact.created.v1",
                priority=1,
                match="any",
                conditions=(
                    ConditionRule(field="context.entity.lifecycle_status", op="eq", value="new"),
                    ConditionRule(field="context.entity.email", op="contains", value="@"),
                ),
                actions=(
                    ActionDefinition(
                        action_id="emit_contact_created",
                        type="emit_event",
                        target="Event Bus",
                        payload={"contact_id": "${context.entity.id}"},
                    ),
                ),
            ),
            request_id="req-1",
        )
        self.assertIn("data", create)

        response = api.evaluate_rules(
            trigger_event="contact.created.v1",
            tenant_id="tenant-99",
            context={"context": {"entity": {"id": "c-1", "email": "user@example.com"}}},
            request_id="req-2",
        )

        self.assertEqual(response["meta"]["request_id"], "req-2")
        self.assertEqual(response["data"]["matched_rule_ids"], ("rule-contact",))


if __name__ == "__main__":
    unittest.main()
