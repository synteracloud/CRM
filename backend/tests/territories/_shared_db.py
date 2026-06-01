"""Shared SQLite engine for all territories tests."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

shared_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SharedSession = sessionmaker(autocommit=False, autoflush=False, bind=shared_engine)
