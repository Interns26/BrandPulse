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


def audit_action_brief(
    source_text: str, brief: dict, contradiction_threshold: float = 0.60
):

    claims = extract_claims(brief)

    flagged_claims = []

    for claim in claims:

        hypothesis_template = f"The claim '{claim}' is " + "{}"

        output = nli_auditor(
            source_text,
            candidate_labels=[
                "contradiction to the article",
                "supported by the article",
            ],
            hypothesis_template=hypothesis_template,
        )

        if isinstance(output, dict):

            for label, scr in zip(output["labels"], output["scores"]):

                if label =="contradiction to the article" and scr > contradiction_threshold:
                    flagged_claims.append(claim)

    return {
        "is_passed": len(flagged_claims) == 0,
        "flagged_claims": flagged_claims,
        "audited_brief": brief,
    }
