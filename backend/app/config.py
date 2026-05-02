from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PORT: int = 3001
    JWT_SECRET: str = "fallback_secret_change_me"
    DATABASE_URL: str = "postgresql://jesus:2025@localhost:5432/costos"
    JWT_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
