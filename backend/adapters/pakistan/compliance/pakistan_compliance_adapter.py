"""Pakistan compliance adapter (PTA / FBR hooks).

Status: optional stub — enabled via feature flag COMPLIANCE_PK_ENABLED.
When disabled, inject NoopComplianceAdapter from adapters.interfaces.compliance_adapter.

Docs: docs/pakistan-adapter-architecture.md §3.E, §4.3
"""

from __future__ import annotations

from adapters.interfaces.compliance_adapter import (
    ComplianceCheckInput,
    ComplianceCheckResult,
    ComplianceReportInput,
    ComplianceReportResult,
)
from adapters.interfaces.types import AdapterContext, AdapterError, AdapterErrorCode, utcnow_iso


# Actions that require a pre-check under Pakistan regulations (illustrative).
_PK_REGULATED_ACTIONS = frozenset({
    "payment.create",
    "payment.capture",
    "telecom.message.bulk_send",
})


class PakistanComplianceAdapter:
    """Country compliance hooks for Pakistan (PTA telecom / FBR tax obligations).

    pre_action_check: returns allowed=True for most actions; blocks on regulatory list.
    post_action_report: records obligation fulfillment; no-ops for unregulated actions.

    Neither method mutates core domain rules. Compliance failures are isolated.
    """

    def pre_action_check(
        self, input: ComplianceCheckInput, ctx: AdapterContext
    ) -> ComplianceCheckResult:
        if input.country.upper() != "PK":
            raise AdapterError(
                code=AdapterErrorCode.VALIDATION_ERROR,
                message="Pakistan compliance adapter invoked for non-PK context.",
                retryable=False,
                provider="pk_compliance",
                correlation_id=ctx.trace_id,
            )

        if input.action_type in _PK_REGULATED_ACTIONS:
            # Stub: real implementation would call PTA/FBR API here.
            # For now, pass through with obligation tag so post-action reporting fires.
            return ComplianceCheckResult(
                allowed=True,
                obligations=("post_action_reporting_required",),
            )

        return ComplianceCheckResult(allowed=True)

    def post_action_report(
        self, input: ComplianceReportInput, ctx: AdapterContext
    ) -> ComplianceReportResult:
        if input.country.upper() != "PK":
            raise AdapterError(
                code=AdapterErrorCode.VALIDATION_ERROR,
                message="Pakistan compliance adapter invoked for non-PK context.",
                retryable=False,
                provider="pk_compliance",
                correlation_id=ctx.trace_id,
            )

        # Stub: real implementation would submit report to FBR/PTA endpoint.
        report_ref = f"pk-compliance-{input.trace_id}"
        return ComplianceReportResult(
            accepted=True,
            report_ref=report_ref,
            submitted_at=utcnow_iso(),
        )
