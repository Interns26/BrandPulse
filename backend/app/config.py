from functools import lru_cache
from typing import Dict
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "BrandPulse"
    debug: bool = False
    
    # Infrastructure & Storage
    database_url: str = "postgresql://brandpulse:brandpulse123@postgres:5432/brandpulse"
    sentiment_model_path: str = "/app/models_storage"
    intent_model_name: str = "MoritzLaurer/deberta-v3-base-zeroshot-v1"
    
    # Ingestion Configuration
    rss_fetch_interval_minutes: int = 30
    rss_user_agent: str = "BrandPulse/1.0"
    
    # Scalable: Pydantic automatically parses JSON strings from env into a Dict
    default_rss_urls: Dict[str, str] = {}

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()