import json
import pytest
from datetime import datetime
from app.ingestion.prefilter import validate_article_prefilter, prefilter_article_dict
from app.ingestion.cleaner import clean_news_content
from app.ingestion.news_fetcher import parse_to_iso_utc


def test_prefilter_valid_competitor_and_context():
    """Tests that articles matching both a competitor and POS context pass the pre-filter."""
    title = "Square POS Suffers Nationwide System Outage"
    content = "Square point of sale payment processing went down across the US for 6 hours today."
    
    is_valid, competitors, contexts = validate_article_prefilter(title, content)
    
    assert is_valid is True
    assert "square" in competitors
    assert any(c in contexts for c in ["pos", "point of sale", "payment processing", "outage"])


def test_prefilter_rejects_exclusion_keywords():
    """Tests that articles with non-POS phrases like 'cinnamon toast' are rejected."""
    title = "Best Breakfast Recipes: How to Make French Cinnamon Toast"
    content = "This cinnamon toast recipe is easy and delicious for morning breakfast."
    
    is_valid, competitors, contexts = validate_article_prefilter(title, content)
    
    assert is_valid is False
    assert len(competitors) == 0


def test_prefilter_rejects_missing_context():
    """Tests that mentioning a competitor without POS context fails the filter."""
    title = "Square Inc. Opens New Corporate Office in New York"
    content = "The financial tech company expanded its real estate footprint today."
    
    is_valid, competitors, contexts = validate_article_prefilter(title, content)
    
    assert is_valid is False


def test_output_contract_schema_matching():
    """Verifies that the enriched article dictionary matches Basim's required schema contract."""
    raw_article = {
        "title": "Toast POS Raises Subscription Fees for Merchants",
        "content": "Toast point of sale systems announced a price increase for all restaurant partners.",
        "url": "https://techcrunch.com/2026/08/01/toast-price-hike/",
        "source_name": "TechCrunch",
        "published_at": "Sat, 01 Aug 2026 14:30:00 GMT",
    }
    
    # Process through cleaning, date parsing, and prefiltering
    raw_article["title"] = clean_news_content(raw_article["title"])
    raw_article["content"] = clean_news_content(raw_article["content"])
    raw_article["published_at"] = parse_to_iso_utc(raw_article["published_at"])
    
    processed = prefilter_article_dict(raw_article)
    
    assert processed is not None
    # Validate required keys for Basim's input contract
    required_keys = {"title", "content", "url", "source_name", "published_at"}
    assert required_keys.issubset(set(processed.keys()))
    
    # Ensure ISO 8601 UTC timestamp format
    assert "T" in processed["published_at"]
    assert processed["source_name"] == "TechCrunch"


def test_clean_news_content_sanitization():
    """Verifies that news text sanitization strips raw URLs and normalizes whitespace."""
    dirty_html = "<p>Square POS experienced an outage. Visit https://status.square.com for info.  </p>"
    cleaned = clean_news_content(dirty_html)
    assert "https://" not in cleaned
    assert "<p>" not in cleaned
    assert cleaned == "Square POS experienced an outage. Visit for info."