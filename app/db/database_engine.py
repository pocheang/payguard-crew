"""
Production-grade database engine with connection pooling and multi-database support.
Supports PostgreSQL, MySQL, and SQLite (dev only).
"""
import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, Engine, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool

from app.config import get_settings


def get_database_url() -> str:
    """Get database URL based on environment configuration."""
    settings = get_settings()

    # Production: PostgreSQL (recommended)
    db_type = os.getenv("DATABASE_TYPE", "sqlite").lower()

    if db_type == "postgresql":
        user = os.getenv("POSTGRES_USER", "payguard")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "payguard")

        if not password:
            raise ValueError("POSTGRES_PASSWORD must be set for PostgreSQL")

        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

    elif db_type == "mysql":
        user = os.getenv("MYSQL_USER", "payguard")
        password = os.getenv("MYSQL_PASSWORD")
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        database = os.getenv("MYSQL_DB", "payguard")

        if not password:
            raise ValueError("MYSQL_PASSWORD must be set for MySQL")

        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"

    elif db_type == "sqlite":
        # SQLite: Dev/Testing only
        if settings.app_env in ["prod", "production"]:
            raise ValueError(
                "SQLite is not suitable for production. "
                "Please set DATABASE_TYPE to 'postgresql' or 'mysql'"
            )
        return f"sqlite:///{settings.db_path}"

    else:
        raise ValueError(f"Unsupported DATABASE_TYPE: {db_type}")


def create_db_engine() -> Engine:
    """Create database engine with production-grade connection pooling."""
    settings = get_settings()
    database_url = get_database_url()
    db_type = os.getenv("DATABASE_TYPE", "sqlite").lower()

    # Production connection pool settings
    pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "40"))
    pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour

    engine_kwargs = {
        "echo": settings.app_env == "dev",
        "future": True,
    }

    if db_type == "sqlite":
        # SQLite: No connection pooling (dev only)
        engine_kwargs["poolclass"] = NullPool
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # PostgreSQL/MySQL: Production connection pooling
        engine_kwargs["poolclass"] = QueuePool
        engine_kwargs["pool_size"] = pool_size
        engine_kwargs["max_overflow"] = max_overflow
        engine_kwargs["pool_timeout"] = pool_timeout
        engine_kwargs["pool_recycle"] = pool_recycle
        engine_kwargs["pool_pre_ping"] = True  # Verify connections before use

    engine = create_engine(database_url, **engine_kwargs)

    # Add connection event listeners for monitoring
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Log new database connections."""
        if settings.app_env == "dev":
            print(f"✅ New database connection established: {id(dbapi_conn)}")

    return engine


# Global engine instance
_engine: Engine | None = None


def get_engine() -> Engine:
    """Get or create the global database engine."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def create_session_factory() -> sessionmaker:
    """Create session factory with production settings."""
    engine = get_engine()
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


# Global session factory
SessionLocal = create_session_factory()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with get_db_session() as session:
            result = session.query(Model).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    with get_db_session() as session:
        yield session


def get_pool_status() -> dict:
    """Get connection pool status for monitoring."""
    engine = get_engine()

    if isinstance(engine.pool, QueuePool):
        return {
            "pool_size": engine.pool.size(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
            "checked_in": engine.pool.checkedin(),
        }

    return {"type": "NullPool", "message": "No connection pooling (SQLite)"}


def close_db_connections():
    """Close all database connections. Call on shutdown."""
    global _engine
    if _engine:
        _engine.dispose()
        _engine = None
