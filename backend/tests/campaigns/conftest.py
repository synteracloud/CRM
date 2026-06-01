"""Seed fixtures for campaigns API tests."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.campaigns._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal

TEST_TENANT = "tenant-test-001"


@pytest.fixture(autouse=True)
def seed_campaigns():
    """Create schema and seed campaign test data."""
    from services.db.base import Base
    import services.db.models  # noqa: F401
    from services.db.models.campaigns import Campaign, CampaignSegment, MessageTemplate

    Base.metadata.create_all(bind=_test_engine)
    now = datetime.now(timezone.utc)
    db = TestSessionLocal()
    try:
        # ── Campaigns ─────────────────────────────────────────────────────────
        campaigns = [
            Campaign(
                campaign_id="cmp-001", tenant_id=TEST_TENANT,
                name="Q1 2026 Email Campaign", type="email",
                status="completed", segment_id="seg-001", template_id="tpl-001",
                activated_at=now, completed_at=now,
                created_by="system", created_at=now, updated_at=now,
            ),
            Campaign(
                campaign_id="cmp-002", tenant_id=TEST_TENANT,
                name="WhatsApp Broadcast Feb", type="whatsapp_broadcast",
                status="scheduled", segment_id="seg-001", template_id="tpl-001",
                created_by="system", created_at=now, updated_at=now,
            ),
            Campaign(
                campaign_id="cmp-003", tenant_id=TEST_TENANT,
                name="Active SMS Campaign", type="sms",
                status="active", segment_id="seg-001", template_id="tpl-001",
                activated_at=now,
                created_by="system", created_at=now, updated_at=now,
            ),
            Campaign(
                campaign_id="cmp-004", tenant_id=TEST_TENANT,
                name="Another Completed", type="email",
                status="completed", segment_id="seg-001", template_id="tpl-001",
                completed_at=now,
                created_by="system", created_at=now, updated_at=now,
            ),
            Campaign(
                campaign_id="cmp-005", tenant_id=TEST_TENANT,
                name="Draft Without Segment", type="email",
                status="draft", segment_id=None, template_id=None,
                created_by="system", created_at=now, updated_at=now,
            ),
            Campaign(
                campaign_id="cmp-006", tenant_id=TEST_TENANT,
                name="Paused Campaign", type="whatsapp_broadcast",
                status="paused", segment_id="seg-001", template_id="tpl-001",
                paused_at=now,
                created_by="system", created_at=now, updated_at=now,
            ),
        ]
        for c in campaigns:
            db.merge(c)

        # ── Segments ──────────────────────────────────────────────────────────
        segments = [
            CampaignSegment(
                segment_id="seg-001", tenant_id=TEST_TENANT,
                name="Active Leads - Punjab", entity_type="lead",
                rules=[{"rule_id": "r1", "field": "lead.city", "operator": "eq", "value": "Lahore"}],
                estimated_size=150, is_dynamic=True,
                created_by="system", created_at=now, updated_at=now,
            ),
            CampaignSegment(
                segment_id="seg-002", tenant_id=TEST_TENANT,
                name="Contact Segment", entity_type="contact",
                rules=[],
                estimated_size=80, is_dynamic=True,
                created_by="system", created_at=now, updated_at=now,
            ),
        ]
        for s in segments:
            db.merge(s)

        # ── Templates ─────────────────────────────────────────────────────────
        templates = [
            MessageTemplate(
                template_id="tpl-001", tenant_id=TEST_TENANT,
                name="Email Welcome Template", channel="email", language="en",
                body="Welcome {{contact.name}}! Thank you for joining us.",
                is_urdu=False, meta_template_status=None,
                created_by="system", created_at=now, updated_at=now,
            ),
            MessageTemplate(
                template_id="tpl-002", tenant_id=TEST_TENANT,
                name="SMS Promo Template", channel="sms", language="en",
                body="Get 20% off your next purchase! Reply YES to claim.",
                is_urdu=False, meta_template_status=None,
                created_by="system", created_at=now, updated_at=now,
            ),
            MessageTemplate(
                template_id="tpl-003", tenant_id=TEST_TENANT,
                name="WhatsApp Broadcast", channel="whatsapp_broadcast", language="en",
                body="Hi {{contact.name}}, we have a special offer for you!",
                is_urdu=False, meta_template_status="approved",
                created_by="system", created_at=now, updated_at=now,
            ),
        ]
        for t in templates:
            db.merge(t)

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
