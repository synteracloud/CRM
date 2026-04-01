from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Literal

SyncStatus = Literal["queued", "syncing", "synced", "failed", "dead_letter"]
ConflictPolicy = Literal["last_write_wins", "merge"]


class SyncError(Exception):
    """Base sync-layer error."""


class ConflictResolutionError(SyncError):
    """Raised when payloads cannot be merged safely."""


@dataclass(frozen=True)
class OfflineAction:
    action_id: str
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
