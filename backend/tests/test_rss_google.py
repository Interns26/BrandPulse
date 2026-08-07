# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

import json
import logging
import os
import sys

# Ensure backend root directory is in import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion.rss_fetcher import fetch_and_filter_pos_batch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("test_rss_google")

OUTPUT_FILE = "ingested_articles.json"

if __name__ == "__main__":
    logger.info("==================================================================")
    logger.info("      STARTING RSS / GOOGLE NEWS INGESTION DIAGNOSTIC TEST       ")
    logger.info("==================================================================")

    articles = fetch_and_filter_pos_batch()

    logger.info("------------------------------------------------------------------")
    logger.info(f"COMPLETE: Verified {len(articles)} articles matching two-factor criteria.")
    logger.info("------------------------------------------------------------------\n")

    for idx, art in enumerate(articles, start=1):
        logger.info(f"[{idx}/{len(articles)}] [{art['source']}] {art['title']}")
        logger.info(f"     URL: {art['url']}")
        logger.info(f"     Words: {art['word_count']}")
        logger.info(f"     Trigger: Entity ['{art['matched_entity']}'] | Context ['{art['matched_context']}']")
        logger.info(f"     Preview: \"{art['content'][:120]}...\"\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    logger.info(f"SUCCESS: Saved verified records directly to '{OUTPUT_FILE}'.\n")