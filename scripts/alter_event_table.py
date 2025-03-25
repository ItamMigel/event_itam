import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь для импорта
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from settings import settings


async def alter_event_table():
    logger.info("Altering event table to add unique constraint...")
    
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
            # Проверяем, существует ли уже ограничение
            check_query = """
            SELECT COUNT(*) FROM pg_constraint 
            WHERE conname = 'uq_event_title_start_date'
            """
            result = await conn.execute(text(check_query))
            constraint_exists = (await result.scalar()) > 0
            
            if not constraint_exists:
                # Добавляем ограничение уникальности
                logger.info("Adding unique constraint on title and start_date...")
                add_constraint_query = """
                ALTER TABLE event 
                ADD CONSTRAINT uq_event_title_start_date 
                UNIQUE (title, start_date);
                """
                await conn.execute(text(add_constraint_query))
                logger.info("Unique constraint added successfully!")
            else:
                logger.info("Unique constraint already exists, skipping.")
            
        logger.info("Event table alteration complete!")
    except Exception as e:
        logger.error(f"Error altering event table: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(alter_event_table()) 