from pathlib import Path
from transformers import pipeline

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOCAL_MODEL_PATH = str(BASE_DIR / "models_storage" / "intent_model")

FIRST_LEVEL = [
    "reporting a system outage, application bug, or software malfunction",
    "a financial matter involving payment, invoicing, refunds, or enterprise pricing",
    "product feedback, a feature request, or UI/performance commentary",
    "a security vulnerability, data exposure, or account takeover risk",
    "an account, login, permissions, or personal-data request such as deletion or export",
    "company news, leadership decisions, funding, or public relations",
    "a direct comparison to a named competitor or alternative tool",
    "a legal, regulatory, copyright, or terms-of-service matter",
]

LEVEL_2_ROUTER = {
    "reporting a system outage, application bug, or software malfunction": [
        "reporting a system outage or server downtime affecting the whole platform",
        "reporting a functional software bug or application crash",
        "reporting a login, registration, or authentication error (not a lost password or 2FA issue)",
        "reporting an integration or API failure between systems",
    ],
    "a financial matter involving payment, invoicing, refunds, or enterprise pricing": [
        "reporting a failed or declined payment or transaction processing error",
        "disputing an unexpected invoice, duplicate charge, or requesting a refund",
        "asking about subscription renewal dates or standard pricing plans",
        "requesting a custom enterprise pricing quote or negotiated plan change",
    ],
    "product feedback, a feature request, or UI/performance commentary": [
        "suggesting a new product feature or functional enhancement",
        "criticizing or praising the user interface design and layout usability",
        "commenting on platform speed, loading times, or performance",
        "asking a general clarifying question about how the product or a policy works",
    ],
    "a security vulnerability, data exposure, or account takeover risk": [
        "reporting a security vulnerability or unintended exposure of private data",
        "flagging a phishing attempt, spam, or abusive user behavior",
        "reporting unauthorized account access or a suspected account takeover",
    ],
    "an account, login, permissions, or personal-data request such as deletion or export": [
        "requesting account deletion or a personal data export under privacy law such as GDPR",
        "troubleshooting two-factor authentication codes or resetting a forgotten password",
        "modifying team member permissions, roles, or organization settings",
    ],
    "company news, leadership decisions, funding, or public relations": [
        "commenting on a corporate acquisition, layoffs, or financial results",
        "reacting to a leadership statement, public policy, or brand controversy",
        "sharing or reacting to general company news or press releases",
    ],
    "a direct comparison to a named competitor or alternative tool": [
        "comparing specific features against a named competing platform",
        "comparing price-to-value against an alternative tool",
        "asking about migrating or switching from a competitor's platform",
    ],
    "a legal, regulatory, copyright, or terms-of-service matter": [
        "alleging copyright, patent, or intellectual property infringement",
        "referencing an antitrust matter, regulatory fine, or government policy update",
        "disputing terms of service or a privacy policy change",
    ],
}


HYPOTHESIS_LEVEL_1 = "This text is about {}."
HYPOTHESIS_LEVEL_2 = "Specifically, this message is {}."

DASHBOARD_LABEL_MAP = {
    "reporting a system outage, application bug, or software malfunction": "Technical Issues",
    "a financial matter involving payment, invoicing, refunds, or enterprise pricing": "Billing & Payments",
    "product feedback, a feature request, or UI/performance commentary": "Inquiry & Feedback",
    "a security vulnerability, data exposure, or account takeover risk": "Security Risks",
    "an account, login, permissions, or personal-data request such as deletion or export": "Account & Access",
    "company news, leadership decisions, funding, or public relations": "PR & Brand Reputation",
    "a direct comparison to a named competitor or alternative tool": "Competitive Comparison",
    "a legal, regulatory, copyright, or terms-of-service matter": "Legal & Compliance",
}


LEAF_INTENTS = {
    # -- Technical Issues --
    "reporting a system outage or server downtime affecting the whole platform": "Technical Issues",
    "reporting a functional software bug or application crash": "Technical Issues",
    "reporting a login, registration, or authentication error (not a lost password or 2FA issue)": "Technical Issues",
    "reporting an integration or API failure between systems": "Technical Issues",
    # -- Billing & Payments --
    "reporting a failed or declined payment or transaction processing error": "Billing & Payments",
    "disputing an unexpected invoice, duplicate charge, or requesting a refund": "Billing & Payments",
    "asking about subscription renewal dates or standard pricing plans": "Billing & Payments",
    "requesting a custom enterprise pricing quote or negotiated plan change": "Billing & Payments",
    # -- Inquiry & Feedback --
    "suggesting a new product feature or functional enhancement": "Inquiry & Feedback",
    "criticizing or praising the user interface design and layout usability": "Inquiry & Feedback",
    "commenting on platform speed, loading times, or performance": "Inquiry & Feedback",
    "asking a general clarifying question about how the product or a policy works": "Inquiry & Feedback",
    # -- Security Risks --
    "reporting a security vulnerability or unintended exposure of private data": "Security Risks",
    "flagging a phishing attempt, spam, or abusive user behavior": "Security Risks",
    "reporting unauthorized account access or a suspected account takeover": "Security Risks",
    # -- Account & Access --
    "requesting account deletion or a personal data export under privacy law such as GDPR": "Account & Access",
    "troubleshooting two-factor authentication codes or resetting a forgotten password": "Account & Access",
    "modifying team member permissions, roles, or organization settings": "Account & Access",
    # -- PR & Brand Reputation --
    "commenting on a corporate acquisition, layoffs, or financial results": "PR & Brand Reputation",
    "reacting to a leadership statement, public policy, or brand controversy": "PR & Brand Reputation",
    "sharing or reacting to general company news or press releases": "PR & Brand Reputation",
    # -- Competitive Comparison --
    "comparing specific features against a named competing platform": "Competitive Comparison",
    "comparing price-to-value against an alternative tool": "Competitive Comparison",
    "asking about migrating or switching from a competitor's platform": "Competitive Comparison",
    # -- Legal & Compliance --
    "alleging copyright, patent, or intellectual property infringement": "Legal & Compliance",
    "referencing an antitrust matter, regulatory fine, or government policy update": "Legal & Compliance",
    "disputing terms of service or a privacy policy change": "Legal & Compliance",
}

CANDIDATE_LABELS = list(LEAF_INTENTS.keys())
HYPOTHESIS_TEMPLATE = "This message is {}."

classifierPipeline = pipeline(
    task="zero-shot-classification",
    model=LOCAL_MODEL_PATH,
    use_safetensors=LOCAL_MODEL_PATH,
)

classifierPipeline2 = pipeline(
    task="zero-shot-classification",
    model=LOCAL_MODEL_PATH,
    use_safetensors=LOCAL_MODEL_PATH,
)

BRANCH_THRESHOLD = 0.30
MIN_BRANCHES = 1  # always keep at least the top branch even if none clear the bar
 

def analyzeIntent(text: str):
    firstLevel = classifierPipeline(
        text,
        candidate_labels=FIRST_LEVEL,
        multi_label=True,
        hypothesis_template=HYPOTHESIS_LEVEL_1,
    )

    output = None

    if isinstance(firstLevel, dict):

        labels = firstLevel["labels"]
        scores = firstLevel["scores"]


        promisingBranches = [lbl for lbl, sc in zip(labels, scores) if sc > BRANCH_THRESHOLD]

        if len(promisingBranches) < MIN_BRANCHES:
            promisingBranches = labels[:MIN_BRANCHES]


        microIntent = []

        for pB in promisingBranches:
            microIntent.extend(LEVEL_2_ROUTER[pB])


        intent = classifierPipeline(
            text,
            candidate_labels=microIntent,
            multi_label=False,
            hypothesis_template=HYPOTHESIS_LEVEL_2,
        )

        if isinstance(intent, dict):

            probableIntent = intent["labels"][0]

            overarchingIntent = next(b for b, leaves in LEVEL_2_ROUTER.items() if probableIntent in leaves)

            output = {
                "category": DASHBOARD_LABEL_MAP[overarchingIntent],
                "description": intent["labels"][0],  # type: ignore
                "confidence": round((intent["scores"][0] * 100), 2),  # type: ignore
            }

    return output


def experimentWithFlatCaegorization(text: str) -> dict:

    intent = classifierPipeline2(
        text,
        candidate_labels=CANDIDATE_LABELS,
        multi_label=False,
        hypothesis_template=HYPOTHESIS_TEMPLATE,
    )

    output = {}

    if isinstance(intent, dict):


        output = {
            "category": LEAF_INTENTS[intent["labels"][0]],
            "description": intent["labels"][0],
            "confidence": round((intent["scores"][0] * 100), 2),
        }

    return output


if __name__ == "__main__":
    testInputs = [
        # --- reporting a technical problem or software error ---
        "Is anyone else getting a 'Connection to DB failed' error on the login page?? critical bug, fix asap pls.",
        "The entire platform has been down for the last two hours, none of my team can log in.",
        "Every time I click 'export to CSV' the app just freezes and I have to force close it.",
        "I can't log in anymore, it keeps saying my password is incorrect even after I reset it.",
        "Our webhook integration stopped receiving events from your API sometime last night with no error logged.",
        # --- managing a financial payment, invoice, or billing issue ---
        "I was charged twice for my subscription this month!! Who do I talk to to get a refund for the duplicate transaction?",
        "My card was declined during checkout but the order still shows as pending in my account.",
        "Can someone explain why my invoice this month is higher than usual? Did the pricing change?",
        "We're a 200-person company looking to move off the standard plan, can we get a custom enterprise quote?",
        "My annual plan is renewing next week, is there a discount available if I switch to the two-year option?",
        # --- providing input regarding product or requesting a feature ---
        "It would be amazing if you could add dark mode to the mobile app, my eyes would thank you.",
        "The new settings menu is way too cluttered, I can never find what I'm looking for anymore.",
        "The dashboard takes almost 10 seconds to load every single time, is that normal?",
        "Quick question, does the free tier include access to the API or is that only on paid plans?",
        "Honestly the drag-and-drop editor feels clunky compared to how smooth the rest of the app is.",
        # --- alerting about a computer security threat or privacy issue ---
        "I think I found a way to view other users' order details just by changing the URL parameter, this needs urgent attention.",
        "Got a phishing email pretending to be from your support team asking for my password, wanted to flag it.",
        "Someone logged into my account from a country I've never visited, is there a way to see the login history?",
        "I noticed my personal data appeared in a public API response that shouldn't be exposed.",
        # --- managing user account settings, profiles, or access permissions ---
        "Please delete my account and all associated data, as required under GDPR.",
        "I'm not receiving the 2FA code via SMS anymore, can you help me reset it?",
        "How do I change one of my team members from admin to a read-only role?",
        "Can you export all of my account data? I need it for a personal record request.",
        # --- discussing company news, public relations, or leadership decisions ---
        "Just saw the news about the acquisition, what does this mean for existing customers like us?",
        "Disappointed to hear about the layoffs announced this morning, hope the affected team is okay.",
        "Congrats on the Series C funding round, exciting to see where the company goes next.",
        "Read the CEO's statement on the recent controversy, curious how this will affect the roadmap.",
        # --- comparing the product or service against market competitors ---
        "How does your platform compare to Competitor X in terms of the reporting features?",
        "We're currently on a rival tool and considering switching, what does migration typically look like?",
        "For the price you charge, Competitor Y offers basically the same features for half the cost.",
        "Does your product support the same level of customization that ToolZ offers?",
        # --- expressing legal concerns, regulatory compliance, or terms of service issues ---
        "One of the illustrations in your latest blog post looks suspiciously similar to artwork we own the rights to.",
        "Are you aware of the new data localization regulations in the EU and how they affect your storage practices?",
        "The updated terms of service seem to remove the clause about data ownership, can someone clarify this change?",
        "We received notice of a regulatory fine related to a vendor using your platform, does this affect us too?",
        # --- ambiguous / cross-category stress tests ---
        "I was double charged and now I can't log in to even check my invoice, everything is broken.",
        "Your competitor just had a data breach, does your platform handle security any differently?",
        "The new pricing page has a broken 'Contact Sales' button, tried three times and it just spins.",
        "Not sure if this is a bug or a feature, but I can see another company's team name in my account switcher.",
    ]

    for input_text in testInputs:
        result = analyzeIntent(input_text)

        # print("*" * 60 + " using PREVIOUS METHOD")
        print(
            f"Text: {input_text}\nCategory: {result['category']}\nDescription: {result['description']}\nConfidence: {result['confidence']}%"  # type: ignore
        )

        print()

        # print("*" * 60 + " using FLAT STRUCTURE METHOD")

        # result = experimentWithFlatCaegorization(input_text)

        # print(
        #     f"Text: {input_text}\nCategory: {result['category']}\nDescription: {result['description']}\nConfidence: {result['confidence']}%"  # type: ignore
        # )

        print("-" * 50)
