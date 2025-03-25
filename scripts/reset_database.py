import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь для импорта
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from persistent.tables import metadata
from settings import settings


async def reset_database():
    logger.info("Resetting database...")
    
    # Создаем соединение с базой данных
    url = settings.pg.url
    if not url:
        url = f"postgresql+asyncpg://{settings.pg.username}:{settings.pg.password}@{settings.pg.host}:{settings.pg.port}/{settings.pg.database}"
    
    logger.info(f"Connecting to database: {url}")
    engine = create_async_engine(
        url,
        echo=True,
        pool_size=5,
        max_overflow=10,
    )
    
    try:
        async with engine.begin() as conn:
            # Удаляем существующие таблицы
            logger.info("Dropping all tables...")
            await conn.run_sync(metadata.drop_all)
            
            # Создаем таблицы заново
            logger.info("Creating tables with new schema...")
            await conn.run_sync(metadata.create_all)
            
        logger.info("Database reset complete!")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_database()) 