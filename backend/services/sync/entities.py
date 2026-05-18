from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Literal

SyncStatus = Literal["queued", "syncing", "synced", "failed", "conflict", "dead_letter"]
ConflictPolicy = Literal["last_write_wins", "merge", "server_wins", "append", "reject", "accept_if_open"]

# Per-entity conflict resolution strategies.
# Source: docs/offline-sync.md §7.2 Resolution Strategies by Entity
ENTITY_CONFLICT_STRATEGY: dict[str, ConflictPolicy] = {
    "lead_stage":    "server_wins",   # stage transitions carry business significance
    "activity":      "append",        # immutable append-only — no conflict possible
    "note":          "append",
    "contact":       "merge",         # field-level merge; overlapping fields: server wins
    "followup":      "last_write_wins",
    "payment":       "reject",        # financial accuracy — require explicit re-entry
    "task":          "accept_if_open",
    "lead":          "merge",         # default for general lead field updates
    "opportunity":   "merge",
    "message":       "append",
}

DEFAULT_CONFLICT_POLICY: ConflictPolicy = "last_write_wins"


class SyncError(Exception):
    """Base sync-layer error."""


class ConflictResolutionError(SyncError):
    """Raised when payloads cannot be merged safely."""


@dataclass(frozen=True)
class OfflineAction:
    action_id: str
    tenant_id: str
    device_id: str
    idempotency_key: str        # (tenant_id + device_id + local_seq_no) — docs §4
    entity_type: str
    entity_id: str
    op: Literal["create", "update", "delete"]
    payload: dict[str, Any]
    base_version: int
    client_timestamp: str
    attempts: int = 0
    status: SyncStatus = "queued"
    last_error: str | None = None

    def touch(self, **changes: Any) -> "OfflineAction":
        return replace(self, **changes)


@dataclass(frozen=True)
class EntityEnvelope:
    entity_type: str
    entity_id: str
    version: int
    updated_at: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SyncResult:
    action_id: str
    status: SyncStatus
    attempts: int
    conflict_detected: bool = False
    resolved_with: ConflictPolicy | None = None
    server_version: int | None = None
    message: str = ""


@dataclass(frozen=True)
class ReliabilityReport:
    queued: int
    synced: int
    failed: int
    dead_letter: int
    conflict_count: int
    data_loss_risk: bool
    data_loss_risk_reasons: tuple[str, ...]
    alignment_percent: float
    score: str


def utc_now() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
