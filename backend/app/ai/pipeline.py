from intent_classifier import analyzeIntent
from sentiment_analyzer import analyzeSentiment

INTENT_PRIORITY_MAP = {
    # CRITICAL / HIGH PRIORITY: Major operational or security blockers
    "reporting system outages or server downtime": "High",
    "reporting core security vulnerabilities or data privacy exposures": "High",
    "reporting a login, registration, or authentication issue": "High",
    # MEDIUM PRIORITY: Financial transactions & functional bugs
    "reporting a functional software bug or application error": "Medium",
    "reporting failed payments or transaction processing errors": "Medium",
    "disputing unexpected invoices, charges, or refund requests": "Medium",
    # LOW PRIORITY: Non-blocking inquiries, feedback, and general chatter
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
            f"Sentiment:\n Label: {sentiment["label"]}\n Confidence: {sentiment["confidence"]}"
        )
        print(
            f"Intent:\n Category: {intent["category"]}\n Description: {intent["description"]}\n Confidence: {intent["confidence"]}"
        )
        print(f"Priority: {priority}")
        print("-" * 50)
