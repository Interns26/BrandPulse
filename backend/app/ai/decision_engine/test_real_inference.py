"""
Module: test_real_inference.py
Purpose: Connects the database to the inference engine to process real live data.
Mechanism: Queries PostgreSQL using settings from config.py, joins Articles and VulnerabilityResults, 
recalculates transient features utilizing centralized domain thresholds, and exports a JSON audit log.
"""

import json
import math
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.database.models import Article, VulnerabilityResult
from app.ai.decision_engine.inference import CampaignDecisionEngine
from app.config import get_settings

# Load centralized configurations
settings = get_settings()

# --- Feature Derivation Helper Functions ---

def calculate_article_age(published_at: datetime) -> float:
    """Calculates absolute hours elapsed since publication, ensuring timezone awareness."""
    if not published_at:
        return 24.0
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = now - published_at
    return max(0.0, delta.total_seconds() / 3600.0)

def derive_severity(v_type: str) -> float:
    """Translates the NLP text label into a numeric severity score for the ML matrix."""
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
    """
    Translates publisher string into a numeric proxy for media reach (Volume),
    utilizing domain blacklists and source tracking from config.py.
    """
    s_name = (source_name or "").lower()
    
    # Domains listed in blacklist or major financial tiers get max weighting (100.0)
    tier1_indicators = ["techcrunch", "bloomberg", "reuters", "wsj", "theverge", "latimes"] + settings.blacklist_domains
    tier2_indicators = ["businesswire", "prnewswire", "yahoo", "marketwatch", "forbes"]
    
    if any(t in s_name for t in tier1_indicators):
        return 100.0
    if any(t in s_name for t in tier2_indicators):
        return 75.0
    return 50.0

# --- Core Execution Process ---

def run_real_data_inference():
    db: Session = SessionLocal()
    
    try:
        # Load the ML model binary into memory
        predictor = CampaignDecisionEngine()
        print(f"[{settings.app_name}] ML predictor loaded successfully in DEBUG={settings.debug} mode.")
    except Exception as e:
        print(f"Failed to load ML predictor: {e}")
        db.close()
        return
    
    # DATABASE JOIN: 
    # Fetches all rows in the VulnerabilityResult table and joins them with their parent Article.
    results = db.query(Article, VulnerabilityResult).join(
        VulnerabilityResult, Article.id == VulnerabilityResult.article_id
    ).all()
    
    print(f"Found {len(results)} vulnerability results for processing.")
    
    if len(results) == 0:
        db.close()
        return
    
    output_payload = []
    
    for idx, (article, vuln) in enumerate(results, 1):
        
        # STEP 1: Feature Extraction & Reassembly
        age_hours = calculate_article_age(article.published_at)
        severity = derive_severity(vuln.vulnerability_type)
        volume = derive_volume(article.source_name)
        
        # Apply exponential time-decay urgency formula
        urgency = 100.0 * math.exp(-0.05 * (age_hours / 24.0))
        
        # Fetch existing opportunity score from DB, or reconstruct using Sprint 2 math
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
        
        # STEP 2: ML Inference Execution
        try:
            decision = predictor.predict(feature_dict)
        except Exception as e:
            decision = {"error": str(e)}
        
        # STEP 3: Payload Construction
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
    
    # STEP 4: Data Export
    output_file = "real_inference_results_final.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=4, default=str)
    
    print(f"PROCESSING COMPLETE. Processed {len(results)} records. Exported to: {output_file}")

if __name__ == "__main__":
    run_real_data_inference()