from __future__ import annotations

import unittest

from services.activity.monitor import EmployeeActivityMonitor, MonitorValidationError


class EmployeeActivityMonitorTests(unittest.TestCase):
    def test_metrics_timeline_and_scoring(self) -> None:
        monitor = EmployeeActivityMonitor()
        monitor.record_activity(
            "ten-1",
            "usr-1",
            "followup",
            trace_id="tr-1",
            request_id="req-1",
            occurred_at="2026-04-01T09:00:00Z",
            response_seconds=300,
            follow_up_due_at="2026-04-01T10:00:00Z",
            follow_up_completed_at="2026-04-01T09:30:00Z",
        )
        monitor.record_activity(
            "ten-1",
            "usr-1",
            "followup",
            trace_id="tr-2",
            request_id="req-2",
            occurred_at="2026-04-01T11:00:00Z",
            response_seconds=600,
            follow_up_due_at="2026-04-01T12:00:00Z",
            follow_up_completed_at="2026-04-01T13:00:00Z",
        )

        timeline = monitor.user_timeline("ten-1", "usr-1")
        self.assertEqual(len(timeline), 2)
        self.assertLessEqual(timeline[0].occurred_at, timeline[1].occurred_at)

        metrics = monitor.user_metrics("ten-1", "usr-1")
        self.assertEqual(metrics.timeline_events, 2)
        self.assertEqual(metrics.follow_up_compliance, 0.5)
        self.assertEqual(metrics.average_response_seconds, 450.0)

        score = monitor.score_user("ten-1", "usr-1")
        self.assertGreaterEqual(score.score, 70.0)

    def test_detect_bypasses_and_alignment_drop(self) -> None:
        monitor = EmployeeActivityMonitor()
        monitor.record_activity(
            "ten-2",
            "usr-risk",
            "message",
            trace_id="tr-risk",
            request_id="req-risk",
            bypass_attempted=True,
        )

        findings = monitor.detect_bypasses("ten-2")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].reason, "BYPASS_FLAGGED")

        validation = monitor.validate_tracking_accuracy("ten-2")
        self.assertLess(validation["alignment_percent"], 100.0)
        self.assertNotEqual(validation["score"], "10/10")

    def test_traceability_is_required(self) -> None:
        monitor = EmployeeActivityMonitor()
        with self.assertRaises(MonitorValidationError):
            monitor.record_activity("ten-1", "usr-1", "followup", trace_id="", request_id="req-x")


if __name__ == "__main__":
    unittest.main()
