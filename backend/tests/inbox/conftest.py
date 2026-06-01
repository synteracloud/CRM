"""Seed fixtures for inbox API tests."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.inbox._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal

TEST_TENANT = "tenant-test-001"


@pytest.fixture(autouse=True)
def seed_inbox():
    """Create schema and seed inbox test data."""
    from services.db.base import Base
    import services.db.models  # noqa: F401
    from services.db.models.conversations import Conversation, ConversationMessage
    from services.db.models.inbox import InboxQueue

    Base.metadata.create_all(bind=_test_engine)
    now = datetime.now(timezone.utc)
    db = TestSessionLocal()
    try:
        # ── Conversations ─────────────────────────────────────────────────────
        # th-001: assigned to u-001, open, whatsapp
        conv1 = Conversation(
            conversation_id="th-001", tenant_id=TEST_TENANT,
            contact_id="ct-001", lead_id="l-001",
            channel="whatsapp", state="open",
            assigned_to="u-001",
            created_at=now, updated_at=now,
        )
        # th-002: resolved, email
        conv2 = Conversation(
            conversation_id="th-002", tenant_id=TEST_TENANT,
            contact_id="ct-002", lead_id=None,
            channel="email", state="resolved",
            assigned_to="u-001",
            created_at=now, updated_at=now,
        )
        # th-003: unassigned, open, whatsapp
        conv3 = Conversation(
            conversation_id="th-003", tenant_id=TEST_TENANT,
            contact_id="ct-003", lead_id=None,
            channel="whatsapp", state="open",
            assigned_to=None,
            created_at=now, updated_at=now,
        )
        for c in [conv1, conv2, conv3]:
            db.merge(c)

        # ── Seed a message on th-001 ──────────────────────────────────────────
        msg = ConversationMessage(
            message_id="msg-001", tenant_id=TEST_TENANT,
            conversation_id="th-001", contact_id="ct-001",
            direction="inbound", text="Hello, I need help.",
            occurred_at=now.isoformat(), created_at=now,
        )
        db.merge(msg)

        # ── Inbox Queues ──────────────────────────────────────────────────────
        queues = [
            InboxQueue(
                queue_id="q-001", tenant_id=TEST_TENANT,
                name="Sales Queue",
                routing_strategy="round_robin",
                skill_tags=None, team_id=None,
                auto_assign=True, is_active=True,
                created_at=now, updated_at=now,
            ),
            InboxQueue(
                queue_id="q-002", tenant_id=TEST_TENANT,
                name="Support Queue",
                routing_strategy="least_loaded",
                skill_tags=None, team_id=None,
                auto_assign=True, is_active=True,
                created_at=now, updated_at=now,
            ),
        ]
        for q in queues:
            db.merge(q)

        db.commit()
    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def db_session():
    """Yield a DB session pointing to the test engine."""
    sess = TestSessionLocal()
    try:
        yield sess
    finally:
        sess.close()
