"""Duplicate detection, prevention, and merge workflows for CRM master records."""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from .entities import (
    DuplicateCandidate,
    DuplicatePreventedError,
    EntityType,
    ManualReviewTask,
    MatchEvidence,
    MergeWorkflow,
    ReviewDecisionError,
    RuleDefinition,
    UpsertDecision,
)

ManualReviewHook = Callable[[ManualReviewTask], None]


class DataDeduplicationEngine:
    """In-memory deduplication engine with conservative auto-merge policy."""

    def __init__(self, review_hook: ManualReviewHook | None = None) -> None:
        self._store: dict[tuple[str, EntityType], dict[str, dict[str, Any]]] = {}
        self._review_hook = review_hook or (lambda _: None)
        self._review_queue: dict[str, ManualReviewTask] = {}
        self._pending_incoming: dict[str, dict[str, Any]] = {}
        self._merge_log: list[MergeWorkflow] = []
        self._rules: tuple[RuleDefinition, ...] = self._build_rules()

    def get_matching_rules(self, entity_type: EntityType | None = None) -> list[RuleDefinition]:
        rules = self._rules
        if entity_type is not None:
            rules = tuple(rule for rule in rules if rule.entity_type == entity_type)
        return list(rules)

    def upsert_record(self, *, entity_type: EntityType, tenant_id: str, record: dict[str, Any]) -> UpsertDecision:
        record_id = self._require_id(entity_type, record)
        record = deepcopy(record)
        record["tenant_id"] = tenant_id

        bucket = self._bucket(tenant_id, entity_type)
        is_update = record_id in bucket

        candidate = self._find_best_candidate(entity_type=entity_type, tenant_id=tenant_id, record_id=record_id, record=record)
        if candidate:
            if self._is_auto_merge_allowed(candidate):
                merge = self._merge_pair(entity_type=entity_type, tenant_id=tenant_id, incoming=record, existing=bucket[candidate.existing_id], evidence=candidate.evidence)
                bucket[merge.survivor_id] = deepcopy(merge.after_survivor)
                if merge.merged_id in bucket:
                    del bucket[merge.merged_id]
                self._merge_log.append(merge)
                return UpsertDecision(
                    decision="merged",
                    entity_type=entity_type,
                    tenant_id=tenant_id,
                    record_id=merge.survivor_id,
                    duplicate_of=merge.survivor_id,
                    merge_id=merge.merge_id,
                    reason=merge.decision_reason,
                )

            review_task = self._enqueue_review(candidate, record)
            raise DuplicatePreventedError(
                f"{entity_type} create/update prevented for {record_id}; probable duplicate {candidate.existing_id}; review_id={review_task.review_id}"
            )

        bucket[record_id] = record
        return UpsertDecision(
            decision="no_match",
            entity_type=entity_type,
            tenant_id=tenant_id,
            record_id=record_id,
            reason="updated_without_duplicate_signal" if is_update else "created_without_duplicate_signal",
        )

    def decide_manual_review(self, review_id: str, *, approve_merge: bool, decided_by: str) -> UpsertDecision:
        task = self._review_queue.get(review_id)
        if not task:
            raise ReviewDecisionError(f"manual review task not found: {review_id}")

        bucket = self._bucket(task.tenant_id, task.entity_type)
        incoming = bucket.get(task.incoming_id) or self._pending_incoming.get(review_id)
        existing = bucket.get(task.existing_id)
        if not incoming or not existing:
            raise ReviewDecisionError(f"manual review task {review_id} references missing records")

        del self._review_queue[review_id]
        self._pending_incoming.pop(review_id, None)

        if not approve_merge:
            return UpsertDecision(
                decision="prevented",
                entity_type=task.entity_type,
                tenant_id=task.tenant_id,
                record_id=task.incoming_id,
                duplicate_of=task.existing_id,
                review_id=review_id,
                reason="manual_reviewer_rejected_merge",
            )

        merge = self._merge_pair(
            entity_type=task.entity_type,
            tenant_id=task.tenant_id,
            incoming=incoming,
            existing=existing,
            evidence=task.evidence,
            executed_by=decided_by,
            reason="manual_review_approved_merge",
        )
        bucket[merge.survivor_id] = deepcopy(merge.after_survivor)
        if merge.merged_id in bucket:
            del bucket[merge.merged_id]
        self._merge_log.append(merge)

        return UpsertDecision(
            decision="merged",
            entity_type=task.entity_type,
            tenant_id=task.tenant_id,
            record_id=merge.survivor_id,
            duplicate_of=merge.survivor_id,
            merge_id=merge.merge_id,
            review_id=review_id,
            reason="manual_review_approved_merge",
        )

    def list_manual_reviews(self) -> list[ManualReviewTask]:
        return list(self._review_queue.values())

    def list_merge_workflows(self) -> list[MergeWorkflow]:
        return list(self._merge_log)

    def get_record(self, *, entity_type: EntityType, tenant_id: str, record_id: str) -> dict[str, Any] | None:
        record = self._bucket(tenant_id, entity_type).get(record_id)
        return deepcopy(record) if record else None

    def _find_best_candidate(
        self,
        *,
        entity_type: EntityType,
        tenant_id: str,
        record_id: str,
        record: dict[str, Any],
    ) -> DuplicateCandidate | None:
        best: DuplicateCandidate | None = None
        for existing_id, existing in self._bucket(tenant_id, entity_type).items():
            if existing_id == record_id:
                continue
            candidate = self._score_pair(entity_type=entity_type, tenant_id=tenant_id, incoming_id=record_id, incoming=record, existing_id=existing_id, existing=existing)
            if not candidate:
                continue
            if not best or candidate.score > best.score:
                best = candidate
        return best

    def _score_pair(
        self,
        *,
        entity_type: EntityType,
        tenant_id: str,
        incoming_id: str,
        incoming: dict[str, Any],
        existing_id: str,
        existing: dict[str, Any],
    ) -> DuplicateCandidate | None:
        evidence: list[MatchEvidence] = []

        def add(rule: str, field: str, left: str, right: str, score: float) -> None:
            evidence.append(MatchEvidence(rule_code=rule, field_name=field, left_value=left, right_value=right, score=score))

        # strong deterministic signals
        in_email = self._normalize_email(incoming.get("email"))
        ex_email = self._normalize_email(existing.get("email"))
        if in_email and ex_email and in_email == ex_email:
            add(f"{entity_type}.email_exact", "email", in_email, ex_email, 0.94)

        in_phone = self._normalize_phone(incoming.get("phone"))
        ex_phone = self._normalize_phone(existing.get("phone"))
        if in_phone and ex_phone and in_phone == ex_phone:
            add(f"{entity_type}.phone_exact", "phone", in_phone, ex_phone, 0.88)

        if entity_type == "account":
            in_domain = self._normalize_domain(incoming.get("website"))
            ex_domain = self._normalize_domain(existing.get("website"))
            if in_domain and ex_domain and in_domain == ex_domain:
                add("account.website_domain_exact", "website", in_domain, ex_domain, 0.92)

        # softer corroborating signals
        if entity_type == "lead":
            if self._normalize_name(incoming.get("company_name")) and self._normalize_name(incoming.get("company_name")) == self._normalize_name(existing.get("company_name")):
                add("lead.company_exact", "company_name", self._normalize_name(incoming.get("company_name")), self._normalize_name(existing.get("company_name")), 0.38)
        elif entity_type == "contact":
            in_full = self._normalize_name(f"{incoming.get('first_name', '')} {incoming.get('last_name', '')}")
            ex_full = self._normalize_name(f"{existing.get('first_name', '')} {existing.get('last_name', '')}")
            if in_full and ex_full and in_full == ex_full:
                add("contact.full_name_exact", "full_name", in_full, ex_full, 0.44)

            if incoming.get("account_id") and incoming.get("account_id") == existing.get("account_id"):
                add("contact.account_exact", "account_id", str(incoming.get("account_id")), str(existing.get("account_id")), 0.35)
        else:
            in_name = self._normalize_name(incoming.get("name"))
            ex_name = self._normalize_name(existing.get("name"))
            if in_name and ex_name and in_name == ex_name:
                add("account.name_exact", "name", in_name, ex_name, 0.48)

            in_addr = self._normalize_name(incoming.get("billing_address"))
            ex_addr = self._normalize_name(existing.get("billing_address"))
            if in_addr and ex_addr and in_addr == ex_addr:
                add("account.billing_address_exact", "billing_address", in_addr, ex_addr, 0.40)

        if not evidence:
            return None

        top_two = sorted((e.score for e in evidence), reverse=True)[:2]
        score = min(1.0, sum(top_two))

        risky_conflict = bool(in_email and ex_email and in_email != ex_email and in_phone and ex_phone and in_phone != ex_phone)
        if score < 0.80:
            return None

        return DuplicateCandidate(
            entity_type=entity_type,
            tenant_id=tenant_id,
            incoming_id=incoming_id,
            existing_id=existing_id,
            score=score,
            evidence=tuple(evidence),
            risky_conflict=risky_conflict,
        )

    def _is_auto_merge_allowed(self, candidate: DuplicateCandidate) -> bool:
        if candidate.risky_conflict:
            return False
        strong_count = sum(1 for e in candidate.evidence if e.score >= 0.88)
        return candidate.score >= 0.95 and strong_count >= 2

    def _enqueue_review(self, candidate: DuplicateCandidate, incoming: dict[str, Any]) -> ManualReviewTask:
        review = ManualReviewTask(
            review_id=f"review-{uuid4().hex[:12]}",
            entity_type=candidate.entity_type,
            tenant_id=candidate.tenant_id,
            incoming_id=candidate.incoming_id,
            existing_id=candidate.existing_id,
            score=candidate.score,
            reason="high_duplicate_probability_requires_human_review",
            evidence=candidate.evidence,
        )
        self._review_queue[review.review_id] = review
        self._pending_incoming[review.review_id] = deepcopy(incoming)
        self._review_hook(review)
        return review

    def _merge_pair(
        self,
        *,
        entity_type: EntityType,
        tenant_id: str,
        incoming: dict[str, Any],
        existing: dict[str, Any],
        evidence: tuple[MatchEvidence, ...],
        executed_by: str = "system:auto",
        reason: str = "safe_auto_merge",
    ) -> MergeWorkflow:
        survivor = self._select_survivor(incoming, existing)
        merged = existing if survivor is incoming else incoming

        before_survivor = deepcopy(survivor)
        before_merged = deepcopy(merged)

        merged_fields = self._apply_merge_policy(before_survivor, before_merged)
        merged_fields["updated_at"] = self._now_iso()

        return MergeWorkflow(
            merge_id=f"merge-{uuid4().hex[:12]}",
            entity_type=entity_type,
            tenant_id=tenant_id,
            survivor_id=str(survivor[self._id_field(entity_type)]),
            merged_id=str(merged[self._id_field(entity_type)]),
            executed_by=executed_by,
            decision_reason=reason,
            evidence=evidence,
            before_survivor=before_survivor,
            before_merged=before_merged,
            after_survivor=merged_fields,
        )

    def _apply_merge_policy(self, survivor: dict[str, Any], merged: dict[str, Any]) -> dict[str, Any]:
        result = deepcopy(survivor)
        protected = {"tenant_id", "created_at", "updated_at"}
        for key, value in merged.items():
            if key in protected:
                continue
            if result.get(key) in (None, "") and value not in (None, ""):
                result[key] = value
        return result

    def _select_survivor(self, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        left_score = self._completeness(left)
        right_score = self._completeness(right)
        if left_score > right_score:
            return left
        if right_score > left_score:
            return right
        left_created = left.get("created_at", "")
        right_created = right.get("created_at", "")
        return left if left_created <= right_created else right

    @staticmethod
    def _completeness(record: dict[str, Any]) -> int:
        return sum(1 for value in record.values() if value not in (None, ""))

    def _bucket(self, tenant_id: str, entity_type: EntityType) -> dict[str, dict[str, Any]]:
        key = (tenant_id, entity_type)
        if key not in self._store:
            self._store[key] = {}
        return self._store[key]

    @staticmethod
    def _id_field(entity_type: EntityType) -> str:
        return {
            "lead": "lead_id",
            "contact": "contact_id",
            "account": "account_id",
        }[entity_type]

    def _require_id(self, entity_type: EntityType, record: dict[str, Any]) -> str:
        id_field = self._id_field(entity_type)
        value = record.get(id_field)
        if not value:
            raise ReviewDecisionError(f"missing required id field {id_field}")
        return str(value)

    @staticmethod
    def _normalize_email(value: Any) -> str:
        return str(value or "").strip().lower()

    @staticmethod
    def _normalize_phone(value: Any) -> str:
        raw = re.sub(r"\D", "", str(value or ""))
        return raw[-10:] if len(raw) >= 10 else raw

    @staticmethod
    def _normalize_domain(value: Any) -> str:
        text = str(value or "").strip().lower()
        text = re.sub(r"^https?://", "", text)
        return text.split("/")[0]

    @staticmethod
    def _normalize_name(value: Any) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip().lower())

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def dump_state(self) -> dict[str, Any]:
        return {
            "store": {f"{tenant}:{entity}": deepcopy(records) for (tenant, entity), records in self._store.items()},
            "merge_log": [asdict(item) for item in self._merge_log],
            "review_queue": [asdict(item) for item in self._review_queue.values()],
        }

    @staticmethod
    def _build_rules() -> tuple[RuleDefinition, ...]:
        return (
            RuleDefinition("lead.email_exact", "lead", "Exact normalized email match.", 0.94, True),
            RuleDefinition("lead.phone_exact", "lead", "Exact normalized phone match.", 0.88, True),
            RuleDefinition("lead.company_exact", "lead", "Exact normalized company name match.", 0.38, False),
            RuleDefinition("contact.email_exact", "contact", "Exact normalized email match.", 0.94, True),
            RuleDefinition("contact.phone_exact", "contact", "Exact normalized phone match.", 0.88, True),
            RuleDefinition("contact.full_name_exact", "contact", "Exact normalized full name match.", 0.44, False),
            RuleDefinition("contact.account_exact", "contact", "Exact account relationship match.", 0.35, False),
            RuleDefinition("account.website_domain_exact", "account", "Exact website domain match.", 0.92, True),
            RuleDefinition("account.name_exact", "account", "Exact normalized account name match.", 0.48, False),
            RuleDefinition("account.billing_address_exact", "account", "Exact normalized billing address match.", 0.40, False),
        )
