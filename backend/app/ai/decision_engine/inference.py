"""
Module: inference.py
Purpose: Provides an object-oriented wrapper for executing the trained ML pipeline.
Mechanism: Loads the serialized model into memory and exposes a `predict` method 
that processes raw dictionaries, extracts probabilities from the Random Forest, 
and returns a structured JSON payload.
"""

import pandas as pd
import joblib
import os
from typing import Dict, Any

class CampaignDecisionEngine:
    def __init__(self, model_path: str = "models_storage/campaign_decision_model.pkl"):
        # Locates and loads the pre-trained binary model file.
        if not os.path.exists(model_path):
             alt_path = os.path.join(os.path.dirname(__file__), "../../models_storage/campaign_decision_model.pkl")
             if os.path.exists(alt_path):
                 model_path = alt_path
             else:
                 raise FileNotFoundError(f"Model binary not found at {model_path}")
        
        self.pipeline = joblib.load(model_path)
        self.target_columns = ["strategy", "channel", "content_type"]

    def predict(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a forward pass through the ML pipeline.
        Expects feature_dict containing exactly 7 keys: severity, urgency, volume, 
        confidence_score, opportunity_score, article_age, vulnerability_type.
        """
        # Convert dictionary to DataFrame (required by scikit-learn pipeline format)
        input_df = pd.DataFrame([feature_dict])

        # Execute point prediction (The absolute decision)
        predictions = self.pipeline.predict(input_df)[0]
        
        # ==========================================
        # CONFIDENCE SCORE EXTRACTION
        # ==========================================
        # Dig into the pipeline to get the raw probabilities. 
        # If 75 out of 100 decision trees voted for "LINKEDIN_EMAIL", the confidence is 75%.
        estimators = self.pipeline.named_steps["classifier"].estimators_
        
        # Must manually apply the StandardScaler/OneHotEncoder before passing to estimators
        preprocessed_input = self.pipeline.named_steps["preprocessor"].transform(input_df)
        
        confidence_scores = {}
        for idx, col in enumerate(self.target_columns):
            # .predict_proba returns an array of probabilities for every possible class
            probs = estimators[idx].predict_proba(preprocessed_input)[0]
            max_prob = float(max(probs))
            confidence_scores[f"{col}_confidence"] = round(max_prob, 4)

        # Assemble the final dictionary for the API/Database
        result = {
            "strategy": predictions[0],
            "channel": predictions[1],
            "content_type": predictions[2],
            "confidence_metrics": confidence_scores,
            "overall_confidence": round(sum(confidence_scores.values()) / len(confidence_scores), 4)
        }

        return result

# Verification Block (Executes only if file is run directly)
if __name__ == "__main__":
    engine = CampaignDecisionEngine(model_path="../../models_storage/campaign_decision_model.pkl")
    sample_input = {
        "severity": 95.0,
        "urgency": 88.0,
        "volume": 100.0,
        "confidence_score": 0.92,
        "opportunity_score": 93.4,
        "article_age": 4.5,
        "vulnerability_type": "System Outage"
    }
    decision = engine.predict(sample_input)
    print("Inference Test Result:", decision)