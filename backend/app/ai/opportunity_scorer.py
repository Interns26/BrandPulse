from datetime import datetime, timezone
import math
from urllib.parse import urlparse

SEVERITY_LOOKUP = {
    "System Outages": 95.0,
    "Price Increases": 80.0,
    "PR Crises": 75,
    "Layoffs": 65,
    "Product Defects": 70,
    "Data Breaches": 90.0,
}

SOURCE_TIER_LOOKUP = {
    # Tier 1: Major Global Tech & Business Publications
    "techcrunch.com": "tier1",
    "fastcompany.com": "tier1",
    "thestreet.com": "tier1",
    "block.xyz": "tier1",
    "shopify.com": "tier1",
    
    # Tier 2: Specialized FinTech, POS, & Industry Trade Media
    "pymnts.com": "tier2",
    "techradar.com": "tier2",
    "restaurantbusinessonline.com": "tier2",
    "paymentsjournal.com": "tier2",
    "digitaltransactions.net": "tier2",
    "kioskmarketplace.com": "tier2",
    "cfotech.com.au": "tier2",
    "restauranttechnologynews.com": "tier2",
    
    # Standard / Tier 3: Vendor-Owned Blogs & Niche Aggregators
    "toasttab.com": "standard",
    "blooloop.com": "standard",
}

DECAY_COEFFICIENT = 0.02


def calculate_severity(vulnerability_type: str) -> float:

    return SEVERITY_LOOKUP.get(vulnerability_type, 50.0)


def extract_source_name(url: str) -> str:
    """
    Extracts a normalized root domain from a URL to use as a source tier lookup key.
    Handles 'www.', subdomains, and country-code TLDs.
    """
    netloc = urlparse(url).netloc.lower()
    
    # Strip leading www.
    if netloc.startswith("www."):
        netloc = netloc[4:]
        
    parts = netloc.split(".")
    
    # Handle multi-part TLDs (e.g., cfotech.com.au -> cfotech.com.au)
    if len(parts) > 2:
        if parts[-2] in ["com", "co", "net", "org", "edu", "gov"]:
            return ".".join(parts[-3:])
        return ".".join(parts[-2:])
        
    return netloc

def get_source_tier(url: str) -> str:
    """
    Utility wrapper to extract domain and resolve its authority tier.
    Defaults to 'standard' if domain is not explicitly mapped.
    """
    source_domain = extract_source_name(url)
    return SOURCE_TIER_LOOKUP.get(source_domain, "standard")


def calculate_volume_score(
    source_tier: str = "standard"
) -> float:

    tier_lookup = {
            "tier1": 100.0,
            "tier2": 75.0,
            "standard": 50.0,
        }

    return tier_lookup.get(source_tier.lower(), 50.0)


def calculate_urgency(published_at: datetime | str, decay_rate: float = 0.05) -> float:

    now = datetime.now(timezone.utc)

    if isinstance(published_at, str):
        clean_str = published_at.replace("Z", "+00:00")
        pub_dt = datetime.fromisoformat(clean_str)
    else:
        pub_dt = published_at

    if pub_dt.tzinfo is None:
        pub_dt = pub_dt.replace(tzinfo=timezone.utc)

    hours_elapsed = (now - pub_dt).total_seconds() / 3600.0
    print(f"\n in caluclate_urgency() -> {hours_elapsed}")
    hours_elapsed = max(0.0, hours_elapsed)

    return round(100 * math.exp(-1 * decay_rate * hours_elapsed), 2)


def compute_opportunity_score(
    vulnerability_type: str, published_at: str | datetime, url: str
) -> dict:

    severity = calculate_severity(vulnerability_type)
    volume = calculate_volume_score(source_tier=get_source_tier(url=url))
    urgency = calculate_urgency(published_at, DECAY_COEFFICIENT)

    final_score = (0.4 * severity) + (0.3 * volume) + (0.3 * urgency)

    return {
        "opportunity_score": round(final_score, 2),
        "severity_score": severity,
        "volume_score": volume,
        "urgency_score": urgency,
        "priority_label": (
            "CRITICAL"
            if final_score >= 80
            else ("HIGH" if final_score >= 70 else "MEDIUM")
        ),
    }
