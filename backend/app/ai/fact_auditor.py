# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

from pathlib import Path
from transformers import pipeline

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOCAL_MODEL_PATH = str(BASE_DIR / "models_storage" / "nli_deberta_small")


nli_auditor = pipeline(
    task="zero-shot-classification", model=LOCAL_MODEL_PATH, use_safetensors=True
)


def extract_claims(brief: dict) -> list[str]:

    claims = []

    if "headline" in brief:
        claims.append(brief["headline"])

    if "vulnerability_summary" in brief:
        claims.append(brief["vulnerability_summary"])

    return claims

def chunk_text(text: str, max_words: int = 300, overlap: int = 50):

    words = text.split()

    if not words:
        return []

    return [
        " ".join(words[i : i + max_words])
        for i in range(0, len(words), max_words - overlap)
    ]

def audit_action_brief(
    article_summary:str,   brief: dict, contradiction_threshold: float = 0.50
):

    claims = extract_claims(brief)

    chunked_summary = chunk_text(article_summary)

    flagged_claims = []

    for claim in claims:

        hypothesis_template = f"The claim '{claim}' is " + "{}"

        max_contradiction_score = 0.0

        for chunk in chunked_summary:

            output = nli_auditor(
                chunk,
                candidate_labels=[
                    "contradiction to the article",
                    "supported by the article",
                ],
                hypothesis_template=hypothesis_template,
            )

            if isinstance(output, dict):

                for label, scr in zip(output["labels"], output["scores"]):

                    if (
                        label == "contradiction to the article"
                        and max_contradiction_score < scr
                    ):
                        max_contradiction_score = scr

                if max_contradiction_score > contradiction_threshold:
                    break

        if max_contradiction_score > contradiction_threshold:
            flagged_claims.append(claim)

    return {
        "is_passed": len(flagged_claims) == 0,
        "flagged_claims": flagged_claims,
        "audited_brief": brief,
    }
