from __future__ import annotations

import unittest

from src.design_system import (
    ComponentContract,
    DesignSystemApi,
    DesignSystemRegistryService,
    DesignSystemValidationError,
    DesignToken,
    INTERACTION_STATE_CONTRACT,
)


class DesignSystemClusterTests(unittest.TestCase):
    def test_snapshot_exposes_tokens_components_and_alias_map(self) -> None:
        service = DesignSystemRegistryService()
        snapshot = service.snapshot()

        self.assertGreaterEqual(snapshot.token_count, 20)
        self.assertGreaterEqual(snapshot.component_count, 8)
        self.assertEqual(snapshot.alias_map["token.stage.closed_won"], "token.intent.success")
        self.assertIn("token.sla.breached", snapshot.alias_map)

    def test_all_components_implement_interaction_state_contract(self) -> None:
        service = DesignSystemRegistryService()
        snapshot = service.snapshot()

        required = set(INTERACTION_STATE_CONTRACT)
        for component in snapshot.components:
            self.assertTrue(required.issubset(set(component.required_states)), component.component_id)

    def test_alias_must_reference_semantic_token(self) -> None:
        bad_tokens = (
            DesignToken("token.intent.success", "semantic", "#00aa00", "ok"),
            DesignToken("token.stage.closed_won", "domain_alias", "token.intent.not_real", "bad mapping"),
        )
        with self.assertRaises(DesignSystemValidationError):
            DesignSystemRegistryService(tokens=bad_tokens)

    def test_missing_interaction_state_is_rejected(self) -> None:
        bad_components = (
            ComponentContract("data.query_table", "data", ("default", "keyboard_focus")),
        )
        with self.assertRaises(DesignSystemValidationError):
            DesignSystemRegistryService(components=bad_components)

    def test_api_envelope(self) -> None:
        api = DesignSystemApi(DesignSystemRegistryService())
        response = api.get_design_system_snapshot(request_id="req-design")

        self.assertEqual(response["meta"]["request_id"], "req-design")
        self.assertIn("data", response)
        self.assertEqual(response["data"]["version"], "design-system-v1")


if __name__ == "__main__":
    unittest.main()
