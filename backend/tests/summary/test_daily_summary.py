"""Tests for MR-004 — Daily WhatsApp Activity Summary."""

from __future__ import annotations

from datetime import date

import pytest

from services.summary.daily_summary import (
    DailySummaryReport,
    compute_daily_summary,
    format_summary_message,
    send_daily_summary,
)


# ── format_summary_message ────────────────────────────────────────────────────

class TestFormatSummaryMessage:
    def test_english_template_renders_all_fields(self):
        report = DailySummaryReport(
            tenant_id="t-001",
            report_date=date(2026, 5, 30),
            leads_captured_today=5,
            followups_completed_today=12,
            followups_missed=3,
            payments_recorded_today=2,
            escalations_active=1,
            total_pipeline_value=1_500_000,
        )
        msg = format_summary_message(report, lang="en")
        assert "5" in msg
        assert "12" in msg
        assert "3" in msg
        assert "2" in msg
        assert "1" in msg
        assert "30 May 2026" in msg
        assert "1,500,000" in msg

    def test_unknown_lang_falls_back_to_english(self):
        report = DailySummaryReport(tenant_id="t-001", report_date=date(2026, 5, 30))
        msg_en  = format_summary_message(report, lang="en")
        msg_unk = format_summary_message(report, lang="xx")
        assert msg_en == msg_unk

    def test_urdu_template_contains_urdu_chars(self):
        report = DailySummaryReport(tenant_id="t-001", report_date=date(2026, 5, 30))
        msg = format_summary_message(report, lang="ur")
        assert "فالو" in msg or "لیڈز" in msg

    def test_zero_values_render_cleanly(self):
        report = DailySummaryReport(tenant_id="t-001", report_date=date(2026, 6, 1))
        msg = format_summary_message(report)
        assert "0" in msg
        assert "01 Jun 2026" in msg


# ── compute_daily_summary ─────────────────────────────────────────────────────

class TestComputeDailySummary:
    def test_returns_report_with_zero_counts_when_db_is_none(self):
        report = compute_daily_summary("t-001", db=None)
        assert isinstance(report, DailySummaryReport)
        assert report.tenant_id == "t-001"
        assert report.leads_captured_today == 0
        assert report.followups_completed_today == 0
        assert report.followups_missed == 0
        assert report.payments_recorded_today == 0
        assert report.escalations_active == 0

    def test_report_date_is_today(self):
        report = compute_daily_summary("t-001", db=None)
        assert report.report_date == date.today()


# ── send_daily_summary ────────────────────────────────────────────────────────

class TestSendDailySummary:
    def test_dry_run_returns_true_without_messaging_engine(self):
        result = send_daily_summary(
            tenant_id="t-001",
            owner_phone="+923001234567",
            lang="en",
            db=None,
            messaging_engine=None,
        )
        assert result is True

    def test_urdu_falls_back_to_english_and_still_succeeds(self):
        # P-017 guard: "ur" is not yet production-ready; function downgrades to "en"
        result = send_daily_summary(
            tenant_id="t-001",
            owner_phone="+923001234567",
            lang="ur",
            db=None,
            messaging_engine=None,
        )
        assert result is True

    def test_send_returns_false_when_messaging_engine_raises(self):
        class BrokenEngine:
            def send_outbound_message(self, **kwargs):
                raise RuntimeError("network failure")

        result = send_daily_summary(
            tenant_id="t-001",
            owner_phone="+923001234567",
            lang="en",
            db=None,
            messaging_engine=BrokenEngine(),
        )
        assert result is False
