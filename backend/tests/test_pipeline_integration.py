import json
import logging
import sys
from pathlib import Path

# Fix Python path resolution so 'app' module can be imported cleanly
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.ai.pipeline import process_ingested_packet
from app.config import get_settings
from app.ingestion.rss_fetcher import build_clean_packet, fetch_feed_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_integration")
settings = get_settings()

TEST_FEEDS = {
    "r_artificial_intelligence": "https://www.reddit.com/r/ArtificialInteligence/.rss",
    "r_samsung": "https://www.reddit.com/r/samsung/.rss",
}

OUTPUT_FILE = ROOT_DIR / "test_results.json"


def run_pipeline_test():
    all_results = []

    for source_name, feed_url in TEST_FEEDS.items():
        logger.info(f"Fetching RSS feed for '{source_name}' from: {feed_url}")
        try:
            feed_data = fetch_feed_data(feed_url, settings.rss_user_agent)
        except Exception as e:
            logger.error(f"Failed to fetch feed {source_name}: {e}")
            continue

        if not feed_data or not getattr(feed_data, "entries", None):
            logger.error(f"No entries found for: {source_name}")
            continue

        entries = feed_data.entries[:3]  # Take top 3 posts per feed

        for entry in entries:
            # 1. Clean and transform RSS entry into pipeline packet
            packet = build_clean_packet(source_name, entry)

            # 2. Process packet through AI inference models (standalone packet mode)
            # Pass db=None or dict-only mode depending on pipeline handling
            processed_output = process_ingested_packet(packet)

            # 3. Append to structured list
            all_results.append(processed_output)

    # 4. Save results to JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False, default=str)

    logger.info(
        f"Successfully saved {len(all_results)} processed posts to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    run_pipeline_test()