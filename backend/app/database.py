"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

# Database URLs
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_ASYNC_URL = os.getenv("DATABASE_ASYNC_URL")


def _normalize_local_database_url(url: str | None) -> str | None:
    if not url:
        return url
    return url.replace("@localhost:", "@127.0.0.1:")

# Synchronous engine (for migrations and scripts)
engine = create_engine(_normalize_local_database_url(DATABASE_URL), echo=False)

# Async engine (for FastAPI)
async_engine = create_async_engine(
    _normalize_local_database_url(DATABASE_ASYNC_URL),
    echo=False,
    connect_args={"ssl": False},
)

# Session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database (create all tables)
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections
    """
    await async_engine.dispose()
