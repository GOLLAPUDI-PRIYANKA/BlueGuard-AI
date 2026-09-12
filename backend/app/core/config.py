from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    DATABASE_URL: str = "postgresql://marineguard:marineguard@localhost:5432/marineguard_db"
    AI_SERVICE_URL: str = "http://localhost:8001"
    AIS_SERVICE_URL: str = "http://localhost:8002"
    GIS_SERVICE_URL: str = "http://localhost:8003"
    ATTRIBUTION_SERVICE_URL: str = "http://localhost:8004"
    FORECAST_SERVICE_URL: str = "http://localhost:8005"
    IMPACT_SERVICE_URL: str = "http://localhost:8006"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    USE_MOCK_SERVICES: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
