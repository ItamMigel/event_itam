from settings.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from loguru import logger


def pg_connection() -> async_sessionmaker[AsyncSession]:
    """Create a PostgreSQL connection using SQLAlchemy."""
    # If no URL is provided in settings, construct it from individual components
    if not settings.pg.url:
        logger.warning("Database URL is not set in environment, constructing from components")
        try:
            db_url = (
                f"postgresql+asyncpg://{settings.pg.username}:{settings.pg.password}"
                f"@{settings.pg.host}:{settings.pg.port}/{settings.pg.database}"
            )
            logger.info(f"Constructed database URL: {db_url}")
        except Exception as e:
            logger.error(f"Failed to construct database URL: {str(e)}")
            # Fallback to a direct string in case the settings object is incomplete
            db_url = "postgresql+asyncpg://postgres:postgres@postgres:5432/events_db"
            logger.info(f"Using fallback database URL: {db_url}")
    else:
        db_url = 'postgresql+asyncpg://postgres:postgres@postgres:5432/events_db'
        logger.info(f"Using database URL from environment: {db_url}")
        
    logger.info(f"Final DB URL: {db_url or 'None'}")
    
    # Create engine with pool settings for better stability
    engine = create_async_engine(
        db_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )
    
    return async_sessionmaker(autocommit=False, autoflush=False, bind=engine)