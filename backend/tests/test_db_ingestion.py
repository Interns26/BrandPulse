import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
from app.database.session import SessionLocal, engine
from app.database.models import Base, Post, IngestionLog
from app.ingestion.rss_fetcher import run_ingestion_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_db")


def test_full_db_ingestion():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Starting ingestion cycle with DB persistence...")
        logs = run_ingestion_pipeline(db)
        
        print("\n" + "="*80)
        print("DATABASE INGESTION SUMMARY")
        print("="*80)
        for log in logs:
            print(f"Source: {log.source} | Fetched: {log.posts_fetched} | New Ingested: {log.posts_new} | Errors: {log.errors}")

        # Query Database for verified records
        stored_posts = db.query(Post).order_by(Post.id.desc()).limit(3).all()
        
        print("\n" + "="*80)
        print("VERIFYING POSTGRES DB STORED POSTS & AI RESULTS")
        print("="*80)
        
        for post in stored_posts:
            print(f"ID              : {post.id}")
            print(f"Title           : {post.title[:60]}...")
            print(f"Sentiment       : {post.sentiment} (Confidence: {post.sentiment_confidence}%)")
            print(f"Intent Category : {post.intent_category}")
            print(f"Intent Desc     : {post.intent_description}")
            print(f"Priority        : {post.priority}")
            print("-" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    test_full_db_ingestion()