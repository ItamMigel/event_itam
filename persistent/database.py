from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.connection import pg_connection

# Create async session maker
async_session_maker = pg_connection()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an async context manager for database sessions.
    
    Usage:
        async with get_session() as session:
            query = select(...)
            result = await session.execute(query)
    
    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise 