"""Rules-based segmentation logic for lead/contact entities."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .entities import SegmentDefinition, SegmentRule, SegmentValidationError

VALID_SEGMENT_ENTITIES: tuple[str, ...] = ("lead", "contact")

LEAD_SEGMENT_FIELDS: tuple[str, ...] = (
    "lead_id",
    "tenant_id",
    "owner_user_id",
    "source",
    "status",
    "score",
    "email",
    "phone",
    "company_name",
    "created_at",
    "converted_at",
)

CONTACT_SEGMENT_FIELDS: tuple[str, ...] = (
    "contact_id",
    "tenant_id",
    "account_id",
    "owner_user_id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "lifecycle_status",
    "created_at",
    "updated_at",
)

VALID_OPERATORS: tuple[str, ...] = (
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "contains",
    "in",
)


class SegmentEvaluator:
    """Validates and evaluates segment rules against records."""

    def validate(self, segment: SegmentDefinition) -> None:
        if segment.entity_type not in VALID_SEGMENT_ENTITIES:
            raise SegmentValidationError(
                f"Unsupported segment entity_type={segment.entity_type}. Supported={VALID_SEGMENT_ENTITIES}"
            )

        allowed_fields = self.allowed_fields(segment.entity_type)
        if not segment.rules:
            raise SegmentValidationError("Segment must include at least one rule.")

        for rule in segment.rules:
            self._validate_rule(rule, allowed_fields)

    def allowed_fields(self, entity_type: str) -> tuple[str, ...]:
        if entity_type == "lead":
            return LEAD_SEGMENT_FIELDS
        if entity_type == "contact":
            return CONTACT_SEGMENT_FIELDS
        return ()

    def evaluate(self, segment: SegmentDefinition, record: dict[str, Any]) -> bool:
        self.validate(segment)
        return all(self._evaluate_rule(rule, record) for rule in segment.rules)

    def _validate_rule(self, rule: SegmentRule, allowed_fields: tuple[str, ...]) -> None:
        if rule.field not in allowed_fields:
            raise SegmentValidationError(
                f"Rule field={rule.field} is invalid for selected entity. Allowed={allowed_fields}"
            )
        if rule.operator not in VALID_OPERATORS:
            raise SegmentValidationError(
                f"Rule operator={rule.operator} is invalid. Allowed={VALID_OPERATORS}"
            )

    def _evaluate_rule(self, rule: SegmentRule, record: dict[str, Any]) -> bool:
        value = record.get(rule.field)

        if rule.operator == "eq":
            return value == rule.value
        if rule.operator == "ne":
            return value != rule.value
        if rule.operator == "gt":
            return value is not None and value > rule.value
        if rule.operator == "gte":
            return value is not None and value >= rule.value
        if rule.operator == "lt":
            return value is not None and value < rule.value
        if rule.operator == "lte":
            return value is not None and value <= rule.value
        if rule.operator == "contains":
            return value is not None and str(rule.value) in str(value)
        if rule.operator == "in":
            if not isinstance(rule.value, str):
                return False
            return str(value) in {part.strip() for part in rule.value.split(",")}
        return False


def serialize_segment(segment: SegmentDefinition) -> dict[str, Any]:
    payload = asdict(segment)
    payload["rules"] = [asdict(rule) for rule in segment.rules]
    return payload
