from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from time import time
from typing import Any


ALLOWED_STATES = {"pending", "in_progress", "succeeded", "failed_retryable", "dead_lettered"}


@dataclass
class Job:
    job_id: str
    payload: dict[str, Any]
    state: str = "pending"
    attempts: int = 0
    max_attempts: int = 5
    last_error: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    updated_at: float = field(default_factory=time)


class RecoveryQueue:
    def __init__(self) -> None:
        self._lock = RLock()
        self._jobs: dict[str, Job] = {}

    def enqueue(self, job_id: str, payload: dict[str, Any], *, max_attempts: int = 5) -> Job:
        with self._lock:
            if job_id in self._jobs:
                return self._jobs[job_id]
            job = Job(job_id=job_id, payload=payload, max_attempts=max_attempts)
            self._jobs[job_id] = job
            return job

    def claim(self, job_id: str) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            if job.state in {"succeeded", "dead_lettered"}:
                return job
            job.state = "in_progress"
            job.updated_at = time()
            return job

    def mark_succeeded(self, job_id: str) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            job.state = "succeeded"
            job.updated_at = time()
            job.history.append({"state": "succeeded", "at": job.updated_at})
            return job

    def mark_failed(self, job_id: str, *, reason: str) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            job.attempts += 1
            job.last_error = reason
            job.updated_at = time()
            if job.attempts >= job.max_attempts:
                job.state = "dead_lettered"
            else:
                job.state = "failed_retryable"
            job.history.append({"state": job.state, "at": job.updated_at, "error": reason})
            return job

    def requeue(self, job_id: str) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            if job.state == "dead_lettered":
                job.state = "pending"
                job.updated_at = time()
                job.history.append({"state": "pending", "at": job.updated_at, "action": "manual_requeue"})
            return job

    def snapshot(self) -> dict[str, Job]:
        with self._lock:
            return dict(self._jobs)
