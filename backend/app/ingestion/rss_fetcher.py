# rss_fetcher.py — Ismail's territory

import hashlib
import logging
from datetime import datetime, timezone
import feedparser
import httpx
from sqlalchemy.orm import Session
import time
from app.config import get_settings
from app.database.models import IngestionLog, Post, RssSource
from app.ingestion.cleaner import clean_text, prepare_text_for_ai

# Basim provides this function — Ismail just imports and calls it
from app.ai.pipeline import process_ingested_packet

logger = logging.getLogger(__name__)
settings = get_settings()


def generate_content_hash(source: str, external_id: str, title: str) -> str:
    """Creates a deterministic SHA-256 hash to prevent duplicate entries."""
    unique_string = f"{source}:{external_id}:{title}"
    return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()


def fetch_feed_data(url: str, user_agent: str) -> feedparser.FeedParserDict:
    """Fetches raw RSS XML using httpx."""
    headers = {"User-Agent": user_agent}
    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return feedparser.parse(response.text)


def build_clean_packet(source_name: str, entry) -> dict:
    """
    Builds a clean data packet from a raw RSS entry.
    This is the ONLY format Ismail's layer outputs.
    """
    external_id = getattr(entry, "id", getattr(entry, "link", ""))
    title = getattr(entry, "title", "")
    raw_content = getattr(entry, "summary", getattr(entry, "description", ""))
    author = getattr(entry, "author", "unknown")
    post_url = getattr(entry, "link", "")

    cleaned_title = clean_text(title)
    cleaned_content = clean_text(raw_content)
    ai_input_text = prepare_text_for_ai(cleaned_title, cleaned_content)
    content_hash = generate_content_hash(source_name, external_id, title)

    return {
        "source": "reddit_rss",
        "source_name": source_name,
        "external_id": external_id,
        "author": author,
        "title": cleaned_title,
        "content": cleaned_content,
        "ai_input_text": ai_input_text,
        "content_hash": content_hash,
        "url": post_url,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }


def process_rss_feed(source_name: str, url: str, db: Session) -> tuple[int, int]:
    """
    Processes a single RSS feed source.
    Builds clean packets and hands them to Basim's pipeline.
    """
    posts_fetched = 0
    posts_new = 0

    try:
        feed = fetch_feed_data(url, settings.rss_user_agent)
        posts_fetched = len(feed.entries)

        for entry in feed.entries:
            # Step 1: Build clean packet
            packet = build_clean_packet(source_name, entry)

            if not packet["ai_input_text"]:
                continue

            # Step 2: Check for duplicates
            existing_post = db.query(Post).filter(
                Post.content_hash == packet["content_hash"]
            ).first()
            if existing_post:
                continue

            # Step 3: Hand off to Basim's function
            # Ismail doesn't know or care what happens inside this function
            success = process_ingested_packet(packet, db)

            if success:
                posts_new += 1

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing RSS feed '{source_name}' ({url}): {e}")
        raise e

    return posts_fetched, posts_new


def run_ingestion_pipeline(db: Session) -> list[IngestionLog]:
    """Iterates across all configured RSS sources."""

    logger.info("=== Entered run_ingestion_pipeline ===")

    logs = []

    logger.info("Loading RSS sources...")
    sources = settings.default_rss_urls

    logger.info("Checking database for active RSS sources...")
    db_sources = db.query(RssSource).filter(RssSource.is_active == True).all()

    logger.info(f"Found {len(db_sources)} active RSS sources in database.")

    if db_sources:
        logger.info("Using RSS sources from database.")
        sources = {source.name: source.url for source in db_sources}
    else:
        logger.info("Using default RSS sources from config.")

    logger.info(f"Total sources to process: {len(sources)}")

    for source_name, url in sources.items():
        logger.info(f"Processing source: {source_name}")

        started_at = datetime.now(timezone.utc)
        error_msg = None
        fetched_count = 0
        new_count = 0

        try:
            logger.info("Calling process_rss_feed()...")
            fetched_count, new_count = process_rss_feed(source_name, url, db)
            logger.info(
                f"process_rss_feed() finished. "
                f"Fetched={fetched_count}, New={new_count}"
            )
            time.sleep(2)

        except Exception as e:
            logger.exception("Error inside process_rss_feed()")
            error_msg = str(e)

        completed_at = datetime.now(timezone.utc)

        logger.info("Creating ingestion log entry...")

        log_entry = IngestionLog(
            source=source_name,
            posts_fetched=fetched_count,
            posts_new=new_count,
            errors=error_msg,
            started_at=started_at,
            completed_at=completed_at,
        )

        db.add(log_entry)
        db.commit()

        logger.info(f"Saved ingestion log for {source_name}")

        logs.append(log_entry)

    logger.info("=== Finished run_ingestion_pipeline ===")

    return logs