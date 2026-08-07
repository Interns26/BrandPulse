# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

from transformers import pipeline
from pathlib import Path

# model being used is lxyuan/distilbert-base-multilingual-cased-sentiments-student

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOCAL_MODEL_PATH = str(BASE_DIR / "models_storage" / "sentiment_model")

sentimentPipeline = pipeline(
    task="text-classification", model=LOCAL_MODEL_PATH, tokenizer=LOCAL_MODEL_PATH
)


def analyzeSentiment(text: str) -> dict:

    output = sentimentPipeline(text, truncation=True, max_length=512)[0]

    return {"label": output["label"], "confidence": round((output["score"] * 100), 2)}


if __name__ == "__main__":

    testInputs = [
        "I keep getting a 500 Internal Server Error every time I click billing.",
        "The application UI is standard, nothing special.",
        "Wow, the loading speed is incredibly fast! Love it.",
    ]

    for input in testInputs:
        pred = analyzeSentiment(input)
        print(f"text: {input}")
        print(f"Label: {pred['label'].upper()} Confidence: {pred['confidence']}%")
        print("-" * 50)
