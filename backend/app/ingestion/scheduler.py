import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import get_settings
from app.database.session import SessionLocal
from app.ingestion.rss_fetcher import run_ingestion_pipeline

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler()


def scheduled_ingestion_job():
    """Wrapper task for APScheduler to manage DB sessions safely."""
    logger.info("Starting scheduled RSS ingestion cycle...")
    db = SessionLocal()
    try:
        logs = run_ingestion_pipeline(db)
        total_new = sum(log.posts_new for log in logs)
        logger.info(f"Ingestion cycle completed successfully. {total_new} new posts ingested.")
    except Exception as e:
        logger.error(f"Scheduled ingestion failed: {e}")
    finally:
        db.close()



def start_scheduler():
    """Starts the background scheduler."""
    interval_minutes = settings.rss_fetch_interval_minutes

     # Run once immediately
    # scheduled_ingestion_job()

    scheduler.add_job(
        scheduled_ingestion_job,
        trigger="interval",
        minutes=interval_minutes,
        id="rss_ingestion_job",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info(f"Ingestion scheduler started. Running every {interval_minutes} minutes.")


def stop_scheduler():
    """Shuts down the background scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Ingestion scheduler stopped.")