"""Daily WhatsApp activity summary for managers (MR-004).

Aggregates today's CRM activity across leads, follow-ups, collections, and
escalations, then formats a WhatsApp template message and sends it via the
messaging adapter to the tenant owner's number.

Schedule: run daily at a configurable time per tenant (default 08:00 PKT).
Docs: backend/market-research-gap-register.md §MR-004
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone

logger = logging.getLogger(__name__)


# ── Report model ──────────────────────────────────────────────────────────────

@dataclass
class DailySummaryReport:
    tenant_id: str
    report_date: date

    leads_captured_today: int = 0
    followups_completed_today: int = 0
    followups_missed: int = 0        # state = overdue
    payments_recorded_today: int = 0
    escalations_active: int = 0

    # Optional: enriched context computed by compute()
    total_open_leads: int = 0
    total_pipeline_value: float = 0.0


# ── i18n templates ────────────────────────────────────────────────────────────

_TEMPLATES: dict[str, str] = {
    "en": (
        "📊 *Daily CRM Summary — {date}*\n\n"
        "🆕 Leads captured: *{leads_captured}*\n"
        "✅ Follow-ups completed: *{followups_completed}*\n"
        "⚠️  Missed follow-ups: *{followups_missed}*\n"
        "💰 Payments recorded: *{payments_recorded}*\n"
        "🚨 Active escalations: *{escalations_active}*\n\n"
        "_Open pipeline: PKR {pipeline_value:,}_\n"
        "_Powered by NexLink CRM_"
    ),
    # P-017: Urdu version pending native speaker sign-off.
    # Placeholder provided; DO NOT send to customers until P-017 resolved.
    "ur": (
        "📊 *روزانہ CRM خلاصہ — {date}*\n\n"
        "🆕 آج کے لیڈز: *{leads_captured}*\n"
        "✅ مکمل فالو اَپ: *{followups_completed}*\n"
        "⚠️  چھوٹے ہوئے فالو اَپ: *{followups_missed}*\n"
        "💰 ادائیگیاں درج: *{payments_recorded}*\n"
        "🚨 فعال ایسکلیشنز: *{escalations_active}*\n\n"
        "_کھلا پائپ لائن: PKR {pipeline_value:,}_\n"
        "_NexLink CRM_"
    ),
}


def format_summary_message(report: DailySummaryReport, lang: str = "en") -> str:
    """Render the summary report as a WhatsApp template string."""
    template = _TEMPLATES.get(lang, _TEMPLATES["en"])
    return template.format(
        date=report.report_date.strftime("%d %b %Y"),
        leads_captured=report.leads_captured_today,
        followups_completed=report.followups_completed_today,
        followups_missed=report.followups_missed,
        payments_recorded=report.payments_recorded_today,
        escalations_active=report.escalations_active,
        pipeline_value=int(report.total_pipeline_value),
    )


# ── Aggregation ───────────────────────────────────────────────────────────────

def compute_daily_summary(tenant_id: str, db=None) -> DailySummaryReport:
    """Aggregate today's CRM activity for a tenant.

    Args:
        tenant_id: Tenant to aggregate for.
        db: SQLAlchemy session. When None, returns zero-filled report
            (safe for tests or when DB is unavailable).

    Returns:
        DailySummaryReport populated with today's counts.
    """
    report = DailySummaryReport(
        tenant_id=tenant_id,
        report_date=date.today(),
    )

    if db is None:
        return report

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        from services.db.models.lead import Lead
        from services.db.models.followup import FollowupTask
        from services.db.models.invoice import Invoice, Payment

        # Leads captured today
        report.leads_captured_today = (
            db.query(Lead)
            .filter(Lead.tenant_id == tenant_id, Lead.created_at >= today_start)
            .count()
        )

        # Total open leads + pipeline value
        open_leads = (
            db.query(Lead)
            .filter(Lead.tenant_id == tenant_id, Lead.status == "open")
            .all()
        )
        report.total_open_leads = len(open_leads)
        report.total_pipeline_value = sum(
            float(l.estimated_value or 0) for l in open_leads
        )

        # Follow-ups completed today
        report.followups_completed_today = (
            db.query(FollowupTask)
            .filter(
                FollowupTask.tenant_id == tenant_id,
                FollowupTask.state == "completed",
                FollowupTask.completed_at >= today_start,
            )
            .count()
        )

        # Missed follow-ups (overdue state)
        report.followups_missed = (
            db.query(FollowupTask)
            .filter(FollowupTask.tenant_id == tenant_id, FollowupTask.state == "overdue")
            .count()
        )

        # Escalations active
        report.escalations_active = (
            db.query(FollowupTask)
            .filter(
                FollowupTask.tenant_id == tenant_id,
                FollowupTask.state.in_(["escalated", "overdue"]),
                FollowupTask.escalation_level.in_(["warning", "escalated", "reassigned"]),
            )
            .count()
        )

        # Payments recorded today (count of paid invoices updated today)
        report.payments_recorded_today = (
            db.query(Invoice)
            .filter(
                Invoice.tenant_id == tenant_id,
                Invoice.status == "paid",
                Invoice.updated_at >= today_start,
            )
            .count()
        )

    except Exception as exc:
        logger.exception("daily_summary: aggregation failed for tenant=%s: %s", tenant_id, exc)

    return report


# ── Send ──────────────────────────────────────────────────────────────────────

def send_daily_summary(
    *,
    tenant_id: str,
    owner_phone: str,
    lang: str = "en",
    db=None,
    messaging_engine=None,
) -> bool:
    """Compute and send the daily summary to the tenant owner via WhatsApp.

    Args:
        tenant_id:       Tenant identifier.
        owner_phone:     E.164 phone number of the manager to notify.
        lang:            Language code — "en" or "ur" (P-017 gate: "ur" is a draft).
        db:              SQLAlchemy session. None = dry-run (compute only, no send).
        messaging_engine: WhatsAppCoreEngine instance. None = log only.

    Returns:
        True if message was sent (or logged), False if aggregation failed.
    """
    if lang == "ur":
        logger.warning(
            "daily_summary: Urdu template is a draft pending P-017 sign-off. "
            "Falling back to English."
        )
        lang = "en"

    report  = compute_daily_summary(tenant_id, db=db)
    message = format_summary_message(report, lang=lang)

    if messaging_engine is None:
        logger.info(
            "daily_summary: [DRY RUN] tenant=%s date=%s message=%r",
            tenant_id,
            report.report_date,
            message,
        )
        return True

    try:
        from adapters.interfaces.types import AdapterContext
        ctx = AdapterContext(tenant_id=tenant_id, user_id="system", request_id="daily-summary")
        messaging_engine.send_outbound_message(
            to=owner_phone,
            body=message,
            intent="daily_summary",
            ctx=ctx,
            business_context="management_report",
        )
        logger.info(
            "daily_summary: sent to %s for tenant=%s date=%s",
            owner_phone, tenant_id, report.report_date,
        )
        return True
    except Exception as exc:
        logger.exception("daily_summary: send failed for tenant=%s: %s", tenant_id, exc)
        return False
