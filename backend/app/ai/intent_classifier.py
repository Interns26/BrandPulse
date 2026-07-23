from transformers import pipeline

MODEL = "facebook/bart-large-mnli"

FIRST_LEVEL = [
    "reporting a technical problem or software error",
    "managing a financial payment, invoice, or billing issue",
    "providing input regarding product or requesting a feature",
    "alerting about a computer security threat or privacy issue",
]

LEVEL_2_ROUTER = {
    "reporting a technical problem or software error": [
        "reporting system outages or server downtime",
        "reporting a functional software bug or application error",
        "reporting a login, registration, or authentication issue",
    ],
    "managing a financial payment, invoice, or billing issue": [
        "reporting failed payments or transaction processing errors",
        "disputing unexpected invoices, charges, or refund requests",
        "inquiring about subscription renewals or pricing plans",
    ],
    "providing input regarding product or requesting a feature": [
        "suggesting new product features or functional enhancements",
        "critiquing the user interface design or layout usability",
        "evaluating platform speed, loading times, and performance",
        "asking a clarifying question regarding the product, company policy or a process",
    ],
    "alerting about a computer security threat or privacy issue": [
        "reporting core security vulnerabilities or data privacy exposures",
        "flagging malicious spam, phishing attempts, or user abuse",
    ],
}

HYPOTHESIS_LEVEL_1 = "The user is writing this message because they are {}."
HYPOTHESIS_LEVEL_2 = "The precise action the user wants to take is {}."

DASHBOARD_LABEL_MAP = {
    "reporting a technical problem or software error": "Technical Issues",
    "managing a financial payment, invoice, or billing issue": "Billing & Payments",
    "providing input regarding product or requesting a feature": "Inquiry & Feedback",
    "alerting about a computer security threat or privacy issue": "Security Risks",
}

classifierPipeline = pipeline(
    task="zero-shot-classification", model=MODEL, use_safetensors=True
)


def analyzeIntent(text: str):
    firstLevel = classifierPipeline(
        text,
        candidate_labels=FIRST_LEVEL,
        multi_label=False,
        hypothesis_template=HYPOTHESIS_LEVEL_1,
    )

    overarchingIntent = firstLevel["labels"][0]
    microIntent = LEVEL_2_ROUTER[overarchingIntent]

    intent = classifierPipeline(
        text,
        candidate_labels=microIntent,
        multi_label=False,
        hypothesis_template=HYPOTHESIS_LEVEL_2,
    )

    output = {
        "category": DASHBOARD_LABEL_MAP[overarchingIntent],
        "description": intent["labels"][0],
        "confidence": round((intent["scores"][0] * 100), 2),
    }

    return output


if __name__ == "__main__":
    testInputs = [
        "Is anyone else getting a 'Connection to DB failed' error on the login page?? critical bug, fix asap pls.",
        "I was charged twice for my subscription this month!! Who do I talk to to get a refund for the duplicate transaction?",
    ]

    for input_text in testInputs:
        result = analyzeIntent(input_text)
        print(f"Text: {input_text}\nCategory: {result['category']}\nDescription: {result['description']}\nConfidence: {result['confidence']}%")
        print("-" * 50)