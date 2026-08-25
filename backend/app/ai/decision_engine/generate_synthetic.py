import numpy as np
import pandas as pd
import random
import os

def generate_synthetic_dataset(num_samples: int = 1000, output_path: str = "synthetic_campaigns.csv"):
    np.random.seed(42)
    random.seed(42)

    vulnerability_types = [
        "System Outage", 
        "Price Increase", 
        "Data Breach", 
        "PR Crisis", 
        "Product Defect", 
        "Layoffs"
    ]
    
    volumes = [50.0, 75.0, 100.0]

    data = []

    for _ in range(num_samples):
        v_type = random.choice(vulnerability_types)
        
        # Base severity derived from domain mapping with noise
        base_severities = {
            "System Outage": 95.0,
            "Data Breach": 90.0,
            "Price Increase": 80.0,
            "PR Crisis": 75.0,
            "Product Defect": 70.0,
            "Layoffs": 65.0
        }
        severity = float(np.clip(np.random.normal(base_severities[v_type], 5.0), 0.0, 100.0))
        
        article_age = float(np.random.exponential(scale=48.0)) # Decay distribution
        urgency = float(100.0 * np.exp(-0.05 * (article_age / 24.0)))
        volume = float(random.choice(volumes))
        confidence_score = float(np.clip(np.random.normal(0.85, 0.08), 0.5, 1.0))
        
        # Opportunity Score calculation (Sprint 2 formula + slight noise)
        opportunity_score = float(np.clip((0.40 * severity) + (0.30 * volume) + (0.30 * urgency) + np.random.normal(0, 2.0), 0.0, 100.0))

        # Heuristic rules for targets
        if v_type in ["System Outage", "Data Breach"] and severity > 80:
            strategy = "COMPETITOR_SWITCHING"
            channel = "LINKEDIN_EMAIL"
            content_type = "COMPARISON_GUIDE"
        elif v_type == "Price Increase":
            strategy = "PROMOTIONAL_OFFER"
            channel = "LINKEDIN_EMAIL" if volume > 50 else "SOCIAL_ONLY"
            content_type = "COMPARISON_GUIDE" if opportunity_score > 75 else "SOCIAL_CAMPAIGN"
        elif v_type in ["PR Crisis", "Layoffs"]:
            strategy = "PRODUCT_AWARENESS"
            channel = "CONTENT_MARKETING"
            content_type = "CASE_STUDY"
        elif v_type == "Product Defect":
            strategy = "RELIABILITY_MESSAGING"
            channel = "WEBINAR_EVENT" if severity > 75 else "CONTENT_MARKETING"
            content_type = "WHITE_PAPER"
        else:
            strategy = "RETENTION_DEFENSE"
            channel = "SOCIAL_ONLY"
            content_type = "SOCIAL_CAMPAIGN"

        # 15% Noise Injection to prevent rigid over-fitting
        if random.random() < 0.15:
            strategy = random.choice(["COMPETITOR_SWITCHING", "RETENTION_DEFENSE", "PROMOTIONAL_OFFER", "RELIABILITY_MESSAGING", "PRODUCT_AWARENESS"])
        if random.random() < 0.15:
            channel = random.choice(["LINKEDIN_EMAIL", "SOCIAL_ONLY", "WEBINAR_EVENT", "CONTENT_MARKETING"])
        if random.random() < 0.15:
            content_type = random.choice(["COMPARISON_GUIDE", "CASE_STUDY", "WHITE_PAPER", "SOCIAL_CAMPAIGN"])

        data.append({
            "severity": severity,
            "urgency": urgency,
            "volume": volume,
            "confidence_score": confidence_score,
            "opportunity_score": opportunity_score,
            "article_age": article_age,
            "vulnerability_type": v_type,
            "strategy": strategy,
            "channel": channel,
            "content_type": content_type
        })

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    generate_synthetic_dataset(1000, "synthetic_campaigns.csv")