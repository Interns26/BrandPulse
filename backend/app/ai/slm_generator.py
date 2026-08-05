from pathlib import Path
from llama_cpp import Llama
import json
from vulnerability_prompts import (
    STAGE2_SYSTEM_PROMPT,
    build_action_brief_user_prompt,
)

LOCAL_MODELS = {}

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LLAMA_LOCAL_MODEL_PATH = str(
    BASE_DIR
    / "models_storage"
    / "llama_3.2_3b_gguf"
    / "llama-3.2-3b-instruct-q4_k_m.gguf"
)

QWEN_LOCAL_MODEL_PATH = str(
    BASE_DIR / "models_storage" / "qwen_1.5b_gguf" / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
)


def generate_action_brief(
    competitors: list[str],
    vulnerability_type: str,
    article_context: str,
    opportunity_score: float,
) -> dict:


    competitors_str = ", ".join(competitors) if len(competitors)>0 else ["Target Competitor"]

    if opportunity_score >= 40.0:

        llama = LOCAL_MODELS.get("llama", None)

        if llama is None:

            llama = Llama(
                model_path=LLAMA_LOCAL_MODEL_PATH,
                n_ctx=2048,
                verbose=False,
            )

            LOCAL_MODELS["llama"] = llama

            model = llama
        else:
            model = llama

    else:

        qwen = LOCAL_MODELS.get("qwen", None)

        if qwen is None:

            qwen = Llama(
                model_path=QWEN_LOCAL_MODEL_PATH,
                n_ctx=2048,
                verbose=False,
            )

            LOCAL_MODELS["qwen"] = qwen

            model = qwen
        else:
            model = qwen

    system_prompt = STAGE2_SYSTEM_PROMPT

    user_prompt = build_action_brief_user_prompt(
        competitors, vulnerability_type, opportunity_score, article_context
    )

    try:

        response = model.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=384,
            response_format={"type": "json_object"},
        )

        raw_text = response["choices"][0]["message"]["content"].strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        # Parse JSON payload
        return json.loads(raw_text)

    except Exception as e:

      return {
            "headline": f"Exploit recent {vulnerability_type} vulnerability affecting {competitors_str}",
            "vulnerability_summary": f"Identified {vulnerability_type} involving {competitors_str} in media coverage.",
            "target_department": "SALES",
            "recommended_action": f"Launch competitive outreach targeting active merchants using {competitors_str}.",
            "urgency": "Medium",
            "generation_error": str(e),
        }
