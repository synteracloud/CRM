"""Seed fixtures for cases API tests.

The cases tests create their own cases dynamically — no seeded cases needed.
This conftest only ensures schema is in place via the setup_test_db fixture
in the test file itself.
"""
from __future__ import annotations

import pytest

from tests.cases._shared_db import shared_engine as _test_engine, SharedSession as TestSessionLocal


@pytest.fixture
def db_session():
    """Yield a DB session pointing to the test engine."""
    sess = TestSessionLocal()
    try:
        yield sess
    finally:
        sess.close()
