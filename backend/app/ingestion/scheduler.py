import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import get_settings
from app.database.session import SessionLocal
from app.ingestion.rss_fetcher import run_ingestion_pipeline
from app.ingestion.news_fetcher import fetch_competitive_news_articles

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler()


def scheduled_ingestion_job():
    """Wrapper task for APScheduler to manage DB sessions safely for Sprint 1."""
    logger.info("Starting scheduled Sprint 1 RSS ingestion cycle...")
    db = SessionLocal()
    try:
        logs = run_ingestion_pipeline(db)
        total_new = sum(log.posts_new for log in logs)
        logger.info(f"Ingestion cycle completed successfully. {total_new} new posts ingested.")
    except Exception as e:
        logger.error(f"Scheduled ingestion failed: {e}")
    finally:
        db.close()


def scheduled_competitive_ingestion_job():
    """Scheduled task for Sprint 2 competitive vulnerability news ingestion."""
    logger.info("Starting scheduled Sprint 2 Competitive News ingestion cycle...")
    try:
        articles = fetch_competitive_news_articles()
        logger.info(f"Competitive ingestion cycle complete. Fetched & pre-filtered {len(articles)} articles.")
        # Future integration point: Pass `articles` directly to Basim's run_vulnerability_pipeline(articles)
    except Exception as e:
        logger.error(f"Scheduled competitive ingestion failed: {e}")


def start_scheduler():
    """Starts the background scheduler for both Sprint 1 and Sprint 2 tasks."""
    sprint1_interval = settings.rss_fetch_interval_minutes
    sprint2_interval = settings.competitive_fetch_interval_minutes

    # Run jobs once immediately on startup
    scheduled_ingestion_job()
    scheduled_competitive_ingestion_job()

    # Sprint 1 Job Registration
    scheduler.add_job(
        scheduled_ingestion_job,
        trigger="interval",
        minutes=sprint1_interval,
        id="rss_ingestion_job",
        replace_existing=True,
    )

    # Sprint 2 Job Registration
    scheduler.add_job(
        scheduled_competitive_ingestion_job,
        trigger="interval",
        minutes=sprint2_interval,
        id="competitive_intel_job",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Ingestion scheduler running. Sprint 1 every {sprint1_interval}m, Sprint 2 every {sprint2_interval}m."
    )


def stop_scheduler():
    """Shuts down the background scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Ingestion scheduler stopped.")