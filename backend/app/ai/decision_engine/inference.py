import pandas as pd
import joblib
import os
from typing import Dict, Any

class CampaignDecisionEngine:
    def __init__(self, model_path: str = "models_storage/campaign_decision_model.pkl"):
        if not os.path.exists(model_path):
             # Fallback check for root vs subfolder execution
             alt_path = os.path.join(os.path.dirname(__file__), "../../models_storage/campaign_decision_model.pkl")
             if os.path.exists(alt_path):
                 model_path = alt_path
             else:
                 raise FileNotFoundError(f"Model binary not found at {model_path}")
        
        self.pipeline = joblib.load(model_path)
        self.target_columns = ["strategy", "channel", "content_type"]

    def predict(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expects feature_dict containing:
        - severity (float)
        - urgency (float)
        - volume (float)
        - confidence_score (float)
        - opportunity_score (float)
        - article_age (float)
        - vulnerability_type (str)
        """
        input_df = pd.DataFrame([feature_dict])

        # Point predictions
        predictions = self.pipeline.predict(input_df)[0]
        
        # Calculate confidence scores per output target
        estimators = self.pipeline.named_steps["classifier"].estimators_
        preprocessed_input = self.pipeline.named_steps["preprocessor"].transform(input_df)
        
        confidence_scores = {}
        for idx, col in enumerate(self.target_columns):
            probs = estimators[idx].predict_proba(preprocessed_input)[0]
            max_prob = float(max(probs))
            confidence_scores[f"{col}_confidence"] = round(max_prob, 4)

        result = {
            "strategy": predictions[0],
            "channel": predictions[1],
            "content_type": predictions[2],
            "confidence_metrics": confidence_scores,
            "overall_confidence": round(sum(confidence_scores.values()) / len(confidence_scores), 4)
        }

        return result

# Verification Block
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