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
        "inquiring about subscription renewals or pricing plans"
    ],
    "providing input regarding product or requesting a feature": [
        "suggesting new product features or functional enhancements",
        "critiquing the user interface design or layout usability",
        "evaluating platform speed, loading times, and performance",
        "asking a clarifying question regarding the product, company policy or a process"
    ],
    "alerting about a computer security threat or privacy issue": [
        "reporting core security vulnerabilities or data privacy exposures",
        "flagging malicious spam, phishing attempts, or user abuse"
    ]
}


# Level 1 checks the macro objective
HYPOTHESIS_LEVEL_1 = "The user is writing this message because they are {}."

# Level 2 zeroes in on the explicit action
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

    overarchingIntent = firstLevel['labels'][0]

    microIntent = LEVEL_2_ROUTER[overarchingIntent]

    intent = classifierPipeline(
        text,
        candidate_labels=microIntent,
        multi_label=False,
        hypothesis_template=HYPOTHESIS_LEVEL_2,
    )

    # descriptions = []
    # confidence = []

    # for i in range(0, len(intent['labels'])):
    #     if 

    output = {
        'category': DASHBOARD_LABEL_MAP[overarchingIntent],
        'description': intent['labels'][0],
        'confidence': round((intent['scores'][0]*100), 2)
    }

    return output


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

        result = analyzeIntent(input)

        print(f'Text: {input}\nCategory: {result['category']}\nDescription: {result['description']}\nConfidence: {result['confidence']}%')
        print('-'*50)