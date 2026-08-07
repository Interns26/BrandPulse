# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

# backend/app/ingestion/fetch_sample_articles.py
import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import json
import logging
from app.ingestion.news_fetcher import fetch_competitive_news_articles

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def fetch_and_save_samples(limit: int = 5, output_file: str = "sample_output_articles.json"):
    logger.info(f"Fetching up to {limit} sample articles...")
    articles = fetch_competitive_news_articles(max_articles=limit)

    contract = [
        {
            "title": a.get("title", ""),
            "content": a.get("content", ""),
            "url": a.get("url", ""),
            "source_name": a.get("source_name", ""),
            "published_at": a.get("published_at", ""),
        }
        for a in articles
    ]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=4, ensure_ascii=False)

    logger.info(f"Saved {len(contract)} articles to {output_file}")

if __name__ == "__main__":
    fetch_and_save_samples(limit=5, output_file="sample_output_articles3.json")