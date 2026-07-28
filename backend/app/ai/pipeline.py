import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.ai.intent_classifier import analyzeIntent
from app.ai.sentiment_analyzer import analyzeSentiment
from app.database.models import Post, SentimentResult, IntentResult

logger = logging.getLogger(__name__)

# ── Priority mapping (unchanged) ──────────────────────────────
INTENT_PRIORITY_MAP = {
    # --- HIGH PRIORITY (Critical outages, active security breaches, & urgent compliance) ---
    "reporting system outages or server downtime": "High",
    "reporting core security vulnerabilities or data privacy exposures": "High",
    "reporting a login, registration, or authentication issue": "High",
    "reporting unauthorized access or account takeover attempts": "High",
    "reporting integration or API failure issues": "High",
    "requesting account deletion or data export under privacy laws": "High",
    "flagging potential copyright, patent, or intellectual property infringement": "High",

    # --- MEDIUM PRIORITY (Functional bugs, billing disputes, sales leads, & PR/legal risks) ---
    "reporting a functional software bug or application error": "Medium",
    "reporting failed payments or transaction processing errors": "Medium",
    "disputing unexpected invoices, charges, or refund requests": "Medium",
    "requesting customized enterprise pricing or plan changes": "Medium",
    "troubleshooting two-factor authentication or password resets": "Medium",
    "modifying team permissions, roles, or organization settings": "Medium",
    "exploring migration or switching options from another platform": "Medium",
    "reacting to public policy, leadership statements, or brand controversy": "Medium",
    "reporting antitrust, regulatory fines, or government policy updates": "Medium",
    "disputing terms of service agreements or privacy policy changes": "Medium",

    # --- LOW PRIORITY (General feedback, feature requests, UI reviews, & standard news) ---
    "inquiring about subscription renewals or pricing plans": "Low",
    "suggesting new product features or functional enhancements": "Low",
    "critiquing the user interface design or layout usability": "Low",
    "evaluating platform speed, loading times, and performance": "Low",
    "asking a clarifying question regarding the product, company policy or a process": "Low",
    "flagging malicious spam, phishing attempts, or user abuse": "Low",
    "commenting on corporate acquisitions, layoffs, or financial results": "Low",
    "sharing news updates or press releases regarding company actions": "Low",
    "evaluating feature parity against competing platforms": "Low",
    "discussing price-to-value ratio compared to alternative tools": "Low",
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
                priority=packet["priority"],
                ai_input_text=ai_input,
            )

            # Create related AI result objects
            post.sentiment_result = SentimentResult(
                sentiment=packet["sentiment"],
                confidence=packet["sentiment_confidence"],
            )
            post.intent_result = IntentResult(
                intent_category=packet["intent_category"],
                intent_description=packet["intent_description"],
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

if __name__ == "__main__":

    testInputs = [
        # Technical & Product Issues
        "Is anyone else getting a 'Connection to DB failed' error on the login page?? critical bug, fix asap pls.",
        "The new dashboard update is completely unusable. Every time I click export, the entire app crashes and freezes my browser.",
        "Your mobile app is lagging so hard today. It takes literally 10 seconds just to scroll down the product feed.",
        "Trying to log in but the OTP email is just not arriving. Stuck on the verification screen for an hour now.",
        "Getting an internal server error 500 when attempting to checkout. Please look into this, my cart is full.",
        "The API endpoints keep throwing a 403 forbidden error even though my auth token is completely valid.",
        "App just crashed randomly while I was mid-edit. Lost all my progress... absolutely frustrating.",
        # Financial & Business Operations
        "I was charged twice for my subscription this month!! Who do I talk to to get a refund for the duplicate transaction?",
        "Hey team, my card failed during renewal but I can't find where to update my billing information on the new UI.",
        "Your pricing tiers make zero sense. Am I on the Pro plan or the Enterprise plan if I have 15 team members?",
        "Tried cancelling my trial last week but I just got an invoice in my email today. Please cancel this immediately.",
        "Is there a way to download the PDF invoice for last quarter's payment? I need it for my company's tax filing.",
        "Locked out of my premium account and the password reset link is expired. Need access urgently for a business presentation.",
        # Product Feedback & Growth
        "It would be amazing if we could get a dark mode option for the desktop site. My eyes are burning during late night coding.",
        "Wow, the loading speed on the v2 platform is incredibly fast! Huge props to the engineering team for this optimization.",
        "The new layout looks clean, but honestly, the old navigation bar was much more intuitive to use.",
        "Can we please get a bulk-select feature for deleting old logs? Doing it one by one is taking forever.",
        # Security & Compliance
        "Just noticed a massive security flaw where user emails are exposed in the public page source code. Fix this immediately!!",
        "Where can I find your updated GDPR policy? Need to make sure our company data pipeline complies with your storage rules.",
        "Getting a ton of weird phishing/spam messages in my inbox from accounts pretending to be your official support team.",
    ]

    for input in testInputs:

        pred = analyzeSentimentAndIntent(input)
        sentiment = pred["sentiment"]
        intent = pred["intent"]
        priority = pred["priority"]

        print(f"Text: {input}")
        print(
            f"Sentiment:\n Label: {sentiment['label']}\n Confidence: {sentiment['confidence']}"
        )
        print(
            f"Intent:\n Category: {intent['category']}\n Description: {intent['description']}\n Confidence: {intent['confidence']}"
        )
        print(f"Priority: {priority}")
        print("-" * 50)