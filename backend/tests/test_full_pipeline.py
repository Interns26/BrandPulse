"""
End-to-end test:
1. Fetch real RSS feeds
2. Clean & build packets
3. Run through AI pipeline (Basim's process_ingested_packet)
4. Store in PostgreSQL
5. Query database to verify
"""
import json
import logging
import sys
sys.path.insert(0, '/app')
from app.database.session import SessionLocal
from app.database.models import Post, SentimentResult, IntentResult
from app.ingestion.rss_fetcher import run_ingestion_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_pipeline():
    db = SessionLocal()
    try:
        # Run the complete ingestion pipeline (all configured RSS sources)
        logger.info("Starting full ingestion pipeline...")
        logs = run_ingestion_pipeline(db)
        total_new = sum(log.posts_new for log in logs)
        logger.info(f"Ingestion complete. {total_new} new posts added.")

        # Query all posts with their AI results
        posts = db.query(Post).order_by(Post.fetched_at.desc()).limit(10).all()

        results = []
        for post in posts:
            sentiment = db.query(SentimentResult).filter(
                SentimentResult.post_id == post.id
            ).first()
            intent = db.query(IntentResult).filter(
                IntentResult.post_id == post.id
            ).first()

            results.append({
                "id": str(post.id),
                "title": post.title,
                "author": post.author,
                "source": post.source_name,
                "fetched_at": post.fetched_at.isoformat() if post.fetched_at else None,
                "sentiment": sentiment.sentiment if sentiment else None,
                "sentiment_confidence": sentiment.confidence if sentiment else None,
                "intent_category": intent.intent_category if intent else None,
                "intent_confidence": intent.confidence if intent else None,
            })

        # Print to terminal
        print("\n" + "="*60)
        print("RECENT POSTS IN DATABASE")
        print("="*60)
        for r in results:
            print(f"Title: {r['title']}")
            print(f"  Sentiment: {r['sentiment']} ({r['sentiment_confidence']}%)")
            print(f"  Intent: {r['intent_category']} ({r['intent_confidence']}%)")
            print(f"  Source: {r['source']} | Author: {r['author']}")
            print(f"  Fetched: {r['fetched_at']}")
            print("-"*60)

        # Optionally save to JSON file
        with open("/app/test_results_db.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info("Results saved to /app/test_results_db.json")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_full_pipeline()