import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import get_settings
from app.database.session import SessionLocal
from app.ingestion.rss_fetcher import run_ingestion_pipeline
from app.ingestion.news_fetcher import fetch_competitive_news_articles
from app.services.article_service import save_article

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
    except Exception:
        logger.exception("Scheduled competitive ingestion failed")
    finally:
        db.close()


def scheduled_competitive_ingestion_job():
    """Fetch competitive news, persist raw articles, then process them."""
    logger.info("Starting Sprint 2 Competitive News ingestion cycle...")

    db = SessionLocal()

    try:
        logger.info("Calling fetch_competitive_news_articles()...")

        articles = fetch_competitive_news_articles()

        logger.info(
            f"Competitive ingestion fetched {len(articles)} articles."
        )

        for i, article_data in enumerate(articles, start=1):
            logger.info(
                f"Saving article {i}/{len(articles)}: "
                f"{article_data.get('title', 'NO TITLE')}"
            )

            save_article(db, article_data)

        logger.info(
            f"Saved {len(articles)} competitive articles to database."
        )

    except Exception:
        logger.exception("Scheduled competitive ingestion failed")

    finally:
        db.close()


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