"""
Sprint 3: Real Data Inference Runner
Processes all 21 Sprint 2 outputs by joining with the articles table for time decay calculations.
"""

import json
import math
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.database.models import Article, VulnerabilityResult
from app.ai.decision_engine.inference import CampaignDecisionEngine

def calculate_article_age(published_at: datetime) -> float:
    if not published_at:
        return 24.0
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - published_at
    return max(0.0, delta.total_seconds() / 3600.0)

def derive_severity(v_type: str) -> float:
    mapping = {
        "System Outages": 95.0,
        "Data Breaches": 90.0,
        "Price Increases": 80.0,
        "PR Crises": 75.0,
        "Product Defects": 70.0,
        "Layoffs": 65.0
    }
    for key, val in mapping.items():
        if key.lower() in (v_type or "").lower():
            return val
    return 70.0

def derive_volume(source_name: str) -> float:
    tier1 = ["techcrunch", "bloomberg", "reuters", "wsj", "theverge", "latimes"]
    tier2 = ["businesswire", "prnewswire", "yahoo", "marketwatch", "forbes"]
    s_name = (source_name or "").lower()
    
    if any(t in s_name for t in tier1):
        return 100.0
    if any(t in s_name for t in tier2):
        return 75.0
    return 50.0

def run_real_data_inference():
    db: Session = SessionLocal()
    
    try:
        predictor = CampaignDecisionEngine()
        print("ML predictor loaded successfully.")
    except Exception as e:
        print(f"Failed to load ML predictor: {e}")
        db.close()
        return
    
    # Unrestricted Inner Join.
    # Matches the 21 vulnerability_results to their parent articles.
    # Automatically drops the 7 articles rejected by Sprint 2.
    results = db.query(Article, VulnerabilityResult).join(
        VulnerabilityResult, Article.id == VulnerabilityResult.article_id
    ).all()
    
    print(f"Found {len(results)} vulnerability results for processing.")
    
    if len(results) == 0:
        db.close()
        return
    
    output_payload = []
    
    for idx, (article, vuln) in enumerate(results, 1):
        
        # 1. Feature Extraction
        age_hours = calculate_article_age(article.published_at)
        severity = derive_severity(vuln.vulnerability_type)
        volume = derive_volume(article.source_name)
        urgency = 100.0 * math.exp(-0.05 * (age_hours / 24.0))
        
        opp_score = getattr(vuln, 'opportunity_score', None)
        if opp_score is None:
            opp_score = (0.40 * severity) + (0.30 * volume) + (0.30 * urgency)
            
        confidence = getattr(vuln, 'confidence_score', 0.85)
        
        feature_dict = {
            "severity": float(severity),
            "urgency": float(urgency),
            "volume": float(volume),
            "confidence_score": float(confidence),
            "opportunity_score": float(opp_score),
            "article_age": float(age_hours),
            "vulnerability_type": vuln.vulnerability_type or "Unknown"
        }
        
        # 2. ML Inference
        try:
            decision = predictor.predict(feature_dict)
        except Exception as e:
            decision = {"error": str(e)}
        
        # 3. Construct JSON Payload
        output_payload.append({
            "article_metadata": {
                "article_id": str(article.id),
                "title": article.title,
                "source": article.source_name,
                "competitors": getattr(article, 'matched_competitors', []),
                "vulnerability_type": vuln.vulnerability_type,
                "published_at_utc": article.published_at.isoformat() if article.published_at else "MISSING_TIME",
                "extracted_age_hours": round(age_hours, 2)
            },
            "ml_features_extracted": feature_dict,
            "campaign_decision": decision
        })
    
    db.close()
    
    output_file = "real_inference_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=4, default=str)
    
    print(f"PROCESSING COMPLETE. Processed 21 records. Exported to: {output_file}")

if __name__ == "__main__":
    run_real_data_inference()