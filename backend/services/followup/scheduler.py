"""Deterministic scheduler queue for follow-up enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import heapq


@dataclass(order=True, frozen=True)
class ScheduledJob:
    run_at: datetime
    job_type: str
    lead_id: str
    task_id: str | None = None


class FollowupJobQueue:
    """Simple time-ordered queue used by follow-up workers."""

    def __init__(self) -> None:
        self._jobs: list[ScheduledJob] = []

    def enqueue(self, job: ScheduledJob) -> None:
        heapq.heappush(self._jobs, job)

    def pop_due(self, now: datetime) -> list[ScheduledJob]:
        due: list[ScheduledJob] = []
        while self._jobs and self._jobs[0].run_at <= now:
            due.append(heapq.heappop(self._jobs))
        return due

    def size(self) -> int:
        return len(self._jobs)
