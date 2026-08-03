"""Database engine and session factory.

Pool settings are env-tunable because the previous fixed `pool_size=3,
max_overflow=0` serialised the service at three concurrent queries — a fourth
request blocked until it timed out. `pool_pre_ping` and `pool_recycle` are the
fix for MySQL closing idle connections after `wait_timeout`: without them
SQLAlchemy hands out a dead socket and the request fails with a 500 that
retries "mysteriously" fix.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configs import Configuration

SQLALCHEMY_DATABASE_URL = Configuration.DB_URI

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    # Recycle below MySQL's default wait_timeout so we never reuse a socket
    # the server has already dropped.
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency yielding a session that is always closed.

    The rollback matters: without it a failed request leaves its transaction
    open, and the next caller to check out that pooled connection inherits the
    aborted transaction state.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
