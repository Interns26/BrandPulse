import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.ai.intent_classifier import analyzeIntent
from app.ai.sentiment_analyzer import analyzeSentiment
from app.database.models import Post, SentimentResult, IntentResult

logger = logging.getLogger(__name__)

# ── Priority mapping (unchanged) ──────────────────────────────
INTENT_PRIORITY_MAP = {
    "reporting system outages or server downtime": "High",
    "reporting core security vulnerabilities or data privacy exposures": "High",
    "reporting a login, registration, or authentication issue": "High",
    "reporting a functional software bug or application error": "Medium",
    "reporting failed payments or transaction processing errors": "Medium",
    "disputing unexpected invoices, charges, or refund requests": "Medium",
    "inquiring about subscription renewals or pricing plans": "Low",
    "suggesting new product features or functional enhancements": "Low",
    "critiquing the user interface design or layout usability": "Low",
    "evaluating platform speed, loading times, and performance": "Low",
    "flagging malicious spam, phishing attempts, or user abuse": "Low",
}


def assignPriority(description: str, sentiment: str) -> str:
    priority = INTENT_PRIORITY_MAP.get(description, "Medium")
    if priority == "Medium" and sentiment.upper() == "NEGATIVE":
        priority = "High"
    elif priority == "Low" and sentiment.upper() == "NEGATIVE":
        priority = "Medium"
    return priority


def analyzeSentimentAndIntent(text: str) -> dict:
    sentiment = analyzeSentiment(text)
    intent = analyzeIntent(text)
    priority = assignPriority(
        description=intent["description"], sentiment=sentiment["label"]
    )
    return {"sentiment": sentiment, "intent": intent, "priority": priority}


def process_ingested_packet(packet: dict, db: Session = None) -> bool:
    """
    Takes Ismail's clean packet, runs AI models, stores results in DB.
    Returns True if successful (post is new and stored), False otherwise.
    """
    try:
        ai_input = packet.get("ai_input_text", "")
        if not ai_input:
            logger.warning("Empty ai_input_text, skipping.")
            return False

        # Run both models
        ai_results = analyzeSentimentAndIntent(ai_input)

        # Enrich packet dict for potential JSON output (not saved to Post)
        packet["sentiment"] = ai_results["sentiment"]["label"]
        packet["sentiment_confidence"] = ai_results["sentiment"]["confidence"]
        packet["intent_category"] = ai_results["intent"]["category"]
        packet["intent_description"] = ai_results["intent"]["description"]
        packet["intent_confidence"] = ai_results["intent"]["confidence"]
        packet["priority"] = ai_results["priority"]

        # If a DB session is provided, persist to PostgreSQL
        if db is not None:
            # Parse fetched_at
            fetched_at_str = packet.get("fetched_at")
            if isinstance(fetched_at_str, str):
                fetched_at_dt = datetime.fromisoformat(fetched_at_str)
            else:
                fetched_at_dt = fetched_at_str

            # Create Post with only the Post columns
            post = Post(
                source=packet["source"],
                source_name=packet["source_name"],
                external_id=packet["external_id"],
                author=packet["author"],
                title=packet["title"],
                content=packet["content"],
                content_hash=packet["content_hash"],
                url=packet["url"],
                fetched_at=fetched_at_dt,
            )

            # Create related AI result objects
            post.sentiment_result = SentimentResult(
                sentiment=packet["sentiment"],
                confidence=packet["sentiment_confidence"],
            )
            post.intent_result = IntentResult(
                intent_category=packet["intent_category"],
                confidence=packet["intent_confidence"],
            )

            db.add(post)
            db.commit()
            logger.info(f"Stored post {packet['content_hash'][:8]}... in DB.")
            return True

        return True  # No DB, but processing succeeded

    except Exception as e:
        logger.error(f"Pipeline failed for packet: {e}")
        if db:
            db.rollback()
        return False