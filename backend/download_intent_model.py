# Copyright (c) UWorx Services 2026. All Rights Reserved. The information contained herein is proprietary and confidential. This proprietary and confidential information, either in whole or in part, shall not be used for any purpose unless permitted by the terms of a valid license agreement.

from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# BASE_DIR targets backend/ directly
BASE_DIR = Path(__file__).resolve().parent
SAVE_DIR = BASE_DIR / "models_storage" / "intent_model"

MODEL_NAME = "facebook/bart-large-mnli"

print(f"Downloading {MODEL_NAME} to {SAVE_DIR}...")

# Ensure destination directory exists
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Download and save tokenizer + model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

tokenizer.save_pretrained(SAVE_DIR)
model.save_pretrained(SAVE_DIR)

print("Saved successfully!")