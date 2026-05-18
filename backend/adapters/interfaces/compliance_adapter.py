"""Canonical ComplianceAdapter contract for country-specific compliance hooks.

Docs: docs/pakistan-adapter-architecture.md §4.3
      docs/architecture-overview.md Layer Model (L2 Interfaces)

Rules:
- Core services depend on this interface only — never on country implementations.
- CHECK_BLOCKED (allowed=False) is a business result, not a system error.
- System/provider failures raise AdapterError.
- When compliance is disabled, inject NoopComplianceAdapter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .types import AdapterContext


@dataclass(frozen=True)
class ComplianceCheckInput:
    action_type: str          # e.g. "payment.create", "lead.convert"
    entity_id: str
    country: str              # ISO-3166 alpha-2 e.g. "PK"
    payload: dict[str, Any]
    occurred_at: str          # ISO-8601 UTC


@dataclass(frozen=True)
class ComplianceCheckResult:
    allowed: bool
    reason_code: str | None = None          # populated when allowed=False
    obligations: tuple[str, ...] = ()       # e.g. ("fbr_reporting_required",)


@dataclass(frozen=True)
class ComplianceReportInput:
    action_type: str
    entity_id: str
    country: str
    payload: dict[str, Any]
    occurred_at: str
    trace_id: str


@dataclass(frozen=True)
class ComplianceReportResult:
    accepted: bool
    report_ref: str | None = None
    submitted_at: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class ComplianceAdapter(Protocol):
    """Interface for country-specific compliance pre-checks and post-reporting."""

    def pre_action_check(
        self, input: ComplianceCheckInput, ctx: AdapterContext
    ) -> ComplianceCheckResult: ...

    def post_action_report(
        self, input: ComplianceReportInput, ctx: AdapterContext
    ) -> ComplianceReportResult: ...


class NoopComplianceAdapter:
    """Pass-through adapter used when compliance checks are disabled via feature flag.

    Returns allowed=True for every check and accepted=True for every report.
    Safe to inject in all non-compliance-regulated environments.
    """

    def pre_action_check(
        self, input: ComplianceCheckInput, ctx: AdapterContext
    ) -> ComplianceCheckResult:
        return ComplianceCheckResult(allowed=True)

    def post_action_report(
        self, input: ComplianceReportInput, ctx: AdapterContext
    ) -> ComplianceReportResult:
        return ComplianceReportResult(accepted=True)
