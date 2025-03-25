import uvicorn
import sys
from loguru import logger

from settings import settings


if __name__ == "__main__":
    # Настраиваем логирование
    logger.remove()  # Удаляем стандартный обработчик
    logger.add(
        sys.stdout, 
        level="DEBUG",  # Устанавливаем уровень логирования DEBUG для подробного вывода
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Добавляем логирование в файл
    logger.add(
        "app_debug.log",
        level="DEBUG",
        rotation="100 MB",  # Ротация логов при превышении размера
        retention="7 days",  # Хранение логов в течение 7 дней
        compression="zip"    # Сжатие старых логов
    )
    
    logger.info(f"Starting server on http://{settings.uvicorn.host}:{settings.uvicorn.port}")
    logger.info(f"Settings: {settings.dict()}")
    
    # Запускаем сервер
    uvicorn.run(
        "app:app",
        host=settings.uvicorn.host,
        port=settings.uvicorn.port,
        reload=True,  # Автоматическая перезагрузка при изменении кода
        log_level="debug"
    ) 