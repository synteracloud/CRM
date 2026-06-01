"""Case domain entities: state machine, SLA tier defaults, transition guards.

Domain spec: backend/docs/domain/cases-domain.md §2, §3, §4
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional


class CaseStatus(str, Enum):
    OPEN                = "OPEN"
    ASSIGNED            = "ASSIGNED"
    IN_PROGRESS         = "IN_PROGRESS"
    WAITING_ON_CUSTOMER = "WAITING_ON_CUSTOMER"
    RESOLVED            = "RESOLVED"
    ESCALATED           = "ESCALATED"
    CLOSED              = "CLOSED"


class CasePriority(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"


class SLATier(str, Enum):
    TIER_1_CRITICAL = "tier_1_critical"
    TIER_2_HIGH     = "tier_2_high"
    TIER_3_STANDARD = "tier_3_standard"
    TIER_4_LOW      = "tier_4_low"


# Default SLA windows — spec §2.5 (Pakistan business hours: 09:00–19:00 PKT Mon–Sat)
SLA_DEFAULTS: dict[SLATier, dict[str, int]] = {
    SLATier.TIER_1_CRITICAL: {"first_response_hours": 1,  "resolution_hours": 8},
    SLATier.TIER_2_HIGH:     {"first_response_hours": 4,  "resolution_hours": 24},
    SLATier.TIER_3_STANDARD: {"first_response_hours": 8,  "resolution_hours": 72},
    SLATier.TIER_4_LOW:      {"first_response_hours": 24, "resolution_hours": 168},
}

# Spec §3.1 — valid transitions per source status
ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "OPEN":                ["ASSIGNED", "CLOSED"],
    "ASSIGNED":            ["IN_PROGRESS", "OPEN", "ESCALATED", "CLOSED"],
    "IN_PROGRESS":         ["WAITING_ON_CUSTOMER", "RESOLVED", "ESCALATED", "CLOSED"],
    "WAITING_ON_CUSTOMER": ["IN_PROGRESS", "RESOLVED", "CLOSED"],
    "RESOLVED":            ["CLOSED", "IN_PROGRESS"],
    "ESCALATED":           ["ASSIGNED", "IN_PROGRESS", "CLOSED"],
    "CLOSED":              ["OPEN"],
}

# Pakistan timezone: UTC+5 (PKT), no DST
_PKT_OFFSET      = timedelta(hours=5)
_BIZ_START_HOUR  = 9   # 09:00 PKT
_BIZ_END_HOUR    = 19  # 19:00 PKT


class CaseTransitionError(ValueError):
    """Raised when an invalid or guard-blocked state transition is attempted."""


def validate_transition(from_status: str, to_status: str) -> None:
    """Raise CaseTransitionError if the transition is not in the allowed matrix."""
    allowed = ALLOWED_TRANSITIONS.get(from_status, [])
    if to_status not in allowed:
        raise CaseTransitionError(
            f"Transition {from_status!r} → {to_status!r} is not permitted. "
            f"Allowed from {from_status!r}: {allowed}"
        )


def _to_pkt_naive(dt: datetime) -> datetime:
    """Convert UTC-aware datetime to PKT naive datetime."""
    return (dt.astimezone(timezone.utc) + _PKT_OFFSET).replace(tzinfo=None)


def _to_utc_aware(dt_pkt: datetime) -> datetime:
    """Convert PKT naive datetime back to UTC-aware."""
    return (dt_pkt - _PKT_OFFSET).replace(tzinfo=timezone.utc)


def compute_sla_deadline(start_utc: datetime, hours: int) -> datetime:
    """
    Advance `hours` business hours from start_utc.
    Business hours: 09:00–19:00 PKT, Monday–Saturday.
    Returns UTC-aware deadline.
    """
    remaining = hours * 60  # work in minutes
    cursor = _to_pkt_naive(start_utc)

    while remaining > 0:
        wd = cursor.weekday()  # 0=Mon … 6=Sun

        if wd == 6:  # Sunday — jump to Monday 09:00
            cursor = (cursor + timedelta(days=1)).replace(
                hour=_BIZ_START_HOUR, minute=0, second=0, microsecond=0
            )
            continue

        if cursor.hour >= _BIZ_END_HOUR:  # after-hours — next business day
            step = 2 if wd == 5 else 1   # Saturday → Monday
            cursor = (cursor + timedelta(days=step)).replace(
                hour=_BIZ_START_HOUR, minute=0, second=0, microsecond=0
            )
            continue

        if cursor.hour < _BIZ_START_HOUR:  # pre-hours — advance to open
            cursor = cursor.replace(
                hour=_BIZ_START_HOUR, minute=0, second=0, microsecond=0
            )
            continue

        # Inside business hours — consume minutes until end-of-day or done
        end_of_biz = cursor.replace(hour=_BIZ_END_HOUR, minute=0, second=0, microsecond=0)
        avail = int((end_of_biz - cursor).total_seconds() / 60)

        if remaining <= avail:
            cursor += timedelta(minutes=remaining)
            remaining = 0
        else:
            remaining -= avail
            cursor = end_of_biz  # triggers after-hours branch next iteration

    return _to_utc_aware(cursor)
