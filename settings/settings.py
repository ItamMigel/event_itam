import multiprocessing as mp

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка значений по умолчанию для обеспечения работы приложения
DEFAULT_DB = "events_db"
DEFAULT_HOST = "postgres"
DEFAULT_PORT = 5432
DEFAULT_USER = "postgres"
DEFAULT_PASSWORD = "postgres"
DEFAULT_CONNECTION_URL = f"postgresql+asyncpg://{DEFAULT_USER}:{DEFAULT_PASSWORD}@{DEFAULT_HOST}:{DEFAULT_PORT}/{DEFAULT_DB}"


class Postgres(BaseModel):
    database: str = Field(default_factory=lambda: os.getenv("POSTGRES_DB", DEFAULT_DB))
    host: str = Field(default_factory=lambda: os.getenv("HOST_POSTGRES", DEFAULT_HOST))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT_POSTGRES", DEFAULT_PORT)))
    username: str = Field(default_factory=lambda: os.getenv("POSTGRES_USER", DEFAULT_USER))
    password: str = Field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", DEFAULT_PASSWORD))
    url: str = Field(default_factory=lambda: os.getenv("CONNECTION_URL", DEFAULT_CONNECTION_URL))


class Uvicorn(BaseModel):
    host: str = Field(default_factory=lambda: os.getenv("HOST_BACKEND", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT_BACKEND", 8000)))
    workers: int = Field(default_factory=lambda: mp.cpu_count() * 2 + 1)


class _Settings(BaseSettings):
    pg: Postgres = Postgres()
    uvicorn: Uvicorn = Uvicorn()

    #model_config = SettingsConfigDict(env_file=".env", env_prefix="app_", env_nested_delimiter="__")


settings = _Settings()
logger.info("Settings initialized: {}", settings.model_dump_json())
