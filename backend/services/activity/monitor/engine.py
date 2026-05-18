"""Employee Activity Monitor built on top of activity-engine style controls."""

from __future__ import annotations

from collections import defaultdict
from uuid import uuid4

from .entities import (
    BypassFinding,
    MonitorEvent,
    MonitorValidationError,
    PerformanceScore,
    UserMetrics,
    parse_rfc3339,
    utc_now,
)


class EmployeeActivityMonitor:
    """Tracks follow-up discipline and response performance with anti-bypass checks."""

    def __init__(self) -> None:
        self._events: list[MonitorEvent] = []

    def record_activity(
        self,
        tenant_id: str,
        user_id: str,
        activity_type: str,
        *,
        trace_id: str,
        request_id: str,
        occurred_at: str | None = None,
        response_seconds: int | None = None,
        follow_up_due_at: str | None = None,
        follow_up_completed_at: str | None = None,
        bypass_attempted: bool = False,
        metadata: dict[str, object] | None = None,
    ) -> MonitorEvent:
        if not tenant_id.strip() or not user_id.strip() or not activity_type.strip():
            raise MonitorValidationError("TENANT_USER_ACTIVITY_REQUIRED")
        if not trace_id.strip() or not request_id.strip():
            raise MonitorValidationError("TRACEABILITY_REQUIRED")
        if response_seconds is not None and response_seconds < 0:
            raise MonitorValidationError("RESPONSE_SECONDS_INVALID")

        event = MonitorEvent(
            event_id=f"mae_{uuid4().hex[:12]}",
            tenant_id=tenant_id,
            user_id=user_id,
            activity_type=activity_type,
            occurred_at=occurred_at or utc_now(),
            trace_id=trace_id,
            request_id=request_id,
            response_seconds=response_seconds,
            follow_up_due_at=follow_up_due_at,
            follow_up_completed_at=follow_up_completed_at,
            bypass_attempted=bypass_attempted,
            metadata=dict(metadata or {}),
        )
        self._events.append(event)
        return event

    def user_timeline(self, tenant_id: str, user_id: str) -> list[MonitorEvent]:
        timeline = [e for e in self._events if e.tenant_id == tenant_id and e.user_id == user_id]
        return sorted(timeline, key=lambda e: parse_rfc3339(e.occurred_at))

    def user_metrics(self, tenant_id: str, user_id: str) -> UserMetrics:
        events = self.user_timeline(tenant_id, user_id)
        total_followups = 0
        on_time_followups = 0
        response_values: list[int] = []
        bypass_count = 0

        for event in events:
            if event.follow_up_due_at:
                total_followups += 1
                if event.follow_up_completed_at and parse_rfc3339(event.follow_up_completed_at) <= parse_rfc3339(event.follow_up_due_at):
                    on_time_followups += 1
            if event.response_seconds is not None:
                response_values.append(event.response_seconds)
            if event.bypass_attempted:
                bypass_count += 1

        follow_up_compliance = 1.0 if total_followups == 0 else on_time_followups / total_followups
        avg_response = 0.0 if not response_values else sum(response_values) / len(response_values)

        return UserMetrics(
            tenant_id=tenant_id,
            user_id=user_id,
            follow_up_compliance=round(follow_up_compliance, 4),
            average_response_seconds=round(avg_response, 2),
            timeline_events=len(events),
            bypass_count=bypass_count,
        )

    def score_user(self, tenant_id: str, user_id: str, target_response_seconds: int = 3600) -> PerformanceScore:
        metrics = self.user_metrics(tenant_id, user_id)

        discipline = max(0.0, min(100.0, metrics.follow_up_compliance * 100.0 - (metrics.bypass_count * 10.0)))
        if metrics.average_response_seconds <= 0:
            performance = 100.0
        else:
            performance = max(0.0, min(100.0, (target_response_seconds / metrics.average_response_seconds) * 100.0))

        weights = {"discipline": 0.6, "performance": 0.4}
        score = round((discipline * weights["discipline"]) + (performance * weights["performance"]), 2)
        grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D"

        return PerformanceScore(
            tenant_id=tenant_id,
            user_id=user_id,
            score=score,
            discipline_component=round(discipline, 2),
            performance_component=round(performance, 2),
            weights=weights,
            grade=grade,
        )

    def detect_bypasses(self, tenant_id: str) -> list[BypassFinding]:
        findings: list[BypassFinding] = []
        for event in self._events:
            if event.tenant_id != tenant_id:
                continue
            if event.bypass_attempted:
                findings.append(BypassFinding(tenant_id, event.user_id, event.event_id, "BYPASS_FLAGGED"))
            if not event.trace_id or not event.request_id:
                findings.append(BypassFinding(tenant_id, event.user_id, event.event_id, "TRACEABILITY_GAP"))
        return findings

    def validate_tracking_accuracy(self, tenant_id: str) -> dict[str, object]:
        tenant_events = [e for e in self._events if e.tenant_id == tenant_id]
        if not tenant_events:
            return {
                "tracking_accuracy_percent": 100.0,
                "alignment_percent": 100.0,
                "score": "10/10",
                "issues": [],
            }

        issues: list[str] = []
        complete = 0
        for event in tenant_events:
            has_core = all([event.event_id, event.user_id, event.activity_type, event.trace_id, event.request_id])
            if has_core:
                complete += 1
            else:
                issues.append(f"incomplete_event:{event.event_id}")

        accuracy = round((complete / len(tenant_events)) * 100.0, 2)
        bypasses = self.detect_bypasses(tenant_id)
        if bypasses:
            issues.append(f"bypass_findings:{len(bypasses)}")
        alignment = round(max(0.0, accuracy - (len(bypasses) * 2.0)), 2)
        score = "10/10" if alignment >= 100.0 and not issues else f"{round((alignment / 10.0), 1)}/10"

        return {
            "tracking_accuracy_percent": accuracy,
            "alignment_percent": alignment,
            "score": score,
            "issues": issues,
            "auto_fix": "10/10" if score == "10/10" else "HARDEN_TRACEABILITY_AND_BLOCK_BYPASS",
        }

    def tenant_summary(self, tenant_id: str) -> dict[str, object]:
        users: dict[str, list[MonitorEvent]] = defaultdict(list)
        for event in self._events:
            if event.tenant_id == tenant_id:
                users[event.user_id].append(event)

        per_user = {}
        for user_id in sorted(users):
            per_user[user_id] = {
                "metrics": self.user_metrics(tenant_id, user_id),
                "score": self.score_user(tenant_id, user_id),
            }

        return {
            "tenant_id": tenant_id,
            "users": per_user,
            "validation": self.validate_tracking_accuracy(tenant_id),
        }
