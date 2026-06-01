"""Seed fixtures for partner API tests."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.partners._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal

TEST_TENANT = "tenant-test-001"


@pytest.fixture(autouse=True)
def seed_partners():
    """Create schema and seed partner test data."""
    from services.db.base import Base
    from services.db.models.partners import Partner, PartnerCommission

    Base.metadata.create_all(bind=_test_engine)

    now = datetime.now(timezone.utc)
    db = TestSessionLocal()
    try:
        partners = [
            Partner(
                partner_id="p-001",
                tenant_id=TEST_TENANT,
                name="NovaTech Solutions",
                partner_tier="platinum",
                status="active",
                region="Punjab",
                city="Lahore",
                contact_name="Ahmad Khan",
                contact_phone="+923001234567",
                contact_email="ahmad@novatech.pk",
                attributed_opp_count=5,
                total_commission_earned=150000.0,
                commission_due=50000.0,
                deal_registration_count=3,
                created_by="system",
                created_at=now,
                updated_at=now,
            ),
            Partner(
                partner_id="p-002",
                tenant_id=TEST_TENANT,
                name="Karachi Digital Partners",
                partner_tier="gold",
                status="active",
                region="Sindh",
                city="Karachi",
                contact_name="Sara Ali",
                contact_phone="+923009876543",
                contact_email="sara@kdp.pk",
                attributed_opp_count=3,
                total_commission_earned=80000.0,
                commission_due=20000.0,
                deal_registration_count=2,
                created_by="system",
                created_at=now,
                updated_at=now,
            ),
            Partner(
                partner_id="p-003",
                tenant_id=TEST_TENANT,
                name="Islamabad Tech Hub",
                partner_tier="silver",
                status="active",
                region="ICT",
                city="Islamabad",
                contact_name="Usman Raza",
                attributed_opp_count=1,
                total_commission_earned=10000.0,
                commission_due=5000.0,
                deal_registration_count=1,
                created_by="system",
                created_at=now,
                updated_at=now,
            ),
            Partner(
                partner_id="p-007",
                tenant_id=TEST_TENANT,
                name="Inactive Partner Co",
                partner_tier="silver",
                status="inactive",
                region="Punjab",
                city="Multan",
                attributed_opp_count=0,
                total_commission_earned=0.0,
                commission_due=0.0,
                deal_registration_count=0,
                created_by="system",
                created_at=now,
                updated_at=now,
            ),
        ]
        for p in partners:
            db.merge(p)

        commissions = [
            PartnerCommission(
                commission_id="com-001",
                partner_id="p-001",
                tenant_id=TEST_TENANT,
                opportunity_id="opp-001",
                opportunity_name="Enterprise Deal A",
                amount=50000.0,
                rate=0.15,
                status="pending",
                calculated_at=now,
                created_at=now,
                updated_at=now,
            ),
            PartnerCommission(
                commission_id="com-002",
                partner_id="p-001",
                tenant_id=TEST_TENANT,
                opportunity_id="opp-002",
                opportunity_name="Enterprise Deal B",
                amount=30000.0,
                rate=0.15,
                status="approved",
                calculated_at=now,
                approved_at=now,
                approved_by="mgr-001",
                created_at=now,
                updated_at=now,
            ),
            PartnerCommission(
                commission_id="com-003",
                partner_id="p-001",
                tenant_id=TEST_TENANT,
                opportunity_id="opp-003",
                opportunity_name="Enterprise Deal C",
                amount=70000.0,
                rate=0.15,
                status="paid",
                calculated_at=now,
                approved_at=now,
                approved_by="mgr-001",
                paid_at=now,
                payment_reference="TRF-2026-001",
                created_at=now,
                updated_at=now,
            ),
        ]
        for c in commissions:
            db.merge(c)

        db.commit()
    finally:
        db.close()
