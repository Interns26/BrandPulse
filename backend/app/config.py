# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

# backend/app/config.py
from functools import lru_cache
from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "BrandPulse"
    debug: bool = False

    # Infrastructure & Storage
    database_url: str = "postgresql://brandpulse:brandpulse123@postgres:5432/brandpulse"
    sentiment_model_path: str = "/app/models_storage"
    intent_model_name: str = "MoritzLaurer/deberta-v3-base-zeroshot-v1"

    # Ingestion Configuration (Sprint 1)
    rss_fetch_interval_minutes: int = 50
    rss_user_agent: str = "desktop:com.brandpulse.app:v1.0.0 (by /u/brandpulse_dev)"
    default_rss_urls: Dict[str, str] = {}

    # Sprint 2 – Competitive News
    competitor_keywords: List[str] = [
        "square", "toast", "clover", "lightspeed", "par tech", "revel",
        "shopify", "ncr", "oracle", "micros", "touchbistro", "vend",
        "stripe", "adyen", "fiserv", "first data"
    ]
    pos_context_keywords: List[str] = [
        "point of sale", "pos", "payment processing", "merchant services",
        "card reader", "checkout system", "cash register", "payment terminal",
        "outage", "price increase", "fee hike", "restaurant tech",
        "merchant acquiring", "fintech"
    ]
    exclusion_keywords: List[str] = [
        "square root", "times square", "square feet", "square inch",
        "town square", "cinnamon toast", "french toast", "clover leaf",
        "four leaf clover", "airport", "album", "tribute", "election",
        "vacuum", "tiger", "diplomacy", "military", "discount"
    ]
    competitive_news_rss_urls: Dict[str, str] = {
        "google_news_pos": "https://news.google.com/rss/search?q=point+of+sale+OR+POS+outage+OR+Square+OR+Toast+OR+Clover&hl=en-US&gl=US&ceid=US:en",
        "techcrunch_pos": "https://techcrunch.com/tag/point-of-sale/feed/",
    }
    competitive_fetch_interval_minutes: int = 30

    # Validation & Extraction Settings
    validation_mode: str = "lenient"  # 'lenient' or 'strict' - START WITH LENIENT
    min_word_count: int = 100         # Lowered from 200 for testing
    extractor_fallback_to_summary: bool = True
    blacklist_domains: List[str] = [
        "wsj.com", "bloomberg.com", "ft.com", "economist.com",
        "nytimes.com", "barrons.com", "seekingalpha.com",
        "theatlantic.com", "newyorker.com", "businessinsider.com"
    ]
    decode_interval: int = 3
    ingestion_log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()