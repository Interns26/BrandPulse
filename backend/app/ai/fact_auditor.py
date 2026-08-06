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


def chunk_source_text(
    source_text: str, max_words: int = 300, overlap: int = 50
) -> list[str]:

    words = source_text.split()

    if not words:
        return []

    return [
        " ".join(words[i : i + max_words])
        for i in range(0, len(words), max_words - overlap)
    ]


def audit_action_brief(
    source_text: str, brief: dict, contradiction_threshold: float = 0.50
):

    claims = extract_claims(brief)

    chunked_source_text = chunk_source_text(source_text)

    flagged_claims = []

    for claim in claims:

        hypothesis_template = f"The claim '{claim}' is " + "{}"

        max_contradiction_score = 0.0

        for chunk in chunked_source_text:

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
