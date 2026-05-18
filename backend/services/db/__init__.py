from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        url = os.environ.get(
            "DATABASE_URL",
            "postgresql+psycopg2://crm:changeme@localhost:5432/crm",
        )
        _engine = create_engine(url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine, _SessionLocal


def get_db() -> Generator[Session, None, None]:
    _, session_factory = _get_engine()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
