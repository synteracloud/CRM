"""Integration tests for public /api/v1/admin/dead-letters DLQ operator API.

Spec: backend/docs/execution-hardening.md
API standards: backend/docs/api-standards.md
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

import services.core.execution.http.public as dlq_module
from services.app import app
from services.auth.jwt_deps import TokenClaims, get_current_user
from services.core.execution.control_plane import ExecutionControlPlane

# ── Fixtures ──────────────────────────────────────────────────────────────────

TEST_TENANT = "tenant-dlq-001"


def _override_admin():
    return TokenClaims(
        sub="admin-001",
        tenant_id=TEST_TENANT,
        role="admin",
        jti=str(uuid.uuid4()),
    )


def _override_non_admin():
    return TokenClaims(
        sub="user-001",
        tenant_id=TEST_TENANT,
        role="sales_rep",
        jti=str(uuid.uuid4()),
    )


@pytest.fixture(autouse=True)
def fresh_plane():
    plane = ExecutionControlPlane()
    dlq_module.set_plane(plane)
    yield plane
    dlq_module.set_plane(ExecutionControlPlane())


@pytest.fixture
def admin_client():
    app.dependency_overrides[get_current_user] = _override_admin
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def non_admin_client():
    app.dependency_overrides[get_current_user] = _override_non_admin
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _seed_dead_letter(plane: ExecutionControlPlane, job_id: str = "job-001") -> str:
    """Enqueue a job and fail it past max_attempts to create a dead-lettered entry."""
    plane.recovery.enqueue(job_id, {"op": "test"}, max_attempts=1)
    plane.recovery.mark_failed(job_id, reason="simulated failure")
    return job_id


# ── GET /api/v1/admin/dead-letters ───────────────────────────────────────────


class TestListDeadLetters:
    def test_empty_queue_returns_200(self, admin_client: TestClient) -> None:
        r = admin_client.get("/api/v1/admin/dead-letters")
        assert r.status_code == 200
        assert r.json()["data"] == []

    def test_lists_dead_lettered_jobs(self, admin_client: TestClient, fresh_plane: ExecutionControlPlane) -> None:
        _seed_dead_letter(fresh_plane, "job-list-001")
        r = admin_client.get("/api/v1/admin/dead-letters")
        assert r.status_code == 200
        assert len(r.json()["data"]) == 1

    def test_non_admin_returns_403(self, non_admin_client: TestClient) -> None:
        r = non_admin_client.get("/api/v1/admin/dead-letters")
        assert r.status_code == 403

    def test_meta_contains_total(self, admin_client: TestClient, fresh_plane: ExecutionControlPlane) -> None:
        _seed_dead_letter(fresh_plane, "job-meta-001")
        r = admin_client.get("/api/v1/admin/dead-letters")
        assert "total" in r.json()["meta"]


# ── POST /api/v1/admin/dead-letters/{id}/retry ───────────────────────────────


class TestRetryDeadLetter:
    def test_retry_transitions_to_in_progress(
        self, admin_client: TestClient, fresh_plane: ExecutionControlPlane
    ) -> None:
        job_id = _seed_dead_letter(fresh_plane, "job-retry-001")
        r = admin_client.post(f"/api/v1/admin/dead-letters/{job_id}/retry")
        assert r.status_code == 200
        assert r.json()["data"]["state"] == "in_progress"

    def test_retry_unknown_job_returns_404(self, admin_client: TestClient) -> None:
        r = admin_client.post("/api/v1/admin/dead-letters/nonexistent/retry")
        assert r.status_code == 404

    def test_retry_non_dead_lettered_returns_409(
        self, admin_client: TestClient, fresh_plane: ExecutionControlPlane
    ) -> None:
        fresh_plane.recovery.enqueue("job-pending", {"op": "test"})
        r = admin_client.post("/api/v1/admin/dead-letters/job-pending/retry")
        assert r.status_code == 409


# ── POST /api/v1/admin/dead-letters/{id}/requeue ─────────────────────────────


class TestRequeueDeadLetter:
    def test_requeue_resets_to_pending(
        self, admin_client: TestClient, fresh_plane: ExecutionControlPlane
    ) -> None:
        job_id = _seed_dead_letter(fresh_plane, "job-requeue-001")
        r = admin_client.post(f"/api/v1/admin/dead-letters/{job_id}/requeue")
        assert r.status_code == 200
        assert r.json()["data"]["state"] == "pending"

    def test_requeue_unknown_job_returns_404(self, admin_client: TestClient) -> None:
        r = admin_client.post("/api/v1/admin/dead-letters/nonexistent/requeue")
        assert r.status_code == 404

    def test_requeue_non_dead_lettered_returns_409(
        self, admin_client: TestClient, fresh_plane: ExecutionControlPlane
    ) -> None:
        fresh_plane.recovery.enqueue("job-pend2", {"op": "test"})
        r = admin_client.post("/api/v1/admin/dead-letters/job-pend2/requeue")
        assert r.status_code == 409
